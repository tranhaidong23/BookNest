import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from day10_evaluate import load_input,verify_lock,SELECTION
from audit_extended import sha
from day05_baselines import load_split

class FinalEvaluationTests(unittest.TestCase):
    def test_allowlists_are_separate(self):
        for name in ('cold_validation_target.csv','../train.csv','ratings.csv'):
            with self.assertRaises(ValueError):load_input(name,{})
        for name in ('warm_test.csv','cold_test_target.csv','cold_test_support.csv'):
            with self.assertRaises(ValueError):load_split(name,{})

    def test_lock_detects_model_or_selection_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'model';p.write_bytes(b'original')
            lock={'selection':SELECTION.copy(),'hashes':{'model':sha(p)}}
            verify_lock(lock,root)
            p.write_bytes(b'changed')
            with self.assertRaises(ValueError):verify_lock(lock,root)
            lock['hashes']['model']=sha(p);lock['selection']['primary']='mf'
            with self.assertRaises(ValueError):verify_lock(lock,root)

if __name__=='__main__':unittest.main()
