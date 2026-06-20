#!/usr/bin/env bash
# sa-0031 / sa-0081 — synthesis Eval line must match ~/.sina/eval_packet_v1b_report.json
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
import re
from pathlib import Path

from eval_report_capture import eval_synthesis_critic_drift_errors

root = Path(__file__).resolve().parents[1]
synthesis_path = root / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"

assert synthesis_path.is_file(), "missing synthesis LOCKED doc"
assert report_path.is_file(), "missing eval_packet_v1b_report.json"

synthesis = synthesis_path.read_text(encoding="utf-8")
rep = json.loads(report_path.read_text(encoding="utf-8"))
errs = eval_synthesis_critic_drift_errors(synthesis, rep)
assert not errs, errs

wins = int(rep.get("live_pilot_wins") or rep.get("packet_wins") or 0)
count = int(rep.get("live_pilot_count") or rep.get("task_count") or 0)
pct = int(rep.get("live_pilot_win_pct") or rep.get("packet_win_pct") or 0)
ratio = f"{wins}/{count}"

# #region agent log
try:
    from _debug_e2e_log_v1 import dbg  # noqa: WPS433

    pendings_line = re.search(r"^\| Eval-1b \|[^\n]+", synthesis, re.MULTILINE)
    dbg(
        hypothesis_id="D",
        location="validate-synthesis-eval-line-v1.sh:check",
        message="synthesis eval line check",
        data={
            "report_ratio": ratio,
            "report_pct": pct,
            "pendings_line": pendings_line.group(0) if pendings_line else None,
            "ratio_in_line": bool(pendings_line and ratio in pendings_line.group(0)),
            "pct_in_line": bool(pendings_line and f"{pct}%" in pendings_line.group(0)),
        },
    )
except Exception:
    pendings_line = re.search(r"^\| Eval-1b \|[^\n]+", synthesis, re.MULTILINE)
# #endregion

# sa-0031 — explicit Eval-1b pendings row must cite live ratio
if pendings_line is None:
    pendings_line = re.search(r"^\| Eval-1b \|[^\n]+", synthesis, re.MULTILINE)
assert pendings_line, "missing Eval-1b pendings row"
line = pendings_line.group(0)
assert ratio in line, f"pendings Eval-1b missing {ratio}"
assert f"{pct}%" in line, f"pendings Eval-1b missing {pct}%"

print(
    f"OK: validate-synthesis-eval-line-v1 · Eval-1b {ratio} ({pct}%) "
    f"aligned with {report_path.name}"
)
PY
