#!/usr/bin/env bash
# AEG demo — induce critic_boot BLOCK, capture forensic bundle, heal to PASS, attach heal receipt.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
BRIEF="${SINA}/agent-briefing/AGENT-AUTO-MONO-latest.json"
BACKUP="${SINA}/agent-briefing/.aeg-demo-backup.json"

say() { printf '%s\n' "$*"; }

if [[ ! -f "$BRIEF" ]]; then
  say "FAIL: briefing missing at $BRIEF"
  exit 1
fi

cp "$BRIEF" "$BACKUP"
say "=== AEG demo — BLOCK capture → heal → proof link ==="
say ""

say "Step 1 — induce BLOCK (context_stale=true)..."
python3 -c "
import json
from pathlib import Path
p = Path('$BRIEF')
d = json.loads(p.read_text())
d['context_stale'] = True
d['aeg_demo'] = True
p.write_text(json.dumps(d, indent=2) + '\n')
"

BLOCK_JSON="$(python3 "$ROOT/scripts/critic_boot_v1.py" --aeg --aeg-skip-ui --json || true)"
VERDICT="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('verdict',''))" "$BLOCK_JSON")"
say "critic_boot verdict: $VERDICT"
PROOF_URL="$(python3 -c "import json,sys; r=json.loads(sys.argv[1]); print((r.get('aeg') or {}).get('proof_url',''))" "$BLOCK_JSON")"
if [[ -n "$PROOF_URL" ]]; then
  say "AEG proof URL: $PROOF_URL"
else
  say "WARN: AEG bundle not attached — running standalone capture..."
  python3 "$ROOT/scripts/aeg_capture_v1.py" --skip-ui --json
fi
say ""

say "Step 2 — heal briefing..."
cp "$BACKUP" "$BRIEF"
python3 -c "
import json
from pathlib import Path
p = Path('$BRIEF')
d = json.loads(p.read_text())
d['context_stale'] = False
d.pop('aeg_demo', None)
p.write_text(json.dumps(d, indent=2) + '\n')
"

PASS_JSON="$(python3 "$ROOT/scripts/critic_boot_v1.py" --json || true)"
say "critic_boot heal verdict: $(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('verdict'))" "$PASS_JSON")"
say ""

say "Step 3 — attach heal receipt to latest AEG bundle (if BLOCK bundle exists)..."
LATEST="${SINA}/aeg-latest-receipt-v1.json"
if [[ -f "$LATEST" ]]; then
  BUNDLE="$(python3 -c "import json; print(json.load(open('$LATEST'))['bundle_dir'])")"
  echo "$PASS_JSON" >"${BUNDLE}/heal_boot_receipt.json"
  python3 "$ROOT/scripts/aeg_capture_v1.py" --from-boot-receipt "${BUNDLE}/critic_boot_receipt.json" --heal-receipt "${BUNDLE}/heal_boot_receipt.json" --skip-ui --json
fi

say ""
say "PASS: AEG demo complete"
say "  Latest receipt: ${SINA}/aeg-latest-receipt-v1.json"
say "  Index: ${SINA}/aeg-index-v1.jsonl"
say "  Open proof: open \"\$(python3 -c \"import json; print(json.load(open('${SINA}/aeg-latest-receipt-v1.json'))['proof_url'])\")\""
