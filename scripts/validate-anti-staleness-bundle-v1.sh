#!/usr/bin/env bash
# validate-anti-staleness-bundle-v1.sh — Anti-staleness v2 full verify chain (AS-01..AS-18)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SCRIPTS="$ROOT/scripts"

fail() { echo "FAIL: validate-anti-staleness-bundle-v1 — $*" >&2; exit 1; }

steps=(
  "validate-hub-p0-no-autorun-v1.sh"
  "validate-factory-spawn-gate-v1.sh"
  "validate-factory-conduct-v1.sh"
  "validate-bowl-hub-p0-alignment-v1.sh"
  "validate-bowl-duties-fresh-v1.sh"
  "validate-brain-sync-hooks-v1.sh"
  "validate-brain-snapshot-sync-v1.sh"
  "validate-active-now-factory-now-v1.sh"
  "validate-queue-ssot-unified-v1.sh"
  "validate-founder-hospital-gate-v1.sh"
  "validate-mandatory-read-paths-v1.sh"
  "validate-law-purity-ssot-v1.sh"
  "validate-governance-completion-backlog-v1.sh"
  "validate-authority-index-coverage-v1.sh"
  "validate-authority-root-coverage-v1.sh"
  "validate-serve-panel-build-v1.sh"
  "validate-goal1-tab-hint-no-autorun-v1.sh"
  "validate-master-tracker-active-now-v1.sh"
  "validate-no-archive-as-law-v1.sh"
  "validate-incident-registry-ids-v1.sh"
  "validate-agent-rules-in-charge-v1.sh"
  "validate-hub-advisor-track-naming-v1.sh"
  "validate-dashboard-no-autorun-v1.sh"
  "validate-s10-eternal-loop-v1.sh"
  "validate-brain-e2e-discipline-v1.sh"
  "validate-brain-intent-e2e-v1.sh"
  "validate-mega-chat-anchors-v1.sh"
  "validate-narrative-bridge-v1.sh"
  "validate-hub-surface-v1.sh"
  "validate-live-founder-decision-form-v1.sh"
  "validate-maintainer-scan-p0-v1.sh"
  "validate-universe-invariants-v1.sh"
  "validate-prompt-feed-no-autosend-copy-v1.sh"
  "validate-founder-close-line-gate-v1.sh"
  "validate-founder-zero-sina-command-v1.sh"
  "validate-law-supersession-surfaces-v1.sh"
  "validate-agent-memory-mirror-v1.sh"
  "validate-agentic-enforcement-stack-v2-v1.sh"
  "validate-judge-center-v1.sh"
  "validate-thread-room-v1.sh"
  "validate-hub-judge-alarm-strip-v1.sh"
  "validate-integration-fabric-registry-v1.py"
  "validate-copy-safety-hub-v1.sh"
  "validate-integrity-form-canvas-ssot-v1.sh"
  "validate-governance-critic-v1.sh"
  "validate-no-fake-progress-form-v1.sh"
  "validate-demo-write-path-v1.sh"
  "validate-governance-events-taxonomy-v1.sh"
  "validate-governance-chat-context-v1.sh"
)

for s in "${steps[@]}"; do
  if [[ "$s" == *.py ]]; then
    python3 "$SCRIPTS/$s" || fail "$s"
  else
    bash "$SCRIPTS/$s" || fail "$s"
  fi
done

echo "OK: validate-anti-staleness-bundle-v1 · ${#steps[@]} steps PASS"
