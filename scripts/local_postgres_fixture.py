"""Isolated native PostgreSQL fixture shared by integration checks, never production."""
from contextlib import contextmanager
from pathlib import Path
import os
import secrets
import socket
import subprocess
import tempfile
import psycopg
from psycopg import sql

ROOT=Path(__file__).resolve().parents[1]
BIN=Path('C:/Program Files/PostgreSQL/18/bin')

@contextmanager
def native_cluster():
    scratch=ROOT/'data/dev';scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='booknest_integration_',dir=scratch) as tmp:
        base=Path(tmp).resolve();assert base.is_relative_to(scratch.resolve()) and base.name.startswith('booknest_integration_')
        cluster=base/'cluster';password=secrets.token_urlsafe(32);runtime_password=secrets.token_urlsafe(32)
        def run(program,args):
            log=base/'process.log'
            with log.open('w',encoding='utf-8') as stream:
                result=subprocess.run([str(BIN/program),*args],stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,timeout=90)
            if result.returncode:raise RuntimeError(program+' failed in isolated fixture; no credential output')
        pw=base/'bootstrap_password';pw.write_text(password,encoding='utf-8')
        run('initdb.exe',['-D',str(cluster),'-U','booknest_fixture_owner','--encoding=UTF8','--locale=C','--auth-host=scram-sha-256','--auth-local=scram-sha-256','--pwfile='+str(pw)]);pw.unlink()
        with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        try:
            run('pg_ctl.exe',['-D',str(cluster),'-l',str(base/'server.log'),'-o',f'-h 127.0.0.1 -p {port}','-w','start'])
            def owner():return psycopg.connect(host='127.0.0.1',port=port,dbname='postgres',user='booknest_fixture_owner',password=password,autocommit=True,connect_timeout=10)
            def runtime():return psycopg.connect(host='127.0.0.1',port=port,dbname='postgres',user='booknest_fixture_runtime',password=runtime_password,autocommit=True,connect_timeout=10)
            with owner() as connection:
                for name in ('001_initial.sql','002_recommendation_support.sql'):connection.execute((ROOT/'db/migrations'/name).read_text(encoding='utf-8'))
                connection.execute(sql.SQL('CREATE ROLE booknest_fixture_runtime LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD {}').format(sql.Literal(runtime_password)))
                connection.execute('GRANT booknest_runtime TO booknest_fixture_runtime')
            yield owner,runtime
        finally:
            if (cluster/'postmaster.pid').exists():run('pg_ctl.exe',['-D',str(cluster),'-m','fast','-w','stop'])
