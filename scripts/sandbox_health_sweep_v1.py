#!/usr/bin/env python3
"""sandbox_health_sweep_v1 — diff live triggers vs data/trigger-registry-v1.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "trigger-registry-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_wrangler_crons(text: str) -> list[str]:
    crons: list[str] = []
    in_triggers = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[triggers]"):
            in_triggers = True
            continue
        if in_triggers and stripped.startswith("["):
            break
        if in_triggers and stripped.startswith("crons"):
            match = re.search(r"\[(.*)\]", line.split("=", 1)[-1])
            if match:
                inner = match.group(1)
                for part in re.findall(r'"([^"]+)"|\'([^\']+)\'', inner):
                    cron = part[0] or part[1]
                    if cron:
                        crons.append(cron.strip())
    return crons


def _parse_gha_workflow(text: str) -> dict[str, Any]:
    events: list[str] = []
    schedules: list[str] = []
    if re.search(r"^\s*workflow_dispatch\s*:", text, re.MULTILINE):
        events.append("workflow_dispatch")
    if re.search(r"^\s*push\s*:", text, re.MULTILINE):
        events.append("push")
    if re.search(r"^\s*pull_request\s*:", text, re.MULTILINE):
        events.append("pull_request")
    if re.search(r"^\s*workflow_run\s*:", text, re.MULTILINE):
        events.append("workflow_run")
    if re.search(r"^\s*repository_dispatch\s*:", text, re.MULTILINE):
        events.append("repository_dispatch")
    if re.search(r"^\s*schedule\s*:", text, re.MULTILINE):
        events.append("schedule")
        for match in re.finditer(r"cron:\s*['\"]([^'\"]+)['\"]", text):
            schedules.append(match.group(1).strip())
    return {"events": sorted(set(events)), "schedules": schedules}


def _discover_live_wrangler_triggers() -> list[dict[str, Any]]:
    live: list[dict[str, Any]] = []
    workers = ROOT / "cloud" / "workers"
    if not workers.is_dir():
        return live
    for wrangler in sorted(workers.glob("*/wrangler.toml")):
        if (wrangler.parent / "DEPRECATED.md").is_file():
            continue
        text = wrangler.read_text(encoding="utf-8", errors="replace")
        crons = _parse_wrangler_crons(text)
        if not crons:
            continue
        rel = str(wrangler.relative_to(ROOT))
        for cron in crons:
            live.append(
                {
                    "signature": f"wrangler:{rel}:{cron}",
                    "type": "wrangler_cron",
                    "path": rel,
                    "schedule": cron,
                }
            )
    return live


def _discover_live_gha_triggers() -> list[dict[str, Any]]:
    live: list[dict[str, Any]] = []
    workflows = ROOT / ".github" / "workflows"
    if not workflows.is_dir():
        return live
    for wf in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        text = wf.read_text(encoding="utf-8", errors="replace")
        parsed = _parse_gha_workflow(text)
        rel = str(wf.relative_to(ROOT))
        if parsed["schedules"]:
            for cron in parsed["schedules"]:
                live.append(
                    {
                        "signature": f"gha_schedule:{rel}:{cron}",
                        "type": "gha_schedule",
                        "path": rel,
                        "schedule": cron,
                    }
                )
        for event in parsed["events"]:
            if event == "schedule":
                continue
            live.append(
                {
                    "signature": f"gha:{rel}:{event}",
                    "type": "gha_workflow",
                    "path": rel,
                    "event": event,
                }
            )
    return live


def _probe_registry_entry(entry: dict[str, Any]) -> dict[str, Any]:
    probe = entry.get("live_probe") if isinstance(entry.get("live_probe"), dict) else {}
    trigger_id = str(entry.get("trigger_id") or "")
    probe_type = str(probe.get("type") or "")
    if probe_type == "policy_only":
        rel = str(probe.get("path") or "")
        path = ROOT / rel.split("#")[0] if rel and not rel.startswith("data/") else ROOT / rel.split("#")[0]
        if rel.startswith("data/"):
            path = ROOT / rel.split("#")[0]
        ok = path.is_file()
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel,
            "reason": None if ok else "policy_ssot_missing",
        }
    if probe_type == "piggyback":
        host_path = ROOT / str(probe.get("host_path") or "")
        forbidden_path = ROOT / str(probe.get("forbidden_path") or "")
        expected = str(probe.get("host_schedule") or entry.get("schedule") or "")
        if not host_path.is_file():
            return {
                "trigger_id": trigger_id,
                "ok": False,
                "reason": "piggyback_host_missing",
                "path": str(probe.get("host_path") or ""),
            }
        host_crons = _parse_wrangler_crons(host_path.read_text(encoding="utf-8", errors="replace"))
        forbidden_crons: list[str] = []
        if forbidden_path.is_file():
            forbidden_crons = _parse_wrangler_crons(
                forbidden_path.read_text(encoding="utf-8", errors="replace")
            )
        ok = expected in host_crons and len(forbidden_crons) == 0
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": str(probe.get("host_path") or ""),
            "forbidden_path": str(probe.get("forbidden_path") or ""),
            "expected_schedule": expected,
            "host_schedules": host_crons,
            "forbidden_schedules": forbidden_crons,
            "reason": None
            if ok
            else ("forbidden_cron_present" if forbidden_crons else "host_schedule_mismatch"),
        }
    rel_path = str(probe.get("path") or "")
    if probe_type == "dispatch_cron":
        dispatch_rel = str(probe.get("dispatch_path") or "data/loop-specialist-cron-dispatch-v1.json")
        dispatch_path = ROOT / dispatch_rel
        wrangler_rel = str(probe.get("wrangler_path") or "cloud/workers/loop-specialist-tick-v1/wrangler.toml")
        wrangler_path = ROOT / wrangler_rel
        expected = str(probe.get("schedule") or entry.get("schedule") or "")
        match_tid = str(probe.get("match_trigger_id") or entry.get("trigger_id") or "")
        if not dispatch_path.is_file() or not wrangler_path.is_file():
            return {
                "trigger_id": trigger_id,
                "ok": False,
                "path": dispatch_rel,
                "reason": "dispatch_or_wrangler_missing",
            }
        dispatch = _read_json(dispatch_path)
        wrangler_crons = _parse_wrangler_crons(wrangler_path.read_text(encoding="utf-8", errors="replace"))
        wrangler_trigger = str(dispatch.get("wrangler_trigger_cron") or "")
        cron_rows = dispatch.get("crons") if isinstance(dispatch.get("crons"), list) else []
        dispatch_match = next(
            (
                row
                for row in cron_rows
                if isinstance(row, dict)
                and str(row.get("trigger_id") or "") == match_tid
                and str(row.get("cron") or "") == expected
            ),
            None,
        )
        ok = bool(dispatch_match) and wrangler_trigger in wrangler_crons
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": dispatch_rel,
            "wrangler_path": wrangler_rel,
            "expected_schedule": expected,
            "match_trigger_id": match_tid,
            "wrangler_trigger_cron": wrangler_trigger,
            "live_wrangler_schedules": wrangler_crons,
            "reason": None if ok else "dispatch_schedule_mismatch",
        }

    path = ROOT / rel_path
    if not rel_path or not path.is_file():
        return {
            "trigger_id": trigger_id,
            "ok": probe_type == "policy_only",
            "reason": "probe_path_missing",
            "path": rel_path,
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    if probe_type == "wrangler_cron":
        crons = _parse_wrangler_crons(text)
        expected = str(probe.get("schedule") or entry.get("schedule") or "")
        ok = expected in crons
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expected_schedule": expected,
            "live_schedules": crons,
            "reason": None if ok else "schedule_mismatch",
        }
    if probe_type == "piggyback_hook":
        expects = probe.get("expects") if isinstance(probe.get("expects"), list) else []
        missing = [e for e in expects if e not in text]
        ok = not missing
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expects": expects,
            "reason": None if ok else f"missing_hooks:{','.join(missing)}",
        }
    if probe_type == "gha_schedule":
        parsed = _parse_gha_workflow(text)
        expected = str(probe.get("schedule") or entry.get("schedule") or "")
        ok = expected in parsed["schedules"]
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expected_schedule": expected,
            "live_schedules": parsed["schedules"],
            "reason": None if ok else "schedule_mismatch",
        }
    if probe_type == "gha_workflow":
        parsed = _parse_gha_workflow(text)
        expects = probe.get("expects") if isinstance(probe.get("expects"), list) else []
        missing = [e for e in expects if e not in parsed["events"]]
        ok = not missing
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expects": expects,
            "live_events": parsed["events"],
            "reason": None if ok else f"missing_events:{','.join(missing)}",
        }
    return {"trigger_id": trigger_id, "ok": False, "reason": "unknown_probe_type", "path": rel_path}


def run_sweep(*, repo_root: Path | None = None, strict: bool = False) -> dict[str, Any]:
    global ROOT, REGISTRY_PATH  # noqa: PLW0603
    if repo_root is not None:
        ROOT = repo_root
        REGISTRY_PATH = ROOT / "data" / "trigger-registry-v1.json"

    registry = _read_json(REGISTRY_PATH)
    triggers = registry.get("triggers") if isinstance(registry.get("triggers"), list) else []
    probe_results = [_probe_registry_entry(t) for t in triggers if isinstance(t, dict)]
    dead_or_mismatch = [r for r in probe_results if not r.get("ok")]

    live_all = _discover_live_wrangler_triggers() + _discover_live_gha_triggers()
    claimed: set[str] = set()
    for entry in triggers:
        if not isinstance(entry, dict):
            continue
        probe = entry.get("live_probe") if isinstance(entry.get("live_probe"), dict) else {}
        rel = str(probe.get("path") or "")
        probe_type = str(probe.get("type") or "")
        if probe_type == "wrangler_cron":
            claimed.add(f"wrangler:{rel}:{entry.get('schedule')}")
        elif probe_type == "piggyback":
            host_rel = str(probe.get("host_path") or "")
            host_sched = str(probe.get("host_schedule") or entry.get("schedule") or "")
            if host_rel and host_sched:
                claimed.add(f"wrangler:{host_rel}:{host_sched}")
        elif probe_type == "gha_schedule":
            claimed.add(f"gha_schedule:{rel}:{entry.get('schedule')}")
        elif probe_type == "gha_workflow":
            for event in probe.get("expects") or []:
                claimed.add(f"gha:{rel}:{event}")
        elif probe_type == "dispatch_cron":
            dispatch_rel = str(probe.get("dispatch_path") or "data/loop-specialist-cron-dispatch-v1.json")
            match_tid = str(probe.get("match_trigger_id") or entry.get("trigger_id") or "")
            sched = str(probe.get("schedule") or entry.get("schedule") or "")
            claimed.add(f"dispatch:{dispatch_rel}:{match_tid}:{sched}")
        elif probe_type == "session_gate_hook":
            claimed.add(f"session_gate:{rel}")

    unregistered = [row for row in live_all if row["signature"] not in claimed]
    if not strict and not (ROOT / ".github" / "workflows").is_dir():
        unregistered = []
        dead_or_mismatch = [
            r
            for r in dead_or_mismatch
            if r.get("reason") not in ("probe_path_missing", "schedule_mismatch", "missing_events")
            or str(r.get("path", "")).startswith("data/")
        ]

    ok = not dead_or_mismatch and not unregistered
    return {
        "schema": "sandbox-health-sweep-v1",
        "version": "1.1.0",
        "at": _now(),
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)) if REGISTRY_PATH.is_relative_to(ROOT) else str(REGISTRY_PATH),
        "registry_trigger_count": len(triggers),
        "live_trigger_count": len(live_all),
        "probe_results": probe_results,
        "dead_or_mismatch": dead_or_mismatch,
        "unregistered_live": unregistered,
        "ok": ok,
        "drift": not ok,
        "report_line": (
            "trigger_sweep_clean · registry matches live"
            if ok
            else f"trigger_drift · dead={len(dead_or_mismatch)} unregistered={len(unregistered)}"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff live triggers vs trigger-registry-v1.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail if workflow files missing")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    row = run_sweep(repo_root=args.repo_root, strict=args.strict)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
