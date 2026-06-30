import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUERY_PATH = ROOT / "scripts" / "query.py"
SPEC = importlib.util.spec_from_file_location("query", QUERY_PATH)
query = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["query"] = query
SPEC.loader.exec_module(query)


class QueryTests(unittest.TestCase):
    def test_exact_numeric_unit_731(self):
        results = query.search("731")
        self.assertEqual(results[0]["id"], "entity-unit-731")
        self.assertEqual(results[0]["match_type"], "exact")

    def test_zero_prefixed_numeric_unit_731(self):
        results = query.search("0731")
        self.assertEqual(results[0]["id"], "entity-unit-731")
        self.assertGreaterEqual(results[0]["confidence"], 1.0)

    def test_chinese_digit_unit_731(self):
        results = query.search("七三一")
        self.assertEqual(results[0]["id"], "entity-unit-731")

    def test_transposed_numeric_unit_731(self):
        results = query.search("713")
        self.assertEqual(results[0]["id"], "entity-unit-731")
        self.assertIn(results[0]["match_type"], {"listed-near-match", "digit-transposition"})
        self.assertLess(results[0]["confidence"], 1.0)

    def test_chinese_alias_for_iwamatsu_yoshio(self):
        results = query.search("严颂")
        self.assertEqual(results[0]["id"], "person-iwamatsu-yoshio")

    def test_pinyin_alias_for_iwamatsu_yoshio(self):
        results = query.search("yansong")
        self.assertEqual(results[0]["id"], "person-iwamatsu-yoshio")

    def test_nanjing_massacre_date(self):
        results = query.search("1937-12-13")
        self.assertEqual(results[0]["id"], "event-nanjing-massacre")
        self.assertEqual(results[0]["date"], "1937-12-13")

    def test_july_7_incident_date_alias(self):
        results = query.search("0707")
        self.assertEqual(results[0]["id"], "event-july-7-incident")


if __name__ == "__main__":
    unittest.main()
