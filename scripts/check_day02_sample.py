"""Offline recheck of the existing 20-book pilot; preserves historical reports."""
import csv
import json
import platform
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from audit_extended import sha, verify_manifest
from audit_source_descriptions import clean_text
from pilot_descriptions import norm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/day02/feasibility_20261119'

def main():
    original = json.loads((ROOT / 'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    archive_manifest = json.loads((ROOT / 'reports/day01/descriptions_20261119/xml_manifest.json').read_text(encoding='utf-8'))
    archive = ROOT / archive_manifest['path']
    verify_manifest(original)
    assert sha(archive) == archive_manifest['sha256']
    matches = json.loads((ROOT / 'reports/day01/descriptions_20261119/matches.json').read_text(encoding='utf-8'))
    with (ROOT / 'data/raw/goodbooks-10k/books.csv').open(encoding='utf-8', newline='') as f:
        books = {b['book_id']: b for b in csv.DictReader(f)}
    with (ROOT / 'data/processed/descriptions_20261119/xml_matches.csv').open(encoding='utf-8', newline='') as f:
        index = {b['book_id']: b for b in csv.DictReader(f)}
    rows = []
    with zipfile.ZipFile(archive) as z:
        for sample in matches:
            b = books[sample['book_id']]
            xml = ET.fromstring(z.read(index[b['book_id']]['member'])).find('book')
            text = clean_text(xml.findtext('description', ''))
            authors = [a.findtext('name', '') for a in xml.findall('authors/author')]
            rows.append({'book_id': b['book_id'],
                'edition_id_matches': xml.findtext('id', '').strip() == b['goodreads_book_id'],
                'work_id_matches': xml.findtext('work/id', '').strip() == b['work_id'],
                'title_matches': norm(xml.findtext('title', '')) == norm(b['title']),
                'primary_author_matches': any(norm(a) == norm(b['authors'].split(',')[0]) for a in authors),
                'description_text_chars': len(text), 'description_nonempty': bool(text)})
    verify_manifest(original)
    assert sha(archive) == archive_manifest['sha256']
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
        'scope': 'NEW offline XML sample check, same 20 book IDs as historical OL pilot; no new API lookup or full audit',
        'sample_size': len(rows), 'sampling': 'Historical seed 20261119; two books per 1000 book_id block',
        'both_ids_match': sum(r['edition_id_matches'] and r['work_id_matches'] for r in rows),
        'title_and_author_match': sum(r['title_matches'] and r['primary_author_matches'] for r in rows),
        'nonempty_descriptions': sum(r['description_nonempty'] for r in rows),
        'sample_description_coverage': sum(r['description_nonempty'] for r in rows)/len(rows),
        'raw_csv_and_archive_hashes_verified_before_after': True,
        'unit_tests_rerun_this_check': False, 'full_audit_rerun_this_check': False,
        'public_rights_verified': False, 'quality_metrics': None, 'rows': rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'sample_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
