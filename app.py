# app.py (edited multi-modal version)
import streamlit as st
import pandas as pd
import altair as alt
import io
import tempfile
import os
from nlp_engine import calculate_risk, process_dataframe
from data_loader import load_uploaded_dataset

st.set_page_config(page_title="Sentinel-X OSINT Dashboard", layout="wide", page_icon="🛡️")

# ----------------------------
# Optional heavy imports (graceful fallback)
# ----------------------------
EASYOCR_AVAILABLE = False
CV2_AVAILABLE = False
PYTESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    pass

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    pass

try:
    import pytesseract
    from PIL import Image as PILImage
    PYTESSERACT_AVAILABLE = True
except Exception:
    pass

# ----------------------------
# Helper functions
# ----------------------------
def try_read_csv(uploaded_file):
    """Try multiple encodings to read CSV safely."""
    encodings = ["utf-8", "iso-8859-1", "cp1252"]
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding=enc)
        except Exception:
            continue
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file, engine="python", on_bad_lines="skip")

def ocr_image_bytes_with_easyocr(image_bytes):
    """Run EasyOCR on bytes and return extracted text."""
    if not EASYOCR_AVAILABLE:
        return ""
    reader = easyocr.Reader(['en'], gpu=False)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tf.write(image_bytes)
        tmp_path = tf.name
    try:
        res = reader.readtext(tmp_path, detail=0)
        text = " ".join(res)
    except Exception:
        text = ""
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return text

def ocr_image_pytesseract(image_bytes):
    """OCR fallback using pytesseract if available."""
    if not PYTESSERACT_AVAILABLE:
        return ""
    try:
        im = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
        text = pytesseract.image_to_string(im)
        return text
    except Exception:
        return ""

def extract_text_from_image(uploaded_image):
    """Extract text from image (EasyOCR first, then pytesseract)."""
    uploaded_image.seek(0)
    bytes_data = uploaded_image.read()
    text = ""
    if EASYOCR_AVAILABLE:
        text = ocr_image_bytes_with_easyocr(bytes_data)
    if not text and PYTESSERACT_AVAILABLE:
        text = ocr_image_pytesseract(bytes_data)
    return text

def extract_text_from_video(uploaded_video, frame_interval=30, max_frames=60):
    """Extract text from video frames."""
    if not CV2_AVAILABLE:
        return "", "cv2_not_installed"

    uploaded_video.seek(0)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(uploaded_video.read())
        temp_path = tf.name

    cap = cv2.VideoCapture(temp_path)
    texts = []
    frame_count = 0
    extracted_frames = 0
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % frame_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                success, encoded_image = cv2.imencode('.png', gray)
                if not success:
                    continue
                image_bytes = encoded_image.tobytes()
                chunk_text = ""
                if EASYOCR_AVAILABLE:
                    chunk_text = ocr_image_bytes_with_easyocr(image_bytes)
                elif PYTESSERACT_AVAILABLE:
                    chunk_text = ocr_image_pytesseract(image_bytes)
                if chunk_text:
                    texts.append(chunk_text)
                    extracted_frames += 1
                if extracted_frames >= max_frames:
                    break
            frame_count += 1
    except Exception:
        pass
    finally:
        cap.release()
        try:
            os.remove(temp_path)
        except Exception:
            pass
    return " ".join(texts), "ok"

# ----------------------------
# UI - Header & Sidebar
# ----------------------------
st.title("🛡️ Sentinel-X OSINT Threat Analyzer")
st.markdown("""
Detect early signs of radicalization or terrorism-related activities by analyzing CSVs, images, or video content.

**Disclaimer:** For demo/educational use only.
""")

st.sidebar.header("Upload (CSV / Image / Video)")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV, image, or video",
    type=["csv", "png", "jpg", "jpeg", "mp4", "mov"]
)
text_column = st.sidebar.text_input("Text Column Name (for CSV)", value="text")

with st.sidebar.expander("Optional tools status (OCR / Video)"):
    st.write(f"EasyOCR installed: {'Yes' if EASYOCR_AVAILABLE else 'No'}")
    st.write(f"OpenCV installed: {'Yes' if CV2_AVAILABLE else 'No'}")
    st.write(f"Pytesseract installed: {'Yes' if PYTESSERACT_AVAILABLE else 'No'}")
    st.markdown("Install EasyOCR, OpenCV, and pytesseract in `requirements.txt` for full functionality.")

# ----------------------------
# Main logic
# ----------------------------
if uploaded_file is None:
    st.info("Upload a CSV, image, or video to start analysis.")
else:
    file_type = uploaded_file.type or uploaded_file.name.split('.')[-1].lower()
    st.write(f"Uploaded file: **{uploaded_file.name}** — detected type: **{file_type}**")

    # ---------- CSV ----------
    if "csv" in file_type or uploaded_file.name.lower().endswith(".csv"):
        try:
            uploaded_file.seek(0)
            df = try_read_csv(uploaded_file)
            st.success(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            # Validate text column
            if text_column not in df.columns:
                alt_cols = ["clean_text", "text", "tweet", "summary", "body"]
                found = next((c for c in alt_cols if c in df.columns), None)
                if found:
                    st.warning(f"Column '{text_column}' not found. Using '{found}' instead.")
                    text_column = found
                else:
                    st.error(f"Column '{text_column}' not found. Adjust sidebar input.")
                    st.stop()

            # Clean text
            if "clean_text" not in df.columns:
                df["clean_text"] = df[text_column].astype(str).str.replace(r"http\S+|www\S+|https\S+", "", regex=True)
                df["clean_text"] = df["clean_text"].str.replace(r'\W', ' ', regex=True).str.lower().str.strip()

            with st.spinner("Running NLP risk analysis..."):
                processed_df = process_dataframe(df, text_column="clean_text")
            st.success("NLP analysis complete.")

            # Metrics
            total = len(processed_df)
            high_count = len(processed_df[processed_df["risk_category"] == "High"])
            moderate_count = len(processed_df[processed_df["risk_category"] == "Moderate"])
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Posts", total)
            col2.metric("High Risk", high_count)
            col3.metric("Moderate Risk", moderate_count)

            # High Risk posts table
            st.subheader("High Risk Posts (top 50)")
            high_df = processed_df[processed_df["risk_category"] == "High"].sort_values("risk_score", ascending=False)
            st.dataframe(high_df.head(50))

            # Pie chart
            rc = processed_df["risk_category"].value_counts().reset_index()
            rc.columns = ["risk_category", "count"]
            pie = alt.Chart(rc).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="count", type="quantitative"),
                color=alt.Color(field="risk_category", type="nominal"),
                tooltip=["risk_category", "count"]
            ).properties(width=400, height=400)
            st.altair_chart(pie, use_container_width=True)

            # Filter & download
            keyword = st.text_input("Filter posts by keyword:")
            risk_filter = st.multiselect("Select risk categories:", ["High", "Moderate", "Low"], default=["High","Moderate","Low"])
            filtered = processed_df[processed_df["risk_category"].isin(risk_filter)]
            if keyword:
                filtered = filtered[filtered["clean_text"].str.contains(keyword, case=False, na=False)]
            st.dataframe(filtered)
            st.download_button("Download processed CSV", data=processed_df.to_csv(index=False).encode("utf-8"), file_name="sentinel_x_processed.csv", mime="text/csv")
        except Exception as e:
            st.error(f"CSV processing failed: {e}")

    # ---------- IMAGE ----------
    elif any(t in file_type for t in ["image", "png", "jpg", "jpeg"]):
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        st.info("Extracting text from image...")
        try:
            uploaded_file.seek(0)
            extracted_text = extract_text_from_image(uploaded_file)
            if not extracted_text:
                st.warning("No text extracted. Install EasyOCR or pytesseract for better OCR.")
            else:
                st.write(extracted_text[:1000])
                df_img = pd.DataFrame({"clean_text":[extracted_text]})
                with st.spinner("Running NLP analysis on image text..."):
                    processed_img_df = process_dataframe(df_img, text_column="clean_text")
                st.success("Image NLP analysis complete.")
                st.dataframe(processed_img_df)
        except Exception as e:
            st.error(f"Image processing failed: {e}")

    # ---------- VIDEO ----------
    elif any(t in file_type for t in ["video", "mp4", "mov"]):
        st.video(uploaded_file)
        st.info("Extracting text from video frames (may be slow)...")
        if not CV2_AVAILABLE or not (EASYOCR_AVAILABLE or PYTESSERACT_AVAILABLE):
            st.error("Video OCR unavailable. Install OpenCV + EasyOCR or pytesseract.")
        else:
            with st.spinner("Processing video frames..."):
                uploaded_file.seek(0)
                text_from_video, status = extract_text_from_video(uploaded_file, frame_interval=30, max_frames=60)
            if status == "cv2_not_installed":
                st.error("OpenCV not installed; cannot process video.")
            elif not text_from_video:
                st.warning("No text found or OCR unavailable.")
            else:
                st.write(text_from_video[:2000])
                df_vid = pd.DataFrame({"clean_text":[text_from_video]})
                with st.spinner("Running NLP on video-extracted text..."):
                    processed_vid_df = process_dataframe(df_vid, text_column="clean_text")
                st.success("Video NLP analysis complete.")
                st.dataframe(processed_vid_df)
    else:
        st.warning("Unsupported file type. Upload CSV, image, or video.")

# ----------------------------
st.markdown("---")
st.markdown("Sentinel-X Prototype | Powered by Streamlit, Transformers, PyVis | Demo Only ⚠️")
