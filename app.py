# app.py
import streamlit as st
import pandas as pd
import altair as alt
from nlp_engine import calculate_risk, process_dataframe
from data_loader import load_uploaded_dataset
from graph_engine import build_graph  # REVISION: Assume this returns a graph object or HTML for inline display

# REVISION: Cache data loading and analysis for better performance on reruns
@st.cache_data
def cached_load(uploaded_file, text_column):
    return load_uploaded_dataset(uploaded_file, text_column)

@st.cache_data
def cached_analyze(df, text_column):
    df = calculate_risk(df)
    return process_dataframe(df, text_column=text_column)

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

**Disclaimer**: This is a prototype for educational/demo purposes only. 
Do not use for real-world surveillance without legal/ethical review. Respect data privacy laws (e.g., GDPR).
""")  # REVISION: Added ethical disclaimer in UI

# --- Sidebar: File upload & settings ---
st.sidebar.header("Step 1: Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV file containing posts or social media data", type=["csv"])
text_column = st.sidebar.text_input("Text Column Name", value="text")

# REVISION: Use session state for persistent messages
if 'df_loaded' not in st.session_state:
    st.session_state.df_loaded = False

df = None
if uploaded_file:
    try:
        df = cached_load(uploaded_file, text_column)
        st.session_state.df_loaded = True
        st.sidebar.success(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")  # REVISION: Persistent via session
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()
else:
    if st.session_state.df_loaded:
        st.session_state.df_loaded = False  # Reset on new upload
    st.info("Please upload a CSV file to analyze risk scores.")

# --- Step 2: Run Risk Analysis ---
if df is not None:
    st.header("Step 2: Run Threat Analysis")
    if st.button("Run Analysis"):
        with st.spinner("Analyzing data..."):
            try:
                # REVISION: Cached analysis for perf
                df = cached_analyze(df, text_column)

                # --- Metrics ---
                st.subheader("Risk Metrics")
                col1, col2, col3 = st.columns(3)
                total_posts = len(df)
                high_risk_count = len(df[df["risk_category"] == "High"])
                moderate_risk_count = len(df[df["risk_category"] == "Moderate"])
                col1.metric("Total Posts", total_posts)
                col2.metric("High Risk", high_risk_count)
                col3.metric("Moderate Risk", moderate_risk_count)

                # REVISION: Handle zero counts gracefully
                if total_posts == 0:
                    st.warning("No data to analyze.")
                    st.stop()

                # --- Risk Pie Chart ---
                risk_counts = df["risk_category"].value_counts().reset_index()
                risk_counts.columns = ["Risk Category", "Count"]
                pie = alt.Chart(risk_counts).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Risk Category", type="nominal", scale=alt.Scale(scheme="category10")),  # REVISION: Added color scheme for better visuals
                    tooltip=["Risk Category", "Count"]
                ).properties(width=400, height=400)
                st.altair_chart(pie, use_container_width=True)

                # --- Top High Risk Posts (limited for UX) ---
                st.subheader("High Risk Posts")
                high_risk_df = df[df["risk_category"] == "High"].sort_values(by="risk_score", ascending=False)
                if len(high_risk_df) > 50:  # REVISION: Limit display to top 50; add expander for full
                    st.dataframe(high_risk_df.head(50))
                    with st.expander(f"Show all {len(high_risk_df)} high-risk posts"):
                        st.dataframe(high_risk_df)
                else:
                    st.dataframe(high_risk_df)

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
                    # REVISION: Added performance warning for large datasets
                    if len(filtered_df) > 1000:
                        st.warning("Large dataset: Filtering may take a moment.")
                    filtered_df = filtered_df[filtered_df[text_column].str.contains(keyword, case=False, na=False)]
                st.dataframe(filtered_df)  # REVISION: Could add pagination here if needed (e.g., via streamlit-aggrid)

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
                # REVISION: Ensure risk_score is numeric
                df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce")
                hist = alt.Chart(df).mark_bar().encode(
                    x=alt.X("risk_score", bin=alt.Bin(maxbins=20)),
                    y=alt.Y("count()", title="Count"),
                    tooltip=["count()"]
                ).properties(width=700, height=300)
                st.altair_chart(hist, use_container_width=True)

                # --- Low Risk Expander ---
                with st.expander("Low Risk Posts (collapsed by default)"):
                    low_risk_df = df[df["risk_category"] == "Low"]
                    if len(low_risk_df) > 0:
                        st.dataframe(low_risk_df)
                    else:
                        st.info("No low-risk posts found.")

                st.success("✅ Analysis complete!")

                # --- Step 3: Graph / Visualization (moved inside analysis block) ---
                st.header("Step 3: Entity Relationship Graph")
                st.write("Visualize relationships between key entities in the dataset.")
                try:
                    # REVISION: Assume build_graph returns HTML string or object; display inline
                    # If it saves to file, load and embed: graph_html = open('graph.html').read()
                    graph_html = build_graph(df)  # Modify graph_engine to return HTML for Streamlit
                    st.components.v1.html(graph_html, height=600, scrolling=True)  # REVISION: Inline display instead of file
                except Exception as e:
                    st.warning(f"Graph generation failed: {e}. Ensure entities are extracted in NLP engine.")

            except Exception as e:
                st.error(f"Analysis failed: {e}")

else:
    st.info("Upload a file to begin.")

# --- Footer ---
st.markdown("---")
st.markdown("Sentinel-X Prototype | Powered by Streamlit, Transformers & PyVis | Demo Only ⚠️")
