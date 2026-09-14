"""
Central Multimodal Analysis Service Orchestrator for Sentinel-X.
Orchestrates Ingestion -> Preprocessing -> NLP/NER/Threat -> Risk Engine -> Cryptographic Evidence Hashing -> SQLite Storage -> Auto-Case Generation.
"""
import uuid
from datetime import datetime

from models.analysis_models import AnalysisInput, AnalysisResult
from models.case_models import CaseRecord, CasePriority, CaseStatus
from engines.risk_engine import calculate_explainable_risk
from services.evidence_service import create_evidence_record
from storage.repository import save_analysis, save_case, log_audit_event
from utils.logging_utils import get_logger

logger = get_logger("analysis_service")

def analyze_input_payload(input_payload: AnalysisInput) -> AnalysisResult:
    """
    Run complete Sentinel-X analysis pipeline on an AnalysisInput object.
    Saves analysis to DB, generates cryptographic SHA-256 evidence record,
    and auto-flags High/Moderate risk content as prioritize cases for human review.
    """
    text_content = input_payload.content or ""
    analysis_id = f"AN-{uuid.uuid4().hex[:8].upper()}"
    
    # 1. Run Explainable Risk & Threat Engines
    risk_res = calculate_explainable_risk(text_content)
    
    # 2. Generate Cryptographic SHA-256 Evidence Record
    ref = input_payload.url_or_reference or "User Payload"
    ev_record = create_evidence_record(
        analysis_id=analysis_id,
        content=text_content,
        source_reference=ref,
        media_type=input_payload.media_type,
        metadata=input_payload.metadata
    )
    
    content_snippet = text_content[:200].replace('\n', ' ') + ("..." if len(text_content) > 200 else "")
    
    # 3. Create Structured AnalysisResult
    result = AnalysisResult(
        analysis_id=analysis_id,
        source_type=input_payload.source_type,
        risk_score=risk_res["risk_score"],
        risk_category=risk_res["risk_category"],
        components=risk_res["components"],
        reasons=risk_res["reasons"],
        threat_details=risk_res["threat_details"],
        entity_details=risk_res["entity_details"],
        evidence_hash=ev_record.sha256_hash,
        content_snippet=content_snippet,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 4. Save to Database Repository
    save_analysis(result)
    log_audit_event("ANALYZE_PAYLOAD", "System", analysis_id, f"Risk Score: {result.risk_score} Category: {result.risk_category}")
    
    # 5. Human-in-the-Loop Auto-Case Generation for High & Moderate Risk Items
    if result.risk_category in ["High", "Moderate"]:
        priority = CasePriority.HIGH if result.risk_category == "High" else CasePriority.MODERATE
        case_id = f"SX-{uuid.uuid4().hex[:6].upper()}"
        title = f"[{result.risk_category.upper()} RISK] Threat Flagged from {input_payload.source_type.upper()}"
        
        case_record = CaseRecord(
            case_id=case_id,
            analysis_id=analysis_id,
            title=title,
            source_type=input_payload.source_type,
            risk_score=result.risk_score,
            priority=priority,
            status=CaseStatus.NEW,
            assigned_analyst="Unassigned",
            reasons=result.reasons,
            evidence_hash=ev_record.sha256_hash,
            content_snippet=content_snippet
        )
        save_case(case_record)
        log_audit_event("AUTO_CREATE_CASE", "System", case_id, f"Flagged High/Moderate item for Analyst Review. Analysis ID: {analysis_id}")
        logger.info(f"Auto-generated Priority Case {case_id} for human analyst review.")
        
    return result
