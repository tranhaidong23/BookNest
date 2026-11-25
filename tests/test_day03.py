import sys
import tempfile
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_day03 import clean_tags, validate_ratings, year_value, frozen_write, nullable_text

class Day03Tests(unittest.TestCase):
    def test_whitespace_only_metadata_is_null(self):
        self.assertIsNone(nullable_text('  \t'))
        self.assertEqual(nullable_text('  Book  II  '),'Book  II')

    def test_conflicting_tags_all_quarantined_and_exact_duplicate_removed(self):
        frame=pd.DataFrame([(1,2,8),(1,2,7),(2,3,4),(2,3,4),(3,4,-1),(4,5,0)],
                           columns=['goodreads_book_id','tag_id','count'])
        kept,excluded=clean_tags(frame)
        self.assertEqual(kept['count'].tolist(),[4,0])
        self.assertEqual(excluded['reason'].value_counts().to_dict(),
                         {'conflicting_key':2,'exact_duplicate_extra':1,'negative_count':1})
        self.assertEqual(len(kept)+len(excluded),len(frame))

    def test_rating_conflicts_unknown_ids_and_missing_fail_closed(self):
        good=pd.DataFrame([(1,2,4),(2,2,1)],columns=['user_id','book_id','rating'])
        validate_ratings(good,{2})
        for bad in [pd.concat([good,good.iloc[:1]]),good.assign(book_id=99),good.assign(rating=0),good.assign(rating=None)]:
            with self.assertRaises(ValueError): validate_ratings(bad,{2})

    def test_bce_preserved_missing_not_zero(self):
        self.assertEqual(year_value('-500.0'),(-500,'review_non_positive'))
        self.assertEqual(year_value(''),(None,'missing'))
        self.assertEqual(year_value('2000.5'),(None,'non_integral_or_invalid'))

    def test_frozen_output_refuses_different_payload(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'artifact'
            frozen_write(p,b'original'); frozen_write(p,b'original')
            with self.assertRaises(ValueError): frozen_write(p,b'changed')
            self.assertEqual(p.read_bytes(),b'original')
