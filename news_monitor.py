#!/usr/bin/env python3
"""
World Intelligence System — Automated News Monitor v2
Uses RSS feeds for reliable parsing. Tracks geopolitical & economic signals.
Run manually or schedule via cron.
"""

import json
import subprocess
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

SITREPS_FILE = Path("/app/mmkr/REAL_LIFE/sitreps.json")
EVENTS_FILE  = Path("/app/mmkr/REAL_LIFE/world_events.json")

# RSS feeds — reliable, no JS rendering required
RSS_FEEDS = {
    "bbc_world":    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "oilprice":     "https://www.oilprice.com/rss/main",
    "al_jazeera":   "https://www.aljazeera.com/xml/rss/all.xml",
    "reuters_biz":  "https://feeds.reuters.com/reuters/businessnews",
}

WATCH_KEYWORDS = [
    "iran", "israel", "lebanon", "ceasefire", "surrender", "hormuz",
    "oil", "brent", "wti", "$100", "$90", "$95", "oil price",
    "azerbaijan", "kurdish", "hezbollah",
    "recession", "unemployment", "fed", "inflation", "stagflation",
    "anthropic", "openai", "pentagon", "china", "taiwan",
    "war", "strike", "attack", "missile", "drone",
    "trump", "market", "dow", "nasdaq"
]

CRITICAL_SIGNALS = {
    "oil_at_100":         lambda t: any(x in t for x in ["$100", "100 a barrel", "triple digit", "century mark"]),
    "oil_over_100":       lambda t: any(x in t for x in ["$105", "$110", "$115", "$120", "$130", "$150"]),
    "ceasefire":          lambda t: "ceasefire" in t,
        "iran_surrender":     lambda t: "surrender" in t and "iran" in t and any(x in t for x in ["surrenders", "iran surrenders", "tehran surrenders", "agreed to surrender", "agrees to surrender"]),
    "lebanon_ground_war": lambda t: "ground" in t and ("invasion" in t or "troops" in t) and "lebanon" in t,
    "hormuz_reopened":    lambda t: "hormuz" in t and ("reopen" in t or "open" in t),
    "us_recession":       lambda t: "recession" in t and any(x in t for x in ["official", "confirm", "declared"]),
    "china_escalation":   lambda t: "china" in t and any(x in t for x in ["taiwan", "south china sea", "military"]),
    "nuclear":            lambda t: "nuclear" in t and any(x in t for x in ["iran", "israel", "strike"]),
}


def load_json(path: Path):
    if path.exists() and path.stat().st_size > 0:
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, default=str))


def fetch_rss(url: str) -> str:
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "15", "-A",
             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
             url],
            capture_output=True, text=True, timeout=20
        )
        return result.stdout
    except Exception as e:
        return ""


def parse_rss(xml_text: str) -> list[dict]:
    """Parse RSS XML into list of {title, description, pubDate, link}."""
    if not xml_text.strip():
        return []
    try:
        # Strip namespaces for simpler parsing
        xml_clean = re.sub(r' xmlns[^"]*"[^"]*"', '', xml_text)
        root = ET.fromstring(xml_clean)
        items = root.findall('.//item')
        results = []
        for item in items:
            def get(tag):
                el = item.find(tag)
                return (el.text or '').strip() if el is not None else ''
            results.append({
                "title":       get("title"),
                "description": get("description")[:500],
                "pubDate":     get("pubDate"),
                "link":        get("link"),
            })
        return results
    except Exception as e:
        return []


def check_signals(items: list[dict]) -> dict:
    """Check all items against critical signal detectors."""
    full_text = " ".join(
        (i["title"] + " " + i["description"]).lower()
        for i in items
    )
    return {
        signal_name: detector(full_text)
        for signal_name, detector in CRITICAL_SIGNALS.items()
        if detector(full_text)
    }


def filter_relevant(items: list[dict]) -> list[dict]:
    """Return only items matching watch keywords."""
    relevant = []
    for item in items:
        t = (item["title"] + " " + item["description"]).lower()
        if any(kw in t for kw in WATCH_KEYWORDS):
            relevant.append(item)
    return relevant


def log_event(event_type: str, description: str, data: dict = None):
    events = load_json(EVENTS_FILE)
    if not isinstance(events, list):
        events = []
    events.append({
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "type":        event_type,
        "description": description,
        "data":        data or {}
    })
    save_json(EVENTS_FILE, events[-500:])


def run_monitor(feeds: list[str] = None, verbose: bool = True) -> dict:
    """Main monitoring loop. Returns summary dict."""
    feeds = feeds or list(RSS_FEEDS.keys())
    now   = datetime.now(timezone.utc).isoformat()

    sitreps = load_json(SITREPS_FILE)
    if not isinstance(sitreps, dict):
        sitreps = {}

    all_relevant = []
    results = {
        "run_timestamp": now,
        "feeds_checked": [],
        "items_found":   0,
        "relevant_hits": 0,
        "active_signals": {},
        "top_headlines": []
    }

    for feed_name in feeds:
        url = RSS_FEEDS.get(feed_name)
        if not url:
            continue

        if verbose:
            print(f"[{now[:19]}] Fetching {feed_name}...")

        xml_text = fetch_rss(url)
        items    = parse_rss(xml_text)
        relevant = filter_relevant(items)

        if verbose:
            print(f"  {len(items)} items, {len(relevant)} relevant")

        # Store in sitreps
        entry = {
            "timestamp":     now,
            "items_total":   len(items),
            "items_relevant": len(relevant),
            "headlines":     [i["title"] for i in relevant[:20]],
            "details":       relevant[:10],
        }
        sitreps.setdefault(feed_name, []).append(entry)
        sitreps[feed_name] = sitreps[feed_name][-50:]

        results["feeds_checked"].append(feed_name)
        results["items_found"]   += len(items)
        results["relevant_hits"] += len(relevant)
        all_relevant.extend(relevant)

    # Check for critical signals across all gathered items
    signals = check_signals(all_relevant)
    results["active_signals"] = signals

    # Top headlines (deduplicated)
    seen = set()
    top = []
    for item in all_relevant:
        if item["title"] not in seen:
            seen.add(item["title"])
            top.append(item["title"])
        if len(top) >= 20:
            break
    results["top_headlines"] = top

    if signals:
        log_event("CRITICAL_SIGNAL", f"Active signals: {list(signals.keys())}", signals)
        if verbose:
            print(f"\n🚨 CRITICAL SIGNALS DETECTED: {list(signals.keys())}")

    if verbose and top:
        print(f"\n--- TOP RELEVANT HEADLINES ---")
        for h in top[:15]:
            print(f"  • {h}")

    save_json(SITREPS_FILE, sitreps)
    return results


def generate_report(feed: str = None) -> str:
    """Print readable intelligence digest from stored sitreps."""
    sitreps = load_json(SITREPS_FILE)
    if not sitreps:
        return "No sitrep data available yet."

    sources = [feed] if feed else list(sitreps.keys())
    lines = [f"=== INTELLIGENCE DIGEST === {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"]

    for src in sources:
        entries = sitreps.get(src, [])
        if not entries:
            continue
        latest = entries[-1]
        lines.append(f"\n--- {src.upper()} (as of {latest['timestamp'][:16]}) ---")
        lines.append(f"    {latest['items_total']} total items, {latest['items_relevant']} relevant")
        for h in latest.get("headlines", [])[:12]:
            lines.append(f"    • {h}")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="World Intelligence News Monitor")
    parser.add_argument("--report", action="store_true", help="Print stored digest")
    parser.add_argument("--feed",   help="Monitor specific feed only")
    parser.add_argument("--quiet",  action="store_true")
    args = parser.parse_args()

    if args.report:
        print(generate_report(args.feed))
    else:
        feeds = [args.feed] if args.feed else None
        results = run_monitor(feeds=feeds, verbose=not args.quiet)
        if not args.quiet:
            print(f"\nSummary: {results['relevant_hits']} relevant items across {len(results['feeds_checked'])} feeds")
