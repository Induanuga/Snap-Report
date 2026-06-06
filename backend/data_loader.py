# data_loader.py
# Reads real Redfin CSV data and computes local market metrics for a given area.

import os
import csv
import random
from datetime import datetime

# Path to the CSV files (relative to backend dir, one level up)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHLY_CSV = os.path.join(
    BASE_DIR,
    "redfin_housing_market_monthly_all_country_key_metrics_2020_Jan_to_2026_Apr.csv"
)
RECENT_CSV = os.path.join(
    BASE_DIR,
    "redfin_housing_market_monthly_all_country_key_metrics_2026_Jan_to_2026_Apr.csv"
)


def load_latest_national_data() -> dict:
    """
    Parse the monthly CSV and return the most recent national data row.
    The CSV is ordered most-recent-first, so we take row index 1 (skip header).
    """
    data = {}
    try:
        with open(MONTHLY_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # First data row is the most recent (2026-04)
                data = {
                    "period_begin": row.get("PERIOD BEGIN", ""),
                    "period_end":   row.get("PERIOD END", ""),
                    "region_name":  row.get("REGION NAME", "National"),
                    "homes_sold":           _safe_float(row.get("HOMES SOLD")),
                    "homes_sold_yoy":       _safe_float(row.get("HOMES SOLD YOY (%)")),
                    "median_price":         _safe_float(row.get("MEDIAN SALE PRICE NSA ($)")),
                    "median_price_yoy":     _safe_float(row.get("MEDIAN SALE PRICE NSA YOY (%)")),
                    "days_on_market":       _safe_float(row.get("MEDIAN DAYS ON MARKET (DAYS)")),
                    "days_on_market_yoy":   _safe_float(row.get("MEDIAN DAYS ON MARKET YOY (%)")),
                    "new_listings":         _safe_float(row.get("NEW LISTINGS")),
                    "new_listings_yoy":     _safe_float(row.get("NEW LISTINGS YOY (%)")),
                    "active_listings":      _safe_float(row.get("ACTIVE LISTINGS")),
                    "active_listings_yoy":  _safe_float(row.get("ACTIVE LISTINGS YOY (%)")),
                    "pending_sales":        _safe_float(row.get("PENDING SALES")),
                    "pending_sales_yoy":    _safe_float(row.get("PENDING SALES YOY (%)")),
                }
                break  # Only need the first (most recent) row
    except FileNotFoundError:
        print(f"[WARNING] CSV not found at {MONTHLY_CSV}. Using fallback data.")
        data = _fallback_data()

    return data


def get_local_market_data(zip_code: str) -> dict:
    """
    Apply zip-code-seeded local variance to the national baseline.
    This simulates area-specific market conditions while using real national trends.
    
    Returns a dictionary ready for the Groq prompt and PDF generator.
    """
    # Seed random with numeric hash of zip_code for reproducible results per area
    seed = sum(ord(c) for c in zip_code) % 10000
    rng = random.Random(seed)

    national = load_latest_national_data()

    def vary(value: float, pct_range: float = 0.12) -> float:
        """Apply ±pct_range local variance to a national value."""
        if value is None:
            return None
        delta = rng.uniform(-pct_range, pct_range)
        return round(value * (1 + delta), 2)

    # Local price can vary significantly by market
    local_price = vary(national["median_price"], 0.18)
    local_dom   = max(1, int(vary(national["days_on_market"], 0.20)))

    # Compute list-to-sale ratio based on DOM (tighter markets = higher ratio)
    base_ratio = 98.5 if local_dom < 30 else (97.5 if local_dom < 45 else 96.0)
    list_to_sale = round(base_ratio + rng.uniform(-1.5, 1.5), 1)

    # Inventory months = active_listings / (homes_sold / period_days * 30)
    local_active   = vary(national["active_listings"], 0.15)
    local_homes_sold = vary(national["homes_sold"], 0.10)
    inventory_months = round((local_active / local_homes_sold) if local_homes_sold else 2.5, 1)

    return {
        # Primary display metrics
        "median_price":         local_price,
        "median_price_yoy":     round(vary(national["median_price_yoy"] or 2.37, 0.3), 2),
        "days_on_market":       local_dom,
        "days_on_market_yoy":   round(vary(national["days_on_market_yoy"] or 400, 0.2), 1),
        "new_listings":         int(vary(national["new_listings"], 0.12) or 0),
        "new_listings_yoy":     round(vary(national["new_listings_yoy"] or 0.74, 0.3), 2),
        "active_listings":      int(local_active or 0),
        "active_listings_yoy":  round(vary(national["active_listings_yoy"] or 1.59, 0.3), 2),
        "homes_sold":           int(local_homes_sold or 0),
        "homes_sold_yoy":       round(vary(national["homes_sold_yoy"] or 1.18, 0.3), 2),
        "pending_sales":        int(vary(national["pending_sales"], 0.10) or 0),
        "pending_sales_yoy":    round(vary(national["pending_sales_yoy"] or 5.57, 0.3), 2),

        # Derived / computed metrics
        "list_to_sale_ratio":   list_to_sale,
        "inventory_months":     inventory_months,
        "price_growth":         round(vary(national["median_price_yoy"] or 2.37, 0.35), 2),

        # National reference values for context
        "national_median_price": national["median_price"],
        "national_period":       national.get("period_end", "Apr 2026"),
        "data_source":           "Redfin Housing Market Data (National, Apr 2026)",
    }


def _safe_float(val):
    """Convert string to float, return None on failure."""
    try:
        return float(str(val).replace(',', '').strip())
    except (ValueError, TypeError):
        return None


def _fallback_data() -> dict:
    """Hardcoded fallback from the 2026-04 row in case CSV is missing."""
    return {
        "period_begin": "2026-04-01",
        "period_end":   "2026-04-30",
        "region_name":  "National",
        "homes_sold":           294846,
        "homes_sold_yoy":       1.18,
        "median_price":         396173,
        "median_price_yoy":     2.37,
        "days_on_market":       49,
        "days_on_market_yoy":   400,
        "new_listings":         398694,
        "new_listings_yoy":     0.74,
        "active_listings":      1482156,
        "active_listings_yoy":  1.59,
        "pending_sales":        350521,
        "pending_sales_yoy":    5.57,
    }
