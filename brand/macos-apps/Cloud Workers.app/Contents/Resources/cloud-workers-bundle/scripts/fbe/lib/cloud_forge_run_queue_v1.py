"""Cloud Forge Run queue — head state on Railway volume + Mac ~/.sina mirror."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
MAC_PHASE = SINA / "phase-observed-v1.json"
ACTIVE_POINTER = ROOT / "data/cloud-forge-run-queue-active-v1.json"
VOLUME_POINTER = Path("/app/receipts/cloud-forge-run/queue-active-pointer-v1.json")
LEGACY_DRAIN = ROOT / "data/secondary-cloud-forge-run-next-100-v1.json"


def _read_pointer() -> dict[str, Any]:
    if _is_headless() and VOLUME_POINTER.is_file():
        doc = _read(VOLUME_POINTER)
        if doc.get("queue_path"):
            return doc
    return _read(ACTIVE_POINTER)


def _write_pointer(doc: dict[str, Any]) -> None:
    doc = {**doc, "saved_at": _now()}
    text = json.dumps(doc, indent=2) + "\n"
    if _is_headless():
        VOLUME_POINTER.parent.mkdir(parents=True, exist_ok=True)
        VOLUME_POINTER.write_text(text, encoding="utf-8")
    try:
        ACTIVE_POINTER.write_text(text, encoding="utf-8")
    except OSError:
        pass


def active_drain_path() -> Path:
    """Resolve active Cloud Forge Run queue SSOT (batch pointer · locked)."""
    ptr = _read_pointer()
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
        forge = Path("/app/receipts/cloud-forge-run/phase-observed-v1.json")
        legacy = Path("/app/receipts/cloud-drain/phase-observed-v1.json")
        if forge.is_file():
            return forge
        if legacy.is_file():
            return legacy
        return forge
    env = os.environ.get("CLOUD_DRAIN_PHASE_PATH", "").strip()
    if env:
        return Path(env)
    return MAC_PHASE


def _normalize_phase_keys(doc: dict[str, Any]) -> dict[str, Any]:
    """Volume may still carry legacy cloud_drain_* keys after physical rename."""
    if not doc.get("cloud_forge_run_head") and doc.get("cloud_drain_head"):
        doc["cloud_forge_run_head"] = doc["cloud_drain_head"]
    if not doc.get("cloud_forge_run_last_completed") and doc.get("cloud_drain_last_completed"):
        doc["cloud_forge_run_last_completed"] = doc["cloud_drain_last_completed"]
    return doc


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "phase-observed-v1.json":
            return _normalize_phase_keys(doc)
        return doc
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


def _plan_num(plan_id: str) -> int:
    text = str(plan_id or "")
    if text.startswith("CLOUD-SEC-"):
        try:
            return int(text.rsplit("-", 1)[-1])
        except ValueError:
            return 0
    return 0


def _has_next_batch_file(ptr: dict[str, Any] | None = None) -> bool:
    ptr = ptr or _read_pointer()
    nxt = ptr.get("next_batch") or {}
    rel = str(nxt.get("queue_path") or "").strip()
    if rel and (ROOT / rel).is_file():
        return True
    bid = int(ptr.get("batch_id") or 0)
    if bid <= 0:
        return False
    return (ROOT / f"data/secondary-cloud-forge-run-batch-{bid + 1}-locked-v1.json").is_file()


def seal_registry_exhausted(*, reason: str = "patch_complete") -> dict[str, Any]:
    """Mark active pointer + phase when final batch is done and no next batch exists."""
    ptr = _read_pointer()
    obs = _read(phase_path())
    batch_id = int(obs.get("batch_id") or ptr.get("batch_id") or 0)
    head = str(obs.get("cloud_forge_run_head") or read_head().get("cloud_forge_run_head") or "")
    last = str(obs.get("cloud_forge_run_last_completed") or head)
    drain_status = str(ptr.get("drain_status") or "")
    if ptr.get("extension_wave2_patch"):
        drain_status = "extension_wave2_complete"
    elif drain_status.endswith("_armed"):
        drain_status = drain_status.replace("_armed", "_complete")
    new_ptr = {
        **ptr,
        "registry_exhausted": True,
        "queue_batch_complete": True,
        "drain_status": drain_status or "registry_exhausted",
        "completed_at": _now(),
        "sealed_reason": reason,
    }
    new_ptr.pop("next_batch", None)
    _write_pointer(new_ptr)
    obs.update(
        {
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last,
            "queue_batch_complete": True,
            "batch_id": batch_id,
            "rebuilt_by": "cloud_forge_run_queue_v1.seal_registry_exhausted",
            "rebuilt_at": _now(),
            "seal_reason": reason,
        }
    )
    _write(phase_path(), obs)
    return {
        "ok": True,
        "schema": "cloud-forge-run-seal-registry-exhausted-v1",
        "batch_id": batch_id,
        "head": head,
        "last_completed": last,
        "drain_status": new_ptr.get("drain_status"),
        "for_founder": {
            "show_this": (
                f"PATCH COMPLETE — {last} · batch {batch_id} · registry exhausted · "
                "no more cloud forge rows in queue"
            ),
        },
    }


def _queue_diagnostics() -> dict[str, Any]:
    ptr = _read_pointer()
    qpath = drain_ssot_path()
    return {
        "active_pointer": str(ACTIVE_POINTER),
        "batch_id": ptr.get("batch_id"),
        "queue_path": str(ptr.get("queue_path") or ""),
        "queue_file": str(qpath),
        "queue_file_exists": qpath.is_file(),
        "cloud_plan_count": len(_cloud_plans()),
        "next_batch": ptr.get("next_batch"),
    }


def boot_heal_queue(*, force: bool = False) -> dict[str, Any]:
    """Railway boot — heal missing queue file / stale phase vs active pointer."""
    if not _is_headless() and not force:
        return {"ok": True, "skipped": "not_headless"}
    ptr = _read_pointer()
    shipped = _read(ACTIVE_POINTER)
    ship_batch = int(shipped.get("batch_id") or 0)
    ptr_batch = int(ptr.get("batch_id") or 0)
    ship_rel = str(shipped.get("queue_path") or "").strip()
    obs_pre = _read(phase_path())
    if (
        _is_headless()
        and ship_batch > ptr_batch
        and ship_rel
        and (ROOT / ship_rel).is_file()
        and (bool(shipped.get("extension_wave2_patch")) or bool(obs_pre.get("queue_batch_complete")))
    ):
        _write_pointer(shipped)
        ptr = shipped
    diag = _queue_diagnostics()
    plans = _cloud_plans()
    obs = _read(phase_path())
    head = str(obs.get("cloud_forge_run_head") or "")
    plan_ids = [str(p.get("id") or "") for p in plans]

    if not diag.get("queue_file_exists"):
        nxt = ptr.get("next_batch") or {}
        nxt_rel = str(nxt.get("queue_path") or "").strip()
        if nxt_rel and (ROOT / nxt_rel).is_file():
            swapped = swap_to_next_batch(reason="boot_heal_missing_active_queue")
            swapped["heal"] = "swapped_to_next_batch"
            return swapped
        return {
            "ok": False,
            "error": "active_queue_file_missing_in_image",
            "diagnostics": diag,
            "for_founder": {
                "show_this": (
                    f"BLOCKER — queue file missing in Railway image: {diag.get('queue_path')} · "
                    "redeploy FBE runner (Dockerfile COPY must include active batch JSON)"
                ),
            },
        }

    if plans and head and head not in plan_ids:
        nxt = ptr.get("next_batch") or {}
        nxt_rel = str(nxt.get("queue_path") or "").strip()
        if nxt_rel:
            nxt_plans = [
                p
                for p in (_read(ROOT / nxt_rel).get("plans") or [])
                if str(p.get("id", "")).startswith("CLOUD-SEC-")
            ]
            if any(str(p.get("id") or "") == head for p in nxt_plans):
                return swap_to_next_batch(reason="boot_heal_head_in_next_batch")
            return swap_to_next_batch(reason="boot_heal_head_not_in_queue")
        return activate_batch(reason="boot_heal_head_not_in_queue")

    obs_batch = int(obs.get("batch_id") or 0)
    ptr_batch = int(ptr.get("batch_id") or 0)
    if obs_batch > ptr_batch and (ptr.get("next_batch") or {}).get("queue_path"):
        return swap_to_next_batch(reason="boot_heal_phase_batch_ahead")

    if not plans:
        return {
            "ok": False,
            "error": "no_cloud_plans_in_active_queue",
            "diagnostics": diag,
        }

    reset = ptr.get("phase_reset") or {}
    reset_head = str(reset.get("cloud_forge_run_head") or plan_ids[0])
    needs_activate = (
        bool(obs.get("queue_batch_complete"))
        or (obs_batch > 0 and ptr_batch > 0 and obs_batch == ptr_batch and head and head not in plan_ids)
    )
    if needs_activate:
        if head and head in plan_ids and _plan_num(head) >= _plan_num(reset_head):
            obs.update(
                {
                    "batch_id": ptr.get("batch_id"),
                    "queue_batch_complete": False,
                    "rebuilt_by": "cloud_forge_run_queue_v1.boot_heal_keep_head",
                    "activate_reason": "boot_heal_sync_batch",
                }
            )
            _write(phase_path(), obs)
            return {"ok": True, "healed": True, "head": head, "heal": "sync_batch_keep_head", "diagnostics": diag}
        return activate_batch(reason="boot_heal_stale_phase")
    return {"ok": True, "healed": False, "head": head or reset_head, "diagnostics": diag}


def swap_to_next_batch(*, reason: str = "batch_complete_handoff") -> dict[str, Any]:
    """Pointer swap — arm pre-locked next batch (batch N+1 on disk)."""
    ptr = _read_pointer()
    nxt = ptr.get("next_batch") or {}
    rel = str(nxt.get("queue_path") or "").strip()
    batch_id = int(nxt.get("batch_id") or 0)
    if not rel or not batch_id:
        return {"ok": False, "error": "no_next_batch_ready", "next_batch": nxt}
    nxt_path = ROOT / rel
    if not nxt_path.is_file():
        return {"ok": False, "error": "next_batch_file_missing", "path": str(nxt_path)}
    drain = _read(nxt_path)
    cloud_plans = [p for p in (drain.get("plans") or []) if str(p.get("id", "")).startswith("CLOUD-SEC-")]
    first_head = str(cloud_plans[0].get("id")) if cloud_plans else ""
    if not first_head:
        return {"ok": False, "error": "next_batch_empty"}
    prev_obs = _read(phase_path())
    prev_last = str(
        prev_obs.get("cloud_forge_run_last_completed")
        or prev_obs.get("cloud_forge_run_head")
        or ""
    )
    prev_plans = [p for p in _cloud_plans() if str(p.get("id", "")).startswith("CLOUD-SEC-")]
    if not prev_last and prev_plans:
        prev_last = str(prev_plans[-1].get("id") or "")
    prev_batch = int(ptr.get("batch_id") or 0)
    archive_key = f"archive_batch{prev_batch}" if prev_batch else "archive_batch_prev"
    new_ptr = {
        **ptr,
        "batch_id": batch_id,
        "queue_path": rel,
        "saved_at": _now(),
        archive_key: str(ptr.get("queue_path") or ""),
        "phase_reset": {
            "cloud_forge_run_head": first_head,
            "cloud_forge_run_last_completed": prev_last or None,
            "queue_batch_complete": False,
        },
        "next_batch": nxt.get("next_batch"),
    }
    nxt_batch_id = batch_id + 1
    candidate = ROOT / f"data/secondary-cloud-forge-run-batch-{nxt_batch_id}-locked-v1.json"
    if candidate.is_file():
        cand_drain = _read(candidate)
        rng = (cand_drain.get("summary") or {}).get("cloud_sec_range")
        new_ptr["next_batch"] = {
            "batch_id": nxt_batch_id,
            "status": "ready_locked",
            "queue_path": f"data/secondary-cloud-forge-run-batch-{nxt_batch_id}-locked-v1.json",
            "cloud_sec_range": rng,
        }
    else:
        new_ptr.pop("next_batch", None)
    _write_pointer(new_ptr)
    return activate_batch(reason=reason)


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
    ptr = _read_pointer()
    obs = _read(phase_path())
    if _is_headless() and not bool(ptr.get("registry_exhausted")):
        plans_pre = _cloud_plans()
        plan_ids_pre = [str(p.get("id") or "") for p in plans_pre]
        head_pre = str(obs.get("cloud_forge_run_head") or "")
        ptr_batch = int(ptr.get("batch_id") or 0)
        obs_batch = int(obs.get("batch_id") or 0)
        batch_mismatch = obs_batch != ptr_batch and ptr_batch > 0
        stale_phase = bool(obs.get("queue_batch_complete")) or (
            head_pre and plan_ids_pre and head_pre not in plan_ids_pre
        )
        if batch_mismatch and head_pre in plan_ids_pre:
            obs["batch_id"] = ptr_batch
            obs["queue_batch_complete"] = False
            obs["rebuilt_by"] = "cloud_forge_run_queue_v1.read_head_sync_batch"
            _write(phase_path(), obs)
        elif stale_phase:
            boot_heal_queue(force=True)
            obs = _read(phase_path())
            ptr = _read_pointer()
    head = str(obs.get("cloud_forge_run_head") or "")
    if not head:
        plans = _cloud_plans()
        head = str(plans[0].get("id")) if plans else ""
    ids = [str(p.get("id") or "") for p in _cloud_plans()]
    last_id = ids[-1] if ids else ""
    last_completed = obs.get("cloud_forge_run_last_completed")
    if not last_completed and head:
        try:
            idx = ids.index(head)
            if idx > 0:
                last_completed = ids[idx - 1]
        except ValueError:
            pass
    batch_complete = bool(obs.get("queue_batch_complete")) or (
        bool(head and last_completed and head == str(last_completed) and head == last_id)
    )
    has_next_batch = _has_next_batch_file(ptr)
    registry_exhausted = bool(
        ptr.get("registry_exhausted")
        or ptr.get("drain_status") in ("competitor_1000_complete", "extension_wave2_complete")
        or (batch_complete and not has_next_batch)
    )
    return {
        "ok": True,
        "schema": "cloud-forge-run-queue-head-v1",
        "at": _now(),
        "cloud_forge_run_head": head,
        "cloud_forge_run_last_completed": last_completed,
        "queue_batch_complete": batch_complete,
        "registry_exhausted": registry_exhausted,
        "drain_status": ptr.get("drain_status"),
        "next_motor_ssot": ptr.get("next_motor_ssot"),
        "phase_path": str(phase_path()),
        "head_is_mock": is_mock_plan(_plan_by_id(head)),
        "observed": obs,
        "batch_id": obs.get("batch_id") or ptr.get("batch_id"),
    }


def skip_head(*, reason: str = "") -> dict[str, Any]:
    path = phase_path()
    obs = _read(path)
    head = str(obs.get("cloud_forge_run_head") or "")
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
            "cloud_forge_run_last_completed": head,
            "cloud_forge_run_head": nxt_id,
            "skipped_from": head,
            "skip_reason": reason or "skip_head",
            "rebuilt_by": "cloud_forge_run_queue_v1.skip_head",
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
        head = str(state.get("cloud_forge_run_head") or "")
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
        "head_now": read_head().get("cloud_forge_run_head"),
    }


def advance_on_pass(*, plan_id: str) -> dict[str, Any]:
    path = phase_path()
    obs = _read(path)
    current_head = str(obs.get("cloud_forge_run_head") or "")
    if not current_head:
        current_head = str(read_head().get("cloud_forge_run_head") or "")
    if current_head and plan_id != current_head:
        return {
            "ok": False,
            "error": "plan_not_queue_head",
            "plan_id": plan_id,
            "cloud_forge_run_head": current_head,
        }
    ids = [str(p.get("id") or "") for p in _cloud_plans()]
    if plan_id not in ids:
        return {"ok": False, "error": "plan_not_in_queue", "plan_id": plan_id}
    idx = ids.index(plan_id)
    at_end = idx + 1 >= len(ids)
    nxt = ids[idx + 1] if not at_end else plan_id
    obs.update(
        {
            "cloud_forge_run_head": nxt,
            "cloud_forge_run_last_completed": plan_id,
            "queue_batch_complete": at_end,
            "rebuilt_by": "cloud_forge_run_queue_v1.advance_on_pass",
            "rebuilt_at": _now(),
        }
    )
    _write(path, obs)
    result = {"ok": True, "completed": plan_id, "head": nxt, "phase_path": str(path)}
    if at_end:
        ptr = _read_pointer()
        nxt_batch = ptr.get("next_batch") or {}
        if nxt_batch.get("status") in ("ready_locked", "ready") and nxt_batch.get("queue_path"):
            handoff = swap_to_next_batch(reason="advance_on_pass_batch_complete")
            result["next_batch_handoff"] = handoff
        elif not _has_next_batch_file(ptr):
            result["registry_seal"] = seal_registry_exhausted(reason="advance_on_pass_final_batch")
    return result


def sync_to_mac_if_newer(cloud_row: dict[str, Any]) -> dict[str, Any]:
    """Mac Hub: pull cloud queue head when cloud rebuilt_at is newer."""
    if _is_headless():
        return {"ok": False, "skipped": "headless"}
    cloud_at = str(
        (cloud_row.get("observed") or {}).get("rebuilt_at")
        or cloud_row.get("rebuilt_at")
        or cloud_row.get("at")
        or ""
    )
    local = _read(MAC_PHASE)
    local_at = str(local.get("rebuilt_at") or "")
    head = str(cloud_row.get("cloud_forge_run_head") or (cloud_row.get("observed") or {}).get("cloud_forge_run_head") or "")
    if not head:
        return {"ok": False, "error": "no_cloud_head"}
    local_head = str(local.get("cloud_forge_run_head") or "")
    diverged = bool(local_head and head != local_head)
    observed = cloud_row.get("observed") if isinstance(cloud_row.get("observed"), dict) else {}
    ptr = _read_pointer()
    cloud_batch = observed.get("batch_id") or cloud_row.get("batch_id") or ptr.get("batch_id")
    batch_diverged = cloud_batch is not None and int(local.get("batch_id") or 0) != int(cloud_batch)
    if not cloud_at:
        if diverged or batch_diverged:
            cloud_at = _now()
        else:
            return {"ok": False, "skipped": "no_cloud_timestamp"}
    if local_at and cloud_at <= local_at and not diverged and not batch_diverged:
        return {"ok": True, "synced": False, "reason": "local_newer_or_equal"}
    batch_id = cloud_batch
    local.update(
        {
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": observed.get("cloud_forge_run_last_completed")
            or cloud_row.get("cloud_forge_run_last_completed"),
            "queue_batch_complete": observed.get("queue_batch_complete", cloud_row.get("queue_batch_complete")),
            "rebuilt_at": cloud_at,
            "rebuilt_by": "cloud_forge_run_queue_v1.sync_to_mac",
            "synced_from_cloud": True,
        }
    )
    if batch_id is not None:
        local["batch_id"] = int(batch_id)
    _write(MAC_PHASE, local)
    reason = "cloud_divergence_repair" if (diverged or batch_diverged) else "cloud_newer"
    return {
        "ok": True,
        "synced": True,
        "head": head,
        "batch_id": local.get("batch_id"),
        "reason": reason,
        "repaired_from": local_head if diverged else None,
    }


def sync_pointer_from_image(*, reason: str = "sync_pointer_from_image") -> dict[str, Any]:
    """Headless — volume pointer may lag shipped image after extension patch deploy."""
    shipped = _read(ACTIVE_POINTER)
    rel = str(shipped.get("queue_path") or "").strip()
    if not rel:
        return {"ok": False, "error": "no_shipped_pointer"}
    if not (ROOT / rel).is_file():
        return {
            "ok": False,
            "error": "shipped_queue_missing_in_image",
            "path": rel,
            "for_founder": {
                "show_this": f"BLOCKER — {rel} missing in Railway image · redeploy FBE runner",
            },
        }
    _write_pointer(shipped)
    armed = activate_batch(reason=reason)
    armed["synced_from_image"] = True
    armed["shipped_batch_id"] = shipped.get("batch_id")
    return armed


def activate_batch(*, reason: str = "founder_activate_batch", batch_id: int | None = None) -> dict[str, Any]:
    ptr = _read_pointer()
    bid = int(batch_id or ptr.get("batch_id") or 0)
    if bid and bid != int(ptr.get("batch_id") or 0):
        return {"ok": False, "error": "batch_id_mismatch", "active": ptr.get("batch_id"), "requested": bid}
    plans = _cloud_plans()
    if not plans:
        healed = boot_heal_queue(force=True)
        if healed.get("ok"):
            plans = _cloud_plans()
        if not plans:
            return {
                "ok": False,
                "error": "no_cloud_plans_in_active_queue",
                "diagnostics": _queue_diagnostics(),
                "boot_heal": healed,
                "for_founder": {
                    "show_this": (
                        "BLOCKER — active drain queue empty in Railway image · "
                        "redeploy with Dockerfile COPY for batch JSON"
                    ),
                },
            }
    first = str(plans[0].get("id"))
    reset = ptr.get("phase_reset") or {}
    path = phase_path()
    obs = _read(path)
    current_head = str(obs.get("cloud_forge_run_head") or "")
    reset_head = str(reset.get("cloud_forge_run_head") or first)
    plan_ids = [str(p.get("id") or "") for p in plans]
    if current_head in plan_ids and _plan_num(current_head) >= _plan_num(reset_head):
        new_head = current_head
    elif reset_head in plan_ids:
        new_head = reset_head
    else:
        new_head = first
    obs.update(
        {
            "cloud_forge_run_head": new_head,
            "cloud_forge_run_last_completed": reset.get("cloud_forge_run_last_completed")
            if new_head == reset_head
            else obs.get("cloud_forge_run_last_completed"),
            "queue_batch_complete": False,
            "batch_id": ptr.get("batch_id"),
            "rebuilt_by": "cloud_forge_run_queue_v1.activate_batch",
            "activate_reason": reason,
        }
    )
    _write(path, obs)
    head_now = str(obs.get("cloud_forge_run_head") or first)
    return {
        "ok": True,
        "batch_id": ptr.get("batch_id"),
        "head": head_now,
        "queue_batch_complete": False,
        "phase_path": str(path),
        "queue_path": str(ptr.get("queue_path") or ""),
        "for_founder": {"show_this": f"Batch {ptr.get('batch_id')} ARMED — head {head_now} · automation resumed"},
    }


def handle_queue_action(body: dict[str, Any] | None) -> dict[str, Any]:
    body = body or {}
    action = str(body.get("action") or "get_head").strip().lower()
    if action in ("get_head", "status"):
        return read_head()
    if action == "boot_heal":
        return boot_heal_queue(force=bool(body.get("force")))
    if action == "reset_pack_gate":
        from cloud_auto_runtime_single_cycle_gate_v1 import reset_gate_for_pack, gate_status  # noqa: WPS433

        reset_gate_for_pack()
        return {"ok": True, "schema": "cloud-forge-run-queue-action-v1", "action": "reset_pack_gate", "gate": gate_status()}
    if action == "swap_to_next_batch":
        return swap_to_next_batch(reason=str(body.get("reason") or "api_swap_to_next_batch"))
    if action == "skip_head":
        return skip_head(reason=str(body.get("reason") or "api_skip_head"))
    if action == "skip_to_next_real":
        return skip_to_next_real(
            reason=str(body.get("reason") or "api_skip_to_next_real"),
            max_skips=int(body.get("max_skips") or 12),
        )
    if action == "set_head":
        head = str(body.get("head") or body.get("cloud_forge_run_head") or "")
        if not head:
            return {"ok": False, "error": "head_required"}
        path = phase_path()
        obs = _read(path)
        obs.update(
            {
                "cloud_forge_run_head": head,
                "cloud_forge_run_last_completed": body.get("last_completed") or obs.get("cloud_forge_run_last_completed"),
                "rebuilt_by": "cloud_forge_run_queue_v1.set_head",
                "set_reason": str(body.get("reason") or "founder_set_head"),
            }
        )
        if "queue_batch_complete" in body:
            obs["queue_batch_complete"] = bool(body.get("queue_batch_complete"))
        _write(path, obs)
        return {"ok": True, "head": head, "phase_path": str(path)}
    if action == "seal_registry_exhausted":
        return seal_registry_exhausted(reason=str(body.get("reason") or "api_seal_registry_exhausted"))
    if action == "sync_pointer_from_image":
        return sync_pointer_from_image(reason=str(body.get("reason") or "api_sync_pointer_from_image"))
    if action == "activate_batch":
        return activate_batch(
            reason=str(body.get("reason") or "founder_activate_batch"),
            batch_id=int(body["batch_id"]) if body.get("batch_id") is not None else None,
        )
    return {"ok": False, "error": "unknown_action", "action": action}
