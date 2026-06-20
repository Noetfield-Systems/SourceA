#!/usr/bin/env python3
"""Append REPO_EXECUTION_LOGS/sourcea on CI pass (sa-0225)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "os" / "plan-library" / "sourcea-1000" / "REGISTRY.json"
LOG_DIR = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"

SKIP_SNIPPETS = (
    "Founder-only:",
    "Founder:",
    "founder Action",
    "founder/lanes:",
    "Wire lane:",
    "TrustField:",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _agent_runnable(title: str) -> bool:
    t = title.lower()
    return not any(s.lower() in t for s in SKIP_SNIPPETS)


def _load_registry() -> dict[str, Any]:
    if not REG.is_file():
        return {}
    return json.loads(REG.read_text(encoding="utf-8"))


def _task_num(task_id: str) -> int:
    if not task_id.startswith("sa-"):
        return -1
    try:
        return int(task_id.split("-", 1)[1])
    except ValueError:
        return -1


def _last_done_task(reg: dict[str, Any]) -> str | None:
    done = [
        p
        for p in reg.get("plans") or []
        if p.get("status") == "done" and str(p.get("id") or "").startswith("sa-")
    ]
    if not done:
        return None
    return max(done, key=lambda p: _task_num(str(p.get("id") or ""))).get("id")


def _next_pick_task(reg: dict[str, Any]) -> str | None:
    from queue_sa_pick_lib_v1 import queue_sa_from_disk  # noqa: WPS433
    from sourcea_pick_lib import pick_backlog_plans  # noqa: WPS433

    qsa = queue_sa_from_disk()
    if qsa:
        return qsa
    picked = pick_backlog_plans(
        reg.get("plans") or [],
        tiers=["T0", "T1", "T2", "T3"],
        limit=1,
        order="phase-first",
    )
    return picked[0].get("id") if picked else None


def _read_latest() -> dict[str, Any]:
    latest = LOG_DIR / "latest.yaml"
    if not latest.is_file():
        return {}
    out: dict[str, Any] = {}
    for raw in latest.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip("'\"")
        if val.lower() == "true":
            out[key] = True
        elif val.lower() == "false":
            out[key] = False
        elif val:
            out[key] = val
    return out


def append_on_ci_pass(*, gate: str = "find_critical_bugs") -> dict[str, Any]:
    """Write stamped CI-pass YAML + refresh latest.yaml (sa-0225)."""
    reg = _load_registry()
    prior = _read_latest()
    last_task = prior.get("last_task") or _last_done_task(reg) or "unknown"
    next_task = _next_pick_task(reg) or prior.get("next_task") or "unknown"
    reported_at = _now()

    latest_body = (
        f"schema_version: 1\n"
        f"repo: sourcea\n"
        f"last_task: {last_task}\n"
        f"status: ci_pass\n"
        f"verify_passed: true\n"
        f"next_task: {next_task}\n"
        f"reported_at: '{reported_at}'\n"
        f"ci_gate: {gate}\n"
    )
    detail_body = (
        f"schema_version: 1\n"
        f"repo: sourcea\n"
        f"event: ci_pass\n"
        f"task: CI pass — {gate}\n"
        f"status: passed\n"
        f"verify_passed: true\n"
        f"evidence:\n"
        f"  task_id: ci_pass\n"
        f"  gate: SINA_AUDIT_STRICT=1 build-sina-command-panel.py && find_critical_bugs.py\n"
        f"  last_task: {last_task}\n"
        f"  next_task: {next_task}\n"
        f"tests:\n"
        f"  status: passed\n"
        f"  command: {gate}\n"
        f"  output_snippet: critical 0\n"
        f"reported_at: '{reported_at}'\n"
        f"reporter: append_repo_execution_log_v1\n"
    )
    detail_path = LOG_DIR / f"{_stamp()}_ci-pass.yaml"
    latest_path = LOG_DIR / "latest.yaml"
    _write_atomic(detail_path, detail_body)
    _write_atomic(latest_path, latest_body)
    print(
        f"OK: append_repo_execution_log_v1 CI pass (sa-0225) · "
        f"last={last_task} next={next_task} · {detail_path.name}"
    )
    return {
        "ok": True,
        "last_task": last_task,
        "next_task": next_task,
        "detail": str(detail_path.relative_to(ROOT)),
        "latest": str(latest_path.relative_to(ROOT)),
    }


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Append REPO_EXECUTION_LOGS on CI pass")
    p.add_argument("--gate", default="find_critical_bugs")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = append_on_ci_pass(gate=args.gate)
    if args.json:
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
