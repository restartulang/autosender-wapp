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
