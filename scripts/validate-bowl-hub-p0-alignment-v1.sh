#!/usr/bin/env bash
# validate-bowl-hub-p0-alignment-v1.sh — bowl duties vs hub P0 id (AS-06)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import json
import sys
from pathlib import Path

bowl = Path("sina-bowl/state.json")
cmd = Path("agent-control-panel/command-data.json")
prog = Path("PROGRAM_PROGRESS.json")

for p in (bowl, cmd):
    if not p.is_file():
        print(f"FAIL: missing {p}")
        sys.exit(1)

b = json.loads(bowl.read_text(encoding="utf-8"))
c = json.loads(cmd.read_text(encoding="utf-8"))
p0_hub = ((c.get("command_center") or {}).get("founder") or {}).get("p0") or {}
hub_id = str(p0_hub.get("id") or "")

locks = {}
if prog.is_file():
    locks = (json.loads(prog.read_text(encoding="utf-8")).get("locks") or {})

prog_p0 = str(locks.get("p0_sku") or "")
duties = " ".join(b.get("asf_duties") or [])

if "Confirm P0: RunReceipt" in duties:
    print("FAIL: bowl asf_duties still cite stale RunReceipt")
    sys.exit(1)

brief = str(b.get("brief_text") or "")
daily = Path("sina-bowl/DAILY_BOWL.md")
daily_text = daily.read_text(encoding="utf-8") if daily.is_file() else ""

if "Confirm P0: RunReceipt" in brief or "Today P zero is RunReceipt" in brief:
    print("FAIL: bowl brief_text still cites stale RunReceipt without STRATEGIC-SLICE/FREEZE")
    sys.exit(1)

if daily_text and "P0 SKU:** RunReceipt" in daily_text and "STRATEGIC-SLICE" not in daily_text:
    print("FAIL: DAILY_BOWL.md P0 SKU is RunReceipt-only — need STRATEGIC-SLICE founder line")
    sys.exit(1)

if hub_id and hub_id not in duties and hub_id not in brief and hub_id not in daily_text:
    if not any(tok in duties.upper() for tok in ("FREEZE", "STRATEGIC-SLICE")):
        print(f"FAIL: bowl duties/brief omit hub P0 id {hub_id}")
        sys.exit(1)

if not any(tok in duties.upper() for tok in ("FREEZE", "SAFETY", "RUN INBOX", "FACTORY-NOW", "FACTORY")):
    print(f"FAIL: bowl duties missing factory signal: {duties[:120]!r}")
    sys.exit(1)

print("OK: validate-bowl-hub-p0-alignment-v1")
PY
