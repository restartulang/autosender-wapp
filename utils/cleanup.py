import subprocess
import logging
import os

logger = logging.getLogger(__name__)

def kill_zombie_chromium():
    """
    Mencari dan mematikan proses chromium.exe yang merupakan zombie process 
    (berjalan secara headless oleh Playwright) untuk mencegah memory leak.
    Fungsi ini dibuat aman agar tidak mematikan browser Chrome utama milik pengguna.
    """
    try:
        if os.name != 'nt':
            return # Saat ini difokuskan pada Windows (menggunakan wmic)
        
        # Dapatkan list proses
        cmd = 'wmic process where "name=\'chrome.exe\' or name=\'chromium.exe\'" get processid,commandline /format:csv'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            return
            
        lines = result.stdout.strip().split('\n')
        killed_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or 'Node' in line: # Skip header csv
                continue
                
            parts = line.split(',')
            if len(parts) >= 3:
                # Format: Node,CommandLine,ProcessId
                command_line = parts[1].lower()
                pid = parts[2].strip()
                
                # Filter ketat: Harus headless DAN diluncurkan oleh ekosistem Playwright kita
                is_headless = '--headless' in command_line
                is_playwright = 'playwright' in command_line or 'autosender_wapp' in command_line or '--disable-dev-shm-usage' in command_line
                
                if is_headless and is_playwright:
                    try:
                        kill_cmd = f'taskkill /F /PID {pid}'
                        subprocess.run(kill_cmd, capture_output=True, shell=True)
                        killed_count += 1
                        logger.debug(f"Killed zombie chromium PID: {pid}")
                    except Exception:
                        pass
        
        if killed_count > 0:
            logger.info(f"Pembersihan Memori: Berhasil menghentikan {killed_count} proses Chromium (Playwright) zombie.")
            
    except Exception as e:
        logger.error(f"Gagal saat mencoba membersihkan zombie chromium: {e}")
