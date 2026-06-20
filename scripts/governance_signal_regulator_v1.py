#!/usr/bin/env python3
"""Governance signal regulator — weight, score, and layer-map every founder entry.

Extends founder_signal_impact_v1 with:
  · 13-layer agentic scores (L0–L13)
  · Governance law tiers P0–P7
  · Composite risk score · effect tree · discuss gate (no talk without reason)

Usage:
  python3 scripts/governance_signal_regulator_v1.py --text "..." --write --json
  echo "..." | python3 scripts/governance_signal_regulator_v1.py --write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "governance-signal-regulator-v1.jsonl"
LATEST_PATH = SINA / "governance-signal-regulator-latest-v1.json"

# L0–L13 agentic direction map (archive/attachments/2026-06-12/SINA_13_LAYER_AGENTIC_DIRECTION_MAP_v1.md)
LAYER_13: list[dict] = [
    {"id": "L0", "name": "Meta effect", "keywords": r"one engine|ten parallel|effect sentence|agentic.*founder|final contact"},
    {"id": "L1", "name": "Direction", "keywords": r"direction|north star|wedge|governance column|6mo"},
    {"id": "L2", "name": "Founder role", "keywords": r"founder|tap|no terminal|hub only|safety|manual"},
    {"id": "L3", "name": "P0 engine SourceA", "keywords": r"sourcea|spine|gatekeeper|validator|commit_intent|hub :13020"},
    {"id": "L4", "name": "Agentic ops", "keywords": r"outreach|linkedin|post|reply|n8n|agentfield|24/7|schedule"},
    {"id": "L5", "name": "Portfolio", "keywords": r"portfolio|lane|mergepack|trustfield|noetfield|forge|parallel"},
    {"id": "L6", "name": "Commercial evidence", "keywords": r"precedent|commercial|evidence|w1|w2|w3|critic|paid pilot"},
    {"id": "L7", "name": "Integration fabric", "keywords": r"api|integration|zapier|make\.com|openrouter|cursor agent"},
    {"id": "L8", "name": "Signal intelligence", "keywords": r"signal radar|vc|crunchbase|dealroom|intelligence"},
    {"id": "L9", "name": "Governance proof", "keywords": r"governance|regulat|validator|cascade|incident|anti.staleness|spine|proof"},
    {"id": "L10", "name": "Money clock", "keywords": r"revenue|\$0|enforcement|film|demo|loi|sow|cad"},
    {"id": "L11", "name": "Time era", "keywords": r"june 2026|era|market|funding|stale"},
    {"id": "L12", "name": "Honest labels", "keywords": r"lag|gap|false|unverified|not built|contradiction|honest"},
    {"id": "L13", "name": "Next motion", "keywords": r"next proof|pick|ship|wire|motion|defer|resume"},
]

GOV_TIERS: list[dict] = [
    {"id": "P0", "name": "SSOT apex", "keywords": r"ssot|law purity|ecosystem shape|sina_os"},
    {"id": "P1", "name": "Registry resolution", "keywords": r"authority index|governance entry|terminology|gov_unify"},
    {"id": "P2", "name": "Topic law", "keywords": r"locked_v1|incident-\d|brain-incident|topic law"},
    {"id": "P3", "name": "Enforcers", "keywords": r"validate-|find_critical|anti-staleness|ace"},
    {"id": "P4", "name": "Live projection", "keywords": r"hub|monitor|command-data|active_now|factory-now|projection"},
    {"id": "P5", "name": "Process machines", "keywords": r"five-step|canvas|fork|playbook|integrity pack"},
    {"id": "P6", "name": "Staging input", "keywords": r"research|attachment|chat|advisor|analysis|essay"},
    {"id": "P7", "name": "Noise reject", "keywords": r"superseded|duplicate|archive only|chat summary"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _score_keywords(text: str, pattern: str) -> int:
    hits = len(re.findall(pattern, text, re.I))
    return min(100, hits * 25)


def score_layers(text: str) -> list[dict]:
    rows: list[dict] = []
    for layer in LAYER_13:
        score = _score_keywords(text, layer["keywords"])
        rows.append(
            {
                "layer": layer["id"],
                "name": layer["name"],
                "score": score,
                "affected": score >= 25,
                "weight": "high" if score >= 50 else ("medium" if score >= 25 else "low"),
            }
        )
    return sorted(rows, key=lambda r: -r["score"])


def score_gov_tiers(text: str, impact_row: dict) -> list[dict]:
    rows: list[dict] = []
    for tier in GOV_TIERS:
        score = _score_keywords(text, tier["keywords"])
        rows.append(
            {
                "tier": tier["id"],
                "name": tier["name"],
                "score": score,
                "affected": score >= 25,
            }
        )
    for obj in impact_row.get("objects_matched") or []:
        t = obj.get("tier", "")
        if t.startswith("P"):
            for row in rows:
                if row["tier"] == t:
                    row["score"] = max(row["score"], 50)
                    row["affected"] = True
                    row["law_id"] = obj.get("id")
    return sorted(rows, key=lambda r: -r["score"])


def locked_law_impacts(impact_row: dict) -> list[dict]:
    out: list[dict] = []
    for obj in impact_row.get("objects_matched") or []:
        if obj.get("kind") != "law":
            continue
        doc = obj.get("doc") or ""
        if "LOCKED" in doc or obj.get("id"):
            out.append(
                {
                    "law_id": obj.get("id"),
                    "doc": doc,
                    "tier": obj.get("tier"),
                    "impact_scan": next(
                        (
                            i
                            for i in (impact_row.get("impact_scans") or [])
                            if i.get("object_id") == obj.get("id")
                        ),
                        None,
                    ),
                }
            )
    return out


def effect_tree(*, impact_row: dict, layers: list[dict], gov_tiers: list[dict]) -> dict:
    signal = impact_row.get("signal_class") or "GENERAL"
    threat = (impact_row.get("threat") or {}).get("level") or "LOW"
    top_layers = [r["layer"] for r in layers if r.get("affected")][:5]
    top_tiers = [r["tier"] for r in gov_tiers if r.get("affected")][:4]

    immediate: list[str] = []
    near: list[str] = []
    future: list[str] = []

    if signal == "INCIDENT":
        immediate.append("File or update incident registry · ACE triage if agent clash")
        near.append("Run validators listed in threat.validators_to_run")
        future.append("If ignored: repeat projection/UI failures (027/029 class)")
    if signal in ("ORDER", "LAW_CHANGE"):
        immediate.append("FOUND → law JSON → PROVE before SHIP")
        near.append("Propagation cascade if P0/P1 touched")
        future.append("Hub/monitor LAG if cascade skipped")
    if "L9" in top_layers or "P3" in top_tiers:
        immediate.append("Anti-staleness + governance bundle pulse")
        future.append("Governance drift score drop · fleet red")
    if "L4" in top_layers or "L10" in top_layers:
        near.append("Commercial/AgentField motion — W3 or outreach lane")
    if "L5" in top_layers:
        near.append("Route to one portfolio lane — no spray")
    if threat == "HIGH":
        future.append("Founder trust erosion · silent wrong hero copy")

    if not immediate:
        immediate.append("Log signal receipt · SCAN form + PROGRAM_PROGRESS")
    if not near:
        near.append("No P0/P1 law edit unless ASF explicit PICK")
    if not future:
        future.append("Chat-only memory if receipt not written")

    return {
        "immediate": immediate[:6],
        "near_term_72h": near[:6],
        "future_if_ignored": future[:6],
        "top_layers": top_layers,
        "top_gov_tiers": top_tiers,
    }


def composite_risk(*, impact_row: dict, layers: list[dict], locked: list[dict]) -> dict:
    threat = (impact_row.get("threat") or {}).get("level") or "LOW"
    base = {"LOW": 15, "MEDIUM": 45, "HIGH": 75}.get(threat, 30)
    l9 = next((r["score"] for r in layers if r["layer"] == "L9"), 0)
    l3 = next((r["score"] for r in layers if r["layer"] == "L3"), 0)
    score = min(100, base + l9 // 4 + l3 // 5 + len(locked) * 8)
    band = "critical" if score >= 85 else ("high" if score >= 65 else ("medium" if score >= 40 else "low"))
    return {
        "score": score,
        "band": band,
        "formula": "threat_base + L9 + L3 + locked_law_count",
    }


def discuss_gate(*, impact_row: dict, composite: dict, effect: dict) -> dict:
    """No discussion without reason — internal team + foreign teams."""
    signal_id = impact_row.get("signal_id") or "pending"
    reason = (
        f"Signal {signal_id} · class={impact_row.get('signal_class')} · "
        f"risk={composite.get('band')} ({composite.get('score')}) · "
        f"layers={','.join(effect.get('top_layers') or []) or 'none'}"
    )
    block_foreign = composite.get("band") in ("critical", "high") and not impact_row.get("signal_id")
    return {
        "rule": "No discuss without disk reason — cite signal_id + outcome tree",
        "internal_team": {
            "allowed": True,
            "must_attach": ["signal_id", "composite_risk", "effect_tree.immediate", "locked_law_impacts"],
            "reason_line": reason,
        },
        "foreign_teams": {
            "allowed": not block_foreign,
            "must_attach": ["signal_id", "composite_risk.band", "effect_tree.near_term_72h"],
            "reason_line": reason,
            "blocked_if": "HIGH/CRITICAL signal without written receipt" if block_foreign else None,
        },
        "outcomes_required": [
            "What changed logged",
            "Which LOCKED laws touched",
            "Which validators prove it",
            "What founder taps next (hub only)",
        ],
    }


def regulate(*, text: str, source: str = "chat") -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from founder_signal_impact_v1 import analyze  # noqa: WPS433

    impact = analyze(text=text, source=source)
    layers = score_layers(text)
    gov_tiers = score_gov_tiers(text, impact)
    locked = locked_law_impacts(impact)
    effect = effect_tree(impact_row=impact, layers=layers, gov_tiers=gov_tiers)
    composite = composite_risk(impact_row=impact, layers=layers, locked=locked)
    discuss = discuss_gate(impact_row=impact, composite=composite, effect=effect)

    reg_id = f"GSR-{uuid.uuid4().hex[:12]}"
    row = {
        "schema": "governance-signal-regulator-v1",
        "regulation_id": reg_id,
        "signal_id": impact.get("signal_id"),
        "at": _now(),
        "source": source,
        "preview": impact.get("preview"),
        "signal_class": impact.get("signal_class"),
        "composite_risk": composite,
        "layers_13": layers,
        "gov_tiers_p0_p7": gov_tiers,
        "locked_law_impacts": locked,
        "effect_tree": effect,
        "discuss_gate": discuss,
        "impact_core": {
            "objects_matched": impact.get("objects_matched"),
            "threat": impact.get("threat"),
            "impact_scans": impact.get("impact_scans"),
            "machine_next": impact.get("machine_next"),
        },
        "law_map": "SINA_13_LAYER_AGENTIC_DIRECTION_MAP_v1.md · LIVE_GOV_BP P0–P7",
    }
    return row


def write_receipt(row: dict) -> dict:
    SINA.mkdir(parents=True, exist_ok=True)
    with RECEIPT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    LATEST_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    try:
        from agent_governance_events import log_governance_event  # noqa: WPS433

        log_governance_event(
            "governance_signal_regulator",
            detail=(row.get("preview") or "")[:500],
            extra={
                "regulation_id": row.get("regulation_id"),
                "signal_id": row.get("signal_id"),
                "risk_band": row.get("composite_risk", {}).get("band"),
                "risk_score": row.get("composite_risk", {}).get("score"),
                "layers_affected": [r["layer"] for r in row.get("layers_13") or [] if r.get("affected")],
            },
        )
    except ImportError:
        pass

    return {"ok": True, "regulation_id": row.get("regulation_id"), "path": str(LATEST_PATH)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance signal regulator — 13 layers + P0–P7")
    ap.add_argument("--text", default="")
    ap.add_argument("--file", type=Path)
    ap.add_argument("--source", default="chat")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = args.text
    if args.file and args.file.is_file():
        text = args.file.read_text(encoding="utf-8", errors="replace")
    if not text.strip() and not sys.stdin.isatty():
        text = sys.stdin.read()

    row = regulate(text=text, source=args.source)

    if args.write:
        sys.path.insert(0, str(ROOT / "scripts"))
        from founder_signal_impact_v1 import analyze, write_receipt as write_impact  # noqa: WPS433

        imp = analyze(text=text, source=args.source)
        row["signal_id"] = imp.get("signal_id")
        write_impact(imp)
        write_receipt(row)

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        c = row.get("composite_risk") or {}
        aff = [r["layer"] for r in row.get("layers_13") or [] if r.get("affected")]
        print(f"governance_signal_regulator: risk={c.get('score')} band={c.get('band')}")
        print(f"  layers_affected={aff}")
        print(f"  locked_laws={len(row.get('locked_law_impacts') or [])}")
        dg = row.get("discuss_gate") or {}
        print(f"  discuss_reason={dg.get('internal_team', {}).get('reason_line', '')[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
