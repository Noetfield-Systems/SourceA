#!/usr/bin/env bash
# AEG full stack — deps → BLOCK demo → validate → host proof link.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
export AEG_ON_BLOCK=1

say() { printf '%s\n' "$*"; }

say "=== AEG full stack $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
say ""

say "Step 1 — capture deps..."
bash "$ROOT/scripts/setup_aeg_deps_v1.sh"
say ""

say "Step 2 — BLOCK → heal demo bundle..."
bash "$ROOT/scripts/run_aeg_critic_boot_demo_v1.sh"
say ""

say "Step 3 — validate structure..."
bash "$ROOT/scripts/validate-aeg-capture-v1.sh"
say ""

say "Step 4 — host proof page (tunnel fallback)..."
HOST_JSON="$(python3 "$ROOT/scripts/host_aeg_bundle_v1.py" --backend auto --json 2>/dev/null || echo '{"ok":false}')"
PROOF_URL="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('proof_url',''))" "$HOST_JSON" 2>/dev/null || true)"
if [[ -n "$PROOF_URL" ]]; then
  say "Hosted proof URL: $PROOF_URL"
else
  LOCAL="$(python3 -c "import json; print(json.load(open('${SINA}/aeg-latest-receipt-v1.json')).get('proof_url',''))" 2>/dev/null || true)"
  say "Local proof (open in browser): $LOCAL"
fi
say ""

say "Step 5 — outbound pack (draft)..."
if [[ -f "${SINA}/aeg-latest-receipt-v1.json" ]]; then
  python3 "$ROOT/scripts/send_aeg_proof_outbound_v1.py" --to "agency@example.com" 2>/dev/null || say "SKIP: Mail draft (configure recipient when ready)"
else
  say "SKIP: no AEG receipt"
fi
say ""

say "PASS: AEG full stack complete"
say "  Latest: ${SINA}/aeg-latest-receipt-v1.json"
say "  Index:  ${SINA}/aeg-index-v1.jsonl"
say "  Next:   Mail → send_aeg_proof_outbound_v1.py --to agency@example.com"
