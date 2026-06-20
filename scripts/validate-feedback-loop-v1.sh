#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
import json
from pathlib import Path

from execution_intelligence.feedback_loop.api import feedback_v1_payload
from execution_intelligence.feedback_loop.loop_engine import SIGNALS_PATH, run_feedback_loop

required = {
    'signal_id', 'signal_type', 'action_id', 'weight', 'reason',
    'source_pattern_id', 'source_decision_id', 'created_at',
}

r = run_feedback_loop(force=True)
assert r.get('ok'), r
assert r.get('signals_count', 0) > 0, 'no signals generated'
assert SIGNALS_PATH.is_file(), 'output file missing'

signals = []
for line in SIGNALS_PATH.read_text(encoding='utf-8').splitlines():
    if line.strip():
        signals.append(json.loads(line))
assert signals, 'jsonl empty'
assert required.issubset(signals[0].keys()), signals[0]
assert signals[0]['signal_type'] in ('prefer', 'avoid', 'reinforce', 'deprioritize')

p = feedback_v1_payload()
assert p.get('ok'), p
assert p.get('schema') == 'execution-feedback-v1'
assert p.get('active_signals'), 'API active_signals empty'
assert p.get('weighted_ranking_summary'), 'ranking missing'
assert 'prefer_actions' in p and 'avoid_actions' in p
assert 'reinforcement_signals' in p and 'deprioritized_actions' in p

print('PASS feedback loop v1', 'signals', len(signals), 'ranked', len(p['weighted_ranking_summary']))
"
