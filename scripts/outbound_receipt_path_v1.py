#!/usr/bin/env python3
"""Outbound execution receipt path SSOT — one file per upgrade+sa, not per sa alone.

Law: receipts/{upgrade_id}-{sa_id}-receipt.json (canonical)
Legacy: receipts/{sa_id}-receipt.json (read-only fallback during migration)
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"
LAW = "receipts/{upgrade_id}-{sa_id}-receipt.json"
LEGACY_LAW = "receipts/{sa_id}-receipt.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_receipt_rel(*, upgrade_id: str, sa_id: str) -> str:
    return f"receipts/{upgrade_id}-{sa_id}-receipt.json"


def legacy_receipt_rel(*, sa_id: str) -> str:
    return f"receipts/{sa_id}-receipt.json"


def canonical_receipt_path(*, upgrade_id: str, sa_id: str) -> Path:
    return RECEIPTS / f"{upgrade_id}-{sa_id}-receipt.json"


def legacy_receipt_path(*, sa_id: str) -> Path:
    return RECEIPTS / f"{sa_id}-receipt.json"


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def receipt_upgrade_matches(path: Path, upgrade_id: str) -> bool:
    row = _read_json(path)
    uid = str(row.get("upgrade_id") or (row.get("meta") or {}).get("upgrade_id") or "")
    return uid == upgrade_id


def resolve_receipt_file(*, upgrade_id: str, sa_id: str) -> tuple[Path | None, str]:
    """Return (path, rel_path) — canonical first, legacy only if upgrade_id matches."""
    if not upgrade_id or not sa_id:
        return None, ""
    canon = canonical_receipt_path(upgrade_id=upgrade_id, sa_id=sa_id)
    if canon.is_file():
        return canon, canonical_receipt_rel(upgrade_id=upgrade_id, sa_id=sa_id)
    legacy = legacy_receipt_path(sa_id=sa_id)
    if legacy.is_file() and receipt_upgrade_matches(legacy, upgrade_id):
        return legacy, legacy_receipt_rel(sa_id=sa_id)
    return None, ""


def receipt_exists(*, upgrade_id: str, sa_id: str) -> bool:
    path, _ = resolve_receipt_file(upgrade_id=upgrade_id, sa_id=sa_id)
    return path is not None


def receipt_done_exists(*, upgrade_id: str, sa_id: str) -> bool:
    """True only when canonical/legacy receipt exists AND status is DONE."""
    path, _ = resolve_receipt_file(upgrade_id=upgrade_id, sa_id=sa_id)
    if path is None:
        return False
    row = _read_json(path)
    return str(row.get("status") or "").upper() == "DONE"


def head_receipt_collision(*, upgrade_id: str, sa_id: str) -> dict:
    """Detect receipt overwrite risk. Canonical law makes legacy same-sa safe."""
    legacy = legacy_receipt_path(sa_id=sa_id)
    canon = canonical_receipt_path(upgrade_id=upgrade_id, sa_id=sa_id)
    if canon.is_file():
        row = _read_json(canon)
        existing_uid = str(row.get("upgrade_id") or "")
        if existing_uid and existing_uid != upgrade_id:
            return {
                "collision": True,
                "sa_id": sa_id,
                "head_upgrade_id": upgrade_id,
                "existing_upgrade_id": existing_uid,
                "canonical_path": canonical_receipt_rel(upgrade_id=upgrade_id, sa_id=sa_id),
                "risk": "canonical_upgrade_mismatch",
            }
        return {"collision": False, "canonical_exists": True}
    if not legacy.is_file():
        return {"collision": False}
    row = _read_json(legacy)
    existing_uid = str(row.get("upgrade_id") or "")
    if existing_uid and existing_uid != upgrade_id:
        return {
            "collision": False,
            "legacy_mismatch": True,
            "sa_id": sa_id,
            "head_upgrade_id": upgrade_id,
            "existing_upgrade_id": existing_uid,
            "legacy_path": legacy_receipt_rel(sa_id=sa_id),
            "safe_with_canonical_law": True,
        }
    return {"collision": False}


def write_receipt(
    *,
    upgrade_id: str,
    sa_id: str,
    title: str = "",
    evidence: str = "",
    extra: dict | None = None,
) -> dict:
    """Write canonical receipt — never overwrites a different upgrade's proof."""
    collision = head_receipt_collision(upgrade_id=upgrade_id, sa_id=sa_id)
    if collision.get("collision"):
        return {
            "ok": False,
            "error": "receipt_collision",
            "collision": collision,
            "hint": f"use {canonical_receipt_rel(upgrade_id=upgrade_id, sa_id=sa_id)}",
        }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    rel = canonical_receipt_rel(upgrade_id=upgrade_id, sa_id=sa_id)
    path = canonical_receipt_path(upgrade_id=upgrade_id, sa_id=sa_id)
    row = {
        "schema": "sourcea-sa-receipt-v1",
        "sa_id": sa_id,
        "status": "DONE",
        "round_type": "act",
        "upgrade_id": upgrade_id,
        "title": title or f"{upgrade_id} shipped",
        "evidence": evidence or f"{upgrade_id} acceptance verified logged",
        "receipt_law": LAW,
        "at": _now(),
        "workspace": str(ROOT),
    }
    if extra:
        row.update(extra)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(path), "receipt_path": rel, "upgrade_id": upgrade_id, "sa_id": sa_id}


def index_receipts_by_upgrade() -> dict[str, tuple[str, str]]:
    """upgrade_id -> (sa_id, receipt_path_rel)."""
    out: dict[str, tuple[str, str]] = {}
    if not RECEIPTS.is_dir():
        return out
    for p in RECEIPTS.glob("*-receipt.json"):
        row = _read_json(p)
        uid = str(row.get("upgrade_id") or (row.get("meta") or {}).get("upgrade_id") or "")
        if not uid:
            m = re.match(r"^(U\d+)-(sa-\d+)-receipt\.json$", p.name, re.I)
            if m:
                uid = m.group(1)
        if uid:
            sa = str(row.get("sa_id") or "")
            if not sa:
                m = re.match(r"^U\d+-(sa-\d+)-receipt\.json$", p.name, re.I)
                if m:
                    sa = m.group(1)
            try:
                rel = str(p.relative_to(ROOT))
            except ValueError:
                rel = str(p)
            out[uid] = (sa, rel)
    return out
