import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from day06_item_knn import incidence,neighbors,recommend

class ItemKNNTests(unittest.TestCase):
    def test_positive_incidence_not_raw_ratings(self):
        t=pd.DataFrame([(1,10,5),(1,20,1),(2,20,4)],columns=['user_id','book_id','rating'])
        np.testing.assert_array_equal(incidence(t,np.array([10,20])).toarray(),[[1,0],[0,1]])

    def test_similarity_shrink_min_overlap_self_and_tie(self):
        a=csr_matrix(np.array([[1,1,1,0],[1,1,1,0],[1,0,0,1]],float));ids=np.array([10,20,30,40])
        idx,w=neighbors(a,ids,shrinks=(10,),max_k=3,block=2)[10]
        self.assertEqual(idx[0].tolist(),[1,2,-1])
        self.assertAlmostEqual(w[0,0],2/np.sqrt(3*2)*2/12)
        self.assertTrue(all(i not in row for i,row in enumerate(idx)))
        self.assertTrue(np.all(w[idx<0]==0))

    def test_profile_changes_ranking_and_low_rating_still_excluded(self):
        ids=np.array([10,20,30,40]);idx=np.array([[2,3],[3,2],[-1,-1],[-1,-1]])
        w=np.array([[.9,.1],[.8,.2],[0,0],[0,0]])
        pop=np.array([4,3,2,1])
        a=recommend([(10,5),(20,1)],ids,idx,w,2,pop)
        b=recommend([(20,5),(10,1)],ids,idx,w,2,pop)
        self.assertEqual(a[0],[30,40]);self.assertEqual(b[0],[40,30]);self.assertFalse(a[1])

    def test_no_positive_or_no_candidate_evidence_fallback(self):
        ids=np.array([10,20,30]);idx=np.array([[1],[-1],[-1]]);w=np.array([[.5],[0],[0]])
        pop=np.array([1,3,2])
        self.assertEqual(recommend([(10,1)],ids,idx,w,1,pop)[:2],([20,30],True))
        self.assertEqual(recommend([(10,5),(20,1)],ids,idx,w,1,pop)[:2],([30],True))

    def test_sparse_scores_match_explicit_sum_and_no_mutation(self):
        ids=np.arange(1,6);idx=np.array([[2,3],[2,4],[0,1],[0,1],[0,1]])
        weights=np.array([[.7,.3],[.2,.8],[.5,.4],[.2,.1],[.1,.05]])
        original=weights.copy();profile=[(1,5),(2,4)];score=np.zeros(5)
        for b,r in profile:
            for j,w in zip(idx[b-1],weights[b-1]):score[j]+=(r-3)*w
        expected=sorted([3,4,5],key=lambda b:(-score[b-1],b))
        self.assertEqual(recommend(profile,ids,idx,weights,2,np.ones(5))[0],expected)
        np.testing.assert_array_equal(weights,original)
