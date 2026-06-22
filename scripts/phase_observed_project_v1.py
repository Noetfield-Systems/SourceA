#!/usr/bin/env python3
"""Observed (status) projection writer — NEVER touches desired/assignment.

Law: data/execution-state-desired-observed-v1.json
Imports phase_desired_read_v1 read-only for cloud_drain_head label only.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
ERA_REPO = ROOT / "data" / "factory-era-v1.json"
EVENT_LOG = SINA / "phase-event-log-v1.jsonl"
OBSERVED = SINA / "phase-observed-v1.json"
HOME_QUEUE = SINA / "healthy-queue-30-active.json"
HOME_STATE = SINA / "healthy-queue-state-v1.json"
ARCHIVE_DIR = ROOT / "archive" / "attachments" / "factory-era" / "forge-factory-cycle2-complete-2026-06-21"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def read_observed_era() -> str:
    obs = _read(OBSERVED)
    if obs.get("era"):
        return str(obs["era"])
    fn = _read(SINA / "factory-now-v1.json")
    if fn.get("era"):
        return str(fn["era"])
    era = _read(SINA / "factory-era-v1.json") or _read(ERA_REPO)
    return str(era.get("current_era") or "")


def read_event_log() -> list[dict[str, Any]]:
    if not EVENT_LOG.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in EVENT_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def has_probe_backed_ratify(*, to_era: str = "phase_market") -> bool:
    """True when event log contains probe_gate_pass ratify for era (law v1.2.0)."""
    for event in read_event_log():
        if str(event.get("to_era") or "") != to_era:
            continue
        if event.get("probe_gate_pass") is True:
            return True
    return False


def derive_era_from_event_log() -> str:
    """Cold-start: last probe-backed transition wins over stale projection files."""
    era = ""
    for event in read_event_log():
        if event.get("probe_gate_pass") is True and event.get("to_era"):
            era = str(event["to_era"])
    return era


def append_event(event: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    line = json.dumps({**event, "at": _now()}, separators=(",", ":"))
    with EVENT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def archive_forge_cycle2() -> list[dict[str, Any]]:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    out: list[dict[str, Any]] = []
    for name, src in [
        ("healthy-queue", HOME_QUEUE),
        ("healthy-queue-state", HOME_STATE),
        ("factory-era-home", SINA / "factory-era-v1.json"),
    ]:
        if not src.is_file():
            out.append({"name": name, "ok": False, "skipped": True})
            continue
        dst = ARCHIVE_DIR / src.name
        shutil.copy2(src, dst)
        out.append({"name": name, "ok": True, "archived_to": str(dst)})
    return out


def mark_forge_queue_exhausted() -> dict[str, Any]:
    q = _read(HOME_QUEUE)
    st = _read(HOME_STATE)
    if q:
        q.update(
            {
                "queue_exhausted": True,
                "phase_strict_complete": True,
                "completed_at": _now(),
                "completed_by": "phase_observed_project_v1",
                "note": "forge_factory_cycle2 observed complete — cloud drain head from founder desired",
            }
        )
        _write(HOME_QUEUE, q)
    if st:
        st.update(
            {
                "queue_exhausted": True,
                "next_pos": max(int(st.get("next_pos") or 1), 11),
                "last_completed_at": _now(),
                "era": "forge_factory_cycle2",
                "completed_by": "phase_observed_project_v1",
            }
        )
        _write(HOME_STATE, st)
    return {"ok": True, "queue_exhausted": True}


def project_era_phase_market(*, cloud_head: str) -> dict[str, Any]:
    base = _read(ERA_REPO) or _read(SINA / "factory-era-v1.json")
    row = {
        **base,
        "schema": "factory-era-v1",
        "current_era": "phase_market",
        "current_brand": "PORTFOLIO-",
        "live_mode": "CLOUD_DRAIN",
        "cloud_drain_head": cloud_head,
        "reconciled_at": _now(),
        "reconciled_by": "phase_observed_project_v1",
        "prior_era": "forge_factory_cycle2",
        "queue_ssot": "data/secondary-cloud-drain-next-100-v1.json",
    }
    archived = list(row.get("archived_eras") or [])
    if not any(a.get("id") == "forge_factory_cycle2" for a in archived):
        archived.append(
            {
                "id": "forge_factory_cycle2",
                "status": "complete_archived",
                "archived_at": _now(),
                "probe_gate": "phase_transition_probe_v1 ff-001..ff-010",
            }
        )
    row["archived_eras"] = archived
    _write(ERA_REPO, row)
    _write(SINA / "factory-era-v1.json", row)
    return row


def write_phase_observed(*, cloud_head: str) -> dict[str, Any]:
    row = {
        "schema": "phase-observed-v1",
        "era": "phase_market",
        "cloud_drain_head": cloud_head,
        "forge_cycle2": "complete",
        "queue_exhausted": True,
        "mac_executes": False,
        "execution_plane": "cloud_forge",
        "rebuilt_by": "phase_observed_project_v1",
        "rebuilt_at": _now(),
        "law": "data/execution-state-desired-observed-v1.json",
    }
    _write(OBSERVED, row)
    return row


def rebuild_factory_now_observed(*, cloud_head: str, caller: str) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from factory_control_v1 import KILL_FLAG, STOP_RECEIPT, _atomic_write, _set_mode_file, rebuild_factory_now  # noqa: WPS433

    KILL_FLAG.unlink(missing_ok=True)
    stop = _read(STOP_RECEIPT)
    if stop:
        stop.update({"cleared_by_asf": True, "cleared_at": _now(), "cleared_by": caller})
        _atomic_write(STOP_RECEIPT, stop)
    _set_mode_file("FREEZE", set_by=caller, reason="phase_market mac observe · cloud drain active")
    fn = rebuild_factory_now(caller=caller, force=True)
    fn["cloud_drain_head"] = cloud_head
    fn["era"] = "phase_market"
    _atomic_write(SINA / "factory-now-v1.json", fn)
    return fn


def project_cycle2_to_market(*, cloud_head: str, caller: str = "phase_observed_project_v1") -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    steps.append({"step": "archive_forge_cycle2", "rows": archive_forge_cycle2()})
    steps.append({"step": "mark_queue_exhausted", **mark_forge_queue_exhausted()})
    era_row = project_era_phase_market(cloud_head=cloud_head)
    steps.append({"step": "era_phase_market", "ok": True, "era": era_row.get("current_era")})
    obs = write_phase_observed(cloud_head=cloud_head)
    steps.append({"step": "phase_observed", "ok": True, **obs})
    try:
        fn = rebuild_factory_now_observed(cloud_head=cloud_head, caller=caller)
        steps.append({"step": "factory_now", "ok": True, "line": fn.get("line"), "cloud_drain_head": cloud_head})
    except Exception as exc:
        steps.append({"step": "factory_now", "ok": False, "error": str(exc)[:200]})
        return {"ok": False, "steps": steps}
    try:
        from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

        u = unify_queue_ssot()
        steps.append({"step": "queue_ssot_unify", "ok": bool(u.get("ok", True))})
    except Exception as exc:
        steps.append({"step": "queue_ssot_unify", "ok": False, "error": str(exc)[:120]})
    return {"ok": True, "steps": steps, "cloud_drain_head": cloud_head}


def already_reconciled_phase_market(*, desired_phase_id: str, cloud_head: str) -> bool:
    if desired_phase_id != "phase-market":
        return False
    obs = _read(OBSERVED)
    era = read_observed_era().replace("-", "_")
    if era not in ("phase_market", "phase-market") and obs.get("era") != "phase_market":
        return False
    return obs.get("forge_cycle2") == "complete" and str(obs.get("cloud_drain_head") or "") == cloud_head
