#!/usr/bin/env python3
"""Mac fast deploy/dispatch — Hub→cloud proxy, never local motor drain."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


TARGETS: dict[str, dict[str, Any]] = {
    "dispatch": {
        "description": "POST /api/cloud-worker/dispatch/v1 via Hub proxy (Mac OK)",
        "needs_plan_id": True,
    },
    "loop_tick": {
        "description": "POST /api/loop-specialist/tick/v1 via Hub proxy (Mac OK)",
        "path": "/api/loop-specialist/tick/v1",
        "body": {},
    },
    "forge_run": {
        "description": "POST /api/forge/v02/run/v1 via Hub proxy (Mac OK)",
        "path": "/api/forge/v02/run/v1",
        "body": {},
    },
    "brain": {
        "description": "Brain worker deploy-verified (local wrangler, not Railway motor)",
        "cmd": ["bash", str(SCRIPTS / "brain_cli_v1.sh"), "deploy-verified"],
    },
    "cf_tick": {
        "description": "Trigger CF full-pack tick from Mac (motor on cloud)",
        "hub_action": "trigger_cf_tick",
    },
}


def _proxy(*, path: str, body: dict[str, Any], timeout_s: int = 180) -> dict[str, Any]:
    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    return proxy_to_cloud(path=path, body=body, timeout_s=timeout_s)


def _hub_action(action: str, **kwargs: Any) -> dict[str, Any]:
    from cloud_workers_hub_v1 import handle_action  # noqa: WPS433

    body = {"action": action, **kwargs}
    return handle_action(body)


def run(*, target: str, plan_id: str = "", dry_run: bool = False) -> dict[str, Any]:
    spec = TARGETS.get(target)
    if not spec:
        return {"ok": False, "error": "unknown_target", "allowed": sorted(TARGETS)}

    if "cmd" in spec:
        proc = subprocess.run(spec["cmd"], cwd=str(ROOT), capture_output=True, text=True, check=False)
        return {
            "ok": proc.returncode == 0,
            "target": target,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-2000:],
            "returncode": proc.returncode,
        }

    if spec.get("hub_action"):
        return _hub_action(str(spec["hub_action"]), force=False)

    if target == "dispatch":
        if not plan_id:
            return {"ok": False, "error": "plan_id_required", "hint": "--plan-id MAC-CTL-002"}
        return _proxy(
            path="/api/cloud-worker/dispatch/v1",
            body={"plan_id": plan_id, "dry_run": dry_run},
        )

    path = str(spec.get("path") or "")
    body = dict(spec.get("body") or {})
    if dry_run:
        body["dry_run"] = True
    row = _proxy(path=path, body=body)
    row["target"] = target
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac cloud deploy/dispatch fast path")
    ap.add_argument("--target", required=True, choices=sorted(TARGETS))
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run(target=args.target, plan_id=args.plan_id, dry_run=args.dry_run)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
