import sys
import tkinter.messagebox as messagebox
import sqlite3
import os
import pathlib

browsers_dir = pathlib.Path(__file__).parent / 'browsers'
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browsers_dir)

from utils.logger import setup_logging
from database.db_manager import init_db
from gui.app_window import AutosenderApp
import logging

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    sys.excepthook = lambda t, v, tb: logging.critical(f'UNHANDLED: {t.__name__}: {v}', exc_info=(t,v,tb))
    
    logger.info("Application starting...")
    
    from utils.cleanup import kill_zombie_chromium
    kill_zombie_chromium()
    
    try:
        init_db()
    except sqlite3.DatabaseError as e:
        import config
        # Use a hidden root to show messagebox before mainloop
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Kritis", f"Database corrupt atau tidak bisa dibuka: {config.DB_PATH}\n\nDetail: {e}")
        sys.exit(1)
    
    app = AutosenderApp()
    app.mainloop()

if __name__ == "__main__":
    main()
