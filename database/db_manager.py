import sqlite3
import logging
from contextlib import contextmanager
import os
import config
from datetime import datetime, timezone, timedelta
import time
from functools import wraps

logger = logging.getLogger(__name__)

class DuplicateSandiError(Exception):
    pass
    
class DBLockedError(Exception):
    pass

def retry_on_locked(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 3
        delay = 0.5
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except DBLockedError as e:
                if attempt < retries - 1:
                    logger.warning(f"Database locked, retrying in {delay}s (Attempt {attempt+1}/{retries})")
                    time.sleep(delay)
                else:
                    logger.error(f"Database locked after {retries} retries, skipping operation.")
                    return None
    return wrapper

@contextmanager
def get_connection(db_path=None):
    conn = None
    try:
        path = db_path or config.DB_PATH
        conn = sqlite3.connect(path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode = WAL;')
        conn.execute('PRAGMA foreign_keys = ON;')
        yield conn
    except sqlite3.OperationalError as e:
        if 'database is locked' in str(e).lower():
            raise DBLockedError("Database is locked")
        raise
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_db(db_path=None):
    try:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_script = f.read()
        else:
            schema_script = """
            PRAGMA journal_mode = WAL;
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS sandi_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waktu_input_utc TEXT NOT NULL,
                tipe_sandi TEXT NOT NULL CHECK (tipe_sandi IN ('METAR', 'SPECI', 'SYNOP', 'TAFOR', 'WXREV')),
                stasiun TEXT DEFAULT 'UNKNOWN',
                isi_sandi TEXT NOT NULL,
                target_utc TEXT NOT NULL,
                status TEXT DEFAULT 'Antri' CHECK (status IN ('Antri', 'Berhasil', 'Gagal', 'Dibatalkan')),
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                waktu_kirim_utc TEXT,
                durasi_kirim_ms INTEGER
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_antri ON sandi_logs(tipe_sandi, target_utc, stasiun) WHERE status='Antri';
            CREATE INDEX IF NOT EXISTS idx_status ON sandi_logs(status);
            CREATE INDEX IF NOT EXISTS idx_target_utc ON sandi_logs(target_utc);
            """
            
        with get_connection(db_path) as conn:
            try:
                conn.execute("ALTER TABLE sandi_logs ADD COLUMN stasiun TEXT DEFAULT 'UNKNOWN'")
                logger.info("Migration: Added 'stasiun' column to sandi_logs.")
            except sqlite3.OperationalError:
                pass
                
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sandi_logs'")
            row = cursor.fetchone()
            if row and 'WXREV' not in row[0]:
                logger.info("Migrating CHECK constraint to support WXREV...")
                conn.execute("PRAGMA foreign_keys=off;")
                conn.execute("ALTER TABLE sandi_logs RENAME TO sandi_logs_old;")
                conn.executescript(schema_script)
                cursor.execute("PRAGMA table_info(sandi_logs_old)")
                cols = [col[1] for col in cursor.fetchall()]
                col_str = ", ".join(cols)
                conn.execute(f"INSERT INTO sandi_logs ({col_str}) SELECT {col_str} FROM sandi_logs_old;")
                conn.execute("DROP TABLE sandi_logs_old;")
                conn.execute("PRAGMA foreign_keys=on;")
            else:
                conn.executescript(schema_script)
                
            conn.execute("CREATE INDEX IF NOT EXISTS idx_target_utc ON sandi_logs(target_utc);")
            conn.commit()
            logger.info("Database initialized successfully.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Kritis: Database error saat inisialisasi: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

@retry_on_locked
def can_schedule(tipe: str, target_utc: datetime, stasiun: str = '', db_path=None) -> tuple[bool, str]:
    target_str = target_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM sandi_logs WHERE tipe_sandi=? AND target_utc=? AND stasiun=? AND status='Antri'", (tipe, target_str, stasiun))
        row = cursor.fetchone()
        if row:
            return (False, f"Duplikat: ID #{row['id']}")
        return (True, '')

@retry_on_locked
def insert_sandi(parse_result, now_utc: datetime, db_path=None) -> int:
    target_str = parse_result.target_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    input_str = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with get_connection(db_path) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sandi_logs (waktu_input_utc, tipe_sandi, stasiun, isi_sandi, target_utc, status) VALUES (?, ?, ?, ?, ?, 'Antri')",
                (input_str, parse_result.tipe, parse_result.stasiun, parse_result.raw, target_str)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'UNIQUE' in str(e).upper() or 'idx_unique_antri' in str(e):
                raise DuplicateSandiError(f"Sandi {parse_result.tipe} untuk target {target_str} sudah ada dalam antrean.")
            raise e

@retry_on_locked
def get_antri(db_path=None) -> list[dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sandi_logs WHERE status='Antri' ORDER BY target_utc ASC")
        return [dict(row) for row in cursor.fetchall()]

@retry_on_locked
def get_riwayat(limit: int = 50, offset: int = 0, db_path=None) -> list[dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sandi_logs WHERE status != 'Antri' ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

@retry_on_locked
def get_riwayat_by_date(date_str: str, limit: int = 50, offset: int = 0, db_path=None) -> list[dict]:
    """Filter riwayat by local date string (YYYY-MM-DD) based on target_utc."""
    local_dt = datetime.strptime(date_str, '%Y-%m-%d').astimezone()
    start_utc = local_dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_utc = (local_dt + timedelta(days=1)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sandi_logs WHERE target_utc >= ? AND target_utc < ? AND status != 'Antri' ORDER BY id DESC LIMIT ? OFFSET ?",
            (start_utc, end_utc, limit, offset)
        )
        return [dict(row) for row in cursor.fetchall()]

@retry_on_locked
def get_riwayat_count(date_str: str = None, db_path=None) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if date_str:
            local_dt = datetime.strptime(date_str, '%Y-%m-%d').astimezone()
            start_utc = local_dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            end_utc = (local_dt + timedelta(days=1)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE target_utc >= ? AND target_utc < ? AND status != 'Antri'", (start_utc, end_utc))
        else:
            cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE status != 'Antri'")
        return cursor.fetchone()[0]

@retry_on_locked
def update_status(id: int, status: str, db_path=None, **kwargs):
    fields = ["status=?"]
    values = [status]
    for k, v in kwargs.items():
        if k in ['error_message', 'waktu_kirim_utc', 'durasi_kirim_ms', 'retry_count']:
            fields.append(f"{k}=?")
            values.append(v)
    values.append(id)
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE sandi_logs SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()

@retry_on_locked
def get_dashboard_counts(date_str=None, db_path=None) -> dict:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE status='Antri'")
        antri = cursor.fetchone()[0]
        
        if date_str == 'ALL':
            cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE status='Berhasil'")
            berhasil = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE status IN ('Gagal', 'Dibatalkan')")
            gagal_batal = cursor.fetchone()[0]
        else:
            target_date = date_str if date_str else datetime.now().strftime('%Y-%m-%d')
            local_dt = datetime.strptime(target_date, '%Y-%m-%d').astimezone()
            start_utc = local_dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            end_utc = (local_dt + timedelta(days=1)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE status='Berhasil' AND target_utc >= ? AND target_utc < ?", (start_utc, end_utc))
            berhasil = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM sandi_logs WHERE status IN ('Gagal', 'Dibatalkan') AND target_utc >= ? AND target_utc < ?", (start_utc, end_utc))
            gagal_batal = cursor.fetchone()[0]
            
        return {'antri': antri, 'berhasil': berhasil, 'gagal_batal': gagal_batal}
