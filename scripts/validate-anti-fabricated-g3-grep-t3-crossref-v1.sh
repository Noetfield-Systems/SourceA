#!/usr/bin/env bash
# validate-anti-fabricated-g3-grep-t3-crossref-v1.sh — sa-0586 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0586-anti-fabricated-g3-grep-t3-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0511-anti-fabricated-g3_LOCKED_v1.md"
receipt = root / "receipts/sa-0511-receipt.json"

assert cross.is_file(), "missing sa-0586 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0511",
    "sa-0536",
    "sa-0561",
    "sa-0586",
    "sa-0511-anti-fabricated-g3_LOCKED_v1.md",
    "validate-anti-fabricated-g3-grep-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0511 attachment missing"
assert receipt.is_file(), "canonical sa-0511 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T3 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("anti_fabricated_g3_grep_t3_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "t2_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.anti_fabricated_g3_grep_t3_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0511":
    raise SystemExit("FAIL: canonical_sa must be sa-0511")
if hook.get("t1_echo_sa") != "sa-0536":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0536")
if hook.get("t2_echo_sa") != "sa-0561":
    raise SystemExit("FAIL: t2_echo_sa must be sa-0561")
if "sa-0586-anti-fabricated-g3-grep-t3-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0586 attachment")

print("OK: validate-anti-fabricated-g3-grep-t3-crossref-v1 · canonical=sa-0511 · t2=sa-0561 · sa-0586")
PY

bash validate-anti-fabricated-g3-grep-v1.sh
