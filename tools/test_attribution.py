"""T5: атрибуція у wide note будується лише з явних вимог джерел."""

import sys

sys.dont_write_bytecode = True  # __pycache__ не потрапляє у vault

import tempfile
import unittest
from pathlib import Path

import catalog_worker

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records"


class AttributionTest(unittest.TestCase):
    def test_only_explicitly_required_sources(self):
        records = catalog_worker.load_records(directory=RECORDS)
        names = [name for name, _ in catalog_worker.attribution_map(records)]
        self.assertEqual(names, ["wikipedia-en", "wikipedia-uk"])

    def test_recommended_but_not_required_is_excluded(self):
        records = catalog_worker.load_records(directory=RECORDS)
        emitted = dict(catalog_worker.attribution_map(records))
        # В arxiv/openalex є attribution_text, але attribution_required: false.
        self.assertNotIn("arxiv", emitted)
        self.assertNotIn("openalex", emitted)

    def test_generated_file_exposes_attribution(self):
        records = catalog_worker.load_records(directory=RECORDS)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sources_generated.py"
            catalog_worker.generate_sources(out, records)
            text = out.read_text(encoding="utf-8")
        self.assertIn("ATTRIBUTION = (", text)
        self.assertIn("wikipedia-en", text)
        self.assertIn("wikipedia-uk", text)
        section = text.split("ATTRIBUTION = (", 1)[1]
        self.assertNotIn('"arxiv"', section)
        self.assertNotIn('"openalex"', section)


if __name__ == "__main__":
    unittest.main()
