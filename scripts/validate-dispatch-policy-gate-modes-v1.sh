#!/usr/bin/env bash
# sa-0611 — SHADOW vs ENFORCE documented in DISPATCH_POLICY_LOCKED_v1.md + model_dispatch SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from pathlib import Path

ROOT = Path.cwd().parent
DOC = ROOT / "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md"
assert DOC.is_file(), DOC
text = DOC.read_text(encoding="utf-8")
for needle in ("SHADOW", "ENFORCE", "gate_shadow_v1.jsonl", "gate_enforce_v1.jsonl", "gate_mode_v1.txt"):
    assert needle in text, f"missing in dispatch policy doc: {needle}"

import model_dispatch as md

modes = md._VALID_GATE_MODES  # noqa: SLF001
assert modes == ("off", "shadow", "enforce"), modes
status = md.gate_status_payload()
assert status.get("ok") is True, status
assert status.get("current_mode") in modes, status.get("current_mode")

from runtime.dispatch_policy.policy_engine import dispatch_policy_payload

dp = dispatch_policy_payload()
assert dp.get("ok") is not False, dp
assert dp.get("doc_path") == "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md", dp.get("doc_path")

print(
    f"OK: validate-dispatch-policy-gate-modes-v1 · modes={modes} "
    f"current={md.current_gate_mode()} doc=DISPATCH_POLICY_LOCKED_v1.md"
)
PY
