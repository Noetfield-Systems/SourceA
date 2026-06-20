#!/usr/bin/env bash
# validate-maintainer-scan-p0-v1.sh — INCIDENT-027: form filled → hub P0 must not headline drain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-maintainer-scan-p0-v1 — $*" >&2; exit 1; }

python3 <<'PY'
import json
import re
import sys

sys.path.insert(0, "scripts")
from founder_p0_next_action_v1 import (
    build_founder_p0_next_action,
    rt_live_gate_active,
    validate_next_action,
)
from live_founder_decision_form_v1 import payload as live_form_payload

form = live_form_payload()
oq = int(form.get("open_questions_count") or 0)
if oq > 0:
    built = build_founder_p0_next_action()
    ok, msg = validate_next_action(built)
    if not ok:
        print(f"FAIL: open-questions builder — {msg}")
        raise SystemExit(1)
    if re.search(r"sa-\d{4}", built, re.I):
        print(f"FAIL: open-questions builder still contains sa-id: {built!r}")
        raise SystemExit(1)
    try:
        import pathlib

        data = json.loads(pathlib.Path("agent-control-panel/command-data.json").read_text(encoding="utf-8"))
        p0 = ((data.get("command_center") or {}).get("founder") or {}).get("p0") or {}
        na = str(p0.get("next_action") or "") if isinstance(p0, dict) else ""
        if na and re.search(r"sa-\d{4}", na, re.I):
            print(f"FAIL: command-data.json leaks sa-id during open questions: {na!r}")
            raise SystemExit(1)
    except FileNotFoundError:
        pass
    print("OK: validate-maintainer-scan-p0-v1 · open questions · no drain headline")
    raise SystemExit(0)

if not rt_live_gate_active():
    print("SKIP: validate-maintainer-scan-p0 — RT LIVE gate not active")
    raise SystemExit(0)

built = build_founder_p0_next_action()
ok, msg = validate_next_action(built)
if not ok:
    print(f"FAIL: builder — {msg}")
    raise SystemExit(1)

if re.search(r"sa-\d{4}", built, re.I):
    print(f"FAIL: builder still contains sa-id: {built!r}")
    raise SystemExit(1)

cmd_path = "agent-control-panel/command-data.json"
try:
    import pathlib

    data = json.loads(pathlib.Path(cmd_path).read_text(encoding="utf-8"))
    p0 = (data.get("command_center") or {}).get("founder") or {}
    p0 = p0.get("p0") or p0
    na = str(p0.get("next_action") or "")
    if na:
        ok2, msg2 = validate_next_action(na)
        if not ok2:
            print(f"FAIL: command-data.json — {msg2}")
            raise SystemExit(1)
except FileNotFoundError:
    pass

print("OK: validate-maintainer-scan-p0-v1 · RT LIVE gate · no drain headline")
PY
