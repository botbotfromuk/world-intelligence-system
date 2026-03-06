#!/usr/bin/env python3
"""
World Intelligence System — Geopolitical Risk Score
Aggregates signals from news, prices, and events into a single 0-100 risk index.

Score components:
  - Oil price / crisis threshold (0-25 pts)
  - Active war zones (0-25 pts)
  - Economic distress signals (0-25 pts)
  - Escalation indicators (0-25 pts)

Score interpretation:
  0-20:   NORMAL — baseline world tension
  21-40:  ELEVATED — notable geopolitical stress
  41-60:  HIGH — significant crisis in progress
  61-80:  CRITICAL — major war / economic shock
  81-100: EXTREME — civilization-level threat
"""

import json
from datetime import datetime, timezone
from pathlib import Path

RISK_HISTORY_FILE = Path("/app/mmkr/REAL_LIFE/risk_history.json")
PRICE_HISTORY_FILE = Path("/app/mmkr/REAL_LIFE/price_history.json")
WORLD_EVENTS_FILE = Path("/app/mmkr/REAL_LIFE/world_events.json")

# ── Component scorers ──────────────────────────────────────────────────────────

def score_oil(prices: dict) -> tuple[int, list[str]]:
    """0-25 based on Brent crude price."""
    brent = prices.get("brent_oilprice") or prices.get("brent_crude") or 70
    notes = []

    if brent >= 150:
        pts = 25
        notes.append(f"Brent ${brent:.0f} — EXTREME (>$150)")
    elif brent >= 120:
        pts = 20
        notes.append(f"Brent ${brent:.0f} — CRITICAL (>$120)")
    elif brent >= 100:
        pts = 16
        notes.append(f"Brent ${brent:.0f} — HIGH (>$100)")
    elif brent >= 90:
        pts = 12
        notes.append(f"Brent ${brent:.0f} — ELEVATED (>$90)")
    elif brent >= 80:
        pts = 8
        notes.append(f"Brent ${brent:.0f} — MODERATE (>$80)")
    else:
        pts = 3
        notes.append(f"Brent ${brent:.0f} — NORMAL")

    return pts, notes


def score_war_zones(active_wars: list[str]) -> tuple[int, list[str]]:
    """
    0-25 based on active war zones.
    Each major active war = +8 pts. Near-war escalation = +3 pts.
    """
    pts = 0
    notes = []

    war_weights = {
        "iran_israel": 10,      # Major regional war
        "russia_ukraine": 8,    # Ongoing major war
        "lebanon_conflict": 5,  # Regional spillover
        "azerbaijan_iran": 6,   # New escalation
        "kurdish_iran": 4,      # Cross-border threat
    }

    for war in active_wars:
        w = war_weights.get(war, 2)
        pts += w
        notes.append(f"+{w}: {war}")

    pts = min(25, pts)
    return pts, notes


def score_economic(indicators: dict) -> tuple[int, list[str]]:
    """0-25 based on economic distress signals."""
    pts = 0
    notes = []

    vix = indicators.get("vix", 15)
    unemployment = indicators.get("unemployment_pct", 4.0)
    monthly_jobs = indicators.get("monthly_jobs_change", 0)
    recession_declared = indicators.get("recession_declared", False)

    if recession_declared:
        pts += 15
        notes.append("+15: Recession officially declared")

    if vix >= 40:
        pts += 6
        notes.append(f"+6: VIX {vix:.0f} (extreme fear)")
    elif vix >= 30:
        pts += 4
        notes.append(f"+4: VIX {vix:.0f} (fear zone)")
    elif vix >= 20:
        pts += 2
        notes.append(f"+2: VIX {vix:.0f} (elevated)")

    if monthly_jobs < -200_000:
        pts += 5
        notes.append(f"+5: Jobs {monthly_jobs:+,}/month (severe)")
    elif monthly_jobs < -50_000:
        pts += 3
        notes.append(f"+3: Jobs {monthly_jobs:+,}/month (negative)")

    if unemployment >= 6.0:
        pts += 4
        notes.append(f"+4: Unemployment {unemployment:.1f}% (high)")
    elif unemployment >= 5.0:
        pts += 2
        notes.append(f"+2: Unemployment {unemployment:.1f}% (rising)")

    pts = min(25, pts)
    return pts, notes


def score_escalation(signals: dict) -> tuple[int, list[str]]:
    """0-25 based on escalation indicators."""
    pts = 0
    notes = []

    escalation_weights = {
        "strait_of_hormuz_closed": (10, "Hormuz CLOSED — catastrophic chokepoint"),
        "nuclear_threat": (12, "Nuclear threat active"),
        "us_troops_engaged": (8, "US troops in direct combat"),
        "gulf_states_threatened": (5, "Gulf states under attack"),
        "global_shipping_disrupted": (6, "Global shipping disrupted"),
        "china_mobilizing": (8, "China military mobilization"),
        "azerbaijan_iron_fist": (4, "Azerbaijan threatening Iran"),
        "kurdish_border_forces": (3, "Kurdish forces at Iran border"),
        "internet_blackout_iran": (2, "Iran internet blackout"),
    }

    for signal, (weight, desc) in escalation_weights.items():
        if signals.get(signal):
            pts += weight
            notes.append(f"+{weight}: {desc}")

    pts = min(25, pts)
    return pts, notes


# ── Main scorer ────────────────────────────────────────────────────────────────

def compute_risk_score(
    prices: dict = None,
    active_wars: list = None,
    economic_indicators: dict = None,
    escalation_signals: dict = None,
) -> dict:
    """Compute total geopolitical risk score (0-100)."""

    prices = prices or {}
    active_wars = active_wars or []
    economic_indicators = economic_indicators or {}
    escalation_signals = escalation_signals or {}

    oil_pts, oil_notes = score_oil(prices)
    war_pts, war_notes = score_war_zones(active_wars)
    eco_pts, eco_notes = score_economic(economic_indicators)
    esc_pts, esc_notes = score_escalation(escalation_signals)

    total = oil_pts + war_pts + eco_pts + esc_pts

    if total >= 81:
        level = "EXTREME"
        emoji = "☢️"
    elif total >= 61:
        level = "CRITICAL"
        emoji = "🔴"
    elif total >= 41:
        level = "HIGH"
        emoji = "🟠"
    elif total >= 21:
        level = "ELEVATED"
        emoji = "🟡"
    else:
        level = "NORMAL"
        emoji = "🟢"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_score": total,
        "level": level,
        "emoji": emoji,
        "components": {
            "oil": {"score": oil_pts, "max": 25, "notes": oil_notes},
            "war_zones": {"score": war_pts, "max": 25, "notes": war_notes},
            "economic": {"score": eco_pts, "max": 25, "notes": eco_notes},
            "escalation": {"score": esc_pts, "max": 25, "notes": esc_notes},
        }
    }


def record_risk_score(score_data: dict):
    """Append score to history file."""
    history = []
    if RISK_HISTORY_FILE.exists():
        try:
            history = json.loads(RISK_HISTORY_FILE.read_text())
        except Exception:
            history = []
    history.append(score_data)
    history = history[-100:]  # keep last 100
    RISK_HISTORY_FILE.write_text(json.dumps(history, indent=2))


def print_risk_report(score_data: dict) -> str:
    """Format risk score as readable report."""
    lines = [
        f"\n{'='*60}",
        f"  GEOPOLITICAL RISK SCORE — {score_data['timestamp'][:16]} UTC",
        f"{'='*60}",
        f"",
        f"  {score_data['emoji']}  TOTAL: {score_data['total_score']}/100 — {score_data['level']}",
        f"",
        f"  Component Breakdown:",
    ]

    for comp_name, comp in score_data["components"].items():
        bar = "█" * comp["score"] + "░" * (comp["max"] - comp["score"])
        lines.append(f"    {comp_name:12s}: [{bar}] {comp['score']:2d}/{comp['max']}")
        for note in comp["notes"]:
            lines.append(f"                 {note}")

    lines.append("")
    lines.append("  Interpretation:")
    lines.append("    0-20: NORMAL | 21-40: ELEVATED | 41-60: HIGH")
    lines.append("    61-80: CRITICAL | 81-100: EXTREME")
    lines.append("=" * 60)

    return "\n".join(lines)


# ── Current world state snapshot (manually updated each tick) ──────────────────

CURRENT_STATE_TICK4 = {
    "prices": {
        "brent_oilprice": 90.50,
        "wti_oilprice": 86.00,
    },
    "active_wars": [
        "iran_israel",
        "russia_ukraine",
        "lebanon_conflict",
        "azerbaijan_iran",
        "kurdish_iran",
    ],
    "economic_indicators": {
        "vix": 26.79,
        "unemployment_pct": 4.4,
        "monthly_jobs_change": -92000,
        "recession_declared": False,
    },
    "escalation_signals": {
        "strait_of_hormuz_closed": True,
        "nuclear_threat": False,
        "us_troops_engaged": True,   # 6 US soldiers killed
        "gulf_states_threatened": True,  # Dubai struck
        "global_shipping_disrupted": True,  # 138→2 ships/day
        "china_mobilizing": False,
        "azerbaijan_iron_fist": True,
        "kurdish_border_forces": True,
        "internet_blackout_iran": True,
    }
}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", action="store_true", help="Score current world state")
    parser.add_argument("--history", action="store_true", help="Show score history")
    args = parser.parse_args()

    if args.history:
        if RISK_HISTORY_FILE.exists():
            history = json.loads(RISK_HISTORY_FILE.read_text())
            print(f"Risk Score History ({len(history)} entries):")
            for entry in history[-10:]:
                print(f"  {entry['timestamp'][:16]} | {entry['emoji']} {entry['total_score']:3d}/100 — {entry['level']}")
        else:
            print("No history yet.")
    else:
        # Default: score current state
        state = CURRENT_STATE_TICK4
        score = compute_risk_score(
            prices=state["prices"],
            active_wars=state["active_wars"],
            economic_indicators=state["economic_indicators"],
            escalation_signals=state["escalation_signals"],
        )
        print(print_risk_report(score))
        record_risk_score(score)
        print(f"\nScore recorded to {RISK_HISTORY_FILE}")
