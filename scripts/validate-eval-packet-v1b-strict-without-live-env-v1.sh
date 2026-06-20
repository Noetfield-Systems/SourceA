#!/usr/bin/env bash
# sa-0024 — strict build runs validate-eval-packet-v1b-live without SINA_EVAL_1B_LIVE=1
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import re
import sys
from pathlib import Path

build = Path("build-sina-command-panel.py").read_text(encoding="utf-8")

if "validate-eval-packet-v1b-live.sh" not in build:
    print("FAIL: validate-eval-packet-v1b-live.sh not in strict build")
    sys.exit(1)

# Live validator line must exist and not be gated on SINA_EVAL_1B_LIVE / live_env
lines = build.splitlines()
live_idx = None
for i, line in enumerate(lines):
    if '_run_audit("validate-eval-packet-v1b-live.sh"' in line:
        live_idx = i
        break
if live_idx is None:
    print("FAIL: validate-eval-packet-v1b-live.sh _run_audit missing from build")
    sys.exit(1)

window = "\n".join(lines[max(0, live_idx - 12) : live_idx + 1])
if re.search(r"if\s+live_env\b", window) or re.search(
    r"if\s+.*SINA_EVAL_1B_LIVE", window
):
    print("FAIL: live validator call must not depend on SINA_EVAL_1B_LIVE / live_env")
    sys.exit(1)

strict_before = any(
    lines[j].strip() == "if strict:" for j in range(max(0, live_idx - 30), live_idx)
)
if not strict_before:
    print("FAIL: validate-eval-packet-v1b-live.sh must run under if strict:")
    sys.exit(1)

# sa-0127 chain must still be present (strict default eval chain)
if "validate-eval-packet-v1b-strict-build-chain-v1.sh" not in build:
    print("FAIL: strict-build-chain validator missing from build (sa-0127)")
    sys.exit(1)

print(
    "OK: validate-eval-packet-v1b-strict-without-live-env-v1 · "
    "live in strict default chain without SINA_EVAL_1B_LIVE gate (sa-0024)"
)
PY

bash validate-eval-packet-v1b-strict-build-chain-v1.sh
