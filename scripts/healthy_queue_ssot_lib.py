"""Healthy queue SSOT — ~/.sina wins over repo (GOAL_HIERARCHY_LOCKED_v1 · INCIDENT-004)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_HOME = Path.home() / ".sina" / "healthy-queue-30-active.json"
QUEUE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
QUEUE_REPO_LEGACY = ROOT / "os" / "plan-library" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
STATE_HOME = Path.home() / ".sina" / "healthy-queue-state-v1.json"
STATE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-state-v1.json"
QUARANTINE_NAME = "healthy-queue-30-active.PARALLEL_COMMERCIAL_QUARANTINED_v1.json"

COMMERCIAL_PHASE = "phase-s5-commercial-lanes"
DEFAULT_PHASE = "phase-s1-eval-dispatch"


def healthy_queue_path() -> Path:
    """Boss queue: ~/.sina when present; repo is fallback only."""
    if QUEUE_HOME.is_file():
        return QUEUE_HOME
    if QUEUE_REPO.is_file():
        return QUEUE_REPO
    return QUEUE_REPO_LEGACY


def healthy_queue_state_path() -> Path:
    """Queue cursor: ~/.sina state when present."""
    if STATE_HOME.is_file():
        return STATE_HOME
    return STATE_REPO


def sync_home_queue_from_repo(*, force: bool = False) -> dict:
    """Keep ~/.sina queue aligned with repo when boss copy drifts (INCIDENT-005)."""
    if not QUEUE_REPO.is_file():
        return {"ok": False, "error": "repo_queue_missing"}
    try:
        repo_data = json.loads(QUEUE_REPO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    repo_items = queue_items(repo_data)
    repo_head = (repo_items[0].get("sa_id") if repo_items else None) or ""
    home_head = ""
    if QUEUE_HOME.is_file():
        try:
            home_items = queue_items(json.loads(QUEUE_HOME.read_text(encoding="utf-8")))
            home_head = (home_items[0].get("sa_id") if home_items else None) or ""
        except (OSError, json.JSONDecodeError):
            home_head = ""
    if force or (repo_head and home_head != repo_head):
        import shutil

        QUEUE_HOME.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(QUEUE_REPO, QUEUE_HOME)
        return {"ok": True, "synced": True, "repo_head": repo_head, "replaced_head": home_head or None}
    return {"ok": True, "synced": False, "repo_head": repo_head, "home_head": home_head}


def load_healthy_queue() -> tuple[Path, dict]:
    path = healthy_queue_path()
    if not path.is_file():
        raise FileNotFoundError("healthy-queue-30-active.json missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from k1_read_gate_v1 import k1_after_queue_read, strict_mode  # noqa: WPS433

        k1 = k1_after_queue_read(path, data)
        if strict_mode() and not k1.get("ok"):
            raise RuntimeError(f"K1 queue read BLOCK: {k1}")
        data["_k1_queue_read"] = k1
    except RuntimeError:
        raise
    except Exception:
        pass
    # Auto-heal: commercial queue in ~/.sina → overwrite with clean repo copy immediately.
    # GOAL_HIERARCHY_LOCKED: sa-05xx = T5 PARALLEL DEFERRED, never default overnight routing.
    if is_commercial_default_queue(data):
        import shutil
        for fallback in (QUEUE_REPO, QUEUE_REPO_LEGACY):
            if fallback.is_file():
                try:
                    fb_data = json.loads(fallback.read_text(encoding="utf-8"))
                    if not is_commercial_default_queue(fb_data):
                        shutil.copy2(fallback, QUEUE_HOME)
                        return QUEUE_HOME, fb_data
                except (OSError, json.JSONDecodeError):
                    pass
    return path, data


def queue_items(data: dict) -> list[dict]:
    return data.get("queue") or data.get("items") or []


def is_commercial_default_queue(data: dict) -> bool:
    """True when queue head is commercial lane — forbidden as CLI/autorun default."""
    items = queue_items(data)
    if not items:
        return False
    phase = (items[0].get("phase") or "").strip()
    sa_id = (items[0].get("sa_id") or "").strip()
    if phase == COMMERCIAL_PHASE:
        return True
    if sa_id.startswith("sa-05"):
        return True
    sa_range = data.get("sa_range") or []
    if sa_range and str(sa_range[0]).startswith("sa-05"):
        return True
    return False


def is_eval_dispatch_queue(data: dict) -> bool:
    items = queue_items(data)
    if not items:
        return False
    phase = (items[0].get("phase") or "").strip()
    return phase == DEFAULT_PHASE or any(
        str((data.get("sa_range") or [""])[0]).startswith("sa-015") for _ in [0]
    )


REGISTRY_PATH = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"


def registry_status_map() -> dict[str, str]:
    if not REGISTRY_PATH.is_file():
        return {}
    try:
        reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        return {str(p.get("id") or "").lower(): str(p.get("status") or "") for p in reg.get("plans") or []}
    except (OSError, json.JSONDecodeError):
        return {}


def registry_status_for_sa(sa_id: str) -> str:
    return registry_status_map().get(str(sa_id or "").lower(), "")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sa_receipt_done(sa_id: str) -> bool:
    """True when receipts/<sa>-receipt.json exists with status DONE."""
    sid = str(sa_id or "").lower()
    if not sid:
        return False
    receipt = ROOT / "receipts" / f"{sid}-receipt.json"
    if not receipt.is_file():
        return False
    try:
        data = json.loads(receipt.read_text(encoding="utf-8"))
        return str(data.get("status") or "").upper() == "DONE"
    except (OSError, json.JSONDecodeError):
        return False


def sa_closeout_complete(sa_id: str) -> bool:
    """REGISTRY done + receipt DONE — must not re-offer on RUN INBOX."""
    sid = str(sa_id or "").lower()
    if not sid:
        return False
    return registry_status_for_sa(sid) == "done" and sa_receipt_done(sid)


def write_phase_strict_idle_queue(*, reason: str = "cycle3_h2_complete", write: bool = True) -> dict:
    """Clear stale phase-strict queue when pack cycle is complete (INCIDENT-017)."""
    doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": "SourceA PHASE_STRICT drain — idle (Goal 1 honest complete)",
        "thread": "STRATEGIC-SLICE",
        "repo": "sourcea",
        "count": 0,
        "rhythm": "3 prompts per sa: check → act → verify+closeout",
        "law": "SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md",
        "generated_at": _now(),
        "phase_strict": True,
        "phase_strict_complete": True,
        "queue_exhausted": True,
        "stop_reason": reason,
        "pick_floor": None,
        "sa_range": [],
        "queue": [],
    }
    state = {
        "next_pos": 1,
        "queue_exhausted": True,
        "last_advanced_at": _now(),
        "last_completed_pos": 0,
        "reset_by": "write_phase_strict_idle_queue",
        "reason": reason,
    }
    if write:
        QUEUE_HOME.parent.mkdir(parents=True, exist_ok=True)
        QUEUE_HOME.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        if QUEUE_REPO.parent.is_dir():
            QUEUE_REPO.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        STATE_HOME.parent.mkdir(parents=True, exist_ok=True)
        STATE_HOME.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        cfg_path = Path.home() / ".sina" / "phase-strict-drain-v1.json"
        if cfg_path.is_file():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                cfg["enabled"] = False
                cfg["idle_at"] = _now()
                cfg["idle_reason"] = reason
                cfg["updated_at"] = _now()
                cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            except (OSError, json.JSONDecodeError):
                pass
    return {"ok": True, "idle": True, "reason": reason, "path": str(QUEUE_HOME)}


def first_open_queue_pos() -> int:
    """First queue index whose sa_id is not done in REGISTRY.

    Phase-strict packs: healthy-queue-state cursor wins over registry inflation
    (registry may mark sa done before CHECK→ACT→VERIFY completes).
    """
    _, raw = load_healthy_queue()
    items = queue_items(raw)
    if not items:
        return len(items) + 1

    registry_pos = len(items) + 1
    status = registry_status_map()
    for idx, item in enumerate(items, start=1):
        sid = str(item.get("sa_id") or "").lower()
        if status.get(sid) != "done" or not sa_receipt_done(sid):
            registry_pos = idx
            break

    if raw.get("phase_strict"):
        state_path = healthy_queue_state_path()
        if state_path.is_file():
            try:
                st = json.loads(state_path.read_text(encoding="utf-8"))
                if st.get("queue_exhausted") or raw.get("queue_exhausted"):
                    return len(items) + 1
                cur = int(st.get("next_pos") or 1)
                if cur > len(items):
                    return len(items) + 1
                if 1 <= cur <= len(items):
                    cur_sa = str(items[cur - 1].get("sa_id") or "").lower()
                    if sa_closeout_complete(cur_sa):
                        for idx in range(cur + 1, len(items) + 1):
                            sid = str(items[idx - 1].get("sa_id") or "").lower()
                            if not sa_closeout_complete(sid):
                                return idx
                        return len(items) + 1
                    if cur <= registry_pos:
                        return cur
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
    # Unified plans (sa-1200+): REGISTRY has no matching rows — use healthy-queue-state cursor.
    if raw.get("plans_unified") or str(raw.get("phase") or "").startswith("phase-unified"):
        state_path = healthy_queue_state_path()
        if state_path.is_file():
            try:
                st = json.loads(state_path.read_text(encoding="utf-8"))
                if st.get("queue_exhausted") or raw.get("queue_exhausted"):
                    return len(items) + 1
                cur = int(st.get("next_pos") or 1)
                if cur > len(items):
                    return len(items) + 1
                if 1 <= cur <= len(items):
                    return cur
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
    # FORGE FACTORY cycle2: healthy-queue-state cursor wins (registry may lag closeout).
    if str(raw.get("era") or "") == "forge_factory_cycle2":
        state_path = healthy_queue_state_path()
        if state_path.is_file():
            try:
                st = json.loads(state_path.read_text(encoding="utf-8"))
                if st.get("queue_exhausted") or raw.get("queue_exhausted"):
                    return len(items) + 1
                cur = int(st.get("next_pos") or 1)
                if cur > len(items):
                    return len(items) + 1
                if 1 <= cur <= len(items):
                    return cur
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
    return registry_pos


_phase_strict_reentry = False


def phase_strict_queue_check() -> dict:
    """INCIDENT-017 — when phase_strict logged, queue head must match queue_sa truth."""
    global _phase_strict_reentry
    if _phase_strict_reentry:
        return {"ok": True, "skipped": True, "reason": "reentry_guard"}
    truth_path = Path.home() / ".sina" / "run-inbox-disk-truth-v1.json"
    if not truth_path.is_file():
        return {"ok": True, "skipped": True, "reason": "no_disk_truth"}
    try:
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    q = truth.get("queue") or {}
    if not q.get("phase_strict"):
        return {"ok": True, "skipped": True, "reason": "phase_strict_off"}
    queue_sa = (q.get("sa_id") or truth.get("queue_sa") or "").strip()
    live_sa = str(truth.get("live_queue_sa") or truth.get("live_queue_sa", "") or "")
    if not live_sa:
        live_sa = queue_sa
    _phase_strict_reentry = True
    try:
        _, raw = load_healthy_queue()
    finally:
        _phase_strict_reentry = False
    items = queue_items(raw)
    head = (items[0].get("sa_id") if items else None) or raw.get("live_queue_sa") or ""
    aligned = not queue_sa or head == queue_sa or head == live_sa
    return {
        "ok": aligned,
        "phase_strict": True,
        "queue_sa": queue_sa,
        "pack_head": head,
        "action": "rebuild phase-strict manifest or align healthy-queue head",
    }
