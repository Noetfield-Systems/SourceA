#!/usr/bin/env bash
# validate-noetfield-nerve-probe-v1.sh — SourceA nerve probe law on disk
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

MIG="$ROOT/infra/supabase/portfolio-spine/migrations/013_improvement_queue_v1.sql"
SSOT="$ROOT/data/noetfield-nerve-probe-ssot-v1.json"
CRON="$ROOT/data/nerve-probe-cloud-cron-v1.json"
WORKER="$ROOT/cloud/workers/loop-specialist-tick-v1/wrangler.toml"
LOOP="$ROOT/cloud/workers/loop-specialist-tick-v1/src/index.js"
E2E="$ROOT/scripts/nf_intake_e2e_v1.py"
DEPLOY="$ROOT/scripts/deploy_nerve_probe_24_7_v1.sh"

[[ -f "$MIG" ]] || fail "missing migration $MIG"
[[ -f "$SSOT" ]] || fail "missing SSOT $SSOT"
[[ -f "$CRON" ]] || fail "missing $CRON"
[[ -f "$WORKER" ]] || fail "missing worker $WORKER"
[[ -f "$LOOP" ]] || fail "missing loop-specialist index"
[[ -f "$E2E" ]] || fail "missing $E2E"
[[ -f "$DEPLOY" ]] || fail "missing $DEPLOY"

grep -q 'improvement_queue' "$MIG" || fail "migration missing improvement_queue"
grep -q 'runNerveProbeCycle' "$LOOP" || fail "loop-specialist missing nerve piggyback"
grep -q 'piggyback_only' "$CRON" || fail "nerve-probe-cloud-cron missing piggyback law"

python3 -c "
import json
from pathlib import Path
ssot = json.loads(Path('$SSOT').read_text())
cron = json.loads(Path('$CRON').read_text())
assert ssot['owner'] == 'sourcea'
assert cron['piggyback_worker'] == 'sourcea-loop-specialist-tick-v1'
assert 'telegram_notified' in ssot['nf_intake_e2e']['pass_requires']
" || fail "SSOT check"

grep -q '*/15' "$WORKER" || fail "worker missing 15m cron"

python3 "$E2E" --dry-run --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok') and d.get('dry_run')
assert 'sourcea-loop-specialist' in d.get('worker_url','')
print('nf_intake_e2e dry-run ok')
"

grep -q 'SA-T-nerve-probe-piggyback' "$ROOT/data/trigger-registry-v1.json" || fail "trigger registry missing SA-T-nerve-probe-piggyback"

echo "OK: validate-noetfield-nerve-probe-v1"
