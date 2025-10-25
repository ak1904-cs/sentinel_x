# Sentinel-X — OSINT Threat Analyzer

Sentinel-X is a prototype Streamlit application for exploratory open-source intelligence (OSINT) analysis. It extracts text from CSVs, images, and videos, applies a lightweight NLP risk-scoring pipeline, and provides an interactive dashboard for inspection and export. This repository is intended for research / demo use only.

Key features
- Robust CSV ingestion and preprocessing.
- Image and video OCR (EasyOCR or Tesseract fallbacks).
- NLP-based risk scoring and categorization.
- Interactive Streamlit dashboard with visualizations and CSV export.
- Utilities for testing OCR and simple graph visualization hooks.

Quick links (code entrypoints & helpers)
- App UI: [app.py](app.py) — main Streamlit application including [`app.try_read_csv`](app.py), [`app.extract_text_from_image`](app.py), and [`app.extract_text_from_video`](app.py).
- NLP/risk engine: [`nlp_engine.process_dataframe`](nlp_engine.py) and [`nlp_engine.calculate_risk`](nlp_engine.py).
- Data loader: [`data_loader.load_uploaded_dataset`](data_loader.py).
- Graph utilities / artifact: [graph_engine.py](graph_engine.py) and [graph.html](graph.html).
- OCR utilities & tests: [utils/ocr_utils.py](utils/ocr_utils.py) and [ocr_test.py](ocr_test.py).
- Example datasets: [data/hate_speech.csv](data/hate_speech.csv), [data/terrorism_small.csv](data/terrorism_small.csv).


Requirements
- Python 3.8+
- See [requirements.txt](requirements.txt) for Python packages.
- Optional system packages for OCR/video:
  - Tesseract (for pytesseract)
  - OpenCV system libs (for cv2)
  - Additional build deps for EasyOCR (GPU optional)

Installation (local)
```sh
# Create and activate virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Python deps
pip install -r 
