#!/usr/bin/env python3
"""SSOT: honest REGISTRY done = receipt logged with DONE-class status only."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from closeout_audit_lib_v1 import HONEST_RECEIPT  # noqa: E402

RECEIPT_RE = re.compile(r"^sa-\d{4}-receipt\.json$")


def honest_receipt_ids() -> set[str]:
    """sa_ids with sa-XXXX-receipt.json and honest status."""
    out: set[str] = set()
    rec_dir = ROOT / "receipts"
    if not rec_dir.is_dir():
        return out
    for p in rec_dir.glob("sa-*-receipt.json"):
        if not RECEIPT_RE.match(p.name):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if str(d.get("status") or "").upper() in HONEST_RECEIPT:
            sa = str(d.get("sa_id") or p.stem.replace("-receipt", ""))
            if sa.startswith("sa-"):
                out.add(sa)
    return out


def audit_registry_done() -> dict:
    """Compare REGISTRY done rows vs receipt files locally (SSOT).

    Honest done = registry status done AND ``receipts/sa-XXXX-receipt.json`` with
    DONE-class status. YAML closeouts alone never count toward monitor progress.
    """
    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = reg.get("plans") or []

    raw_done: list[str] = []
    honest_done: list[str] = []
    unproven_done: list[str] = []

    receipt_ids = honest_receipt_ids()

    for pl in plans:
        sa = pl.get("id") or ""
        st = pl.get("status") or ""
        if st != "done":
            continue
        raw_done.append(sa)
        # Permanent law: receipt file is the only honest progress marker.
        if sa in receipt_ids:
            honest_done.append(sa)
        else:
            unproven_done.append(sa)

    total = len(plans) or 1000
    return {
        "ok": len(unproven_done) == 0,
        "total": total,
        "raw_done": len(raw_done),
        "honest_done": len(honest_done),
        "unproven_done": len(unproven_done),
        "receipt_file_count": len(receipt_ids),
        "yaml_only_done": len([sa for sa in raw_done if sa not in receipt_ids]),
        "drift": len(raw_done) != len(honest_done),
        "raw_done_ids": raw_done,
        "honest_done_ids": honest_done,
        "unproven_done_ids": unproven_done,
        "law": "REGISTRY done requires receipts/sa-XXXX-receipt.json — no YAML-only inflate",
    }


def enforce_honest_registry(*, dry_run: bool = False) -> dict:
    """Auto-revert any done row without honest proof (runs on hub build)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "revert_unproven",
        ROOT / "scripts" / "revert-unproven-registry-done-v1.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    revert = mod.revert

    before = audit_registry_done()
    if before["unproven_done"] == 0:
        return {"ok": True, "enforced": False, "reason": "already_honest", **before}
    rev = revert(dry_run=dry_run)
    after = audit_registry_done()
    return {
        "ok": after["unproven_done"] == 0,
        "enforced": True,
        "dry_run": dry_run,
        "reverted_count": rev.get("reverted_count", 0),
        "before": before,
        "after": after,
    }
