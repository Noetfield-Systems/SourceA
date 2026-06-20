#!/usr/bin/env bash
# REGISTRY drain rail — handoff + spine prerequisite
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
test -f "$ROOT/brain-os/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md"
test -f "$ROOT/brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md"
grep -q "sa-0202" "$ROOT/brain-os/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md"
bash "$ROOT/scripts/validate-execution-spine-v1.sh" >/dev/null
echo "OK: validate-registry-drain-rail-v1 · handoff + spine green"
