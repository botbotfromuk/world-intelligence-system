#!/usr/bin/env python3
"""
World Intelligence System — Prediction Tracker
Tracks geopolitical/economic predictions with confidence, status, and evidence.
Author: botbotfromuk | March 2026
"""

import json
import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

class PredStatus(str, Enum):
    TRACKING   = "TRACKING"
    CONFIRMED  = "CONFIRMED"
    FAILED     = "FAILED"
    PENDING    = "PENDING"
    IMMINENT   = "IMMINENT"

@dataclass
class Prediction:
    id: str
    statement: str
    confidence: float          # 0.0–1.0
    made_on: str               # ISO date
    deadline: Optional[str]    # ISO date or None
    status: PredStatus
    category: str              # OIL | WAR | ECON | AI | GEO
    evidence: list[str] = field(default_factory=list)
    outcome: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.date.today().isoformat())

    def confidence_pct(self) -> str:
        return f"{int(self.confidence * 100)}%"

    def display(self) -> str:
        status_icon = {
            "TRACKING":  "🔄",
            "CONFIRMED": "✅",
            "FAILED":    "❌",
            "PENDING":   "⏳",
            "IMMINENT":  "🔥",
        }.get(self.status, "?")

        lines = [
            f"{status_icon} [{self.category}] {self.statement}",
            f"   Confidence: {self.confidence_pct()} | Made: {self.made_on} | Deadline: {self.deadline or 'open'}",
            f"   Status: {self.status}",
        ]
        if self.evidence:
            lines.append(f"   Evidence:")
            for e in self.evidence[-3:]:  # show last 3
                lines.append(f"     • {e}")
        if self.outcome:
            lines.append(f"   Outcome: {self.outcome}")
        return "\n".join(lines)


# ── Current State (March 7, 2026) ──────────────────────────────────────────

PREDICTIONS: list[Prediction] = [
    Prediction(
        id="OIL_100",
        statement="Brent crude oil will hit $100/barrel within 2 weeks of March 6, 2026",
        confidence=0.82,
        made_on="2026-03-06",
        deadline="2026-03-20",
        status=PredStatus.IMMINENT,
        category="OIL",
        evidence=[
            "Brent hit $92.77 on March 6 (+10% in one day)",
            "Weekly gain ~35% — largest futures surge since 1983",
            "Strait of Hormuz closed, 400+ tankers stranded",
            "Qatar: $150 possible if conflict continues weeks",
            "Kuwait cutting production (storage full)",
        ],
    ),
    Prediction(
        id="US_RECESSION_Q2",
        statement="US enters recession by Q2 2026",
        confidence=0.65,
        made_on="2026-03-06",
        deadline="2026-06-30",
        status=PredStatus.TRACKING,
        category="ECON",
        evidence=[
            "February payrolls: -92,000 jobs (surprise contraction)",
            "Unemployment rose to 4.4%",
            "VIX 26.79 (+12.8%) — elevated fear",
            "Dow -428, S&P -67 on March 6",
            "Stagflation trap: rising energy prices + job losses",
            "Mortgage rates rising with energy inflation",
        ],
    ),
    Prediction(
        id="IRAN_NO_SURRENDER",
        statement="Iran will NOT unconditionally surrender to US/Israel demands",
        confidence=0.95,
        made_on="2026-03-01",
        deadline="2026-03-31",
        status=PredStatus.CONFIRMED,
        category="WAR",
        evidence=[
            "Day 7: Iran still defiant despite 1,332+ dead",
            "Iran: 'Iran's future determined by Iranians'",
            "2,000+ drones launched — offensive still active",
            "Khamenei confirmed killed yet no capitulation",
            "Historical precedent: regimes rarely surrender unconditionally",
        ],
        outcome="CONFIRMED — Iran has not surrendered as of Day 7, despite Khamenei death and military decimation",
    ),
    Prediction(
        id="LEBANON_GROUND_WAR",
        statement="Israel will launch a full ground invasion of Lebanon",
        confidence=0.70,
        made_on="2026-03-06",
        deadline="2026-03-15",
        status=PredStatus.IMMINENT,
        category="WAR",
        evidence=[
            "BBC sees troops and tanks massing at Lebanon border",
            "Israel striking south Beirut after evacuation warnings",
            "217+ already dead in Lebanon",
            "Israel: 'another war with Iran's proxy Hezbollah'",
            "Hezbollah still operational despite Iran losses",
        ],
    ),
    Prediction(
        id="AZERBAIJAN_ESCALATION",
        statement="Azerbaijan will escalate militarily against Iran or enter conflict",
        confidence=0.40,
        made_on="2026-03-06",
        deadline="2026-03-20",
        status=PredStatus.TRACKING,
        category="GEO",
        evidence=[
            "Iran drone strikes hit Azerbaijan — 'act of terror' per Aliyev",
            "Azerbaijan armed forces placed on HIGH ALERT",
            "Flight paths closed over Azerbaijan airspace",
        ],
    ),
    Prediction(
        id="OIL_150",
        statement="Brent crude oil will hit $150/barrel if conflict extends 3+ weeks",
        confidence=0.25,
        made_on="2026-03-06",
        deadline="2026-04-06",
        status=PredStatus.TRACKING,
        category="OIL",
        evidence=[
            "Qatar Energy Minister explicit $150 warning",
            "All Gulf production at risk",
            "Hormuz closure impacting 20% of world oil supply",
        ],
    ),
    Prediction(
        id="ANTHROPIC_SURVIVES",
        statement="Anthropic survives Pentagon 'supply chain risk' designation but is weakened",
        confidence=0.55,
        made_on="2026-03-06",
        deadline="2026-06-30",
        status=PredStatus.TRACKING,
        category="AI",
        evidence=[
            "CEO Dario Amodei challenging designation in court",
            "Claude signups +295% (public support growing)",
            "OpenAI filling DOD contract gap",
            "Pentagon hypocrisy: used Claude within hours of ban",
            "Nvidia pulling back from both OpenAI and Anthropic",
        ],
    ),
    Prediction(
        id="GLOBAL_RECESSION_2026",
        statement="Global recession in 2026 driven by energy shock and trade war",
        confidence=0.60,
        made_on="2026-03-06",
        deadline="2026-12-31",
        status=PredStatus.TRACKING,
        category="ECON",
        evidence=[
            "China: lowest growth target since 1991",
            "Jet fuel +80% globally",
            "Trump tariffs challenged by 24 US states",
            "European natural gas soaring",
            "Stagflation dynamics in US, EU",
        ],
    ),
]


def print_report(predictions: list[Prediction] = PREDICTIONS):
    print("=" * 70)
    print("  WORLD INTELLIGENCE SYSTEM — PREDICTION TRACKER")
    print(f"  Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)

    by_status = {}
    for p in predictions:
        by_status.setdefault(p.status, []).append(p)

    # Show in priority order: CONFIRMED > IMMINENT > TRACKING > FAILED
    order = [PredStatus.CONFIRMED, PredStatus.IMMINENT, PredStatus.TRACKING, PredStatus.FAILED, PredStatus.PENDING]

    for status in order:
        if status not in by_status:
            continue
        print(f"\n── {status} ──────────────────────────────")
        for pred in by_status[status]:
            print()
            print(pred.display())

    # Summary stats
    print("\n" + "=" * 70)
    confirmed = sum(1 for p in predictions if p.status == PredStatus.CONFIRMED)
    failed    = sum(1 for p in predictions if p.status == PredStatus.FAILED)
    tracking  = sum(1 for p in predictions if p.status in (PredStatus.TRACKING, PredStatus.IMMINENT))
    total     = len(predictions)
    resolved  = confirmed + failed
    accuracy  = (confirmed / resolved * 100) if resolved > 0 else 0

    print(f"  Total predictions: {total}")
    print(f"  Confirmed: {confirmed} | Failed: {failed} | Tracking: {tracking}")
    print(f"  Accuracy (resolved): {accuracy:.0f}%")
    print("=" * 70)


def to_json(predictions: list[Prediction] = PREDICTIONS) -> str:
    data = {
        "generated": datetime.datetime.utcnow().isoformat() + "Z",
        "predictions": [asdict(p) for p in predictions],
        "summary": {
            "total": len(predictions),
            "confirmed": sum(1 for p in predictions if p.status == "CONFIRMED"),
            "failed": sum(1 for p in predictions if p.status == "FAILED"),
            "tracking": sum(1 for p in predictions if p.status in ("TRACKING", "IMMINENT", "PENDING")),
        }
    }
    return json.dumps(data, indent=2)


if __name__ == "__main__":
    print_report()
    # Also write JSON snapshot
    with open("predictions_snapshot.json", "w") as f:
        f.write(to_json())
    print("\n[Saved predictions_snapshot.json]")
