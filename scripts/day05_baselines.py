"""Train-only baselines; validation only. Test paths are rejected by the loader."""
import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np
import pandas as pd
from audit_extended import sha
from prepare_day03 import frozen_write, write_json

ROOT=Path(__file__).resolve().parents[1]
SPLIT=ROOT/'data/processed/day04_split_v1'
OUT=ROOT/'reports/day05/baselines_20261123'
DATA=ROOT/'data/processed/day05_baselines_v1'
ALLOWED={'train.csv','warm_validation.csv','cold_validation_support.csv','cold_validation_target.csv','catalogue_ids.csv'}

def load_split(name,manifest):
    if name not in ALLOWED: raise ValueError('Not an approved Day5 input: '+name)
    p=SPLIT/name
    if sha(p)!=manifest['outputs'][str(p.relative_to(ROOT))]: raise ValueError('Split hash mismatch')
    return pd.read_csv(p,dtype='int64')

def fit_bias(train,lam,iterations=10):
    users=np.sort(train.user_id.unique()); items=np.sort(train.book_id.unique())
    ui=np.searchsorted(users,train.user_id); ii=np.searchsorted(items,train.book_id)
    r=train.rating.to_numpy(dtype=float); mu=float(r.mean())
    uc=np.bincount(ui); ic=np.bincount(ii)
    bu=np.zeros(len(users)); bi=np.zeros(len(items)); objectives=[]
    for _ in range(iterations):
        bu=np.bincount(ui,weights=r-mu-bi[ii])/(uc+lam)
        bi=np.bincount(ii,weights=r-mu-bu[ui])/(ic+lam)
        residual=r-mu-bu[ui]-bi[ii]
        objectives.append(float(residual@residual+lam*(bu@bu+bi@bi)))
    return {'mu':mu,'lambda':lam,'users':dict(zip(map(int,users),map(float,bu))),
            'items':dict(zip(map(int,items),map(float,bi))),'objectives':objectives}

def cold_bias(support,model):
    return float(sum(float(r)-model['mu']-model['items'].get(int(b),0.) for b,r in support)/(model['lambda']+len(support)))

def top_k(order,seen,k=10):
    found=[]
    for b in order:
        b=int(b)
        if b not in seen:
            found.append(b)
            if len(found)==k: break
    return found

def ranking_metrics(top,relevant,k=10):
    if len(top)!=len(set(top)): raise ValueError('Duplicate recommendations')
    if not relevant: return None
    hits=np.array([int(b in relevant) for b in top[:k]])
    dcg=float((hits/np.log2(np.arange(len(hits))+2)).sum())
    ideal=float((1/np.log2(np.arange(min(k,len(relevant)))+2)).sum())
    return {'ndcg':dcg/ideal,'recall':float(hits.sum()/len(relevant)),'precision':float(hits.sum()/k)}

def paired_ci(a,b):
    delta=np.asarray(a)-np.asarray(b); rng=np.random.default_rng(20261121)
    means=[float(delta[rng.integers(0,len(delta),size=len(delta))].mean()) for _ in range(1000)]
    return {'mean_delta':float(delta.mean()),'percentile_95':np.quantile(means,[.025,.975]).tolist(),'users':len(delta)}

def evaluate(label,target,profiles,catalogue,models,counts,mu,cold):
    orders={'popularity':sorted(catalogue,key=lambda b:(-counts.get(b,0),b))}
    for name,m in models.items():
        orders[name]=sorted(catalogue,key=lambda b:(-m['items'].get(b,0.),b))
    rows={n:[] for n in orders}; recs={n:[] for n in orders}; times={n:[] for n in orders}
    errors={n:[0.,0.,0] for n in ['global_mean',*models]}
    for order in orders.values(): top_k(order,set())
    for user,g in target.groupby('user_id',sort=True):
        profile=profiles[int(user)]; seen={b for b,r in profile}
        books=g.book_id.to_numpy(); truth=g.rating.to_numpy(dtype=float)
        relevant=set(g.loc[g.rating>=4,'book_id'])
        for name,order in orders.items():
            start=time.perf_counter_ns(); top=top_k(order,seen); elapsed=time.perf_counter_ns()-start
            assert len(top)==10 and not seen.intersection(top)
            times[name].append(elapsed/1e6)
            metric=ranking_metrics(top,relevant)
            rows[name].append({'user_id':int(user),'positive_targets':len(relevant),**(metric or {'ndcg':None,'recall':None,'precision':None})})
            recs[name].append({'user_id':int(user),'book_ids':top})
        predictions={'global_mean':np.full(len(g),mu)}
        for name,m in models.items():
            ub=cold_bias(profile,m) if cold else m['users'].get(int(user),0.)
            predictions[name]=np.clip(m['mu']+ub+np.array([m['items'].get(int(b),0.) for b in books]),1,5)
        for name,pred in predictions.items():
            diff=pred-truth
            errors[name][0]+=float(diff@diff); errors[name][1]+=float(np.abs(diff).sum()); errors[name][2]+=len(diff)
    result={}
    timing={}
    for name,rr in rows.items():
        valid=[r for r in rr if r['ndcg'] is not None]
        distinct={b for rec in recs[name] for b in rec['book_ids']}
        result[name]={'users':len(rr),'ranking_users':len(valid),'users_without_positive_target':len(rr)-len(valid),
                      **{k:float(np.mean([r[k] for r in valid])) for k in ['ndcg','recall','precision']},
                      'catalogue_coverage':len(distinct)/len(catalogue),'recommended_distinct_books':len(distinct)}
        timing[name]={'p50_ms':float(np.quantile(times[name],.5)),'p95_ms':float(np.quantile(times[name],.95)),'users':len(rr)}
        write_json(DATA/f'{label}_{name}_users.json',rr)
        write_json(DATA/f'{label}_{name}_top10.json',recs[name])
    for name,(sq,ab,n) in errors.items():
        result.setdefault(name,{})['rating_metrics']={'rmse':float(np.sqrt(sq/n)),'mae':ab/n,'pairs':n}
    return result,rows,timing

def main():
    split_manifest=ROOT/'reports/day04/split_20261120/manifest.json'
    manifest=json.loads(split_manifest.read_text(encoding='utf-8'))
    snapshot=ROOT/'reports/day04/split_20261120/protocol_v0.1.md'
    assert sha(snapshot)==manifest['protocol_snapshot_sha256']
    frames={n:load_split(n,manifest) for n in sorted(ALLOWED)}
    train=frames['train.csv']; warm=frames['warm_validation.csv']; support=frames['cold_validation_support.csv']; target=frames['cold_validation_target.csv']
    catalogue=sorted(map(int,frames['catalogue_ids.csv'].book_id))
    assert not set(train.user_id)&set(target.user_id)
    assert set(support.user_id)==set(target.user_id)
    assert not set(zip(support.user_id,support.book_id))&set(zip(target.user_id,target.book_id))
    counts={int(k):int(v) for k,v in train.groupby('book_id').size().items()}; mu=float(train.rating.mean())
    models={}; fit_times={}
    for lam in (10,50):
        name=f'bias_l{lam}'; print('Fit',name,'on train only',flush=True)
        start=time.perf_counter(); models[name]=fit_bias(train,lam); fit_times[name]=time.perf_counter()-start
        assert all(a>=b-1e-7 for a,b in zip(models[name]['objectives'],models[name]['objectives'][1:]))
        write_json(DATA/(name+'.json'),models[name])
    write_json(DATA/'popularity.json',{'counts':counts,'train_mean':mu})
    results={}; rows5=None; timings={}
    for k in (3,5,10):
        label=f'cold_validation_k{k}'
        profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in support.loc[support.support_rank<=k].groupby('user_id')}
        print('Evaluate',label,flush=True)
        results[label],rows,timings[label]=evaluate(label,target,profiles,catalogue,models,counts,mu,True)
        if k==5: rows5=rows
    profiles={int(u):list(zip(map(int,g.book_id),map(int,g.rating))) for u,g in train.groupby('user_id')}
    print('Evaluate warm_validation',flush=True)
    results['warm_validation'],_,timings['warm_validation']=evaluate('warm_validation',warm,profiles,catalogue,models,counts,mu,False)
    chosen=max(models,key=lambda n:(results['cold_validation_k5'][n]['ndcg'],results['cold_validation_k5'][n]['recall'],-models[n]['lambda']))
    paired={}
    a=[r for r in rows5[chosen] if r['ndcg'] is not None]; b=[r for r in rows5['popularity'] if r['ndcg'] is not None]
    assert [r['user_id'] for r in a]==[r['user_id'] for r in b]
    for metric in ['ndcg','recall']:
        paired[metric]=paired_ci([r[metric] for r in a],[r[metric] for r in b])
    write_json(OUT/'metrics.json',{'results':results,'selected_bias':chosen,'selection':'cold-validation k5 NDCG then Recall',
        'paired_bootstrap_vs_popularity':paired,'bootstrap_scope':'validation, post-selection; not independent test evidence',
        'train_rows':len(train),'train_mean':mu,'test_evaluated':False})
    # Timings intentionally separate from deterministic artifacts.
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'timing_latest.json').write_text(json.dumps({'fit_seconds':fit_times,'inference':timings,'platform':platform.platform(),
        'processor':platform.processor(),'scope':'single process cached static order lookup/filter/Top10; excludes fit/load/metrics/serialization'},indent=2)+'\n',encoding='utf-8')
    for n in ALLOWED: assert sha(SPLIT/n)==manifest['outputs'][str((SPLIT/n).relative_to(ROOT))]
    inputs={str((SPLIT/n).relative_to(ROOT)):sha(SPLIT/n) for n in sorted(ALLOWED)}
    inputs.update({str(p.relative_to(ROOT)):sha(p) for p in [split_manifest,snapshot,ROOT/'docs/DAY05_BASELINES.md']})
    write_json(OUT/'manifest.json',{'version':'day05_baselines_v1','inputs':inputs,
        'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(DATA.glob('*.json'))},
        'metrics_sha256':sha(OUT/'metrics.json'),'script_sha256':sha(Path(__file__)),
        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
        'input_allowlist':sorted(ALLOWED),'test_files_read':False,'models_trained':True,'test_evaluated':False})
    print(json.dumps({'selected_bias':chosen,'cold_validation_k5':results['cold_validation_k5'],'paired':paired},indent=2),flush=True)

if __name__=='__main__': main()
