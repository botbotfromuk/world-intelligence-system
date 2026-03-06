#!/usr/bin/env python3
"""
World Intelligence Tracker
Automated geopolitical and economic monitoring system
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import json

@dataclass
class Prediction:
    id: str
    description: str
    confidence: float  # 0-1
    made_at: str
    status: str  # "active", "confirmed", "failed", "expired"
    notes: str = ""
    updated_at: str = ""

@dataclass
class WorldEvent:
    id: str
    category: str  # "military", "economic", "political", "energy"
    description: str
    date: str
    significance: int  # 1-10
    sources: list = field(default_factory=list)
    related_predictions: list = field(default_factory=list)

@dataclass
class MarketSnapshot:
    timestamp: str
    brent_crude: float
    wti_crude: float
    dow_jones: Optional[float] = None
    sp500: Optional[float] = None
    vix: Optional[float] = None
    notes: str = ""

# Current state as of March 6-7, 2026
PREDICTIONS = [
    Prediction(
        id="OIL_100",
        description="Brent crude oil will hit $100/barrel within 2 weeks",
        confidence=0.80,
        made_at="2026-03-06",
        status="active",
        notes="Currently at $92.77 (+10% today). Hormuz closed. ~$7 gap remaining.",
        updated_at="2026-03-06"
    ),
    Prediction(
        id="US_RECESSION_Q2",
        description="US enters recession by Q2 2026",
        confidence=0.65,
        made_at="2026-03-06",
        status="active",
        notes="Feb jobs: -92K. Stagflation risk. Oil shock incoming.",
        updated_at="2026-03-06"
    ),
    Prediction(
        id="IRAN_NO_SURRENDER",
        description="Iran will NOT unconditionally surrender to US/Israel demands",
        confidence=0.95,
        made_at="2026-03-06",
        status="confirmed",
        notes="Day 7: Still defiant. Strategy of endurance confirmed by BBC analysis.",
        updated_at="2026-03-07"
    ),
    Prediction(
        id="LEBANON_GROUND_WAR",
        description="Israel launches full ground invasion of Lebanon",
        confidence=0.70,
        made_at="2026-03-07",
        status="active",
        notes="Troops and tanks massing at border. BBC reporters on scene. IMMINENT.",
        updated_at="2026-03-07"
    ),
    Prediction(
        id="AZERBAIJAN_ESCALATION",
        description="Azerbaijan enters conflict or provides corridor access",
        confidence=0.40,
        made_at="2026-03-07",
        status="active",
        notes="Armed forces on HIGH ALERT after Iranian drone strikes on border.",
        updated_at="2026-03-07"
    ),
    Prediction(
        id="OIL_150_QATAR_SCENARIO",
        description="Oil hits $150/barrel (Qatar worst-case scenario)",
        confidence=0.25,
        made_at="2026-03-07",
        status="active",
        notes="Requires: Hormuz fully blocked + Azerbaijan pipeline disruption + Lebanon war escalation.",
        updated_at="2026-03-07"
    ),
    Prediction(
        id="GLOBAL_RECESSION_2026",
        description="Global recession in 2026",
        confidence=0.60,
        made_at="2026-03-06",
        status="active",
        notes="Oil shock + US stagflation + China slowdown (lowest growth target since 1991).",
        updated_at="2026-03-06"
    ),
]

MARKET_SNAPSHOTS = [
    MarketSnapshot(
        timestamp="2026-03-06T15:00:00Z",
        brent_crude=92.77,
        wti_crude=91.27,
        dow_jones=47527.80,
        sp500=6763.71,
        vix=26.79,
        notes="Day high: $94.64. Daily change: +10.03% Brent, +12.47% WTI. Weekly: ~+35%. Historic surge."
    ),
]

KEY_EVENTS = [
    WorldEvent(
        id="KHAMENEI_KILLED",
        category="military",
        description="Iranian Supreme Leader Khamenei confirmed killed",
        date="2026-03-05",
        significance=10,
        sources=["BBC"],
    ),
    WorldEvent(
        id="HORMUZ_CLOSED",
        category="energy",
        description="Strait of Hormuz closed — 400+ tankers stranded. 20% of world oil supply disrupted.",
        date="2026-03-01",
        significance=10,
        sources=["Reuters"],
    ),
    WorldEvent(
        id="DUBAI_STRUCK",
        category="military",
        description="Iran strikes Dubai luxury landmarks — Gulf states alarmed. All red lines crossed.",
        date="2026-03-06",
        significance=8,
        sources=["BBC"],
    ),
    WorldEvent(
        id="AZERBAIJAN_ALERT",
        category="military",
        description="Azerbaijan places armed forces on HIGH ALERT after Iranian drone strikes cross border",
        date="2026-03-07",
        significance=7,
        sources=["BBC"],
    ),
    WorldEvent(
        id="LEBANON_INVASION_IMMINENT",
        category="military",
        description="Israeli troops and tanks massing at Lebanon border — full ground invasion imminent",
        date="2026-03-07",
        significance=9,
        sources=["BBC"],
    ),
    WorldEvent(
        id="US_JOBS_MINUS_92K",
        category="economic",
        description="US loses 92,000 jobs in February 2026 — unemployment rises to 4.4%. Stagflation risk.",
        date="2026-03-06",
        significance=8,
        sources=["US Labor Department"],
    ),
]

def get_scenario_probabilities():
    return {
        "A_quick_resolution": 0.20,
        "B_grinding_war_2_4_weeks": 0.50,
        "C_regional_escalation": 0.30,
    }

def print_report():
    now = datetime.now(timezone.utc).isoformat()
    print("=" * 60)
    print("WORLD INTELLIGENCE SYSTEM")
    print(f"Generated: {now}")
    print("=" * 60)
    print()
    confirmed = [p for p in PREDICTIONS if p.status == 'confirmed']
    failed = [p for p in PREDICTIONS if p.status == 'failed']
    active = [p for p in PREDICTIONS if p.status == 'active']
    print(f"Predictions: {len(active)} active, {len(confirmed)} confirmed ✅, {len(failed)} failed ❌")
    print()
    for p in PREDICTIONS:
        emoji = "✅" if p.status == "confirmed" else "❌" if p.status == "failed" else "🟡"
        print(f"{emoji} [{p.confidence:.0%}] {p.description}")
        print(f"   → {p.notes}")
    print()
    latest = MARKET_SNAPSHOTS[0]
    print(f"OIL: Brent=${latest.brent_crude} | WTI=${latest.wti_crude}")
    print(f"MARKET: Dow={latest.dow_jones} | S&P={latest.sp500} | VIX={latest.vix}")
    print()
    print("SCENARIOS:")
    for name, prob in get_scenario_probabilities().items():
        bar = '█' * int(prob * 20)
        print(f"  {name}: {prob:.0%} {bar}")

if __name__ == "__main__":
    print_report()
