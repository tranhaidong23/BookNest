import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_wikipedia_gap import checked_payload, extract_span


class WikipediaEvidenceTests(unittest.TestCase):
    def test_tampered_cached_body_rejected(self):
        body = '{"query": {}}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cache.json'
            payload = {'body': body, 'body_sha256': hashlib.sha256(body.encode()).hexdigest()}
            path.write_text(json.dumps(payload), encoding='utf-8')
            self.assertEqual(checked_payload(path), {'query': {}})
            payload['body'] = '{"query": {"changed": true}}'
            path.write_text(json.dumps(payload), encoding='utf-8')
            with self.assertRaises(ValueError):
                checked_payload(path)

    def test_span_excludes_unreviewed_neighbors(self):
        self.assertEqual(extract_span('QUOTE\nSTART premise\nEND review', 'START', '\nEND'), 'START premise')
        with self.assertRaises(ValueError):
            extract_span('START one START two END', 'START', 'END')
        with self.assertRaises(ValueError):
            extract_span('START missing boundary', 'START', 'END')

    def test_api_error_not_counted_as_missing_book(self):
        body = json.dumps({'error': {'code': 'maxlag'}})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cache.json'
            path.write_text(json.dumps({'body': body, 'body_sha256': hashlib.sha256(body.encode()).hexdigest()}), encoding='utf-8')
            with self.assertRaises(ValueError):
                checked_payload(path)
