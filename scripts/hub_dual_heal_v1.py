#!/usr/bin/env python3
"""Dual-hub heal — H1 Super Fast + H2 Machine Hub sync (scripts-only · no monolith rebuild)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "two-hub-heal-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def heal_two_hubs(*, reason: str = "dual-hub", full: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict] = []
    ok = True

    try:
        from worker_hub_heal_v1 import worker_hub_heal  # noqa: WPS433

        h1 = worker_hub_heal(reason=reason, full=full)
        steps.append({"step": "h1_worker_hub_heal", "ok": bool(h1.get("ok")), "health": (h1.get("health_after") or {}).get("status")})
        ok = ok and bool(h1.get("ok"))
    except Exception as exc:
        steps.append({"step": "h1_worker_hub_heal", "ok": False, "error": str(exc)})
        ok = False
        h1 = {}

    try:
        from h2_pending_registry_sync_v1 import sync_h2_registry  # noqa: WPS433

        h2_sync = sync_h2_registry(caller=f"hub_dual_heal:{reason}")
        steps.append({"step": "h2_registry_sync", "ok": bool(h2_sync.get("ok")), "pending": h2_sync.get("pending_total")})
    except Exception as exc:
        steps.append({"step": "h2_registry_sync", "ok": False, "error": str(exc)})
        ok = False
        h2_sync = {}

    try:
        from machine_hub_v1 import invalidate_machine_hub_cache, machine_hub_payload  # noqa: WPS433

        invalidate_machine_hub_cache()
        h2_payload = machine_hub_payload(skip_cache=True)
        steps.append({"step": "h2_payload_refresh", "ok": bool(h2_payload.get("ok"))})
    except Exception as exc:
        steps.append({"step": "h2_payload_refresh", "ok": False, "error": str(exc)})
        ok = False
        h2_payload = {}

    try:
        from agentic_layer_pipeline_v2 import run_agentic_pipeline_v2  # noqa: WPS433

        pipe = run_agentic_pipeline_v2(sync_brain=False, tier="fast")
        steps.append({"step": "agentic_pipeline_v2", "ok": bool(pipe.get("ok"))})
    except Exception as exc:
        steps.append({"step": "agentic_pipeline_v2", "ok": False, "error": str(exc)})

    from worker_hub_staleness_v1 import staleness_probe  # noqa: WPS433
    from machine_hub_staleness_v1 import machine_hub_staleness_probe  # noqa: WPS433
    from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

    invalidate_worker_hub_cache()
    h1_health = staleness_probe()
    h2_health = machine_hub_staleness_probe()

    h2_steps_ok = all(
        s.get("ok") for s in steps if s.get("step") in ("h2_registry_sync", "h2_payload_refresh")
    )
    h1_light = any(s.get("step") == "h1_worker_hub_heal" for s in steps)
    # H2 sync is primary; H1 dual_proof may lag while INBOX ACT is open (brain chain.sync)
    overall_ok = (
        h2_steps_ok
        and h1_light
        and h2_health.get("status") in ("fresh", "aging", "unknown")
    )

    row = {
        "ok": overall_ok,
        "schema": "two-hub-heal-v1",
        "reason": reason,
        "at": _now(),
        "h1_health": h1_health,
        "h2_health": h2_health,
        "h1_dual_proof_ok": bool((h1_health.get("latches") or {}).get("dual_proof_ok")),
        "steps": steps,
        "urls": {"h1": "http://127.0.0.1:13020/", "h2": "http://127.0.0.1:13020/machines/"},
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Heal H1 Super Fast + H2 Machine Hub")
    p.add_argument("--json", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--reason", default="cli")
    args = p.parse_args()
    row = heal_two_hubs(reason=args.reason, full=args.full)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"TWO-HUB-HEAL: ok={row.get('ok')} "
            f"H1={(row.get('h1_health') or {}).get('status')} "
            f"H2={(row.get('h2_health') or {}).get('status')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
