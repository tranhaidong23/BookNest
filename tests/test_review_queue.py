import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from review_description_queue import disposition

class ReviewQueueTests(unittest.TestCase):
    def test_unknown_nonempty_requires_explicit_review(self):
        with self.assertRaises(ValueError):
            disposition('unreviewed-id','Some text')
        self.assertEqual(disposition('unreviewed-id','')[0],'missing_source')

    def test_placeholder_and_edition_note_cannot_be_accepted_as_synopsis(self):
        self.assertEqual(disposition('4280','For Ingest Only')[0],'reject_placeholder')
        self.assertEqual(disposition('4622','Dramatization note')[0],'needs_more_evidence')
        self.assertEqual(disposition('6846','Shared volume text')[0],'hold_volume_specificity')

if __name__=='__main__':
    unittest.main()
