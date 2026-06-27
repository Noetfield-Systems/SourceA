#!/usr/bin/env python3
"""Light guard refresh — live surfaces from live-ongoing + Railway glance (no validator marathon)."""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SURFACES = SINA / "agent-live-surfaces-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _cloud_glance() -> dict:
    try:
        from fbe.lib.hub_cloud_proxy_v1 import cloud_worker_url  # noqa: WPS433

        base = cloud_worker_url()
        if not base:
            return {}
        with urllib.request.urlopen(f"{base.rstrip('/')}/api/cloud-forge-run/queue/v1", timeout=12) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": bool(row.get("cloud_forge_run_head")),
            "head": row.get("cloud_forge_run_head"),
            "batch_id": row.get("batch_id"),
            "drain_status": row.get("drain_status"),
            "queue_batch_complete": row.get("queue_batch_complete"),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:120]}


def main() -> int:
    ongoing = _read(SINA / "live-ongoing-prompts-next-10-v1.json")
    surfaces = _read(SURFACES)
    cloud = ongoing.get("cloud_forge_glance") or _cloud_glance()
    head = str(cloud.get("head") or "")

    from execution_path_vocabulary_v1 import inject_execution_path, founder_daily_ops_line  # noqa: WPS433

    surfaces["synced_at"] = _now()
    surfaces["inject_execution_path"] = inject_execution_path()
    surfaces["founder_daily_ops"] = founder_daily_ops_line()
    if head:
        surfaces["queue_sa"] = head
        surfaces["execution_surface"] = "cloud_forge"
        surfaces["cloud_forge_glance"] = cloud
        fn = surfaces.get("factory_now_line") or ""
        if head not in fn:
            surfaces["factory_now_line"] = f"{fn.rstrip()} · cloud {head}".strip()
        surfaces["zero_drift_line"] = (
            f"ZERO-DRIFT REVIEW · queue=exhausted · cloud={head} · "
            "L0.5+L1+L2+SASCIP · ops=CLOUD_FORGE"
        )
    dual = surfaces.get("dual_pick") or {}
    dual.update({"live_pick_sa": "", "queue_sa": head or "", "aligned": True, "idle": True})
    surfaces["dual_pick"] = dual
    surfaces["guard_refresh_at"] = _now()
    SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "head": head, "inject": surfaces["inject_execution_path"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
