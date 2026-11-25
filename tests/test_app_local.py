import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from booknest.recommender import Recommender,load_local_catalogue,explanation
from streamlit.testing.v1 import AppTest

class ServingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.engine=Recommender();cls.catalogue=load_local_catalogue()

    def test_rejects_unknown_duplicate_and_invalid_ratings(self):
        for profile in [[(999999,1)],[(1,5),(1,4)],[(1,0)],[(1,6)],[(True,5)],[(1,3.5)]]:
            with self.assertRaises(ValueError):self.engine.recommend(profile)

    def test_evidence_only_uses_supplied_positive_ratings(self):
        profile=[(1,5),(2,1),(3,4)];result=self.engine.recommend(profile)
        self.assertEqual(len(result['items']),10)
        self.assertFalse({x['book_id'] for x in result['items']}&{1,2,3})
        for item in result['items']:
            for evidence in item['evidence']:
                self.assertIn(evidence['book_id'],{1,3});self.assertGreater(evidence['contribution'],0)
            self.assertTrue(explanation(item,self.catalogue))
        self.assertFalse(self.engine.weight.flags.writeable)
        fallback=self.engine.recommend([(1,1),(2,2),(3,3)])
        self.assertTrue(fallback['fallback']);self.assertTrue(all(not i['evidence'] for i in fallback['items']))

class LocalAppTests(unittest.TestCase):
    def app(self):
        a=AppTest.from_file(str(ROOT/'app/main.py'),default_timeout=30).run()
        self.assertFalse(a.exception);return a

    def test_search_empty_and_session_isolation(self):
        a=self.app();a.text_input[0].set_value('no-such-book-qzx827').run()
        self.assertFalse(a.exception);self.assertEqual(len(a.select_slider),0)
        a.session_state['ratings']={1:5}
        b=self.app();self.assertEqual(b.session_state['ratings'],{})

    def test_rating_shelf_recommendations_and_history(self):
        a=self.app();books=[]
        for offset in range(3):
            slider=a.select_slider[offset];book=int(slider.key.rsplit('_',1)[1]);books.append(book)
            slider.set_value(5).run();a.button(key=f'save_catalogue_{book}').click().run()
        self.assertEqual(len(a.session_state['ratings']),3)
        a.button(key=f'add_catalogue_{books[0]}').click().run()
        self.assertEqual(a.session_state['shelf'][books[0]],'Muốn đọc')
        a.sidebar.radio[0].set_value('Gợi ý cho bạn').run();a.button[0].click().run()
        self.assertFalse(a.exception);run=a.session_state['latest']
        self.assertEqual(len(run['items']),10);self.assertFalse({i['book_id'] for i in run['items']}&set(books))
        self.assertEqual(len(a.session_state['history']),1)
        snapshot=list(a.session_state['history'][0]['profile'])
        a.sidebar.radio[0].set_value('Khám phá').run();a.button(key=f'del_catalogue_{books[0]}').click().run()
        self.assertIsNone(a.session_state['latest']);self.assertEqual(a.session_state['history'][0]['profile'],snapshot)
        a.sidebar.radio[0].set_value('Lịch sử').run();self.assertFalse(a.exception);self.assertEqual(len(a.expander),1)

    def test_public_mode_stops_before_catalogue_display(self):
        with patch.dict(os.environ,{'BOOKNEST_MODE':'public'}):
            a=AppTest.from_file(str(ROOT/'app/main.py')).run()
            self.assertFalse(a.exception);self.assertEqual(len(a.error),1);self.assertEqual(len(a.select_slider),0)

if __name__=='__main__':unittest.main()
