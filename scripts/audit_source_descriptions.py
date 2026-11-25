"""Audit pinned Goodbooks XML archive, without extracting reviews or modifying raw CSVs."""
import argparse
import csv
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

from audit_extended import isbn_valid, sha, verify_manifest
from pilot_descriptions import norm, candidate_isbn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/day01/descriptions_20261119'
DETAIL = ROOT / 'data/processed/descriptions_20261119'
ARCHIVE = ROOT / 'data/raw/goodbooks-10k-xml/books_xml.zip'
MANIFEST = OUT / 'xml_manifest.json'

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden += 1
        elif tag in {'br', 'p', 'div', 'li'}:
            self.parts.append(' ')
    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)
        elif tag in {'p', 'div', 'li'}:
            self.parts.append(' ')
    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

def clean_text(value):
    parser = TextOnly()
    parser.feed(value)
    return re.sub(r'\s+', ' ', ''.join(parser.parts)).strip()

def accept_id_link(edition_matches, work_matches, record_count):
    return bool(edition_matches and work_matches and record_count == 1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    original = json.loads((ROOT / 'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    verify_manifest(original)
    url = f"https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/{original['revision']}/books_xml/books_xml.zip"
    OUT.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        if not args.fetch:
            raise RuntimeError('Archive missing; use --fetch')
        if MANIFEST.exists():
            raise RuntimeError('Manifest exists but archive missing: restore matching archive explicitly')
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        temp = ARCHIVE.with_suffix('.download')
        with urllib.request.urlopen(url, timeout=60) as response, temp.open('wb') as f:
            while block := response.read(1024 * 1024):
                f.write(block)
        with zipfile.ZipFile(temp) as z:
            if z.testzip() is not None:
                raise ValueError('ZIP integrity failure')
        temp.rename(ARCHIVE)
        MANIFEST.write_text(json.dumps({'url': url, 'revision': original['revision'],
            'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'path': str(ARCHIVE.relative_to(ROOT)),
            'bytes': ARCHIVE.stat().st_size, 'sha256': sha(ARCHIVE),
            'license_note': 'Repository declares CC BY-SA 4.0; third-party descriptions and covers require separate rights review.'}, indent=2) + '\n', encoding='utf-8')
    archive_manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if sha(ARCHIVE) != archive_manifest['sha256']:
        raise ValueError('Archive hash mismatch')
    with (ROOT / 'data/raw/goodbooks-10k/books.csv').open(encoding='utf-8', newline='') as f:
        books = list(csv.DictReader(f))
    by_id = {b['goodreads_book_id']: b for b in books}
    rows = []
    errors = []
    seen = Counter()
    with zipfile.ZipFile(ARCHIVE) as z:
        for member in z.infolist():
            if not member.filename.endswith('.xml'):
                continue
            body = z.read(member)
            try:
                root = ET.fromstring(body)
                book = root.find('book') if root.tag != 'book' else root
                if book is None:
                    raise ValueError('No book element')
                gid = book.findtext('id', '').strip()
                seen[gid] += 1
                source = by_id.get(gid)
                raw_desc = book.findtext('description', '')
                desc = clean_text(raw_desc)
                authors = [a.findtext('name', '') for a in book.findall('authors/author')]
                isbn = book.findtext('isbn', '').strip()
                isbn13 = book.findtext('isbn13', '').strip()
                work_id = book.findtext('work/id', '').strip()
                row = {'member': member.filename, 'member_sha256': hashlib.sha256(body).hexdigest(),
                    'book_id': source['book_id'] if source else '', 'goodreads_book_id': gid,
                    'work_id': work_id, 'xml_title': book.findtext('title', ''), 'xml_authors': ' | '.join(authors),
                    'edition_id_match': source is not None, 'work_id_match': bool(source and work_id == source['work_id']),
                    'title_match': bool(source and norm(book.findtext('title', '')) == norm(source['title'])),
                    'primary_author_match': bool(source and any(norm(a) == norm(source['authors'].split(',')[0]) for a in authors)),
                    'xml_isbn': isbn, 'xml_isbn13': isbn13, 'isbn_valid': isbn_valid(isbn), 'isbn13_valid': isbn_valid(isbn13),
                    'csv_isbn_candidate_agrees': bool(source and isbn and candidate_isbn(source['isbn'])[0] == isbn),
                    'description_raw_chars': len(raw_desc), 'description_text_chars': len(desc),
                    'description_sha256': hashlib.sha256(desc.encode()).hexdigest() if desc else '',
                    'known_ingest_placeholder': 'for ingest only' in desc.casefold(),
                    'has_html': bool(re.search(r'<[^>]+>', raw_desc)),
                    'source_url': f'https://www.goodreads.com/book/show/{gid}',
                    'rights_status': 'unresolved', 'public_display_allowed': False}
                rows.append(row)
            except (ET.ParseError, ValueError) as exc:
                errors.append({'member': member.filename, 'error': str(exc)})
    for r in rows:
        r['unique_edition_record'] = seen[r['goodreads_book_id']] == 1
        r['id_link_accepted'] = accept_id_link(r['edition_id_match'], r['work_id_match'], seen[r['goodreads_book_id']])
    DETAIL.mkdir(parents=True, exist_ok=True)
    with (DETAIL / 'xml_matches.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    matched = [r for r in rows if r['id_link_accepted']]
    counts = Counter(r['description_sha256'] for r in matched if r['description_sha256'])
    issues = [r for r in rows if not r['id_link_accepted'] or not r['title_match'] or not r['primary_author_match']
              or r['description_text_chars'] < 80 or counts[r['description_sha256']] > 1 or r['known_ingest_placeholder']]
    (DETAIL / 'xml_review_queue.json').write_text(json.dumps(issues, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verify_manifest(original)
    assert sha(ARCHIVE) == archive_manifest['sha256']
    metrics = {'date': '2026-11-19', 'source_revision': original['revision'], 'catalogue_books': len(books),
        'xml_records_parsed': len(rows), 'parse_errors': errors, 'missing_catalogue_edition_ids': sorted(set(by_id) - set(seen)),
        'duplicate_edition_ids': {k: v for k, v in seen.items() if v > 1},
        'id_link_accepted': len(matched), 'title_disagreements': sum(not r['title_match'] for r in matched),
        'primary_author_disagreements': sum(not r['primary_author_match'] for r in matched),
        'nonempty_descriptions': sum(r['description_text_chars'] > 0 for r in matched),
        'nonempty_description_coverage': sum(r['description_text_chars'] > 0 for r in matched) / len(books),
        'empty_descriptions': sum(r['description_text_chars'] == 0 for r in matched),
        'short_nonempty_descriptions_under_80_chars': sum(0 < r['description_text_chars'] < 80 for r in matched),
        'descriptions_with_html': sum(r['has_html'] for r in matched),
        'duplicate_nonempty_description_groups': sum(n > 1 for n in counts.values()),
        'duplicate_nonempty_description_rows': sum(n for n in counts.values() if n > 1),
        'known_ingest_placeholder_rows': sum(r['known_ingest_placeholder'] for r in matched),
        'valid_xml_isbn10': sum(r['isbn_valid'] for r in matched), 'valid_xml_isbn13': sum(r['isbn13_valid'] for r in matched),
        'csv_isbn_candidate_agrees': sum(r['csv_isbn_candidate_agrees'] for r in matched),
        'review_queue_rows': len(issues), 'public_rights_cleared_books': 0,
        'semantic_description_quality': None, 'language_detection': 'not performed',
        'quality_metrics': None, 'raw_and_archive_hashes_verified_before_and_after': True}
    (OUT / 'xml_coverage.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
