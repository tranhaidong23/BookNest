"""Prepare operational metadata locally; never export ratings/raw descriptions or approvals."""
import json
from pathlib import Path
from audit_extended import sha
from prepare_day03 import write_json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/day11/schema_local_20261123'
DATA=ROOT/'data/processed/day11_operational_v1'

def operational_row(row):
    return {'book_id':int(row['book_id']),'title':row['title'],'authors':row['authors'],
        'goodreads_edition_id':str(row['goodreads_book_id']),'goodreads_work_id':str(row['work_id']),
        'source_url':row['source_url'],'source_revision':row['source_revision'],
        'metadata_status':'pending','metadata_evidence_url':None,'cover_url':None,'cover_status':'pending','cover_evidence_url':None}

def main():
    source=ROOT/'data/processed/day03_v2/books.jsonl';mfile=ROOT/'reports/day03/preparation_v2_20261120/manifest.json'
    m=json.loads(mfile.read_text());assert sha(source)==m['outputs'][str(source.relative_to(ROOT))]
    rows=[operational_row(json.loads(line)) for line in source.read_text(encoding='utf-8').splitlines()]
    assert len(rows)==len({r['book_id'] for r in rows})==10000
    assert all(r['title'].strip() and r['authors'].strip() for r in rows)
    write_json(DATA/'books.json',rows)
    write_json(OUT/'catalogue_manifest.json',{'rows':len(rows),'public_metadata_approved':0,'descriptions_exported':0,'benchmark_ratings_exported':0,
        'inputs':{str(source.relative_to(ROOT)):sha(source),str(mfile.relative_to(ROOT)):sha(mfile)},
        'output':str((DATA/'books.json').relative_to(ROOT)),'output_sha256':sha(DATA/'books.json'),'script_sha256':sha(Path(__file__))})
    print('Prepared 10000 metadata rows, all pending; no descriptions, covers or benchmark ratings exported.')

if __name__=='__main__':main()
