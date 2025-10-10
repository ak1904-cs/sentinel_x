# app.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from transformers import pipeline
from nlp_engine import calculate_risk, process_dataframe

st.set_page_config(page_title="Sentinel-X OSINT Dashboard", layout="wide", page_icon="🛡️")

# --- Sidebar ---
st.sidebar.title("Sentinel-X Controls")
st.sidebar.markdown("Upload dataset and analyze risk scores for posts.")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
text_column = st.sidebar.text_input("Text Column Name", value="text")

# --- Data handling ---
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        df = process_dataframe(df, text_column=text_column)
    except Exception as e:
        st.error(f"Error loading or processing dataset: {e}")
        st.stop()
else:
    st.info("Please upload a CSV to analyze risk scores.")
    df = None

# --- Main Layout ---
st.title("Sentinel-X OSINT Threat Analysis Dashboard 🛡️")
st.markdown("""
Sentinel-X is an **OSINT prototype** for early detection of extremist content.
It calculates risk scores for posts and categorizes them as **High**, **Moderate**, or **Low** risk.
""")

if df is not None:
    # --- Metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Posts", len(df))
    col2.metric("High Risk", len(df[df["risk_category"] == "High"]))
    col3.metric("Moderate Risk", len(df[df["risk_category"] == "Moderate"]))

    # --- Risk Category Pie Chart ---
    risk_counts = df["risk_category"].value_counts().reset_index()
    risk_counts.columns = ["Risk Category", "Count"]

    pie = alt.Chart(risk_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Risk Category", type="nominal"),
        tooltip=["Risk Category", "Count"]
    ).properties(width=400, height=400)
    st.altair_chart(pie, use_container_width=True)

    # --- Display top High Risk posts ---
    st.subheader("High Risk Posts")
    st.dataframe(df[df["risk_category"] == "High"].sort_values(by="risk_score", ascending=False))

    # --- Search / Filter ---
    st.subheader("Search and Filter Posts")
    keyword = st.text_input("Filter by keyword:")
    risk_filter = st.multiselect("Filter by Risk Category", ["High", "Moderate", "Low"], default=["High", "Moderate", "Low"])

    filtered_df = df[
        df["risk_category"].isin(risk_filter)
    ]
    if keyword:
        filtered_df = filtered_df[filtered_df[text_column].str.contains(keyword, case=False, na=False)]

    st.dataframe(filtered_df)

    # --- Download Processed CSV ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Processed CSV",
        data=csv,
        file_name="sentinel_x_processed.csv",
        mime="text/csv"
    )

    # --- Optional: Risk Score Histogram ---
    st.subheader("Risk Score Distribution")
    hist = alt.Chart(df).mark_bar().encode(
        x=alt.X("risk_score", bin=alt.Bin(maxbins=20)),
        y='count()',
        tooltip=["count()"]
    ).properties(width=700, height=300)
    st.altair_chart(hist, use_container_width=True)

    # --- Optional: Advanced UI / Expander for Low Risk posts ---
    with st.expander("Low Risk Posts (collapsed by default)"):
        st.dataframe(df[df["risk_category"] == "Low"])

# --- Footer ---
st.markdown("---")
st.markdown("Sentinel-X Prototype | Powered by Streamlit & Transformers | Demo Only ⚠️")

