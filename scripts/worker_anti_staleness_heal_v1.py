#!/usr/bin/env python3
"""Worker fast anti-staleness probe + auto-heal — loop default (~1–8s, no full fleet).

Law: WORKER_FAST_ANTI_STALENESS_AUTO_HEAL_LOCKED_v1.md
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
COOLDOWN_PATH = SINA / "worker-as-heal-cooldown-v1.json"
RECEIPT_PATH = SINA / "worker-as-heal-receipt-v1.json"
DEFAULT_COOLDOWN_SEC = 45


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cooldown_ok(*, cooldown_sec: int = DEFAULT_COOLDOWN_SEC) -> bool:
    if not COOLDOWN_PATH.is_file():
        return True
    try:
        row = json.loads(COOLDOWN_PATH.read_text(encoding="utf-8"))
        at = row.get("at") or ""
        if not at:
            return True
        dt = datetime.fromisoformat(str(at).replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        return age >= cooldown_sec
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return True


def _touch_cooldown() -> None:
    COOLDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    COOLDOWN_PATH.write_text(json.dumps({"schema": "worker-as-heal-cooldown-v1", "at": _now()}, indent=2) + "\n")


def worker_anti_staleness_heal(
    *,
    reason: str = "worker-loop",
    force: bool = False,
    deep: bool = False,
) -> dict:
    """Fast anti-staleness + auto-heal for Worker loop entry/verify."""
    sys.path.insert(0, str(SCRIPTS))
    t0 = time.monotonic()
    steps: list[dict] = []

    if reason in ("safety", "founder-safety", "founder-ecosystem-safety"):
        from worker_hub_safety_v1 import run_h1_safety  # noqa: WPS433
        from worker_hub_staleness_v1 import staleness_probe  # noqa: WPS433
        from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

        safety = run_h1_safety()
        steps.append(
            {
                "step": "ecosystem_safety",
                "ok": bool(safety.get("ok")),
                "message": safety.get("message"),
            }
        )
        invalidate_worker_hub_cache()
        health_after = staleness_probe()
        ms = round((time.monotonic() - t0) * 1000)
        row = {
            "ok": bool(safety.get("ok")),
            "schema": "worker-anti-staleness-heal-v1",
            "reason": reason,
            "healed": False,
            "safety": True,
            "message": safety.get("message"),
            "ms": ms,
            "health_after": health_after,
            "steps": steps,
            "at": _now(),
        }
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    from worker_hub_staleness_v1 import staleness_probe  # noqa: WPS433
    from machine_hub_staleness_v1 import machine_hub_staleness_probe  # noqa: WPS433

    health_before = staleness_probe()
    h2_health_before = machine_hub_staleness_probe()
    steps.append({"step": "probe", "ok": True, "status": health_before.get("status")})
    steps.append({"step": "h2_probe", "ok": True, "status": h2_health_before.get("status")})

    try:
        from brain_governance_wire_v1 import wire_brain_governance  # noqa: WPS433

        wire = wire_brain_governance(sync_brain=False)
        steps.append(
            {
                "step": "brain_l2_wire",
                "ok": bool(wire.get("ok")),
                "queue_head": (wire.get("queue_head") or {}).get("sa_id"),
                "l2_count": len((wire.get("l2_wired") or {}).get("agents") or []),
            }
        )
    except Exception as exc:
        steps.append({"step": "brain_l2_wire", "ok": False, "error": str(exc)})

    need_heal = (
        bool(health_before.get("auto_heal_recommended"))
        or bool(h2_health_before.get("auto_heal_recommended"))
        or health_before.get("status") in ("stale", "critical", "unknown")
        or h2_health_before.get("status") in ("stale", "critical", "unknown")
    )

    # Always: kill hung validators (cheap · prevents 3 min shell)
    try:
        from worker_stuck_recovery_v1 import kill_hung_processes, sync_orchestrator_from_inbox  # noqa: WPS433

        killed = kill_hung_processes()
        steps.append({"step": "kill_hung", "ok": True, "count": killed.get("count", 0)})
        sync = sync_orchestrator_from_inbox()
        steps.append({"step": "orch_inbox_sync", "ok": sync.get("ok", False), "synced": sync.get("synced")})
    except Exception as exc:
        steps.append({"step": "kill_hung", "ok": False, "error": str(exc)})

    if deep:
        try:
            from worker_stuck_recovery_v1 import run_recovery  # noqa: WPS433

            rec = run_recovery(redeliver=False)
            steps.append({"step": "stuck_recovery_deep", "ok": rec.get("ok", False)})
        except Exception as exc:
            steps.append({"step": "stuck_recovery_deep", "ok": False, "error": str(exc)})

    hub_healed = False
    founder_tap = reason in ("founder", "founder-tap", "auto-stale", "cli") or str(reason).startswith("founder")
    run_hub_heal = need_heal or founder_tap or force
    if run_hub_heal and (force or founder_tap or _cooldown_ok(cooldown_sec=int(health_before.get("heal_cooldown_sec") or DEFAULT_COOLDOWN_SEC))):
        try:
            from worker_hub_heal_v1 import worker_hub_heal  # noqa: WPS433

            heal_row = worker_hub_heal(reason=reason)
            hub_healed = True
            _touch_cooldown()
            steps.append(
                {
                    "step": "hub_heal",
                    "ok": heal_row.get("ok", False),
                    "status_after": (heal_row.get("health_after") or {}).get("status"),
                }
            )
        except Exception as exc:
            steps.append({"step": "hub_heal", "ok": False, "error": str(exc)})
    elif need_heal and h2_health_before.get("auto_heal_recommended"):
        try:
            from h2_pending_registry_sync_v1 import sync_h2_registry  # noqa: WPS433
            from machine_hub_v1 import invalidate_machine_hub_cache  # noqa: WPS433

            sync_h2_registry(caller=f"worker_anti_staleness:{reason}")
            invalidate_machine_hub_cache()
            steps.append({"step": "h2_registry_sync", "ok": True, "skipped": "cooldown_h1"})
        except Exception as exc:
            steps.append({"step": "h2_registry_sync", "ok": False, "error": str(exc)})
    elif need_heal:
        steps.append({"step": "hub_heal", "ok": True, "skipped": "cooldown"})

    try:
        from worker_inject_lib import INBOX_JSON, heal_inbox_meta, inbox_status  # noqa: WPS433

        inbox = inbox_status()
        if inbox.get("pending") and INBOX_JSON.is_file():
            data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
            meta = data.get("meta") or {}
            prompt = data.get("prompt") or ""
            healed_meta = heal_inbox_meta(meta, prompt)
            if healed_meta.get("sa_id") != meta.get("sa_id"):
                data["meta"] = healed_meta
                INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                steps.append({"step": "inbox_meta_heal", "ok": True, "sa_id": healed_meta.get("sa_id")})
            else:
                steps.append({"step": "inbox_meta_heal", "ok": True, "skipped": True})
        else:
            steps.append({"step": "inbox_meta_heal", "ok": True, "skipped": True})
    except Exception as exc:
        steps.append({"step": "inbox_meta_heal", "ok": False, "error": str(exc)})

    from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

    invalidate_worker_hub_cache()
    health_after = staleness_probe()
    h2_health_after = machine_hub_staleness_probe()
    ms = round((time.monotonic() - t0) * 1000)

    # Pass on real latch/status failures only — cosmetic shell notes are not blockers
    try:
        from worker_hub_staleness_v1 import health_passes  # noqa: WPS433

        ok = health_passes(health_after)
    except Exception:
        ok = health_after.get("status") in ("fresh", "aging") and not (health_after.get("issues") or [])

    row = {
        "ok": ok,
        "schema": "worker-anti-staleness-heal-v1",
        "reason": reason,
        "healed": hub_healed,
        "deep": deep,
        "ms": ms,
        "health_before": health_before,
        "health_after": health_after,
        "h2_health_before": h2_health_before,
        "h2_health_after": h2_health_after,
        "steps": steps,
        "at": _now(),
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker fast anti-staleness auto-heal")
    p.add_argument("--json", action="store_true")
    p.add_argument("--probe", action="store_true", help="Probe only")
    p.add_argument("--force", action="store_true", help="Bypass heal cooldown")
    p.add_argument("--deep", action="store_true", help="Full stuck recovery (Unstick class)")
    p.add_argument("--reason", default="cli")
    args = p.parse_args()

    if args.probe:
        sys.path.insert(0, str(SCRIPTS))
        from worker_hub_staleness_v1 import staleness_probe  # noqa: WPS433

        row = staleness_probe()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"PROBE: {row.get('status')} heal={row.get('auto_heal_recommended')}")
        return 0 if not (row.get("issues")) else 1

    row = worker_anti_staleness_heal(reason=args.reason, force=args.force, deep=args.deep)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"AS-HEAL: ok={row.get('ok')} {row.get('ms')}ms "
            f"before={row['health_before'].get('status')} "
            f"after={row['health_after'].get('status')} healed={row.get('healed')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
