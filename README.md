Sentinel-X — OSINT Threat Analyzer
Sentinel-X is a prototype Streamlit application for exploratory OSINT analysis of text extracted from CSVs, images, and videos. It combines lightweight OCR, simple preprocessing, and an NLP-based risk-scoring pipeline to highlight potentially risky content for demo / research purposes.

Key components

Web UI and I/O: app.py — entrypoint and Streamlit UI. See functions app.try_read_csv, app.extract_text_from_image and app.extract_text_from_video.
NLP/risk pipeline: nlp_engine.process_dataframe and nlp_engine.calculate_risk.
Data loading helpers: data_loader.load_uploaded_dataset.
Graph utilities / visualization: graph_engine.py and graph.html.
OCR utilities & tests: ocr_utils.py and ocr_test.py.
Example datasets: hate_speech.csv, terrorism_small.csv.
Repository files

app.py
nlp_engine.py
data_loader.py
graph_engine.py
graph.html
ocr_test.py
ocr_utils.py
requirements.txt
setup.sh
devcontainer.json
packages.sh
runtime.txt
hate_speech.csv
terrorism_small.csv
README.md
Quickstart (local)

Create a virtualenv and install dependencies:
(Optional) For OCR/video support install system deps (see packages.sh and setup.sh):
Run the app:
How it works (high level)

The Streamlit app (app.py) accepts CSV, image, or video uploads via the sidebar.
CSV flow: reads CSV robustly with app.try_read_csv, normalizes text into clean_text, then calls nlp_engine.process_dataframe to compute risk scores and categories. Results are displayed and downloadable.
Image flow: extracts text using EasyOCR (if available) or pytesseract via app.extract_text_from_image and runs the same NLP pipeline.
Video flow: samples frames using OpenCV and runs OCR on frames via app.extract_text_from_video. Extracted text is analyzed with the NLP pipeline.
Graphing and relationship visualization tools are available from graph_engine.py and graph.html.
Important implementation points and hooks

OCR: app tries EasyOCR first and falls back to pytesseract. See app.ocr_image_bytes_with_easyocr and app.ocr_image_pytesseract.
NLP pipeline: Core scoring and preprocessing live in nlp_engine.process_dataframe and nlp_engine.calculate_risk.
Data loader: helper(s) in data_loader.load_uploaded_dataset provide an abstraction for different upload formats.
Development & testing

The repository includes a devcontainer config at devcontainer.json for reproducible development.
Streamlit-specific environment hints are in packages.sh and runtime.txt.
Use ocr_test.py and ocr_utils.py to validate OCR behavior with different engines.
Security, ethics, and disclaimer

This project is a prototype / demo. It is not intended for operational deployment, automated actionable decisions, or any use that may harm people.
Outputs should be treated as exploratory indicators requiring human review.
See the top of app.py for the visible disclaimer text.
Contributing

Report issues or open PRs for bug fixes, improved OCR handling, better preprocessing, or more robust risk models.
When adding heavy dependencies (e.g., EasyOCR, OpenCV, Tesseract), update requirements.txt and the setup scripts (.streamlit / setup.sh).
License

Add your preferred license file to the repo (e.g., LICENSE) to state permitted uses.
If you want, I can:

Draft a CONTRIBUTING.md or LICENSE file.
Add a minimal CI job to run linting or tests.
Produce a compact developer checklist to get the devcontainer running.
