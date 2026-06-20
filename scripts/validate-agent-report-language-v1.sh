#!/usr/bin/env bash
# validate-agent-report-language-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/agent-report-language-standard-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/agent_report_language_gate_v1.py || { echo "FAIL missing gate"; exit 1; }
test -f .cursor/rules/027-agent-report-plan-story-v1.mdc || { echo "FAIL missing rule 027"; exit 1; }

GOOD='You asked why email is still deferred. WitnessBC prod still serves the old journalism page, so sites stay RED even though TrustField and Noetfield return 200.'
python3 scripts/agent_report_language_gate_v1.py --scan-text "$GOOD" --json >/dev/null

BAD='Language standard wired. Gate PASS. SSOT updated.'
if python3 scripts/agent_report_language_gate_v1.py --scan-text "$BAD" --json >/dev/null 2>&1; then
  echo "FAIL parrot claim should not PASS"
  exit 1
fi

grep -q 'agent_report_language' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct gate not wired"; exit 1; }

echo "PASS: validate-agent-report-language-v1"
