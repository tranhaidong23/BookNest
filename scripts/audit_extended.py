"""Read-only extended audit. Run from any directory; output aggregate reports."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/goodbooks-10k'
OUT = ROOT / 'reports/day01/extended_20261119'

def pair_summary(frame):
    keys = ['user_id', 'book_id']
    duplicated = frame.duplicated(keys, keep=False)
    repeated = frame.loc[duplicated]
    conflicts = 0
    if 'rating' in frame and not repeated.empty:
        conflicts = int((repeated.groupby(keys)['rating'].nunique(dropna=False) > 1).sum())
    return {
        'rows': len(frame),
        'duplicate_extra_rows': int(frame.duplicated(keys).sum()),
        'duplicate_pairs': int(len(repeated.drop_duplicates(keys))),
        'conflicting_rating_pairs': conflicts,
    }

def isbn_valid(value):
    value = value.replace('-', '').replace(' ', '').upper()
    if len(value) == 10 and value[:9].isdigit() and (value[-1].isdigit() or value[-1] == 'X'):
        digits = [int(c) for c in value[:9]] + [10 if value[-1] == 'X' else int(value[-1])]
        return sum((10 - i) * d for i, d in enumerate(digits)) % 11 == 0
    if len(value) == 13 and value.isdigit():
        return sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(value)) % 10 == 0
    return False

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def verify_manifest(manifest):
    for entry in manifest['files']:
        path = ROOT / entry['path']
        if sha(path) != entry['sha256']:
            raise ValueError(f"Raw hash mismatch: {entry['name']}")

def main():
    manifest = json.loads((ROOT / 'docs/DATA_MANIFEST.json').read_text(encoding='utf-8'))
    verify_manifest(manifest)
    books = pd.read_csv(RAW / 'books.csv', dtype=str, keep_default_na=False)
    ratings = pd.read_csv(RAW / 'ratings.csv', dtype={'user_id': 'int32', 'book_id': 'int32', 'rating': 'int8'})
    to_read = pd.read_csv(RAW / 'to_read.csv', dtype={'user_id': 'int32', 'book_id': 'int32'})
    tags = pd.read_csv(RAW / 'tags.csv', dtype={'tag_id': 'int32', 'tag_name': str}, keep_default_na=False)
    book_tags = pd.read_csv(RAW / 'book_tags.csv', dtype={'goodreads_book_id': 'int32', 'tag_id': 'int32', 'count': 'int32'})
    print('Loaded CSVs; checking duplicates and metadata.', flush=True)
    user_counts = ratings.groupby('user_id').size()
    book_counts = ratings.groupby('book_id').size()
    isbn_checks = {}
    for column in ['isbn', 'isbn13']:
        present = books[column].str.strip().ne('')
        valid = books.loc[present, column].map(isbn_valid)
        isbn_checks[column] = {
            'missing': int((~present).sum()), 'present': int(present.sum()),
            'raw_text_not_valid_isbn': int((~valid).sum()),
            'raw_scientific_notation_rows': int(books.loc[present, column].str.contains(r'[eE][+-]?\d+', regex=True).sum()),
            'raw_shorter_than_10_digits_rows': int(books.loc[present, column].str.fullmatch(r'\d{1,9}').sum()),
            'note': 'Checks raw text only: scientific notation and possibly lost leading zeros are source serialization issues. Do not conclude the underlying books have invalid ISBNs. No repair applied; lost precision cannot be assumed recoverable.'
        }
    rating_keys = pd.MultiIndex.from_frame(ratings[['user_id', 'book_id']])
    to_read_keys = pd.MultiIndex.from_frame(to_read[['user_id', 'book_id']])
    years = pd.to_numeric(books['original_publication_year'], errors='coerce')
    rated_ids = set(ratings['book_id'])
    catalogue_ids = set(books['book_id'].astype(int))
    most_popular = book_counts.sort_values(ascending=False)
    top1pct = max(1, len(book_counts) // 100)
    distribution = ratings['rating'].value_counts().sort_index().rename_axis('rating').reset_index(name='count')
    distribution['fraction'] = distribution['count'] / len(ratings)
    top_tags = book_tags.groupby('tag_id')['count'].sum().rename('shelf_count_sum').reset_index()
    top_tags = top_tags.merge(tags, on='tag_id', how='left', validate='one_to_one').sort_values('shelf_count_sum', ascending=False).head(30)
    result = {
        'date': '2026-11-19', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_revision': manifest['revision'], 'python': platform.python_version(), 'pandas': pd.__version__,
        'books': len(books), 'users': len(user_counts), 'ratings': pair_summary(ratings),
        'invalid_rating_rows': int((~ratings['rating'].between(1, 5)).sum()),
        'rating_unknown_book_rows': int((~ratings['book_id'].isin(catalogue_ids)).sum()),
        'books_duplicate_id_extra_rows': int(books.duplicated('book_id').sum()),
        'books_duplicate_work_id_extra_rows': int(books.duplicated('work_id').sum()),
        'missing_metadata': {c: int(books[c].str.strip().eq('').sum()) for c in books},
        'isbn_checks': isbn_checks,
        'year_flags': {'missing_or_non_numeric': int(years.isna().sum()),
                       'non_positive': int(years.le(0).sum()), 'after_2017_snapshot': int(years.gt(2017).sum()),
                       'note': 'Flags for review, not proof of error; BCE dates may be legitimate.'},
        'to_read': {**pair_summary(to_read),
                    'unknown_book_rows': int((~to_read['book_id'].isin(catalogue_ids)).sum()),
                    'unknown_user_rows': int((~to_read['user_id'].isin(user_counts.index)).sum()),
                    'rows_also_in_ratings': int(to_read_keys.isin(rating_keys).sum()),
                    'note': 'Want-to-read is a separate signal, not a star rating or automatic negative.'},
        'tags': {'rows': len(tags), 'duplicate_id_extra_rows': int(tags.duplicated('tag_id').sum()),
                 'empty_names': int(tags['tag_name'].str.strip().eq('').sum()),
                 'book_tag_rows': len(book_tags),
                 'duplicate_book_tag_extra_rows': int(book_tags.duplicated(['goodreads_book_id', 'tag_id']).sum()),
                 'negative_counts': int(book_tags['count'].lt(0).sum()),
                 'zero_counts': int(book_tags['count'].eq(0).sum()),
                 'unknown_book_rows': int((~book_tags['goodreads_book_id'].isin(books['goodreads_book_id'].astype(int))).sum()),
                 'unknown_tag_rows': int((~book_tags['tag_id'].isin(tags['tag_id'])).sum()),
                 'note': 'Shelves include reading status and personal labels; not all are genres.'},
        'rating_distribution': {str(row.rating): int(row.count) for row in distribution.itertuples()},
        'user_rating_count_quantiles': {str(k): float(v) for k, v in user_counts.quantile([0, .25, .5, .75, 1]).items()},
        'book_rating_count_quantiles': {str(k): float(v) for k, v in book_counts.quantile([0, .25, .5, .75, 1]).items()},
        'observed_pair_density': len(ratings.drop_duplicates(['user_id', 'book_id'])) / (len(user_counts) * len(books)),
        'top_one_percent_books_rating_share': float(most_popular.head(top1pct).sum() / len(ratings)),
        'description_column_present': 'description' in books,
        'ratings_timestamp_present': 'timestamp' in ratings,
        'rated_books_not_in_catalogue': len(rated_ids - catalogue_ids),
        'unverified': ['cover URL availability', 'description source coverage and matching',
                       'public display rights for third-party book text/covers', 'off-device backup'],
        'quality_metrics': None, 'models_trained': False,
    }
    verify_manifest(manifest)
    result['raw_hashes_verified_before_and_after'] = True
    OUT.mkdir(parents=True, exist_ok=True)
    distribution.to_csv(OUT / 'rating_distribution.csv', index=False)
    top_tags.to_csv(OUT / 'top_shelves.csv', index=False)
    books['language_code'].replace('', '(missing)').value_counts().rename_axis('language_code').reset_index(name='books').to_csv(OUT / 'languages.csv', index=False)
    (OUT / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['books', 'users', 'ratings', 'to_read', 'isbn_checks', 'tags']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
