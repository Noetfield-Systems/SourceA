#!/usr/bin/env bash
# validate-agent-runtime-cloud-ci-v1.sh — deploy/CI tier · network validators
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0

_run() {
  local name="$1"
  shift
  if "$@"; then
    echo "OK: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

_run_sh() {
  local name="$1"
  shift
  if bash "$@"; then
    echo "OK: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

echo "=== Agent runtime cloud-CI ==="

_run_sh "mac-light" scripts/validate-agent-runtime-mac-light-v1.sh
_run_sh "client" scripts/validate-cloud-comprehension-client-v1.sh
_run_sh "railway" scripts/validate-cloud-comprehension-railway-v1.sh
_run_sh "hub-contract" scripts/validate-comprehension-hub-contract-v1.sh
_run_sh "nerve-line" scripts/validate-comprehension-nerve-line-v1.sh
_run_sh "ld-live" scripts/validate-cloud-ld-drain-live-v1.sh

if [[ "$fail" -eq 0 ]]; then
  echo "PASS: validate-agent-runtime-cloud-ci-v1"
  exit 0
fi
echo "FAIL: validate-agent-runtime-cloud-ci-v1"
exit 1
