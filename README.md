# GSTSaathi - GST Compliance Software

**Version:** 0.1.0 (P0 MVP - In Development)  
**Status:** Phases 1-5 Implemented, Phase 6 Delivery Pack Added  
**Target Users:** Indian MSMEs for GST compliance automation

---

## Overview

GSTSaathi is an AI-powered GST compliance automation tool designed for Indian MSMEs. It automates invoice management, ITC reconciliation, and GST return filing using a multi-agent AI architecture with smolagents CodeAgents.

---

## Screenshots


### 1. Login Page

![Login Page](frontend/public/screenshots/login-page.png)

### 2. Invoice Upload

![Invoice Upload](frontend/public/screenshots/invoice-upload.png)

### 3. Dashboard Overview

![Dashboard Overview](frontend/public/screenshots/dashboard-overview.png)

### 4. Reconciliation Results

![Reconciliation Results](frontend/public/screenshots/reconciliation-results.png)

### 5. Export Reports

![Export Reports](frontend/public/screenshots/export-reports.png)

### 5. Exported Report Excel

![Export Reports](frontend/public/screenshots/exported-report.png)

### Key Features (P0 MVP)

- **Excel/CSV Invoice Upload** - Drag-drop upload with automatic parsing
- **GSTIN Validation** - Real-time format and checksum validation (ValidatorAgent)
- **Duplicate Detection** - Flag duplicate invoices automatically (DataAgent)
- **GSTR-2B Reconciliation** - Auto-match invoices with GSTR-2B data (ReconciliationAgent)
- **ITC Calculation** - Calculate eligible Input Tax Credit Section 17(5) (ComplianceAgent)
- **GSTR-1/3B Export** - Generate GST portal-compatible JSON/Excel files (FilingAgent)
- **Dashboard** - View compliance metrics, ITC at risk, mismatches

---

## Tech Stack

### Backend

| Component       | Technology                 |
| --------------- | -------------------------- |
| Framework       | FastAPI 0.135+             |
| Agent Framework | smolagents 1.24+           |
| LLM Framework   | LangChain 1.2+             |
| LLM             | Gemini API                 |
| Data Processing | pandas 3.0+                |
| Database        | SQLite + SQLAlchemy 2.0+   |
| Auth            | JWT (python-jose) + bcrypt |
| Vector Store    | ChromaDB 1.5.5             |

### Frontend

| Component  | Technology      |
| ---------- | --------------- |
| Framework  | React 18 + Vite |
| UI Library | Ant Design 5    |
| State      | Zustand         |
| HTTP       | Axios           |
| Styling    | Tailwind CSS    |

---

## Project Structure

```
gst-compliance/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB connection
│   │   ├── models/              # SQLAlchemy models (6 tables)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # REST routes (auth, upload, reconcile, export, dashboard)
│   │   ├── services/            # Business logic (auth, upload, export)
│   │   ├── agents/              # smolagents CodeAgents (6 P0 agents)
│   │   ├── utils/               # Utilities (GSTIN, HSN, ITC calculators)
│   │   └── middleware/          # Custom middleware
│   ├── uploads/                 # Uploaded files
│   ├── exports/                 # Generated exports
│   ├── gst_law_db/              # ChromaDB persistence
│   ├── requirements.txt
│   ├── .env
│   └── start.bat                # Windows quick start
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── api/                 # API client (axios)
│   │   ├── store/               # Zustand stores
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── start.bat                # Windows quick start
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python:** 3.11 or 3.12 (not 3.13+)
- **Node.js:** 18+
- **Gemini API Key:** Get from https://makersuite.google.com/app/apikey

### Backend Setup (Windows)

1. **Navigate to backend directory:**

   ```cmd
   cd backend
   ```

2. **Run quick start script:**

   ```cmd
   start.bat
   ```

   Or manually:

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```

3. **Edit `.env` and add your Gemini API key:**

   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Start the server:**

   ```cmd
   uvicorn app.main:app --reload
   ```

5. **Access API docs:** http://localhost:8000/docs

### Frontend Setup (Windows)

1. **Navigate to frontend directory:**

   ```cmd
   cd frontend
   ```

2. **Install dependencies:**

   ```cmd
   npm install
   ```

3. **Start development server:**

   ```cmd
   npm run dev
   ```

4. **Access the app:** http://localhost:5173

---

## API Endpoints

### Authentication

| Endpoint             | Method | Description             |
| -------------------- | ------ | ----------------------- |
| `/api/auth/register` | POST   | Register new user       |
| `/api/auth/login`    | POST   | Login and get JWT token |

### Upload

| Endpoint               | Method | Description               |
| ---------------------- | ------ | ------------------------- |
| `/api/upload/invoices` | POST   | Upload invoice Excel/CSV  |
| `/api/upload/gstr2b`   | POST   | Upload GSTR-2B JSON/Excel |
| `/api/upload/history`  | GET    | Get upload history        |

### Reconciliation

| Endpoint                        | Method | Description                    |
| ------------------------------- | ------ | ------------------------------ |
| `/api/reconcile/run`            | POST   | Run reconciliation             |
| `/api/reconcile/status/:job_id` | GET    | Get reconciliation status      |
| `/api/reconcile/results`        | GET    | Get reconciliation results     |
| `/api/reconcile/log`            | GET    | Get reconciliation run history |

### Export

| Endpoint                      | Method | Description              |
| ----------------------------- | ------ | ------------------------ |
| `/api/export/gstr1`           | GET    | Download GSTR-1 JSON     |
| `/api/export/gstr3b`          | GET    | Download GSTR-3B Excel   |
| `/api/export/mismatch-report` | GET    | Download mismatch report |

### Dashboard

| Endpoint                 | Method | Description           |
| ------------------------ | ------ | --------------------- |
| `/api/dashboard/metrics` | GET    | Get dashboard metrics |
| `/api/dashboard/summary` | GET    | Get dashboard summary |

---

## AI Agents (P0)

The P0 MVP includes 6 smolagents CodeAgents:

| Agent                   | Purpose                                            | Tools                                                       |
| ----------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
| **ValidatorAgent**      | Validate GSTIN format + checksum, HSN code         | `validate_gstin()`, `validate_hsn_code()`                   |
| **DataAgent**           | Parse Excel/CSV, detect duplicates, transform data | `parse_excel()`, `detect_duplicates()`                      |
| **ReconciliationAgent** | Match invoices with GSTR-2B, classify mismatches   | `exact_match_invoices()`, `classify_mismatch()`             |
| **ComplianceAgent**     | Calculate eligible ITC, apply Section 17(5)        | `calculate_eligible_itc()`, `calculate_net_gst_liability()` |
| **FilingAgent**         | Generate GSTR-1 JSON, GSTR-3B Excel                | `generate_gstr1_return()`, `generate_gstr3b_return()`       |
| **OrchestratorAgent**   | Coordinate agent workflows                         | `process_invoice_upload()`, `run_reconciliation()`          |

---

### Generate sample data

From `backend/` run:

```bash
python tests/generate_sample_data.py
```

This generates:

- `backend/tests/sample_data/invoices.csv` (1000+ rows, includes duplicates and invalid GSTIN samples)
- `backend/tests/sample_data/gstr2b.json` (~80% match set with mismatches)

### Suggested validation flow

1. Register and login in frontend.
2. Create company profile in Settings.
3. Upload `invoices.csv` and `gstr2b.json`.
4. Run reconciliation and review mismatch table and reconciliation log.
5. Verify dashboard cards and ITC-at-risk widget.
6. Export GSTR-1, GSTR-3B, and mismatch report.

---

## Current Status

### Completed

- ✅ Backend project structure
- ✅ Database models (6 tables: users, companies, invoices, gstr2b_entries, reconciliation_results, audit_logs)
- ✅ API routes (auth, upload, reconcile, export, dashboard)
- ✅ Services (auth_service, upload_service, export_service)
- ✅ Utility modules (GSTIN validator, HSN validator, ITC calculator)
- ✅ 6 AI Agents using smolagents
- ✅ Frontend project structure
- ✅ Frontend API client and Zustand stores

### Next Steps

1. Install backend dependencies and test server startup
2. Install frontend dependencies and test server startup
3. Create sample test data (invoices.xlsx, gstr2b.json)
4. Test end-to-end flow with sample data
5. Implement remaining frontend pages

---

## Success Criteria

| Metric             | Target                        |
| ------------------ | ----------------------------- |
| Invoice Processing | 1000 invoices in < 30 seconds |
| Reconciliation     | 500 matches in < 10 seconds   |
| Dashboard Load     | < 2 seconds                   |
| GSTIN Validation   | 100% accuracy                 |

---

## Common Issues

### ChromaDB Python Version Error

**Error:** `ChromaDB is not supported for versions greater than python 3.12`  
**Solution:** Use Python 3.11 or 3.12 (not 3.13+)

### Gemini API Not Working

**Check:** Ensure `GEMINI_API_KEY` is set in `.env` file  
**Get Key:** https://makersuite.google.com/app/apikey

### pandas 3.0 Breaking Changes

**Reference:** See https://pandas.pydata.org/docs/whatsnew/v3.0.0.html

---

## License

MIT

---

## Contact

For questions or support, refer to the hackathon team channels.
