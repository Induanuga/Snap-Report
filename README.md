# SnapReport 

## What It Does

- Agent enters their name, email, and target zip code / area
- Applies local market variance per zip code
- Calls **Groq LLM** (llama-3.3-70b) to write a professional market narrative
- Generates a **branded PDF report** (SnapReport + Snaphomz)
- Frontend displays stats cards + AI summary + PDF download button


## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Styling | Plain CSS (SaaS dashboard aesthetic) |
| Backend | Python FastAPI |
| AI | Groq API (llama-3.3-70b-versatile) |
| PDF | ReportLab |
| Data | Redfin CSV + local variance |


## Quick Start

### 1. Get a Groq API Key (free)
→ https://console.groq.com/

### 2. Configure Backend
```bash
cd backend
copy .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Runs on http://localhost:8000
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 5. Open the App
→ http://localhost:5173


## Project Structure

```
Snap-Report/
│
├── redfin_housing_market_monthly_*.csv   ← Real Redfin data files
├── redfin_housing_market_weekly_*.csv
│
├── backend/
│   ├── main.py              ← FastAPI app + /generate-report endpoint
│   ├── data_loader.py       ← Reads Redfin CSVs, applies local variance
│   ├── pdf_generator.py     ← ReportLab branded PDF generator
│   ├── requirements.txt
│   ├── .env                 ← Your GROQ_API_KEY goes here
│   └── generated_reports/   ← PDFs saved here, served as static files
│
└── frontend/
    ├── src/
    │   ├── App.jsx            ← Main app + form logic
    │   ├── App.css            ← SaaS dashboard styling
    │   └── components/
    │       ├── StatCard.jsx   ← Metric card component
    │       └── ReportResults.jsx  ← Results display
    ├── index.html
    └── package.json
```



## Architecture

```
Browser (React/Vite :5173)
    │  POST /generate-report
    ▼
FastAPI (:8000)
    ├── data_loader.py  ← reads real Redfin CSV → local variance
    ├── Groq API        ← llama-3.3-70b-versatile
    └── pdf_generator.py → saves branded PDF
         │
         └── /reports/{filename} (static)
    ▼
Browser downloads PDF
```



## API

### `POST /generate-report`

**Request:**
```json
{
  "agent_name": "Jane Smith",
  "email": "jane@realty.com",
  "zip_code": "94025"
}
```

**Response:**
```json
{
  "summary": "1. Market Overview\n...",
  "market_data": {
    "median_price": 467000,
    "days_on_market": 38,
    "price_growth": 3.1,
    ...
  },
  "pdf_url": "/reports/report_2026_06_06_120000_94025.pdf"
}
```

### `GET /health`
Returns server status + Groq configuration check.

