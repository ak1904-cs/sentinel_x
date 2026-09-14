# 🛡️ Sentinel-X — Multimodal OSINT Threat Intelligence & Risk Analysis Platform

**Sentinel-X** is an open-source Multimodal Open-Source Intelligence (OSINT) Threat Analysis & Risk Profiling Platform designed to ingest text, CSV datasets, images, and video files, extract intelligence, identify named entities, score risk explainably, and visualize relationship networks.

---

## 🌟 Architecture & Highlights

```text
                               SENTINEL-X PLATFORM
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ↓                            ↓                            ↓
         TEXT                          CSV                        MEDIA
     (Direct Input)           (Multi-encoding / Gzip)        (Images & Videos)
           │                            │                            │
           │                            │                       OCR Engine
           │                            │               (EasyOCR + Tesseract)
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        ↓
                               Text Preprocessing
                      (Unicode, URLs, Hashtags, Mentions)
                                        ↓
               ┌────────────────────────┴────────────────────────┐
               ↓                                                 ↓
        NLP Engine (TF-IDF)                             Threat Indicator Engine
   (Hate & Abusive Language ML)                    (Threats, Weapons & Planning)
               ↓                                                 ↓
               └────────────────────────┬────────────────────────┘
                                        ↓
                               spaCy NER Engine
                       (PERSON, ORG, GPE, LOC, DATE, EVENT)
                                        ↓
                       Configurable Explainable Risk Engine
                             (Score 0-100 & Reasons)
                                        ↓
                       Risk-Aware Network Graph Engine
                           (PyVis Interactive Graph)
                                        ↓
                          Analyst Streamlit Dashboard
                           (Reports / PDF / JSON Export)
```

---

## ✨ Features

- **Multimodal Intelligence Pipeline**: Ingests direct text, CSV files (including gzipped datasets), images (PNG/JPG), and video files (MP4/MOV).
- **Intelligent Media OCR**: Image preprocessing (grayscale, CLAHE contrast enhancement) with EasyOCR primary engine & Tesseract fallback. Samples video frames with timestamp deduplication.
- **Dedicated Threat & Weapon Engine**: Detects violent action words, radicalization keywords, weapon/indicator lexicons (`AK-47`, `C4`, `RPG`, `IED`), and operational planning patterns (Time + Location + Action).
- **spaCy Named Entity Recognition (NER)**: Extracts `PERSON`, `ORG`, `GPE`, `LOC`, `DATE`, and `EVENT` with canonical entity alias normalization (`NYC` $\rightarrow$ `New York`, `ISIS` $\rightarrow$ `ISIS`).
- **Explainable Risk Scoring**: Configurable weights in `config/settings.py` generating a 0–100 risk score, risk level (`HIGH`, `MODERATE`, `LOW`), and human-readable bulleted reasoning.
- **Interactive Network Graph**: Risk-colored PyVis entity relationship network (`Red` for High Risk, `Orange` for Moderate Risk, `Green` for Low Risk) with interactive tooltips and connection strength.
- **Automated Intelligence Reports**: One-click generation of JSON, CSV, and formatted PDF intelligence reports.

---

## 🛠️ Project Structure

```text
sentinel-x/
│
├── app.py                     # Analyst Dashboard (Streamlit Frontend)
├── config/
│   └── settings.py            # Centralized settings & configurable risk weights
├── engines/
│   ├── nlp_engine.py          # TF-IDF + Logistic Regression ML Classifier
│   ├── threat_engine.py       # Threat lexicons, weapon indicators & planning rules
│   ├── risk_engine.py         # Configurable explainable risk engine (0-100 score)
│   ├── entity_engine.py       # spaCy NER + entity normalization
│   ├── graph_engine.py        # Risk-aware PyVis interactive network graph
│   └── ocr_engine.py          # Image & Video OCR pipeline (EasyOCR + Tesseract)
├── services/
│   ├── csv_service.py         # Multi-encoding CSV batch loader & processor
│   ├── image_service.py       # Image threat analysis service
│   ├── video_service.py       # Video timeline frame sampling service
│   └── report_service.py      # Automated PDF/JSON/CSV report generator
├── utils/
│   ├── text_utils.py          # Text normalization & signal extraction
│   ├── file_utils.py          # File type validation & temporary file handling
│   └── logging_utils.py       # Application logging (logs/sentinel_x.log)
├── data/                      # Raw datasets & cached ML models
├── tests/                     # Unit and integration test suite
├── requirements.txt           # Cleaned dependency manifest
└── README.md                  # System Documentation
```

---

## ⚙️ Installation & Usage

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/sentinel-x.git
cd sentinel-x
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run Automated Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 3. Launch Streamlit Analyst Dashboard
```bash
streamlit run app.py
```

---

## 🔬 Methodology & Evaluation

- **ML Classifier Baseline**: TF-IDF + Logistic Regression trained on `data/hate_speech.csv` achieving **85.4% Accuracy** and **86.9% F1-Score**.
- **Configurable Risk Scoring**:
  $$\text{Risk Score} = (0.30 \times \text{Threat}) + (0.30 \times \text{Context ML}) + (0.20 \times \text{spaCy Entity}) + (0.20 \times \text{Planning Signal})$$
- Weights can be adjusted in `config/settings.py`.

---

## ⚠️ Disclaimer

*For OSINT research, threat analysis demonstration, and educational use only.*
