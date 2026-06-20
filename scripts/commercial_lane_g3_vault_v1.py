#!/usr/bin/env python3
"""Commercial lane G3 vault visibility — conditional PRIORITY evidence (sa-0525)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
PRIORITY = SOURCE_A / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
PROGRESS = SOURCE_A / "PROGRAM_PROGRESS.json"
WIRE_PROGRESS = SOURCE_A / "brain-os/law/WIRE_LANE_PROGRESS.md"
WIRE_PLAN = Path.home() / "Desktop/AI Dev Bridge OS/config/locked_plan.json"
CROSSREF = "archive/attachments/2026-06-14/sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md"

G3_VAULT_AGENTS = ("wire", "trustfield", "sourcea")
G3_KEYWORDS = ("g3", "tailscale", "wire-g3", "g3_tailscale", "proof:g3", "record:g3")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def wire_g3_disk_status() -> str:
    """Disk SSOT: locked_plan wire_proof.g3_tailscale, else PROGRAM_PROGRESS signals_auto.wire."""
    if WIRE_PLAN.is_file():
        try:
            data = json.loads(WIRE_PLAN.read_text(encoding="utf-8"))
            status = str((data.get("wire_proof") or {}).get("g3_tailscale") or "").strip().lower()
            if status:
                return status
        except (OSError, json.JSONDecodeError):
            pass
    if PROGRESS.is_file():
        try:
            prog = json.loads(PROGRESS.read_text(encoding="utf-8"))
            status = str(((prog.get("signals_auto") or {}).get("wire") or {}).get("g3_tailscale") or "")
            return status.strip().lower() or "unknown"
        except (OSError, json.JSONDecodeError):
            pass
    return "unknown"


def _doc_matches_g3(doc: dict) -> bool:
    blob = json.dumps(doc, ensure_ascii=False).lower()
    title = str(doc.get("title") or "").lower()
    tags = [str(t).lower() for t in (doc.get("tags") or [])]
    for key in G3_KEYWORDS:
        if key in blob or key in title or any(key in t for t in tags):
            return True
    return False


def probe_g3_vault_visibility() -> dict:
    """Scan workspace vaults for G3 evidence; never raises."""
    import sys

    scripts = SOURCE_A / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from agent_workspace_vault import vault_summary  # noqa: WPS433

    hits: list[dict] = []
    for agent_id in G3_VAULT_AGENTS:
        try:
            summary = vault_summary(agent_id, doc_limit=50, activity_limit=5)
        except Exception as exc:  # noqa: BLE001
            hits.append({"agent_id": agent_id, "error": str(exc)})
            continue
        for doc in summary.get("recent_documents") or []:
            if _doc_matches_g3(doc):
                hits.append({"agent_id": agent_id, "doc_id": doc.get("id"), "title": doc.get("title")})

    disk = wire_g3_disk_status()
    disk_pass = disk in ("pass", "done", "green", "true")
    visible = bool(hits) or disk_pass
    return {
        "ok": True,
        "visible": visible,
        "wire_g3_disk": disk,
        "vault_hits": hits,
        "agents_scanned": list(G3_VAULT_AGENTS),
        "wire_progress_doc": str(WIRE_PROGRESS),
        "at": _now(),
    }


def append_priority_g3_evidence_if_visible(*, dry_run: bool = False) -> dict:
    """Append SOURCEA-PRIORITY evidence row only when G3 is visible in vault or disk pass."""
    probe = probe_g3_vault_visibility()
    if not probe.get("visible"):
        return {"ok": True, "appended": False, "reason": "g3_not_visible", "probe": probe}

    if not PRIORITY.is_file():
        return {"ok": False, "error": "missing_priority", "probe": probe}

    text = PRIORITY.read_text(encoding="utf-8")
    marker = "sa-0525"
    if marker in text and f"| {marker}" in text or f"sa-0525 " in text:
        return {"ok": True, "appended": False, "reason": "already_present", "probe": probe}

    hits = probe.get("vault_hits") or []
    hit_note = f"vault_hits={len(hits)}" if hits else f"wire_g3_disk={probe.get('wire_g3_disk')}"
    row = (
        f"| {_now()[:10]} | sa-0525 Append commercial lane evidence when G3 visible in vault | "
        f"{CROSSREF} · G3 visible · {hit_note} · validate-commercial-lane-g3-vault-evidence-v1 PASS |\n"
    )
    if dry_run:
        return {"ok": True, "appended": False, "dry_run": True, "row": row.strip(), "probe": probe}

    anchor = "| 2026-06-14 | sa-0524 Document two-clock slice"
    if anchor in text:
        text = text.replace(anchor, row + anchor, 1)
    else:
        text = text.rstrip() + "\n" + row
    PRIORITY.write_text(text, encoding="utf-8")
    return {"ok": True, "appended": True, "reason": "g3_visible", "probe": probe, "row": row.strip()}
