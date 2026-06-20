#!/usr/bin/env bash
# validate-no-fake-progress-form-v1.sh — form 0 open must not hide unshipped picks (NO_FAKE_PROGRESS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SCRIPTS="$ROOT/scripts"

fail() { echo "FAIL: validate-no-fake-progress-form-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "fake-green form probe"
import json
import re
import sys
from pathlib import Path

ROOT = Path("/Users/sinakazemnezhad/Desktop/SourceA")
FORM = ROOT / "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md"
APPLIED = Path.home() / ".sina/canvas-form-picks-applied-v1.json"
SHIP_RECEIPT = Path.home() / ".sina/form-ship-receipt-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from live_founder_decision_form_v1 import all_open_questions  # noqa: E402

if not FORM.is_file():
    print("SKIP: form missing")
    sys.exit(0)

if not APPLIED.is_file():
    print("OK: no applied picks file — nothing to fake-green")
    sys.exit(0)

applied_data = json.loads(APPLIED.read_text(encoding="utf-8"))
applied_ids = set((applied_data.get("picks") or {}).keys())
open_rows = all_open_questions()
open_count = len(open_rows)

text = FORM.read_text(encoding="utf-8")
answered_block = ""
if "## 2. §ANSWERED" in text:
    tail = text.split("## 2. §ANSWERED", 1)[1]
    for marker in ("## 3.", "## 4.", "## 5."):
        if marker in tail:
            tail = tail.split(marker, 1)[0]
            break
    answered_block = tail

answered_ids = set(re.findall(r"\| \*\*([^|*]+)\*\* \|", answered_block))
unshipped = sorted(applied_ids - answered_ids)

# Explicit batch SHIP receipt may cover defer/reconcile rows still in applied json
if SHIP_RECEIPT.is_file():
    try:
        rec = json.loads(SHIP_RECEIPT.read_text(encoding="utf-8"))
        covered = set(rec.get("shipped_ids") or rec.get("ids") or [])
        if rec.get("ok") and covered >= applied_ids:
            print(f"OK: form-ship-receipt covers all {len(applied_ids)} applied picks")
            sys.exit(0)
        unshipped = sorted(set(unshipped) - covered)
    except (OSError, json.JSONDecodeError):
        pass

if open_count == 0 and unshipped:
    print(
        f"FAKE_GREEN: form open=0 but {len(unshipped)} applied pick(s) not in §ANSWERED "
        f"and no form-ship-receipt: {unshipped[:8]}{'…' if len(unshipped) > 8 else ''}",
        file=sys.stderr,
    )
    sys.exit(1)

if unshipped and open_count > 0:
    # picks recorded but rows still open — warn only if some applied hide others
    hidden = applied_ids & {q["id"] for q in open_rows}
    if hidden:
        print(f"WARN: {len(hidden)} applied ids still listed open — sync drift", file=sys.stderr)

print(
    f"OK: validate-no-fake-progress-form-v1 · open={open_count} · "
    f"applied={len(applied_ids)} · unshipped={len(unshipped)}"
)
PY
