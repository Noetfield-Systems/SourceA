#!/usr/bin/env bash
# Light Brain refresh — rules + positioning SSOT + live sources + bundle sync (no www crawl).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Brain light refresh (no www crawl) ==="
python3 scripts/distill_positioning_public_v1.py
python3 scripts/distill_brain_public_rules_v1.py
python3 scripts/distill_brain_live_sources_v1.py
python3 scripts/sync_brain_chat_knowledge_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
print(f\"light OK: {r.get('chunk_count')} chunks · live {r.get('live_source_files')}\")
"
python3 scripts/brain_refresh_gate_v1.py --save --json >/dev/null
echo "DONE light — deploy: bash scripts/brain_cli_v1.sh deploy-no-refresh"
