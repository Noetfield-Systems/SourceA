#!/usr/bin/env bash
# Strict build must leave Eval-1b report + capture meta under ~/.sina
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from eval_report_capture import assert_capture_artifacts, capture_eval_report

errs = assert_capture_artifacts()
if errs and any("strict_build_capture" in e for e in errs):
    capture_eval_report(strict=True)
    errs = assert_capture_artifacts()
if errs:
    for e in errs:
        print(f"FAIL: {e}")
    raise SystemExit(1)
from pathlib import Path
import json

rep = json.loads((Path.home() / ".sina" / "eval_packet_v1b_report.json").read_text())
print(
    f"OK: validate-eval-report-capture-v1 · {rep.get('path')} · "
    f"mode={rep.get('mode')} ci={rep.get('ci_mode')}"
)
PY
