"""Map Streamlit-verified OIDC claims to an app UUID.

Never pass request JSON, query params or an unverified decoded JWT here. Signature,
nonce and OIDC exchange validation belong to Streamlit/Authlib. This module adds
claim/session policy and database provisioning, not a standalone JWT verifier.
"""
from dataclasses import dataclass
from uuid import uuid4
from urllib.parse import urlsplit
import math
import time
import psycopg
from psycopg.rows import dict_row

class IdentityError(RuntimeError):pass

@dataclass(frozen=True)
class Identity:
    issuer:str
    subject:str
    display_name:str

def from_streamlit_user(user,*,expected_issuer,client_id,now=None,max_age_seconds=28800):
    now=time.time() if now is None else now
    parsed=urlsplit(expected_issuer)
    if parsed.scheme!='https' or not parsed.netloc or parsed.query or parsed.fragment or parsed.username:
        raise IdentityError('Invalid configured issuer')
    if not isinstance(client_id,str) or not client_id or max_age_seconds<=0:raise IdentityError('Invalid authentication policy')
    if user.get('is_logged_in') is not True:raise IdentityError('Sign in required')
    if user.get('iss')!=expected_issuer:raise IdentityError('Unexpected identity provider')
    subject=user.get('sub')
    if not isinstance(subject,str) or not subject.strip() or len(subject)>255:raise IdentityError('Missing stable identity subject')
    audience=user.get('aud');audience=[audience] if isinstance(audience,str) else audience
    if not isinstance(audience,list) or not audience or not all(isinstance(a,str) for a in audience) or client_id not in audience:
        raise IdentityError('Unexpected token audience')
    if (len(audience)>1 and user.get('azp')!=client_id) or ('azp' in user and user['azp']!=client_id):raise IdentityError('Unexpected authorized party')
    def timestamp(key):
        value=user.get(key)
        if type(value) not in (int,float) or not math.isfinite(value):raise IdentityError('Invalid session time')
        return value
    issued=timestamp('iat');expires=timestamp('exp')
    if expires<=now or issued>now+60 or issued>=expires or now-issued>max_age_seconds:
        raise IdentityError('Session expired or invalid; sign in again')
    if 'nbf' in user and timestamp('nbf')>now+60:raise IdentityError('Session not active yet')
    name=user.get('name');name=name.strip()[:100] if isinstance(name,str) and name.strip() else 'Bạn đọc BookNest'
    return Identity(expected_issuer,subject,name)

def resolve_identity(connect,identity):
    if not isinstance(identity,Identity):raise IdentityError('A server-validated identity is required')
    try:
        with connect() as connection:
            if connection.info.transaction_status!=psycopg.pq.TransactionStatus.IDLE:raise IdentityError('Fresh broker connection required')
            with connection.transaction():
                with connection.cursor(row_factory=dict_row) as c:
                    role=c.execute("SELECT rolsuper,rolbypassrls,rolcreaterole,rolcreatedb FROM pg_roles WHERE rolname=current_user").fetchone()
                    owner=c.execute("SELECT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='booknest' AND pg_has_role(current_user,c.relowner,'MEMBER')) AS owns").fetchone()
                    if not role or any(role.values()) or owner['owns']:raise IdentityError('Restricted identity broker required')
                    c.execute("SELECT set_config('booknest.auth_issuer',%s,true),set_config('booknest.auth_subject',%s,true)",(identity.issuer,identity.subject))
                    # Identity is (issuer,subject), never email or caller-chosen UUID.
                    inserted=c.execute('INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES(%s,%s,%s,%s) ON CONFLICT(auth_issuer,auth_subject) DO NOTHING RETURNING user_id',(uuid4(),identity.issuer,identity.subject,identity.display_name)).fetchone()
                    if inserted:return inserted['user_id']
                    existing=c.execute('SELECT user_id FROM booknest.app_users WHERE auth_issuer=%s AND auth_subject=%s',(identity.issuer,identity.subject)).fetchone()
                    if existing:return existing['user_id']
                    raise IdentityError('Identity could not be resolved')
    except psycopg.Error:
        raise IdentityError('Identity storage unavailable') from None
