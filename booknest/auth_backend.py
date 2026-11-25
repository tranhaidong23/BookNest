"""Local PostgreSQL account bootstrap for Streamlit's verified user object.

No network authentication is initiated here. Only loopback database URLs are
accepted until the separate cloud configuration/verification phase is authorized.
"""
from dataclasses import dataclass,field
from functools import partial
import psycopg
from psycopg.conninfo import conninfo_to_dict
from .identity import from_streamlit_user,resolve_identity,IdentityError
from .repository import PostgresRepository

@dataclass(frozen=True)
class AccountConfig:
    issuer:str
    client_id:str
    runtime_dsn:str=field(repr=False)
    broker_dsn:str=field(repr=False)

def local_connection_factory(dsn):
    if not isinstance(dsn,str) or not dsn.strip():raise IdentityError('Database configuration missing')
    try:params=conninfo_to_dict(dsn)
    except psycopg.Error:raise IdentityError('Invalid database configuration') from None
    host=params.get('host');address=params.get('hostaddr')
    if host not in ('localhost','127.0.0.1','::1') or params.get('service') or (address and address not in ('127.0.0.1','::1')):
        raise IdentityError('Only an explicitly configured loopback database is enabled')
    if not params.get('user') or not params.get('dbname'):raise IdentityError('Database identity and name are required')
    # Pin DNS-free loopback; an external hostaddr cannot override the host check.
    params['hostaddr']='::1' if host=='::1' else '127.0.0.1'
    params['connect_timeout']='10'
    return partial(psycopg.connect,**params,autocommit=True)

def account_from_streamlit(user,config,*,now=None):
    # Reject invalid/expired claims before any connection/provisioning call.
    identity=from_streamlit_user(user,expected_issuer=config.issuer,client_id=config.client_id,now=now)
    runtime=local_connection_factory(config.runtime_dsn);broker=local_connection_factory(config.broker_dsn)
    uid=resolve_identity(broker,identity)
    return PostgresRepository(runtime,uid)
