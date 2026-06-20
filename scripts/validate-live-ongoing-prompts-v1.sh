#!/usr/bin/env bash
# Validate live ongoing next-10 SSOT — cursor-aligned, no gaps.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"

python3 - <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "scripts")
from healthy_queue_ssot_lib import healthy_queue_state_path

SINA = Path.home() / ".sina"
OUT = SINA / "live-ongoing-prompts-next-10-v1.json"
STALE_SEC = 120  # strict in monitor tick; relaxed in manual validate

if not OUT.is_file():
    print("FAIL: missing live-ongoing-prompts-next-10-v1.json — run live_ongoing_prompts_v1.py --rebuild")
    raise SystemExit(1)

data = json.loads(OUT.read_text(encoding="utf-8"))
errors = []

if data.get("schema") != "live-ongoing-prompts-next-10-v1":
    errors.append("bad schema")

state = {}
sp = healthy_queue_state_path()
if sp.is_file():
    state = json.loads(sp.read_text(encoding="utf-8"))
cursor = int(state.get("next_pos") or data.get("cursor_pos") or 1)
if int(data.get("cursor_pos") or 0) != cursor:
    errors.append(f"cursor_pos mismatch file={data.get('cursor_pos')} disk={cursor}")

turns = data.get("turns") or []
if not turns:
    errors.append("empty turns")
elif turns[0].get("queue_pos") != cursor:
    errors.append(f"turns[0].queue_pos={turns[0].get('queue_pos')} != cursor={cursor}")

positions = [int(t.get("queue_pos") or 0) for t in turns]
for i in range(1, len(positions)):
    if positions[i] != positions[i - 1] + 1:
        errors.append(f"gap in slice at pos {positions[i-1]} -> {positions[i]}")
        break

if len(turns) > 10:
    errors.append(f"turns count {len(turns)} > 10")

built = data.get("built_at") or ""
if built:
    try:
        ts = datetime.fromisoformat(built.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        if age > STALE_SEC and __import__("os").environ.get("LIVE_ONGOING_STRICT_AGE") == "1":
            errors.append(f"built_at stale {int(age)}s")
    except ValueError:
        errors.append("bad built_at")

if errors:
    print("FAIL: validate-live-ongoing-prompts-v1", errors)
    raise SystemExit(1)

print(
    f"OK: validate-live-ongoing-prompts-v1 · cursor={cursor} "
    f"turns={len(turns)} head={turns[0].get('sa_id')}/{turns[0].get('queue_role')}"
)
PY
