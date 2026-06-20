#!/usr/bin/env bash
# sa-0506 — TrustField vault note crosswalk
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
attach = root / "archive/attachments/2026-06-14/sa-0506-trustfield-vault-note_LOCKED_v1.md"
scoreboard = root / "AGENT_SCOREBOARD_LOCKED_v1.md"
assert attach.is_file() and scoreboard.is_file()
assert "vault" in scoreboard.read_text(encoding="utf-8").lower()
PY
echo "OK: validate-trustfield-vault-note-v1 · sa-0506"
