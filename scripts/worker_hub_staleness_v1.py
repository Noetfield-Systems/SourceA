#!/usr/bin/env python3
"""Fast anti-staleness probe for Worker Hub — disk only, no full AS bundle."""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SHELL = ROOT / "agent-control-panel" / "command-data-shell.json"
INBOX = SINA / "worker-prompt-inbox-v1.json"
HONEST = SINA / "PROGRAM_1000_HONEST_STATUS.json"
TRUTH = SINA / "run-inbox-disk-truth-v1.json"
FACTORY = SINA / "factory-now-v1.json"
GLANCE = SINA / "commercial-pipeline-glance-v1.json"
BOOT = SINA / "worker-hub-boot-v1.json"
WIRE = SINA / "disk-live-wire-receipt-v1.json"


def _freshest_built_at(*, shell: dict) -> tuple[str | None, str]:
    """Use newest disk timestamp — shell alone is often stale; factory/pipeline are live."""
    candidates: list[tuple[str, str]] = []
    shell_at = shell.get("built_at")
    if shell_at:
        candidates.append((str(shell_at), "command-data-shell.json"))
    for path, key, label in (
        (FACTORY, "at", "factory-now-v1.json"),
        (GLANCE, "at", "commercial-pipeline-glance-v1.json"),
        (BOOT, "built_at", "worker-hub-boot-v1.json"),
        (WIRE, "synced_at", "disk-live-wire-receipt-v1.json"),
    ):
        row = _read_json(path)
        ts = row.get(key)
        if ts:
            candidates.append((str(ts), label))
    if not candidates:
        return None, "none"
    parsed = [(ts, label, _parse_iso(ts)) for ts, label in candidates]
    parsed = [(ts, label, dt) for ts, label, dt in parsed if dt is not None]
    if not parsed:
        return shell_at, "command-data-shell.json"
    parsed.sort(key=lambda x: x[2], reverse=True)
    return parsed[0][0], parsed[0][1]

FORBIDDEN_AUTO = (
    r"auto-run",
    r"auto run",
    r"start auto",
    r"goal 1 auto-run",
)

STALE_SEC = 180
AGING_SEC = 60
CRITICAL_SEC = 600


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        s = str(ts).replace("Z", "+00:00")
        if "T" not in s and len(s) >= 19:
            s = s[:10] + "T" + s[11:]
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def _age_sec(ts: str | None) -> float | None:
    dt = _parse_iso(ts)
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _p0_latch_ok(shell: dict) -> tuple[bool, str]:
    p0 = ((shell.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    na = str(p0.get("next_action") or "")
    low = na.lower()
    for pat in FORBIDDEN_AUTO:
        if re.search(pat, low, re.I):
            return False, f"AS-01: forbidden AUTO-RUN in p0 ({pat})"
    return True, "AS-01 ok"


def staleness_probe(*, built_at: str | None = None, queue_sa_id: str | None = None) -> dict:
    """Return health block for worker-hub API (~ms, no subprocess)."""
    shell = _read_json(SHELL)
    freshest_at, freshest_src = _freshest_built_at(shell=shell)
    built_at = built_at or freshest_at or shell.get("built_at")
    shell_at = shell.get("built_at")
    shell_age = _age_sec(shell_at)
    age = _age_sec(built_at)
    inbox = _read_json(INBOX)
    truth = _read_json(TRUTH)
    honest = _read_json(HONEST)

    issues: list[str] = []
    latches: dict[str, bool] = {}

    p0_ok, p0_msg = _p0_latch_ok(shell)
    latches["as01_p0_no_autorun"] = p0_ok
    if not p0_ok:
        issues.append(p0_msg)

    live_sa = str((truth.get("live_pick") or {}).get("id") or truth.get("live_sa") or "")
    queue_sa = str(queue_sa_id or (truth.get("queue") or {}).get("sa_id") or truth.get("queue_sa") or "")
    dual_ok = not live_sa or not queue_sa or live_sa == queue_sa
    latches["dual_pick_aligned"] = dual_ok
    if not dual_ok:
        issues.append(f"dual_pick drift live={live_sa} queue={queue_sa}")

    inbox_pending = bool(inbox.get("pending"))
    inbox_age = _age_sec(inbox.get("updated_at") or inbox.get("at"))
    if inbox_pending and age is not None and inbox_age is not None and inbox_age < age - 30:
        latches["inbox_fresher_than_shell"] = False
        issues.append("inbox pending but shell older than inbox")
    else:
        latches["inbox_fresher_than_shell"] = True

    honest_age = _age_sec(honest.get("at"))
    if honest_age is not None and honest_age > CRITICAL_SEC:
        latches["honest_status_fresh"] = False
        issues.append(f"PROGRAM_1000_HONEST_STATUS stale ({int(honest_age)}s)")
    else:
        latches["honest_status_fresh"] = True

    factory = _read_json(FACTORY)
    dual_proof_ok = factory.get("dual_proof_ok")
    valid_yes = factory.get("valid_yes")
    brain_vy = factory.get("brain_vy")
    latches["dual_proof_ok"] = True if dual_proof_ok is None else bool(dual_proof_ok)
    if dual_proof_ok is False:
        issues.append(f"dual_proof GAP — brain {brain_vy} vs valid {valid_yes}")

    notes: list[str] = []
    if shell_age is not None and shell_age >= CRITICAL_SEC and age is not None and age < CRITICAL_SEC:
        latches["shell_stale_projection_ok"] = True
        notes.append(
            f"projection shell stale ({int(shell_age)}s) — health uses {freshest_src}"
        )
    elif shell_age is not None and shell_age >= STALE_SEC:
        latches["shell_stale_projection_ok"] = shell_age < CRITICAL_SEC
        if shell_age >= CRITICAL_SEC:
            notes.append(f"projection shell aging ({int(shell_age)}s)")
    else:
        latches["shell_stale_projection_ok"] = True

    if age is None:
        status = "unknown"
        auto_heal = True
    elif not p0_ok or not dual_ok:
        status = "critical"
        auto_heal = True
    elif age >= CRITICAL_SEC:
        status = "critical"
        auto_heal = True
    elif age >= STALE_SEC:
        status = "stale"
        auto_heal = True
    elif age >= AGING_SEC:
        status = "aging"
        auto_heal = False
    else:
        status = "fresh"
        auto_heal = False

    if dual_proof_ok is False:
        auto_heal = True
        if status == "fresh":
            status = "aging"

    return {
        "schema": "worker-hub-staleness-v1",
        "status": status,
        "age_sec": round(age, 1) if age is not None else None,
        "built_at": built_at,
        "freshness_source": freshest_src,
        "shell_age_sec": round(shell_age, 1) if shell_age is not None else None,
        "auto_heal_recommended": auto_heal,
        "latches": latches,
        "issues": issues,
        "notes": notes,
        "poll_interval_sec": 8 if status in ("stale", "critical", "aging") else 15,
        "heal_cooldown_sec": 45,
    }


def health_passes(health: dict) -> bool:
    """True when status + latches are safe — cosmetic notes do not fail."""
    status = health.get("status")
    if status in ("critical", "stale", "unknown"):
        return False
    latches = health.get("latches") or {}
    if latches.get("dual_proof_ok") is False:
        return False
    if not latches.get("as01_p0_no_autorun", True):
        return False
    if not latches.get("dual_pick_aligned", True):
        return False
    if not latches.get("inbox_fresher_than_shell", True):
        return False
    if not latches.get("honest_status_fresh", True):
        return False
    return True


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker hub staleness probe")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = staleness_probe()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"STALENESS: {row.get('status')} age={row.get('age_sec')} heal={row.get('auto_heal_recommended')}")
    return 0 if row.get("status") != "critical" or not row.get("issues") else 1


if __name__ == "__main__":
    raise SystemExit(main())
