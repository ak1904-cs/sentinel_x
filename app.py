"""
Sentinel-X — End-to-End Human-in-the-Loop OSINT Threat Intelligence Platform
Analyst Dashboard (Streamlit Frontend)
"""
import streamlit as st
import pandas as pd
import altair as alt
import json

from config.settings import DEFAULT_TEXT_COLUMN, RISK_THRESHOLDS, RISK_WEIGHTS
from utils.file_utils import validate_file_upload, get_file_type_category
from models.analysis_models import AnalysisInput
from models.case_models import CaseStatus, CasePriority
from engines.nlp_engine import get_nlp_engine
from engines.entity_engine import get_entity_engine
from engines.graph_engine import display_graph_in_streamlit
from ingestion.source_manager import SourceManager
from services.analysis_service import analyze_input_payload
from services.csv_service import load_csv_file, detect_text_column, process_csv_dataframe
from services.image_service import process_uploaded_image
from services.video_service import process_uploaded_video
from services.case_service import get_all_cases, get_open_review_queue, escalate_case, dismiss_case, add_case_note
from services.report_service import generate_json_report, generate_pdf_report
from storage.repository import list_audit_logs, list_evidence, list_analyses

# Page Configuration
st.set_page_config(
    page_title="Sentinel-X OSINT Threat Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .metric-card { background-color: #1E293B; border-radius: 8px; padding: 16px; border: 1px solid #334155; }
    .high-risk { color: #EF4444; font-weight: bold; }
    .mod-risk { color: #F59E0B; font-weight: bold; }
    .low-risk { color: #10B981; font-weight: bold; }
    .case-card { background-color: #161B22; padding: 14px; border-radius: 6px; border-left: 4px solid #30363D; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Session State
if "current_single_result" not in st.session_state:
    st.session_state.current_single_result = None
if "current_df" not in st.session_state:
    st.session_state.current_df = None
if "active_case" not in st.session_state:
    st.session_state.active_case = None

# Sidebar Header & User Role Selection
st.sidebar.title("🛡️ Sentinel-X")
st.sidebar.markdown("**Multimodal OSINT Platform**")
st.sidebar.markdown("*Human-in-the-Loop Intelligence*")
st.sidebar.markdown("---")

analyst_name = st.sidebar.text_input("Active Analyst Identity:", value="Analyst-Alpha")
user_role = st.sidebar.selectbox("Analyst Role Access:", ["Analyst", "Senior Reviewer", "Auditor"])

st.sidebar.markdown("---")
st.sidebar.subheader("System Engines")
with st.sidebar.expander("AI Capabilities", expanded=False):
    st.write("**NLP ML Model:** TF-IDF + Logistic Regression")
    st.write("**NER Engine:** spaCy (PERSON, ORG, GPE, LOC)")
    st.write("**OCR Engine:** EasyOCR + Tesseract")
    st.write("**Storage Engine:** SQLite + Cryptographic SHA-256")

st.sidebar.caption("Sentinel-X v2.0 | Human-in-the-Loop Threat Platform")

# Main Page Header
st.title("🛡️ Sentinel-X — OSINT Threat Intelligence Platform")
st.markdown("*Multimodal Data Ingestion, spaCy Entity Extraction, Explainable Risk Engine & Priority Case Review Queue.*")

# 11 Navigation Tabs
tab_overview, tab_ingest, tab_text, tab_csv, tab_media, tab_threats, tab_graph, tab_cases, tab_reports, tab_audit, tab_settings = st.tabs([
    "📊 Overview",
    "🌐 OSINT Web & RSS",
    "📝 Text Analysis",
    "📁 CSV Batch",
    "🖼️ Image & Video OCR",
    "🚨 Threat Catalog",
    "🕸️ Network Graph",
    "🕵️ Analyst Case Queue",
    "📄 Reports & Exports",
    "🔐 Audit & Evidence",
    "⚙️ Settings"
])

# ==============================================================================
# TAB 1: OVERVIEW DASHBOARD
# ==============================================================================
with tab_overview:
    st.header("Platform Executive Overview")
    
    all_cases = get_all_cases()
    total_analyses = len(list_analyses())
    open_cases = [c for c in all_cases if c.status in [CaseStatus.NEW, CaseStatus.UNDER_REVIEW]]
    escalated_cases = [c for c in all_cases if c.status == CaseStatus.ESCALATED]
    dismissed_cases = [c for c in all_cases if c.status == CaseStatus.DISMISSED]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Analyses Processed", total_analyses)
    col2.metric("Open Cases Pending Review 🔴", len(open_cases))
    col3.metric("Escalated Cases 🚨", len(escalated_cases))
    col4.metric("Dismissed Cases 🟢", len(dismissed_cases))
    
    st.markdown("---")
    c_left, c_right = st.columns([1, 1])
    
    with c_left:
        st.subheader("Open Cases Queue Summary")
        if open_cases:
            q_data = [{"Case ID": c.case_id, "Priority": c.priority.value, "Status": c.status.value, "Score": c.risk_score, "Source": c.source_type} for c in open_cases[:10]]
            st.dataframe(pd.DataFrame(q_data), use_container_width=True)
        else:
            st.info("No open cases pending analyst review.")
            
    with c_right:
        st.subheader("Recent System Audit Trail")
        logs = list_audit_logs(limit=8)
        if logs:
            st.dataframe(pd.DataFrame(logs)[["timestamp", "action", "actor", "target_id"]], use_container_width=True)
        else:
            st.info("Audit log is currently empty.")

# ==============================================================================
# TAB 2: OSINT WEB & RSS INGESTION
# ==============================================================================
with tab_ingest:
    st.header("Public Web & RSS Feed Ingestion Layer")
    st.markdown("Ingest publicly accessible web pages or public RSS/Atom feeds.")
    
    ingest_type = st.selectbox("Select Ingestion Source Type:", ["web", "rss", "api"])
    source_url = st.text_input("Enter Public Source URL:", value="https://news.ycombinator.com")
    
    if st.button("Collect & Analyze OSINT Source", type="primary"):
        if not source_url.strip():
            st.warning("Please enter a valid source URL.")
        else:
            with st.spinner("Fetching public content & running multimodal analysis..."):
                payloads = SourceManager.ingest_source(source_url, ingest_type)
                
                results = []
                for payload in payloads:
                    res = analyze_input_payload(payload)
                    results.append(res)
                    
            st.success(f"Ingested & Analyzed {len(results)} payload items!")
            
            for res in results:
                st.markdown(f"**Source URL:** {res.source_type.upper()} | **Risk Score:** {res.risk_score} ({res.risk_category})")
                st.code(res.content_snippet)

# ==============================================================================
# TAB 3: TEXT THREAT ANALYZER
# ==============================================================================
with tab_text:
    st.header("Single Text Threat Analysis")
    user_input_text = st.text_area("Paste Text Payload:", value="", height=120)
    
    if st.button("Run Threat Analysis on Text", type="primary"):
        if not user_input_text.strip():
            st.warning("Please enter text payload.")
        else:
            with st.spinner("Executing Analysis Service & Evidence Hashing..."):
                payload = AnalysisInput(source_type="text", content=user_input_text)
                res = analyze_input_payload(payload)
                st.session_state.current_single_result = res
            st.success("Analysis Complete & Saved to Database!")
            
    if st.session_state.current_single_result:
        res = st.session_state.current_single_result
        st.markdown("---")
        st.subheader(f"Analysis Result (ID: {res.analysis_id})")
        st.metric("Risk Score", f"{res.risk_score} / 100 ({res.risk_category})")
        st.write(f"**Cryptographic SHA-256 Hash:** `{res.evidence_hash}`")
        st.subheader("Explainable Reasons")
        for r in res.reasons:
            st.markdown(f"- {r}")

# ==============================================================================
# TAB 4: CSV BATCH ANALYSIS
# ==============================================================================
with tab_csv:
    st.header("CSV Batch Threat Analysis")
    uploaded_csv = st.file_uploader("Upload CSV or gzipped CSV", type=["csv", "gz"])
    user_col = st.text_input("Text Column Name (blank for auto-detect):", value="")
    
    if uploaded_csv is not None:
        valid, msg = validate_file_upload(uploaded_csv)
        if not valid:
            st.error(msg)
        else:
            df_raw = load_csv_file(uploaded_csv)
            st.success(f"CSV Loaded: {len(df_raw)} rows.")
            target_col = detect_text_column(df_raw, user_col if user_col.strip() else None)
            
            if st.button("Execute Batch CSV Analysis", type="primary"):
                with st.spinner("Processing dataset..."):
                    proc_df = process_csv_dataframe(df_raw, target_col)
                    st.session_state.current_df = proc_df
                st.success("Batch Analysis Completed!")
                
    if st.session_state.current_df is not None:
        st.dataframe(st.session_state.current_df.head(100), use_container_width=True)

# ==============================================================================
# TAB 5: IMAGE & VIDEO OCR
# ==============================================================================
with tab_media:
    st.header("Multimodal OCR Intelligence")
    media_file = st.file_uploader("Upload Image or Video", type=["png", "jpg", "jpeg", "mp4", "mov"])
    
    if media_file is not None:
        file_cat = get_file_type_category(media_file.name)
        if file_cat == "image":
            st.image(media_file, caption="Uploaded Image", use_column_width=True)
            if st.button("Run Image OCR & Threat Analysis", type="primary"):
                with st.spinner("Running EasyOCR + Tesseract..."):
                    res = process_uploaded_image(media_file)
                    st.json(res["risk_analysis"])
        elif file_cat == "video":
            st.video(media_file)
            if st.button("Run Video Frame OCR & Timeline Analysis", type="primary"):
                with st.spinner("Sampling video frames..."):
                    res = process_uploaded_video(media_file)
                    st.json(res["risk_analysis"])

# ==============================================================================
# TAB 6: THREAT CATALOG
# ==============================================================================
with tab_threats:
    st.header("Threat & Weapon Lexicons Catalog")
    from engines.threat_engine import THREAT_KEYWORDS, RADICALIZATION_KEYWORDS, WEAPON_INDICATORS
    st.write("**Violent Threat Keywords:**", list(THREAT_KEYWORDS))
    st.write("**Radicalization Indicators:**", list(RADICALIZATION_KEYWORDS))
    st.write("**Tactical & Weapon Lexicon:**", list(WEAPON_INDICATORS))

# ==============================================================================
# TAB 7: NETWORK GRAPH
# ==============================================================================
with tab_graph:
    st.header("Risk-Aware Entity Relationship Graph")
    if st.session_state.current_df is not None:
        display_graph_in_streamlit(st.session_state.current_df, height=650)
    else:
        display_graph_in_streamlit(pd.DataFrame(), height=650)

# ==============================================================================
# TAB 8: ANALYST CASE QUEUE & HUMAN-IN-THE-LOOP INVESTIGATION
# ==============================================================================
with tab_cases:
    st.header("🕵️ Human-in-the-Loop Analyst Case Queue")
    st.markdown("*Sentinel-X flags potential threat content into cases. Authorized human analysts review evidence and make official decisions.*")
    
    status_filter = st.selectbox("Filter Queue by Status:", ["ALL", "NEW", "UNDER_REVIEW", "ESCALATED", "DISMISSED", "CLOSED"])
    filter_val = None if status_filter == "ALL" else status_filter
    
    cases_list = get_all_cases(filter_val)
    st.subheader(f"Priority Cases ({len(cases_list)} found)")
    
    if not cases_list:
        st.info("No cases match the selected status filter.")
    else:
        c_list_col, c_detail_col = st.columns([1, 2])
        
        with c_list_col:
            st.subheader("Select Case to Investigate")
            for c in cases_list:
                status_icon = "🔴" if c.status == CaseStatus.NEW else ("🟠" if c.status == CaseStatus.UNDER_REVIEW else ("🚨" if c.status == CaseStatus.ESCALATED else "🟢"))
                if st.button(f"{status_icon} [{c.priority.value}] {c.case_id}: {c.title[:30]}...", key=c.case_id):
                    st.session_state.active_case = c
                    
        with c_detail_col:
            if st.session_state.active_case:
                c = st.session_state.active_case
                st.subheader(f"Investigation View: Case {c.case_id}")
                st.markdown(f"**Title:** {c.title}")
                st.markdown(f"**Status:** `{c.status.value}` | **Priority:** `{c.priority.value}` | **Assigned Analyst:** `{c.assigned_analyst}`")
                st.markdown(f"**Risk Score:** `{c.risk_score} / 100` | **SHA-256 Evidence Hash:** `{c.evidence_hash}`")
                
                st.subheader("Source Content Snippet")
                st.code(c.content_snippet)
                
                st.subheader("Flagged Threat Reasons")
                for r in c.reasons:
                    st.markdown(f"- {r}")
                    
                st.subheader("Analyst Notes History")
                if c.notes:
                    for note in c.notes:
                        st.markdown(f"**[{note.timestamp}] {note.analyst}:** {note.note}")
                else:
                    st.caption("No analyst notes recorded yet.")
                    
                st.markdown("---")
                st.subheader("Human Analyst Action & Decision")
                new_note = st.text_input("Add Investigation Note:", key=f"note_{c.case_id}")
                
                col_esc, col_dism, col_note = st.columns(3)
                with col_esc:
                    if st.button("🚨 Escalate Case", type="primary", key=f"esc_{c.case_id}"):
                        escalate_case(c.case_id, analyst_name, new_note)
                        st.success(f"Case {c.case_id} Escalated!")
                        st.rerun()
                        
                with col_dism:
                    if st.button("🟢 Dismiss Case", key=f"dism_{c.case_id}"):
                        dismiss_case(c.case_id, analyst_name, new_note)
                        st.info(f"Case {c.case_id} Dismissed.")
                        st.rerun()
                        
                with col_note:
                    if st.button("📝 Append Note", key=f"app_{c.case_id}"):
                        if new_note.strip():
                            add_case_note(c.case_id, new_note, analyst_name)
                            st.success("Note added.")
                            st.rerun()

# ==============================================================================
# TAB 9: REPORTS & EXPORTS
# ==============================================================================
with tab_reports:
    st.header("Automated Intelligence Reports & Exports")
    if st.session_state.current_single_result:
        res = st.session_state.current_single_result
        if hasattr(res, 'risk_score'):
            res_dict = {
                "analysis_id": res.analysis_id,
                "risk_score": res.risk_score,
                "risk_category": res.risk_category,
                "reasons": res.reasons,
                "threat_details": res.threat_details,
                "entity_details": res.entity_details,
                "evidence_hash": res.evidence_hash
            }
        else:
            res_dict = res
            
        json_str = generate_json_report(res_dict)
        pdf_bytes = generate_pdf_report(res_dict)
        
        st.download_button("📥 Download JSON Intelligence Report", data=json_str, file_name="sentinel_x_report.json", mime="application/json")
        st.download_button("📥 Download PDF Intelligence Report", data=pdf_bytes, file_name="sentinel_x_report.pdf", mime="application/pdf")
    else:
        st.info("Run an analysis in Text, Web, CSV, or Media tab first.")

# ==============================================================================
# TAB 10: AUDIT & EVIDENCE TRAIL
# ==============================================================================
with tab_audit:
    st.header("🔐 Cryptographic Evidence & System Audit Trail")
    
    st.subheader("Recorded Cryptographic SHA-256 Evidence Records")
    evidence_list = list_evidence(limit=25)
    if evidence_list:
        st.dataframe(pd.DataFrame(evidence_list)[["evidence_id", "sha256_hash", "source_reference", "media_type", "collected_at"]], use_container_width=True)
    else:
        st.info("No evidence records created yet.")
        
    st.subheader("System Audit Logs")
    audit_logs = list_audit_logs(limit=50)
    if audit_logs:
        st.dataframe(pd.DataFrame(audit_logs), use_container_width=True)
    else:
        st.info("No audit events recorded yet.")

# ==============================================================================
# TAB 11: PLATFORM SETTINGS
# ==============================================================================
with tab_settings:
    st.header("⚙️ Sentinel-X Platform Configuration")
    st.subheader("Configurable Risk Engine Weights")
    st.json(RISK_WEIGHTS)
    st.subheader("Risk Thresholds")
    st.json(RISK_THRESHOLDS)
