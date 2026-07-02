#!/usr/bin/env bash
# validate-cursor-bootstrap-v1.sh — enterprise Cursor bootstrap pack gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
fail() { echo "FAIL: cursor-bootstrap — $*" >&2; FAIL=1; }

# --- machine SSOT ---
for f in \
  data/cursor-bootstrap-ledger-v1.json \
  data/architecture-ledger-v1.json \
  data/cursor-corporate-bootstrap-master-v1.json \
  data/multi-factory-enterprise-tree-advisory-v1.json \
  docs/architecture_ledger.json
do
  [[ -f "$f" ]] || fail "missing $f"
done

python3 - <<'PY' || fail "ledger schema"
import json
from pathlib import Path
for p in [
    Path("data/cursor-bootstrap-ledger-v1.json"),
    Path("data/architecture-ledger-v1.json"),
    Path("docs/architecture_ledger.json"),
]:
    d = json.loads(p.read_text())
    assert d.get("schema") or d.get("ssot_path"), p
    if p.name == "cursor-bootstrap-ledger-v1.json":
        assert d.get("core_contracts"), p
    else:
        assert d.get("core_contracts") or d.get("microservices_routing") or d.get("immutable_contracts"), p
boot = json.loads(Path("data/cursor-bootstrap-ledger-v1.json").read_text())
arch = json.loads(Path("data/architecture-ledger-v1.json").read_text())
assert boot.get("architecture_ledger_ssot") == "data/architecture-ledger-v1.json"
assert arch.get("ssot_aliases", {}).get("cursor_bootstrap") == "data/cursor-bootstrap-ledger-v1.json"
print("OK: ledger JSON schema + cross-alias")
PY

# --- docs ---
for f in \
  docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md \
  docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md \
  docs/SCALE_EVOLUTION_LOCKED_v1.md \
  docs/COMPLETE_CONTEXT.md
do
  [[ -f "$f" ]] || fail "missing $f"
done

bash scripts/validate-doc-datetime-header-v1.sh docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md || fail "datetime header bootstrap pack"
bash scripts/validate-doc-datetime-header-v1.sh docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md || fail "datetime header context index"
bash scripts/validate-doc-datetime-header-v1.sh docs/SCALE_EVOLUTION_LOCKED_v1.md || fail "datetime header scale evolution"

# --- cursor wiring ---
[[ -f .cursorrules ]] || fail "missing root .cursorrules"
[[ -f .cursor/rules/024-cursor-enterprise-bootstrap.mdc ]] || fail "missing 024 rule"
[[ -f .env.example ]] || fail "missing .env.example"

# --- shared layer ---
for f in shared/types/index.ts shared/types/receipts-v1.ts shared/types/campaign-v1.ts shared/utils/clients.ts; do
  [[ -f "$f" ]] || fail "missing $f"
done

# --- apps factories ---
for d in video-ad-factory apple-store-api analytics-intelligence; do
  [[ -f "apps/$d/README.md" ]] || fail "missing apps/$d/README.md"
done
[[ -f apps/video-ad-factory/.cursor/rules/011-video-ad-factory.mdc ]] || fail "missing video-ad factory rules"

# --- PHASE_1 machines ---
[[ -f data/supabase-migration-001-campaign-automations-v1.sql ]] || fail "missing supabase migration SSOT"
[[ -f scripts/video_ad_factory_orchestrate_v1.py ]] || fail "missing video_ad_factory_orchestrate"
[[ -f scripts/video_ad_rendering_bridge_v1.py ]] || fail "missing video_ad_rendering_bridge"
if python3 scripts/founder_session_gate_v1.py validate-video-ad-factory-chain-v1.sh --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('ok') else 1)"; then
  bash scripts/validate-video-ad-factory-chain-v1.sh >/dev/null || fail "video-ad-factory chain"
else
  echo "NOTE: skipped video-ad-factory chain — founder session heavy gate"
fi

# --- chained E2E (fast) ---
if curl -sf --max-time 3 http://127.0.0.1:13020/health >/dev/null 2>&1; then
  bash scripts/validate-super-fast-hub-v1.sh >/dev/null || fail "super-fast hub"
  echo "OK: hub E2E chained"
else
  echo "INFO: hub down — skip hub chain"
fi

python3 - <<'PY' || fail "mcp-campus bootstrap wire"
import json
from pathlib import Path
reg = json.loads(Path("data/mcp-chain-campus-registries-v1.json").read_text())
cb = reg.get("cursor_bootstrap") or {}
assert cb.get("ledger") == "data/cursor-bootstrap-ledger-v1.json"
assert (reg.get("campuses") or {}).get("sourcea", {}).get("cursor_bootstrap_ledger")
print("OK: mcp-campus-registries cursor_bootstrap wired")
PY

if [[ "$FAIL" -ne 0 ]]; then exit 1; fi
echo "OK: validate-cursor-bootstrap-v1 · enterprise pack wired"
