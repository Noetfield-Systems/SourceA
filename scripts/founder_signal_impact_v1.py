#!/usr/bin/env python3
"""Founder signal intake → classify → authority match → impact scan → disk receipt.

Every ASF message (order, incident, analysis, law change) should pass through this
before agents SHIP. Closes the gap between chat and governance spine (INCIDENT-029 class).

Usage:
  python3 scripts/founder_signal_impact_v1.py --text "..." --write --json
  echo "..." | python3 scripts/founder_signal_impact_v1.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "founder-signal-impact-v1.jsonl"
LATEST_PATH = SINA / "founder-signal-impact-latest-v1.json"
AUTHORITY_INDEX = ROOT / "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
INCIDENT_REGISTRY = ROOT / "brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"

P0_IDS = frozenset({"SSOT", "LAW_PURITY", "SINA_OS_SSOT"})
P1_IDS = frozenset(
    {
        "AUTHORITY_INDEX",
        "GOVERNANCE_ENTRY",
        "TERMINOLOGY_DICT",
        "FOUNDER_DIRECTION_TERMS",
        "GOV_UNIFY_BATCH",
        "LIVE_GOV_BP",
        "GOV_EVENT_SPINE",
    }
)

SIGNAL_PATTERNS: list[tuple[str, str]] = [
    ("INCIDENT", r"incident[- ]?0?\d{2,3}|INCIDENT-\d+|what happened|ignored.*order|violated"),
    ("LAW_CHANGE", r"law change|new rule|LOCKED|supersed|authority row|governance.unif"),
    ("PICK", r"ASF:\s*FIVE-STEP|FIVE-STEP\s*—\s*PICK|Q-RT-LIVE|Q-1\.10"),
    ("ANALYSIS", r"analysis|insight|verdict|threat|danger|risk|impact|affect"),
    ("ORDER", r"must|have to|bring the|fix now|check this|do whatever|ship|wire"),
    ("STATUS", r"said:|report holds|PASS|GREEN|verified|in the repository"),
]

PHRASE_TO_LAW: list[tuple[str, str, str]] = [
    (r"zero governance latency", "LIVE_GOV_BP", "P1"),
    (r"governance.level|governance-level|governance system", "GOV_EVENT_SPINE", "P1"),
    (r"anti.staleness", "ANTI_STALENESS", "P3"),
    (r"live form|founder form|canvas", "LIVE_DECISION_FORM", "P5"),
    (r"authority index", "AUTHORITY_INDEX", "P1"),
    (r"propagation cascade", "LIVE_GOV_BP", "P1"),
    (r"external.critic|FR-003", "CRITIC", "P2"),
]

RISK_KEYWORDS = (
    "danger",
    "threat",
    "risk",
    "ignore",
    "stale",
    "violate",
    "wrong",
    "false",
    "gap",
    "latency",
    "conflict",
    "law",
    "incident",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _load_authority_rows() -> list[dict]:
    if not AUTHORITY_INDEX.is_file():
        return []
    rows: list[dict] = []
    for line in AUTHORITY_INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("| `"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4 or parts[1] in ("ID", "----"):
            continue
        rid = parts[1].strip("` ")
        doc = parts[2].strip("` ")
        if not rid or rid == "ID":
            continue
        rows.append({"id": rid, "doc": doc})
    return rows


def _tier_for_row(row_id: str) -> str:
    if row_id in P0_IDS or row_id.startswith("SINA_OS"):
        return "P0"
    if row_id in P1_IDS:
        return "P1"
    if row_id.startswith("INCIDENT") or "INCIDENT" in row_id:
        return "P2"
    if row_id.startswith("VALIDATE") or "VALIDATOR" in row_id:
        return "P3"
    if row_id in ("LIVE_DECISION_FORM", "FIVE_STEP", "SYS_INTEGRITY_100"):
        return "P5"
    return "P2"


def classify_signal(text: str) -> str:
    low = (text or "").strip().lower()
    if not low:
        return "EMPTY"
    hits: list[str] = []
    for label, pat in SIGNAL_PATTERNS:
        if re.search(pat, text, re.I):
            hits.append(label)
    if "PICK" in hits:
        return "PICK"
    if "INCIDENT" in hits:
        return "INCIDENT"
    if "LAW_CHANGE" in hits:
        return "LAW_CHANGE"
    if "ORDER" in hits:
        return "ORDER"
    if "ANALYSIS" in hits:
        return "ANALYSIS"
    if "STATUS" in hits:
        return "STATUS"
    try:
        from factory_control_v1 import classify_founder_message  # noqa: WPS433

        fc = classify_founder_message(text)
        if fc == "ASF_STOP":
            return "ORDER"
        if fc == "ASF_ORDER":
            return "ORDER"
    except ImportError:
        pass
    return "GENERAL"


def match_objects(text: str, authority_rows: list[dict]) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()

    for m in re.finditer(r"INCIDENT-0?(\d{2,3})", text, re.I):
        iid = f"INCIDENT-{int(m.group(1)):03d}"
        if iid not in seen:
            seen.add(iid)
            found.append({"kind": "incident", "id": iid, "tier": "P2"})

    for m in re.finditer(r"FR-\d{4}-\d{2}-\d{2}-[a-f0-9]+", text, re.I):
        fid = m.group(0).upper()
        if fid not in seen:
            seen.add(fid)
            found.append({"kind": "founder_request", "id": fid, "tier": "P1"})

    for m in re.finditer(r"\b(\d{1,2}\.\d{2})\b", text):
        step = m.group(1)
        if step not in seen:
            seen.add(step)
            found.append({"kind": "integrity_step", "id": step, "tier": "P5"})

    low = text.lower()
    for row in authority_rows:
        rid = row["id"]
        doc = (row.get("doc") or "").lower()
        tokens = [rid.lower().replace("_", " "), rid.lower(), doc.replace("_", " ")]
        if any(t and len(t) > 4 and t in low for t in tokens):
            if rid not in seen:
                seen.add(rid)
                found.append({"kind": "law", "id": rid, "tier": _tier_for_row(rid), "doc": row.get("doc")})

    for pat, rid, tier in PHRASE_TO_LAW:
        if re.search(pat, text, re.I) and rid not in seen:
            seen.add(rid)
            doc = next((r.get("doc") for r in authority_rows if r["id"] == rid), "")
            found.append({"kind": "law", "id": rid, "tier": tier, "doc": doc, "match": "phrase"})

    for m in re.finditer(r"`([A-Z][A-Z0-9_]{3,})`", text):
        tok = m.group(1)
        if tok not in seen:
            row = next((r for r in authority_rows if r["id"] == tok), None)
            if row:
                seen.add(tok)
                found.append(
                    {"kind": "law", "id": tok, "tier": _tier_for_row(tok), "doc": row.get("doc")}
                )

    return found[:24]


def _impact_for_objects(objects: list[dict]) -> list[dict]:
    impacts: list[dict] = []
    try:
        from governance_reference_graph_v1 import impact_scan  # noqa: WPS433
    except ImportError:
        return impacts
    for obj in objects:
        if obj.get("kind") != "law":
            continue
        oid = obj["id"]
        row = impact_scan(object_id=oid)
        if row.get("ok"):
            impacts.append({"object_id": oid, "affected": row.get("affected", {})})
    return impacts


def assess_threat(*, signal_class: str, text: str, objects: list[dict], impacts: list[dict]) -> dict:
    low = text.lower()
    risk_hits = [k for k in RISK_KEYWORDS if k in low]
    tiers = {o.get("tier") for o in objects if o.get("tier")}
    has_p0 = "P0" in tiers
    has_p1 = "P1" in tiers
    open_incident = any(o.get("kind") == "incident" for o in objects)

    level = "LOW"
    if signal_class in ("INCIDENT", "LAW_CHANGE") or has_p0:
        level = "HIGH"
    elif signal_class == "ORDER" and (len(risk_hits) >= 2 or has_p1):
        level = "HIGH"
    elif has_p1 or open_incident or len(risk_hits) >= 3:
        level = "MEDIUM"
    elif signal_class in ("ORDER", "ANALYSIS") or risk_hits:
        level = "MEDIUM"

    cascade = False
    reasons: list[str] = []
    if signal_class == "LAW_CHANGE" or has_p0 or has_p1:
        cascade = True
        reasons.append("P0/P1 touch or law-change class → governance_propagation_cascade")
    if signal_class == "PICK":
        cascade = True
        reasons.append("Founder PICK → cascade reason=founder_pick")
    if signal_class == "ORDER" and ("governance" in low or "machine" in low) and has_p1:
        cascade = True
        reasons.append("Governance machinery order touching P1 → cascade after SHIP")
    if signal_class == "INCIDENT" and level in ("HIGH", "MEDIUM"):
        reasons.append("Incident signal → registry + spine; ACE if agent clash")
    if "projection" in low or "sidebar" in low or "stale" in low:
        reasons.append("Projection/UI lag class (INCIDENT-027/029) → hub align + form JSON before hero")

    validators: list[str] = ["validate-anti-staleness-bundle-v1.sh"]
    if impacts:
        for imp in impacts:
            for v in imp.get("affected", {}).get("validators") or []:
                if v not in validators:
                    validators.append(v)
    if signal_class == "INCIDENT":
        validators.append("validate-incident-registry-ids-v1.sh")
    if "form" in low or "canvas" in low:
        validators.append("validate-live-founder-decision-form-v1.sh")

    return {
        "level": level,
        "risk_keywords": risk_hits[:12],
        "tiers_touched": sorted(tiers),
        "cascade_recommended": cascade,
        "cascade_reasons": reasons,
        "validators_to_run": validators[:8],
        "ace_recommended": signal_class == "INCIDENT" or "conflict" in low,
    }


def analyze(*, text: str, source: str = "chat") -> dict:
    authority_rows = _load_authority_rows()
    signal_class = classify_signal(text)
    objects = match_objects(text, authority_rows)
    impacts = _impact_for_objects(objects)
    threat = assess_threat(signal_class=signal_class, text=text, objects=objects, impacts=impacts)

    sid = f"FSI-{uuid.uuid4().hex[:12]}"
    row = {
        "schema": "founder-signal-impact-v1",
        "signal_id": sid,
        "at": _now(),
        "source": source,
        "signal_class": signal_class,
        "preview": (text or "")[:400],
        "checksum": _checksum(text or ""),
        "objects_matched": objects,
        "impact_scans": impacts,
        "threat": threat,
        "machine_next": {
            "read_first": [
                "live_founder_decision_form_v1.py --json",
                "PROGRAM_PROGRESS.json",
                "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md",
            ],
            "never": ["chat-only law", "sidebar success without compile proof", "leaf→thorn inversion"],
        },
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
            "founder_signal_impact",
            detail=row.get("preview", "")[:500],
            extra={
                "signal_id": row.get("signal_id"),
                "signal_class": row.get("signal_class"),
                "threat_level": row.get("threat", {}).get("level"),
                "cascade_recommended": row.get("threat", {}).get("cascade_recommended"),
            },
        )
    except ImportError:
        pass

    try:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        affected = [o["id"] for o in row.get("objects_matched") or [] if o.get("id")]
        for imp in row.get("impact_scans") or []:
            for obj in imp.get("affected", {}).get("objects") or []:
                if obj not in affected:
                    affected.append(obj)
        append_event(
            event_type="FOUNDER_SIGNAL",
            object_id=row.get("signal_id") or "founder-signal",
            object_kind="system",
            agent_id="founder",
            correlation_id=row.get("signal_id"),
            payload={
                "signal_class": row.get("signal_class"),
                "threat": row.get("threat"),
                "preview": row.get("preview"),
            },
            gate="founder_signal_impact_v1",
            proof=str(LATEST_PATH),
            affected_objects=affected[:32],
            validator_set=row.get("threat", {}).get("validators_to_run"),
        )
    except ImportError:
        pass

    return {"ok": True, "signal_id": row.get("signal_id"), "path": str(LATEST_PATH)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder signal → governance impact analysis")
    ap.add_argument("--text", default="", help="Founder message body")
    ap.add_argument("--file", type=Path, help="Read message from file")
    ap.add_argument("--source", default="chat", help="chat · hub · track")
    ap.add_argument("--write", action="store_true", help="Append jsonl + spine + governance log")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = args.text
    if args.file and args.file.is_file():
        text = args.file.read_text(encoding="utf-8", errors="replace")
    if not text.strip() and not sys.stdin.isatty():
        text = sys.stdin.read()

    row = analyze(text=text, source=args.source)
    if args.write:
        write_receipt(row)

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        t = row.get("threat") or {}
        print(f"founder_signal_impact: class={row.get('signal_class')} threat={t.get('level')}")
        print(f"  objects={len(row.get('objects_matched') or [])} cascade={t.get('cascade_recommended')}")
        if t.get("cascade_reasons"):
            for r in t["cascade_reasons"][:4]:
                print(f"  → {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
