#!/usr/bin/env bash
# command-data.json eval_packet win_pct must match ~/.sina live reports (no stale hub drift).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 - <<'PY'
import json
import os
import sys
from pathlib import Path

root = Path(os.environ["ROOT"])
cmd_path = root / "agent-control-panel" / "command-data.json"
v1_disk = Path.home() / ".sina" / "eval_packet_v1_report.json"
v1b_disk = Path.home() / ".sina" / "eval_packet_v1b_report.json"

errors: list[str] = []

def load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def cmp_int(label: str, hub_val, disk_val) -> None:
    if hub_val is None and disk_val is None:
        return
    if hub_val is None or disk_val is None:
        errors.append(f"{label}: missing hub={hub_val} disk={disk_val}")
        return
    if int(hub_val) != int(disk_val):
        errors.append(f"{label}: hub={hub_val} disk={disk_val}")


if not cmd_path.is_file():
    errors.append("missing agent-control-panel/command-data.json — run build-sina-command-panel.py")
else:
    cmd = load(cmd_path)
    sr = cmd.get("system_roadmap") or {}
    hub_v1 = sr.get("eval_packet") or {}
    hub_v1b = sr.get("eval_packet_v1b") or {}
    disk_v1 = load(v1_disk)
    disk_v1b = load(v1b_disk)

    if not disk_v1:
        errors.append(f"missing {v1_disk}")
    if not disk_v1b:
        errors.append(f"missing {v1b_disk}")

    cmp_int("eval-1 packet_win_pct", hub_v1.get("packet_win_pct"), disk_v1.get("packet_win_pct"))
    cmp_int("eval-1 packet_wins", hub_v1.get("packet_wins"), disk_v1.get("packet_wins"))
    cmp_int("eval-1 task_count", hub_v1.get("task_count"), disk_v1.get("task_count"))

    cmp_int("eval-1b packet_win_pct", hub_v1b.get("packet_win_pct"), disk_v1b.get("packet_win_pct"))
    cmp_int("eval-1b scaffold_win_pct", hub_v1b.get("scaffold_win_pct"), disk_v1b.get("scaffold_win_pct"))
    cmp_int("eval-1b scaffold_wins", hub_v1b.get("scaffold_wins"), disk_v1b.get("scaffold_wins"))
    cmp_int("eval-1b task_count", hub_v1b.get("task_count"), disk_v1b.get("task_count"))

    if hub_v1b.get("mode") and disk_v1b.get("mode") and hub_v1b.get("mode") != disk_v1b.get("mode"):
        errors.append(f"eval-1b mode: hub={hub_v1b.get('mode')} disk={disk_v1b.get('mode')}")

    if hub_v1.get("ok") is not None and disk_v1.get("ok") is not None and hub_v1.get("ok") != disk_v1.get("ok"):
        errors.append(f"eval-1 ok: hub={hub_v1.get('ok')} disk={disk_v1.get('ok')}")
    if hub_v1b.get("scaffold_ok") is not None and disk_v1b.get("scaffold_ok") is not None:
        if hub_v1b.get("scaffold_ok") != disk_v1b.get("scaffold_ok"):
            errors.append(
                f"eval-1b scaffold_ok: hub={hub_v1b.get('scaffold_ok')} disk={disk_v1b.get('scaffold_ok')}"
            )

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print("OK: validate-command-data-eval-win-pct-v1 · command-data matches ~/.sina eval reports")
PY
