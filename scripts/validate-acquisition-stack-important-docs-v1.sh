#!/usr/bin/env bash
# sa-0516 — acquisition stack docs indexed in important_docs_index.py
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0516-acquisition-stack-important-docs_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
python3 - <<'PY'
import json
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("idi", Path("scripts/important_docs_index.py"))
idi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(idi)

paths = []
for _sid, _title, _aud, docs in idi._RAW_SECTIONS:
    for row in docs:
        paths.append(row[0])

required = [
    "product/ACQUISITION_STACK_LOCKED_v1.md",
    "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md",
    "product/PARTICIPATION_HOOKS_LOCKED_v1.md",
    "product/MERGEPACK_SUITE_LOCKED_v1.md",
]
missing = [p for p in required if p not in paths]
if missing:
    raise SystemExit(f"FAIL: important_docs_index missing {missing}")

for p in required:
    assert (Path(p)).is_file(), f"FAIL: doc not on disk {p}"

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
mp = (pp.get("signals_auto") or {}).get("mergepack") or {}
for key in ("stack", "ecosystem", "hooks", "suite"):
    val = mp.get(key) or ""
    if not val:
        raise SystemExit(f"FAIL: PROGRAM_PROGRESS mergepack.{key} missing")

print("OK: validate-acquisition-stack-important-docs-v1 · sa-0516")
PY
