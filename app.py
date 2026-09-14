"""
Sentinel-X — Multimodal OSINT Threat Intelligence & Risk Analysis Platform
Analyst Dashboard (Streamlit Frontend)
"""
import streamlit as st
import pandas as pd
import altair as alt
import json

from config.settings import DEFAULT_TEXT_COLUMN, RISK_THRESHOLDS, RISK_WEIGHTS
from utils.file_utils import validate_file_upload, get_file_type_category
from engines.nlp_engine import get_nlp_engine
from engines.threat_engine import analyze_threat_indicators
from engines.entity_engine import get_entity_engine
from engines.risk_engine import calculate_explainable_risk
from engines.graph_engine import display_graph_in_streamlit, build_interactive_graph
from services.csv_service import load_csv_file, detect_text_column, process_csv_dataframe
from services.image_service import process_uploaded_image
from services.video_service import process_uploaded_video
from services.report_service import generate_json_report, generate_pdf_report

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
    .stApp {
        background-color: #0E1117;
    }
    .metric-card {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #334155;
    }
    .high-risk {
        color: #EF4444;
        font-weight: bold;
    }
    .mod-risk {
        color: #F59E0B;
        font-weight: bold;
    }
    .low-risk {
        color: #10B981;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []
if "current_df" not in st.session_state:
    st.session_state.current_df = None
if "current_single_result" not in st.session_state:
    st.session_state.current_single_result = None

# Sidebar Header & Info
st.sidebar.title("🛡️ Sentinel-X")
st.sidebar.markdown("**Multimodal OSINT Platform**")
st.sidebar.markdown("---")

st.sidebar.subheader("System Status")
with st.sidebar.expander("AI & Engine Capabilities", expanded=False):
    nlp_engine = get_nlp_engine()
    st.write(f"**ML Classifier Status:** {'Loaded (TF-IDF + LogReg)' if nlp_engine.is_trained else 'Initializing'}")
    entity_eng = get_entity_engine()
    st.write(f"**NER Model Status:** {'Active (spaCy)' if entity_eng.nlp else 'Fallback Regex'}")
    st.write("**OCR Engines:** EasyOCR + Tesseract Fallback")
    st.write("**Graph Engine:** PyVis Interactive Network")

st.sidebar.markdown("---")
st.sidebar.caption("Sentinel-X v2.0 | Threat Intelligence System")

# Main Header
st.title("🛡️ Sentinel-X — OSINT Threat Intelligence Platform")
st.markdown("Automated Multimodal Threat Detection, spaCy Entity Extraction, Explainable Risk Analysis & Network Graphing.")

# Tabs Navigation
tab_overview, tab_text, tab_csv, tab_media, tab_threats, tab_graph, tab_reports = st.tabs([
    "📊 Overview",
    "📝 Text Analysis",
    "📁 CSV Batch Analysis",
    "🖼️ Image & Video OCR",
    "🚨 Threat Catalog",
    "🕸️ Network Graph",
    "📄 Intelligence Reports"
])

# ==============================================================================
# TAB 1: OVERVIEW DASHBOARD
# ==============================================================================
with tab_overview:
    st.header("Executive Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    history_count = len(st.session_state.analysis_history)
    high_count = sum(1 for item in st.session_state.analysis_history if item.get("risk_category") == "High")
    mod_count = sum(1 for item in st.session_state.analysis_history if item.get("risk_category") == "Moderate")
    low_count = sum(1 for item in st.session_state.analysis_history if item.get("risk_category") == "Low")
    
    col1.metric("Total Analyzed Items", history_count)
    col2.metric("High Risk Detected 🔴", high_count)
    col3.metric("Moderate Risk 🟠", mod_count)
    col4.metric("Low / Clear 🟢", low_count)
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("Configurable Risk Engine Weights")
        st.json(RISK_WEIGHTS)
        st.caption("Weights are configured in `config/settings.py` for transparent tuning.")
        
    with col_right:
        st.subheader("Recent Platform Activity")
        if st.session_state.analysis_history:
            recent_df = pd.DataFrame(st.session_state.analysis_history)[["timestamp", "input_type", "risk_score", "risk_category"]].tail(10)
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No analysis session data recorded yet. Use Text, CSV, or Media tabs to process content.")

# ==============================================================================
# TAB 2: TEXT THREAT ANALYZER
# ==============================================================================
with tab_text:
    st.header("Single Text Threat Analysis")
    st.markdown("Enter raw social media text, forum post, transcript, or suspect communication.")
    
    sample_text = st.selectbox(
        "Load Sample Demonstration Text:",
        [
            "Custom Input",
            "URGENT: Cell meeting tomorrow at 22:00 near embassy. Bringing AK-47 rifles and C4 explosives for the attack on target location.",
            "Recruitment drive for jihad movement in Europe. Join our channel for manifesto and radical propaganda.",
            "Great weather today in New York! Having coffee with friends near Central Park."
        ]
    )
    
    default_val = "" if sample_text == "Custom Input" else sample_text
    user_input_text = st.text_area("Paste Text Payload:", value=default_val, height=120)
    
    if st.button("Run Threat Analysis", type="primary"):
        if not user_input_text.strip():
            st.warning("Please enter text payload to analyze.")
        else:
            with st.spinner("Analyzing threat indicators, spaCy entities & risk score..."):
                res = calculate_explainable_risk(user_input_text)
                res["input_type"] = "Text Payload"
                res["timestamp"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.current_single_result = res
                st.session_state.analysis_history.append(res)
                
            st.success("Analysis Complete!")
            
    if st.session_state.current_single_result:
        res = st.session_state.current_single_result
        score = res["risk_score"]
        cat = res["risk_category"]
        
        st.markdown("---")
        r_col1, r_col2 = st.columns([1, 2])
        
        with r_col1:
            st.metric("Overall Risk Score", f"{score} / 100")
            if cat == "High":
                st.error("🚨 RISK CATEGORY: HIGH")
            elif cat == "Moderate":
                st.warning("⚠️ RISK CATEGORY: MODERATE")
            else:
                st.success("✅ RISK CATEGORY: LOW")
                
            st.subheader("Component Breakdown")
            st.json(res["components"])
            
        with r_col2:
            st.subheader("Explainable Reasoning")
            for r in res["reasons"]:
                st.markdown(f"- {r}")
                
            st.subheader("Extracted spaCy Entities")
            by_type = res["entity_details"].get("by_type", {})
            if any(by_type.values()):
                st.json(by_type)
            else:
                st.info("No high-confidence named entities detected.")

# ==============================================================================
# TAB 3: CSV BATCH ANALYSIS
# ==============================================================================
with tab_csv:
    st.header("CSV Batch Threat Analysis")
    st.markdown("Upload dataset (supports standard CSV & gzipped CSVs like GTD).")
    
    uploaded_csv = st.file_uploader("Upload CSV File", type=["csv", "gz"])
    user_col = st.text_input("Specify Text Column Name (leave blank for auto-detection):", value="")
    
    if uploaded_csv is not None:
        valid, msg = validate_file_upload(uploaded_csv)
        if not valid:
            st.error(msg)
        else:
            df_raw = load_csv_file(uploaded_csv)
            st.success(f"CSV Loaded: {len(df_raw)} rows, {len(df_raw.columns)} columns.")
            
            target_col = detect_text_column(df_raw, user_col if user_col.strip() else None)
            st.info(f"Target text column identified: **'{target_col}'**")
            
            if st.button("Execute Batch CSV Risk Analysis", type="primary"):
                with st.spinner("Processing records through Sentinel-X engines..."):
                    proc_df = process_csv_dataframe(df_raw, target_col)
                    st.session_state.current_df = proc_df
                    st.success("Batch Analysis Completed!")
                    
    if st.session_state.current_df is not None:
        df_proc = st.session_state.current_df
        st.markdown("---")
        
        b_col1, b_col2, b_col3 = st.columns(3)
        b_col1.metric("Total Rows", len(df_proc))
        b_col2.metric("High Risk Posts", len(df_proc[df_proc["risk_category"] == "High"]))
        b_col3.metric("Moderate Risk Posts", len(df_proc[df_proc["risk_category"] == "Moderate"]))
        
        st.subheader("Processed Results Table")
        filter_risk = st.multiselect("Filter by Risk Category:", ["High", "Moderate", "Low"], default=["High", "Moderate", "Low"])
        filtered_df = df_proc[df_proc["risk_category"].isin(filter_risk)]
        st.dataframe(filtered_df.head(100), use_container_width=True)
        
        # Download Processed CSV
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Processed CSV Results", data=csv_bytes, file_name="sentinel_x_analysis_results.csv", mime="text/csv")

# ==============================================================================
# TAB 4: IMAGE & VIDEO OCR
# ==============================================================================
with tab_media:
    st.header("Multimodal OCR Intelligence (Images & Video)")
    media_file = st.file_uploader("Upload Image or Video File", type=["png", "jpg", "jpeg", "mp4", "mov"])
    
    if media_file is not None:
        file_cat = get_file_type_category(media_file.name)
        st.write(f"File: **{media_file.name}** | Type: **{file_cat.upper()}**")
        
        if file_cat == "image":
            st.image(media_file, caption="Uploaded Image", use_column_width=True)
            if st.button("Run Image OCR & Threat Analysis", type="primary"):
                with st.spinner("Executing Image Preprocessing & OCR Reader..."):
                    img_res = process_uploaded_image(media_file)
                    st.session_state.current_single_result = img_res["risk_analysis"]
                    
                if img_res["status"] == "no_text_found":
                    st.warning("No clear text detected in image.")
                else:
                    st.success(f"OCR Complete ({img_res['ocr_engine']} Engine, {img_res['ocr_confidence']}% Confidence)")
                    st.subheader("Extracted OCR Text")
                    st.code(img_res["extracted_text"])
                    st.subheader("Risk Evaluation")
                    st.json(img_res["risk_analysis"])
                    
        elif file_cat == "video":
            st.video(media_file)
            if st.button("Run Video Frame OCR & Timeline Analysis", type="primary"):
                with st.spinner("Sampling video frames & deduplicating subtitle text..."):
                    vid_res = process_uploaded_video(media_file)
                    st.session_state.current_single_result = vid_res["risk_analysis"]
                    
                if vid_res["status"] == "no_text_found":
                    st.warning("No text extracted from sampled video frames.")
                else:
                    st.success(f"Video OCR Complete ({vid_res['frames_analyzed']} frames analyzed)")
                    st.subheader("Deduplicated Timestamp Timeline")
                    for seg in vid_res["timeline_segments"]:
                        st.markdown(f"**[{seg['timestamp']}]** {seg['text']} *(Confidence: {seg['confidence']}%)*")
                    st.subheader("Overall Video Risk Evaluation")
                    st.json(vid_res["risk_analysis"])

# ==============================================================================
# TAB 5: THREAT CATALOG
# ==============================================================================
with tab_threats:
    st.header("Threat & Weapon Lexicons Catalog")
    st.markdown("Inspect pre-configured lexicons, radicalization indicators, and dedicated weapon detection rules.")
    
    from engines.threat_engine import THREAT_KEYWORDS, RADICALIZATION_KEYWORDS, WEAPON_INDICATORS
    
    t1, t2, t3 = st.tabs(["Violent Threat Keywords", "Radicalization Indicators", "Tactical & Weapon Lexicon"])
    with t1:
        st.write(list(THREAT_KEYWORDS))
    with t2:
        st.write(list(RADICALIZATION_KEYWORDS))
    with t3:
        st.write(list(WEAPON_INDICATORS))

# ==============================================================================
# TAB 6: NETWORK GRAPH
# ==============================================================================
with tab_graph:
    st.header("Risk-Aware Entity Relationship Graph")
    st.markdown("Interactive PyVis visualization. Nodes are color-coded by Risk Level (🔴 High, 🟠 Moderate, 🟢 Low).")
    
    if st.session_state.current_df is not None:
        display_graph_in_streamlit(st.session_state.current_df, height=650)
    else:
        st.info("No CSV dataset loaded. Displaying baseline entity network demonstration:")
        display_graph_in_streamlit(pd.DataFrame(), height=650)

# ==============================================================================
# TAB 7: INTELLIGENCE REPORTS
# ==============================================================================
with tab_reports:
    st.header("Automated Intelligence Reports & Exports")
    st.markdown("Export current analysis payload into JSON or PDF intelligence reports.")
    
    if st.session_state.current_single_result:
        res_data = st.session_state.current_single_result
        st.subheader("Report Preview")
        st.json(res_data)
        
        col_json, col_pdf = st.columns(2)
        with col_json:
            json_str = generate_json_report(res_data)
            st.download_button("📥 Download JSON Intelligence Report", data=json_str, file_name="sentinel_x_report.json", mime="application/json")
            
        with col_pdf:
            pdf_bytes = generate_pdf_report(res_data)
            st.download_button("📥 Download PDF Intelligence Report", data=pdf_bytes, file_name="sentinel_x_report.pdf", mime="application/pdf")
    else:
        st.info("Run an analysis in Text, CSV, or Media tab first to generate a report.")
