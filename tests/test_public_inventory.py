import tempfile
import unittest
from pathlib import Path
from scripts.review_public_files import inventory

class PublicInventoryTests(unittest.TestCase):
    def test_exclusions_and_redacted_secret_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ['data','artifacts','.venv','node_modules','.vscode']:
                (root/name).mkdir();(root/name/'private.txt').write_text('not for inventory')
            (root/'.env').write_text('not for inventory')
            (root/'secrets.toml').write_text('not for inventory')
            token='ghp_'+'a'*36
            (root/'oops.py').write_text('TOKEN='+token)
            result=inventory(root)
            self.assertEqual([r['path'] for r in result['files']],['oops.py'])
            self.assertEqual(result['findings'],[{'path':'oops.py','category':'github_token'}])
            self.assertNotIn(token,str(result));self.assertFalse(result['ready_to_publish'])

    def test_notebook_outputs_require_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'demo.ipynb').write_text('{"cells":[{"outputs":[{"text":"synthetic"}]}]}')
            result=inventory(root)
            self.assertEqual(result['findings'][0]['category'],'notebook_outputs_manual_review')
