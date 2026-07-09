#!/usr/bin/env python3
"""Inventory scheduled loops by trigger host: cloud vs local (advisor dispatch 1)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wrangler_crons(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    crons: list[str] = []
    in_triggers = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[triggers]"):
            in_triggers = True
            continue
        if in_triggers and s.startswith("["):
            break
        if in_triggers and s.startswith("crons"):
            m = re.search(r"\[(.*)\]", line.split("=", 1)[-1])
            if m:
                crons.extend(re.findall(r'"([^"]+)"', m.group(1)))
    return crons


def build_inventory() -> dict:
    rows: list[dict] = []

    # CF workers with crons
    workers = ROOT / "cloud" / "workers"
    for wrangler in sorted(workers.glob("*/wrangler.toml")):
        name_m = re.search(r'name\s*=\s*"([^"]+)"', wrangler.read_text(encoding="utf-8"))
        name = name_m.group(1) if name_m else wrangler.parent.name
        crons = _wrangler_crons(wrangler)
        if not crons:
            if "DEPRECATED" in wrangler.read_text(encoding="utf-8", errors="replace")[:500]:
                rows.append(
                    {
                        "loop_id": name,
                        "trigger_host": "cloudflare_piggyback",
                        "alive_when_laptop_closed": True,
                        "note": "cron removed — piggybacks loop-specialist",
                    }
                )
            continue
        for cron in crons:
            rows.append(
                {
                    "loop_id": name,
                    "trigger_host": "cloudflare",
                    "schedule": cron,
                    "alive_when_laptop_closed": True,
                    "migrate_action": "none",
                }
            )

    # GHA — schedule forbidden; event/manual only
    wf_dir = ROOT / ".github" / "workflows"
    for wf in sorted(wf_dir.glob("*.yml")):
        text = wf.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^\s*schedule\s*:", text, re.M):
            rows.append(
                {
                    "loop_id": wf.stem,
                    "trigger_host": "github_actions_schedule",
                    "alive_when_laptop_closed": False,
                    "migrate_action": "MIGRATE_TO_CF — forbidden by cf-only-24-7 law",
                }
            )
            continue
        if "workflow_dispatch" in text:
            rows.append(
                {
                    "loop_id": wf.stem,
                    "trigger_host": "github_actions_manual",
                    "alive_when_laptop_closed": True,
                    "migrate_action": "founder_manual_or_ci_only",
                }
            )

    # Mac-local patterns (founder session — not 24/7 cloud)
    mac_patterns = [
        ("agent_session_gate_run_v1.py", "mac_cursor_session"),
        ("brain-session-start.sh", "mac_founder_session"),
        ("loop_specialist_tick_v1.py", "mac_manual_tick"),
        ("enter-mac-control-plane-v1.sh", "mac_control_plane"),
    ]
    for script, host in mac_patterns:
        if (ROOT / "scripts" / script).is_file():
            rows.append(
                {
                    "loop_id": script,
                    "trigger_host": host,
                    "alive_when_laptop_closed": False,
                    "migrate_action": "by_design_mac_control_plane_or_manual",
                }
            )

    cloud_alive = [r for r in rows if r.get("alive_when_laptop_closed")]
    local_sleep = [r for r in rows if not r.get("alive_when_laptop_closed")]

    return {
        "schema": "loop-trigger-host-inventory-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "one_law": "48h laptop-closed test: only cloudflare + railway + gha_event rows count as alive",
        "summary": {
            "cloud_alive_count": len(cloud_alive),
            "local_or_manual_count": len(local_sleep),
            "diagnosis": "agentic_with_cloud_motors — autonomy_gap = mac_session_triggers + founder_gated_queue",
        },
        "rows": rows,
        "cloud_motors_24_7": [
            "sourcea-loop-specialist-tick-v1 */15",
            "sourcea-cloud-auto-runtime-tick-v1 */10",
            "sourcea-deadman-v1 */30",
        ],
        "missing_for_full_autonomy": [
            "loop_registry migration applied on portfolio-spine",
            "deadman secrets + deploy",
            "widen machine_safe Kaizen recipes",
            "founder_gated items still wait for Sina (by L5/L7 design)",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write data/loop-trigger-host-inventory-v1.json")
    args = parser.parse_args()

    report = build_inventory()
    out = ROOT / "data" / "loop-trigger-host-inventory-v1.json"
    if args.write:
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"OK: loop_trigger_host_inventory — "
            f"cloud_alive={report['summary']['cloud_alive_count']} "
            f"local/manual={report['summary']['local_or_manual_count']}"
        )
        if args.write:
            print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
