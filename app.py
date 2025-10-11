# app.py
import streamlit as st
import pandas as pd
from nlp_engine import calculate_risk, process_dataframe

st.set_page_config(page_title="Sentinel-X: Counter-Terrorism OSINT Analysis", layout="wide")

st.title("🛡️ Sentinel-X OSINT Threat Analyzer")
st.write("""
Detect early signs of radicalization or terrorism-related activities
by analyzing uploaded datasets and media content.
""")

# File upload section
st.header("Step 1: Upload Dataset")
uploaded_file = st.file_uploader(
    "Upload CSV file containing posts or social media data",
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading CSV: {e}")

# Run Analysis section
if uploaded_file:
    st.header("Step 2: Run Threat Analysis")
    if st.button("Run Analysis"):
        with st.spinner("Analyzing data..."):
            try:
                # Call your NLP engine to calculate risk
                results = calculate_risk(df)

                # Display summary
                st.subheader("Risk Analysis Summary")
                st.write("High-risk posts/users flagged:")
                high_risk = results[results['risk_score'] >= 0.7]
                st.dataframe(high_risk)

                st.write("Moderate-risk posts/users for review:")
                moderate_risk = results[(results['risk_score'] >= 0.4) & (results['risk_score'] < 0.7)]
                st.dataframe(moderate_risk)

                st.write("Low-risk posts/users (monitor only):")
                low_risk = results[results['risk_score'] < 0.4]
                st.dataframe(low_risk)

                st.success("✅ Analysis complete!")

            except Exception as e:
                st.error(f"Analysis failed: {e}")

# Optional: Geo / graph placeholders
st.header("Step 3: Graph & Geolocation")
st.write("Graphs, network visualization, and geolocation features can be added here for the next iteration.")
    # --- Optional Visualization ---
    st.subheader("Entity Relationship Graph (Top Keywords)")
    from data_loader import load_uploaded_dataset
    df = load_uploaded_dataset(uploaded_file, text_column)


