#!/usr/bin/env bash
# sa-0032 / sa-0082 — fail if live eval ok but Eval-1b still listed in honest_score.not_here
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
from pathlib import Path

import audit_hub_source_alignment as audit
from system_roadmap import _build_world_target_map

report_path = Path.home() / ".sina" / "eval_packet_v1b_report.json"
assert report_path.is_file(), "missing eval_packet_v1b_report.json"

rep = json.loads(report_path.read_text(encoding="utf-8"))
live_ok = rep.get("mode") == "live" and rep.get("live_ok", rep.get("ok"))
assert hasattr(audit, "_check_honest_score_not_here_regression"), (
    "audit missing _check_honest_score_not_here_regression (sa-0032)"
)

wtm = _build_world_target_map()
not_here = (wtm.get("honest_score") or {}).get("not_here") or []
stale_eval = (
    "Eval-1b behavioral proof",
    "Eval-1b live LLM A/B",
    "Eval-1b below threshold",
)

if live_ok:
    for stale in stale_eval:
        assert not any(stale in str(line) for line in not_here), (
            f"live eval ok but not_here still lists {stale!r}: {not_here!r}"
        )

errors: list[str] = []
audit._check_honest_score_not_here_regression(errors, {"world_target_map": wtm})
assert not errors, errors

wins = int(rep.get("live_pilot_wins") or 0)
count = int(rep.get("live_pilot_count") or 0)
print(
    f"OK: validate-eval-live-not-here-regression-v1 · live_ok={live_ok} "
    f"· pilots {wins}/{count} · not_here={len(not_here)} rows"
)
PY
