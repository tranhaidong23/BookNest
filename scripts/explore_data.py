"""Read-only introduction to the Goodbooks-10k book/rating join."""
import csv
from itertools import islice
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/raw/goodbooks-10k'

def main():
    with (DATA / 'books.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    books = {row['book_id']: row for row in rows}
    if len(books) != len(rows):
        raise ValueError('Duplicate book_id would overwrite a lookup entry')
    with (DATA / 'ratings.csv').open(encoding='utf-8-sig', newline='') as stream:
        for rating in islice(csv.DictReader(stream), 5):
            book = books[rating['book_id']]
            print(f"User {rating['user_id']} | {book['title']} | {rating['rating']} stars")
    print(f'Unique books: {len(books):,}')
    for field in ['title', 'authors', 'isbn', 'language_code']:
        print(f'Missing {field}: {sum(not b.get(field, "").strip() for b in books.values()):,}')

if __name__ == '__main__':
    main()
