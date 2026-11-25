"""Real PostgreSQL broker provisioning with synthetic, explicitly trusted test claims."""
import sys
import json
import secrets
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import psycopg
from psycopg import sql
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from local_postgres_fixture import native_cluster
from booknest.identity import from_streamlit_user,resolve_identity,IdentityError
from booknest.repository import PostgresRepository
from audit_extended import sha

OUT=ROOT/'reports/day12_14/identity_20261123'

def main():
    checks=[]
    with native_cluster() as (owner,runtime):
        password=secrets.token_urlsafe(32)
        with owner() as c:
            version=c.execute('SELECT version()').fetchone()[0]
            c.execute((ROOT/'db/migrations/003_identity_broker.sql').read_text(encoding='utf-8'))
            c.execute(sql.SQL('CREATE ROLE booknest_fixture_broker LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD {}').format(sql.Literal(password)))
            c.execute('GRANT booknest_identity_broker TO booknest_fixture_broker')
            params={k:v for k,v in c.info.get_parameters().items() if k in ('host','port','dbname')}
        def broker():return psycopg.connect(**params,user='booknest_fixture_broker',password=password,autocommit=True,connect_timeout=10)
        def identity(sub,issuer='https://identity.example.invalid',name='Alice'):
            return from_streamlit_user({'is_logged_in':True,'iss':issuer,'sub':sub,'aud':'booknest','iat':1000,'exp':5000,'name':name},expected_issuer=issuer,client_id='booknest',now=2000)
        a=identity('user-a');b=identity('user-b',name='Bob')
        uid=resolve_identity(broker,a);assert resolve_identity(broker,a)==uid;checks.append('repeated issuer subject resolves same UUID')
        with ThreadPoolExecutor(max_workers=4) as pool:
            values=list(pool.map(lambda _:resolve_identity(broker,b),range(8)))
        assert len(set(values))==1 and values[0]!=uid;checks.append('eight concurrent first-login resolutions create one account')
        other=resolve_identity(broker,identity('user-a','https://another.example.invalid'))
        assert other not in (uid,values[0]);checks.append('same subject at another issuer remains distinct')
        repo=PostgresRepository(runtime,uid);repo.update_display_name('Chosen display name')
        resolve_identity(broker,identity('user-a',name='Changed provider name'))
        assert repo.profile()['display_name']=='Chosen display name';checks.append('repeat login does not overwrite app profile edits')
        with broker() as c:
            assert c.execute('SELECT user_id FROM booknest.app_users').fetchall()==[]
            with c.transaction():
                c.execute("SELECT set_config('booknest.auth_issuer',%s,true),set_config('booknest.auth_subject',%s,true)",(a.issuer,a.subject))
                assert c.execute('SELECT user_id FROM booknest.app_users').fetchall()==[(uid,)]
            assert c.execute('SELECT user_id FROM booknest.app_users').fetchall()==[]
        checks.append('broker lookup confined to transaction issuer subject and clears afterward')
        rejected=[]
        for statement in ['SELECT * FROM booknest.user_ratings','SELECT * FROM booknest.reading_list','SELECT * FROM booknest.recommendation_runs','SELECT * FROM booknest.book_descriptions',"UPDATE booknest.app_users SET display_name='changed'",'DELETE FROM booknest.app_users']:
            try:
                with broker() as c:c.execute(statement)
            except psycopg.errors.InsufficientPrivilege:rejected.append(statement.split()[0])
            else:raise AssertionError('Broker exceeded privileges')
        assert len(rejected)==6;checks.append('broker cannot access personal content source text or mutate existing identities')
        for connection in (owner,runtime):
            try:resolve_identity(connection,a)
            except IdentityError:pass
            else:raise AssertionError('Wrong credential role accepted')
        checks.append('migration-owner and runtime connections cannot provision identities')
        with owner() as c:assert c.execute('SELECT count(*) FROM booknest.app_users').fetchone()[0]==3
        checks.append('exactly three intended synthetic accounts persisted')
    OUT.mkdir(parents=True,exist_ok=True)
    paths=['booknest/identity.py','db/migrations/003_identity_broker.sql','scripts/verify_identity.py','tests/test_identity.py']
    (OUT/'validation.json').write_text(json.dumps({'engine':version,'checks_passed':len(checks),'checks':checks,'synthetic_claims_only':True,
        'external_oidc_exchange_verified':False,'neon_connected':False,'isolated_cluster_stopped_and_removed':True,
        'sources_sha256':{p:sha(ROOT/p) for p in paths}},indent=2)+'\n',encoding='utf-8')
    print('Passed',len(checks),'identity broker integration checks; no external OIDC call, test cluster cleaned.')

if __name__=='__main__':main()
