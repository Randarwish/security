import unittest
import hashlib
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from promptshield.budget import status
from promptshield.run import metrics, parse_label, run


class BenchmarkTests(unittest.TestCase):
    def test_invalid_outputs_count_against_accuracy(self):
        result = metrics([1, 0, 1], [1, 0, None])
        self.assertEqual(result['accuracy_counting_invalid_as_wrong'], 2 / 3)
        self.assertEqual(result['invalid_predictions'], 1)

    def test_strict_output_validation(self):
        for text in ('{"label":true}', '{"label":"1"}', '{"label":2}'):
            with self.assertRaises(ValueError):
                parse_label(text)

    def test_budget_boundaries(self):
        self.assertEqual(status(300, 89.99)['crossed_thresholds_percent'], [])
        self.assertEqual(status(300, 90)['crossed_thresholds_percent'], [30])
        self.assertTrue(status(300, 300)['exhausted'])
        for value in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                status(300, value)

    def test_tampered_dataset_stops_before_running(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"text":"hello", "label":0}\n'
            path = root / 'test.jsonl'
            path.write_bytes(payload + b'\n')
            (root / 'manifest.json').write_text(json.dumps({'files': {'test.jsonl': {
                'sha256': hashlib.sha256(payload).hexdigest()}}}))
            args = SimpleNamespace(limit=1, provider='baseline', data=path)
            with self.assertRaisesRegex(ValueError, 'integrity'):
                run(args)


if __name__ == '__main__':
    unittest.main()
