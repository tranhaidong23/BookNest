"""Download a pinned Goodbooks-10k snapshot; audit without changing raw data."""
import argparse
import csv
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def get(url):
    return urlopen(Request(url, headers={'User-Agent': 'BookNest-academic-project'}), timeout=120)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def collect():
    manifest_path = ROOT / 'docs/DATA_MANIFEST.json'
    old = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    if old:
        revision = old['revision']
    else:
        with get('https://api.github.com/repos/zygmuntz/goodbooks-10k/commits/master') as response:
            revision = json.load(response)['sha']
    base = f'https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/{revision}/'
    raw = ROOT / 'data/raw/goodbooks-10k'
    raw.mkdir(parents=True, exist_ok=True)
    entries = []
    for name in ['README.md', 'LICENSE', 'books.csv', 'ratings.csv', 'tags.csv', 'book_tags.csv', 'to_read.csv']:
        target = raw / name
        prior = next((f for f in old['files'] if f['name'] == name), None) if old else None
        if target.exists():
            if not prior:
                raise RuntimeError(f'Unmanifested existing file: {name}; refusing overwrite')
            if sha(target) != prior['sha256']:
                raise RuntimeError(f'Existing file hash mismatch: {name}')
        else:
            print(f'Downloading {name}', flush=True)
            part = target.with_suffix(target.suffix + '.part')
            with get(base + name) as response, part.open('wb') as output:
                for block in iter(lambda: response.read(1024 * 1024), b''):
                    output.write(block)
                expected = response.headers.get('Content-Length')
            if expected is not None and part.stat().st_size != int(expected):
                raise RuntimeError(f'Incomplete download: {name}')
            os.replace(part, target)
        entry = {'name': name, 'path': target.relative_to(ROOT).as_posix(),
                 'url': base + name, 'bytes': target.stat().st_size, 'sha256': sha(target)}
        if name.endswith('.csv'):
            with target.open(encoding='utf-8-sig', newline='') as stream:
                reader = csv.reader(stream)
                entry['columns'] = next(reader)
                entry['rows'] = sum(1 for _ in reader)
        entries.append(entry)
        # Save after each verified download so reruns can resume safely.
        dump(manifest_path, {'dataset': 'Goodbooks-10k', 'revision': revision,
                            'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
                            'license_declared_by_repository': 'CC BY-SA 4.0', 'files': entries})
    print('Snapshot downloaded and SHA-256 recorded.', flush=True)

def audit():
    manifest = json.loads((ROOT / 'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    for entry in manifest['files']:
        assert sha(ROOT / entry['path']) == entry['sha256'], entry['name']
    raw = ROOT / 'data/raw/goodbooks-10k'
    with (raw / 'books.csv').open(encoding='utf-8-sig', newline='') as stream:
        books = list(csv.DictReader(stream))
    book_ids = {int(b['book_id']) for b in books}
    gr_ids = {int(b['goodreads_book_id']) for b in books}
    counts, users, rated_books = Counter(), Counter(), set()
    invalid_rating = unknown_book = rating_rows = 0
    with (raw / 'ratings.csv').open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            uid, bid, rating = int(row['user_id']), int(row['book_id']), int(row['rating'])
            rating_rows += 1
            counts[rating] += 1
            users[uid] += 1
            rated_books.add(bid)
            invalid_rating += rating not in range(1, 6)
            unknown_book += bid not in book_ids
    with (raw / 'tags.csv').open(encoding='utf-8-sig', newline='') as stream:
        tag_ids = {int(row['tag_id']) for row in csv.DictReader(stream)}
    bad_tag_book = bad_tag_id = 0
    with (raw / 'book_tags.csv').open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            bad_tag_book += int(row['goodreads_book_id']) not in gr_ids
            bad_tag_id += int(row['tag_id']) not in tag_ids
    missing = {key: sum(not b[key].strip() for b in books) for key in books[0]}
    report = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'revision': manifest['revision'],
        'raw_hashes_verified': True, 'books': len(books), 'unique_book_ids': len(book_ids),
        'ratings': rating_rows, 'users': len(users), 'rated_books': len(rated_books),
        'rating_distribution': dict(sorted(counts.items())), 'invalid_ratings': invalid_rating,
        'ratings_unknown_book_ids': unknown_book, 'minimum_ratings_per_user': min(users.values()),
        'maximum_ratings_per_user': max(users.values()),
        'observed_density': rating_rows / (len(users) * len(book_ids)),
        'book_tags_unknown_book_ids': bad_tag_book, 'book_tags_unknown_tag_ids': bad_tag_id,
        'missing_book_fields': missing,
        'description_column_present': 'description' in books[0],
        'ratings_timestamp_column_present': 'timestamp' in next(f['columns'] for f in manifest['files'] if f['name'] == 'ratings.csv'),
        'not_yet_checked': ['duplicate user-book ratings', 'to_read foreign keys',
                            'cover URL availability', 'description matching and coverage',
                            'public display rights for third-party metadata and covers'],
        'no_model_trained': True, 'quality_metrics': None,
    }
    dump(ROOT / 'reports/day01/data_audit.json', report)
    print(json.dumps({k: report[k] for k in ['books', 'ratings', 'users', 'invalid_ratings', 'ratings_unknown_book_ids', 'description_column_present']}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['collect', 'audit'])
    args = parser.parse_args()
    collect() if args.action == 'collect' else audit()
