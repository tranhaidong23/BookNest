import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from freeze_day02_catalogue import public_ready

class CatalogueGateTests(unittest.TestCase):
    def fixture(self):
        # Synthetic fixture, not a real permission grant or generated introduction.
        return {'identity_status':'matched_edition_and_work','content_status':'verified_sufficient',
            'intro_status':'reviewed','intro_word_count':75,
            'rights':{'description_display':'verified','adaptation':'verified','evidence_url':'https://example.org/permission'}}

    def test_missing_rights_or_adaptation_evidence_blocks_public_text(self):
        self.assertTrue(public_ready(self.fixture()))
        self.assertFalse(public_ready({}))
        for key,value in [('description_display','unresolved'),('adaptation','unresolved'),('evidence_url',None)]:
            r=self.fixture(); r['rights'][key]=value
            self.assertFalse(public_ready(r))

    def test_identity_content_and_intro_all_required(self):
        for key,value in [('identity_status','candidate'),('content_status','unreviewed_text_candidate'),
                          ('intro_status','not_generated'),('intro_word_count',59),('intro_word_count',101)]:
            r=self.fixture(); r[key]=value
            self.assertFalse(public_ready(r))

if __name__=='__main__':
    unittest.main()
