#!/usr/bin/env bash
# SourceA auth domains — live audit wrapper (app · ca · uk)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/sourcea_auth_domains_audit_v1.py" --mode live --json
