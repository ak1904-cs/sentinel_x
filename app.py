# app.py
import streamlit as st
import pandas as pd
import altair as alt
from nlp_engine import calculate_risk, process_dataframe
from data_loader import load_uploaded_dataset
from graph_engine import build_graph

# --- Page config ---
st.set_page_config(
    page_title="Sentinel-X OSINT Dashboard",
    layout="wide",
    page_icon="🛡️"
)

st.title("🛡️ Sentinel-X OSINT Threat Analyzer")
st.markdown("""
Detect early signs of radicalization or terrorism-related activities
by analyzing uploaded datasets and media content.
""")

# --- Sidebar: File upload & settings ---
st.sidebar.header("Step 1: Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV file containing posts or social media data", type=["csv"])
text_column = st.sidebar.text_input("Text Column Name", value="text")

if uploaded_file:
    try:
        # Load & clean uploaded dataset
        df = load_uploaded_dataset(uploaded_file, text_column)
        st.sidebar.success(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()
else:
    df = None
    st.info("Please upload a CSV file to analyze risk scores.")

# --- Step 2: Run Risk Analysis ---
if df is not None:
    st.header("Step 2: Run Threat Analysis")
    if st.button("Run Analysis"):
        with st.spinner("Analyzing data..."):
            try:
                # Calculate risk scores & categories
                df = calculate_risk(df)
                df = process_dataframe(df, text_column=text_column)

                # --- Metrics ---
                st.subheader("Risk Metrics")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Posts", len(df))
                col2.metric("High Risk", len(df[df["risk_category"] == "High"]))
                col3.metric("Moderate Risk", len(df[df["risk_category"] == "Moderate"]))

                # --- Risk Pie Chart ---
                risk_counts = df["risk_category"].value_counts().reset_index()
                risk_counts.columns = ["Risk Category", "Count"]
                pie = alt.Chart(risk_counts).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Risk Category", type="nominal"),
                    tooltip=["Risk Category", "Count"]
                ).properties(width=400, height=400)
                st.altair_chart(pie, use_container_width=True)

                # --- Top High Risk Posts ---
                st.subheader("High Risk Posts")
                st.dataframe(df[df["risk_category"] == "High"].sort_values(by="risk_score", ascending=False))

                # --- Search & Filter ---
                st.subheader("Search and Filter Posts")
                keyword = st.text_input("Filter by keyword:")
                risk_filter = st.multiselect(
                    "Filter by Risk Category", 
                    ["High", "Moderate", "Low"], 
                    default=["High", "Moderate", "Low"]
                )
                filtered_df = df[df["risk_category"].isin(risk_filter)]
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

                # --- Risk Score Distribution Histogram ---
                st.subheader("Risk Score Distribution")
                hist = alt.Chart(df).mark_bar().encode(
                    x=alt.X("risk_score", bin=alt.Bin(maxbins=20)),
                    y='count()',
                    tooltip=["count()"]
                ).properties(width=700, height=300)
                st.altair_chart(hist, use_container_width=True)

                # --- Low Risk Expander ---
                with st.expander("Low Risk Posts (collapsed by default)"):
                    st.dataframe(df[df["risk_category"] == "Low"])

                st.success("✅ Analysis complete!")

            except Exception as e:
                st.error(f"Analysis failed: {e}")

    # --- Step 3: Graph / Visualization ---
    st.header("Step 3: Entity Relationship Graph")
    st.write("Visualize relationships between key entities in the dataset.")
    try:
        build_graph(df)  # Make sure build_graph handles the DataFrame correctly
        st.success("Graph generated successfully! Check 'graph.html'.")
    except Exception as e:
        st.warning(f"Graph generation failed: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Sentinel-X Prototype | Powered by Streamlit, Transformers & PyVis | Demo Only ⚠️")
