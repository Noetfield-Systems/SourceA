#!/usr/bin/env bash
# validate-commercial-outbound-e2e-v1.sh — full commercial outbound e2e (no new app)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

fail() { echo "FAIL: validate-commercial-outbound-e2e-v1 — $*" >&2; exit 1; }

echo "=== commercial outbound e2e ==="

bash scripts/validate-commercial-pipeline-v1.sh
bash scripts/validate-commercial-eval-booking-v1.sh
bash scripts/validate-commercial-reply-agent-v1.sh
bash scripts/validate-commercial-recipient-guard-v1.sh
bash scripts/validate-commercial-sender-guard-v1.sh

# Regenerate packs with public W1 URL (no --open-mail)
python3 scripts/commercial_pipeline_repair_v1.py --json >/dev/null || fail "pipeline repair"

python3 scripts/commercial_recipient_guard_v1.py --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
bad=[i for i in d.get('issues',[]) if i.get('issue')!='placeholder']
if bad:
    for i in bad: print('E2E BLOCK:', i)
    raise SystemExit(1)
print('OK: e2e outbound scan ·', d.get('placeholders',0), 'draft placeholders')
"

python3 scripts/commercial_mail_draft_v1.py --lane AB1 --check-mail --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
if d.get('ok'):
    print('OK: hello@sourcea.app in Mail.app — open-mail allowed')
else:
    print('WARN: hello@sourcea.app not in Mail.app — packs OK but open-mail blocked')
    print('  accounts:', d.get('mail_accounts'))
" || true

echo "PASS: validate-commercial-outbound-e2e-v1"
