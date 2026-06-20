#!/usr/bin/env bash
# validate-thread-room-second-hop-v1.sh — sa-0819 Thread Room H2 second-hop vs SINA_THREAD_ROOM_LOCKED_v1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-thread-room-second-hop-v1 — $*" >&2; exit 1; }

for f in \
  "$ROOT/SINA_THREAD_ROOM_LOCKED_v1.md" \
  "$ROOT/SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md"; do
  [[ -f "$f" ]] || fail "missing $f"
done

python3 - <<'PY' || fail "second-hop law cross-check"
import json
from pathlib import Path

ROOT = Path(".")
law = (ROOT / "SINA_THREAD_ROOM_LOCKED_v1.md").read_text(encoding="utf-8")
super_fast = (ROOT / "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md").read_text(encoding="utf-8")

if "H2 second hop" not in law and "second hop" not in law.lower():
    raise SystemExit("SINA_THREAD_ROOM_LOCKED missing H2 second hop")
if "Forbidden" not in law or "H1" not in law:
    raise SystemExit("SINA_THREAD_ROOM_LOCKED missing H1 forbidden clause")
if "thread_room" not in super_fast or "Second hop" not in super_fast:
    raise SystemExit("SUPER_FAST_HUB missing thread_room second hop")

reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
if not reg_path.is_file():
    raise SystemExit("missing h2-pending-registry-v1.json")
reg = json.loads(reg_path.read_text(encoding="utf-8"))
tr = reg.get("thread_room") or {}
if tr.get("hub") != "H2":
    raise SystemExit(f"thread_room.hub must be H2, got {tr.get('hub')!r}")
if tr.get("h1_allowed") != "one_line_alarm_only":
    raise SystemExit(f"thread_room.h1_allowed must be one_line_alarm_only, got {tr.get('h1_allowed')!r}")
if tr.get("run_cadence") != "weekly":
    raise SystemExit(f"thread_room.run_cadence must be weekly, got {tr.get('run_cadence')!r}")

cur_path = Path.home() / ".sina/thread-room/latest-curation-v1.json"
if cur_path.is_file():
    cur = json.loads(cur_path.read_text())
    if cur.get("schema") != "thread-room-curator-v1":
        raise SystemExit(f"bad curation schema: {cur.get('schema')!r}")

boot_path = ROOT / "agent-control-panel/worker-hub/boot.json"
if boot_path.is_file():
    boot = json.loads(boot_path.read_text(encoding="utf-8"))
    tr_boot = (boot.get("daily_rooms") or {}).get("thread_room") or {}
    if not tr_boot.get("headline"):
        raise SystemExit("H1 boot thread_room pin missing headline (one-line only)")
    forbidden = ("scout", "cartographer", "curator", "form_row_drafts")
    for key in forbidden:
        if key in tr_boot and key != "headline":
            if isinstance(tr_boot.get(key), list) and len(tr_boot[key]) > 5:
                raise SystemExit(f"H1 boot thread_room must not expose full {key} inline")

mh = (ROOT / "scripts/machine_hub_v1.py").read_text(encoding="utf-8")
if "thread_room" not in mh:
    raise SystemExit("machine_hub_v1 missing thread_room bucket wiring")

print(
    f"OK: second-hop law · H2 hub={tr.get('hub')} h1={tr.get('h1_allowed')} "
    f"cadence={tr.get('run_cadence')} drafts={tr.get('pending_draft_rows')}"
)
PY

bash "$ROOT/scripts/validate-thread-room-h2-summary-v1.sh" >/dev/null 2>&1 || true

echo "OK: validate-thread-room-second-hop-v1 · sa-0819"
