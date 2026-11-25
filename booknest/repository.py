"""PostgreSQL persistence bound to a server-resolved identity, not browser-supplied IDs.

The caller supplies a factory for fresh runtime connections and a UUID resolved
after authentication. This module does not authenticate tokens or provision users.
"""
from contextlib import contextmanager
from uuid import UUID,uuid4
import psycopg
from psycopg.rows import dict_row

class StorageError(RuntimeError):pass
class StaleProfileError(StorageError):pass

def book_id(value):
    if type(value) is not int or value<=0:raise ValueError('Book ID must be a positive integer')
    return value

def rating_value(value):
    if type(value) is not int or not 1<=value<=5:raise ValueError('Rating must be an integer from 1 to 5')
    return value

class PostgresRepository:
    def __init__(self,connect,user_id):
        self._connect=connect;self.user_id=UUID(str(user_id))

    @contextmanager
    def _transaction(self):
        try:
            with self._connect() as connection:
                if connection.info.transaction_status!=psycopg.pq.TransactionStatus.IDLE:
                    raise StorageError('A fresh idle runtime connection is required')
                with connection.transaction():
                    with connection.cursor(row_factory=dict_row) as cursor:
                        role=cursor.execute("SELECT rolsuper,rolbypassrls,rolcreaterole,rolcreatedb FROM pg_roles WHERE rolname=current_user").fetchone()
                        owner=cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='booknest' AND pg_has_role(current_user,c.relowner,'MEMBER')) AS owns").fetchone()
                        if not role or any(role.values()) or owner['owns']:
                            raise StorageError('Use a restricted runtime connection, not the migration owner')
                        cursor.execute("SELECT set_config('booknest.user_id',%s,true)",(str(self.user_id),))
                        # Serialize this user's repository operations, including profile check + run snapshot.
                        cursor.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',(str(self.user_id),))
                        if not cursor.execute('SELECT 1 FROM booknest.app_users WHERE user_id=%s',(self.user_id,)).fetchone():
                            raise StorageError('Authenticated identity is not provisioned')
                        yield cursor
        except psycopg.Error:
            # DB details can disclose schema, another user's identifiers, or connection information.
            raise StorageError('Database operation failed; no partial change was saved') from None

    def profile(self):
        with self._transaction() as c:
            return c.execute('SELECT user_id,display_name,created_at FROM booknest.app_users WHERE user_id=%s',(self.user_id,)).fetchone()

    def update_display_name(self,name):
        if not isinstance(name,str) or not 1<=len(name.strip())<=100:raise ValueError('Invalid display name')
        with self._transaction() as c:c.execute('UPDATE booknest.app_users SET display_name=%s WHERE user_id=%s',(name.strip(),self.user_id))

    def ratings(self):
        with self._transaction() as c:
            return {r['book_id']:r['rating'] for r in c.execute('SELECT book_id,rating FROM booknest.user_ratings WHERE user_id=%s ORDER BY book_id',(self.user_id,)).fetchall()}

    def save_rating(self,book,rating):
        book_id(book);rating_value(rating)
        with self._transaction() as c:
            c.execute('INSERT INTO booknest.user_ratings(user_id,book_id,rating) VALUES(%s,%s,%s) ON CONFLICT(user_id,book_id) DO UPDATE SET rating=EXCLUDED.rating,updated_at=now()',(self.user_id,book,rating))

    def delete_rating(self,book):
        book_id(book)
        with self._transaction() as c:
            c.execute('DELETE FROM booknest.user_ratings WHERE user_id=%s AND book_id=%s',(self.user_id,book));return c.rowcount>0

    def shelf(self):
        with self._transaction() as c:
            return {r['book_id']:r['state'] for r in c.execute('SELECT book_id,state FROM booknest.reading_list WHERE user_id=%s ORDER BY book_id',(self.user_id,)).fetchall()}

    def save_shelf(self,book,state):
        book_id(book)
        if state not in ('want_to_read','reading','finished'):raise ValueError('Invalid reading state')
        with self._transaction() as c:
            c.execute('INSERT INTO booknest.reading_list(user_id,book_id,state) VALUES(%s,%s,%s) ON CONFLICT(user_id,book_id) DO UPDATE SET state=EXCLUDED.state,updated_at=now()',(self.user_id,book,state))

    def delete_shelf(self,book):
        book_id(book)
        with self._transaction() as c:
            c.execute('DELETE FROM booknest.reading_list WHERE user_id=%s AND book_id=%s',(self.user_id,book));return c.rowcount>0

    def search_catalogue(self,query='',limit=24,offset=0):
        if not isinstance(query,str) or len(query)>200:raise ValueError('Search query too long')
        if type(limit) is not int or not 1<=limit<=100 or type(offset) is not int or offset<0:raise ValueError('Invalid page')
        # Treat SQL LIKE wildcards as literal user text; all values are bound parameters.
        escaped=query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        with self._transaction() as c:
            return c.execute("SELECT * FROM booknest.public_catalogue WHERE title ILIKE %s ESCAPE E'\\\\' OR authors ILIKE %s ESCAPE E'\\\\' ORDER BY book_id LIMIT %s OFFSET %s",('%'+escaped+'%','%'+escaped+'%',limit,offset)).fetchall()

    def catalogue_snapshot(self):
        # One statement sees one catalogue snapshot. No pagination drift or
        # per-page connections; permissions still come exclusively from the view.
        with self._transaction() as c:
            return c.execute('SELECT * FROM booknest.public_catalogue ORDER BY book_id').fetchall()

    def save_run(self,profile,items,model_version,catalogue_version):
        profile=list(profile);items=list(items)
        if len(profile)>10000 or len({b for b,r in profile})!=len(profile):raise ValueError('Invalid profile')
        for b,r in profile:book_id(b);rating_value(r)
        if not 1<=len(items)<=10 or len({i['book_id'] for i in items})!=len(items):raise ValueError('Invalid recommendation items')
        seen={b for b,r in profile}
        for item in items:
            book_id(item['book_id'])
            if item['book_id'] in seen:raise ValueError('Recommended item is already rated')
            if not isinstance(item['explanation'],str) or not 1<=len(item['explanation'])<=2000:raise ValueError('Invalid explanation')
        if any(not isinstance(v,str) or not 1<=len(v)<=200 for v in (model_version,catalogue_version)):raise ValueError('Invalid artifact version')
        run_id=uuid4()
        with self._transaction() as c:
            current=c.execute('SELECT book_id,rating FROM booknest.user_ratings WHERE user_id=%s ORDER BY book_id',(self.user_id,)).fetchall()
            if [(r['book_id'],r['rating']) for r in current]!=sorted(profile):raise StaleProfileError('Ratings changed; generate recommendations again')
            c.execute('INSERT INTO booknest.recommendation_runs(run_id,user_id,model_version,support_count,catalogue_version) VALUES(%s,%s,%s,%s,%s)',(run_id,self.user_id,model_version,len(profile),catalogue_version))
            c.executemany('INSERT INTO booknest.recommendation_support(run_id,user_id,book_id,rating) VALUES(%s,%s,%s,%s)',[(run_id,self.user_id,b,r) for b,r in profile])
            c.executemany('INSERT INTO booknest.recommendation_items(run_id,user_id,rank,book_id,explanation) VALUES(%s,%s,%s,%s,%s)',[(run_id,self.user_id,index+1,i['book_id'],i['explanation']) for index,i in enumerate(items)])
        return run_id

    def history(self,limit=20):
        if type(limit) is not int or not 1<=limit<=100:raise ValueError('Invalid history limit')
        with self._transaction() as c:
            runs=c.execute('SELECT run_id,model_version,support_count,catalogue_version,created_at FROM booknest.recommendation_runs WHERE user_id=%s ORDER BY created_at DESC,run_id LIMIT %s',(self.user_id,limit)).fetchall()
            for run in runs:
                run['profile']=c.execute('SELECT book_id,rating FROM booknest.recommendation_support WHERE run_id=%s AND user_id=%s ORDER BY book_id',(run['run_id'],self.user_id)).fetchall()
                run['items']=c.execute('SELECT rank,book_id,explanation FROM booknest.recommendation_items WHERE run_id=%s AND user_id=%s ORDER BY rank',(run['run_id'],self.user_id)).fetchall()
            return runs

    def delete_run(self,run_id):
        run_id=UUID(str(run_id))
        with self._transaction() as c:
            c.execute('DELETE FROM booknest.recommendation_runs WHERE run_id=%s AND user_id=%s',(run_id,self.user_id));return c.rowcount>0
