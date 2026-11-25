"""Disposable loopback-only PostgreSQL cluster, SCRAM logins; no existing services touched."""
import json
import os
import secrets
import socket
import subprocess
import tempfile
from pathlib import Path
from audit_extended import sha

ROOT=Path(__file__).resolve().parents[1]
BIN=Path('C:/Program Files/PostgreSQL/18/bin')
OUT=ROOT/'reports/day11/native_postgres_20261123'
A='10000000-0000-0000-0000-000000000001'
B='10000000-0000-0000-0000-000000000002'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    scratch=ROOT/'data/dev';scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='booknest_pg_',dir=scratch) as temp:
        base=Path(temp).resolve()
        assert base.is_relative_to(scratch.resolve()) and base.name.startswith('booknest_pg_')
        cluster=base/'cluster';pwfile=base/'bootstrap_password';ownerpw=secrets.token_urlsafe(32);runtimepw=secrets.token_urlsafe(32)
        pwfile.write_text(ownerpw,encoding='utf-8');started=False
        def command(executable,args,env=None,input=None,check=True):
            if executable=='pg_ctl.exe':
                # Windows daemon children can inherit PIPE handles and hold communicate()
                # open after pg_ctl exits. Use a file, never PIPE, for lifecycle commands.
                log=base/'controller.log'
                with log.open('w',encoding='utf-8') as stream:
                    run=subprocess.run([str(BIN/executable),*args],stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,env=env,timeout=90)
                result=subprocess.CompletedProcess(run.args,run.returncode,'',log.read_text(encoding='utf-8',errors='replace'))
            else:
                result=subprocess.run([str(BIN/executable),*args],input=input,text=True,encoding='utf-8',errors='replace',capture_output=True,env=env,timeout=90)
            if check and result.returncode:
                # Never print SQL inputs/passwords; only a sanitized diagnostic.
                diagnostic=result.stderr.replace(ownerpw,'[redacted]').replace(runtimepw,'[redacted]')
                raise RuntimeError(executable+' failed: '+diagnostic[-2000:])
            return result
        command('initdb.exe',['-D',str(cluster),'-U','booknest_test_owner','--encoding=UTF8','--locale=C','--auth-host=scram-sha-256','--auth-local=scram-sha-256','--pwfile='+str(pwfile)])
        pwfile.unlink()
        with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        try:
            command('pg_ctl.exe',['-D',str(cluster),'-l',str(base/'server.log'),'-o',f'-h 127.0.0.1 -p {port}','-w','start']);started=True
            def sql(statement,user='booknest_test_owner',password=None,check=True):
                env={**os.environ,'PGPASSWORD':password if password is not None else ownerpw,'PGCLIENTENCODING':'UTF8'}
                return command('psql.exe',['-X','-q','-A','-t','-v','ON_ERROR_STOP=1','-h','127.0.0.1','-p',str(port),'-U',user,'-d','postgres'],env=env,input=statement,check=check)
            migration=ROOT/'db/migrations/001_initial.sql';sql(migration.read_text(encoding='utf-8'))
            # Random URL-safe passwords are never written in SQL artifacts or command arguments.
            sql("CREATE ROLE booknest_test_login LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD '"+runtimepw+"'; GRANT booknest_runtime TO booknest_test_login;")
            sql(f"INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES ('{A}','synthetic','a','Alice'),('{B}','synthetic','b','Bob'); INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url) VALUES(1,'Synthetic test','Test','https://example.invalid','test','approved','https://example.invalid/permission'); INSERT INTO booknest.user_ratings(user_id,book_id,rating) VALUES('{A}',1,5),('{B}',1,2);")
            runtime=lambda statement:sql(statement,'booknest_test_login',runtimepw)
            version=sql('SELECT version();').stdout.strip()
            runtime("DO $$ BEGIN ASSERT current_user='booknest_test_login'; ASSERT NOT (SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname=current_user); ASSERT (SELECT count(*) FROM booknest.user_ratings)=0; END $$;")
            for uid,rating in [(A,5),(B,2)]:
                runtime(f"BEGIN; SELECT set_config('booknest.user_id','{uid}',true); DO $$ BEGIN ASSERT (SELECT count(*) FROM booknest.user_ratings)=1; ASSERT (SELECT rating FROM booknest.user_ratings)={rating}; ASSERT (SELECT user_id FROM booknest.user_ratings)='{uid}'::uuid; END $$; COMMIT; BEGIN; DO $$ BEGIN ASSERT booknest.current_user_id() IS NULL; ASSERT (SELECT count(*) FROM booknest.user_ratings)=0; END $$; COMMIT;")
            runtime(f"BEGIN; SELECT set_config('booknest.user_id','{A}',true); DO $$ DECLARE changed integer; BEGIN UPDATE booknest.user_ratings SET rating=1 WHERE user_id='{B}'; GET DIAGNOSTICS changed=ROW_COUNT; ASSERT changed=0; END $$; ROLLBACK;")
            failures={}
            for name,statement in {
                'base_metadata_read':'SELECT * FROM booknest.books;',
                'auth_subject_update':f"BEGIN; SELECT set_config('booknest.user_id','{A}',true); UPDATE booknest.app_users SET auth_subject='other';",
                'cross_user_insert':f"BEGIN; SELECT set_config('booknest.user_id','{A}',true); INSERT INTO booknest.recommendation_runs VALUES('20000000-0000-0000-0000-000000000001','{B}','synthetic',3,'synthetic',now());",
                'owner_role_escalation':'SET ROLE booknest_test_owner;',
                'truncate':'TRUNCATE booknest.user_ratings;',
            }.items():
                result=sql(statement,'booknest_test_login',runtimepw,check=False)
                assert result.returncode!=0,name;failures[name]='rejected'
            wrong=sql('SELECT 1;','booknest_test_login','intentionally-wrong-test-password',check=False)
            assert wrong.returncode!=0 and 'password authentication failed' in wrong.stderr.lower()
            report={'engine':version,'loopback_only':True,'isolated_cluster':True,'scram_correct_login':True,'scram_wrong_password_rejected':True,
                'two_real_runtime_logins_rls_isolation':True,'same_connection_transaction_context_reset':True,'cross_user_update_zero_rows':True,
                'forbidden_actions':failures,'migration_sha256':sha(migration),'verifier_sha256':sha(Path(__file__)),
                'existing_database_services_modified':False,'neon_connected':False,'oidc_verified':False,'connection_pool_tested':False}
            (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            print('Native PostgreSQL: SCRAM logins, two-user RLS, transaction reset and 5 forbidden actions passed.')
        finally:
            if started or (cluster/'postmaster.pid').exists():command('pg_ctl.exe',['-D',str(cluster),'-m','fast','-w','stop'])
    print('Owned test server stopped; isolated temporary cluster removed.')

if __name__=='__main__':main()
