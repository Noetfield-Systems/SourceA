#!/usr/bin/env python3
"""NewMatch T0 situation router — deterministic rules · $0 · cloud-ready contract.

Law: data/newmatch-graph-schema-v1.json · data/newmatch-factory-v1.json
Usage:
  python3 scripts/newmatch_situation_router_t0_v1.py --json
  python3 scripts/newmatch_situation_router_t0_v1.py --stdin-json --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data" / "newmatch-graph-schema-v1.json"

RED_FLAGS = re.compile(
    r"\b(scam|wire transfer|urgent money|crypto pump|send \$|western union)\b",
    re.I,
)
BUSINESS = re.compile(
    r"\b(partnership|invest|fundraise|msb|compliance|agency|consult|pilot|demo|saas|revenue)\b",
    re.I,
)
DATING = re.compile(r"\b(match|hinge|bumble|tinder|coffee|date|mutual like)\b", re.I)
PROFESSIONAL = re.compile(r"\b(linkedin|inmail|founder|ceo|cto|board|advisor|hire)\b", re.I)
FOUNDER_GATE = re.compile(r"\b(contract|legal|publish|invoice|payment|nda|sign)\b", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _signal_text(signals: list[dict]) -> str:
    parts: list[str] = []
    for s in signals:
        parts.append(str(s.get("raw_text_redacted") or s.get("text") or ""))
        parts.append(str(s.get("kind") or ""))
        parts.append(str(s.get("source_app") or ""))
    return " ".join(parts)


def route(payload: dict) -> dict:
    schema = _load_schema()
    signals = payload.get("signals") or []
    text = _signal_text(signals)
    stale_days = int(payload.get("stale_days") or 0)
    kinds = {str(s.get("kind") or "") for s in signals}

    if RED_FLAGS.search(text):
        return _result("block", 0.92, "red_flag_keyword", schema)

    if FOUNDER_GATE.search(text) or payload.get("founder_gate"):
        return _result("founder_gate", 0.88, "founder_gate_trigger", schema)

    business_hits = len(BUSINESS.findall(text))
    dating_hit = bool(DATING.search(text)) or "dating_mutual_like" in kinds or "dating_message" in kinds
    prof_hit = bool(PROFESSIONAL.search(text)) or "linkedin_connection" in kinds

    if business_hits >= 2:
        return _result("business_opportunity", min(0.95, 0.7 + business_hits * 0.05), "business_signals", schema)

    if dating_hit and prof_hit:
        return _result("hybrid_explore", 0.72, "dating_professional_overlap", schema)

    if dating_hit and business_hits == 0:
        return _result("personal_nurture", 0.68, "dating_no_business", schema)

    if stale_days >= 30:
        return _result("defer", 0.8, "stale_30d", schema)

    return _result("hybrid_explore", 0.45, "ambiguous_t1_candidate", schema, t1_hint=True)


def _result(
    route_name: str,
    confidence: float,
    reason: str,
    schema: dict,
    *,
    t1_hint: bool = False,
) -> dict:
    routes = schema.get("entities", {}).get("situation", {}).get("routes", [])
    if route_name not in routes:
        route_name = "founder_gate"
    follow = {
        "personal_nurture": "Soft 7d cadence · no pitch",
        "hybrid_explore": "One clarifying question · founder approve",
        "business_opportunity": "Hand to NF-RD · TF-001 · SourceA SKU",
        "defer": "No auto ping until new signal",
        "block": "No contact",
        "founder_gate": "Hub form only",
    }
    out = {
        "ok": True,
        "route": route_name,
        "confidence": round(confidence, 3),
        "tier_used": "T0",
        "marginal_cost_usd": 0.0,
        "reason": reason,
        "follow_up_hint": follow.get(route_name, ""),
        "free_tier_first": True,
        "t1_fallback_recommended": t1_hint and confidence < 0.55,
        "blocker": None if route_name != "block" else "red_flag — no outbound",
        "saved_at": _now(),
        "schema": "newmatch-situation-router-t0-v1",
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--stdin-json", action="store_true")
    ap.add_argument("--demo", action="store_true", help="Run built-in demo cases")
    args = ap.parse_args()

    if args.demo:
        cases = [
            {"name": "dating", "signals": [{"kind": "dating_mutual_like", "raw_text_redacted": "mutual like on hinge"}]},
            {"name": "business", "signals": [{"raw_text_redacted": "partnership pilot for saas compliance demo"}]},
            {"name": "block", "signals": [{"raw_text_redacted": "urgent money wire transfer scam"}]},
        ]
        doc = {"ok": True, "demo": [{**route(c), "case": c["name"]} for c in cases]}
    elif args.stdin_json:
        payload = json.load(sys.stdin)
        doc = route(payload)
    else:
        doc = route({"signals": [{"kind": "manual_note", "raw_text_redacted": "coffee next week"}]})

    if args.json or args.demo or args.stdin_json:
        print(json.dumps(doc, indent=2))
    else:
        print(f"route={doc['route']} confidence={doc['confidence']} tier={doc['tier_used']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
