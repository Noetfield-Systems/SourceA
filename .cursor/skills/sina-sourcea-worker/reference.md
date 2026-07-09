# Worker reference — YAML, validators, paths

## WORKER_ROUND_REPORT (required footer every turn)

```yaml
status: WORKER_ROUND_REPORT
round_type: check | act | verify
sa_focus: sa-XXXX
phase: validate | act | closeout
validate:
  spine: PASS|FAIL
  critical_bugs: 0
  validators_run:
    - name: find_critical_bugs.py
      result: PASS|FAIL
act:
  performed: true|false
  fixes: []
  files_touched: []
verify:
  command: build-sina-command-panel.py + find_critical_bugs.py
  result: PASS|FAIL
  critical_bugs: 0
closeout:
  registry_updated: []
  priority_row: true|false
  execution_log: none
summary: One line — what was proven logged
next_action: act | verify | NONE
```

Broker parses this block from your last reply. **No report = turn did not happen.**

## CHECK turn validators (read-only)

```bash
cd ~/Desktop/Noetfield-Systems/SourceA/scripts
python3 find_critical_bugs.py          # SINA_FCB_FAST=1 optional on CHECK
python3 audit_hub_source_alignment.py
bash validate-registry-honest-gate-v1.sh
```

Report gaps vs task `.md` — `next_action: act` only if gap found.

## ACT turn

```bash
python3 scripts/prompt_feasibility_gate.py --role worker --strict
python3 scripts/cursor_window_preflight_v1.py   # when paste path used
```

Minimal diff · run task `.md` verify commands · no receipt-only closeout.

## VERIFY turn

```bash
cd ~/Desktop/Noetfield-Systems/SourceA/scripts
SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py
python3 find_critical_bugs.py
```

Receipt: `brain-os/plan-registry/sourcea-1000/receipts/sa-XXXX-receipt.json`

## Broker CLI

```bash
python3 scripts/goal1_lane_broker.py pickup
python3 scripts/goal1_lane_broker.py worker-submit --stdin
python3 scripts/goal1_lane_broker.py brain-poll    # Brain only — Worker does not poll
```

## Auto-run / headless

- **RUN INBOX** when Brain routes — one sa per turn → broker. Cursor AUTO-RUN does not exist.
- Worker chat may be empty; output still must end with `WORKER_ROUND_REPORT`.
- Watch: `~/.sina/goal1-worker-batch-latest.log` for `AGENT START` / `AGENT DONE`.

## Honest metrics

```bash
python3 scripts/program-1000-honest-status-v1.py --write
bash scripts/enforce-registry-hygiene-v1.sh
```

Valid YES = receipt + broker proof — quote this in reports, not REGISTRY `done` count alone.
