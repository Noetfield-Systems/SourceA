"""Cloud drain queue — head state on Railway volume + Mac ~/.sina mirror."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
MAC_PHASE = SINA / "phase-observed-v1.json"
ACTIVE_POINTER = ROOT / "data/cloud-drain-queue-active-v1.json"
LEGACY_DRAIN = ROOT / "data/secondary-cloud-drain-next-100-v1.json"


def active_drain_path() -> Path:
    """Resolve active cloud drain queue SSOT (batch pointer · locked)."""
    ptr = _read(ACTIVE_POINTER)
    rel = str(ptr.get("queue_path") or "").strip()
    if rel:
        return ROOT / rel
    return LEGACY_DRAIN


def drain_ssot_path() -> Path:
    return active_drain_path()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_headless() -> bool:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless":
        return True
    if os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return Path("/app/receipts").is_dir()


def phase_path() -> Path:
    if _is_headless():
        return Path("/app/receipts/cloud-drain/phase-observed-v1.json")
    env = os.environ.get("CLOUD_DRAIN_PHASE_PATH", "").strip()
    if env:
        return Path(env)
    return MAC_PHASE


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.setdefault("schema", "phase-observed-v1")
    doc["rebuilt_at"] = _now()
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _cloud_plans() -> list[dict[str, Any]]:
    drain = _read(drain_ssot_path())
    return [p for p in (drain.get("plans") or []) if str(p.get("id", "")).startswith("CLOUD-SEC-")]


def _plan_by_id(plan_id: str) -> dict[str, Any] | None:
    return next((p for p in _cloud_plans() if str(p.get("id")) == plan_id), None)


def is_mock_plan(plan: dict[str, Any] | None) -> bool:
    if not plan:
        return False
    if plan.get("auto_pass") is True:
        return True
    if str(plan.get("drain_lane") or "") == "scaffold":
        return True
    blob = json.dumps(plan).lower()
    return "mock_only" in blob or "mock run-detail" in blob or "stub mock" in blob


def read_head() -> dict[str, Any]:
    obs = _read(phase_path())
    head = str(obs.get("cloud_drain_head") or "")
    if not head:
        plans = _cloud_plans()
        head = str(plans[0].get("id")) if plans else ""
    ids = [str(p.get("id") or "") for p in _cloud_plans()]
    last_id = ids[-1] if ids else ""
    last_completed = obs.get("cloud_drain_last_completed")
    batch_complete = bool(obs.get("queue_batch_complete")) or (
        bool(head and last_completed and head == str(last_completed) and head == last_id)
    )
    return {
        "ok": True,
        "schema": "cloud-drain-queue-head-v1",
        "at": _now(),
        "cloud_drain_head": head,
        "cloud_drain_last_completed": last_completed,
        "queue_batch_complete": batch_complete,
        "phase_path": str(phase_path()),
        "head_is_mock": is_mock_plan(_plan_by_id(head)),
        "observed": obs,
    }


def skip_head(*, reason: str = "") -> dict[str, Any]:
    path = phase_path()
    obs = _read(path)
    head = str(obs.get("cloud_drain_head") or "")
    cloud_plans = _cloud_plans()
    idx = next((i for i, p in enumerate(cloud_plans) if p.get("id") == head), -1)
    if idx < 0:
        if cloud_plans:
            head = str(cloud_plans[0].get("id"))
            idx = 0
        else:
            return {"ok": False, "error": "head_not_found", "head": head}
    if idx >= len(cloud_plans) - 1:
        return {"ok": False, "error": "no_next_plan", "head": head}
    nxt_id = str(cloud_plans[idx + 1].get("id"))
    obs.update(
        {
            "cloud_drain_last_completed": head,
            "cloud_drain_head": nxt_id,
            "skipped_from": head,
            "skip_reason": reason or "skip_head",
            "rebuilt_by": "cloud_drain_queue_v1.skip_head",
        }
    )
    _write(path, obs)
    return {
        "ok": True,
        "from": head,
        "to": nxt_id,
        "phase_path": str(path),
        "for_founder": {"show_this": f"Skipped {head} → head now {nxt_id}"},
    }


def skip_to_next_real(*, reason: str = "", max_skips: int = 12) -> dict[str, Any]:
    skipped: list[dict[str, Any]] = []
    for _ in range(max_skips):
        state = read_head()
        head = str(state.get("cloud_drain_head") or "")
        plan = _plan_by_id(head)
        if not is_mock_plan(plan):
            return {
                "ok": True,
                "head_now": head,
                "skipped": skipped,
                "skipped_count": len(skipped),
                "head_is_mock": False,
                "for_founder": {
                    "show_this": f"Head now {head} — ready for Proceed"
                    if skipped
                    else f"Head {head} is already a real row — no skip needed",
                },
            }
        row = skip_head(reason=reason or "skip_to_next_real_mock")
        if not row.get("ok"):
            row["skipped_so_far"] = skipped
            return row
        skipped.append(row)
    return {
        "ok": False,
        "error": "max_skips_reached",
        "skipped": skipped,
        "head_now": read_head().get("cloud_drain_head"),
    }


def advance_on_pass(*, plan_id: str) -> dict[str, Any]:
    path = phase_path()
    obs = _read(path)
    current_head = str(obs.get("cloud_drain_head") or "")
    if not current_head:
        current_head = str(read_head().get("cloud_drain_head") or "")
    if current_head and plan_id != current_head:
        return {
            "ok": False,
            "error": "plan_not_queue_head",
            "plan_id": plan_id,
            "cloud_drain_head": current_head,
        }
    ids = [str(p.get("id") or "") for p in _cloud_plans()]
    if plan_id not in ids:
        return {"ok": False, "error": "plan_not_in_queue", "plan_id": plan_id}
    idx = ids.index(plan_id)
    at_end = idx + 1 >= len(ids)
    nxt = ids[idx + 1] if not at_end else plan_id
    obs.update(
        {
            "cloud_drain_head": nxt,
            "cloud_drain_last_completed": plan_id,
            "queue_batch_complete": at_end,
            "rebuilt_by": "cloud_drain_queue_v1.advance_on_pass",
            "rebuilt_at": _now(),
        }
    )
    _write(path, obs)
    return {"ok": True, "completed": plan_id, "head": nxt, "phase_path": str(path)}


def sync_to_mac_if_newer(cloud_row: dict[str, Any]) -> dict[str, Any]:
    """Mac Hub: pull cloud queue head when cloud rebuilt_at is newer."""
    if _is_headless():
        return {"ok": False, "skipped": "headless"}
    cloud_at = str((cloud_row.get("observed") or {}).get("rebuilt_at") or cloud_row.get("rebuilt_at") or "")
    local = _read(MAC_PHASE)
    local_at = str(local.get("rebuilt_at") or "")
    head = str(cloud_row.get("cloud_drain_head") or (cloud_row.get("observed") or {}).get("cloud_drain_head") or "")
    if not head:
        return {"ok": False, "error": "no_cloud_head"}
    local_head = str(local.get("cloud_drain_head") or "")
    diverged = bool(local_head and head != local_head)
    if not cloud_at:
        return {"ok": False, "skipped": "no_cloud_timestamp"}
    if local_at and cloud_at <= local_at and not diverged:
        return {"ok": True, "synced": False, "reason": "local_newer_or_equal"}
    local.update(
        {
            "cloud_drain_head": head,
            "cloud_drain_last_completed": (cloud_row.get("observed") or {}).get("cloud_drain_last_completed")
            or cloud_row.get("cloud_drain_last_completed"),
            "rebuilt_at": cloud_at,
            "rebuilt_by": "cloud_drain_queue_v1.sync_to_mac",
            "synced_from_cloud": True,
        }
    )
    _write(MAC_PHASE, local)
    reason = "cloud_divergence_repair" if diverged else "cloud_newer"
    return {"ok": True, "synced": True, "head": head, "reason": reason, "repaired_from": local_head if diverged else None}


def handle_queue_action(body: dict[str, Any] | None) -> dict[str, Any]:
    body = body or {}
    action = str(body.get("action") or "get_head").strip().lower()
    if action in ("get_head", "status"):
        return read_head()
    if action == "skip_head":
        return skip_head(reason=str(body.get("reason") or "api_skip_head"))
    if action == "skip_to_next_real":
        return skip_to_next_real(
            reason=str(body.get("reason") or "api_skip_to_next_real"),
            max_skips=int(body.get("max_skips") or 12),
        )
    if action == "set_head":
        head = str(body.get("head") or body.get("cloud_drain_head") or "")
        if not head:
            return {"ok": False, "error": "head_required"}
        path = phase_path()
        obs = _read(path)
        obs.update(
            {
                "cloud_drain_head": head,
                "cloud_drain_last_completed": body.get("last_completed") or obs.get("cloud_drain_last_completed"),
                "rebuilt_by": "cloud_drain_queue_v1.set_head",
                "set_reason": str(body.get("reason") or "founder_set_head"),
            }
        )
        _write(path, obs)
        return {"ok": True, "head": head, "phase_path": str(path)}
    return {"ok": False, "error": "unknown_action", "action": action}
