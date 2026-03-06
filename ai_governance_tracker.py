"""
AI Governance Conflict Tracker
Tracks the escalating AI governance war: tech companies vs. governments
Key story: Anthropic vs Pentagon supply chain risk designation (March 2026)
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import json

@dataclass
class AIConflictEvent:
    date: str
    actor: str
    action: str
    impact: str
    severity: str  # LOW / MEDIUM / HIGH / CRITICAL
    source: str

@dataclass 
class AICompanyStatus:
    name: str
    government_relationship: str  # ALLY / NEUTRAL / HOSTILE / BANNED
    dod_access: bool
    key_event: str
    commercial_impact: str
    market_position: str

# Current AI governance conflict status
COMPANIES = {
    "Anthropic": AICompanyStatus(
        name="Anthropic",
        government_relationship="HOSTILE",
        dod_access=False,
        key_event="Pentagon supply chain risk designation March 6 2026 - SUING DOD",
        commercial_impact="Banned from DoD contractors; 1M+ daily Claude signups unaffected",
        market_position="Most downloaded AI app globally; major revenue from commercial/enterprise"
    ),
    "OpenAI": AICompanyStatus(
        name="OpenAI", 
        government_relationship="ALLY",
        dod_access=True,
        key_event="New DoD contract signed after Anthropic fallout; Altman praised Trump",
        commercial_impact="Major government contract windfall; benefiting from Anthropic exclusion",
        market_position="Stepping into Anthropic's government gap; dominant consumer"
    ),
    "Microsoft": AICompanyStatus(
        name="Microsoft",
        government_relationship="ALLY",
        dod_access=True,
        key_event="Keeping Anthropic for non-DoD work; fully compliant with Pentagon on DoD",
        commercial_impact="Can separate Claude usage: civilian OK, DoD excluded",
        market_position="Straddling both sides pragmatically"
    ),
    "Google": AICompanyStatus(
        name="Google",
        government_relationship="NEUTRAL",
        dod_access=True,
        key_event="Not in current story; watching from sidelines",
        commercial_impact="No immediate impact; may benefit from Anthropic weakness",
        market_position="Strong government presence via Google Cloud"
    )
}

EVENTS = [
    AIConflictEvent(
        date="2026-03-04",
        actor="US DoD",
        action="Threatened Anthropic with deadline on AI safeguards",
        impact="Negotiations started",
        severity="HIGH",
        source="BBC"
    ),
    AIConflictEvent(
        date="2026-03-05",
        actor="Trump",
        action="Truth Social: ordered all federal agencies to stop using Anthropic",
        impact="Stock/commercial concern; negotiations break down",
        severity="CRITICAL",
        source="BBC/Reuters"
    ),
    AIConflictEvent(
        date="2026-03-06",
        actor="Pentagon",
        action="Official supply chain risk designation - effective immediately",
        impact="Anthropic banned from all DoD contractor use",
        severity="CRITICAL",
        source="BBC"
    ),
    AIConflictEvent(
        date="2026-03-06",
        actor="Anthropic/Amodei",
        action="Announced lawsuit challenging supply chain risk designation",
        impact="Legal battle begins; 'not legally sound'",
        severity="HIGH",
        source="BBC"
    ),
    AIConflictEvent(
        date="2026-03-06",
        actor="OpenAI/Altman",
        action="New DoD contract signed; 'more guardrails than any previous'",
        impact="OpenAI wins government market; Anthropic loses",
        severity="HIGH",
        source="BBC"
    ),
]

def print_status_report():
    print("=" * 70)
    print("AI GOVERNANCE CONFLICT TRACKER")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)
    
    print("\n📊 COMPANY STATUS")
    print("-" * 70)
    for name, co in COMPANIES.items():
        status_emoji = {"HOSTILE": "🔴", "ALLY": "🟢", "NEUTRAL": "🟡", "BANNED": "⛔"}.get(co.government_relationship, "⚪")
        dod = "✅" if co.dod_access else "❌"
        print(f"\n{status_emoji} {name} (DoD Access: {dod})")
        print(f"   Government: {co.government_relationship}")
        print(f"   Key Event: {co.key_event}")
        print(f"   Commercial: {co.commercial_impact}")
    
    print("\n\n📅 TIMELINE")
    print("-" * 70)
    for event in sorted(EVENTS, key=lambda e: e.date):
        sev_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "⚪"}.get(event.severity, "⚪")
        print(f"{sev_emoji} [{event.date}] {event.actor}: {event.action}")
        print(f"   → Impact: {event.impact}")
    
    print("\n\n🔮 ANALYSIS")
    print("-" * 70)
    print("""
ROOT CAUSE: Anthropic refused to allow DoD unfettered access to Claude for:
  1. Mass surveillance operations
  2. Autonomous weapons systems
  
This put Anthropic on a collision course with an administration that demands
full military compliance from contractors.

ANTHROPIC'S POSITION:
  - "Responsible AI" = maintaining usage policies even for government
  - Dario Amodei: "We will not allow our tools to harm civilians"
  - Result: Designated enemy of the military-industrial complex

OPENAI'S POSITION:
  - "More guardrails" = marketing spin; Altman close to Trump circle
  - Donated to/praised Trump personally
  - Willing to sign contracts Anthropic won't sign

LONG-TERM IMPLICATIONS:
  1. AI governance split: "safety-first" vs "military-compliant" companies
  2. Anthropic maintains commercial momentum (1M daily signups)
  3. OpenAI risks reputation with safety community
  4. European/Asian markets may PREFER Anthropic (no DoD stigma)
  5. Senator Gillibrand (D): "A gift to our adversaries" — bipartisan concern

PREDICTION UPDATE:
  AI_ANTHROPIC_COMMERCIAL: 75% → Confirmed escalating; revenue at risk from federal
  AI_OPENAI_GOVERNMENT_WIN: NEW 80% — already materializing
  AI_SAFETY_GOVERNANCE_CRISIS: NEW 70% — precedent set for military coercion of AI companies
""")

def export_json():
    return {
        "timestamp": datetime.now().isoformat(),
        "companies": {k: vars(v) for k, v in COMPANIES.items()},
        "events": [vars(e) for e in EVENTS],
        "key_prediction": "OpenAI wins government, Anthropic wins commercial/global",
        "risk_level": "HIGH"
    }

if __name__ == "__main__":
    print_status_report()
    
    # Save JSON
    with open("ai_governance_state.json", "w") as f:
        json.dump(export_json(), f, indent=2)
    print("\n✅ Saved ai_governance_state.json")
