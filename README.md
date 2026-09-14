# 🛡️ Sentinel-X — End-to-End Human-in-the-Loop OSINT Threat Intelligence Platform

**Sentinel-X** is an open-source, human-in-the-loop Multimodal Open-Source Intelligence (OSINT) Threat Analysis & Case Management Platform. It ingests public web content, RSS feeds, CSV datasets, images, and video files, detects threat signals and named entities, computes explainable risk scores, hashes evidence cryptographically via SHA-256, and routes priority items to authorized human analysts for review, escalation, or dismissal.

> **Human-in-the-Loop Principle**: AI assists human analysts by surfacing and prioritizing potential threat signals; it does not autonomously accuse, identify, or punish individuals.

---

## 🌟 End-to-End Workflow Architecture

```text
                     ┌──────────────────────┐
                     │      SENTINEL-X      │
                     │ OSINT THREAT INTEL   │
                     └──────────┬───────────┘
                                │
                         SOURCE INGESTION
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
       Public Web          RSS Feeds        User Uploads
      Page Fetcher          Collector     (CSV/Image/Video)
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                         DATA NORMALization
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
              TEXT            IMAGE           VIDEO
                                │               │
                               OCR             Frames
                                │               │
                └───────────────┼───────────────┘
                                ▼
                         NLP ANALYSIS
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
             Threat          NER           Context
           Indicators      Entities       Classifier
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                         RISK ENGINE
                  (Configurable 0-100 Score)
                                │
                                ▼
                    SHA-256 EVIDENCE HASHING
                                │
                         SQLITE DATABASE
                                │
                    AUTOMATED CASE GENERATION
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
              Low/Moderate                  High
                   │                         │
               Dashboard               Analyst Queue
                                             │
                                             ▼
                                      HUMAN ANALYST
                                             │
                                  ┌──────────┴─────────┐
                                  ▼                    ▼
                              Dismiss              Escalate
                                                       │
                                                       ▼
                                             Official Report PDF
```

---

## ✨ Core Features

1. **Multimodal Ingestion Layer (`ingestion/`)**:
   - Ingests direct text, CSV datasets (including gzipped GTD format), images (PNG/JPG), and video files (MP4/MOV).
   - Ingests public web pages (`web_ingestor.py`) and public RSS/Atom feeds (`rss_ingestor.py`).
2. **Dual ML & Threat Engines (`engines/`)**:
   - TF-IDF + Logistic Regression ML classifier trained on `data/hate_speech.csv` (**85.4% Accuracy**, **86.9% F1-Score**).
   - Dedicated threat, radicalization, and weapon lexicons (`AK-47`, `C4`, `RPG`, `IED`).
   - Operational planning pattern detection (Location + Time + Action).
   - spaCy Named Entity Recognition (`PERSON`, `ORG`, `GPE`, `LOC`, `DATE`, `EVENT`) with canonical alias normalization (`NYC` $\rightarrow$ `New York`, `ISIS` $\rightarrow$ `ISIS`).
3. **Configurable Explainable Risk Scoring**:
   - Weights configured in `config/settings.py` generating 0–100 risk score and transparent bulleted reasons.
4. **Cryptographic SHA-256 Evidence Hashing & SQLite Storage (`storage/`)**:
   - Computes SHA-256 evidence content hashes for tamper-proof provenance.
   - Stores analyses, cases, evidence records, analyst notes, and audit event logs in SQLite (`storage/sentinel_x.db`).
5. **Human-in-the-Loop Priority Case Review Queue (`services/case_service.py`)**:
   - Automatically flags High and Moderate risk items into priority cases (`NEW` status).
   - Human analysts review source evidence, add notes, and trigger official decisions: `Escalate Case` or `Dismiss Case`.
6. **Risk-Aware Network Graphing & PDF Reports**:
   - Interactive PyVis network graph (`Red` = High Risk, `Orange` = Moderate Risk, `Green` = Low Risk).
   - One-click JSON, CSV, and formatted PDF intelligence report generation.

---

## 📁 Repository Structure

```text
sentinel-x/
│
├── app.py                         # Streamlit Analyst Dashboard (11 Tabs)
├── config/
│   └── settings.py                # Platform parameters, weights & thresholds
├── models/
│   ├── analysis_models.py         # AnalysisInput & AnalysisResult models
│   ├── case_models.py             # CaseRecord, CaseStatus, CasePriority models
│   └── evidence_models.py         # EvidenceRecord SHA-256 model
├── storage/
│   ├── database.py                # SQLite Connection & Schema Initializer
│   └── repository.py              # CRUD Repository for DB tables
├── ingestion/
│   ├── source_manager.py          # Unified source routing dispatcher
│   ├── web_ingestor.py            # Public webpage content extractor
│   ├── rss_ingestor.py            # RSS/Atom feed parser
│   └── api_ingestor.py            # Authorized API adapter
├── engines/
│   ├── nlp_engine.py              # TF-IDF ML Classifier
│   ├── threat_engine.py           # Violent keywords, weapons & planning rules
│   ├── entity_engine.py           # spaCy NER + canonical normalization
│   ├── risk_engine.py             # Configurable 0-100 explainable risk engine
│   ├── graph_engine.py            # PyVis interactive network graph
│   └── ocr_engine.py              # EasyOCR + Tesseract image & video frame OCR
├── services/
│   ├── analysis_service.py        # Central pipeline orchestrator
│   ├── case_service.py            # Human analyst case review workflow
│   ├── evidence_service.py        # SHA-256 evidence hashing & provenance
│   ├── csv_service.py             # CSV batch loader & GTD dataset processor
│   ├── image_service.py           # Image OCR threat service
│   ├── video_service.py           # Video frame sampling & timeline service
│   └── report_service.py          # Automated PDF, JSON & CSV report generator
├── utils/
│   ├── text_utils.py              # Text normalization & signal extraction
│   ├── file_utils.py              # Security file validation & size checking
│   └── logging_utils.py           # Application logger & audit event logger
├── data/                          # Training datasets & cached ML models
├── tests/                         # Full automated unit test suite
├── requirements.txt               # Dependencies manifest
└── README.md                      # Documentation
```

---

## ⚙️ Installation & Running

```bash
# 1. Clone & Install Dependencies
git clone https://github.com/your-username/sentinel-x.git
cd sentinel-x
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Execute Automated Unit Tests
python -m unittest discover -s tests -p "test_*.py"

# 3. Launch Dashboard App
streamlit run app.py
```

---

## ⚠️ Privacy & Ethical OSINT Boundaries

- **Target Data**: Focuses exclusively on public web content, RSS feeds, authorized APIs, and user-submitted evidence.
- **Strictly Excluded**: Private credential harvesting, bypassing authentication, unauthorized scraping, or evading platform controls.
- **Analyst Role**: AI generates risk scores and explanations to assist decision-makers; human analysts make final review decisions.
