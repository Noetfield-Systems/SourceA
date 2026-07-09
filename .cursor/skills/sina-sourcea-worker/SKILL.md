---
name: sina-sourcea-worker
description: >-
  SourceA Goal 1 Worker — INBOX drain, CHECK/ACT/VERIFY per sa, broker submit,
  honest receipts only. Use when RUN INBOX, worker turn, sa-#### task, registry
  drain, WORKER_ROUND_REPORT, goal1_lane_broker, or headless auto-run follow-up.
disable-model-invocation: true
---

# SourceA Worker

**Routine skills:** `@sina-conscious-recovery` (thin context / governance topics) · `@agent-self-audit-loop` (session-start/close) · `shared/truth-projection/SKILL.md` (Goal 1 drain)

**Workspace:** `~/Desktop/Noetfield-Systems/SourceA` only · **You are not** maintainer, Brain, or broker chat.

## Load every session

1. `python3 scripts/agent_session_gate_run_v1.py --role worker --json` — receipt `ok=true`
2. `python3 scripts/agent_truth_bundle_v1.py --json` — disk truth same turn
3. `HUB_DEACTIVATED` law (`SINA_AUTHORITY_INDEX_MAP` row) — **never** legacy hub brand in founder text · **never** read all incidents
4. `brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`
5. `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md` — **INCIDENT-024** (machine owns order)
6. Skills: `agent-skills/shared/truth-projection/SKILL.md` · `agent-skills/shared/founder-freeze-conduct/SKILL.md`

**Law:** Cursor AUTO-RUN / Hub batch buttons = **STALE**. Execution = **RUN INBOX** only.

**REGISTRY_DRAIN:** `REGISTRY_DRAIN_RAIL_LOCKED_v1.md` · `REGISTRY_DRAIN_PROCESS_LOCKED_v1.md` — one sa/turn · receipt logged only.

## Founder close-line (INCIDENT-028 — mandatory)

**NEVER:** "Confirm auto-send" · legacy hub brand name · "read all incidents" · "Prompt feed" as daily path

**Pre-ship (fast ~2s):** `python3 scripts/agent_session_gate_run_v1.py --role worker --scan-text "<draft>" --pre-ship`

**CORRECT:** Worker chat **RUN INBOX** · optional Worker Hub `http://127.0.0.1:13020/` — queue from `live-ongoing-prompts-next-10-v1.json`

**P0:** Worker Hub → **Safety check** · M1 Canvas PICKs — **never** legacy `/legacy/` tabs as daily path.

## One turn contract

```text
FEASIBILITY → INBOX role (one) → EXECUTE → WORKER_ROUND_REPORT → broker worker-submit → STOP
```

| Role | Do | Forbidden |
|------|-----|-----------|
| **CHECK** | Read task .md · run read-only validators · gap report | implement · closeout · pick 30 |
| **ACT** | Minimal diff for bound `sa_id` only | closeout · batch · second sa |
| **VERIFY** | Validators + receipt + honest closeout | implement new scope |

**Law:** one prompt = one purpose · one sa per turn · disk beats chat.

## INBOX (disk SSOT)

```bash
cd ~/Desktop/Noetfield-Systems/SourceA
python3 scripts/worker_inject_lib.py --status
```

| Path | Purpose |
|------|---------|
| `~/.sina/worker-prompt-inbox-v1.json` | Machine pending |
| `.sina-loop/INBOX.md` | Human-readable same prompt |

- If `pending: true` → execute **disk** prompt (not chat memory).
- Headless auto-run: Hub delivers INBOX; you may run via `run inbox` or agent CLI — same rules.
- **Never** edit `~/Desktop/Noetfield-Systems/SourceA` hub (`agent-control-panel`, `sina-command-server.py`) — maintainer only.

## Feasibility (before ACT)

```bash
python3 scripts/prompt_feasibility_gate.py --role worker --strict
```

On `STOP_INJECT` / `FEASIBILITY_BLOCKED` → report `BLOCKED` · no implement.

## Broker (mechanical — not Brain chat)

After every turn, last lines of reply must include parseable YAML (see reference.md).

```bash
python3 scripts/goal1_lane_broker.py worker-submit --stdin   # paste WORKER_ROUND_REPORT block
python3 scripts/worker_inject_lib.py --clear
```

Brain polls `brain-poll` · you **submit** · broker advances queue.

## Honest progress (only valid proof)

| Counts | Does not count |
|--------|----------------|
| `receipts/sa-XXXX-receipt.json` logged | YAML batch stamp · chat claim · REGISTRY without receipt |
| Broker CHECK→ACT→VERIFY chain | Hub % without receipt |
| `enforce-registry-hygiene-v1.sh` PASS | fake done in REGISTRY |

```bash
python3 scripts/enforce-registry-hygiene-v1.sh
python3 scripts/program-1000-honest-status-v1.py --write
```

## VERIFY closeout checklist

**Law:** `SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1.md` · `WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md` — never full `find_critical_bugs` on VERIFY (60–180s stall).

```bash
cd ~/Desktop/Noetfield-Systems/SourceA/scripts
bash worker_turn_entry_v1.sh   # gate + anti-staleness auto-heal
bash worker_verify_ultra_v1.sh # probe + heal + hub check (~1–8s)
```

- Receipt `source` ∈ `goal1_lane_broker` · `worker_inbox` · `api` · `maintainer_executor`
- `critical_bugs: 0` on **FCB fast** before claiming PASS (full fleet = Hub Safety only)
- One sa in `registry_updated` only
- **Forbidden default:** full `find_critical_bugs.py` · `build-sina-command-panel.py`

## Session start (first edit)

```bash
cd ~/Desktop/Noetfield-Systems/SourceA/scripts
bash worker_turn_entry_v1.sh          # gate + anti-staleness auto-heal
python3 brain_validate_goal1_v1.py --json
# Full find_critical_bugs = Hub Safety only — never default on loop
```

## Forbidden (instant FAIL)

- UNATTENDED BATCH · pick 30 · multi-sa closeout
- Implement on CHECK · closeout on ACT
- Trust chat over disk · skip `worker-submit`
- OpenRouter / live eval on ACT when gate closed
- Maintainer hub patches · Brain ASF voice

## Research → skill (structural lessons)

Before promoting a new workflow to law: use shared skill `@sina-research-intake` → Agent Hub pipeline.

## Related skills

| Skill | When |
|-------|------|
| `@sina-research-intake` | Research should be evaluated before build |
| `@sina-registry-drain` | Receipt / quarantine / honest gate focus |
| `@sina-sourcea-brain` | Not you — Brain judges; you execute |

*End sina-sourcea-worker*
