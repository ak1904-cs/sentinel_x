# app.py
import streamlit as st
import pandas as pd
from PIL import Image
import cv2
import tempfile
import os
import streamlit as st
import pandas as pd
from nlp_engine import calculate_risk  # placeholder for Step 6
from nlp_engine import calculate_risk

st.title("Sentinel-X OSINT Threat Analyzer")

uploaded_file = st.file_uploader("Upload a CSV with posts", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())

    if st.button("Run Analysis"):
        # Process each post
        results = []
        for idx, row in df.iterrows():
            text = row['text'] if 'text' in row else str(row)
            res = calculate_risk(text)
            results.append(res)

        # Merge results into dataframe
        results_df = pd.DataFrame(results)
        df = pd.concat([df.reset_index(drop=True), results_df], axis=1)

        st.write("Analysis Results:", df)
        st.success("Analysis complete!")


st.set_page_config(page_title="Sentinel-X OSINT Analysis", layout="wide")
st.title("Sentinel-X: Counter-Terrorism OSINT Analysis & Threat Actor Profiling")

st.sidebar.header("Upload Data / Media")
st.sidebar.markdown("""
Upload CSV files, images, or videos for analysis. 
Supported:
- CSV: Terrorism/Hate Speech datasets
- Images: JPG, PNG
- Videos: MP4
""")

# -----------------------------
# 1. CSV Upload
# -----------------------------
csv_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if csv_file:
    try:
        df = pd.read_csv(csv_file)
        st.subheader("Uploaded CSV Preview")
        st.dataframe(df.head())
        st.success(f"CSV '{csv_file.name}' uploaded successfully!")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")

# -----------------------------
# 2. Image Upload
# -----------------------------
image_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if image_file:
    try:
        image = Image.open(image_file)
        st.subheader("Uploaded Image Preview")
        st.image(image, caption=image_file.name, use_column_width=True)
        st.success("Image uploaded successfully!")
    except Exception as e:
        st.error(f"Failed to open image: {e}")

# -----------------------------
# 3. Video Upload
# -----------------------------
video_file = st.sidebar.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
if video_file:
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        st.subheader("Uploaded Video Preview")
        st.video(tfile.name)
        st.success("Video uploaded successfully!")
    except Exception as e:
        st.error(f"Failed to load video: {e}")

# -----------------------------
# 4. Run Analysis Button
# -----------------------------
if st.button("Run Threat Analysis"):
    st.info("Analysis started...")
    
    # CSV Analysis placeholder
    if csv_file:
        st.write("Processing CSV...")
        # Example: call your NLP function here
        if 'df' in locals():
            df['risk_score'] = df.apply(lambda row: calculate_risk(row['text']) if 'text' in row else 0, axis=1)
            st.subheader("CSV Risk Scores Preview")
            st.dataframe(df.head())
    
    # Image Analysis placeholder
    if image_file:
        st.write("Processing Image...")
        st.info("Image risk analysis placeholder (Step 6)")
    
    # Video Analysis placeholder
    if video_file:
        st.write("Processing Video...")
        st.info("Video risk analysis placeholder (Step 6)")
    
    st.success("Analysis complete (placeholders only for now)")

st.sidebar.markdown("---")
st.sidebar.write("Sentinel-X Prototype v1.0")
