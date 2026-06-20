#!/usr/bin/env bash
# sa-0044 / sa-0094 / sa-0019 — ChatGPT critic Eval claim vs ~/.sina/eval_packet_v1b_report.json
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

bash validate-eval-critic-synthesis-alignment-v1.sh
bash validate-synthesis-eval-line-v1.sh

python3 - <<'PY'
import json
from pathlib import Path

from eval_report_capture import eval_synthesis_critic_drift_errors

root = Path(__file__).resolve().parents[1]
scripts = Path(__file__).resolve().parent
synthesis_path = root / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"
report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"

assert synthesis_path.is_file(), "missing synthesis LOCKED doc (sa-0044)"
assert report_path.is_file(), "missing eval_packet_v1b_report.json (sa-0044)"
audit = (scripts / "audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "eval_synthesis_critic_drift_errors" in audit, "audit missing critic drift guard (sa-0044)"

rep = json.loads(report_path.read_text(encoding="utf-8"))
errs = eval_synthesis_critic_drift_errors(synthesis_path.read_text(encoding="utf-8"), rep)
assert not errs, errs

wins = int(rep.get("live_pilot_wins") or rep.get("packet_wins") or 0)
count = int(rep.get("live_pilot_count") or rep.get("task_count") or 0)
pct = int(rep.get("live_pilot_win_pct") or rep.get("packet_win_pct") or 0)
print(
    f"OK: validate-eval-critic-claim-v1 · mode={rep.get('mode')} · "
    f"{wins}/{count} ({pct}%) matches synthesis + disk report"
)
PY
