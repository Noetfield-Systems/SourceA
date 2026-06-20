#!/usr/bin/env bash
# Automated BLOCK → PASS wow moment for Mac Guard agency demo.
# Law: MAC_GUARD_AGENCY_DEMO_SCRIPT_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
BRIEF="${SINA}/agent-briefing/AGENT-AUTO-MONO-latest.json"
BACKUP="${SINA}/agent-briefing/.demo-block-pass-backup.json"
RECEIPT="${SINA}/critic-boot-v1.json"

say() { printf '%s\n' "$*"; }

run_boot() {
  python3 "$ROOT/scripts/critic_boot_v1.py" --json || true
}

show_verdict() {
  local label="$1"
  local json="$2"
  python3 -c "
import json, sys
r = json.loads(sys.argv[1])
print(f'=== {sys.argv[2]} ===')
print(f\"verdict: {r.get('verdict')}\")
print(f\"line:    {r.get('founder_line')}\")
for c in r.get('checks') or []:
    mark = 'OK' if c.get('ok') else 'FAIL'
    print(f\"  [{mark}] {c.get('name')}: {c.get('reason')}\")
" "$json" "$label"
}

say "=== Mac Guard demo — BLOCK → PASS ==="
say ""

if [[ ! -f "$BRIEF" ]]; then
  say "FAIL: briefing missing at $BRIEF"
  say "Run session gate / briefing first."
  exit 1
fi

cp "$BRIEF" "$BACKUP"
say "Backed up briefing → $BACKUP"
say ""

say "Step 1 — induce stale SSOT (context_stale=true)..."
python3 -c "
import json
from pathlib import Path
p = Path('$BRIEF')
d = json.loads(p.read_text())
d['context_stale'] = True
d['demo_induced_block'] = True
p.write_text(json.dumps(d, indent=2) + '\n')
"

BLOCK_JSON="$(run_boot)"
show_verdict "BLOCK (expected)" "$BLOCK_JSON"
VERDICT="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('verdict',''))" "$BLOCK_JSON")"
if [[ "$VERDICT" != "BLOCK" ]]; then
  say "WARN: expected BLOCK — showing current state anyway"
fi
say ""

say "Step 2 — restore briefing + clear stale flag..."
cp "$BACKUP" "$BRIEF"
python3 -c "
import json
from pathlib import Path
p = Path('$BRIEF')
d = json.loads(p.read_text())
d['context_stale'] = False
d.pop('demo_induced_block', None)
p.write_text(json.dumps(d, indent=2) + '\n')
"

say "Step 3 — re-sync SSOT fingerprint if needed..."
python3 "$ROOT/scripts/critic_boot_v1.py" --json >/dev/null || true

PASS_JSON="$(run_boot)"
show_verdict "PASS (recovered)" "$PASS_JSON"
VERDICT="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('verdict',''))" "$PASS_JSON")"
say ""
if [[ "$VERDICT" == "PASS" ]]; then
  say "Demo arc complete: BLOCK → PASS"
  say "Receipt: $RECEIPT"
  exit 0
fi
say "FAIL: recovery did not reach PASS — inspect blockers above"
exit 1
