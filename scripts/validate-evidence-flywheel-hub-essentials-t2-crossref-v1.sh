#!/usr/bin/env bash
# validate-evidence-flywheel-hub-essentials-t2-crossref-v1.sh — sa-0569 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0569-evidence-flywheel-hub-essentials-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0519-evidence-flywheel-hub-essentials_LOCKED_v1.md"
flywheel = root / "product/EVIDENCE_FLYWHEEL_LOCKED_v1.md"
receipt = root / "receipts/sa-0519-receipt.json"

assert cross.is_file(), "missing sa-0569 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0519",
    "sa-0544",
    "sa-0569",
    "sa-0519-evidence-flywheel-hub-essentials_LOCKED_v1.md",
    "EVIDENCE_FLYWHEEL_LOCKED_v1.md",
    "hub_essentials_pillar",
    "validate-evidence-flywheel-hub-essentials-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0519 attachment missing"
assert flywheel.is_file(), "EVIDENCE_FLYWHEEL_LOCKED_v1.md missing"
assert receipt.is_file(), "canonical sa-0519 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("evidence_flywheel_hub_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.evidence_flywheel_hub_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0519":
    raise SystemExit("FAIL: canonical_sa must be sa-0519")
if hook.get("t1_echo_sa") != "sa-0544":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0544")
if "sa-0569-evidence-flywheel-hub-essentials-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0569 attachment")

print("OK: validate-evidence-flywheel-hub-essentials-t2-crossref-v1 · canonical=sa-0519 · t1=sa-0544 · sa-0569")
PY

bash validate-evidence-flywheel-hub-essentials-v1.sh
