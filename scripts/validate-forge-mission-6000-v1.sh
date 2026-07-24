#!/usr/bin/env bash
# Validate Forge Mission 6000 — 3 packs × 1000 + master manifest.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "=== validate-forge-mission-6000-v1 ==="

for pack in \
  sourcea-site-score-up-1000 \
  sourcea-site-score-up-1000-batch2 \
  forge-terminal-score-up-1000 \
  chat-unify-score-up-1000; do
  reg="$ROOT/brain-os/plan-registry/$pack/REGISTRY.json"
  test -f "$reg" || { echo "FAIL: missing $reg"; exit 1; }
  python3 -c "
import json,sys
r=json.load(open('$reg'))
n=len(r.get('plans',[]))
if r.get('count',n)!=1000 or n!=1000:
    sys.exit(f'FAIL $pack count={r.get(\"count\")} plans={n}')
ids=[p['id'] for p in r['plans']]
if len(ids)!=len(set(ids)):
    sys.exit('FAIL duplicate ids in $pack')
print('OK $pack', ids[0], '…', ids[-1])
"
done

test -f "$ROOT/docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md" || { echo "FAIL: law"; exit 1; }
test -f "$ROOT/data/forge-visual-parity-contract-v1.json" || { echo "FAIL: visual contract"; exit 1; }
test -f "$ROOT/brain-os/plan-registry/FORGE_MISSION_6000_MASTER_v1.json" || { echo "FAIL: master"; exit 1; }

python3 -c "
import json
from pathlib import Path
titles=set()
for pack in Path('brain-os/plan-registry').glob('*/REGISTRY.json'):
    if 'score-up' not in str(pack):
        continue
    for p in json.loads(pack.read_text())['plans']:
        t=p['title'].lower().strip()
        if t in titles:
            raise SystemExit(f'DUP title: {p[\"title\"]}')
        titles.add(t)
print(f'OK cross-pack unique titles: {len(titles)}')
"

echo "validate-forge-mission-6000-v1.sh: PASS · 6000 plans"
