#!/usr/bin/env bash
# Gate new INCIDENT-NNN filings — registry check (INCIDENT-015).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INCIDENT_ID="${1:-${INCIDENT_ID:-}}"
if [[ -z "$INCIDENT_ID" ]]; then
  echo "FAIL: usage: validate-incident-filing-v1.sh INCIDENT-NNN" >&2
  exit 1
fi
if [[ ! "$INCIDENT_ID" =~ ^INCIDENT-[0-9]{3}$ ]]; then
  echo "FAIL: invalid incident id format: $INCIDENT_ID" >&2
  exit 1
fi
REG="$ROOT/brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"
if rg -q "\\*\\*${INCIDENT_ID#INCIDENT-}\\*\\*" "$REG" 2>/dev/null; then
  echo "FAIL: $INCIDENT_ID already assigned in AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md" >&2
  exit 1
fi
if rg -q "$INCIDENT_ID" "$ROOT/brain-os/incidents/" "$ROOT"/SINA_*INCIDENT* 2>/dev/null; then
  echo "FAIL: $INCIDENT_ID collision on disk — rg found existing references" >&2
  exit 1
fi
echo "OK: validate-incident-filing-v1 · $INCIDENT_ID slot free"
