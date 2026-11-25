import {PGlite} from '@electric-sql/pglite';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const sha=s=>createHash('sha256').update(s).digest('hex');
const out=path.join(root,'reports/day11/schema_local_20261123');
const manifest=JSON.parse(await readFile(path.join(out,'catalogue_manifest.json'),'utf8'));
const data=await readFile(path.join(root,manifest.output),'utf8');assert.equal(sha(data),manifest.output_sha256);
const migration=await readFile(path.join(root,'db/migrations/001_initial.sql'),'utf8');
const sql=await readFile(path.join(root,'db/import_books.sql'),'utf8');
const db=new PGlite();await db.exec(migration);await db.query(sql,[data]);
assert.equal(Number((await db.query('SELECT count(*) AS n FROM booknest.books')).rows[0].n),10000);
for(const table of ['book_descriptions','app_users','user_ratings','reading_list','recommendation_runs','recommendation_items'])assert.equal(Number((await db.query(`SELECT count(*) AS n FROM booknest.${table}`)).rows[0].n),0);
await db.exec('SET ROLE booknest_runtime');assert.equal((await db.query('SELECT * FROM booknest.public_catalogue')).rows.length,0);await db.exec('RESET ROLE');
let duplicateRejected=false;try{await db.query(sql,[data]);}catch(e){assert.equal(e.code,'23505');duplicateRejected=true;}assert.ok(duplicateRejected);
const actual=(await db.query('SELECT * FROM booknest.books ORDER BY book_id')).rows;
const expected=JSON.parse(data).sort((a,b)=>a.book_id-b.book_id);assert.deepEqual(actual,expected);
await writeFile(path.join(out,'import_validation.json'),JSON.stringify({rows_read_back:actual.length,all_fields_exact_match:true,
 public_catalogue_rows:0,personal_tables_empty:true,duplicate_import_rejected:true,neon_connected:false,
 catalogue_sha256:sha(data),migration_sha256:sha(migration),import_sql_sha256:sha(sql),verifier_sha256:sha(await readFile(fileURLToPath(import.meta.url)))},null,2)+'\n');
await db.close();console.log('Read back all 10000 operational rows exactly; public catalogue empty; no benchmark users/ratings imported.');
