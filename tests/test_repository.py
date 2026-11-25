import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from booknest.repository import PostgresRepository

class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        def forbidden():raise AssertionError('Invalid input reached the database')
        self.repo=PostgresRepository(forbidden,'10000000-0000-0000-0000-000000000001')
    def test_rating_rejects_bool_float_and_out_of_range(self):
        for book,rating in [(True,5),(1,False),(1,0),(1,6),(1,3.2),(-1,3)]:
            with self.assertRaises(ValueError):self.repo.save_rating(book,rating)
    def test_limits_states_and_uuid(self):
        with self.assertRaises(ValueError):self.repo.save_shelf(1,'unknown')
        with self.assertRaises(ValueError):self.repo.history(1000)
        with self.assertRaises(ValueError):self.repo.search_catalogue(limit=True)
        with self.assertRaises(ValueError):self.repo.delete_run('not-a-uuid')
    def test_recommendations_cannot_include_seen_or_duplicate_books(self):
        for items in [[{'book_id':1,'explanation':'test'}],[{'book_id':2,'explanation':'test'}]*2]:
            with self.assertRaises(ValueError):self.repo.save_run([(1,5)],items,'model','catalogue')
    def test_snapshot_rejects_duplicate_profile_and_empty_explanation(self):
        with self.assertRaises(ValueError):self.repo.save_run([(1,5),(1,4)],[{'book_id':2,'explanation':'test'}],'model','catalogue')
        with self.assertRaises(ValueError):self.repo.save_run([(1,5)],[{'book_id':2,'explanation':''}],'model','catalogue')

if __name__=='__main__':unittest.main()
