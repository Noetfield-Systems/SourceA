#!/bin/bash
# INCIDENT-005 B2 — true queue sync: home → repo
# Run once: bash scripts/finish-b2-sync.sh
set -euo pipefail

HOME_Q="$HOME/.sina/healthy-queue-30-active.json"
HOME_S="$HOME/.sina/healthy-queue-state-v1.json"
REPO_Q="$HOME/Desktop/SourceA/brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json"
REPO_S="$HOME/Desktop/SourceA/brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-state-v1.json"

echo "=== B2: Syncing home → repo queue ==="
cp "$HOME_Q" "$REPO_Q" && echo "✅ queue synced"
cp "$HOME_S" "$REPO_S" && echo "✅ state synced"

echo ""
echo "=== Gatekeeper ==="
python3 "$HOME/Desktop/SourceA/scripts/gatekeeper_v1.py"

echo ""
echo "=== Registry ==="
python3 "$HOME/Desktop/SourceA/scripts/goal-progress-v1.py" 2>/dev/null | grep -E "done|total|320" || \
python3 -c "
import json; reg=json.load(open('$HOME/Desktop/SourceA/brain-os/plan-registry/sourcea-1000/REGISTRY.json'))
plans=reg.get('plans',[]); done=sum(1 for p in plans if p.get('status')=='done')
print(f'Registry: {done}/1000 done')
"
