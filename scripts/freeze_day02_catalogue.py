"""Freeze a local identity/status catalogue; never export source text or approve rights."""
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from audit_extended import sha, verify_manifest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/day02/catalogue_v1_20261119'
DATA = ROOT/'data/processed/catalogue_v1'

def public_ready(record):
    """Text/AI public gate; cover permission is separately enforced by its consumer."""
    rights = record.get('rights', {})
    return (record.get('identity_status') == 'matched_edition_and_work'
        and record.get('content_status') == 'verified_sufficient'
        and record.get('intro_status') == 'reviewed'
        and 60 <= record.get('intro_word_count', 0) <= 100
        and rights.get('description_display') == 'verified'
        and rights.get('adaptation') == 'verified'
        and bool(rights.get('evidence_url')))

def main():
    original = json.loads((ROOT/'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    xml_manifest = json.loads((ROOT/'reports/day01/descriptions_20261119/xml_manifest.json').read_text(encoding='utf-8'))
    audit_path = ROOT/'reports/day02/review_20261119/review_audit.json'
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    verify_manifest(original)
    if sha(ROOT/xml_manifest['path']) != xml_manifest['sha256']:
        raise ValueError('XML ZIP changed')
    for path, digest in audit['outputs'].items():
        if sha(ROOT/path) != digest:
            raise ValueError('Review output changed: ' + path)
    review_path = ROOT/'data/processed/review_20261119/review_decisions.json'
    reviews = {r['book_id']:r for r in json.loads(review_path.read_text(encoding='utf-8'))}
    index_path = ROOT/'data/processed/descriptions_20261119/xml_matches.csv'
    with index_path.open(encoding='utf-8',newline='') as f:
        index_rows = list(csv.DictReader(f))
    index = {r['book_id']:r for r in index_rows}
    with (ROOT/'data/raw/goodbooks-10k/books.csv').open(encoding='utf-8',newline='') as f:
        books = list(csv.DictReader(f))
    ids = {b['book_id'] for b in books}
    if len(ids) != len(books) or len(index) != len(index_rows) or ids != set(index):
        raise ValueError('Catalogue/index duplicate or missing IDs')
    if not set(reviews).issubset(ids):
        raise ValueError('Unknown review ID')
    records = []
    for b in sorted(books,key=lambda b:int(b['book_id'])):
        x = index[b['book_id']]
        if x['goodreads_book_id'] != b['goodreads_book_id'] or x['work_id'] != b['work_id'] or x['id_link_accepted'] != 'True':
            raise ValueError('Identity mismatch')
        review = reviews.get(b['book_id'])
        record = {'book_id':int(b['book_id']),'goodreads_edition_id':b['goodreads_book_id'],
            'goodreads_work_id':b['work_id'],'title':b['title'],'authors':b['authors'],
            'benchmark_include':True,'identity_status':'matched_edition_and_work',
            'content_status':review['status'] if review else 'unreviewed_text_candidate',
            'source_scope':'edition','source_url':x['source_url'],'source_revision':original['revision'],
            'xml_member':x['member'],'xml_member_sha256':x['member_sha256'],
            'source_text_sha256':x['description_sha256'] or None,
            'intro_status':'not_generated','intro_word_count':0,
            'rights':{'description_display':'unresolved','adaptation':'unresolved','cover_display':'unresolved','evidence_url':None},
            'cover_mode':'placeholder_required','product_candidate':not review or review['status']=='title_flag_resolved_only'}
        record['public_intro_ready'] = public_ready(record)
        records.append(record)
    DATA.mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    payload = ''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records).encode('utf-8')
    dest = DATA/'catalogue.jsonl'
    if dest.exists() and dest.read_bytes() != payload:
        raise ValueError('Frozen catalogue differs; create a new version instead')
    if not dest.exists():
        dest.write_bytes(payload)
    verify_manifest(original)
    if sha(ROOT/xml_manifest['path']) != xml_manifest['sha256']:
        raise ValueError('XML ZIP changed after run')
    result = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'catalogue_version':'v1',
        'benchmark_books':len(records),'product_screening_candidates':sum(r['product_candidate'] for r in records),
        'content_status_counts':dict(Counter(r['content_status'] for r in records)),
        'public_intro_ready':sum(r['public_intro_ready'] for r in records),
        'all_book_covers_require_placeholder':all(r['cover_mode']=='placeholder_required' for r in records),
        'local_catalogue_frozen':True,'day02_full_public_catalogue_acceptance':False,
        'raw_and_xml_hashes_verified_before_after':True,'quality_metrics':None,
        'artifact':{'path':str(dest.relative_to(ROOT)),'sha256':sha(dest),'bytes':dest.stat().st_size},
        'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/DATA_MANIFEST.json',index_path,review_path,audit_path]},
        'script_sha256':sha(Path(__file__))}
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__':
    main()
