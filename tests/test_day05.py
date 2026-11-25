import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from day05_baselines import ranking_metrics,top_k,fit_bias,cold_bias,load_split,paired_ci

class Day05Tests(unittest.TestCase):
    def test_hand_computed_ranking(self):
        m=ranking_metrics([2,4,1],{1,2,9},3)
        self.assertAlmostEqual(m['recall'],2/3)
        self.assertAlmostEqual(m['precision'],2/3)
        self.assertAlmostEqual(m['ndcg'],1.5/(1+1/np.log2(3)+.5))
        self.assertIsNone(ranking_metrics([1,2],set()))
        self.assertEqual(ranking_metrics([1],{1})['precision'],.1)
        with self.assertRaises(ValueError): ranking_metrics([1,1],{1})

    def test_exclude_only_supplied_and_ties(self):
        scores={1:2,2:2,3:1,4:0}
        order=sorted(scores,key=lambda b:(-scores[b],b))
        self.assertEqual(top_k(order,{2},2),[1,3])
        self.assertEqual(top_k(order,{1,2,3,4}),[])

    def test_fit_matches_ridge_linear_system(self):
        train=pd.DataFrame([(1,1,5),(1,2,3),(2,1,2),(2,2,1)],columns=['user_id','book_id','rating'])
        m=fit_bias(train,10,iterations=100)
        X=np.array([[1,0,1,0],[1,0,0,1],[0,1,1,0],[0,1,0,1]],dtype=float)
        expected=np.linalg.solve(X.T@X+10*np.eye(4),X.T@(train.rating.to_numpy()-m['mu']))
        np.testing.assert_allclose([m['users'][1],m['users'][2],m['items'][1],m['items'][2]],expected,atol=1e-10)
        self.assertTrue(all(a>=b-1e-9 for a,b in zip(m['objectives'],m['objectives'][1:])))

    def test_cold_support_formula_does_not_mutate_items(self):
        m={'mu':3.,'lambda':10,'items':{1:.5}}
        self.assertAlmostEqual(cold_bias([(1,5),(9,1)],m),-.5/12)
        self.assertEqual(cold_bias([],m),0)
        self.assertEqual(m['items'],{1:.5})

    def test_test_input_rejected_before_io(self):
        for name in ['warm_test.csv','cold_test_target.csv','../ratings.csv']:
            with self.assertRaises(ValueError):load_split(name,{})

    def test_paired_bootstrap_zero_and_constant(self):
        self.assertEqual(paired_ci([1,2],[1,2])['percentile_95'],[0,0])
        self.assertEqual(paired_ci([2,3],[1,2])['percentile_95'],[1,1])
