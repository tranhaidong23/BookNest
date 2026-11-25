"""Observed-only residual MF with train biases fixed; validation-only fold-in."""
import os
for _key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[_key]='1'
import json
import time
import platform
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from audit_extended import sha
from prepare_day03 import write_json
from day05_baselines import load_split,ALLOWED,SPLIT,ranking_metrics,paired_ci
from day06_item_knn import save_array

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/day08_09/mf_20261123'
DATA=ROOT/'data/processed/day08_mf_v1'

def ridge(design,response,lam):
    if lam<=0: raise ValueError('Positive regularization required')
    return np.linalg.solve(design.T@design+lam*np.eye(design.shape[1]),design.T@response)

def update_rows(observed,other,lam):
    result=np.zeros((observed.shape[0],other.shape[1]))
    for row in range(observed.shape[0]):
        lo,hi=observed.indptr[row:row+2]
        result[row]=ridge(other[observed.indices[lo:hi]],observed.data[lo:hi],lam)
    return result

def objective(matrix,p,q,lam):
    total=lam*(np.square(p).sum()+np.square(q).sum())
    for u in range(matrix.shape[0]):
        lo,hi=matrix.indptr[u:u+2]
        residual=matrix.data[lo:hi]-q[matrix.indices[lo:hi]]@p[u]
        total+=residual@residual
    return float(total)

def fit(matrix,dimension,lam,epochs=8):
    p=np.zeros((matrix.shape[0],dimension))
    q=np.random.default_rng(20261123).normal(0,.1,size=(matrix.shape[1],dimension))
    transpose=matrix.T.tocsr(); trace=[objective(matrix,p,q,lam)]
    for epoch in range(epochs):
        p=update_rows(matrix,q,lam);q=update_rows(transpose,p,lam)
        loss=objective(matrix,p,q,lam)
        assert loss<=trace[-1]+max(1e-7,1e-10*trace[-1]),'ALS objective increased'
        trace.append(loss)
        print('ALS',dimension,lam,'epoch',epoch+1,'objective',round(loss,4),flush=True)
    return p,q,trace

def fold_in(indices,ratings,q,bi,mu,lam):
    indices=np.asarray(indices,dtype=int);r=np.asarray(ratings,dtype=float)
    ub=float(np.sum(r-mu-bi[indices])/(50+len(indices)))
    vector=ridge(q[indices],r-mu-bi[indices]-ub,lam)
    return vector,ub

def score_all(profile,ids,q,bi,mu,lam,warm_vector=None,warm_bias=None):
    mapping=np.searchsorted(ids,[b for b,r in profile])
    if np.any(mapping>=len(ids)) or not np.array_equal(ids[mapping],[b for b,r in profile]):
        raise ValueError('Unknown profile item')
    if warm_vector is None:
        vector,ub=fold_in(mapping,[r for b,r in profile],q,bi,mu,lam)
    else: vector,ub=warm_vector,float(warm_bias)
    scores=mu+ub+bi+q@vector
    eligible=np.ones(len(ids),dtype=bool);eligible[mapping]=False
    choices=np.flatnonzero(eligible)
    order=choices[np.lexsort((ids[choices],-scores[choices]))[:10]]
    return ids[order].tolist(),scores

def evaluate(label,target,profiles,ids,q,bi,mu,lam,p=None,users=None,bu=None):
    rows=[];tops=[];times=[];squared=absolute=0.;pairs=0;clipped=0
    user_index={} if users is None else {int(u):i for i,u in enumerate(users)}
    def run(user,profile):
        u=user_index.get(int(user))
        return score_all(profile,ids,q,bi,mu,lam,None if p is None else p[u],None if p is None else bu[u])
    first=int(target.user_id.iloc[0]);run(first,profiles[first])
    for user,g in target.groupby('user_id',sort=True):
        profile=profiles[int(user)]
        start=time.perf_counter_ns();top,scores=run(user,profile);times.append((time.perf_counter_ns()-start)/1e6)
        assert len(top)==10 and not set(top)&{b for b,r in profile}
        rel=set(g.loc[g.rating>=4,'book_id']);metric=ranking_metrics(top,rel)
        rows.append({'user_id':int(user),'positive_targets':len(rel),**(metric or {'ndcg':None,'recall':None,'precision':None})})
        tops.append({'user_id':int(user),'book_ids':top})
        indices=np.searchsorted(ids,g.book_id.to_numpy());raw=scores[indices]
        diff=np.clip(raw,1,5)-g.rating.to_numpy(dtype=float)
        squared+=float(diff@diff);absolute+=float(np.abs(diff).sum());pairs+=len(diff)
        clipped+=int(((raw<1)|(raw>5)).sum())
    valid=[r for r in rows if r['ndcg'] is not None];covered={b for t in tops for b in t['book_ids']}
    result={'users':len(rows),'ranking_users':len(valid),'users_without_positive_target':len(rows)-len(valid),
        **{m:float(np.mean([r[m] for r in valid])) for m in ['ndcg','recall','precision']},
        'catalogue_coverage':len(covered)/len(ids),'recommended_distinct_books':len(covered),
        'rating_metrics':{'rmse':float(np.sqrt(squared/pairs)),'mae':absolute/pairs,'pairs':pairs,'clipped_predictions':clipped}}
    write_json(DATA/(label+'_users.json'),rows);write_json(DATA/(label+'_top10.json'),tops)
    return result,rows,{'p50_ms':float(np.quantile(times,.5)),'p95_ms':float(np.quantile(times,.95)),'users':len(rows)}

def main():
    split_path=ROOT/'reports/day04/split_20261120/manifest.json';sm=json.loads(split_path.read_text())
    snapshot=ROOT/'reports/day04/split_20261120/protocol_v0.1.md';assert sha(snapshot)==sm['protocol_snapshot_sha256']
    bpath=ROOT/'reports/day05/baselines_20261123/manifest.json';bm=json.loads(bpath.read_text())
    bias_path=ROOT/'data/processed/day05_baselines_v1/bias_l50.json';assert sha(bias_path)==bm['outputs'][str(bias_path.relative_to(ROOT))]
    bias=json.loads(bias_path.read_text())
    kpath=ROOT/'reports/day06_07/item_knn_20261123/manifest.json';km=json.loads(kpath.read_text())
    kmetric=ROOT/'reports/day06_07/item_knn_20261123/metrics.json';assert sha(kmetric)==km['metrics_sha256']
    frames={n:load_split(n,sm) for n in sorted(ALLOWED)}
    train=frames['train.csv'];target=frames['cold_validation_target.csv'];support=frames['cold_validation_support.csv']
    ids=np.sort(frames['catalogue_ids.csv'].book_id.to_numpy());users=np.sort(train.user_id.unique())
    assert not set(users)&set(target.user_id)
    assert not set(zip(support.user_id,support.book_id))&set(zip(target.user_id,target.book_id))
    mu=bias['mu'];bu=np.array([bias['users'].get(str(u),0.) for u in users]);bi=np.array([bias['items'].get(str(i),0.) for i in ids])
    ui=np.searchsorted(users,train.user_id);ii=np.searchsorted(ids,train.book_id)
    residual=train.rating.to_numpy(dtype=float)-mu-bu[ui]-bi[ii]
    matrix=csr_matrix((residual,(ui,ii)),shape=(len(users),len(ids)))
    assert matrix.nnz==len(train) # preserve observed zero residuals
    for name,array in [('user_ids',users),('catalogue_ids',ids),('user_bias',bu),('item_bias',bi)]:save_array(DATA/(name+'.npy'),array)
    def profiles(size):return {int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in support.loc[support.support_rank<=size].groupby('user_id')}
    p5=profiles(5);grid={};allrows={};times={};traces={}
    for dimension in (16,32):
        for lam in (10,50):
            name=f'd{dimension}_l{lam}';print('Fit MF',name,flush=True)
            start=time.perf_counter();p,q,trace=fit(matrix,dimension,lam);fit_time=time.perf_counter()-start
            save_array(DATA/(name+'_P.npy'),p);save_array(DATA/(name+'_Q.npy'),q);traces[name]=trace
            print('Validate cold5',name,flush=True)
            grid[name],allrows[name],timing=evaluate('cold5_'+name,target,p5,ids,q,bi,mu,lam)
            times[name]={'fit_seconds':fit_time,'inference':timing}
    chosen=max(grid,key=lambda n:(grid[n]['ndcg'],grid[n]['recall'],-int(n.split('_')[0][1:]),-int(n.split('_')[1][1:])))
    lam=int(chosen.split('_')[1][1:]);p=np.load(DATA/(chosen+'_P.npy'));q=np.load(DATA/(chosen+'_Q.npy'))
    additional={}
    for size in (3,10):
        label=f'cold_validation_k{size}';print('Selected',chosen,label,flush=True)
        additional[label],_,times[label]=evaluate(label,target,profiles(size),ids,q,bi,mu,lam)
    warm_profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in train.groupby('user_id')}
    print('Selected warm_validation',chosen,flush=True)
    additional['warm_validation'],_,times['warm_validation']=evaluate('warm_validation',frames['warm_validation.csv'],warm_profiles,ids,q,bi,mu,lam,p,users,bu)
    kp=json.loads(kmetric.read_text())['selected']
    comparison_paths={'popularity':ROOT/'data/processed/day05_baselines_v1/cold_validation_k5_popularity_users.json',
                      'item_knn':ROOT/f'data/processed/day06_item_knn_v1/cold5_{kp}_users.json'}
    selected=[r for r in allrows[chosen] if r['ndcg'] is not None];cis={}
    for name,path in comparison_paths.items():
        expected=(bm if name=='popularity' else km)['outputs'][str(path.relative_to(ROOT))];assert sha(path)==expected
        base=[r for r in json.loads(path.read_text()) if r['ndcg'] is not None]
        assert [r['user_id'] for r in selected]==[r['user_id'] for r in base]
        cis[name]={metric:paired_ci([r[metric] for r in selected],[r[metric] for r in base]) for metric in ['ndcg','recall']}
    write_json(OUT/'metrics.json',{'grid_cold5':grid,'selected':chosen,'additional':additional,'paired_delta_vs':cis,
        'ci_scope':'validation post-selection, not independent test','train_rows':len(train),'train_users':len(users),
        'mu':mu,'fixed_bias_lambda':50,'als_epochs':8,'seed':20261123,
        'catalogue_items_without_train':int(len(ids)-train.book_id.nunique()),'test_evaluated':False})
    write_json(OUT/'training_objectives.json',traces)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'timing_latest.json').write_text(json.dumps({'runs':times,'platform':platform.platform(),'blas_threads_requested':1,
        'scope':'cold fold-in + all scores + exclude + full sort Top10; warm stored user factor; excludes load/fit/metrics'},indent=2)+'\n')
    for n in ALLOWED:assert sha(SPLIT/n)==sm['outputs'][str((SPLIT/n).relative_to(ROOT))]
    inputs={str((SPLIT/n).relative_to(ROOT)):sha(SPLIT/n) for n in sorted(ALLOWED)}
    inputs.update({str(p.relative_to(ROOT)):sha(p) for p in [split_path,snapshot,bpath,bias_path,kpath,kmetric,*comparison_paths.values(),ROOT/'docs/DAY08_MATRIX_FACTORIZATION.md']})
    write_json(OUT/'manifest.json',{'version':'day08_mf_v1','inputs':inputs,'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(DATA.iterdir()) if p.is_file()},
        'script_sha256':sha(Path(__file__)),'metrics_sha256':sha(OUT/'metrics.json'),'objectives_sha256':sha(OUT/'training_objectives.json'),
        'numpy':np.__version__,'pandas':pd.__version__,'test_read_or_evaluated':False})
    print(json.dumps({'chosen':chosen,'grid':grid,'additional':additional,'ci':cis},indent=2),flush=True)

if __name__=='__main__':main()
