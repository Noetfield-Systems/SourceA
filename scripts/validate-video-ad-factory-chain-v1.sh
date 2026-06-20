#!/usr/bin/env bash
# validate-video-ad-factory-chain-v1.sh — orchestration · bridge · billing stub chain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f data/multi-factory-enterprise-tree-advisory-v1.json ]] || fail "missing advisory SSOT"
[[ -f data/architecture-ledger-v1.json ]] || fail "missing architecture ledger"
[[ -f data/supabase-migration-001-campaign-automations-v1.sql ]] || fail "missing supabase migration SSOT"
[[ -f scripts/video_ad_factory_orchestrate_v1.py ]] || fail "missing orchestration"
[[ -f scripts/video_ad_rendering_bridge_v1.py ]] || fail "missing rendering bridge"
[[ -f scripts/fbe_billing_webhook_stub_v1.py ]] || fail "missing billing webhook stub"

python3 scripts/fbe_billing_webhook_stub_v1.py --demo --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok'), d"
python3 scripts/video_ad_factory_orchestrate_v1.py --seed-demo --json >/dev/null
python3 scripts/video_ad_factory_orchestrate_v1.py --campaign-id demo-campaign-v1 --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok'), d"
python3 scripts/video_ad_rendering_bridge_v1.py --campaign-id demo-campaign-v1 --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok'), d"

echo "OK: validate-video-ad-factory-chain-v1 · advisory · ledger · orchestration · bridge · billing"
