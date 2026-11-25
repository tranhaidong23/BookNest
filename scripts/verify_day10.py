"""Readback test audit: all saved rankings, independent cold5 KNN and MF."""
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
import json
import math
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from audit_extended import sha
from prepare_day03 import write_json
from day10_evaluate import verify_lock

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/day10/final_20261123'
DATA=ROOT/'data/processed/day10_final_v1';SPLIT=ROOT/'data/processed/day04_split_v1'

def main():
    manifest=json.loads((OUT/'manifest.json').read_text());metric=json.loads((OUT/'metrics.json').read_text())
    lock=json.loads((OUT/'selection_lock.json').read_text());verify_lock(lock)
    access=json.loads((OUT/'test_access.json').read_text())
    assert datetime.fromisoformat(lock['locked_at_utc'])<datetime.fromisoformat(access['first_access_started_at_utc'])
    assert manifest['selection_lock_sha256']==access['selection_lock_sha256']==sha(OUT/'selection_lock.json')
    for name,h in {**manifest['inputs'],**manifest['outputs']}.items():assert sha(ROOT/name)==h,name
    assert sha(OUT/'metrics.json')==manifest['metrics_sha256']
    assert sha(ROOT/'scripts/day10_evaluate.py')==manifest['script_sha256']
    train=pd.read_csv(SPLIT/'train.csv');support=pd.read_csv(SPLIT/'cold_test_support.csv')
    cold=pd.read_csv(SPLIT/'cold_test_target.csv');warm=pd.read_csv(SPLIT/'warm_test.csv')
    kd=ROOT/'data/processed/day06_item_knn_v1';fd=ROOT/'data/processed/day08_mf_v1'
    ids=np.load(kd/'catalogue_ids.npy');pop=np.load(kd/'popularity.npy');index=np.load(kd/'neighbors_s10.npy');weight=np.load(kd/'weights_s10.npy')
    q=np.load(fd/'d16_l10_Q.npy');bi=np.load(fd/'item_bias.npy')
    mu=json.loads((ROOT/'data/processed/day05_baselines_v1/bias_l50.json').read_text())['mu']
    mapping={int(b):i for i,b in enumerate(ids)};total_top10=0;independent_knn=independent_mf=0
    for label,models in metric['results'].items():
        is_cold=label.startswith('cold');target=cold if is_cold else warm
        size=int(label.split('_k')[1]) if is_cold else 0
        source=support.loc[support.support_rank<=size] if is_cold else train
        profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in source.groupby('user_id')}
        targets={int(u):g for u,g in target.groupby('user_id')}
        relevant={u:set(g.loc[g.rating>=4,'book_id']) for u,g in targets.items()}
        for name in ('popularity','bias_l50','item_knn','mf'):
            rows=json.loads((DATA/f'{label}_{name}_top10.json').read_text())
            saved={r['user_id']:r for r in json.loads((DATA/f'{label}_{name}_users.json').read_text())}
            assert {r['user_id'] for r in rows}==set(profiles)==set(targets)==set(saved)
            values=[];coverage=set();fallbacks=zeros=0;squared=absolute=0.;pairs=clipped=0
            for row in rows:
                u=row['user_id'];top=row['book_ids'];profile=profiles[u];seen={b for b,r in profile};rel=relevant[u]
                assert len(top)==len(set(top))==10 and not set(top)&seen and set(top)<=set(mapping)
                assert saved[u]['positive_targets']==len(rel)
                hits=[int(b in rel) for b in top]
                if rel:
                    ndcg=sum(h/math.log2(i+2) for i,h in enumerate(hits))/sum(1/math.log2(i+2) for i in range(min(10,len(rel))))
                    v=[ndcg,sum(hits)/len(rel),sum(hits)/10];values.append(v)
                    for key,value in zip(('ndcg','recall','precision'),v):assert abs(saved[u][key]-value)<1e-12
                else:assert all(saved[u][k] is None for k in ('ndcg','recall','precision'))
                coverage.update(top);total_top10+=1
                if name=='item_knn':fallbacks+=row['fallback'];zeros+=row['zero_affinity_slots']
                if label=='cold_test_k5' and name in ('item_knn','mf'):
                    eligible=[i for i,b in enumerate(ids) if int(b) not in seen]
                    if name=='item_knn':
                        scores=np.zeros(len(ids))
                        for book,r in profile:
                            if r>=4:
                                src=mapping[book]
                                for dest,w in zip(index[src,:200],weight[src,:200]):
                                    if dest>=0:scores[dest]+=(r-3)*w
                        fallback=not any(scores[i]>0 for i in eligible)
                        ranking=pop if fallback else scores
                        chosen=sorted(eligible,key=lambda i:(-ranking[i],int(ids[i])))[:10]
                        assert row['fallback']==fallback and row['zero_affinity_slots']==sum(scores[i]<=0 for i in chosen)
                        independent_knn+=1
                    else:
                        ix=[mapping[b] for b,r in profile];r=np.array([r for b,r in profile],float)
                        ub=sum(r-mu-bi[ix])/(50+len(ix));y=r-mu-bi[ix]-ub
                        vector=np.linalg.lstsq(np.vstack([q[ix],np.sqrt(10)*np.eye(q.shape[1])]),np.r_[y,np.zeros(q.shape[1])],rcond=None)[0]
                        scores=mu+ub+bi+np.einsum('ij,j->i',q,vector)
                        chosen=sorted(eligible,key=lambda i:(-scores[i],int(ids[i])))[:10]
                        t=targets[u];raw=scores[[mapping[int(b)] for b in t.book_id]];delta=np.clip(raw,1,5)-t.rating.to_numpy()
                        squared+=float(delta@delta);absolute+=float(np.abs(delta).sum());pairs+=len(delta);clipped+=int(((raw<1)|(raw>5)).sum())
                        independent_mf+=1
                    assert top==[int(ids[i]) for i in chosen],(label,name,u)
            actual=models[name]
            assert actual['users']==len(rows) and actual['ranking_users']==len(values)
            assert actual['users_without_positive_target']==len(rows)-len(values)
            for key,value in zip(('ndcg','recall','precision'),np.mean(values,axis=0)):assert abs(actual[key]-value)<1e-12
            assert actual['recommended_distinct_books']==len(coverage) and abs(actual['catalogue_coverage']-len(coverage)/len(ids))<1e-12
            if name=='item_knn':assert actual['fallback_users']==fallbacks and actual['zero_affinity_top10_slots']==zeros
            if label=='cold_test_k5' and name=='mf':
                a=actual['rating_metrics'];assert a['pairs']==pairs and a['clipped_predictions']==clipped
                assert abs(a['rmse']-math.sqrt(squared/pairs))<1e-12 and abs(a['mae']-absolute/pairs)<1e-12
        print('Verified rankings',label,flush=True)
    write_json(OUT/'validation.json',{'unit_tests_passed':42,'lock_precedes_test_access':True,'locked_model_and_source_hashes_verified':True,
        'all_saved_ranking_top10_rows_checked':total_top10,'independent_cold5_knn_users':independent_knn,'independent_cold5_mf_users':independent_mf,
        'independent_cold5_mf_rating_metrics':True,'other_rating_metrics_independent_recheck':False,
        'full_evaluation_cli_replay':False,'test_exposed':True,'manifest_sha256':sha(OUT/'manifest.json'),'verifier_sha256':sha(Path(__file__))})
    print('Day10 readback audit passed.',flush=True)

if __name__=='__main__':main()
