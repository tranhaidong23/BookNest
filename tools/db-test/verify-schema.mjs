import {PGlite} from '@electric-sql/pglite';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const migration=await readFile(path.join(root,'db/migrations/001_initial.sql'),'utf8');
const db=new PGlite();const checks=[];
const a='10000000-0000-0000-0000-000000000001',b='10000000-0000-0000-0000-000000000002';
const ra='20000000-0000-0000-0000-000000000001',rb='20000000-0000-0000-0000-000000000002';
async function test(name,fn){await fn();checks.push(name);console.log('PASS',name);}
async function rejected(sql,params,code){let caught=false;try{await db.query(sql,params);}catch(e){caught=true;assert.equal(e.code,code);}assert.ok(caught,'Expected rejection');}
async function user(id,fn){await db.exec('BEGIN; SET LOCAL ROLE booknest_runtime;');if(id)await db.query("SELECT set_config('booknest.user_id',$1,true)",[id]);try{await fn();}finally{await db.exec('ROLLBACK');}}
await test('migration executes in PostgreSQL engine',async()=>{await db.exec(migration);});
const version=(await db.query('SELECT version() AS version')).rows[0].version;
await db.query("INSERT INTO booknest.app_users(user_id,auth_issuer,auth_subject,display_name) VALUES ($1,'test','a','Alice'),($2,'test','b','Bob')",[a,b]);
await db.exec(`INSERT INTO booknest.books(book_id,title,authors,source_url,source_revision,metadata_status,metadata_evidence_url)
 VALUES (1,'Synthetic approved book','Test author','https://example.invalid/1','test','approved','https://example.invalid/permission'),
 (2,'Synthetic pending book','Test author','https://example.invalid/2','test','pending',NULL);
 INSERT INTO booknest.book_descriptions(description_id,book_id,source_url,source_revision,source_text_sha256,source_scope,intro_vi)
 VALUES ('30000000-0000-0000-0000-000000000001',1,'https://example.invalid/source','test',repeat('a',64),'work','UNAPPROVED TEST TEXT');`);
await db.query('INSERT INTO booknest.user_ratings(user_id,book_id,rating) VALUES($1,1,5),($2,1,2)',[a,b]);
await db.query("INSERT INTO booknest.reading_list(user_id,book_id,state) VALUES($1,1,'reading'),($2,1,'finished')",[a,b]);
await db.query("INSERT INTO booknest.recommendation_runs(run_id,user_id,model_version,support_count,catalogue_version) VALUES($1,$2,'test',3,'synthetic'),($3,$4,'test',3,'synthetic')",[ra,a,rb,b]);
await db.query("INSERT INTO booknest.recommendation_items(run_id,user_id,rank,book_id,explanation) VALUES($1,$2,1,1,'Synthetic evidence'),($3,$4,1,1,'Synthetic evidence')",[ra,a,rb,b]);
await test('runtime role lacks elevated flags',async()=>{
 const r=(await db.query("SELECT rolsuper,rolbypassrls,rolcreaterole,rolcreatedb,rolcanlogin FROM pg_roles WHERE rolname='booknest_runtime'")).rows[0];assert.ok(Object.values(r).every(v=>v===false));
});
await test('all five personal tables force RLS',async()=>{
 const r=(await db.query("SELECT relrowsecurity,relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='booknest' AND c.relname IN ('app_users','user_ratings','reading_list','recommendation_runs','recommendation_items')")).rows;
 assert.equal(r.length,5);assert.ok(r.every(x=>x.relrowsecurity&&x.relforcerowsecurity));
});
await test('missing user context sees no personal records',async()=>user(null,async()=>{
 for(const t of ['app_users','user_ratings','reading_list','recommendation_runs','recommendation_items'])assert.equal((await db.query(`SELECT * FROM booknest.${t}`)).rows.length,0);
}));
await test('Alice and Bob each see only their own five tables',async()=>{
 for(const id of [a,b])await user(id,async()=>{for(const t of ['app_users','user_ratings','reading_list','recommendation_runs','recommendation_items']){
 const rows=(await db.query(`SELECT * FROM booknest.${t}`)).rows;assert.equal(rows.length,1);assert.equal(rows[0].user_id,id);
 }});
});
await test('cross-user updates and deletes affect zero rows',async()=>user(a,async()=>{
 assert.equal((await db.query('UPDATE booknest.user_ratings SET rating=1 WHERE user_id=$1 RETURNING *',[b])).rows.length,0);
 assert.equal((await db.query('DELETE FROM booknest.reading_list WHERE user_id=$1 RETURNING *',[b])).rows.length,0);
}));
await test('cross-user insert denied',async()=>user(a,async()=>rejected("INSERT INTO booknest.recommendation_runs(run_id,user_id,model_version,support_count,catalogue_version) VALUES('20000000-0000-0000-0000-000000000003',$1,'test',3,'test')",[b],'42501')));
await test('changing row owner denied',async()=>user(a,async()=>rejected('UPDATE booknest.user_ratings SET user_id=$1 WHERE user_id=$2',[b,a],'42501')));
await test('auth identity cannot be edited by runtime',async()=>user(a,async()=>rejected("UPDATE booknest.app_users SET auth_subject='other' WHERE user_id=$1",[a],'42501')));
await test('own display name and rating update allowed',async()=>user(a,async()=>{
 assert.equal((await db.query("UPDATE booknest.app_users SET display_name='Alice edited' RETURNING display_name")).rows[0].display_name,'Alice edited');
 assert.equal((await db.query('UPDATE booknest.user_ratings SET rating=4 RETURNING rating')).rows[0].rating,4);
}));
await test('rating bounds enforced',async()=>user(a,async()=>rejected('UPDATE booknest.user_ratings SET rating=0',[],'23514')));
await test('reading states enforced',async()=>user(a,async()=>rejected("UPDATE booknest.reading_list SET state='invented'",[],'23514')));
await test('runtime cannot read pending base metadata or text',async()=>user(a,async()=>rejected('SELECT * FROM booknest.books',[],'42501')));
await test('runtime cannot read private descriptions',async()=>user(a,async()=>rejected('SELECT * FROM booknest.book_descriptions',[],'42501')));
await test('public view gates metadata text and covers separately',async()=>user(a,async()=>{
 const rows=(await db.query('SELECT * FROM booknest.public_catalogue')).rows;
 assert.equal(rows.length,1);assert.equal(rows[0].book_id,1);assert.equal(rows[0].intro_vi,'Chưa có mô tả được xác minh');assert.equal(rows[0].intro_source_url,null);assert.equal(rows[0].cover_url,null);
}));
await test('cannot rate a book with pending metadata',async()=>user(a,async()=>rejected('INSERT INTO booknest.user_ratings VALUES($1,2,4,now())',[a],'42501')));
await test('composite foreign key prevents attaching to another users run',async()=>{
 const emptyRun='20000000-0000-0000-0000-000000000004';
 await db.query("INSERT INTO booknest.recommendation_runs(run_id,user_id,model_version,support_count,catalogue_version) VALUES($1,$2,'test',3,'test')",[emptyRun,b]);
 await user(a,async()=>rejected("INSERT INTO booknest.recommendation_items VALUES($1,$2,2,1,'test')",[emptyRun,a],'23503'));
});
await test('rank bounds enforced',async()=>user(a,async()=>rejected("INSERT INTO booknest.recommendation_items VALUES($1,$2,11,1,'test')",[ra,a],'23514')));
await test('runtime cannot truncate personal records',async()=>user(a,async()=>rejected('TRUNCATE booknest.user_ratings',[],'42501')));
await test('transaction-local identity does not persist after rollback',async()=>{
 const v=(await db.query("SELECT nullif(current_setting('booknest.user_id',true),'') AS id")).rows[0].id;assert.equal(v,null);
});
await test('metadata approval requires evidence',async()=>rejected("UPDATE booknest.books SET metadata_status='approved' WHERE book_id=2",[],'23514'));
await test('intro appears only after rights identity and content gates',async()=>{
 await db.exec("UPDATE booknest.book_descriptions SET identity_verified=true,content_reviewed=true,rights_status='approved',rights_evidence_url='https://example.invalid/permission'");
 await user(a,async()=>{const r=(await db.query('SELECT intro_vi,intro_source_url FROM booknest.public_catalogue')).rows[0];assert.equal(r.intro_vi,'UNAPPROVED TEST TEXT');assert.equal(r.intro_source_url,'https://example.invalid/source');});
});
await test('reviewer can inspect pending metadata but not user data',async()=>{
 await db.exec('SET ROLE booknest_local_reviewer');
 assert.equal((await db.query('SELECT * FROM booknest.books')).rows.length,2);
 await rejected('SELECT * FROM booknest.user_ratings',[],'42501');await db.exec('RESET ROLE');
});
await test('duplicate migration fails rather than silently overwriting',async()=>{
 let caught=false;try{await db.exec(migration);}catch(e){caught=true;assert.equal(e.code,'42P06');}
 assert.ok(caught);await db.exec('ROLLBACK');
});
const pkg=JSON.parse(await readFile(path.join(root,'tools/db-test/package-lock.json'),'utf8'));
const report={engine:version,pglite:pkg.packages['node_modules/@electric-sql/pglite'].version,checks_passed:checks.length,checks,
 migration_sha256:createHash('sha256').update(migration).digest('hex'),test_script_sha256:createHash('sha256').update(await readFile(fileURLToPath(import.meta.url))).digest('hex'),
 scope:'isolated in-memory PostgreSQL via PGlite, synthetic fixtures, SET LOCAL ROLE; not Neon, network login, OIDC, pooling or concurrent load validation',neon_connected:false};
const out=path.join(root,'reports/day11/schema_local_20261123');await mkdir(out,{recursive:true});await writeFile(path.join(out,'validation.json'),JSON.stringify(report,null,2)+'\n');
await db.close();console.log('Passed',checks.length,'database checks.');
