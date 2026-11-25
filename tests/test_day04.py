import hashlib
import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from split_day04 import assign, user_groups, check_partition, support_prefix

class Day04Tests(unittest.TestCase):
    def fixture(self):
        return pd.DataFrame([(u,b,(b%5)+1) for u in range(1,21) for b in range(1,24)],
                            columns=['user_id','book_id','rating'])

    def test_independent_protocol_hash_and_floor_boundaries(self):
        src=self.fixture(); f=assign(src)
        order=sorted(range(1,21),key=lambda u:(hashlib.sha256(f'booknest|v0.1|20261120|users|{u}|'.encode()).digest(),u))
        self.assertEqual(set(f.loc[f.group=='development','user_id']),set(order[:16]))
        self.assertEqual(set(f.loc[f.group=='cold_validation','user_id']),set(order[16:18]))
        u=order[0]
        books=sorted(range(1,24),key=lambda b:(hashlib.sha256(f'booknest|v0.1|20261120|warm_pairs|{u}|{b}'.encode()).digest(),b))
        self.assertEqual(set(f.loc[(f.user_id==u)&(f.partition=='warm_validation'),'book_id']),set(books[:2]))
        self.assertEqual(set(f.loc[(f.user_id==u)&(f.partition=='warm_test'),'book_id']),set(books[2:4]))
        check_partition(f,src)

    def test_cold_support_nesting_and_target_disjoint(self):
        f=assign(self.fixture())
        for group in ['cold_validation','cold_test']:
            s=f.loc[f.partition==group+'_support']; t=f.loc[f.partition==group+'_target']
            previous=set()
            for k in (3,5,10):
                part=support_prefix(s,k)
                keys=set(zip(part.user_id,part.book_id))
                self.assertTrue(previous<=keys)
                self.assertFalse(keys & set(zip(t.user_id,t.book_id)))
                self.assertTrue(part.groupby('user_id').size().eq(k).all())
                previous=keys
            self.assertTrue(t.groupby('user_id').size().eq(13).all())

    def test_order_and_label_independent(self):
        src=self.fixture(); f=assign(src)
        changed=src.sample(frac=1,random_state=42).assign(rating=1)
        cols=['user_id','book_id','partition','group','support_rank']
        pd.testing.assert_frame_equal(f[cols],assign(changed)[cols])

    def test_insufficient_cold_is_quarantined_not_train(self):
        src=self.fixture(); groups=user_groups(src.user_id.unique())
        cold=next(u for u,g in groups.items() if g=='cold_test')
        warm=next(u for u,g in groups.items() if g=='development')
        src=src.loc[~src.user_id.isin([cold,warm])|src.book_id.le(9)]
        f=assign(src)
        self.assertEqual(set(f.loc[f.user_id==cold,'partition']),{'cold_test_ineligible'})
        self.assertEqual(set(f.loc[f.user_id==warm,'partition']),{'train'})
        check_partition(f,src)

    def test_duplicate_pairs_fail(self):
        src=self.fixture()
        with self.assertRaises(ValueError): assign(pd.concat([src,src.iloc[:1]]))
