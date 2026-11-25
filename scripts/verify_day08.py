"""Independent augmented least-squares readback, selected cold5 and item equations."""
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
import json
import math
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from audit_extended import sha
from prepare_day03 import write_json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/day08_09/mf_20261123'
DATA=ROOT/'data/processed/day08_mf_v1'
SPLIT=ROOT/'data/processed/day04_split_v1'

def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    for name,h in {**manifest['inputs'],**manifest['outputs']}.items():assert sha(ROOT/name)==h,name
    assert sha(ROOT/'data/processed/catalogue_v1/catalogue.jsonl')=='869aa530a03b016a0795cfc1f752a927f59dc5df5f49d4054e6a4e9806c1de55'
    assert not any('test.csv' in n or 'cold_test_' in n for n in manifest['inputs'])
    assert sha(ROOT/'scripts/day08_mf.py')==manifest['script_sha256']
    assert sha(OUT/'metrics.json')==manifest['metrics_sha256']
    assert sha(OUT/'training_objectives.json')==manifest['objectives_sha256']
    traces=json.loads((OUT/'training_objectives.json').read_text())
    for trace in traces.values():assert len(trace)==9 and np.isfinite(trace).all() and np.all(np.diff(trace)<=1e-7)
    metric=json.loads((OUT/'metrics.json').read_text());name=metric['selected'];lam=int(name.split('_l')[1]);mu=metric['mu']
    ids=np.load(DATA/'catalogue_ids.npy');users=np.load(DATA/'user_ids.npy')
    bi=np.load(DATA/'item_bias.npy');bu=np.load(DATA/'user_bias.npy')
    p=np.load(DATA/(name+'_P.npy'));q=np.load(DATA/(name+'_Q.npy'));dimension=q.shape[1]
    for path in DATA.glob('*.npy'):assert np.isfinite(np.load(path,allow_pickle=False)).all()
    augment=np.sqrt(lam)*np.eye(dimension)
    train=pd.read_csv(SPLIT/'train.csv')
    sampled=np.unique(np.r_[0,np.random.default_rng(20261123).choice(len(ids),19,replace=False)])
    for i in sampled:
        g=train.loc[train.book_id==ids[i]];ui=np.searchsorted(users,g.user_id)
        y=g.rating.to_numpy()-mu-bu[ui]-bi[i]
        expected=np.linalg.lstsq(np.vstack([p[ui],augment]),np.r_[y,np.zeros(dimension)],rcond=None)[0]
        np.testing.assert_allclose(q[i],expected,atol=1e-10,rtol=1e-10)
    support=pd.read_csv(SPLIT/'cold_validation_support.csv').query('support_rank <= 5')
    target=pd.read_csv(SPLIT/'cold_validation_target.csv')
    profiles={int(u):g for u,g in support.groupby('user_id')}
    targets={int(u):g for u,g in target.groupby('user_id')}
    tops=json.loads((DATA/('cold5_'+name+'_top10.json')).read_text())
    saved={r['user_id']:r for r in json.loads((DATA/('cold5_'+name+'_users.json')).read_text())}
    assert {r['user_id'] for r in tops}==set(profiles)==set(targets)==set(saved)
    ndcgs=[];recalls=[];precisions=[];covered=set();squared=absolute=0.;pairs=clipped=0
    for row in tops:
        u=row['user_id'];g=profiles[u];ix=np.searchsorted(ids,g.book_id)
        ub=sum(g.rating.to_numpy()-mu-bi[ix])/(50+len(ix))
        y=g.rating.to_numpy()-mu-bi[ix]-ub
        vector=np.linalg.lstsq(np.vstack([q[ix],augment]),np.r_[y,np.zeros(dimension)],rcond=None)[0]
        scores=mu+ub+bi+np.einsum('ij,j->i',q,vector)
        seen=set(g.book_id);eligible=[i for i,b in enumerate(ids) if b not in seen]
        chosen=sorted(eligible,key=lambda i:(-scores[i],int(ids[i])))[:10]
        top=[int(ids[i]) for i in chosen];assert row['book_ids']==top,u
        covered.update(top);t=targets[u];relevant=set(t.loc[t.rating>=4,'book_id'])
        assert saved[u]['positive_targets']==len(relevant)
        if relevant:
            hits=[int(b in relevant) for b in top]
            ndcg=sum(h/math.log2(j+2) for j,h in enumerate(hits))/sum(1/math.log2(j+2) for j in range(min(10,len(relevant))))
            recall=sum(hits)/len(relevant);precision=sum(hits)/10
            for k,v in [('ndcg',ndcg),('recall',recall),('precision',precision)]:assert abs(saved[u][k]-v)<1e-12
            ndcgs.append(ndcg);recalls.append(recall);precisions.append(precision)
        else:assert saved[u]['ndcg'] is None
        raw=scores[np.searchsorted(ids,t.book_id)];delta=np.clip(raw,1,5)-t.rating.to_numpy()
        squared+=float(delta@delta);absolute+=float(np.abs(delta).sum());pairs+=len(delta);clipped+=int(((raw<1)|(raw>5)).sum())
    actual=metric['grid_cold5'][name]
    for k,v in [('ndcg',np.mean(ndcgs)),('recall',np.mean(recalls)),('precision',np.mean(precisions)),('catalogue_coverage',len(covered)/len(ids))]:assert abs(actual[k]-v)<1e-12,(k,v)
    assert actual['users']==len(tops) and actual['ranking_users']==len(ndcgs)
    assert actual['rating_metrics']['pairs']==pairs and actual['rating_metrics']['clipped_predictions']==clipped
    assert abs(actual['rating_metrics']['rmse']-math.sqrt(squared/pairs))<1e-12
    assert abs(actual['rating_metrics']['mae']-absolute/pairs)<1e-12
    write_json(OUT/'validation.json',{'unit_tests_passed':40,'hashes_verified':True,'all_factor_arrays_finite':True,
        'catalogue_v1_hash_unchanged':True,'python':platform.python_version(),'scipy':scipy.__version__,
        'supporting_code_sha256':{n:sha(ROOT/n) for n in ['requirements.txt','scripts/day05_baselines.py','scripts/day06_item_knn.py','scripts/prepare_day03.py','scripts/audit_extended.py','tests/test_day08.py']},
        'all_objective_traces_nonincreasing':True,'selected_item_equations_augmented_lstsq_checked':len(sampled),
        'selected_cold5_top10_users_checked':len(tops),'selected_cold5_ranking_users_checked':len(ndcgs),
        'selected_cold5_rating_pairs_checked':pairs,'independent_augmented_lstsq_metrics_match':True,
        'full_training_cli_replay':False,'test_read_or_evaluated':False,'manifest_sha256':sha(OUT/'manifest.json'),
        'verifier_sha256':sha(Path(__file__))})
    print('Verified hashes, objective traces,',len(sampled),'item equations,',len(tops),'cold5 Top10 and',pairs,'rating predictions.',flush=True)

if __name__=='__main__':main()
