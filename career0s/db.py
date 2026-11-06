"""SQLite storage layer. One local file, no server, no cost."""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "career0s.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    owner         TEXT,
    source_list   TEXT,
    sector        TEXT,
    markets       TEXT,
    priority      TEXT,
    role_angle    TEXT,
    careers_url   TEXT,
    ats           TEXT,          -- greenhouse | lever | workday | unknown
    ats_slug      TEXT,          -- board token / slug for the ATS API
    rank          INTEGER,
    UNIQUE(name, owner)
);

CREATE TABLE IF NOT EXISTS jobs (
    id            INTEGER PRIMARY KEY,
    company_id    INTEGER REFERENCES companies(id),
    company_name  TEXT,
    source        TEXT,          -- greenhouse | lever | ...
    external_id   TEXT,          -- id from the ATS
    title         TEXT,
    location      TEXT,
    description   TEXT,
    url           TEXT,
    posted_at     TEXT,
    discovered_at TEXT DEFAULT (datetime('now')),
    role_family   TEXT,
    score         INTEGER,
    llm_score     INTEGER,
    llm_reason    TEXT,
    status        TEXT DEFAULT 'new',  -- new|shortlisted|rejected|prepared|applied
    UNIQUE(source, external_id)
);

CREATE TABLE IF NOT EXISTS applications (
    id            INTEGER PRIMARY KEY,
    job_id        INTEGER REFERENCES jobs(id),
    prepared_at   TEXT,
    submitted_at  TEXT,
    cv_used       TEXT,
    cover_letter  TEXT,
    outcome       TEXT,
    notes         TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score);
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
