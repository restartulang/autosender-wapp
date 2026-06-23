import threading
import queue
import asyncio
import time
from datetime import datetime
import config
from database import db_manager as db
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, ntp_manager, sender, gui_queue):
        self.ntp_manager = ntp_manager
        self.sender = sender
        self.gui_queue = gui_queue
        
        self.send_queue = queue.Queue()
        self._stop_evt = threading.Event()
        self._processing_ids = set()
        
        self._sched_thread = threading.Thread(target=self._sched_loop, daemon=True, name="SchedulerThread")
        self._sender_thread = threading.Thread(target=self._sender_loop_wrap, daemon=True, name="SenderThread")
        
    def start(self):
        if not self._sched_thread.is_alive():
            self._sched_thread.start()
        if not self._sender_thread.is_alive():
            self._sender_thread.start()
            
    def stop(self):
        self._stop_evt.set()
        
    def _sched_loop(self):
        self._expected_tick_time = time.time()
        while not self._stop_evt.wait(config.SCHEDULER_TICK_SEC):
            actual_time = time.time()
            if actual_time - self._expected_tick_time > 120:
                logger.warning("Sistem kemungkinan baru bangun dari sleep (gap > 120s). Force NTP resync.")
                self.ntp_manager._do_sync()
            self._expected_tick_time = actual_time + config.SCHEDULER_TICK_SEC
            
            try:
                antri = db.get_antri()
                if not antri:
                    continue
                    
                now_utc = self.ntp_manager.get_accurate_utc().replace(tzinfo=None)
                is_safe = self.ntp_manager.is_safe_to_send()
                
                for item in antri:
                    item_id = item['id']
                    if item_id in self._processing_ids:
                        continue
                        
                    target_utc = datetime.strptime(item['target_utc'], '%Y-%m-%dT%H:%M:%SZ')
                    diff = (target_utc - now_utc).total_seconds()
                    
                    if diff <= config.PRE_SEND_LEAD_SEC:
                        if is_safe:
                            self._processing_ids.add(item_id)
                            self.send_queue.put(item)
                        elif diff <= 0:
                            logger.warning(f"ID #{item_id} target passed but NTP is HOLD. Delaying send.")
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                
    def _sender_loop_wrap(self):
        asyncio.run(self._sender_loop())
        
    async def _sender_loop(self):
        while not self._stop_evt.is_set():
            try:
                item = self.send_queue.get_nowait()
                res = await self.sender.send(item['isi_sandi'], log_id=item['id'])
                
                status = 'Berhasil' if res.success else 'Gagal'
                waktu_kirim = self.ntp_manager.get_accurate_utc().strftime('%Y-%m-%dT%H:%M:%SZ')
                
                db.update_status(
                    item['id'], 
                    status, 
                    error_message=res.error_message, 
                    waktu_kirim_utc=waktu_kirim, 
                    durasi_kirim_ms=res.duration_ms
                )
                self._processing_ids.discard(item['id'])
                self.send_queue.task_done()
                
                if hasattr(self, 'on_send_complete') and self.on_send_complete:
                    self.gui_queue.put(self.on_send_complete)
            except queue.Empty:
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Sender async error: {e}")
                await asyncio.sleep(1)
