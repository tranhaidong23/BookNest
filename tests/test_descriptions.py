"""Guard against false identity acceptance and unsafe text extraction."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_source_descriptions import accept_id_link, clean_text
from pilot_descriptions import candidate_isbn

class DescriptionTests(unittest.TestCase):
    def test_both_namespaced_ids_and_unique_record_required(self):
        self.assertTrue(accept_id_link(True, True, 1))
        for values in [(True, False, 1), (False, True, 1), (True, True, 2), (True, True, 0)]:
            self.assertFalse(accept_id_link(*values))

    def test_zero_padding_is_only_hypothesis(self):
        self.assertEqual(candidate_isbn('306406152'), ('0306406152', 'leading_zero_hypothesis'))
        self.assertEqual(candidate_isbn('0306406152'), ('0306406152', 'raw_checksum_valid'))
        self.assertEqual(candidate_isbn('9.78030640615e+12'), ('', 'unavailable'))
        self.assertEqual(candidate_isbn('306406153'), ('', 'unavailable'))

    def test_plain_text_preserves_words_and_discards_executable_content(self):
        self.assertEqual(clean_text('<p>A &amp; B</p><p>C<br>D</p><script>bad()</script><style>bad</style>'), 'A & B C D')
        self.assertEqual(clean_text(''), '')

if __name__ == '__main__':
    unittest.main()
