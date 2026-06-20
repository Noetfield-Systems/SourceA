# SourceA Execution Session Lock — 2026-06-08

**Saved:** 2026-06-08T08:20:22Z · **Retrofit:** doc-datetime-law batch retrofit
**Status: LOCKED** · **Author: ASF + Advisor** · **Session: Cowork 2026-06-08**

> This file captures every architectural decision made in the 2026-06-08 session.
> It is authoritative. Drift from this file must be treated as a regression.

---

## CONTEXT: WHY THIS MATTERS

SourceA is not a hobby. It is the infrastructure OS for:
- **FORGE** — primary commercial product
- **AI Dev Bridge / M8** — developer tooling revenue
- **Holding structure** — VIRLUX, Noetfield, TrustField, SinaaiMonoRepo

Every decision in this file was made against ROA (Return on Automation) speed,
cost intelligence, and execution correctness. Do not revert without ASF sign-off.

---

## DECISION 1: THREE-ENGINE FULL STACK (LOCKED)

All three engines are ACTIVE. None is deprecated.

| Engine | File | Job | When |
|--------|------|-----|------|
| **Claude Code CLI** | `scripts/claude_code_agent_v1.py` | Real file execution (Bash/Write/Edit/Read) | `act`, `implement`, `build`, `fix`, `patch` roles |
| **API Agent** | `scripts/claude_api_agent_v1.py` | Auto-run headless, 24/7, no supervision | `check`, `verify`, `audit`, `review` roles + away mode |
| **Cursor** | IDE | UI-heavy, multi-file refactors, stuck tasks | Blocked 2+ times, React/CSS, ASF pair-programming |

**Anti-pattern locked**: Never route `act` tasks to API agent. API agent has NO filesystem tools.

---

## DECISION 2: PHASE DRAIN ORDER (LOCKED — ROA-FIRST)

File: `scripts/sourcea_pick_lib.py` → `PHASE_ORDER` tuple

```python
PHASE_ORDER = (
    "phase-s0-ssot-alignment",       # already done
    "phase-s1-eval-dispatch",        # ACTIVE — finish 41 tasks → unlocks dispatch gate
    "phase-s5-commercial-lanes",     # ROA PRIORITY — FORGE + revenue (pulled from pos 6 → pos 3)
    "phase-s2-hub-build-ci",
    "phase-s3-scoreboard-fleet",
    "phase-s4-spine-loop",
    "phase-s6-wtm-pre-llm",
    "phase-s7-council-governance",   # DEFER — low ROA
    "phase-s8-hub-ui-ux",            # DEFER — low ROA
    "phase-s9-research-models",      # DEFER — low ROA
)
```

**Why**: Old order had s5-commercial at position 6 (282 tasks away from revenue).
New order: s5-commercial at position 3 (41 tasks away — finish s1 only).
**Impact: -242 tasks to first revenue.**

---

## DECISION 3: MODEL ROUTING (LOCKED — COST INTELLIGENCE)

| Role | Model | Cost/turn | Reasoning |
|------|-------|-----------|-----------|
| `check`, `verify`, `audit`, `review`, `test`, `validate`, `read`, `assess` | Haiku 4.5 (`claude-haiku-4-5-20251001`) | ~$0.002–0.006 | Reasoning only, no tools |
| `act`, `implement`, `build`, `fix`, `patch`, `create`, `write`, `exec` | Sonnet 4.6 (`claude-sonnet-4-6`) | ~$0.05–0.25 | Real tool use + complex reasoning |
| Unknown/fallback | Sonnet 4.6 | — | Safe default |

Queue breakdown (current 30-task queue): 20 CHECK (Haiku) + 10 ACT (Sonnet).

---

## DECISION 4: PROMPT ARCHITECTURE (LOCKED)

### API Agent (`claude_api_agent_v1.py`) — key features:

1. **Receipt skip guard** — `_receipt_exists(sa_id)` checked before building prompt. If DONE receipt exists, Claude verifies it rather than re-running.
2. **Forbidden list** — `item["forbidden"]` handled as both `list` and `str`.
3. **Live eval gate** — `live_eval_required=true` + `_openrouter_credits_ok()` check. If credits unavailable → status=BLOCKED, not hallucinated PASS.
4. **No-tool declaration** — system prompt explicitly states: "You have NO filesystem tools."
5. **WORKER_ROUND_REPORT fields**: `sa_id`, `role`, `status`, `summary`, `evidence`, `gaps`, `next_action`

### CLI Agent (`claude_code_agent_v1.py`) — key features:

1. **Receipt skip guard** — `_receipt_exists_cli(sa_id)` — if DONE, verify-only mode, no re-implement.
2. **Forbidden list** — list or string, rendered as hard-stop rules.
3. **Live eval gate** — curl check to Hub :13020 before act. If unavailable → BLOCKED receipt.
4. **4-step execution contract** (enforced in every prompt):
   - STEP 0: Feasibility gate (`prompt_feasibility_gate.py`)
   - STEP 1: Validate (run §Verify from task .md)
   - STEP 2: Act (only if role=act and not already done)
   - STEP 3: Re-verify
   - STEP 4: Write receipt (always last — `receipts/{sa_id}-receipt.json`)
5. **Receipt format** locked: `{"sa_id":"...","status":"DONE","files_written":[],"commands_run":[],"summary":"..."}`

---

## DECISION 5: OPENROUTER INTEGRATION (LOCKED)

- **Key**: `SourceA-Eval-1b` (`sk-or-v1-e4d...d07`)
- **Limit**: $10/month · **Used**: $0.333 · **Remaining**: ~$9.67
- **Flag file**: `~/.sina/openrouter-credits-ok.flag` (touch = credits OK, rm = credits gone)
- **Purpose**: Eval-1b live test calls for `live_eval_required=true` tasks
- **Gate**: `dispatch_ready=true` requires OpenRouter to be working
- **Cost**: ~10–20 API calls per test cycle, cheap models (Llama, Gemini Flash ~$0.001/call = under $0.05/cycle)

**If credits run out**: remove flag file, both agents will report BLOCKED for live_eval tasks automatically.

---

## DECISION 6: AUTORUN DAEMON (LOCKED)

- **Plist**: `~/Library/LaunchAgents/com.sourcea.autorun-worker.plist`
- **Interval**: every 90 seconds, `RunAtLoad=false`
- **Command**: `python3 scripts/claude_code_agent_v1.py` (CLI agent, routes by role)
- **Kill switch**: `touch ~/.sina/auto-run-disabled-v1.flag`
- **Resume**: `rm ~/.sina/auto-run-disabled-v1.flag`
- **Logs**: `~/.sina/autorun-worker.log` and `~/.sina/autorun-worker-err.log`
- **Re-install**: `bash scripts/install-autorun.sh`

---

## FULL COST STACK (LOCKED ESTIMATE)

| Cost type | Service | Per turn | Volume | Est. total |
|-----------|---------|---------|--------|-----------|
| CLI — act/build | Anthropic API (Sonnet) | ~$0.05–0.25 | ~40% tasks | ~$28 |
| API — check/verify | Anthropic API (Haiku) | ~$0.002–0.006 | ~40% tasks | ~$4 |
| API — complex verify | Anthropic API (Sonnet) | ~$0.02–0.05 | ~20% tasks | ~$5 |
| Eval-1b live tests | OpenRouter | ~$0.001/call | ~500 cycles | ~$1–5 |
| Cursor AI | Cursor subscription | flat | exception path | flat |
| **SourceA total** | | | **681 tasks** | **~$33–47** |

---

## EXECUTION REALITY MODEL (LOCKED)

```
ASF (Founder)         → Hub actions only (http://127.0.0.1:13020)
Brain (Cursor)        → routing, narration, orchestration
CLI Agent             → act/build/fix — real file execution + receipts
API Agent             → check/verify — reasoning only, no filesystem
OpenRouter            → Eval-1b live test calls
Validator scripts     → truth layer
Receipts on disk      → only truth that counts
Advisor (Cowork)      → external reasoning, no execution authority
```

**Hard rule**: `receipts/{sa_id}-receipt.json` with `status: DONE` = done. Nothing else counts.

---

## FILES CHANGED THIS SESSION

| File | Change |
|------|--------|
| `scripts/sourcea_pick_lib.py` | Phase order: s5-commercial moved to position 3 (was 6) |
| `scripts/claude_api_agent_v1.py` | `_build_system_prompt` + `_build_user_prompt` rewritten with all 6 prompt features |
| `scripts/claude_code_agent_v1.py` | `_build_worker_prompt` rewritten with all 6 prompt features + `_receipt_exists_cli` |
| `brain-os/EXECUTION_ENGINE_STRATEGY_LOCKED_v1.md` | Three-engine strategy document created |
| `~/.sina/openrouter-credits-ok.flag` | Created — signals OpenRouter credits available |
| `~/Library/LaunchAgents/com.sourcea.autorun-worker.plist` | Installed via install-autorun.sh |

---

## NEXT ACTIONS (priority order)

1. ✅ Phase reorder → done
2. ✅ Prompt intelligence → done
3. ✅ OpenRouter credits OK → $9.67 remaining, flag set
4. **[ ] Telegram bot** — `scripts/telegram_bot_v1.py` — phone control (/status /start /pause /cost)
5. **[ ] Validate end-to-end** — run `python3 scripts/claude_code_agent_v1.py --trace` on one ACT turn, confirm receipt written
6. **[ ] Stuck watchdog** — auto-kill turns >5min stall, auto-resume
7. **[ ] Auto-repair loop** — validator fail → patch → re-run (P4 on roadmap)

---

*Lock date: 2026-06-08 · Session author: ASF*
*Disk state is truth. This file is the session record.*
