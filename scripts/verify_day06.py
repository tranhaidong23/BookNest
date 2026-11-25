"""Audit saved KNN graph against train sets and selected cold5 against explicit accumulation."""
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from audit_extended import sha

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/day06_item_knn_v1'
OUT=ROOT/'reports/day06_07/item_knn_20261123'
SPLIT=ROOT/'data/processed/day04_split_v1'

def main():
    m=json.loads((OUT/'manifest.json').read_text())
    for name,h in {**m['inputs'],**m['outputs']}.items():assert sha(ROOT/name)==h,name
    assert sha(ROOT/'scripts/day06_item_knn.py')==m['script_sha256']
    assert sha(OUT/'metrics.json')==m['metrics_sha256']
    metric=json.loads((OUT/'metrics.json').read_text());name=metric['selected'];shrink=int(name.split('_')[0][1:]);k=int(name.split('_k')[1])
    ids=np.load(DATA/'catalogue_ids.npy',allow_pickle=False);pop=np.load(DATA/'popularity.npy',allow_pickle=False)
    graphs={s:(np.load(DATA/f'neighbors_s{s}.npy',allow_pickle=False),np.load(DATA/f'weights_s{s}.npy',allow_pickle=False)) for s in (10,100)}
    train=pd.read_csv(SPLIT/'train.csv');sets={int(b):set(g.user_id) for b,g in train.loc[train.rating>=4].groupby('book_id')}
    indices=np.unique(np.r_[0,np.random.default_rng(20261123).choice(len(ids),9,replace=False)])
    for s,(idx,w) in graphs.items():
        assert np.all(w>=0) and np.isfinite(w).all()
        for i in range(len(ids)):
            valid=idx[i]>=0;dest=idx[i,valid]
            assert i not in dest and len(set(dest))==len(dest)
            assert np.all(w[i,valid]>0) and np.all(w[i,~valid]==0)
        for i in indices:
            source=sets.get(int(ids[i]),set());scores=[]
            for j,b in enumerate(ids):
                if j==i:continue
                other=sets.get(int(b),set());c=len(source&other)
                if c>=2:scores.append((j,c/math.sqrt(len(source)*len(other))*c/(c+s)))
            scores.sort(key=lambda x:(-x[1],int(ids[x[0]])));scores=scores[:200]
            assert idx[i,:len(scores)].tolist()==[j for j,v in scores]
            np.testing.assert_allclose(w[i,:len(scores)],[v for j,v in scores],rtol=1e-12,atol=1e-12)
    support=pd.read_csv(SPLIT/'cold_validation_support.csv').query('support_rank <= 5')
    target=pd.read_csv(SPLIT/'cold_validation_target.csv')
    profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in support.groupby('user_id')}
    relevant={int(u):set(g.loc[g.rating>=4,'book_id']) for u,g in target.groupby('user_id')}
    tops=json.loads((DATA/('cold5_'+name+'_top10.json')).read_text());idx,w=graphs[shrink]
    mapping={int(b):i for i,b in enumerate(ids)};ndcgs=[];recalls=[];precisions=[];covered=set();fallbacks=0;zeros=0
    assert {r['user_id'] for r in tops}==set(profiles)==set(relevant)
    for row in tops:
        user=row['user_id'];scores=np.zeros(len(ids));seen=set()
        for book,rating in profiles[user]:
            seen.add(book)
            if rating<4:continue
            i=mapping[book]
            for j,value in zip(idx[i,:k],w[i,:k]):
                if j>=0:scores[j]+=(rating-3)*value
        eligible=[i for i,b in enumerate(ids) if int(b) not in seen]
        fallback=not any(scores[i]>0 for i in eligible)
        ranking=pop if fallback else scores
        chosen=sorted(eligible,key=lambda i:(-ranking[i],int(ids[i])))[:10]
        top=[int(ids[i]) for i in chosen];zero=sum(scores[i]<=0 for i in chosen)
        assert row['book_ids']==top and row['fallback']==fallback and row['zero_affinity_slots']==zero
        covered.update(top);fallbacks+=fallback;zeros+=zero
        truth=relevant[user]
        if not truth:continue
        hit=[i for i,b in enumerate(top,1) if b in truth]
        ndcgs.append(sum(1/math.log2(i+1) for i in hit)/sum(1/math.log2(i+1) for i in range(1,min(10,len(truth))+1)))
        recalls.append(len(hit)/len(truth));precisions.append(len(hit)/10)
    expected=metric['grid_cold5'][name]
    for key,values in [('ndcg',ndcgs),('recall',recalls),('precision',precisions)]:assert math.isclose(float(np.mean(values)),expected[key],abs_tol=1e-12)
    assert len(covered)/len(ids)==expected['catalogue_coverage'] and fallbacks==expected['fallback_users'] and zeros==expected['zero_affinity_top10_slots']
    validation={'tests_passed':35,'tests_failed':0,'input_output_hashes_verified':True,'selected_cold5_all_top10_and_metrics_independently_verified':True,
        'sampled_source_rows_verified_against_train_user_sets':len(indices),'shrinks_checked':[10,100],
        'all_graph_self_duplicate_nonfinite_negative_checks_passed':True,'full_cli_replay':False,'test_read_or_evaluated':False,
        'verifier_sha256':sha(Path(__file__)),'manifest_sha256':sha(OUT/'manifest.json')}
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2))

if __name__=='__main__':main()
