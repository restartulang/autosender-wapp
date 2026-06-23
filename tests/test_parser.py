import unittest
from datetime import datetime, timezone
from core.parser import parse, _build_target_utc

class TestParser(unittest.TestCase):
    def setUp(self):
        self.now_utc = datetime(2023, 10, 15, 12, 0, tzinfo=timezone.utc)
        
    def test_metar_normal(self):
        res = parse("METAR WAPP 151200Z 12010KT", self.now_utc)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.tipe, "METAR")
        self.assertEqual(res.target_utc.hour, 12)
        
    def test_metar_cor(self):
        res = parse("COR METAR 151200Z", self.now_utc)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.tipe, "METAR")
        
    def test_metar_auto(self):
        res = parse("AUTO METAR WAPP 151200Z", self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_speci(self):
        res = parse("SPECI WAPP 151230Z", self.now_utc)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.tipe, "SPECI")
        
    def test_synop_valid(self):
        res = parse("AAXX 15121 99999", self.now_utc)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.tipe, "SYNOP")
        self.assertEqual(res.target_utc.hour, 12)
        
    def test_synop_gg_99_invalid(self):
        res = parse("AAXX 15991", self.now_utc)
        self.assertFalse(res.is_valid)
        self.assertIn("Waktu invalid", res.error_msg)
        
    def test_synop_gg_23_valid(self):
        res = parse("AAXX 15231", self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_taf_amd(self):
        res = parse("TAF AMD WAPP 151200Z", self.now_utc)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.tipe, "TAFOR")
        
    def test_taf_normal(self):
        res = parse("TAF WAPP 151200Z", self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_no_keyword(self):
        res = parse("HELLO WORLD 151200Z", self.now_utc)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.tipe, "UNKNOWN")
        
    def test_metar_hh_99(self):
        res = parse("METAR 159900Z", self.now_utc)
        self.assertFalse(res.is_valid)
        
    def test_metar_mm_60(self):
        res = parse("METAR 151260Z", self.now_utc)
        self.assertFalse(res.is_valid)
        
    def test_multiline(self):
        text = "SOME NOISE\nMETAR WAPP 151200Z\nMORE NOISE"
        res = parse(text, self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_leading_whitespace(self):
        res = parse("   METAR WAPP 151200Z", self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_taf_cor(self):
        res = parse("TAF COR WAPP 151200Z", self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_rollover_bulan(self):
        now = datetime(2023, 10, 30, tzinfo=timezone.utc)
        target = _build_target_utc(2, 12, 0, now)
        self.assertEqual(target.month, 11)
        
    def test_rollover_tahun(self):
        now = datetime(2023, 12, 31, tzinfo=timezone.utc)
        target = _build_target_utc(2, 12, 0, now)
        self.assertEqual(target.month, 1)
        self.assertEqual(target.year, 2024)
        
    def test_synop_multiline(self):
        res = parse("\n\nAAXX 15121\n123", self.now_utc)
        self.assertTrue(res.is_valid)
        
    def test_invalid_day(self):
        res = parse("METAR 321200Z", self.now_utc)
        self.assertFalse(res.is_valid)
        self.assertIn("Tanggal invalid", res.error_msg)
        
    def test_invalid_month_day(self):
        now = datetime(2023, 2, 28, tzinfo=timezone.utc)
        res = parse("METAR 291200Z", now) # Feb 2023 is not leap year
        self.assertFalse(res.is_valid)

if __name__ == '__main__':
    unittest.main()
