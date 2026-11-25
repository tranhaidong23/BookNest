"""Locked final evaluation. No fitting; separate test allowlist and output directory."""
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import day05_baselines as baselines
import day06_item_knn as knn
import day08_mf as mf
from audit_extended import sha
from prepare_day03 import write_json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/day10/final_20261123'
DATA=ROOT/'data/processed/day10_final_v1'
SPLIT=ROOT/'data/processed/day04_split_v1'
ALLOWED={'train.csv','catalogue_ids.csv','warm_test.csv','cold_test_support.csv','cold_test_target.csv'}
SELECTION={'primary':'item_knn','item_knn':'s10_k200','mf':'d16_l10','bias':'bias_l50',
           'support_sizes':[3,5,10],'primary_scenario':'cold_test_k5','refit':False}
MANIFESTS=['reports/day05/baselines_20261123/manifest.json','reports/day06_07/item_knn_20261123/manifest.json','reports/day08_09/mf_20261123/manifest.json']
CODE=['scripts/day10_evaluate.py','scripts/day05_baselines.py','scripts/day06_item_knn.py','scripts/day08_mf.py','scripts/audit_extended.py','scripts/prepare_day03.py','docs/DAY10_FINAL_EVALUATION.md']

def load_input(name,manifest):
    if name not in ALLOWED:raise ValueError('Not a locked Day10 input: '+name)
    p=SPLIT/name
    if sha(p)!=manifest['outputs'][str(p.relative_to(ROOT))]:raise ValueError('Split hash mismatch')
    return pd.read_csv(p,dtype='int64')

def verify_lock(lock,root=ROOT):
    if lock['selection']!=SELECTION:raise ValueError('Selection differs from lock')
    for name,h in lock['hashes'].items():
        if sha(root/name)!=h:raise ValueError('Locked file differs: '+name)

def lock_selection():
    path=OUT/'selection_lock.json'
    if path.exists():
        verify_lock(json.loads(path.read_text()));print('Existing lock verified; no test read.');return
    hashes={}
    for name in MANIFESTS:
        m=json.loads((ROOT/name).read_text());hashes[name]=sha(ROOT/name)
        metric=Path(name).parent/'metrics.json';assert sha(ROOT/metric)==m['metrics_sha256']
        hashes[str(metric)]=sha(ROOT/metric)
        # Validate and lock all model-family artifacts without reading any test input.
        for output,h in m['outputs'].items():
            assert sha(ROOT/output)==h,output
            hashes[output]=h
    k=json.loads((ROOT/'reports/day06_07/item_knn_20261123/metrics.json').read_text())
    f=json.loads((ROOT/'reports/day08_09/mf_20261123/metrics.json').read_text())
    b=json.loads((ROOT/'reports/day05/baselines_20261123/metrics.json').read_text())
    assert k['selected']==SELECTION['item_knn'] and f['selected']==SELECTION['mf'] and b['selected_bias']==SELECTION['bias']
    for name in CODE+['reports/day04/split_20261120/manifest.json','reports/day04/split_20261120/protocol_v0.1.md']:
        hashes[name]=sha(ROOT/name)
    write_json(path,{'locked_at_utc':datetime.now(timezone.utc).isoformat(),'selection':SELECTION,'hashes':hashes,
        'test_read_at_lock':False,'selection_basis':'cold-validation5 NDCG then Recall; no test tuning'})
    print('Selection locked. No test input read.',flush=True)

def main():
    lock_path=OUT/'selection_lock.json';lock=json.loads(lock_path.read_text());verify_lock(lock)
    sm=json.loads((ROOT/'reports/day04/split_20261120/manifest.json').read_text())
    assert sha(ROOT/'reports/day04/split_20261120/protocol_v0.1.md')==sm['protocol_snapshot_sha256']
    access=OUT/'test_access.json'
    if not access.exists():write_json(access,{'first_access_started_at_utc':datetime.now(timezone.utc).isoformat(),'selection_lock_sha256':sha(lock_path),'note':'Written before first test input read; test is now exposed, including if run fails.'})
    assert json.loads(access.read_text())['selection_lock_sha256']==sha(lock_path)
    frames={name:load_input(name,sm) for name in sorted(ALLOWED)}
    train=frames['train.csv'];support=frames['cold_test_support.csv'];target=frames['cold_test_target.csv']
    assert not set(train.user_id)&set(target.user_id)
    assert set(support.user_id)==set(target.user_id)
    assert not set(zip(support.user_id,support.book_id))&set(zip(target.user_id,target.book_id))
    assert not set(zip(train.user_id,train.book_id))&set(zip(frames['warm_test.csv'].user_id,frames['warm_test.csv'].book_id))
    kd=ROOT/'data/processed/day06_item_knn_v1';fd=ROOT/'data/processed/day08_mf_v1';bd=ROOT/'data/processed/day05_baselines_v1'
    ids=np.load(kd/'catalogue_ids.npy');pop=np.load(kd/'popularity.npy')
    index=np.load(kd/'neighbors_s10.npy');weights=np.load(kd/'weights_s10.npy')
    assert np.array_equal(ids,np.sort(frames['catalogue_ids.csv'].book_id))
    assert np.array_equal(ids,np.load(fd/'catalogue_ids.npy'))
    users=np.load(fd/'user_ids.npy');p=np.load(fd/'d16_l10_P.npy');q=np.load(fd/'d16_l10_Q.npy')
    bi=np.load(fd/'item_bias.npy');bu=np.load(fd/'user_bias.npy')
    bias=json.loads((bd/'bias_l50.json').read_text())
    bias['users']={int(k):v for k,v in bias['users'].items()};bias['items']={int(k):v for k,v in bias['items'].items()}
    counts={int(b):int(c) for b,c in zip(ids,pop)};mu=bias['mu']
    baselines.DATA=DATA;knn.DATA=DATA;mf.DATA=DATA
    results={};timings={};ci={};unseen={}
    scenarios=[(f'cold_test_k{size}',target,{int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in support.loc[support.support_rank<=size].groupby('user_id')},True) for size in (3,5,10)]
    warm_profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in train.groupby('user_id')}
    scenarios.append(('warm_test',frames['warm_test.csv'],warm_profiles,False))
    train_books=set(train.book_id)
    for label,t,profiles,cold in scenarios:
        print('Final evaluation',label,'baselines',flush=True)
        result,rows,timing=baselines.evaluate(label,t,profiles,ids.tolist(),{'bias_l50':bias},counts,mu,cold)
        print('Final evaluation',label,'KNN',flush=True)
        result['item_knn'],rows['item_knn'],timing['item_knn']=knn.evaluate(label+'_item_knn',t,profiles,ids,index,weights,200,pop)
        print('Final evaluation',label,'MF',flush=True)
        result['mf'],rows['mf'],timing['mf']=mf.evaluate(label+'_mf',t,profiles,ids,q,bi,mu,10,None if cold else p,None if cold else users,None if cold else bu)
        baseline=[r for r in rows['popularity'] if r['ndcg'] is not None];comparisons={}
        for name in ('item_knn','mf','bias_l50'):
            selected=[r for r in rows[name] if r['ndcg'] is not None]
            assert [r['user_id'] for r in selected]==[r['user_id'] for r in baseline]
            comparisons[name]={m:baselines.paired_ci([r[m] for r in selected],[r[m] for r in baseline]) for m in ('ndcg','recall')}
        results[label]=result;ci[label]=comparisons;timings[label]=timing
        unseen[label]={'items_without_train':len(set(ids)-train_books),'target_pairs_without_train_item':int((~t.book_id.isin(train_books)).sum())}
        print(label,json.dumps({n:{k:v for k,v in r.items() if k in ('ndcg','recall','rating_metrics')} for n,r in result.items()}),flush=True)
    write_json(OUT/'metrics.json',{'results':results,'paired_delta_vs_popularity':ci,'unseen':unseen,'primary_comparison':'cold_test_k5 item_knn minus popularity; NDCG and Recall','additional_comparisons':'descriptive/exploratory; no multiple-comparison correction','selection':SELECTION,'test_evaluated':True,'refit':False})
    (OUT/'timing_latest.json').write_text(json.dumps(timings,indent=2)+'\n',encoding='utf-8')
    verify_lock(lock)
    inputs={str((SPLIT/n).relative_to(ROOT)):sha(SPLIT/n) for n in sorted(ALLOWED)}
    for name,h in inputs.items():assert h==sm['outputs'][name]
    write_json(OUT/'manifest.json',{'version':'day10_final_v1','selection_lock_sha256':sha(lock_path),'inputs':inputs,
        'outputs':{str(x.relative_to(ROOT)):sha(x) for x in sorted(DATA.iterdir()) if x.is_file()},'metrics_sha256':sha(OUT/'metrics.json'),'script_sha256':sha(Path(__file__)),'test_evaluated':True})
    print('Final evaluation saved; no model refit or selection on test.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--lock',action='store_true');args=parser.parse_args()
    lock_selection() if args.lock else main()
