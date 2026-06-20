#!/usr/bin/env python3
"""Quarantine batch closeout YAML — dead as proof, not deleted."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"
QUARANTINE = LOGS / "QUARANTINE_BATCH_YAML"
MANIFEST = QUARANTINE / "manifest.jsonl"

SA_RE = re.compile(r"(sa-\d{4})")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sa_from_name(name: str) -> str | None:
    m = SA_RE.search(name)
    return m.group(1) if m else None


def is_quarantined_path(path: Path) -> bool:
    try:
        return QUARANTINE in path.resolve().parents
    except OSError:
        return "QUARANTINE_BATCH_YAML" in str(path)


def quarantine_yaml_for_sa(*, sa_id: str, reason: str = "unproven_revert") -> list[str]:
    """Move active closeout YAMLs for sa_id into quarantine. Returns moved paths."""
    if not sa_id.startswith("sa-"):
        return []
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []
    for p in sorted(LOGS.glob(f"*plan-with-no-asf*{sa_id}*.yaml")):
        if is_quarantined_path(p):
            continue
        dest = QUARANTINE / p.name
        if dest.exists():
            dest = QUARANTINE / f"{p.stem}_{_now().replace(':', '')}{p.suffix}"
        shutil.move(str(p), str(dest))
        moved.append(str(dest))
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps({"at": _now(), "sa_id": sa_id, "from": str(p), "to": str(dest), "reason": reason})
                + "\n"
            )
    return moved


def quarantine_all_except(*, keep_sa: set[str], reason: str = "batch_yaml_purge") -> dict:
    """Quarantine every plan-with-no-asf YAML whose sa is not in keep_sa."""
    keep = {s for s in keep_sa if s.startswith("sa-")}
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    moved = 0
    samples: list[str] = []
    for p in sorted(LOGS.glob("*plan-with-no-asf*.yaml")):
        if is_quarantined_path(p):
            continue
        sa = _sa_from_name(p.name)
        if not sa or sa in keep:
            continue
        dest = QUARANTINE / p.name
        if dest.exists():
            dest = QUARANTINE / f"{p.stem}_{_now().replace(':', '')}{p.suffix}"
        shutil.move(str(p), str(dest))
        moved += 1
        if len(samples) < 15:
            samples.append(sa)
        with MANIFEST.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps({"at": _now(), "sa_id": sa, "from": str(p), "to": str(dest), "reason": reason})
                + "\n"
            )
    return {"ok": True, "moved_count": moved, "keep_count": len(keep), "samples": samples}


def evidence_is_quarantined_only(*, sa_id: str, evidence: str) -> bool:
    """True if only closeout proof for sa_id lives in quarantine (no active YAML)."""
    needle = (evidence or "").strip()[:80]
    active = list(LOGS.glob(f"*plan-with-no-asf*{sa_id}*.yaml"))
    active = [p for p in active if not is_quarantined_path(p)]
    if active:
        return False
    q = list(QUARANTINE.glob(f"*plan-with-no-asf*{sa_id}*.yaml")) if QUARANTINE.is_dir() else []
    return bool(q) and len(needle) >= 12
