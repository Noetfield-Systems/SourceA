#!/usr/bin/env bash
# validate-wire-lane-progress-t1-crossref-v1.sh — sa-0537 ACT T1 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0537-wire-lane-progress-t1-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0512-wire-lane-progress_LOCKED_v1.md"
wire_doc = root / "WIRE_LANE_PROGRESS.md"
receipt = root / "receipts/sa-0512-receipt.json"

assert cross.is_file(), "missing sa-0537 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0512",
    "sa-0537",
    "sa-0512-wire-lane-progress_LOCKED_v1.md",
    "WIRE_LANE_PROGRESS.md",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0512 attachment missing"
assert wire_doc.is_file(), "WIRE_LANE_PROGRESS.md missing"
assert receipt.is_file(), "canonical sa-0512 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T1 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("wire_lane_progress_t1_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.wire_lane_progress_t1_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0512":
    raise SystemExit("FAIL: canonical_sa must be sa-0512")
if "sa-0537-wire-lane-progress-t1-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0537 attachment")

print("OK: validate-wire-lane-progress-t1-crossref-v1 · canonical=sa-0512 · sa-0537")
PY

bash validate-wire-lane-progress-v1.sh
