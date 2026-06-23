import unittest
from unittest.mock import patch, MagicMock
from core.ntp_sync import NTPManager, NTPStatus
from datetime import datetime, timezone
import config

class TestNTPManager(unittest.TestCase):
    def setUp(self):
        self.ntp_mgr = NTPManager()
        
    @patch('ntplib.NTPClient.request')
    def test_sync_success(self, mock_request):
        mock_res = MagicMock()
        mock_res.offset = 1.5
        mock_request.return_value = mock_res
        
        self.ntp_mgr._do_sync()
        state = self.ntp_mgr.state
        self.assertEqual(state.status, NTPStatus.SYNCED)
        self.assertEqual(state.offset_seconds, 1.5)
        self.assertTrue(self.ntp_mgr.is_safe_to_send())
        
    @patch('ntplib.NTPClient.request')
    def test_sync_failure_to_hold(self, mock_request):
        # First sync success
        mock_res = MagicMock()
        mock_res.offset = 1.5
        mock_request.return_value = mock_res
        self.ntp_mgr._do_sync()
        
        # Next sync fails
        mock_request.side_effect = Exception("Mock timeout")
        self.ntp_mgr._do_sync()
        
        state = self.ntp_mgr.state
        self.assertEqual(state.status, NTPStatus.HOLD)
        self.assertFalse(self.ntp_mgr.is_safe_to_send())
        
    @patch('ntplib.NTPClient.request')
    def test_initial_failure_stays_init(self, mock_request):
        mock_request.side_effect = Exception("Mock timeout")
        self.ntp_mgr._do_sync()
        
        state = self.ntp_mgr.state
        self.assertEqual(state.status, NTPStatus.INIT)
        
    def test_get_accurate_utc(self):
        self.ntp_mgr._state.offset_seconds = 3600.0 # 1 hour offset
        now = datetime.now(timezone.utc)
        acc = self.ntp_mgr.get_accurate_utc()
        
        diff = (acc - now).total_seconds()
        self.assertTrue(3599 < diff < 3601)

if __name__ == '__main__':
    unittest.main()
