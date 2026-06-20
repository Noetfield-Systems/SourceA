#!/usr/bin/env bash
# validate-integrity-form-canvas-ssot-v1.sh — INCIDENT-029: M1 Canvas slot D only · 43-row sync
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-integrity-form-canvas-ssot-v1 — $*" >&2; exit 1; }

M1_CANVAS="$HOME/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
SCRATCH_SOURCEA="$HOME/.cursor/projects/Users-sinakazemnezhad-Desktop-SourceA/canvases/live-founder-decision-form.canvas.tsx"
SYNTHESIS="$ROOT/archive/attachments/2026-06-12/MAINTAINER_2_CROSS_CHAT_GOV_COMMERCIAL_INCIDENT_SYNTHESIS_LOCKED_v1.md"

[[ -f "$M1_CANVAS" ]] || fail "missing M1 integrity Canvas (slot D)"
[[ ! -f "$SCRATCH_SOURCEA" ]] || fail "scratch live-founder-decision-form.canvas.tsx must stay deleted"

grep -q "pending-confirmations" "$M1_CANVAS" || fail "M1 Canvas missing pending-confirmations view"
grep -q "CROSS_CHAT_SYNTHESIS" "$M1_CANVAS" || fail "M1 Canvas missing cross-chat synthesis link"
grep -q "OPEN_FORM_QUESTIONS" "$M1_CANVAS" || fail "M1 Canvas must import OPEN_FORM_QUESTIONS"
grep -q "@generated-integrity-form-data-begin" "$M1_CANVAS" || fail "M1 Canvas missing inlined generated 100 agent POV data"
grep -q "from \"./integrity-form-data.generated\"" "$M1_CANVAS" && fail "M1 Canvas must not use relative imports (Canvas SDK)"
V2_SCRATCH="$HOME/.cursor/projects/Users-sinakazemnezhad-Desktop-SourceA/canvases/sourcea-100-agent-pov-form-v2.canvas.tsx"
[[ ! -f "$V2_SCRATCH" ]] || fail "scratch agent-pov v2 canvas must be archived/deleted (INCIDENT-029)"
[[ -f "$SYNTHESIS" ]] || fail "missing cross-chat synthesis LOCKED doc"

grep -q "INCIDENT-029" "$ROOT/brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md" || fail "INCIDENT-029 not in MANDATORY_READ Maintainer"

grep -q "@generated-integrity-open-row-spec-begin" "$M1_CANVAS" || fail "M1 Canvas missing inlined open-row spec (no relative imports)"
grep -q "from \"./integrity-open-row-spec\"" "$M1_CANVAS" && fail "M1 Canvas must not import integrity-open-row-spec (Canvas SDK)"

# SSOT check only — disk submit is founder Submit on M1 Canvas (canvas_form_submit_v1.py)

while IFS= read -r bad; do
  [[ -z "$bad" ]] && continue
  fail "forbidden scratch founder form canvas: $bad"
done < <(find "$HOME/.cursor/projects" -maxdepth 4 -type f -name '*founder*form*.canvas.tsx' 2>/dev/null || true)

python3 - <<PY || fail "canvas row sync vs form JSON"
import json
import re
import subprocess
from pathlib import Path

root = Path("$ROOT")
canvas = Path.home() / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
text = canvas.read_text(encoding="utf-8")

raw = subprocess.check_output(
    ["python3", str(root / "scripts/live_founder_decision_form_v1.py"), "--json"],
    text=True,
)
form = json.loads(raw)
open_ids = [q["id"] for q in form.get("open_questions") or []]
open_count = int(form.get("open_questions_count") or 0)

gen_path = Path.home() / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/integrity-form-data.generated.ts"
if not gen_path.is_file():
    raise SystemExit("missing integrity-form-data.generated.ts — run generate_integrity_canvas_form_data_v1.py")
gen_text = gen_path.read_text(encoding="utf-8")
m_open = re.search(r"export const OPEN_FORM_QUESTIONS = \[(.*?)\];", gen_text, re.DOTALL)
if not m_open:
    raise SystemExit("OPEN_FORM_QUESTIONS missing in generated data")
sync_ids = set(re.findall(r'id:\\s*"([^"]+)"', m_open.group(1)))
m100 = re.search(r"export const AGENT_POV_FORM_QUESTIONS = \[(.*?)\];", gen_text, re.DOTALL)
if not m100:
    raise SystemExit("AGENT_POV_FORM_QUESTIONS missing in generated data")
if len(re.findall(r'id:\\s*"([^"]+)"', m100.group(1))) != 100:
    raise SystemExit("AGENT_POV_FORM_QUESTIONS must have 100 rows")
missing = [i for i in open_ids if i not in sync_ids]
if missing:
    raise SystemExit(f"form open ids missing from canvas sync arrays: {missing}")
extra = sorted(sync_ids - set(open_ids))
if extra:
    raise SystemExit(f"canvas sync ids not open on form: {extra}")
if len(sync_ids) != open_count:
    raise SystemExit(f"canvas sync count {len(sync_ids)} != form {open_count}")

print(f"OK: canvas sync · {open_count} rows · ids match form JSON")
PY

echo "OK: validate-integrity-form-canvas-ssot-v1 · M1 slot D · no scratch form · form sync"
