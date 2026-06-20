#!/usr/bin/env bash
# validate-trustfield-p10-strategic-pendings-t2-crossref-v1.sh — sa-0568 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0568-trustfield-p10-strategic-pendings-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0518-trustfield-p10-strategic-pendings_LOCKED_v1.md"
hub_script = root / "scripts/strategic_synthesis_hub.py"
receipt = root / "receipts/sa-0518-receipt.json"

assert cross.is_file(), "missing sa-0568 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0518",
    "sa-0543",
    "sa-0568",
    "sa-0518-trustfield-p10-strategic-pendings_LOCKED_v1.md",
    "strategic_synthesis_hub.py",
    "validate-trustfield-p10-strategic-pendings-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0518 attachment missing"
assert hub_script.is_file(), "strategic_synthesis_hub.py missing"
assert receipt.is_file(), "canonical sa-0518 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("trustfield_p10_strategic_pendings_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.trustfield_p10_strategic_pendings_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0518":
    raise SystemExit("FAIL: canonical_sa must be sa-0518")
if hook.get("t1_echo_sa") != "sa-0543":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0543")
if "sa-0568-trustfield-p10-strategic-pendings-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0568 attachment")

print("OK: validate-trustfield-p10-strategic-pendings-t2-crossref-v1 · canonical=sa-0518 · t1=sa-0543 · sa-0568")
PY

bash validate-trustfield-p10-strategic-pendings-v1.sh
