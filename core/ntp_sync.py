from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import threading
import ntplib
import config
import logging

logger = logging.getLogger(__name__)

class NTPStatus(Enum):
    SYNCED = 'synced'
    HOLD = 'hold'
    INIT = 'init'

@dataclass
class NTPState:
    status: NTPStatus = NTPStatus.INIT
    offset_seconds: float = 0.0
    last_sync_utc: datetime | None = None
    last_error: str = ''

class NTPManager:
    def __init__(self):
        self._state = NTPState()
        self._lock = threading.RLock()
        self._callbacks = []
        self._stop_evt = threading.Event()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name='NTPThread')
        self._ntp_client = ntplib.NTPClient()
    
    def start(self):
        if not self._thread.is_alive():
            self._thread.start()
            
    def stop(self):
        self._stop_evt.set()
        
    def get_accurate_utc(self) -> datetime:
        with self._lock:
            offset = self._state.offset_seconds
        return datetime.now(timezone.utc) + timedelta(seconds=offset)
        
    def is_safe_to_send(self) -> bool:
        with self._lock:
            return self._state.status == NTPStatus.SYNCED
            
    @property
    def state(self) -> NTPState:
        with self._lock:
            return NTPState(
                status=self._state.status,
                offset_seconds=self._state.offset_seconds,
                last_sync_utc=self._state.last_sync_utc,
                last_error=self._state.last_error
            )
            
    def register_callback(self, fn):
        with self._lock:
            self._callbacks.append(fn)
            
    def _poll_loop(self):
        self._do_sync()
        while not self._stop_evt.wait(config.NTP_POLL_INTERVAL):
            self._do_sync()
            
    def _do_sync(self):
        servers = [config.NTP_SERVER, config.NTP_FALLBACK]
        success = False
        
        for server in servers:
            try:
                response = self._ntp_client.request(server, version=3, timeout=config.NTP_TIMEOUT)
                with self._lock:
                    self._state.status = NTPStatus.SYNCED
                    self._state.offset_seconds = response.offset
                    self._state.last_sync_utc = datetime.now(timezone.utc)
                    self._state.last_error = ''
                success = True
                break
            except Exception as e:
                logger.warning(f"NTP sync failed for {server}: {e}")
                with self._lock:
                    self._state.last_error = f"{server} failed: {e}"
                    
        if not success:
            with self._lock:
                if self._state.status != NTPStatus.INIT:
                    self._state.status = NTPStatus.HOLD
                    
        self._notify_callbacks()
        
    def _notify_callbacks(self):
        with self._lock:
            callbacks = list(self._callbacks)
            current_state = self.state
            
        for cb in callbacks:
            try:
                cb(current_state)
            except Exception as e:
                logger.error(f"Callback error: {e}")
