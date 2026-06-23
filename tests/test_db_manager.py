import unittest
from datetime import datetime, timezone
import database.db_manager as db
from core.parser import ParseResult
import sqlite3
import tempfile
import os

class TestDBManager(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        db.init_db(self.db_path)
        self.now = datetime(2023, 10, 15, 12, 0, tzinfo=timezone.utc)
        self.target = datetime(2023, 10, 15, 13, 0, tzinfo=timezone.utc)
        
    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except OSError:
            pass
        
    def test_insert_sandi(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        id1 = db.insert_sandi(pr, self.now, self.db_path)
        self.assertIsNotNone(id1)
        
    def test_insert_duplicate_antri(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        db.insert_sandi(pr, self.now, self.db_path)
        with self.assertRaises(db.DuplicateSandiError):
            db.insert_sandi(pr, self.now, self.db_path)
            
    def test_can_schedule_duplicate(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        db.insert_sandi(pr, self.now, self.db_path)
        can, msg = db.can_schedule('METAR', self.target, self.db_path)
        self.assertFalse(can)
        self.assertIn("Duplikat", msg)
        
    def test_can_schedule_ok(self):
        can, msg = db.can_schedule('METAR', self.target, self.db_path)
        self.assertTrue(can)
        
    def test_get_antri(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        db.insert_sandi(pr, self.now, self.db_path)
        antri = db.get_antri(self.db_path)
        self.assertEqual(len(antri), 1)
        self.assertEqual(antri[0]['tipe_sandi'], 'METAR')
        
    def test_get_riwayat(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        id1 = db.insert_sandi(pr, self.now, self.db_path)
        # Update status to Berhasil so it appears in riwayat
        db.update_status(id1, 'Berhasil', db_path=self.db_path)
        riwayat = db.get_riwayat(limit=10, db_path=self.db_path)
        self.assertEqual(len(riwayat), 1)
        
    def test_update_status(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        id1 = db.insert_sandi(pr, self.now, self.db_path)
        db.update_status(id1, 'Berhasil', db_path=self.db_path, retry_count=1)
        
        riwayat = db.get_riwayat(limit=1, db_path=self.db_path)
        self.assertEqual(riwayat[0]['status'], 'Berhasil')
        self.assertEqual(riwayat[0]['retry_count'], 1)
        
    def test_duplicate_after_success(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        id1 = db.insert_sandi(pr, self.now, self.db_path)
        db.update_status(id1, 'Berhasil', db_path=self.db_path)
        
        # Should allow insert again for same target if previous is not 'Antri'
        id2 = db.insert_sandi(pr, self.now, self.db_path)
        self.assertNotEqual(id1, id2)
        
    def test_dashboard_counts(self):
        counts = db.get_dashboard_counts(self.db_path)
        self.assertIn('antri', counts)
        self.assertIn('berhasil_hari_ini', counts)
        self.assertIn('gagal_batal_hari_ini', counts)
        
    def test_update_status_gagal(self):
        pr = ParseResult('METAR', self.target, 'RAW TEXT')
        id1 = db.insert_sandi(pr, self.now, self.db_path)
        db.update_status(id1, 'Gagal', db_path=self.db_path, error_message='Timeout')
        riwayat = db.get_riwayat(limit=1, db_path=self.db_path)
        self.assertEqual(riwayat[0]['status'], 'Gagal')
        self.assertEqual(riwayat[0]['error_message'], 'Timeout')
        
    def test_get_antri_order(self):
        pr1 = ParseResult('METAR', datetime(2023, 10, 15, 14, 0, tzinfo=timezone.utc), 'R1')
        pr2 = ParseResult('METAR', datetime(2023, 10, 15, 13, 0, tzinfo=timezone.utc), 'R2')
        db.insert_sandi(pr1, self.now, self.db_path)
        db.insert_sandi(pr2, self.now, self.db_path)
        
        antri = db.get_antri(self.db_path)
        self.assertEqual(antri[0]['target_utc'], '2023-10-15T13:00:00Z') # Should be ascending
        
    def test_invalid_tipe(self):
        pr = ParseResult('INVALID', self.target, 'RAW TEXT')
        with self.assertRaises(sqlite3.IntegrityError):
            db.insert_sandi(pr, self.now, self.db_path)

if __name__ == '__main__':
    unittest.main()
