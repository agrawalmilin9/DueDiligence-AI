# DueDiligence AI — Backend

FastAPI backend and modular due diligence research pipeline for the DueDiligence AI application.

## Overview

The backend provides:
- **FastAPI HTTP API** for creating and retrieving due diligence investigations.
- **Investigation Status Tracking**: `pending` → `running` (with step tracking) → `completed` / `failed`.
- **7-Stage Diligence Pipeline**:
  1. `identify`: Company entity identification
  2. `company_info`: Company information & funding metrics
  3. `founders`: Founder background & track record research
  4. `market`: Market landscape & competitor analysis
  5. `claims`: Claim extraction & source verification (scaffold marked as `UNVERIFIED`)
  6. `risks`: Multi-vector risk assessment & key findings
  7. `report`: Investment recommendation & structured memo synthesis
- **Separate Service Modules**:
  - `services/crustdata.py`: Crustdata API client and integration boundary.
  - `services/research.py`: Web search (Perplexity/Tavily) & AI reasoning (OpenAI/Gemini) integration boundary.
  - `services/storage.py`: Thread-safe investigation storage and state management.
- **Frontend Contract Compatibility**: Outputs camelCase JSON fields matching `lib/types.ts: InvestigationReport`.

---

## Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py              # GET /health
│   │       └── investigations.py       # POST /investigations, GET /investigations/{id}, GET /investigations/{id}/report
│   ├── pipeline/
│   │   ├── base.py                    # BasePipelineStage & PipelineContext
│   │   ├── orchestrator.py            # Sequential 7-stage pipeline runner
│   │   └── stages/
│   │       ├── s1_company_identifier.py
│   │       ├── s2_company_info.py
│   │       ├── s3_founder_researcher.py
│   │       ├── s4_market_researcher.py
│   │       ├── s5_claim_verifier.py
│   │       ├── s6_risk_analyzer.py
│   │       └── s7_report_generator.py
│   ├── schemas/
│   │   ├── base.py                    # CamelModel (camelCase JSON alias generator)
│   │   ├── common.py                  # Enums: ClaimStatus, Recommendation, RiskLevel, Status
│   │   ├── company.py                 # CompanyOverview, CompanyMetrics, Founder, Competitor
│   │   ├── report.py                  # KeyFinding, Risk, Claim, RecommendationSummary, Memo
│   │   └── investigation.py           # InvestigationCreateRequest, InvestigationRecord, InvestigationSummary
│   ├── services/
│   │   ├── crustdata.py               # Crustdata API service module
│   │   ├── research.py                # AI/Web research service module
│   │   └── storage.py                 # In-memory storage & status tracking
│   ├── config.py                      # Environment and CORS settings
│   └── main.py                        # FastAPI entrypoint & middleware
├── tests/
│   ├── conftest.py                    # TestClient fixture
│   ├── test_health.py                 # Health endpoint tests
│   ├── test_investigations.py         # Investigation API contract & status tests
│   └── test_pipeline.py               # 7-stage pipeline execution tests
├── .env.example                       # Example environment variables
├── .env                               # Local backend environment
├── requirements.txt                   # Python dependencies
└── README.md
```

---

## Setup & Running

### 1. Requirements

Ensure Python 3.10+ is installed:
```bash
python --version
```

### 2. Environment Configuration

Copy `.env.example` to `.env` (already created locally):
```bash
cd backend
cp .env.example .env
```

### 3. Start the Backend Server

From the `backend` directory:
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or from the project root:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at:
- **API Root**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Tests

From the `backend` directory:
```bash
cd backend
python -m pytest -v
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint returning status, version, and server timestamp |
| `POST` | `/investigations` | Accepts `{ "companyName": "...", "request": "..." }`, starts 7-step pipeline, returns `InvestigationRecord` |
| `GET` | `/investigations` | Returns list of `InvestigationSummary[]` for dashboard recent items |
| `GET` | `/investigations/{id}` | Returns `InvestigationRecord` with status (`pending`, `running`, `completed`, `failed`), `currentStep`, and `report` |
| `GET` | `/investigations/{id}/report` | Direct `InvestigationReport` JSON matching frontend TypeScript types for direct drop-in |
