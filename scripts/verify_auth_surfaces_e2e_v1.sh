#!/usr/bin/env bash
# Legacy wrapper — delegates to SourceA auth domains machine (live).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/sourcea_auth_domains_audit_v1.py" --mode live "$@"
