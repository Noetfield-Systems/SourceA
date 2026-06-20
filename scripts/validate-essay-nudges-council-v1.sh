#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from agent_essay_discourse import essay_discourse_payload
from pathlib import Path

lib = Path("sina_command_lib.py").read_text(encoding="utf-8")
assert "essay_discourse" in lib and "council_room" in lib, "council must embed essay_discourse"

ed = essay_discourse_payload()
nudges = ed.get("essay_nudges") or []
assert isinstance(nudges, list), "essay_nudges must be list"
assert "nudge_count" in ed, "nudge_count required"
assert "sa-0316" in Path("agent_essay_discourse.py").read_text(encoding="utf-8"), "sa-0316 marker"
print(f"OK: validate-essay-nudges-council-v1 · {len(nudges)} essay_nudges for council (sa-0316)")
PY
