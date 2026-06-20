#!/usr/bin/env bash
# validate-next-phase-founder-open-v1.sh — sa-0807 H2 next_phase vs PROGRAM_PROGRESS founder_open
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-next-phase-founder-open-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "next_phase vs founder_open"
import json
import sys
from pathlib import Path

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "scripts"))

reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
pp_path = ROOT / "PROGRAM_PROGRESS.json"
if not reg_path.is_file():
    raise SystemExit("missing h2-pending-registry-v1.json")
if not pp_path.is_file():
    raise SystemExit("missing PROGRAM_PROGRESS.json")

reg = json.loads(reg_path.read_text(encoding="utf-8"))
pp = json.loads(pp_path.read_text(encoding="utf-8"))

next_phase = list(reg.get("next_phase") or [])
if not next_phase:
    raise SystemExit("next_phase bucket empty")

founder_open = ""
for row in pp.get("todos") or pp.get("todo") or []:
    if isinstance(row, dict) and row.get("founder_open"):
        founder_open = str(row["founder_open"])
        break
if not founder_open:
    raise SystemExit("PROGRAM_PROGRESS todo.founder_open missing")

form_open = int((reg.get("form_open") or {}).get("count") or 0)
if form_open != 0 and "0 open PICK" not in founder_open:
    raise SystemExit(f"form_open={form_open} but founder_open lacks 0 open PICKs")

# next_phase row ids must appear in registry or align with founder_open themes
themes = ("W1", "W3", "Phase 3", "OpenRouter")
for theme in themes:
    in_np = any(theme.lower() in str(r.get("title") or r.get("id") or "").lower() for r in next_phase)
    in_fo = theme.lower() in founder_open.lower()
    if not (in_np or in_fo):
        raise SystemExit(f"theme {theme!r} missing from next_phase and founder_open")

from h2_pending_count_lib_v1 import count_h2_pending  # noqa: WPS433

counts = count_h2_pending(reg)
if counts["pending_total"] > 15:
    raise SystemExit(f"pending_total inflated: {counts['pending_total']}")

print(
    f"OK: validate-next-phase-founder-open-v1 · next_phase={len(next_phase)} "
    f"pending={counts['pending_total']} · founder_open aligned"
)
PY

bash "$ROOT/scripts/validate-h2-pending-honest-count-v1.sh" >/dev/null || fail "h2 honest count"

echo "OK: validate-next-phase-founder-open-v1 · sa-0807"
