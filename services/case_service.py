"""
Human-in-the-Loop Case Management Service for Sentinel-X.
Enables authorized analysts to investigate cases, review evidence, add investigation notes,
and transition case statuses (NEW -> UNDER_REVIEW -> DISMISSED / ESCALATED / CLOSED).
"""
from typing import List, Optional
from models.case_models import CaseRecord, CaseStatus, CasePriority, CaseNote
from storage.repository import list_cases, update_case_status, add_case_note, log_audit_event, get_db_connection
from utils.logging_utils import get_logger

logger = get_logger("case_service")

def get_all_cases(status_filter: Optional[str] = None) -> List[CaseRecord]:
    """Retrieve cases list filtered by status or all."""
    return list_cases(status_filter)

def get_open_review_queue() -> List[CaseRecord]:
    """Retrieve cases requiring analyst review (NEW, UNDER_REVIEW)."""
    all_cases = list_cases()
    return [c for c in all_cases if c.status in [CaseStatus.NEW, CaseStatus.UNDER_REVIEW]]

def review_case(case_id: str, analyst_name: str = "Analyst"):
    """Mark case status as UNDER_REVIEW when opened by analyst."""
    update_case_status(case_id, CaseStatus.UNDER_REVIEW, analyst_name)

def escalate_case(case_id: str, analyst_name: str, notes: str = ""):
    """Escalate case for official escalation workflow."""
    if notes.strip():
        add_case_note(case_id, f"[ESCALATED] {notes}", analyst_name)
    update_case_status(case_id, CaseStatus.ESCALATED, analyst_name)
    log_audit_event("ESCALATE_CASE", analyst_name, case_id, f"Case escalated by analyst. Notes: {notes[:60]}")
    logger.info(f"Case {case_id} escalated by analyst '{analyst_name}'.")

def dismiss_case(case_id: str, analyst_name: str, notes: str = ""):
    """Dismiss case with analyst justification."""
    if notes.strip():
        add_case_note(case_id, f"[DISMISSED] {notes}", analyst_name)
    update_case_status(case_id, CaseStatus.DISMISSED, analyst_name)
    log_audit_event("DISMISS_CASE", analyst_name, case_id, f"Case dismissed by analyst. Justification: {notes[:60]}")
    logger.info(f"Case {case_id} dismissed by analyst '{analyst_name}'.")

def close_case(case_id: str, analyst_name: str, notes: str = ""):
    """Close completed case."""
    if notes.strip():
        add_case_note(case_id, f"[CLOSED] {notes}", analyst_name)
    update_case_status(case_id, CaseStatus.CLOSED, analyst_name)
