#!/usr/bin/env bash
# validate-founder-agentic-commercial-policy-v1.sh — founder policy lock checks
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$ROOT/brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md"
FLAG="${HOME}/.sina/auto-run-disabled-v1.flag"
CONSOLIDATED="/Users/sinakazemnezhad/Desktop/SinaaiDataBase/FOUNDER_LIVE_AGENT_CONSOLIDATED_LOCKED_v1.md"
SKILL="$ROOT/agent-skills/shared/agentic-commercial/SKILL.md"
REGISTRY="$ROOT/agent-skills/REGISTRY_LOCKED_v1.json"

fail() { echo "FAIL: validate-founder-agentic-commercial-policy-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing law $LAW"
grep -q "Cursor AUTO-RUN is not a goal" "$LAW" || fail "law missing AUTO-RUN depriority"
grep -q "founder never dials or sends email" "$LAW" || fail "law missing agentic commercial line"

[[ -f "$FLAG" ]] || fail "auto-run-disabled flag must exist at $FLAG"

[[ -f "$CONSOLIDATED" ]] || fail "missing consolidated doc"
grep -q "FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN" "$CONSOLIDATED" || fail "consolidated not wired"
grep -q "founder never sends email" "$CONSOLIDATED" || fail "consolidated missing email law"

[[ -f "$SKILL" ]] || fail "missing shared skill $SKILL"
grep -q "sina-agentic-commercial" "$REGISTRY" || fail "registry missing agentic-commercial"

echo "OK: validate-founder-agentic-commercial-policy-v1"
