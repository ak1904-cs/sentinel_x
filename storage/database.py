"""
SQLite Database Schema and Connection Initializer for Sentinel-X.
"""
import sqlite3
import os
from config.settings import BASE_DIR
from utils.logging_utils import get_logger

logger = get_logger("database")

DB_DIR = os.path.join(BASE_DIR, "storage")
DB_FILE = os.path.join(DB_DIR, "sentinel_x.db")

def get_db_connection() -> sqlite3.Connection:
    """Return a thread-safe connection to Sentinel-X SQLite DB."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database tables for analyses, cases, evidence, and audit logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Analyses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        analysis_id TEXT PRIMARY KEY,
        source_type TEXT NOT NULL,
        risk_score REAL NOT NULL,
        risk_category TEXT NOT NULL,
        components_json TEXT NOT NULL,
        reasons_json TEXT NOT NULL,
        threat_details_json TEXT NOT NULL,
        entity_details_json TEXT NOT NULL,
        evidence_hash TEXT NOT NULL,
        content_snippet TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    # 2. Cases Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        analysis_id TEXT NOT NULL,
        title TEXT NOT NULL,
        source_type TEXT NOT NULL,
        risk_score REAL NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_analyst TEXT NOT NULL,
        reasons_json TEXT NOT NULL,
        evidence_hash TEXT NOT NULL,
        content_snippet TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(analysis_id) REFERENCES analyses(analysis_id)
    )
    """)

    # 3. Case Notes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_notes (
        note_id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        analyst TEXT NOT NULL,
        note TEXT NOT NULL,
        FOREIGN KEY(case_id) REFERENCES cases(case_id)
    )
    """)

    # 4. Evidence Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id TEXT PRIMARY KEY,
        analysis_id TEXT NOT NULL,
        sha256_hash TEXT NOT NULL,
        source_reference TEXT NOT NULL,
        media_type TEXT NOT NULL,
        content_length INTEGER NOT NULL,
        metadata_json TEXT NOT NULL,
        collected_at TEXT NOT NULL,
        FOREIGN KEY(analysis_id) REFERENCES analyses(analysis_id)
    )
    """)

    # 5. Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        target_id TEXT NOT NULL,
        details TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    logger.info("SQLite database schema initialized successfully.")

# Run initialization on import
init_db()
