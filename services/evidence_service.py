"""
Cryptographic Evidence Management & SHA-256 Hashing Service for Sentinel-X.
Calculates content hashes, records evidence provenance, and verifies evidence integrity.
"""
import hashlib
import uuid
from datetime import datetime
from models.evidence_models import EvidenceRecord
from storage.repository import save_evidence, log_audit_event
from utils.logging_utils import get_logger

logger = get_logger("evidence_service")

def compute_sha256(content: str | bytes) -> str:
    """Compute SHA-256 hex string of content text or bytes."""
    hasher = hashlib.sha256()
    if isinstance(content, str):
        hasher.update(content.encode('utf-8'))
    elif isinstance(content, bytes):
        hasher.update(content)
    return hasher.hexdigest()

def create_evidence_record(analysis_id: str, content: str | bytes, source_reference: str, media_type: str = "text/plain", metadata: dict = None) -> EvidenceRecord:
    """
    Generate cryptographic SHA-256 evidence record and persist to SQLite repository.
    """
    sha256_hash = compute_sha256(content)
    evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    content_len = len(content)
    
    ev_record = EvidenceRecord(
        evidence_id=evidence_id,
        analysis_id=analysis_id,
        sha256_hash=sha256_hash,
        source_reference=source_reference or "User Payload",
        media_type=media_type,
        content_length=content_len,
        metadata=metadata or {}
    )
    
    save_evidence(ev_record)
    log_audit_event("CREATE_EVIDENCE_RECORD", "System", evidence_id, f"SHA256: {sha256_hash[:16]}... Source: {source_reference[:30]}")
    logger.info(f"Generated SHA-256 evidence record {evidence_id} (Hash: {sha256_hash[:12]}...)")
    return ev_record

def verify_evidence_integrity(content: str | bytes, expected_hash: str) -> bool:
    """Verify content against recorded SHA-256 hash."""
    actual_hash = compute_sha256(content)
    return actual_hash.lower() == expected_hash.lower()
