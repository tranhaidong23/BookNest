"""Meaningful fixtures: distinguish repeated ratings from conflicting labels."""
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_extended import pair_summary, isbn_valid

class AuditTests(unittest.TestCase):
    def test_duplicate_and_conflicting_ratings(self):
        df = pd.DataFrame([(1, 10, 5), (1, 10, 5), (2, 10, 1), (2, 10, 4), (2, 11, 3)],
                          columns=['user_id', 'book_id', 'rating'])
        self.assertEqual(pair_summary(df), {'rows': 5, 'duplicate_extra_rows': 2,
                                           'duplicate_pairs': 2, 'conflicting_rating_pairs': 1})

    def test_same_book_different_users_is_not_duplicate(self):
        df = pd.DataFrame([(1, 10, 4), (2, 10, 4)], columns=['user_id', 'book_id', 'rating'])
        self.assertEqual(pair_summary(df)['duplicate_extra_rows'], 0)

    def test_to_read_pair_duplicates(self):
        df = pd.DataFrame([(1, 10), (1, 10)], columns=['user_id', 'book_id'])
        self.assertEqual(pair_summary(df)['duplicate_extra_rows'], 1)
        self.assertEqual(pair_summary(df)['conflicting_rating_pairs'], 0)

    def test_isbn_known_checksums(self):
        for value in ['0-306-40615-2', '9780306406157', '080442957X']:
            self.assertTrue(isbn_valid(value), value)
        for value in ['', '9780306406158', '0306406153', 'not-an-isbn']:
            self.assertFalse(isbn_valid(value), value)

if __name__ == '__main__':
    unittest.main()
