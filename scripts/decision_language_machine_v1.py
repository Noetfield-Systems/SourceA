#!/usr/bin/env python3
"""Decision Language Machine v1 — SourceA-local runtime consumer.

SG owns Dictionary · Terminology · language_gate · Library canon · meaning rules · doctrine.
SourceA consumes canon read-only; hardens local runtime only (fixtures · tests · receipts).

The form is test data. The machine is the deliverable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SSOT = ROOT / "data/decision-language-machine-v1.json"
FIXTURE_80 = ROOT / "data/decision-language-machine-form-official-fixture-v1.json"
RECEIPT_DIR = Path.home() / ".sina/decision-language-machine"

# Founder-approved FORM_OFFICIAL collapse fixture (80 → 22 mapped / 58 excluded). Shipped — do not resubmit.
FORM_OFFICIAL_22_MAPPED = [
    "Q-SESSION-FORM-BUILD",
    "Q-CHAT-LANG-01",
    "Q-CHAT-PLUSONE-01",
    "Q-MF-01",
    "Q-MF-02",
    "Q-MF-03",
    "Q-MF-04",
    "Q-MF-05",
    "Q-MF-06",
    "Q-MF-07",
    "Q-MF-08",
    "Q-MF-10",
    "Q-FINAL-01",
    "Q-FINAL-02",
    "Q-FINAL-03",
    "Q-FINAL-04",
    "Q-FINAL-05",
    "Q-FINAL-06",
    "Q-FINAL-07",
    "Q-SESSION-INBOX-NEXT",
    "Q-SESSION-CLOUD-CF06",
    "Q-THREAD-DEPLOY-01",
]

CLUSTER_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("CLUSTER-ENF-FILM", re.compile(r"^ENF-", re.I)),
    ("CLUSTER-SESSION-ARCH", re.compile(r"^Q-SESSION-ARCH", re.I)),
    ("CLUSTER-SESSION-FLOW", re.compile(r"^Q-SESSION-(FORM|GATHER|UNIFY|INBOX|CLOUD|PHASE|TUNNEL|WBC)", re.I)),
    ("CLUSTER-CHAT", re.compile(r"^Q-CHAT-", re.I)),
    ("CLUSTER-FINAL", re.compile(r"^Q-FINAL-", re.I)),
    ("CLUSTER-MF", re.compile(r"^Q-MF-", re.I)),
    ("CLUSTER-BC", re.compile(r"^Q-BC-", re.I)),
    ("CLUSTER-CONF", re.compile(r"^Q-CONF-", re.I)),
    ("CLUSTER-CW", re.compile(r"^Q-CW-", re.I)),
    ("CLUSTER-WBC", re.compile(r"^Q-WBC-", re.I)),
    ("CLUSTER-THREAD", re.compile(r"^Q-THREAD-", re.I)),
    ("CLUSTER-CANVAS", re.compile(r"^11\.", re.I)),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_receipt(stage: str, payload: dict[str, Any]) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPT_DIR / f"{stage}-receipt-v1.json"
    body = {"schema": "decision-language-machine-stage-receipt-v1", "stage": stage, "at": _now(), **payload}
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return path


def consume_sg_canon() -> dict[str, Any]:
    """Read-only SG canon consumption — SourceA never redefines these sources."""
    out: dict[str, Any] = {"authority": "SG", "mode": "read_only", "sources": {}}

    try:
        from founder_voice_terminology_v1 import canvas_terminology

        rows = canvas_terminology(max_rows=64)
        out["sources"]["terminology"] = {
            "consumer": "founder_voice_terminology_v1.canvas_terminology",
            "row_count": len(rows),
            "terms": {r["term"].lower(): r["sayInstead"] for r in rows if r.get("term")},
        }
    except Exception as exc:
        out["sources"]["terminology"] = {"error": str(exc), "terms": {}}

    try:
        from agent_report_language_gate_v1 import scan_text

        out["sources"]["language_gate"] = {
            "consumer": "agent_report_language_gate_v1.scan_text",
            "probe_ok": scan_text("plain English check", founder_asked_why=False).get("ok"),
        }
    except Exception as exc:
        out["sources"]["language_gate"] = {"error": str(exc)}

    out["law"] = "SG owns Dictionary · Terminology · language_gate · Library canon · meaning rules · doctrine"
    _write_receipt("sg_canon_consume", out)
    return out


def _sg_terminology_terms(canon: dict[str, Any]) -> dict[str, str]:
    return (canon.get("sources") or {}).get("terminology", {}).get("terms") or {}


def _plain_english(title: str, options: list[str] | None) -> str:
    """Rewrite to plain English — never inject recommended as authority."""
    t = (title or "").strip()
    t = re.sub(r"\s+", " ", t)
    if options:
        opts = [o.split("—")[0].strip() for o in options if o.strip()]
        if opts:
            t = f"{t} Options: {'; '.join(opts[:4])}."
    return t


def _extract_terms(text: str) -> list[str]:
    tokens = re.findall(r"[A-Z][A-Z0-9_-]{2,}|[A-Za-z]{4,}", text)
    seen: set[str] = set()
    out: list[str] = []
    for tok in tokens:
        key = tok.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(tok)
    return out[:24]


def _sg_canon_flags(plain: str, terms: list[str], terminology: dict[str, str]) -> list[str]:
    """Flag unclear language via SG terminology consumer only — no local banned lists."""
    flags: list[str] = []
    for term in terms:
        tl = term.lower()
        if tl in terminology:
            flags.append(f"SG_TERMINOLOGY:{term}→{terminology[tl][:80]}")
    try:
        from agent_report_language_gate_v1 import scan_text

        gate = scan_text(plain, founder_asked_why=False)
        if not gate.get("ok"):
            for hit in gate.get("hits") or []:
                flags.append(f"SG_LANGUAGE_GATE:{hit.get('id', 'hit')}")
    except Exception:
        pass
    return flags


def _cluster_id(row_id: str, row: dict[str, Any]) -> str:
    dup = row.get("duplicate_cluster")
    if dup:
        return str(dup)
    for cid, pat in CLUSTER_RULES:
        if pat.search(row_id):
            return cid
    return "CLUSTER-MISC"


def _classify(row: dict[str, Any], *, mapped: bool, sg_flags: list[str]) -> str:
    if sg_flags:
        return "DICTIONARY_FIX_NEEDED"
    if not mapped:
        return "DEFER"
    title = (row.get("title") or "").lower()
    tier = (row.get("gather_tier") or "").lower()
    if tier in {"p0_meta", "p0"} or row.get("id", "").startswith("Q-FINAL"):
        return "FOUNDER_FACT"
    if "confirm" in title or "accept" in title:
        return "MACHINE_VALIDATABLE"
    return "ADVISOR_REVIEW"


def _load_fixture_ids(fixture: str | None) -> set[str] | None:
    if fixture != "form_official_80" or not FIXTURE_80.is_file():
        return None
    data = json.loads(FIXTURE_80.read_text(encoding="utf-8"))
    mapped = set(data.get("mapped_ids") or [])
    excluded = set(data.get("excluded_ids") or [])
    return mapped | excluded


def ingest_rows(*, fixture: str | None = None) -> list[dict[str, Any]]:
    from live_founder_decision_form_v1 import all_open_questions

    live = {r["id"]: r for r in all_open_questions()}
    fixture_ids = _load_fixture_ids(fixture)
    if fixture_ids:
        rows = [live[i] for i in sorted(fixture_ids) if i in live]
        missing = sorted(fixture_ids - set(live))
        _write_receipt(
            "ingest",
            {
                "fixture": fixture,
                "count": len(fixture_ids),
                "live_matched": len(rows),
                "missing_shipped": missing,
                "ids": sorted(fixture_ids),
                "note": "missing_shipped = already answered in partial batch — fixture stub only",
            },
        )
        if missing:
            for mid in missing:
                rows.append(
                    {
                        "id": mid,
                        "title": mid,
                        "options": [],
                        "gather_tier": "fixture_stub_shipped",
                    }
                )
        rows.sort(key=lambda r: r["id"])
        return rows

    rows = list(live.values())
    _write_receipt("ingest", {"fixture": fixture or "live", "count": len(rows), "ids": [r["id"] for r in rows]})
    return rows


def run_pipeline(
    *,
    fixture: str = "form_official_80",
    write_apply: bool = False,
    allow_apply_map: bool = False,
) -> dict[str, Any]:
    canon = consume_sg_canon()
    terminology = _sg_terminology_terms(canon)
    raw_rows = ingest_rows(fixture=fixture)

    enriched: list[dict[str, Any]] = []
    for row in raw_rows:
        rid = row["id"]
        plain = _plain_english(row.get("title", ""), row.get("options"))
        terms = _extract_terms(f"{row.get('title', '')} {' '.join(row.get('options') or [])}")
        sg_flags = _sg_canon_flags(plain, terms, terminology)
        mapped = rid in FORM_OFFICIAL_22_MAPPED
        cluster = _cluster_id(rid, row)
        classification = _classify(row, mapped=mapped, sg_flags=sg_flags)
        enriched.append(
            {
                "id": rid,
                "plain_english": plain,
                "terms": terms,
                "sg_canon_flags": sg_flags,
                "cluster": cluster,
                "classification": classification,
                "mapped": mapped,
            }
        )

    _write_receipt("rewrite_plain_english", {"count": len(enriched), "sample": enriched[:3]})
    _write_receipt("extract_terms", {"count": len(enriched), "unique_terms": sorted({t for r in enriched for t in r["terms"]})[:40]})
    _write_receipt(
        "sg_canon_check",
        {
            "authority": "SG",
            "dictionary_fix_needed": sum(1 for r in enriched if r["classification"] == "DICTIONARY_FIX_NEEDED"),
            "terminology_terms_loaded": len(terminology),
        },
    )

    clusters: dict[str, list[str]] = defaultdict(list)
    for r in enriched:
        clusters[r["cluster"]].append(r["id"])
    _write_receipt("cluster", {"cluster_count": len(clusters), "clusters": dict(clusters)})

    by_class: dict[str, int] = defaultdict(int)
    for r in enriched:
        by_class[r["classification"]] += 1
    _write_receipt("classify", {"counts": dict(by_class)})

    mapped_rows = [r for r in enriched if r["mapped"]]
    excluded_rows = [r for r in enriched if not r["mapped"]]
    advisor = [r for r in mapped_rows if r["classification"] in {"ADVISOR_REVIEW", "MACHINE_VALIDATABLE"}]
    founder_facts = [r for r in mapped_rows if r["classification"] == "FOUNDER_FACT"]

    reduced = {
        "schema": "decision-language-machine-reduced-sheet-v1",
        "at": _now(),
        "authority_note": "Reduced sheet for review only — not submit authority",
        "advisor_decisions": [{"id": r["id"], "plain_english": r["plain_english"], "classification": r["classification"]} for r in advisor],
        "founder_facts": [{"id": r["id"], "plain_english": r["plain_english"]} for r in founder_facts],
        "deferred_summary": f"{len(excluded_rows)} rows excluded · do not resubmit",
    }
    reduced_path = RECEIPT_DIR / "reduced-sheet-v1.json"
    reduced_path.write_text(json.dumps(reduced, indent=2) + "\n", encoding="utf-8")
    _write_receipt("reduced_sheet", {"path": str(reduced_path), "advisor": len(advisor), "founder_facts": len(founder_facts)})

    apply_path = RECEIPT_DIR / "apply-map-v1.json"
    apply_written = False
    if allow_apply_map and write_apply:
        apply_map = {
            "schema": "decision-language-machine-apply-map-v1",
            "at": _now(),
            "fixture": fixture,
            "authority_note": "Founder explicit picks required — recommendations are not authority",
            "mapped_ids": FORM_OFFICIAL_22_MAPPED,
            "picks": {},
            "excluded_ids": [r["id"] for r in excluded_rows],
            "excluded_count": len(excluded_rows),
            "mapped_count": len(mapped_rows),
        }
        apply_path.write_text(json.dumps(apply_map, indent=2) + "\n", encoding="utf-8")
        apply_written = True
    _write_receipt(
        "apply_map",
        {
            "path": str(apply_path) if apply_written else None,
            "written": apply_written,
            "reason": "consume-only default — partial batch already shipped",
        },
    )

    summary = {
        "ok": True,
        "machine": "decision_language_machine_v1",
        "mode": "consume_only",
        "fixture": fixture,
        "raw_count": len(raw_rows),
        "cluster_count": len(clusters),
        "mapped_count": len(mapped_rows),
        "excluded_count": len(excluded_rows),
        "advisor_decisions": len(advisor),
        "founder_facts": len(founder_facts),
        "sg_canon_authority": "SG",
        "apply_map_written": apply_written,
        "reduced_sheet_path": str(reduced_path),
        "receipt_dir": str(RECEIPT_DIR),
    }
    final_path = RECEIPT_DIR / "pipeline-receipt-v1.json"
    final_path.write_text(json.dumps({"schema": "decision-language-machine-pipeline-receipt-v1", "at": _now(), **summary}, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Decision Language Machine v1 (SourceA consume-only runtime)")
    ap.add_argument("--fixture", default="form_official_80")
    ap.add_argument("--allow-apply-map", action="store_true", help="Write apply map skeleton (no picks — founder authority only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = run_pipeline(fixture=args.fixture, write_apply=args.allow_apply_map, allow_apply_map=args.allow_apply_map)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"DLM v1 consume: {result['raw_count']} raw → {result['cluster_count']} clusters → "
            f"{result['mapped_count']} mapped / {result['excluded_count']} excluded"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
