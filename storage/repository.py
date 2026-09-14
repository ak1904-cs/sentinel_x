"""
Repository Data Access Layer for Sentinel-X SQLite Database.
"""
import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

from storage.database import get_db_connection
from models.analysis_models import AnalysisResult
from models.case_models import CaseRecord, CaseStatus, CasePriority, CaseNote
from models.evidence_models import EvidenceRecord
from utils.logging_utils import get_logger

logger = get_logger("repository")

# --- ANALYSES CRUD ---
def save_analysis(res: AnalysisResult):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO analyses 
    (analysis_id, source_type, risk_score, risk_category, components_json, reasons_json, threat_details_json, entity_details_json, evidence_hash, content_snippet, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        res.analysis_id,
        res.source_type,
        res.risk_score,
        res.risk_category,
        json.dumps(res.components),
        json.dumps(res.reasons),
        json.dumps(res.threat_details),
        json.dumps(res.entity_details),
        res.evidence_hash,
        res.content_snippet,
        res.timestamp
    ))
    conn.commit()
    conn.close()

def list_analyses(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "analysis_id": r["analysis_id"],
            "source_type": r["source_type"],
            "risk_score": r["risk_score"],
            "risk_category": r["risk_category"],
            "components": json.loads(r["components_json"]),
            "reasons": json.loads(r["reasons_json"]),
            "threat_details": json.loads(r["threat_details_json"]),
            "entity_details": json.loads(r["entity_details_json"]),
            "evidence_hash": r["evidence_hash"],
            "content_snippet": r["content_snippet"],
            "timestamp": r["timestamp"]
        })
    return results

# --- CASES CRUD ---
def save_case(case: CaseRecord):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO cases 
    (case_id, analysis_id, title, source_type, risk_score, priority, status, assigned_analyst, reasons_json, evidence_hash, content_snippet, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case.case_id,
        case.analysis_id,
        case.title,
        case.source_type,
        case.risk_score,
        case.priority.value if isinstance(case.priority, CasePriority) else case.priority,
        case.status.value if isinstance(case.status, CaseStatus) else case.status,
        case.assigned_analyst,
        json.dumps(case.reasons),
        case.evidence_hash,
        case.content_snippet,
        case.created_at,
        case.updated_at
    ))
    conn.commit()
    conn.close()

def update_case_status(case_id: str, new_status: CaseStatus, analyst: str = "Analyst") -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_str = new_status.value if isinstance(new_status, CaseStatus) else new_status
    
    cursor.execute("""
    UPDATE cases SET status = ?, assigned_analyst = ?, updated_at = ? WHERE case_id = ?
    """, (status_str, analyst, now_str, case_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if updated:
        log_audit_event("UPDATE_CASE_STATUS", analyst, case_id, f"Changed status to {status_str}")
    return updated

def add_case_note(case_id: str, note_text: str, analyst: str = "Analyst"):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO case_notes (case_id, timestamp, analyst, note) VALUES (?, ?, ?, ?)
    """, (case_id, now_str, analyst, note_text))
    
    cursor.execute("UPDATE cases SET updated_at = ? WHERE case_id = ?", (now_str, case_id))
    conn.commit()
    conn.close()
    log_audit_event("ADD_CASE_NOTE", analyst, case_id, f"Added note: {note_text[:50]}...")

def get_case_notes(case_id: str) -> List[CaseNote]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM case_notes WHERE case_id = ? ORDER BY note_id ASC", (case_id,))
    rows = cursor.fetchall()
    conn.close()
    return [CaseNote(timestamp=r["timestamp"], analyst=r["analyst"], note=r["note"]) for r in rows]

def list_cases(status_filter: Optional[str] = None) -> List[CaseRecord]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("SELECT * FROM cases WHERE status = ? ORDER BY risk_score DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM cases ORDER BY risk_score DESC")
    rows = cursor.fetchall()
    conn.close()

    cases = []
    for r in rows:
        notes = get_case_notes(r["case_id"])
        cases.append(CaseRecord(
            case_id=r["case_id"],
            analysis_id=r["analysis_id"],
            title=r["title"],
            source_type=r["source_type"],
            risk_score=r["risk_score"],
            priority=CasePriority(r["priority"]),
            status=CaseStatus(r["status"]),
            assigned_analyst=r["assigned_analyst"],
            reasons=json.loads(r["reasons_json"]),
            evidence_hash=r["evidence_hash"],
            content_snippet=r["content_snippet"],
            notes=notes,
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        ))
    return cases

# --- EVIDENCE CRUD ---
def save_evidence(ev: EvidenceRecord):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO evidence
    (evidence_id, analysis_id, sha256_hash, source_reference, media_type, content_length, metadata_json, collected_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ev.evidence_id,
        ev.analysis_id,
        ev.sha256_hash,
        ev.source_reference,
        ev.media_type,
        ev.content_length,
        json.dumps(ev.metadata),
        ev.collected_at
    ))
    conn.commit()
    conn.close()

def list_evidence(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence ORDER BY collected_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- AUDIT LOGS CRUD ---
def log_audit_event(action: str, actor: str, target_id: str, details: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO audit_logs (timestamp, action, actor, target_id, details) VALUES (?, ?, ?, ?, ?)
    """, (now_str, action, actor, target_id, details))
    conn.commit()
    conn.close()

def list_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
