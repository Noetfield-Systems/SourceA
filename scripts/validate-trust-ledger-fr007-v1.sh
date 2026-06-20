#!/usr/bin/env bash
# sa-0503 — TRUST_LEDGER FR-007 shipped signal
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
ROOT="$(cd .. && pwd)"

python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
doc = root / "TRUST_LEDGER_SCHEMA_LOCKED_v1.md"
attach = root / "archive/attachments/2026-06-14/sa-0503-trust-ledger-fr007_LOCKED_v1.md"
assert doc.is_file(), doc
assert attach.is_file(), attach
PY
bash validate-founder-request-fleet-sync-v1.sh
echo "OK: validate-trust-ledger-fr007-v1 · sa-0503"
