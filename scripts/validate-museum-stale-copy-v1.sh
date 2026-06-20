#!/usr/bin/env bash
# validate-museum-stale-copy-v1.sh — Zone C founder hero must not daily-steer Prompt feed / auto-send
# Law: SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md · SOURCEA_GOV_META_AUDIT_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-museum-stale-copy-v1 — $*" >&2; exit 1; }

DATA="$ROOT/agent-control-panel/command-data.json"
[[ -f "$DATA" ]] || fail "missing command-data.json (museum projection)"

python3 - <<'PY' "$DATA"
import json
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
founder = (data.get("command_center") or {}).get("founder") or {}
blob = json.dumps(founder, ensure_ascii=False)

patterns = [
    (re.compile(r"Prompt\s+feed", re.I), "Prompt feed"),
    (re.compile(r"auto[- ]?send", re.I), "auto-send"),
    (re.compile(r"Confirm\s+auto", re.I), "Confirm auto"),
    (re.compile(r"Open\s+Sina\s+Command\s*→\s*Prompt", re.I), "Open Sina Command Prompt feed"),
]

hits = [label for pat, label in patterns if pat.search(blob)]
if hits:
    raise SystemExit(
        "FAIL: command_center.founder hero contains daily-steer poison: "
        + ", ".join(hits)
        + " — scrub hero or sync from factory-now only (INCIDENT-033)"
    )

print(f"OK: validate-museum-stale-copy-v1 · founder hero clean · bytes {path.stat().st_size}")
PY

echo "OK: validate-museum-stale-copy-v1"
