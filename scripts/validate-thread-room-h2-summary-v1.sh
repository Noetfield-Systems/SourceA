#!/usr/bin/env bash
# validate-thread-room-h2-summary-v1.sh — sa-0809 H2 thread_room headline vs latest-curation-v1.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-thread-room-h2-summary-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "thread_room H2 summary alignment"
import json
from pathlib import Path

cur_path = Path.home() / ".sina/thread-room/latest-curation-v1.json"
reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
boot_path = Path("agent-control-panel/worker-hub/boot.json")

if not cur_path.is_file():
    raise SystemExit("missing latest-curation-v1.json")
if not reg_path.is_file():
    raise SystemExit("missing h2-pending-registry-v1.json")
if not boot_path.is_file():
    raise SystemExit("missing worker-hub/boot.json")

cur = json.loads(cur_path.read_text(encoding="utf-8"))
reg = json.loads(reg_path.read_text(encoding="utf-8"))
boot = json.loads(boot_path.read_text(encoding="utf-8"))

summary = (cur.get("executive_summary") or "").strip()
tr_reg = reg.get("thread_room") or {}
h2_head = (tr_reg.get("headline") or "").strip()
tr_boot = (boot.get("daily_rooms") or {}).get("thread_room") or {}
boot_head = (tr_boot.get("headline") or "").strip()

if tr_reg.get("hub") != "H2":
    raise SystemExit(f"thread_room.hub must be H2, got {tr_reg.get('hub')!r}")
if cur.get("schema") != "thread-room-curator-v1":
    raise SystemExit(f"bad curation schema: {cur.get('schema')!r}")
if summary != h2_head:
    raise SystemExit("h2-pending-registry headline != curation executive_summary")
if summary != boot_head:
    raise SystemExit("worker-hub boot daily_rooms.thread_room.headline != curation executive_summary")
drafts = len(cur.get("form_row_drafts") or [])
pending = int(tr_reg.get("pending_draft_rows") or 0)
if pending != drafts:
    raise SystemExit(f"pending_draft_rows {pending} != form_row_drafts {drafts}")

case_id = cur.get("case_id") or ""
if tr_boot.get("case_id") != case_id:
    raise SystemExit(f"boot case_id {tr_boot.get('case_id')!r} != curation {case_id!r}")

print(
    f"OK: validate-thread-room-h2-summary-v1 · case_id={case_id} "
    f"drafts={drafts} · H2 registry + boot match curation"
)
PY

echo "OK: validate-thread-room-h2-summary-v1 · sa-0809"
