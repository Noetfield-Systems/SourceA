#!/usr/bin/env bash
# validate-mergepack-kpi-trio-t3-crossref-v1.sh — sa-0584 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0584-mergepack-kpi-trio-t3-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0509-mergepack-kpi-trio_LOCKED_v1.md"
receipt = root / "receipts/sa-0509-receipt.json"

assert cross.is_file(), "missing sa-0584 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0509",
    "sa-0534",
    "sa-0559",
    "sa-0584",
    "sa-0509-mergepack-kpi-trio_LOCKED_v1.md",
    "validate-mergepack-kpi-trio-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0509 attachment missing"
assert receipt.is_file(), "canonical sa-0509 receipt missing"
for marker in ("kpiTrioHtml", "command-data-shell.json", "build-sina-command-panel.py"):
    assert marker not in text, f"T3 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("mergepack_kpi_trio_t3_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "t2_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.mergepack_kpi_trio_t3_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0509":
    raise SystemExit("FAIL: canonical_sa must be sa-0509")
if hook.get("t1_echo_sa") != "sa-0534":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0534")
if hook.get("t2_echo_sa") != "sa-0559":
    raise SystemExit("FAIL: t2_echo_sa must be sa-0559")
if "sa-0584-mergepack-kpi-trio-t3-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0584 attachment")

print("OK: validate-mergepack-kpi-trio-t3-crossref-v1 · canonical=sa-0509 · t2=sa-0559 · sa-0584")
PY

bash validate-mergepack-kpi-trio-v1.sh
