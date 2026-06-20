#!/usr/bin/env python3
"""Shared proof audit helpers for REGISTRY closeout validation."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"
LOGS = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"

HONEST_RECEIPT = frozenset({"DONE", "PASS", "VERIFIED", "CHECK_PASSED"})


def load_receipts() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not RECEIPTS.is_dir():
        return out
    for p in RECEIPTS.glob("sa-*-receipt.json"):
        m = re.match(r"(sa-\d+)", p.name)
        if not m:
            continue
        sa = m.group(1)
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            d = {}
        out[sa] = {
            "receipt_status": str(d.get("status") or ""),
            "receipt_at": str(d.get("at") or ""),
            "receipt_path": str(p),
        }
    return out


def load_closeouts() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not LOGS.is_dir():
        return out
    for p in sorted(LOGS.glob("*.yaml")):
        if "plan-with-no-asf" not in p.name:
            continue
        if "QUARANTINE_BATCH_YAML" in str(p):
            continue
        m = re.search(r"(sa-\d+)", p.name)
        if not m:
            continue
        sa = m.group(1)
        text = p.read_text(encoding="utf-8")
        rep = re.search(r"reporter: (\S+)", text)
        sn = re.search(r"output_snippet: (.+)", text)
        at = re.search(r"reported_at: '([^']+)'", text)
        out[sa] = {
            "closeout_reporter": rep.group(1) if rep else "",
            "closeout_evidence": (sn.group(1).strip() if sn else "")[:200],
            "closeout_reported_at": at.group(1) if at else "",
        }
    return out


def proof_verdict(sa: str, registry_status: str, rec: dict | None, clo: dict | None) -> str:
    if registry_status != "done":
        return "BACKLOG"
    if rec and rec.get("receipt_status", "").upper() in HONEST_RECEIPT:
        if clo and clo.get("closeout_reporter") == "cursor-worker-batch":
            return "RECEIPT_AND_BATCH_YAML"
        return "HONEST_RECEIPT"
    if clo:
        rep = clo.get("closeout_reporter") or "unknown"
        if rep == "cursor-worker-batch":
            return "BATCH_CLOSEOUT_ONLY"
        if rep == "goal1_lane_broker":
            return "BROKER_YAML_ONLY"
        if rep == "cursor-worker":
            return "WORKER_YAML_ONLY"
        if rep == "cursor-maintainer":
            return "MAINTAINER_YAML_ONLY"
        return "YAML_ONLY_OTHER"
    return "DONE_NO_PROOF_ON_DISK"


def is_unproven_done(proof: str) -> bool:
    return proof in (
        "BATCH_CLOSEOUT_ONLY",
        "DONE_NO_PROOF_ON_DISK",
        "BROKER_YAML_ONLY",
        "WORKER_YAML_ONLY",
        "MAINTAINER_YAML_ONLY",
        "YAML_ONLY_OTHER",
    )
