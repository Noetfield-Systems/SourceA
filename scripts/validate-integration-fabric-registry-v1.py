#!/usr/bin/env python3
"""Validate ~/.sina/integration-fabric-registry-v1.yaml — required rows + disk receipts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REGISTRY = Path.home() / ".sina/integration-fabric-registry-v1.yaml"
ROOT = Path(__file__).resolve().parents[1]

REQUIRED_API_IDS = frozenset(
    {
        "agent-session-gate",
        "agent-memory-mirror",
        "live-founder-form",
        "judge-center-batch",
        "thread-room-batch",
        "hub-judge-alarm-strip",
        "anti-staleness-bundle",
    }
)

REQUIRED_RECEIPTS = [
    Path.home() / ".sina/live-founder-decision-form-v1.json",
    Path.home() / ".sina/judge-center/latest-resolution-v1.json",
    Path.home() / ".sina/judge-center/latest-alarm-strip-v1.json",
    Path.home() / ".sina/thread-room/latest-curation-v1.json",
    Path.home() / ".sina/agent-memory-mirror-v1.json",
]

REQUIRED_SCRIPTS = [
    ROOT / "scripts/judge_center_run_v1.py",
    ROOT / "scripts/thread_room_run_v1.py",
    ROOT / "scripts/hub_judge_alarm_strip_v1.py",
    ROOT / "scripts/live_founder_decision_form_v1.py",
    ROOT / "scripts/agent_session_gate_run_v1.py",
]


def _load_registry() -> dict:
    if not REGISTRY.is_file():
        raise FileNotFoundError(f"missing registry: {REGISTRY}")
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    text = REGISTRY.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    # minimal fallback without PyYAML
    row: dict = {"schema": "integration-fabric-registry-v1", "apis": []}
    if "schema: integration-fabric-registry-v1" not in text:
        raise ValueError("invalid schema line")
    if "status: running" not in text:
        raise ValueError("status must be running")
    for line in text.splitlines():
        if line.strip().startswith("- id:"):
            api_id = line.split(":", 1)[1].strip()
            row.setdefault("apis", []).append({"id": api_id})
    for section in ("golden_rules", "authority_rows", "megachat_anchors", "n8n_workflows"):
        if f"{section}:" not in text:
            raise ValueError(f"missing section: {section}")
    row["status"] = "running"
    return row


def validate(*, json_out: bool = False) -> dict:
    errors: list[str] = []
    reg = _load_registry()

    if reg.get("schema") != "integration-fabric-registry-v1":
        errors.append("schema must be integration-fabric-registry-v1")
    if reg.get("status") not in ("running", "stub_running"):
        errors.append(f"unexpected status: {reg.get('status')}")

    apis = reg.get("apis") or []
    if isinstance(apis, list):
        api_ids = {a.get("id") for a in apis if isinstance(a, dict)}
    else:
        api_ids = set()
    missing = REQUIRED_API_IDS - api_ids
    if missing:
        errors.append(f"missing api ids: {sorted(missing)}")

    for p in REQUIRED_RECEIPTS:
        if not p.is_file():
            errors.append(f"missing receipt: {p}")

    for p in REQUIRED_SCRIPTS:
        if not p.is_file():
            errors.append(f"missing script: {p}")

    if not (ROOT / "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md").is_file():
        errors.append("missing live founder form law")

    rooms = reg.get("authority_rows") or {}
    for room in ("FORM_OFFICE", "JUDGE_CENTER", "THREAD_ROOM", "DISK_MACHINE"):
        if isinstance(rooms, dict) and room not in rooms:
            errors.append(f"missing authority_rows.{room}")

    result = {
        "ok": not errors,
        "schema": "integration-fabric-registry-validate-v1",
        "registry_path": str(REGISTRY),
        "registry_status": reg.get("status"),
        "api_count": len(apis) if isinstance(apis, list) else 0,
        "errors": errors,
    }
    return result


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        result = validate()
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)]}
    if args.json:
        print(json.dumps(result, indent=2))
    elif result.get("ok"):
        print(
            f"OK: validate-integration-fabric-registry-v1 · apis={result.get('api_count')} · "
            f"path={REGISTRY}"
        )
    else:
        print("FAIL: validate-integration-fabric-registry-v1", file=sys.stderr)
        for e in result.get("errors") or []:
            print(f"  - {e}", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
