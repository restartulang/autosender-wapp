import logging
import os
from logging.handlers import TimedRotatingFileHandler
from config import LOG_DIR

def setup_logging():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    log_file = os.path.join(LOG_DIR, 'autosender.log')
    
    # Root logger setup
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(threadName)-15s | %(name)s | %(message)s')
    
    # File handler: Rotasi harian (tiap tengah malam), simpan log 30 hari terakhir
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger
