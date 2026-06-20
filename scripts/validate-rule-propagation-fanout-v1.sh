#!/usr/bin/env bash
# Validate rule propagation fanout — era · queue head · surfaces line
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
FAIL=0

era_ok=0
if [[ -f "${ROOT}/data/factory-era-v1.json" ]]; then
  era_ok=1
fi
if [[ -f "${SINA}/factory-era-v1.json" ]]; then
  era_ok=1
fi
if [[ "${era_ok}" -ne 1 ]]; then
  echo "FAIL: factory-era-v1.json missing"
  FAIL=1
fi

FN_LINE=""
if [[ -f "${SINA}/factory-now-v1.json" ]]; then
  MODE="$(python3 -c "import json; print(json.load(open('${SINA}/factory-now-v1.json')).get('mode',''))")"
  QSA="$(python3 -c "import json; print(json.load(open('${SINA}/factory-now-v1.json')).get('queue_sa',''))")"
  if [[ "${MODE}" != "FORGE_FACTORY" ]]; then
    echo "FAIL: factory-now mode=${MODE} expected FORGE_FACTORY"
    FAIL=1
  fi
  if [[ -z "${QSA}" ]]; then
    echo "FAIL: factory-now queue_sa empty"
    FAIL=1
  fi
fi

if [[ -f "${SINA}/agent-live-surfaces-v1.json" ]]; then
  FN_LINE="$(python3 -c "import json; print(json.load(open('${SINA}/agent-live-surfaces-v1.json')).get('factory_now_line',''))")"
  if [[ "${FN_LINE}" != *"FORGE FACTORY"* ]]; then
    echo "FAIL: surfaces factory_now_line missing FORGE FACTORY: ${FN_LINE}"
    FAIL=1
  fi
fi

RC=0
python3 "${ROOT}/scripts/rule_propagation_fanout_v1.py" --fast --json >/dev/null || RC=$?
if [[ "${RC}" -ne 0 ]]; then
  echo "FAIL: rule_propagation_fanout_v1.py --fast"
  FAIL=1
fi

if [[ "${FAIL}" -eq 0 ]]; then
  echo "PASS: validate-rule-propagation-fanout-v1"
  exit 0
fi
echo "FAIL: validate-rule-propagation-fanout-v1"
exit 1
