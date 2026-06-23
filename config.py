# config.py

STATION_ID = 'WAPP'
STATION_NAME = 'Stasiun Meteorologi Pattimura Ambon'
TIMEZONE_OFFSET_H = 9

NTP_SERVER = 'ntp.bmkg.go.id'
NTP_FALLBACK = 'pool.ntp.org'
NTP_POLL_INTERVAL = 60
NTP_TIMEOUT = 5
NTP_MAX_OFFSET_SEC = 30

DB_PATH = 'autosender_wapp.db'

CMSS_LOGIN_URL = 'https://bmkgsatu.bmkg.go.id/'
CMSS_GTS_URL = 'https://bmkgsatu.bmkg.go.id/gts_messages'
CMSS_TIMEOUT_MS = 30000
CMSS_MAX_RETRIES = 3

SENDER_MODE = 'playwright'

LOG_DIR = 'logs'
LOG_MAX_BYTES = 5_242_880
LOG_BACKUP_COUNT = 3

KEYRING_SERVICE = 'autosender_wapp_cmss'

SCHEDULER_TICK_SEC = 1
PRE_SEND_LEAD_SEC = 10
