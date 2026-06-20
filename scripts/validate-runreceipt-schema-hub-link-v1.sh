#!/usr/bin/env bash
# sa-0505 — RUNRECEIPT schema hub link
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
python3 - <<PY
from pathlib import Path
root = Path("$ROOT")
schema = root / "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md"
attach = root / "archive/attachments/2026-06-14/sa-0505-runreceipt-schema-hub-link_LOCKED_v1.md"
assert schema.is_file() and attach.is_file()
text = schema.read_text(encoding="utf-8")
assert "run.jsonl" in text and "summary.json" in text
PY
echo "OK: validate-runreceipt-schema-hub-link-v1 · sa-0505"
