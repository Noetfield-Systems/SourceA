#!/usr/bin/env bash
# sa-0513 — ChatGPT commercial critique cross-ref vs PROGRAM_PROGRESS locks
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0513-commercial-critique-vs-program-progress-locks_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
python3 - <<'PY'
import json
from pathlib import Path

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
cc = (pp.get("signals_auto") or {}).get("commercial_critique") or {}
required = ("crossref_doc", "aligned", "open_gaps", "dispatch_ready_note")
missing = [k for k in required if k not in cc]
if missing:
    raise SystemExit(f"FAIL: PROGRAM_PROGRESS signals_auto.commercial_critique missing {missing}")
if "sa-0513-commercial-critique" not in str(cc.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0513 attachment")
if "legal_artifacts" not in str(cc.get("open_gaps", [])):
    raise SystemExit("FAIL: open_gaps must include legal_artifacts")
print("OK: validate-commercial-critique-program-progress-locks-v1 · sa-0513")
PY
