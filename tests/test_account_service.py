import os
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from booknest.recommender import Recommender
from booknest.account_service import product_recommendations,safe_saved_explanation
from streamlit.testing.v1 import AppTest

class ProductCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.engine=Recommender()
    def test_full_universe_matches_frozen_serving_for_sample_profiles(self):
        catalogue={int(b):{'title':str(b)} for b in self.engine.ids}
        for profile in [[],[(1,5),(2,1),(3,4)],[(10,1),(20,2),(30,3)]]:
            old=self.engine.recommend(profile);new=product_recommendations(self.engine,profile,catalogue)
            self.assertEqual([i['book_id'] for i in old['items']],[i['book_id'] for i in new['items']]);self.assertEqual(old['fallback'],new['fallback'])
    def test_only_approved_unseen_books_and_no_withdrawn_support_titles(self):
        catalogue={b:{'title':'Approved '+str(b)} for b in [1,2,3,4,5,6,7]}
        result=product_recommendations(self.engine,[(1,5),(8,5),(2,1)],catalogue)
        self.assertTrue({i['book_id'] for i in result['items']}<={3,4,5,6,7})
        self.assertTrue(all('WITHDRAWN SECRET TITLE' not in i['explanation'] for i in result['items']))
        self.assertEqual(product_recommendations(self.engine,[(1,5)],{})['items'],[])
    def test_saved_explanation_never_reads_stored_text_or_hidden_title(self):
        result=safe_saved_explanation(self.engine,[{'book_id':1,'rating':5}],2,{2:{'title':'Allowed'}})
        self.assertNotIn('The Hunger Games',result)
        self.assertEqual(safe_saved_explanation(self.engine,[],2,{}),'Thông tin sách hiện chưa sẵn sàng để hiển thị.')
    def test_postgres_mode_without_config_fails_closed(self):
        with patch.dict(os.environ,{'BOOKNEST_MODE':'postgres'}):
            app=AppTest.from_file(str(ROOT/'app/main.py')).run()
            self.assertFalse(app.exception);self.assertEqual(len(app.error),1);self.assertEqual(len(app.select_slider),0)

if __name__=='__main__':unittest.main()
