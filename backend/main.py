# main.py
# FastAPI backend for SnapReport – AI-powered real estate market report generator.

import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from groq import Groq

from data_loader import get_local_market_data
from pdf_generator import generate_pdf, REPORTS_DIR

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="SnapReport API",
    description="AI-powered real estate market report generator using Redfin data + Groq LLM",
    version="1.0.0",
)

# ── CORS – allow the Vite dev server ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve generated PDFs as static files ────────────────────────────────────
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

# ── Groq client ─────────────────────────────────────────────────────────────
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("[WARNING] GROQ_API_KEY not set. Narrative generation will fail.")

groq_client = Groq(api_key=groq_api_key) if groq_api_key else None


# ── Request / Response models ────────────────────────────────────────────────
class ReportRequest(BaseModel):
    agent_name: str
    email: str
    zip_code: str


class ReportResponse(BaseModel):
    summary: str
    market_data: dict
    pdf_url: str


# ── Groq prompt builder ──────────────────────────────────────────────────────
def build_prompt(zip_code: str, market_data: dict) -> str:
    price   = f"${market_data.get('median_price', 0):,.0f}"
    dom     = market_data.get("days_on_market", 0)
    inv     = market_data.get("inventory_months", 0)
    new_lst = f"{market_data.get('new_listings', 0):,}"
    growth  = f"{market_data.get('price_growth', 0):+.2f}%"
    ratio   = f"{market_data.get('list_to_sale_ratio', 0):.1f}%"
    nat_p   = f"${market_data.get('national_median_price', 0):,.0f}"
    period  = market_data.get("national_period", "Apr 2026")

    return f"""You are a professional real estate market analyst writing for sophisticated clients.

Generate a concise, data-driven monthly housing market report for the area: {zip_code}

MARKET DATA (based on Redfin national data for {period}, adjusted for local market):
- Median Sale Price: {price} (National baseline: {nat_p})
- Median Days on Market: {dom} days
- Inventory: {inv} months of supply
- New Listings: {new_lst}
- Year-over-Year Price Growth: {growth}
- List-to-Sale Ratio: {ratio}

Write a professional report with these FOUR sections (label each clearly):

1. Market Overview
Summarize current market conditions, price trends, and whether it's a buyer's or seller's market.

2. Buyer Insight
Practical advice for buyers based on the data — competition level, negotiation room, timing.

3. Seller Insight
Practical advice for sellers — pricing strategy, how quickly homes are moving, demand signals.

4. Short-Term Forecast
A 30-60 day outlook based on current trends. Concise and data-grounded.

Tone: Professional, confident, and concise. Use specific numbers from the data provided.
Length: 250-350 words total. No markdown formatting — plain text only."""


# ── Main endpoint ────────────────────────────────────────────────────────────
@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Full pipeline:
    1. Load Redfin national data + apply local variance
    2. Build prompt and call Groq LLM
    3. Generate branded PDF via ReportLab
    4. Return summary, market data, and PDF download URL
    """
    if not groq_client:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured. Please set it in backend/.env"
        )

    # ── Step 1: Load market data ─────────────────────────────────────────────
    try:
        market_data = get_local_market_data(request.zip_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data loading error: {str(e)}")

    # ── Step 2: Generate AI narrative via Groq ───────────────────────────────
    try:
        prompt = build_prompt(request.zip_code, market_data)
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert real estate market analyst. Write clear, data-driven reports."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.65,
        )
        summary = completion.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Groq API error: {str(e)}")

    # ── Step 3: Generate PDF ─────────────────────────────────────────────────
    try:
        filename = generate_pdf(
            agent_name=request.agent_name,
            email=request.email,
            zip_code=request.zip_code,
            market_data=market_data,
            summary=summary,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

    return ReportResponse(
        summary=summary,
        market_data=market_data,
        pdf_url=f"/reports/{filename}",
    )


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "groq_configured": groq_client is not None,
    }
