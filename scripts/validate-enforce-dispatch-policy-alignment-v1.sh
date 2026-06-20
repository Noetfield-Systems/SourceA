#!/usr/bin/env bash
# sa-0020 / sa-0086 — synthesis ENFORCE claims must match gate SSOT + dispatch-policy API
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
import urllib.request
from pathlib import Path

import model_dispatch
from runtime.dispatch_policy.policy_engine import dispatch_policy_payload

root = Path(__file__).resolve().parents[1]
synthesis_path = root / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
assert synthesis_path.is_file(), "missing synthesis doc (sa-0020)"

gate_disk = model_dispatch.current_gate_mode()
payload = dispatch_policy_payload()
assert payload.get("gate_mode") == gate_disk, (
    f"payload gate_mode drift: {payload.get('gate_mode')!r} vs disk {gate_disk!r}"
)
assert payload.get("current_gate_mode") == gate_disk, payload.get("current_gate_mode")

with urllib.request.urlopen("http://127.0.0.1:13020/api/dispatch-policy-v1", timeout=60) as resp:
    api = json.loads(resp.read().decode())
assert api.get("ok"), api
assert api.get("gate_mode") == gate_disk, (
    f"API gate_mode drift: {api.get('gate_mode')!r} vs disk {gate_disk!r}"
)
assert api.get("current_gate_mode") == gate_disk, api.get("current_gate_mode")
assert api.get("gate_is_enforce") == (gate_disk == "enforce"), api.get("gate_is_enforce")

synthesis = synthesis_path.read_text(encoding="utf-8")
errs = model_dispatch.enforce_synthesis_critic_drift_errors(synthesis, gate_disk)
assert not errs, errs

print(
    f"OK: validate-enforce-dispatch-policy-alignment-v1 · "
    f"gate_mode={gate_disk} · API+payload aligned · synthesis ok"
)
PY
