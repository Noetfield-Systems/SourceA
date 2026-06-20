#!/usr/bin/env bash
# validate-machines-brokers-stale-copy-v1.sh — live machine/broker injects must not steer stale brand
set -euo pipefail
SINA="${HOME}/.sina"
FORBIDDEN='Sina Command|Prompt feed|Confirm auto-send|AUTO-RUN P0'

fail() { echo "FAIL: validate-machines-brokers-stale-copy-v1 — $*" >&2; exit 1; }

LIVE=(
  "goal1-lane-broker-v1.json"
  "brain-broker-inbox-v1.json"
  "worker-prompt-inbox-v1.json"
  "brain-wire-v1.json"
  "governance-brain-wire-v1.json"
  "l1-brain-pipeline-wire-v1.json"
  "l1-agent-pipeline-wire-v1.json"
  "monitor-live-v1.json"
  "run-inbox-routing-v1.json"
  "run-inbox-disk-truth-v1.json"
  "agent-live-surfaces-v1.json"
  "worker-live-context-v1.json"
  "brain-live-context-v1.json"
  "execution-lane-v1.json"
  "governance-stairlift-v1.json"
  "worker-asf-directive-latch-v1.json"
  "mac-health/live-pulse-v1.json"
)

for rel in "${LIVE[@]}"; do
  path="${SINA}/${rel}"
  if [[ ! -f "$path" ]]; then
    echo "SKIP missing ${rel}"
    continue
  fi
  if grep -Eiq "$FORBIDDEN" "$path"; then
    grep -Ein "$FORBIDDEN" "$path" | head -5 >&2
    fail "stale copy in ${rel}"
  fi
  echo "✓ clean ${rel}"
done

bash "$(dirname "$0")/validate-disk-live-wire-v1.sh" >/dev/null || fail "disk-live-wire"

echo "OK: validate-machines-brokers-stale-copy-v1 · ${#LIVE[@]} live surfaces"
