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

    def test_jinan_massacre_numeric_alias(self):
        results = query.search("0503")
        self.assertEqual(results[0]["id"], "event-jinan-massacre")

    def test_pingxingguan_victory_date_alias(self):
        results = query.search("0925")
        self.assertEqual(results[0]["id"], "event-pingxingguan-victory")

    def test_hundred_regiments_date_alias(self):
        results = query.search("1940-08-20")
        self.assertEqual(results[0]["id"], "event-hundred-regiments-offensive")

    def test_japan_surrender_date_alias(self):
        results = query.search("1945-08-15")
        self.assertEqual(results[0]["id"], "event-japan-surrender")

    def test_china_theater_surrender_date_alias(self):
        results = query.search("1945-09-09")
        self.assertEqual(results[0]["id"], "event-china-theater-surrender")

    def test_tojo_hideki_pinyin_alias(self):
        results = query.search("dongtiaoyingji")
        self.assertEqual(results[0]["id"], "person-tojo-hideki")

    def test_matsui_iwane_chinese_alias(self):
        results = query.search("松井石根")
        self.assertEqual(results[0]["id"], "person-matsui-iwane")

    def test_doihara_kenji_pinyin_alias(self):
        results = query.search("tufeiyuanxianer")
        self.assertEqual(results[0]["id"], "person-doihara-kenji")

    def test_suzuki_keiku_chinese_alias(self):
        results = query.search("铃木启久")
        self.assertEqual(results[0]["id"], "person-suzuki-keiku")


if __name__ == "__main__":
    unittest.main()
