#!/usr/bin/env bash
# sa-0502 — RunReceipt artifact schema wired to validate-verify-wire-v1
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
ROOT="$(cd .. && pwd)"
export ROOT

python3 - <<'PY'
from pathlib import Path
import os

root = Path(os.environ["ROOT"])
for p in (
    root / "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md",
    root / "archive/attachments/2026-06-14/sa-0502-verify-wire-runreceipt-schema_LOCKED_v1.md",
    root / "scripts/runreceipt/pack_v1.py",
):
    assert p.is_file(), f"missing {p}"
text = (root / "scripts/validate-verify-wire-v1.sh").read_text(encoding="utf-8")
assert "assert_runreceipt_artifacts" in text, "validate-verify-wire-v1 must assert artifacts (sa-0522)"
assert "build_pack" not in text, "validate-verify-wire-v1 must not auto-build (sa-0522)"
PY

python3 - <<'PY'
from runreceipt.pack_v1 import build_pack

out = build_pack(status="PASS")
assert out.get("ok"), out
PY

bash validate-verify-wire-v1.sh
echo "OK: validate-verify-wire-runreceipt-schema-v1 · sa-0502 schema + wire pack PASS"
