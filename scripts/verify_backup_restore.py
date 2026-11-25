"""Synthetic pg_dump/pg_restore drill in one disposable local cluster."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import UUID
import psycopg
from psycopg import sql
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from local_postgres_fixture import native_cluster,BIN
from booknest.repository import PostgresRepository
OUT=ROOT/'reports/day16_17/restore_20261123'

def snapshot(connect):
    with connect() as c:
        tables=[row[0] for row in c.execute("SELECT tablename FROM pg_tables WHERE schemaname='booknest' ORDER BY tablename")]
        data={name:c.execute(sql.SQL('SELECT row_to_json(t)::text FROM booknest.{} t ORDER BY row_to_json(t)::text').format(sql.Identifier(name))).fetchall() for name in tables}
        policies=c.execute("SELECT tablename,policyname,permissive,roles,cmd,qual,with_check FROM pg_policies WHERE schemaname='booknest' ORDER BY tablename,policyname").fetchall()
        flags=c.execute("SELECT c.relname,c.relrowsecurity,c.relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='booknest' AND c.relkind='r' ORDER BY c.relname").fetchall()
        grants=c.execute("SELECT grantee,table_name,privilege_type FROM information_schema.role_table_grants WHERE table_schema='booknest' ORDER BY 1,2,3").fetchall()
        return {'data':data,'policies':policies,'flags':flags,'grants':grants}

def main():
    checks=[]
    with native_cluster() as (owner,runtime):
        a,b=UUID(int=701),UUID(int=702)
        with owner() as c:
            c.execute((ROOT/'db/migrations/003_identity_broker.sql').read_text(encoding='utf-8'))
            version=c.execute('SELECT version()').fetchone()[0]
            for uid in (a,b):c.execute("INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES(%s,'synthetic',%s,'Synthetic restore user')",(uid,str(uid)))
            c.execute("INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url) SELECT i,'Synthetic book '||i,'Synthetic author','https://example.invalid/source','v1',CASE WHEN i=6 THEN 'pending' ELSE 'approved' END,CASE WHEN i=6 THEN NULL ELSE 'https://example.invalid/evidence' END FROM generate_series(1,6)i")
            c.execute("INSERT INTO booknest.book_descriptions(description_id,book_id,source_url,source_revision,source_text_sha256,source_scope,intro_vi) VALUES(%s,1,'https://example.invalid/source','v1',%s,'work','Synthetic pending content')",(UUID(int=703),'a'*64))
            params={k:v for k,v in c.info.get_parameters().items() if k in ('host','port','user','dbname')}
            password=c.info.password
        ra,rb=PostgresRepository(runtime,a),PostgresRepository(runtime,b)
        for book,rating in [(1,5),(2,4),(3,2)]:ra.save_rating(book,rating)
        rb.save_rating(4,1);ra.save_shelf(5,'want_to_read');rb.save_shelf(1,'finished')
        run=ra.save_run([(1,5),(2,4),(3,2)],[{'book_id':4,'explanation':'Synthetic explanation'},{'book_id':5,'explanation':'Synthetic explanation'}],'synthetic-model','synthetic-catalogue')
        before=snapshot(owner)
        with owner() as c:c.execute('CREATE DATABASE booknest_restore_fixture TEMPLATE template0')
        with tempfile.TemporaryDirectory(prefix='booknest_backup_',dir=ROOT/'data/dev') as temp:
            archive=Path(temp)/'synthetic.dump'
            env=os.environ.copy();env['PGPASSWORD']=password;env['PGCONNECT_TIMEOUT']='10'
            base=['--host',params['host'],'--port',params['port'],'--username',params['user'],'--no-password']
            for program,args in [('pg_dump.exe',[*base,'--dbname','postgres','--format=custom','--file',str(archive)]),
                                 ('pg_restore.exe',[*base,'--dbname','booknest_restore_fixture','--exit-on-error','--single-transaction',str(archive)])]:
                result=subprocess.run([str(BIN/program),*args],env=env,stdin=subprocess.DEVNULL,capture_output=True,timeout=90)
                if result.returncode:raise RuntimeError(program+' failed; output withheld to avoid credential leakage')
            archive_bytes=archive.stat().st_size;archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
        checks.append('custom archive restored to separate empty database without overwriting source')
        def restored_owner():return psycopg.connect(**{**params,'dbname':'booknest_restore_fixture'},password=password,autocommit=True)
        with runtime() as c:
            runtime_params={k:v for k,v in c.info.get_parameters().items() if k in ('host','port','user')};runtime_password=c.info.password
        def restored_runtime():return psycopg.connect(**runtime_params,dbname='booknest_restore_fixture',password=runtime_password,autocommit=True)
        after=snapshot(restored_owner)
        for key in before:
            assert before[key]==after[key],key
            checks.append('exact restored '+key+' matches source')
        restored_a,restored_b=PostgresRepository(restored_runtime,a),PostgresRepository(restored_runtime,b)
        assert restored_a.ratings()==ra.ratings() and restored_b.ratings()==rb.ratings()
        assert restored_a.shelf()==ra.shelf() and restored_b.shelf()==rb.shelf()
        assert restored_a.history()==ra.history() and restored_b.history()==[]
        checks.append('runtime repository retains separate owner ratings shelves and snapshot history')
        assert len(restored_a.catalogue_snapshot())==5
        assert all(row['intro_source_url'] is None and row['intro_vi']=='Chưa có mô tả được xác minh' for row in restored_a.catalogue_snapshot())
        checks.append('pending metadata and description remain hidden after restore')
        with restored_runtime() as c:
            assert c.execute('SELECT count(*) FROM booknest.user_ratings').fetchone()[0]==0
            for query in ['SELECT * FROM booknest.book_descriptions','SELECT * FROM booknest.books','SET ROLE booknest_fixture_owner']:
                try:c.execute(query)
                except psycopg.errors.InsufficientPrivilege:pass
                else:raise AssertionError('Restored grants exposed restricted data or role')
        checks.append('no-context RLS and forbidden raw-table or owner-role access remain enforced')
        assert restored_b.delete_run(run) is False and len(restored_a.history())==1
        assert restored_a.delete_run(run) is True
        with restored_owner() as c:
            assert c.execute('SELECT count(*) FROM booknest.recommendation_support').fetchone()[0]==0
            assert c.execute('SELECT count(*) FROM booknest.recommendation_items').fetchone()[0]==0
        assert len(ra.history())==1
        checks.append('restored ownership and cascade delete work while source database stays unchanged')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'validation.json').write_text(json.dumps({'postgres':version,'checks_passed':len(checks),'checks':checks,
        'archive_bytes':archive_bytes,'archive_sha256':archive_hash,'archive_deleted':True,
        'synthetic_data_only':True,'same_cluster_roles_preexisting':True,'cross_cluster_roles_restore_verified':False,
        'cloud_backup_verified':False,'temporary_cluster_stopped_and_removed':True,
        'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['scripts/verify_backup_restore.py','booknest/repository.py','db/migrations/001_initial.sql','db/migrations/002_recommendation_support.sql','db/migrations/003_identity_broker.sql']}},indent=2)+'\n',encoding='utf-8')
    print('Passed',len(checks),'synthetic backup/restore checks; archive and temporary cluster removed.')

if __name__=='__main__':main()
