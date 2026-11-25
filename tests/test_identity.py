import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from booknest.identity import from_streamlit_user,IdentityError

class IdentityPolicyTests(unittest.TestCase):
    def setUp(self):
        self.claims={'is_logged_in':True,'iss':'https://identity.example.invalid','sub':'stable-123','aud':'booknest','iat':1000,'exp':5000,'name':' Alice ','email':'same@example.invalid'}
    def parse(self,**changes):
        return from_streamlit_user({**self.claims,**changes},expected_issuer=self.claims['iss'],client_id='booknest',now=2000)
    def test_identity_uses_issuer_subject_not_email(self):
        self.assertEqual(self.parse(),self.parse(email='different@example.invalid'))
        self.assertNotEqual(self.parse(),self.parse(sub='another-user'))
        self.assertEqual(self.parse().display_name,'Alice')
    def test_rejects_unauthenticated_wrong_issuer_audience_and_missing_subject(self):
        for changes in [{'is_logged_in':False},{'is_logged_in':'true'},{'iss':'https://evil.invalid'},{'aud':'other'},{'sub':''}]:
            with self.assertRaises(IdentityError):self.parse(**changes)
    def test_session_times_must_be_finite_valid_and_unexpired(self):
        for changes in [{'exp':2000},{'exp':float('nan')},{'iat':float('inf')},{'iat':True},{'iat':2100},{'iat':-30000},{'nbf':2100}]:
            with self.assertRaises(IdentityError):self.parse(**changes)
    def test_multi_audience_requires_matching_authorized_party(self):
        with self.assertRaises(IdentityError):self.parse(aud=['booknest','other'])
        self.assertEqual(self.parse(),self.parse(aud=['booknest','other'],azp='booknest'))
        with self.assertRaises(IdentityError):self.parse(azp='other')
    def test_untrusted_config_and_missing_timestamps_fail_closed(self):
        with self.assertRaises(IdentityError):from_streamlit_user(self.claims,expected_issuer='http://identity.example.invalid',client_id='booknest',now=2000)
        with self.assertRaises(IdentityError):self.parse(exp=None)

if __name__=='__main__':unittest.main()
