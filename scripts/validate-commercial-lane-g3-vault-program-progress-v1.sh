#!/usr/bin/env bash
# sa-0525 — PROGRAM_PROGRESS commercial_lane_g3_vault hook + validator wired
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0525-commercial-lane-g3-vault-evidence_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
hook = (pp.get("signals_auto") or {}).get("commercial_lane_g3_vault") or {}
for key in ("crossref_doc", "probe_fn", "append_fn", "validator", "vault_agents", "wire_progress_doc"):
    if key not in hook:
        raise SystemExit(f"FAIL: signals_auto.commercial_lane_g3_vault missing {key}")
if "sa-0525-commercial-lane-g3-vault" not in str(hook.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0525 attachment")
if hook.get("probe_fn") != "scripts/commercial_lane_g3_vault_v1.py::probe_g3_vault_visibility":
    raise SystemExit("FAIL: probe_fn mismatch")
if hook.get("append_fn") != "scripts/commercial_lane_g3_vault_v1.py::append_priority_g3_evidence_if_visible":
    raise SystemExit("FAIL: append_fn mismatch")

mod = Path("scripts/commercial_lane_g3_vault_v1.py").read_text(encoding="utf-8")
for fn in ("probe_g3_vault_visibility", "append_priority_g3_evidence_if_visible", "wire_g3_disk_status"):
    if f"def {fn}" not in mod:
        raise SystemExit(f"FAIL: commercial_lane_g3_vault_v1 missing {fn}")

print("OK: validate-commercial-lane-g3-vault-program-progress-v1 · sa-0525")
PY
bash scripts/validate-commercial-lane-g3-vault-evidence-v1.sh
