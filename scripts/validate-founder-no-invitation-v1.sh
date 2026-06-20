#!/usr/bin/env bash
# Founder NO INVITATION — stable system · guards only (machine)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-founder-no-invitation-v1 — $*" >&2; exit 1; }

[[ -f "$HOME/.sina/founder-no-agent-invitation-v1.flag" ]] \
  || fail "missing founder-no-agent-invitation-v1.flag"

python3 - <<'PY' || fail "behavior SSOT"
import json
from pathlib import Path
ssot = json.loads((Path("data/agent-behavior-settings-v1.json")).read_text())
block = ssot.get("founder_no_invitation") or {}
assert block.get("active") is True, block
print("OK: founder_no_invitation active")
PY

grep -q 'no invitation' data/agent-behavior-settings-v1.json || fail "behavior missing no invitation"
grep -q 'no invitation' .cursor/rules/agent-founder-intent-first.mdc || fail "rule missing no invitation"

python3 - <<'PY' || fail "close-line blocks invitation"
import json, subprocess, sys
proc = subprocess.run(
    [sys.executable, "scripts/founder_close_line_gate_v1.py", "--text", "Problem fixed. One next tap: open form.", "--json"],
    capture_output=True, text=True,
)
d = json.loads(proc.stdout)
assert not d.get("ok"), d
assert any(h.get("id") == "F24" for h in d.get("hits") or []), d
print("OK: close-line blocks one next tap")
PY

python3 - <<'PY' || fail "conduct blocks invitation"
import json, subprocess, sys
proc = subprocess.run(
    [sys.executable, "scripts/agentic_conduct_gate_v1.py", "--role", "worker", "--task-text", "Done. Hard refresh the form page now.", "--json"],
    capture_output=True, text=True,
)
d = json.loads(proc.stdout)
v = [x for x in (d.get("violations") or []) if "founder_invitation" in x]
assert v, d
print("OK: conduct blocks invitation language")
PY

python3 - <<'PY' || fail "guard-only text allowed"
import json, subprocess, sys
proc = subprocess.run(
    [sys.executable, "scripts/agentic_conduct_gate_v1.py", "--role", "worker", "--task-text", "Guard ON · FORM_AGENT_SUBMIT_FORBIDDEN · validate PASS", "--json"],
    capture_output=True, text=True,
)
d = json.loads(proc.stdout)
v = [x for x in (d.get("violations") or []) if "founder_invitation" in x]
assert not v, d
print("OK: guard-only text allowed")
PY

echo "PASS: validate-founder-no-invitation-v1"
