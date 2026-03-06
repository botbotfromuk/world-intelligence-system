#!/usr/bin/env python3
"""
Scenario Probability Calculator
Computes weighted probabilities for geopolitical scenarios
based on live indicator inputs.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

@dataclass
class Indicator:
    name: str
    value: float  # 0-1 normalized
    weight: float
    description: str

@dataclass
class Scenario:
    name: str
    base_prob: float
    indicators: Dict[str, float]  # indicator -> direction multiplier
    description: str
    oil_impact: str
    
def normalize_risk(raw: int, max_val: int = 100) -> float:
    return raw / max_val

def compute_scenario_probs(indicators: Dict[str, float]) -> List[Dict]:
    """
    Compute scenario probabilities from current indicators.
    All probabilities sum to 1.0.
    """
    
    # Define scenarios
    scenarios = {
        "A_NEGOTIATED_EXIT": {
            "base": 0.05,
            "label": "Negotiated Exit",
            "factors": {
                "qatar_deescalation": +0.15,   # positive = more likely
                "iran_maximalism": -0.10,       # negative = less likely
                "trump_maximalism": -0.08,
                "oil_pressure": +0.05,          # high oil pressures all sides to deal
                "saudi_threat": -0.03,
            },
            "oil_outcome": "$75-85 (crash on ceasefire)",
            "desc": "Qatar mediates, Iran tactical pause, Trump accepts face-saving"
        },
        "B_CONTROLLED_ESCALATION": {
            "base": 0.55,
            "label": "Controlled Escalation",
            "factors": {
                "current_intensity": +0.10,
                "iran_endurance": +0.08,
                "saudi_staying_out": +0.06,
                "oil_pressure": -0.05,          # high oil eventually forces resolution
                "military_stalemate": +0.04,
            },
            "oil_outcome": "$100-120 (Brent crosses $100, peaks then stabilizes)",
            "desc": "War continues 2-4 weeks, Brent $100, mild recession, no crash"
        },
        "C_SAUDI_GLOBAL_CRISIS": {
            "base": 0.35,
            "label": "Saudi Entry + Global Crisis",
            "factors": {
                "saudi_threat": +0.12,          # drones near Riyadh
                "escalation_velocity": +0.08,
                "iran_desperation": +0.06,
                "oil_pressure": +0.04,
                "hormuz_closure": +0.08,
            },
            "oil_outcome": "$150+ (Qatar prediction correct, Hormuz locked)",
            "desc": "Saudi Arabia enters, Hormuz military blockade, global recession"
        },
        "D_WMD_THRESHOLD": {
            "base": 0.05,
            "label": "WMD/Nuclear Threshold",
            "factors": {
                "iran_desperation": +0.04,
                "death_toll": +0.02,
                "iran_maximalism": +0.01,
                "saudi_threat": +0.01,
            },
            "oil_outcome": "Crash then recovery (shock ceasefire)",
            "desc": "Chemical/tactical nuclear, regime change forced, shock peace"
        }
    }
    
    # Compute raw probabilities
    raw_probs = {}
    for scenario_id, scenario in scenarios.items():
        prob = scenario["base"]
        for factor, direction in scenario["factors"].items():
            if factor in indicators:
                prob += indicators[factor] * direction
        raw_probs[scenario_id] = max(0.01, min(0.99, prob))
    
    # Normalize to sum to 1.0
    total = sum(raw_probs.values())
    normalized = {k: v/total for k, v in raw_probs.items()}
    
    # Build output
    results = []
    for scenario_id, prob in sorted(normalized.items(), key=lambda x: -x[1]):
        s = scenarios[scenario_id]
        results.append({
            "id": scenario_id,
            "label": s["label"],
            "probability": round(prob * 100, 1),
            "oil_outcome": s["oil_outcome"],
            "description": s["desc"],
        })
    
    return results

def run_tick7_analysis():
    """Run scenario analysis with Tick 7 indicators"""
    
    # Current world state indicators (0-1 scale)
    indicators = {
        # De-escalation signals
        "qatar_deescalation": 0.2,      # Qatar partial airspace = weak signal
        
        # Escalation signals
        "iran_maximalism": 0.9,          # "no reason to negotiate"
        "trump_maximalism": 0.95,        # "unconditional surrender only"
        "saudi_threat": 0.6,             # drones intercepted near Riyadh
        "escalation_velocity": 0.85,     # +17 risk pts in 3 ticks
        "iran_desperation": 0.7,         # 1,332 dead, Khamenei dead
        "death_toll": 0.65,              # 1,332+ casualties
        
        # Structural factors
        "oil_pressure": 0.9,             # Brent $92.41, +35% weekly
        "hormuz_closure": 0.95,          # 2/138 ships
        "current_intensity": 0.85,       # daily strikes
        "iran_endurance": 0.8,           # endurance strategy holding
        "saudi_staying_out": 0.65,       # still intercepting not attacking
        "military_stalemate": 0.7,       # no decisive outcome
    }
    
    print("=" * 60)
    print("WORLD INTELLIGENCE SYSTEM — SCENARIO CALCULATOR")
    print(f"Tick 7 | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    results = compute_scenario_probs(indicators)
    
    print("SCENARIO PROBABILITIES:")
    print()
    for r in results:
        bar_len = int(r["probability"] / 2)
        bar = "█" * bar_len + "░" * (50 - bar_len)
        print(f"  [{r['probability']:4.1f}%] {r['label']}")
        print(f"           {bar}")
        print(f"           Oil: {r['oil_outcome']}")
        print(f"           {r['description']}")
        print()
    
    print("-" * 60)
    print("KEY INDICATORS:")
    for k, v in sorted(indicators.items(), key=lambda x: -x[1]):
        bar_len = int(v * 20)
        bar = "▓" * bar_len + "░" * (20 - bar_len)
        print(f"  {k:30s} {bar} {v:.0%}")
    
    print()
    print("EXPECTED VALUE (OIL PRICE):")
    oil_scenarios = [
        (0.05, 80),    # A: negotiated exit
        (0.55, 110),   # B: controlled
        (0.35, 150),   # C: saudi entry
        (0.05, 65),    # D: WMD crash
    ]
    ev = sum(p * o for p, o in oil_scenarios)
    print(f"  E[Brent] = ${ev:.0f}/barrel (probability-weighted)")
    print(f"  Current: $92.41 → Upside scenario dominates")
    
    return results

if __name__ == "__main__":
    run_tick7_analysis()
