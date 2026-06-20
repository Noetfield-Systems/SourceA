"""Commercial / live-eval blockers — never queue ACT/VERIFY for impossible sa."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "os/plan-library/sourcea-1000/REGISTRY.json"
BLOCKERS = Path.home() / ".sina/healthy-queue-blockers-v1.json"
CI_MODE = Path.home() / ".sina/eval_1b_ci_mode_v1.json"

LIVE_EVAL_MARKERS = (
    "eval_1b_gate_ok",
    "eval-1b live",
    "validate-eval-packet-v1b-live",
    "openrouter",
)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def live_eval_available() -> tuple[bool, str]:
    """True only when OpenRouter live probe passes (not structural_only / 402)."""
    row = _read_json(CI_MODE)
    if row.get("live_probe_ok") is True and row.get("mode") == "live":
        return True, row.get("reason") or "live"
    reason = row.get("reason") or "structural_only"
    if reason == "openrouter_402":
        return False, "openrouter_402"
    return False, reason


def _blob_has_live_eval(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in LIVE_EVAL_MARKERS)


def sa_requires_live_eval(sa: dict, *, scope: str = "full") -> bool:
    """Whether sa honestly needs live Eval-1b / OpenRouter.

    scope=instruction — CHECK/ACT skip decision (queue item instruction only).
    scope=full — pack filtering (includes verify block in prompt file).
    """
    if sa.get("live_eval_required") is False:
        return False
    if sa.get("live_eval_required") is True:
        return True
    forbidden = sa.get("forbidden") or []
    if any("openrouter" in str(x).lower() or "eval_1b" in str(x).lower() for x in forbidden):
        return False
    keys = ("instruction", "title") if scope == "instruction" else ("title", "verify", "agent_prompt", "path", "id")
    blob = " ".join(str(sa.get(k) or "") for k in keys).lower()
    if _blob_has_live_eval(blob):
        return True
    if scope == "full":
        path = sa.get("path") or sa.get("sa_path") or ""
        if path:
            full = ROOT / path if not str(path).startswith("/") else Path(path)
            if not full.is_file():
                full = ROOT / "os/plan-library/sourcea-1000/prompts" / str(path).split("prompts/", 1)[-1]
            if full.is_file():
                blob += " " + full.read_text(encoding="utf-8", errors="replace").lower()
        return _blob_has_live_eval(blob)
    return False


def blocker_after_check(*, sa_id: str, queue_role: str, queue_item: dict | None = None) -> dict | None:
    """After CHECK: if ACT/VERIFY needs live eval but credits blocked → skip slice."""
    if queue_role != "check":
        return None
    sa = dict(queue_item or {})
    if not sa.get("id") and not sa.get("sa_id"):
        plans = _read_json(REG).get("plans") or []
        sa = next((p for p in plans if p.get("id") == sa_id), {"id": sa_id})
    sa.setdefault("id", sa_id)
    if not sa_requires_live_eval(sa, scope="instruction"):
        return None
    ok, reason = live_eval_available()
    if ok:
        return None
    return {
        "sa_id": sa_id,
        "blocked": True,
        "reason": reason,
        "action": "STOP_AFTER_CHECK",
        "message": (
            f"{sa_id} requires live Eval-1b/OpenRouter — {reason}. "
            "SKIP ACT+VERIFY; do NOT mark REGISTRY done; pick next achievable sa."
        ),
        "founder_action": "Top up OpenRouter credits — then regenerate healthy queue",
    }


def record_blocker(row: dict) -> None:
    data = _read_json(BLOCKERS)
    items = [x for x in (data.get("items") or []) if x.get("sa_id") != row.get("sa_id")]
    items.append({**row, "recorded_at": row.get("recorded_at") or _now()})
    data["items"] = items[-50:]
    data["schema"] = "healthy-queue-blockers-v1"
    BLOCKERS.parent.mkdir(parents=True, exist_ok=True)
    BLOCKERS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def filter_achievable_picks(plans: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split backlog into achievable now vs blocked on live eval."""
    ok, reason = live_eval_available()
    if ok:
        return plans, []
    achievable, blocked = [], []
    for p in plans:
        if sa_requires_live_eval(p):
            blocked.append({**p, "block_reason": reason})
        else:
            achievable.append(p)
    return achievable, blocked
