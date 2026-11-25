"""Positive-incidence Item-KNN; train-only graph, validation-only selection."""
import io
import json
import time
import platform
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
from scipy.sparse import csr_matrix
from audit_extended import sha
from prepare_day03 import frozen_write,write_json
from day05_baselines import load_split,ALLOWED,SPLIT,ranking_metrics,paired_ci

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed/day06_item_knn_v1'
OUT=ROOT/'reports/day06_07/item_knn_20261123'

def incidence(train,ids):
    positive=train.loc[train.rating>=4]
    users=np.sort(train.user_id.unique())
    row=np.searchsorted(users,positive.user_id);col=np.searchsorted(ids,positive.book_id)
    if not np.array_equal(ids[col],positive.book_id):raise ValueError('Unknown item')
    return csr_matrix((np.ones(len(row),dtype=np.float64),(row,col)),shape=(len(users),len(ids)))

def neighbors(a,ids,shrinks=(10,100),max_k=200,block=256):
    n=len(ids); freq=np.asarray(a.sum(axis=0)).ravel()
    result={s:(np.full((n,max_k),-1,dtype=np.int32),np.zeros((n,max_k))) for s in shrinks}
    for start in range(0,n,block):
        counts=(a[:,start:start+block].T@a).toarray()
        denom=np.sqrt(freq[start:start+len(counts),None]*freq[None,:])
        cosine=np.divide(counts,denom,out=np.zeros_like(counts),where=denom>0)
        for offset,c in enumerate(counts):
            src=start+offset
            valid=(c>=2);valid[src]=False
            dest=np.flatnonzero(valid)
            for shrink in shrinks:
                sim=cosine[offset,dest]*c[dest]/(c[dest]+shrink)
                order=np.lexsort((ids[dest],-sim))[:max_k]
                chosen=dest[order]; index,weight=result[shrink]
                index[src,:len(chosen)]=chosen;weight[src,:len(chosen)]=sim[order]
        if start%2048==0:print('Graph rows',start,'/',n,flush=True)
    return result

def recommend(profile,ids,index,weight,k,popularity):
    seen={int(b) for b,r in profile}
    sources=[(int(np.searchsorted(ids,b)),r-3) for b,r in profile if r>=4]
    score=np.zeros(len(ids))
    if sources:
        si=np.array([s for s,w in sources]);scale=np.array([w for s,w in sources])
        if np.any(si>=len(ids)) or any(ids[s]!=b for (s,_),(b,r) in zip(sources,[(b,r) for b,r in profile if r>=4])):
            raise ValueError('Unknown profile item')
        target=index[si,:k].ravel();values=(weight[si,:k]*scale[:,None]).ravel()
        good=target>=0
        score=np.bincount(target[good],weights=values[good],minlength=len(ids))
    allowed=~np.isin(ids,list(seen));fallback=not np.any(score[allowed]>0)
    ranking=popularity if fallback else score
    eligible=np.flatnonzero(allowed)
    order=eligible[np.lexsort((ids[eligible],-ranking[eligible]))[:10]]
    return ids[order].tolist(),fallback,int((score[order]<=0).sum())

def evaluate(label,target,profiles,ids,index,weight,k,popularity):
    rows=[];tops=[];timing=[];fallbacks=0;zero=0
    recommend(next(iter(profiles.values())),ids,index,weight,k,popularity)
    for u,g in target.groupby('user_id',sort=True):
        profile=profiles[int(u)]
        start=time.perf_counter_ns();top,fallback,z=recommend(profile,ids,index,weight,k,popularity)
        timing.append((time.perf_counter_ns()-start)/1e6)
        assert len(top)==10 and not set(top)&{b for b,r in profile}
        relevant=set(g.loc[g.rating>=4,'book_id'])
        metric=ranking_metrics(top,relevant)
        rows.append({'user_id':int(u),'positive_targets':len(relevant),**(metric or {'ndcg':None,'recall':None,'precision':None})})
        tops.append({'user_id':int(u),'book_ids':top,'fallback':fallback,'zero_affinity_slots':z})
        fallbacks+=fallback;zero+=z
    valid=[r for r in rows if r['ndcg'] is not None]
    covered={b for r in tops for b in r['book_ids']}
    result={'users':len(rows),'ranking_users':len(valid),'users_without_positive_target':len(rows)-len(valid),
        **{m:float(np.mean([r[m] for r in valid])) for m in ['ndcg','recall','precision']},
        'catalogue_coverage':len(covered)/len(ids),'recommended_distinct_books':len(covered),
        'fallback_users':int(fallbacks),'zero_affinity_top10_slots':int(zero)}
    write_json(DATA/(label+'_users.json'),rows);write_json(DATA/(label+'_top10.json'),tops)
    return result,rows,{'p50_ms':float(np.quantile(timing,.5)),'p95_ms':float(np.quantile(timing,.95)),'users':len(rows)}

def save_array(path,array):
    stream=io.BytesIO();np.save(stream,array,allow_pickle=False);frozen_write(path,stream.getvalue())

def main():
    split_path=ROOT/'reports/day04/split_20261120/manifest.json'
    sm=json.loads(split_path.read_text()); snapshot=ROOT/'reports/day04/split_20261120/protocol_v0.1.md'
    assert sha(snapshot)==sm['protocol_snapshot_sha256']
    baseline_path=ROOT/'reports/day05/baselines_20261123/manifest.json';bm=json.loads(baseline_path.read_text())
    bmetric=ROOT/'reports/day05/baselines_20261123/metrics.json';assert sha(bmetric)==bm['metrics_sha256']
    frames={n:load_split(n,sm) for n in sorted(ALLOWED)}
    train=frames['train.csv'];target=frames['cold_validation_target.csv'];support=frames['cold_validation_support.csv']
    ids=np.sort(frames['catalogue_ids.csv'].book_id.to_numpy())
    assert not set(train.user_id)&set(target.user_id)
    counts=train.groupby('book_id').size();pop=np.array([counts.get(b,0) for b in ids],dtype=float)
    start=time.perf_counter();a=incidence(train,ids);graphs=neighbors(a,ids);fit_seconds=time.perf_counter()-start
    save_array(DATA/'catalogue_ids.npy',ids);save_array(DATA/'popularity.npy',pop)
    for s,(idx,w) in graphs.items():save_array(DATA/f'neighbors_s{s}.npy',idx);save_array(DATA/f'weights_s{s}.npy',w)
    def profiles(k):return {int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in support.loc[support.support_rank<=k].groupby('user_id')}
    p5=profiles(5);grid={};rows5={};timings={}
    for s in (10,100):
        for k in (50,200):
            name=f's{s}_k{k}';print('Validation grid',name,flush=True)
            grid[name],rows5[name],timings[name]=evaluate('cold5_'+name,target,p5,ids,*graphs[s],k,pop)
    chosen=max(grid,key=lambda n:(grid[n]['ndcg'],grid[n]['recall'],-int(n.split('_k')[1]),-int(n.split('_')[0][1:])))
    s=int(chosen.split('_')[0][1:]);k=int(chosen.split('_k')[1]);additional={}
    for size in (3,10):
        label=f'cold_validation_k{size}';print('Selected',label,chosen,flush=True)
        additional[label],_,timings[label]=evaluate(label,target,profiles(size),ids,*graphs[s],k,pop)
    warm_profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in train.groupby('user_id')}
    print('Selected warm_validation',chosen,flush=True)
    additional['warm_validation'],_,timings['warm_validation']=evaluate('warm_validation',frames['warm_validation.csv'],warm_profiles,ids,*graphs[s],k,pop)
    ppath=ROOT/'data/processed/day05_baselines_v1/cold_validation_k5_popularity_users.json'
    assert sha(ppath)==bm['outputs'][str(ppath.relative_to(ROOT))]
    baseline=[r for r in json.loads(ppath.read_text()) if r['ndcg'] is not None]
    selected=[r for r in rows5[chosen] if r['ndcg'] is not None]
    assert [r['user_id'] for r in selected]==[r['user_id'] for r in baseline]
    ci={m:paired_ci([r[m] for r in selected],[r[m] for r in baseline]) for m in ['ndcg','recall']}
    write_json(OUT/'metrics.json',{'grid_cold5':grid,'selected':chosen,'additional':additional,'paired_vs_popularity':ci,
        'baseline_metrics':json.loads(bmetric.read_text())['results'],'ci_scope':'validation post-selection, not independent test',
        'test_evaluated':False,'rating_prediction_metrics':None})
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'timing_latest.json').write_text(json.dumps({'fit_seconds':fit_seconds,'inference':timings,'platform':platform.platform(),
        'scope':'cached graph; score+exclude+full-catalogue sort Top10; single process; excludes load/fit/metrics'},indent=2)+'\n')
    inputs={str((SPLIT/n).relative_to(ROOT)):sha(SPLIT/n) for n in sorted(ALLOWED)}
    for n in ALLOWED:assert sha(SPLIT/n)==sm['outputs'][str((SPLIT/n).relative_to(ROOT))]
    inputs.update({str(p.relative_to(ROOT)):sha(p) for p in [split_path,snapshot,baseline_path,bmetric,ppath,ROOT/'docs/DAY06_ITEM_KNN.md']})
    write_json(OUT/'manifest.json',{'version':'day06_item_knn_v1','inputs':inputs,
        'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(DATA.iterdir()) if p.is_file()},
        'script_sha256':sha(Path(__file__)),'metrics_sha256':sha(OUT/'metrics.json'),
        'numpy':np.__version__,'scipy':scipy.__version__,'pandas':pd.__version__,'train_positive_pairs':int(a.nnz),
        'train_users':int(a.shape[0]),'catalogue_items':len(ids),'test_read_or_evaluated':False})
    print(json.dumps({'chosen':chosen,'grid':grid,'additional':additional,'ci':ci},indent=2),flush=True)

if __name__=='__main__':main()
