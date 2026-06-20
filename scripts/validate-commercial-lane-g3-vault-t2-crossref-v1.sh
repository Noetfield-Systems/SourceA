#!/usr/bin/env bash
# validate-commercial-lane-g3-vault-t2-crossref-v1.sh — sa-0575 ACT T2 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0575-commercial-lane-g3-vault-t2-crossref_LOCKED_v1.md"
canonical_doc = root / "archive/attachments/2026-06-14/sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md"
probe_fn = root / "scripts/commercial_lane_g3_vault_v1.py"
receipt = root / "receipts/sa-0525-receipt.json"

assert cross.is_file(), "missing sa-0575 cross-ref doc"
text = cross.read_text(encoding="utf-8")
for needle in (
    "sa-0525",
    "sa-0550",
    "sa-0575",
    "sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md",
    "probe_g3_vault_visibility",
    "append_priority_g3_evidence_if_visible",
    "validate-commercial-lane-g3-vault-program-progress-v1.sh",
):
    assert needle in text, f"cross-ref missing {needle}"
assert canonical_doc.is_file(), "canonical sa-0525 attachment missing"
assert probe_fn.is_file(), "commercial_lane_g3_vault_v1.py missing"
assert receipt.is_file(), "canonical sa-0525 receipt missing"
for marker in ("build-sina-command-panel.py", "hub_self_refresh"):
    assert marker not in text, f"T2 cross-ref must not duplicate implementation prose ({marker})"

pp = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("commercial_lane_g3_vault_t2_crossref") or {}
for key in ("crossref_doc", "canonical_sa", "t1_echo_sa", "validator"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.commercial_lane_g3_vault_t2_crossref missing {key}")
if hook.get("canonical_sa") != "sa-0525":
    raise SystemExit("FAIL: canonical_sa must be sa-0525")
if hook.get("t1_echo_sa") != "sa-0550":
    raise SystemExit("FAIL: t1_echo_sa must be sa-0550")
if "sa-0575-commercial-lane-g3-vault-t2-crossref" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0575 attachment")

print("OK: validate-commercial-lane-g3-vault-t2-crossref-v1 · canonical=sa-0525 · t1=sa-0550 · sa-0575")
PY

bash validate-commercial-lane-g3-vault-program-progress-v1.sh
