#!/usr/bin/env bash
# sa-0019 / sa-0081 — synthesis Eval claims must match ~/.sina/eval_packet_v1b_report.json
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
from pathlib import Path

from eval_report_capture import eval_synthesis_critic_drift_errors

root = Path(__file__).resolve().parents[1]
synthesis_path = root / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"

assert synthesis_path.is_file(), "missing SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md (sa-0019)"
assert report_path.is_file(), "missing eval_packet_v1b_report.json (sa-0019)"

synthesis = synthesis_path.read_text(encoding="utf-8")
rep = json.loads(report_path.read_text(encoding="utf-8"))
errs = eval_synthesis_critic_drift_errors(synthesis, rep)
assert not errs, errs

wins = int(rep.get("live_pilot_wins") or 0)
count = int(rep.get("live_pilot_count") or 0)
pct = int(rep.get("live_pilot_win_pct") or rep.get("packet_win_pct") or 0)
print(
    f"OK: validate-eval-critic-synthesis-alignment-v1 · "
    f"mode={rep.get('mode')} live_ok={rep.get('live_ok')} · {wins}/{count} ({pct}%) aligned"
)
PY
