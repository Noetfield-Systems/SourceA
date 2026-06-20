#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"

python3 -c "
from execution_intelligence_v2.api import intelligence_v2_payload
from execution_intelligence_v2.strategy_optimizer import planner_v2_signals

p = intelligence_v2_payload()
assert p.get('ok'), p
assert p.get('predictions'), 'missing predictions'
assert p.get('risk_scores'), 'missing risk_scores'
assert p.get('recommendations', {}).get('recommended_tasks'), 'missing recommendations'
assert p.get('causal_graph_summary', {}).get('link_count', 0) >= 0
sig = planner_v2_signals()
assert 'execution_intelligence_v2' in sig
print('PASS execution intelligence v2',
      'predictions', len(p['predictions']),
      'best', p['strategy']['summary'].get('best_next_action'))
"
