#!/usr/bin/env bash
# validate-acquisition-stack-important-docs-t3-crossref-v1.sh — sa-0591 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0591-acquisition-stack-important-docs-t3-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0516-acquisition-stack-important-docs_LOCKED_v1.md"
index_script = root / "scripts/important_docs_index.py"
receipt = root / "receipts/sa-0516-receipt.json"

assert cross.is_file(), "missing sa-0591 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0516",
    "sa-0541",
    "sa-0566",
    "sa-0591",
    "sa-0516-acquisition-stack-important-docs_LOCKED_v1.md",
    "validate-acquisition-stack-important-docs-v1.sh",
    "important_docs_index.py",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0516 attachment missing"
assert index_script.is_file(), "important_docs_index.py missing"
assert receipt.is_file(), "canonical sa-0516 receipt missing"
for marker in ("_RAW_SECTIONS", "build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T3 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("acquisition_stack_important_docs_t3_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "t2_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.acquisition_stack_important_docs_t3_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0516":
    raise SystemExit("FAIL: canonical_sa must be sa-0516")
if hook.get("t1_echo_sa") != "sa-0541":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0541")
if hook.get("t2_echo_sa") != "sa-0566":
    raise SystemExit("FAIL: t2_echo_sa must be sa-0566")
if "sa-0591-acquisition-stack-important-docs-t3-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0591 attachment")

print("OK: validate-acquisition-stack-important-docs-t3-crossref-v1 · canonical=sa-0516 · t2=sa-0566 · sa-0591")
PY

bash validate-acquisition-stack-important-docs-v1.sh
