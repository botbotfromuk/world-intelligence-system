#!/usr/bin/env python3
"""
World Intelligence System — Geopolitical Risk Score v2
Aggregates signals from news, prices, and events into a single 0-100 risk index.

Score components:
  - Oil price / crisis threshold (0-25 pts)
  - Active war zones (0-25 pts)
  - Economic distress signals (0-25 pts)
  - Escalation indicators (0-35 pts, overflow → bonus)
  - Bonus: compounding catastrophe multiplier (0-10 pts extra)

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

# ── Component scorers ──────────────────────────────────────────────────────────

def score_oil(prices: dict) -> tuple[int, list[str]]:
    """0-25 based on Brent crude price."""
    brent = prices.get("brent_oilprice") or prices.get("brent_crude") or 70
    notes = []

    if brent >= 150:
        pts = 25
        notes.append(f"Brent ${brent:.0f} — EXTREME (>$150)")
    elif brent >= 120:
        pts = 22
        notes.append(f"Brent ${brent:.0f} — CRITICAL (>$120)")
    elif brent >= 100:
        pts = 18
        notes.append(f"Brent ${brent:.0f} — HIGH (>$100)")
    elif brent >= 90:
        pts = 14
        notes.append(f"Brent ${brent:.0f} — ELEVATED (>$90)")
    elif brent >= 80:
        pts = 8
        notes.append(f"Brent ${brent:.0f} — MODERATE (>$80)")
    else:
        pts = 3
        notes.append(f"Brent ${brent:.0f} — NORMAL")
    
    # Bonus for weekly surge magnitude
    weekly_pct = prices.get("weekly_pct_change", 0)
    if weekly_pct >= 30:
        pts = min(25, pts + 4)
        notes.append(f"+4 bonus: Weekly surge +{weekly_pct:.0f}% (historic)")
    elif weekly_pct >= 15:
        pts = min(25, pts + 2)
        notes.append(f"+2 bonus: Weekly surge +{weekly_pct:.0f}%")

    return min(25, pts), notes


def score_war_zones(active_wars: list[str]) -> tuple[int, list[str]]:
    """0-25 based on active war zones."""
    pts = 0
    notes = []

    war_weights = {
        "iran_israel": 10,      # Major regional war, US engaged
        "russia_ukraine": 8,    # Ongoing major war
        "lebanon_conflict": 5,  # Regional spillover (full ground war)
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
    stagflation_risk = indicators.get("stagflation_risk", False)
    lng_halted = indicators.get("lng_force_majeure", False)

    if recession_declared:
        pts += 15
        notes.append("+15: Recession officially declared")
    
    if stagflation_risk:
        pts += 5
        notes.append("+5: Stagflation trap (oil shock + job loss)")

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
    
    if lng_halted:
        pts += 3
        notes.append("+3: QatarEnergy Force Majeure (20% global LNG offline)")

    pts = min(25, pts)
    return pts, notes


def score_escalation(signals: dict) -> tuple[int, list[str]]:
    """0-35 based on escalation indicators (higher cap than other components)."""
    pts = 0
    notes = []

    escalation_weights = {
        "strait_of_hormuz_closed": (10, "Hormuz CLOSED — catastrophic chokepoint"),
        "nuclear_threat": (15, "Nuclear threat active"),
        "us_troops_engaged": (8, "US troops in direct combat"),
        "gulf_states_threatened": (5, "Gulf states under attack"),
        "global_shipping_disrupted": (6, "Global shipping disrupted"),
        "china_mobilizing": (8, "China military mobilization"),
        "russia_proxy_confirmed": (8, "Russia providing Iran targeting intel (AP confirmed)"),
        "beirut_mass_evacuation": (6, "Beirut mass evacuation — 90K displaced"),
        "qatar_lng_halted": (4, "QatarEnergy Force Majeure (LNG halted)"),
        "azerbaijani_retaliation_imminent": (5, "Azerbaijan retaliating against Iran"),
        "azerbaijan_iron_fist": (4, "Azerbaijan threatening Iran — HIGH ALERT"),
        "kurdish_border_forces": (3, "Kurdish forces at Iran border"),
        "internet_blackout_iran": (2, "Iran internet blackout"),
        "us_ally_not_notified": (3, "US allies not notified of strikes (fracturing coalition)"),
        "saudi_military_action": (8, "Saudi Arabia military engagement"),
    }

    for signal, (weight, desc) in escalation_weights.items():
        if signals.get(signal):
            pts += weight
            notes.append(f"+{weight}: {desc}")

    pts = min(35, pts)
    return pts, notes


def score_catastrophe_bonus(all_signals: dict) -> tuple[int, list[str]]:
    """0-10 bonus for compounding catastrophes."""
    pts = 0
    notes = []
    
    critical_count = sum([
        all_signals.get("strait_of_hormuz_closed", False),
        all_signals.get("russia_proxy_confirmed", False),
        all_signals.get("beirut_mass_evacuation", False),
        all_signals.get("us_troops_engaged", False),
        all_signals.get("qatar_lng_halted", False),
    ])
    
    if critical_count >= 5:
        pts += 10
        notes.append("+10: 5+ simultaneous catastrophes (compounding crisis)")
    elif critical_count >= 4:
        pts += 7
        notes.append(f"+7: {critical_count} simultaneous catastrophes")
    elif critical_count >= 3:
        pts += 4
        notes.append(f"+4: {critical_count} simultaneous catastrophes")
    
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
    bonus_pts, bonus_notes = score_catastrophe_bonus(escalation_signals)

    total = min(100, oil_pts + war_pts + eco_pts + esc_pts + bonus_pts)

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
            "escalation": {"score": esc_pts, "max": 35, "notes": esc_notes},
            "catastrophe_bonus": {"score": bonus_pts, "max": 10, "notes": bonus_notes},
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
        lines.append(f"    {comp_name:20s}: [{bar}] {comp['score']:2d}/{comp['max']}")
        for note in comp["notes"]:
            lines.append(f"                         {note}")

    lines.append("")
    lines.append("  Interpretation:")
    lines.append("    0-20: NORMAL | 21-40: ELEVATED | 41-60: HIGH")
    lines.append("    61-80: CRITICAL | 81-100: EXTREME")
    lines.append("=" * 60)

    return "\n".join(lines)


# ── Current world state snapshot (TICK 9 — March 6-7, 2026) ───────────────────

CURRENT_STATE = {
    "prices": {
        "brent_oilprice": 92.55,
        "wti_oilprice": 91.10,
        "murban": 102.20,
        "weekly_pct_change": 35.0,  # +35% week (largest since 1983)
    },
    "active_wars": [
        "iran_israel",
        "russia_ukraine",
        "lebanon_conflict",
        "azerbaijan_iran",
        "kurdish_iran",
    ],
    "economic_indicators": {
        "vix": 28.20,
        "unemployment_pct": 4.4,
        "monthly_jobs_change": -92000,
        "recession_declared": False,
        "stagflation_risk": True,
        "lng_force_majeure": True,     # QatarEnergy
    },
    "escalation_signals": {
        "strait_of_hormuz_closed": True,
        "nuclear_threat": False,
        "us_troops_engaged": True,           # 6 US soldiers killed
        "gulf_states_threatened": True,      # Embassy struck, refinery hit
        "global_shipping_disrupted": True,   # 138→2 ships/day
        "china_mobilizing": False,
        "russia_proxy_confirmed": True,      # AP: targeting intel to Iran
        "beirut_mass_evacuation": True,      # 90K displaced
        "qatar_lng_halted": True,            # Force Majeure
        "azerbaijani_retaliation_imminent": False,  # Not yet
        "azerbaijan_iron_fist": True,        # HIGH ALERT
        "kurdish_border_forces": True,
        "internet_blackout_iran": True,
        "us_ally_not_notified": True,        # Saudi Arabia frozen out
        "saudi_military_action": False,      # Not yet
    }
}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
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
        score = compute_risk_score(
            prices=CURRENT_STATE["prices"],
            active_wars=CURRENT_STATE["active_wars"],
            economic_indicators=CURRENT_STATE["economic_indicators"],
            escalation_signals=CURRENT_STATE["escalation_signals"],
        )
        print(print_risk_report(score))
        record_risk_score(score)
        print(f"\nScore recorded to {RISK_HISTORY_FILE}")
