import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from day08_mf import ridge, update_rows, fit, fold_in, score_all
import numpy as np
from scipy.sparse import csr_matrix


class MatrixFactorizationTests(unittest.TestCase):
    def test_ridge_against_augmented_lstsq(self):
        x=np.array([[1.,2.],[3.,-1.],[0.,4.]])
        y=np.array([2.,-1.,3.]);lam=10.
        expected=np.linalg.lstsq(np.vstack([x,np.sqrt(lam)*np.eye(2)]),np.r_[y,[0.,0.]],rcond=None)[0]
        np.testing.assert_allclose(ridge(x,y,lam),expected)
        with self.assertRaises(ValueError):ridge(x,y,0)

    def test_observed_zero_is_not_missing(self):
        m=csr_matrix(([0.,2.],([0,0],[0,1])),shape=(1,2))
        self.assertEqual(m.nnz,2)
        np.testing.assert_allclose(update_rows(m,np.ones((2,1)),1),[[2/3]])
        missing=csr_matrix(([2.],([0],[1])),shape=(1,2))
        np.testing.assert_allclose(update_rows(missing,np.ones((2,1)),1),[[1.]])

    def test_als_decreases_objective_and_final_item_equation(self):
        m=csr_matrix(np.array([[1.,0.,-1.],[2.,1.,0.],[0.,-2.,3.]]))
        p,q,trace=fit(m,2,1,epochs=3)
        self.assertTrue(np.all(np.diff(trace)<=1e-10))
        for i in range(m.shape[1]):
            users=m[:,i].nonzero()[0]
            x=p[users];y=m[users,i].toarray().ravel()
            expected=np.linalg.lstsq(np.vstack([x,np.eye(2)]),np.r_[y,[0.,0.]],rcond=None)[0]
            np.testing.assert_allclose(q[i],expected,atol=1e-12)

    def test_fold_in_is_read_only_and_empty_profile(self):
        q=np.array([[1.,2.],[3.,4.]]);before=q.copy();bi=np.array([.2,-.1])
        p,ub=fold_in([0,1],[5,2],q,bi,3.,10)
        expected_bias=(5-3-.2+2-3+.1)/52
        self.assertAlmostEqual(ub,expected_bias)
        expected=np.linalg.lstsq(np.vstack([q,np.sqrt(10)*np.eye(2)]),np.r_[np.array([5,2])-3-bi-ub,[0.,0.]],rcond=None)[0]
        np.testing.assert_allclose(p,expected);np.testing.assert_array_equal(q,before)
        p,ub=fold_in([],[],q,bi,3.,10)
        np.testing.assert_array_equal(p,[0.,0.]);self.assertEqual(ub,0)

    def test_ranking_unclipped_and_excludes_low_rated_seen(self):
        ids=np.arange(1,14);q=np.zeros((13,1));bi=np.array([5.,2.2,2.1]+[0.]*10)
        top,scores=score_all([(1,1)],ids,q,bi,3.,10)
        self.assertNotIn(1,top);self.assertEqual(top[:3],[2,3,4]);self.assertGreater(scores[1],5)
        top,_=score_all([],ids,q,np.zeros(13),3.,10)
        self.assertEqual(top,list(range(1,11)))
        with self.assertRaises(ValueError):score_all([(99,3)],ids,q,bi,3.,10)

if __name__=='__main__':unittest.main()
