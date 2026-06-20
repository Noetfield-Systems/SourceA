#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-live-founder-decision-form-v1 — $*" >&2; exit 1; }

DOC="$ROOT/SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md"
NORM="$ROOT/SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md"
[[ -f "$DOC" ]] || fail "missing live form"
[[ -f "$NORM" ]] || fail "missing normalization law"
grep -q "LIVE_DECISION_FORM" "$ROOT/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md" || fail "authority row"
grep -q "0m" "$ROOT/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md" || fail "governance §0m"
grep -q "LIVE_FOUNDER_DECISION_FORM" "$ROOT/brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md" || fail "MANDATORY_READ"
grep -q "live_founder_decision_form" "$ROOT/prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md" || fail "FIVE_STEP SCAN hook"
FIRST="$ROOT/archive/attachments/2026-06-11/SOURCEA_LIVE_FOUNDER_DECISION_FORM_FIRST_FORM_LOCKED_v1.md"
[[ -f "$FIRST" ]] || fail "missing FIRST FORM archive"
grep -q "NORM-CAPS" "$DOC" || fail "NORM-CAPS in form"
ANSWERS="$ROOT/archive/attachments/2026-06-11/SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md"
[[ -f "$ANSWERS" ]] || fail "missing v2 answers receipt"
grep -q "v2 FILLED" "$DOC" || fail "v2 FILLED marker in form law"
grep -q "FIRST FORM" "$DOC" || fail "FIRST FORM pointer in live form"
grep -q "100% equivalent" "$NORM" || fail "CAPS rule in norm doc"
grep -q '"/api/live-founder-decision-form-v1"' "$ROOT/scripts/sina-command-server.py" || fail "API route missing"
grep -q 'action == "submit"' "$ROOT/scripts/sina-command-server.py" || fail "form submit POST missing"
[[ -f "$ROOT/scripts/canvas_form_submit_v1.py" ]] || fail "canvas_form_submit_v1.py missing"
python3 "$ROOT/scripts/live_founder_decision_form_v1.py" --write-receipt >/dev/null || fail "form script"
[[ -f "$HOME/.sina/live-founder-decision-form-v1.json" ]] || fail "receipt json"
bash "$ROOT/scripts/validate-form-founder-supremacy-v1.sh"
python3 - <<'PY'
import json
import sys
import urllib.request

with urllib.request.urlopen("http://127.0.0.1:13020/api/live-founder-decision-form-v1", timeout=8) as r:
    d = json.loads(r.read().decode("utf-8"))
if not d.get("ok"):
    print("FAIL: form API ok=false", file=sys.stderr)
    sys.exit(1)
if d.get("form_edition") != "v2":
    print("FAIL: form_edition must be v2", file=sys.stderr)
    sys.exit(1)
if not (d.get("first_form") or {}).get("saved"):
    print("FAIL: first_form archive not saved", file=sys.stderr)
    sys.exit(1)
oq = int(d.get("open_questions_count") or 0)
awaiting = bool(d.get("awaiting_founder_picks"))
if d.get("needs_asf_fill"):
    print("FAIL: v2 filled but needs_asf_fill still true", file=sys.stderr)
    sys.exit(1)
if awaiting != (oq > 0):
    print("FAIL: awaiting_founder_picks must match open_questions_count", file=sys.stderr)
    sys.exit(1)
v2 = d.get("v2_answers") or {}
if not v2.get("filled") or int(v2.get("count") or 0) != 6:
    print("FAIL: v2_answers must report 6 filled rows", file=sys.stderr)
    sys.exit(1)
print(f"OK: live form API · v2 filled · open_questions={oq} · drift_floor={d.get('drift_floor')}")
PY

echo "OK: validate-live-founder-decision-form-v1"
