"""Local synthetic workload, not cloud capacity or recommender quality evaluation."""
import hashlib
import json
import os
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from uuid import UUID
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from local_postgres_fixture import native_cluster
from booknest.recommender import Recommender
from booknest.repository import PostgresRepository
from booknest.account_service import approved_catalogue,product_recommendations,create_saved_recommendations
OUT=ROOT/'reports/day16_17/local_performance_20261123'

def measure(fn,count):
    samples=[]
    for _ in range(count):
        start=time.perf_counter();fn();samples.append((time.perf_counter()-start)*1000)
    return {'n':count,'median_ms':float(np.median(samples)),'p95_ms':float(np.percentile(samples,95)),
        'min_ms':min(samples),'max_ms':max(samples),'samples_ms':samples}

def main():
    start=time.perf_counter();engine=Recommender();load_ms=(time.perf_counter()-start)*1000
    memory=sum(a.nbytes for a in (engine.ids,engine.popularity,engine.index,engine.weight))
    rng=np.random.default_rng(20261123)
    profiles={k:[[(int(b),int(r)) for b,r in zip(rng.choice(engine.ids,size=k,replace=False),rng.integers(1,6,size=k))] for _ in range(100)] for k in (3,5,10)}
    catalogue={int(b):{'title':'Synthetic book '+str(b)} for b in engine.ids};timing={}
    for k,rows in profiles.items():
        for profile in rows[:5]:engine.recommend(profile);product_recommendations(engine,profile,catalogue)
        for name,fn in [('frozen_engine',lambda p:engine.recommend(p)),('product_engine',lambda p:product_recommendations(engine,p,catalogue))]:
            iterator=iter(rows);timing[name+'_support_'+str(k)]=measure(lambda:fn(next(iterator)),100)
    with native_cluster() as (owner,runtime):
        identities=[UUID(int=300+i) for i in range(2)]
        with owner() as c:
            version=c.execute('SELECT version()').fetchone()[0]
            with c.cursor() as cur:
                cur.executemany("INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES(%s,'synthetic',%s,'Synthetic user')",[(uid,str(uid)) for uid in identities])
            c.execute("INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url) SELECT i,'Synthetic book '||i,'Synthetic author','https://example.invalid/source','synthetic-v1','approved','https://example.invalid/evidence' FROM generate_series(1,10000) i")
        connection_count=0
        def counted():
            nonlocal connection_count
            connection_count+=1;return runtime()
        repo=PostgresRepository(counted,identities[0]);other=PostgresRepository(runtime,identities[1])
        def legacy_pages():
            result={};offset=0
            while True:
                rows=repo.search_catalogue(limit=100,offset=offset)
                result.update({r['book_id']:r for r in rows})
                if len(rows)<100:return result
                offset+=100
        before=connection_count;legacy=legacy_pages();legacy_connections=connection_count-before
        before=connection_count;current=approved_catalogue(repo);snapshot_connections=connection_count-before
        assert legacy==current and len(current)==10000
        timing['catalogue_legacy_101_connections']=measure(legacy_pages,3)
        timing['catalogue_snapshot_1_connection']=measure(lambda:approved_catalogue(repo),20)
        for target in (repo,other):
            for b,r in [(1,5),(2,4),(3,2),(4,5),(5,3)]:target.save_rating(b,r)
        timing['rating_upsert_fresh_connection']=measure(lambda:repo.save_rating(1,5),20)
        timing['recommend_and_persist_cached_catalogue']=measure(lambda:create_saved_recommendations(repo,engine,current),20)
        with ThreadPoolExecutor(max_workers=4) as pool:
            start=time.perf_counter()
            results=list(pool.map(lambda i:create_saved_recommendations(repo if i%2==0 else other,engine,current),range(20)))
            parallel_ms=(time.perf_counter()-start)*1000
        assert len({r['run_id'] for r in results})==20
        assert len(repo.history(limit=100))==30 and len(other.history(limit=100))==10
        with owner() as c:c.execute("UPDATE booknest.books SET metadata_status='pending' WHERE book_id=10000")
        assert 10000 not in approved_catalogue(repo)
    result={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),
        'python':platform.python_version(),'numpy':np.__version__,'logical_cpu_count':os.cpu_count(),
        'postgres':version,'model_load_with_hash_ms':load_ms,'model_array_bytes':memory,
        'profile_seed':20261123,'synthetic_profiles':True,'synthetic_catalogue_rows':10000,
        'timing':timing,'catalogue_parity':True,'connections_per_load':{'previous':legacy_connections,'current':snapshot_connections},
        'concurrent_save':{'workers':4,'accounts':2,'operations':20,'wall_ms':parallel_ms,'distinct_runs':20,'owner_counts':[30,10]},
        'revocation_visible_next_snapshot':True,'cluster_stopped_and_removed':True,
        'scope_excludes':['OIDC','browser rendering','Neon','Render','network WAN','AI','sustained load','test metrics'],
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['scripts/benchmark_local.py','booknest/recommender.py','booknest/account_service.py','booknest/repository.py']}}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'benchmark.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:{'median_ms':v['median_ms'],'p95_ms':v['p95_ms'],'n':v['n']} for k,v in timing.items()},indent=2))
    print('All parity, revocation and concurrent ownership checks passed; temporary cluster removed.')

if __name__=='__main__':main()
