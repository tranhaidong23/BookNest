"""Small, cached Open Library pilot. No production acceptance or raw mutation.
Run with --fetch to permit network; default replays immutable cached responses.
"""
import argparse
import csv
import hashlib
import json
import random
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from audit_extended import isbn_valid, verify_manifest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/day01/descriptions_20261119'
CACHE = ROOT / 'data/external/openlibrary/pilot_20261119'

def candidate_isbn(raw):
    if isbn_valid(raw):
        return raw, 'raw_checksum_valid'
    if re.fullmatch(r'\d{1,9}', raw) and isbn_valid(raw.zfill(10)):
        return raw.zfill(10), 'leading_zero_hypothesis'
    return '', 'unavailable'

def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value).casefold() if c.isalnum())

def base_title(value):
    return re.sub(r'\s*\([^)]*\)\s*$', '', value).strip()

def description(record):
    value = record.get('description', '')
    return (value.get('value', '') if isinstance(value, dict) else value).strip()

class Client:
    def __init__(self, fetch):
        self.fetch = fetch
        self.entries = []
        self.last = 0

    def get(self, path):
        url = 'https://openlibrary.org' + path
        key = hashlib.sha256(url.encode()).hexdigest()
        file = CACHE / (key + '.json')
        if not file.exists():
            if not self.fetch:
                raise RuntimeError('Missing cache: ' + url)
            time.sleep(max(0, 1.1 - (time.monotonic() - self.last)))
            req = urllib.request.Request(url, headers={'User-Agent': 'BookNest-Educational-Pilot/0.1'})
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    body = response.read()
                    status = response.status
                payload = {'url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                           'status': status, 'body_sha256': hashlib.sha256(body).hexdigest(),
                           'body': body.decode('utf-8')}
            except Exception as exc:
                payload = {'url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                           'status': None, 'error': str(exc), 'body': '{}'}
            self.last = time.monotonic()
            CACHE.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        payload = json.loads(file.read_text(encoding='utf-8'))
        if payload.get('body_sha256') and hashlib.sha256(payload['body'].encode()).hexdigest() != payload['body_sha256']:
            raise ValueError('Cache body hash mismatch')
        self.entries.append({k: v for k, v in payload.items() if k != 'body'} | {
            'path': str(file.relative_to(ROOT)), 'cache_sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
        return json.loads(payload['body'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    verify_manifest(manifest)
    with (ROOT / 'data/raw/goodbooks-10k/books.csv').open(encoding='utf-8', newline='') as f:
        books = sorted(csv.DictReader(f), key=lambda b: int(b['book_id']))
    rng = random.Random(20261119)
    sample = [dict(b, stratum=str(i + 1)) for i in range(10) for b in rng.sample(books[i*1000:(i+1)*1000], 2)]
    client = Client(args.fetch)
    isbns = [candidate_isbn(b['isbn'])[0] for b in sample]
    query = urllib.parse.urlencode({'bibkeys': ','.join('ISBN:' + i for i in isbns if i), 'jscmd': 'details', 'format': 'json'})
    batch = client.get('/api/books?' + query)
    results = []
    for b, isbn in zip(sample, isbns):
        edition = batch.get('ISBN:' + isbn, {}).get('details', {})
        author_names = [a['name'] for a in edition.get('authors', []) if a.get('name')]
        for a in edition.get('authors', []):
            if not a.get('name') and a.get('key', '').startswith('/authors/'):
                author_names.append(client.get(a['key'] + '.json').get('name', ''))
        work_keys = [w['key'] for w in edition.get('works', [])]
        method = 'isbn_lookup' if edition else 'title_author_search'
        if not edition:
            q = urllib.parse.urlencode({'title': base_title(b['title']), 'author': b['authors'].split(',')[0],
                                        'fields': 'key,title,author_name', 'limit': 5})
            search = client.get('/search.json?' + q)
            docs = search.get('docs', [])
            # Search only generates candidates: never silently chooses first of several.
            eligible = [d for d in docs if norm(d.get('title', '')) in {norm(base_title(b['title'])), norm(b['original_title'])}
                        and any(norm(a) == norm(b['authors'].split(',')[0]) for a in d.get('author_name', []))]
            if len(eligible) == 1:
                work_keys = [eligible[0]['key']]
                author_names = eligible[0].get('author_name', [])
            search_count = search.get('numFound', search.get('num_found'))
        else:
            search_count = None
        works = [client.get(k + '.json') for k in work_keys if re.fullmatch(r'/works/OL\d+W', k)]
        titles = [edition.get('title', '')] + [w.get('title', '') for w in works]
        title_ok = any(norm(t) in {norm(base_title(b['title'])), norm(b['original_title'])} for t in titles if t)
        author_ok = any(norm(a) == norm(b['authors'].split(',')[0]) for a in author_names if a)
        goodreads = edition.get('identifiers', {}).get('goodreads', [])
        direct_id = b['goodreads_book_id'] in [str(x) for x in goodreads]
        ed_desc = description(edition)
        work_desc = [description(w) for w in works if description(w)]
        result = {k: b[k] for k in ['book_id', 'stratum', 'title', 'original_title', 'authors', 'goodreads_book_id', 'work_id', 'isbn', 'language_code']}
        result.update(isbn_candidate=isbn, isbn_status=candidate_isbn(b['isbn'])[1], method=method,
                      edition_key=edition.get('key'), work_keys=work_keys, source_titles=titles,
                      source_authors=author_names, source_goodreads_ids=goodreads,
                      source_isbn10=edition.get('isbn_10', []), source_isbn13=edition.get('isbn_13', []),
                      source_languages=edition.get('languages', []), source_publish_date=edition.get('publish_date'),
                      source_publishers=edition.get('publishers', []), search_num_found=search_count,
                      title_agrees=title_ok, primary_author_agrees=author_ok, goodreads_edition_id_agrees=direct_id,
                      edition_description_chars=len(ed_desc), work_description_chars=[len(d) for d in work_desc],
                      description_available=bool(ed_desc or work_desc),
                      automated_status='candidate_consistent' if title_ok and author_ok else 'needs_review',
                      rights_status='unresolved', public_display_allowed=False)
        results.append(result)
        print(b['book_id'], result['automated_status'], bool(ed_desc), bool(work_desc), flush=True)
    verify_manifest(manifest)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [('matches.json', results), ('response_manifest.json', client.entries)]:
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    stats = {'date': '2026-11-19', 'seed': 20261119, 'sample_size': len(sample),
             'sampling': '2 uniformly sampled books per contiguous 1000 book_id block; small diagnostic pilot, not full catalogue coverage',
             'catalogue_size': len(books), 'catalogue_isbn_candidate_status': dict(Counter(candidate_isbn(b['isbn'])[1] for b in books)),
             'sample_isbn_candidate_status': dict(Counter(r['isbn_status'] for r in results)),
             'edition_records_found': sum(bool(r['edition_key']) for r in results),
             'description_available_before_matching': sum(r['description_available'] for r in results),
             'automated_consistent_candidates': sum(r['automated_status'] == 'candidate_consistent' for r in results),
             'consistent_candidates_with_description': sum(r['automated_status'] == 'candidate_consistent' and r['description_available'] for r in results),
             'goodreads_edition_id_agrees': sum(r['goodreads_edition_id_agrees'] for r in results),
             'request_errors': sum(e['status'] is None for e in client.entries),
             'full_catalogue_description_coverage': None, 'quality_metrics': None,
             'raw_hashes_verified_before_and_after': True}
    (OUT / 'coverage.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    main()
