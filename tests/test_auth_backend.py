import sys
import unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from booknest.auth_backend import AccountConfig,local_connection_factory,account_from_streamlit
from booknest.identity import IdentityError

class AuthBackendTests(unittest.TestCase):
    def test_connection_requires_explicit_loopback_and_never_connects_during_validation(self):
        for dsn in ['host=cloud.invalid user=test dbname=test','host=127.0.0.1 hostaddr=8.8.8.8 user=test dbname=test','service=other user=test dbname=test','user=test dbname=test']:
            with self.assertRaises(IdentityError):local_connection_factory(dsn)
        factory=local_connection_factory('host=localhost user=test dbname=test password=synthetic')
        self.assertEqual(factory.keywords['hostaddr'],'127.0.0.1')
    def test_config_repr_does_not_contain_secrets(self):
        c=AccountConfig('https://example.invalid','client','runtime-secret','broker-secret')
        self.assertNotIn('runtime-secret',repr(c));self.assertNotIn('broker-secret',repr(c))
    def test_invalid_claims_never_reach_identity_database(self):
        config=AccountConfig('https://example.invalid','client','invalid','invalid')
        with patch('booknest.auth_backend.resolve_identity',side_effect=AssertionError('Unexpected DB access')) as resolve:
            with self.assertRaises(IdentityError):account_from_streamlit({'is_logged_in':False},config)
            resolve.assert_not_called()

if __name__=='__main__':unittest.main()
