#!/usr/bin/env python3
"""
World Intelligence System — Price Trend Tracker
Tracks oil, market indices, and commodity prices over time.
Stores historical data and computes trend signals.
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PRICES_FILE = Path("/app/mmkr/REAL_LIFE/price_history.json")

# Scrapers for key prices (using curl + simple parsing)
PRICE_SOURCES = {
    "brent_crude": {
        "url": "https://finance.yahoo.com/quote/BZ%3DF/",
        "pattern": r'"regularMarketPrice"[^}]*?"raw":([\d.]+)',
        "fallback_pattern": r'([\d.]+)\s*(?:USD)?\s*(?:per barrel|bbl)',
        "unit": "USD/bbl",
    },
    "wti_crude": {
        "url": "https://finance.yahoo.com/quote/CL%3DF/",
        "pattern": r'"regularMarketPrice"[^}]*?"raw":([\d.]+)',
        "unit": "USD/bbl",
    },
    "sp500": {
        "url": "https://finance.yahoo.com/quote/%5EGSPC/",
        "pattern": r'"regularMarketPrice"[^}]*?"raw":([\d.]+)',
        "unit": "index",
    },
    "vix": {
        "url": "https://finance.yahoo.com/quote/%5EVIX/",
        "pattern": r'"regularMarketPrice"[^}]*?"raw":([\d.]+)',
        "unit": "index",
    },
    "gold": {
        "url": "https://finance.yahoo.com/quote/GC%3DF/",
        "pattern": r'"regularMarketPrice"[^}]*?"raw":([\d.]+)',
        "unit": "USD/oz",
    },
}

# OilPrice.com scraper for context text
OILPRICE_RSS = "https://www.oilprice.com/rss/main"


def load_history() -> dict:
    if PRICES_FILE.exists() and PRICES_FILE.stat().st_size > 0:
        try:
            return json.loads(PRICES_FILE.read_text())
        except Exception:
            pass
    return {}


def save_history(data: dict):
    PRICES_FILE.write_text(json.dumps(data, indent=2, default=str))


def fetch_url(url: str, timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), "-A",
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120",
             "--compressed",
             url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        return result.stdout
    except Exception:
        return ""


def extract_price(html: str, pattern: str) -> float | None:
    try:
        m = re.search(pattern, html)
        if m:
            return float(m.group(1))
    except Exception:
        pass
    return None


def fetch_oilprice_context() -> dict:
    """Scrape OilPrice RSS for latest price mentions."""
    xml = fetch_url(OILPRICE_RSS)
    prices_mentioned = {}

    # Look for Brent price in headlines
    brent_pattern = r'[Bb]rent[^$]*\$([\d.]+)'
    wti_pattern = r'WTI[^$]*\$([\d.]+)'

    for match in re.finditer(brent_pattern, xml):
        val = float(match.group(1))
        if 50 < val < 300:  # sanity check
            prices_mentioned['brent_oilprice'] = val

    for match in re.finditer(wti_pattern, xml):
        val = float(match.group(1))
        if 50 < val < 300:
            prices_mentioned['wti_oilprice'] = val

    # Extract headlines mentioning prices
    title_pattern = r'<title><!\[CDATA\[([^\]]+)\]\]></title>'
    headlines = re.findall(title_pattern, xml)[:20]
    price_headlines = [h for h in headlines if any(
        x in h for x in ['$', 'price', 'barrel', 'crude', 'brent', 'WTI', 'oil']
    )]

    return {
        "prices": prices_mentioned,
        "price_headlines": price_headlines[:10]
    }


def record_prices(prices: dict, source: str = "manual") -> dict:
    """Add a price snapshot to history."""
    history = load_history()
    ts = datetime.now(timezone.utc).isoformat()

    snapshot = {
        "timestamp": ts,
        "source": source,
        "prices": prices,
    }

    history.setdefault("snapshots", []).append(snapshot)
    history["snapshots"] = history["snapshots"][-200:]  # keep last 200
    history["last_updated"] = ts

    save_history(history)
    return snapshot


def compute_trend(asset: str, lookback: int = 5) -> dict:
    """Compute price trend for an asset over last N snapshots."""
    history = load_history()
    snapshots = history.get("snapshots", [])

    values = []
    for snap in snapshots[-lookback:]:
        p = snap["prices"].get(asset)
        if p is not None:
            values.append((snap["timestamp"], float(p)))

    if len(values) < 2:
        return {"asset": asset, "trend": "insufficient_data", "values": values}

    first_val = values[0][1]
    last_val = values[-1][1]
    change_pct = ((last_val - first_val) / first_val) * 100 if first_val else 0

    direction = "UP" if change_pct > 1 else "DOWN" if change_pct < -1 else "FLAT"

    return {
        "asset": asset,
        "trend": direction,
        "change_pct": round(change_pct, 2),
        "first": first_val,
        "latest": last_val,
        "n_points": len(values),
        "values": values,
    }


def print_trend_report() -> str:
    """Generate a readable trend report."""
    history = load_history()
    snapshots = history.get("snapshots", [])

    if not snapshots:
        return "No price history yet. Run with --record first."

    latest = snapshots[-1]
    lines = [
        f"=== PRICE TREND REPORT === {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Last snapshot: {latest['timestamp'][:16]} UTC",
        "",
        "--- LATEST PRICES ---"
    ]

    for asset, price in latest["prices"].items():
        trend = compute_trend(asset)
        n_pts = trend.get("n_points", 0)
        trend_str = f" [{trend['trend']} {trend.get('change_pct', 0):+.1f}%]" if n_pts >= 2 else ""
        lines.append(f"  {asset:25s}: {price:8.2f}{trend_str}")

    # Prediction checks
    prices = latest["prices"]
    lines.append("")
    lines.append("--- PREDICTION STATUS ---")

    brent = prices.get("brent_oilprice") or prices.get("brent_crude")
    if brent:
        if brent >= 100:
            lines.append(f"  ✅ OIL_100: CONFIRMED! Brent ${brent:.2f} >= $100")
        elif brent >= 95:
            lines.append(f"  🟡 OIL_100: IMMINENT — Brent ${brent:.2f} (gap: ${100-brent:.2f})")
        else:
            lines.append(f"  🔴 OIL_100: TRACKING — Brent ${brent:.2f} (gap: ${100-brent:.2f})")

    vix = prices.get("vix")
    if vix:
        if vix > 30:
            lines.append(f"  ⚠️  VIX: FEAR ZONE at {vix:.2f} (>30 = recession signal)")
        elif vix > 20:
            lines.append(f"  🟡 VIX: ELEVATED at {vix:.2f} (20-30 = uncertainty)")
        else:
            lines.append(f"  ✅ VIX: CALM at {vix:.2f} (<20 = stable)")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Price Trend Tracker")
    parser.add_argument("--record", nargs="+", help="Record prices: key=value pairs e.g. brent_crude=92.5")
    parser.add_argument("--fetch-oil", action="store_true", help="Fetch prices from OilPrice RSS")
    parser.add_argument("--trend", help="Show trend for specific asset")
    parser.add_argument("--report", action="store_true", help="Print full trend report")
    args = parser.parse_args()

    if args.fetch_oil:
        print("Fetching from OilPrice.com...")
        ctx = fetch_oilprice_context()
        print(f"Prices found: {ctx['prices']}")
        print("Price headlines:")
        for h in ctx['price_headlines']:
            print(f"  • {h}")
        if ctx['prices']:
            snap = record_prices(ctx['prices'], source="oilprice_rss")
            print(f"\nRecorded: {snap['prices']}")

    elif args.record:
        prices = {}
        for item in args.record:
            k, v = item.split("=")
            prices[k] = float(v)
        snap = record_prices(prices, source="manual")
        print(f"Recorded snapshot: {snap}")

    elif args.trend:
        result = compute_trend(args.trend)
        print(json.dumps(result, indent=2))

    elif args.report:
        print(print_trend_report())

    else:
        # Default: fetch oil + show report
        ctx = fetch_oilprice_context()
        if ctx['prices']:
            record_prices(ctx['prices'], source="oilprice_rss")
        print(print_trend_report())
