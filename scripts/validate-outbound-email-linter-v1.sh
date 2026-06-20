#!/usr/bin/env bash
# validate-outbound-email-linter-v1.sh — OEGCC step 1 checker smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FIX="$ROOT/scripts/fixtures/outbound-email-linter"
fail=0

[[ -f scripts/outbound_email_linter_v1.py ]] || { echo "FAIL: missing linter script"; exit 1; }

python3 - <<'PY' || fail=1
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(".")
PY = sys.executable
FIX = ROOT / "scripts/fixtures/outbound-email-linter"


def run(body_file: Path) -> dict:
    proc = subprocess.run(
        [PY, str(ROOT / "scripts/outbound_email_linter_v1.py"), "--body-file", str(body_file), "--json"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = proc.stdout[proc.stdout.find("{") :]
    row = json.loads(out)
    row["_exit"] = proc.returncode
    return row


pass_row = run(FIX / "pass.txt")
if not pass_row.get("ok"):
    raise SystemExit(f"FAIL pass fixture: {pass_row}")
if pass_row.get("warnings"):
    raise SystemExit(f"FAIL pass fixture has warnings: {pass_row.get('warnings')}")

warn_row = run(FIX / "warn_101words.txt")
if not warn_row.get("ok"):
    raise SystemExit(f"FAIL warn fixture should pass hard gate: {warn_row}")
if not any(w.get("id") == "word_count_soft" for w in warn_row.get("warnings") or []):
    raise SystemExit(f"FAIL warn fixture missing word_count_soft: {warn_row}")

opener_row = run(FIX / "fail_opener.txt")
if opener_row.get("ok"):
    raise SystemExit(f"FAIL opener fixture should block: {opener_row}")
if not any(f.get("id") == "banned_opener" for f in opener_row.get("failures") or []):
    raise SystemExit(f"FAIL opener fixture missing banned_opener: {opener_row}")

long_row = run(FIX / "fail_141words.txt")
if long_row.get("ok"):
    raise SystemExit(f"FAIL 141w fixture should block: {long_row}")
if not any(f.get("id") == "word_count" for f in long_row.get("failures") or []):
    raise SystemExit(f"FAIL 141w fixture missing word_count: {long_row}")

if not pass_row.get("repair_lines") == []:
    raise SystemExit("FAIL pass should have empty repair_lines")

print("OK: outbound-email-linter · pass · warn@101 · opener fail · 141w fail")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-outbound-email-linter-v1"
  exit 0
fi
echo "FAIL: validate-outbound-email-linter-v1"
exit 1
