# CURSOR FIX — SourceA Overnight Loop Reset
**Registry: 335/1000 done. Queue poisoned. Fix and restart.**

---

## WHAT BROKE

Queue `~/.sina/healthy-queue-30-active.json` had commercial/done tasks (sa-0153, sa-0501–sa-0509).
`autorun_dispatcher_v1.py` hit INCIDENT-004 → aborted every turn → zero progress.

---

## RUN THESE COMMANDS IN ORDER — NO SKIPPING

```bash
# 1. Kill everything
pkill -f autorun_dispatcher_v1.py
pkill -f start-overnight-3engine
rm -f ~/.sina/overnight-3engine-v1.pid

# 2. Write correct queue to ~/.sina/
# (queue was regenerated to sa-0326–sa-0365 · phase-s3-scoreboard-fleet · no live eval)
cp ~/Desktop/SourceA/os/plan-library/sourcea-1000/prompts/healthy-queue-30-active.json \
   ~/.sina/healthy-queue-30-active.json

# 3. Reset queue state to pos 1
echo '{"next_pos":1,"queue_total":30,"reset_at":"2026-06-08"}' \
  > ~/.sina/healthy-queue-state-v1.json

# 4. Reset broker to idle
python3 -c "
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home()/'.sina/goal1-lane-broker-v1.json'
p.write_text(json.dumps({
  'schema':'goal1-lane-broker-v1',
  'status':'idle',
  'updated_at':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
  'note':'clean-restart'
})+'\n')
print('broker reset OK')
"

# 5. Fix ACTIVE_NOW.md
cat > ~/Desktop/SourceA/ACTIVE_NOW.md << 'EOF'
# ACTIVE NOW

Current Queue: sa-0326–sa-0365 · phase-s3-scoreboard-fleet
Current sa_id: sa-0326 · check · pos 1/30
Reset: 2026-06-08
EOF

# 6. Start overnight loop
bash ~/Desktop/SourceA/scripts/start-overnight-3engine-v1.sh

# 7. Verify turn 1
sleep 5
tail -20 ~/.sina/overnight-3engine-v1.log
```

---

## EXPECTED OUTPUT (turn 1)

```
DISPATCHER → API engine sa=sa-0326 role=check pos=1/30
```

If you see `sa-0326` → loop is healthy. Registry will advance.

---

## VERIFIED FACTS (read from disk before writing this prompt)

| Fact | Value |
|------|-------|
| Registry done | 335 |
| Correct queue start | sa-0326 (first s3 backlog T1) |
| Correct queue end | sa-0365 |
| Phase | phase-s3-scoreboard-fleet |
| live_eval_required | false on all 30 |
| Queue file updated | os/plan-library/sourcea-1000/prompts/healthy-queue-30-active.json |
| sa-0355/0356 | already DONE — excluded from queue |

---

## IF TURN 1 STILL SHOWS STALE sa-0153

Dispatcher stale-queue guard may not be reading `~/.sina/` correctly. Run:

```bash
python3 -c "
import json
from pathlib import Path
q = json.loads((Path.home()/'.sina/healthy-queue-30-active.json').read_text())
print('first id:', q['queue'][0]['sa_id'])
print('range:', q['sa_range'])
"
```

Must print `sa-0326`. If not, step 2 failed — rerun it.
