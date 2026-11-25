"""Exercise the actual Python repository over SCRAM PostgreSQL connections."""
import sys
import json
from pathlib import Path
from uuid import UUID
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from local_postgres_fixture import native_cluster
from booknest.repository import PostgresRepository,StorageError,StaleProfileError
from audit_extended import sha
import psycopg

A=UUID('10000000-0000-0000-0000-000000000001');B=UUID('10000000-0000-0000-0000-000000000002')
OUT=ROOT/'reports/day12_14/postgres_repository_20261123'

def fails(kind,call):
    try:call()
    except kind:return
    raise AssertionError('Expected '+kind.__name__)

def main():
    checks=[]
    with native_cluster() as (owner,connect):
        with owner() as c:
            version=c.execute('SELECT version()').fetchone()[0]
            c.execute("INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES(%s,'synthetic','a','Alice'),(%s,'synthetic','b','Bob')",(A,B))
            for i in range(1,5):
                c.execute("INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url) VALUES(%s,%s,'Synthetic author','https://example.invalid/source','test',%s,%s)",(i,'Synthetic book '+str(i),'pending' if i==4 else 'approved',None if i==4 else 'https://example.invalid/evidence'))
        a=PostgresRepository(connect,A);b=PostgresRepository(connect,B)
        assert a.profile()['display_name']=='Alice' and b.profile()['display_name']=='Bob';checks.append('own profile persisted and isolated')
        a.save_rating(1,5);b.save_rating(1,2);a.save_rating(1,4)
        assert a.ratings()=={1:4} and b.ratings()=={1:2};checks.append('upsert ratings survive fresh connections and stay isolated')
        assert PostgresRepository(connect,A).ratings()=={1:4};checks.append('new repository instance reads durable state')
        assert a.delete_rating(1) and a.ratings()=={} and not a.delete_rating(1) and b.ratings()=={1:2};a.save_rating(1,5);checks.append('delete is missing not zero and cannot affect another user')
        a.save_shelf(2,'reading');b.save_shelf(2,'finished');a.save_shelf(2,'want_to_read')
        assert a.shelf()=={2:'want_to_read'} and b.shelf()=={2:'finished'}
        assert a.delete_shelf(2) and not a.shelf() and b.shelf()=={2:'finished'};checks.append('shelf CRUD isolated and persistent')
        assert len(a.search_catalogue())==3 and a.search_catalogue('%')==[] and a.search_catalogue("'; DROP TABLE booknest.books; --")==[];checks.append('public catalogue gate and literal search wildcards')
        payload="Alice'; DROP TABLE booknest.app_users; --";a.update_display_name(payload)
        assert a.profile()['display_name']==payload and b.profile()['display_name']=='Bob';checks.append('bound parameters keep SQL-like display names literal')
        fails(StorageError,lambda:a.save_rating(4,4));assert a.ratings()=={1:5};checks.append('pending metadata write rejected without partial rating changes')
        fails(StorageError,lambda:PostgresRepository(owner,A).ratings());checks.append('repository refuses migration owner credentials')
        fails(StorageError,lambda:PostgresRepository(connect,UUID(int=9)).ratings());checks.append('unprovisioned identity rejected')
        items=[{'book_id':2,'explanation':'Synthetic test evidence'},{'book_id':3,'explanation':'Synthetic test evidence'}]
        run=a.save_run([(1,5)],items,'synthetic-model','synthetic-catalogue')
        history=PostgresRepository(connect,A).history();assert len(history)==1 and len(history[0]['items'])==2 and history[0]['profile']==[{'book_id':1,'rating':5}]
        assert b.history()==[] and not b.delete_run(run);checks.append('run items and support snapshot persist with cross-user history isolation')
        a.save_rating(1,4);assert a.history()[0]['profile']==[{'book_id':1,'rating':5}]
        fails(StaleProfileError,lambda:a.save_run([(1,5)],items,'test','test'));assert len(a.history())==1;checks.append('immutable snapshot and stale profile rejection')
        fails(StorageError,lambda:a.save_run([(1,4)],[items[0],{'book_id':4,'explanation':'Pending book must fail'}],'test','test'))
        assert len(a.history())==1
        with owner() as c:
            assert c.execute('SELECT count(*) FROM booknest.recommendation_runs').fetchone()[0]==1
            assert c.execute('SELECT count(*) FROM booknest.recommendation_support').fetchone()[0]==1
            assert c.execute('SELECT count(*) FROM booknest.recommendation_items').fetchone()[0]==2
        checks.append('run support and items atomically roll back on late item failure')
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures=[executor.submit(repo.save_rating,1,rating) for _ in range(4) for repo,rating in ((a,5),(b,2))]
            for f in futures:f.result()
        assert a.ratings()=={1:5} and b.ratings()=={1:2};checks.append('eight concurrent writes across fresh connections stay isolated')
        assert a.delete_run(run) and a.history()==[]
        with owner() as c:
            assert c.execute('SELECT count(*) FROM booknest.recommendation_support').fetchone()[0]==0
            assert c.execute('SELECT count(*) FROM booknest.recommendation_items').fetchone()[0]==0
        checks.append('owned history deletion cascades snapshot and items')
        with connect() as c:
            assert c.execute("SELECT nullif(current_setting('booknest.user_id',true),'')").fetchone()[0] is None
            assert c.execute('SELECT count(*) FROM booknest.user_ratings').fetchone()[0]==0
        checks.append('fresh runtime connection has no leaked user context')
    OUT.mkdir(parents=True,exist_ok=True)
    sources=['booknest/repository.py','scripts/local_postgres_fixture.py','scripts/verify_repository.py','db/migrations/001_initial.sql','db/migrations/002_recommendation_support.sql']
    (OUT/'validation.json').write_text(json.dumps({'engine':version,'psycopg':psycopg.__version__,'checks_passed':len(checks),'checks':checks,
        'isolated_cluster_stopped_and_removed':True,'app_ui_connected':False,'oidc_verified':False,'neon_connected':False,
        'sources_sha256':{p:sha(ROOT/p) for p in sources}},indent=2)+'\n',encoding='utf-8')
    print('Passed',len(checks),'repository integration checks; isolated cluster stopped and removed.')

if __name__=='__main__':main()
