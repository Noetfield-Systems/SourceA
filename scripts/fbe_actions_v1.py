#!/usr/bin/env python3
"""FBE Hub actions — spawn · freeze · resume · retire (W1 stubs)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY_PATH = SINA / "fbe-factory-registry-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def run_action(action: str, *, template_id: str = "web-product-factory-v1") -> dict:
    action = action.strip().lower()
    if action == "spawn":
        from fbe_spawn_factory_v1 import spawn  # noqa: WPS433

        return spawn(template_id=template_id)

    registry = _read_json(REGISTRY_PATH)
    instances = list(registry.get("instances") or [])
    inst = next((i for i in instances if i.get("template_id") == template_id), None)
    if not inst and action != "spawn":
        return {"ok": False, "error": f"no instance {template_id}"}

    if action == "freeze":
        inst["status"] = "frozen"
    elif action == "resume":
        inst["status"] = "w1_adapter_ready"
    elif action == "retire":
        inst["status"] = "retired"
    else:
        return {"ok": False, "error": f"unknown action {action}"}

    inst["updated_at"] = _now()
    registry["instances"] = instances
    registry["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "action": action, "template_id": template_id, "status": inst.get("status"), "at": _now()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", required=True)
    ap.add_argument("--template-id", default="web-product-factory-v1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_action(args.action, template_id=args.template_id)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
