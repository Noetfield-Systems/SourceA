# BRAIN FULL SYSTEM MAP — architecture, automation, hub (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-06  
**Audience:** Brain read-only — route workers, remind ASF  
**Companion:** `BRAIN_FOUNDER_INTENT_REGISTRY_LOCKED_v1.md` · `docs/ARCHITECTURE.md`

---

## 1. Four planes (whole picture)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GOVERNANCE — Council, fleet, Track, Scoreboard, critic   │
│ 2. HUB CONTROL — Sina Command :13020, Refresh, WTM panels   │
│ 3. PRE-LLM + RUNTIME — D1–D16, ENFORCE, C1–C7, dispatch     │
│ 4. PORTFOLIO LANES — TrustField, Wire, Factory, MergePack   │
└─────────────────────────────────────────────────────────────┘
```

**Bottleneck (intentional):**

```
Context → Plan → Runtime → STOP (dispatch_ready: false)
```

Behavioral proof (Eval-1b live) before execution closure — not new D-modules.

---

## 2. Ownership matrix

| Who | Does | Does NOT |
|-----|------|----------|
| **ASF (founder)** | Hub Refresh, Track, Actions, demos, credits, commercial | Daily micro-task design |
| **Brain** | Pick, route, conflict analysis, remind | Code sa-XXXX, 10+ file edits |
| **Worker** | One sa-XXXX, verify, closeout | Pick own scope, flip dispatch_ready |
| **Product lanes** | TrustField, wire, mono design | SourceA law edits |

---

## 3. Three automation loops (never confuse)

### Loop A — PLAN WITH NO ASF (SourceA maintainer queue)

**Purpose:** Always something to build — machine verify without founder authority.

| Item | Value |
|------|-------|
| Pack | `sourcea-1000-locked` — 1000 prompts |
| Progress | ~95 done / 916 backlog (refresh REGISTRY) |
| Trigger | `PLAN WITH NO ASF` |
| Pick | `bash scripts/plan-no-asf-run.sh pick 1` |
| Implement | **New worker chat** + `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` |
| Verify | `plan-no-asf-run.sh verify-hub` |
| Closeout | REGISTRY done + SOURCEA-PRIORITY evidence row |

```bash
cd ~/Desktop/SourceA
bash scripts/plan-no-asf-run.sh full 1
# → worker implements printed sa-XXXX → verify-hub → closeout
```

**10-loop interpretation:** Run **10 worker sessions** back-to-back (sa-0114 … sa-0123) — each session = one pick. Hub does not auto-chain these yet.

---

### Loop B — SinaPromptOS (multi-repo morning factory)

**Purpose:** Think once weekly → execute five days across TrustField, mono, VIRLUX, etc.

| Item | Value |
|------|-------|
| Root | `~/Desktop/SinaPromptOS/` |
| Mode default | `semi-auto` · `auto_sync_plan: false` |
| Entry | `./scripts/dispatch-day.sh` or `python main.py` |
| Daemon | `python main.py --daemon` (optional 24/7) |
| Output | `outputs/ready_to_paste/ready_to_paste_<repo>.txt` |
| Founder step | Paste **one** file per silver Cursor repo chat |

```bash
cd ~/Desktop/SinaPromptOS && ./scripts/dispatch-day.sh
```

**Docs:** `SINAAI_10X_AUTOMATION_ARCHITECTURE_LOCKED_v1.md` · `SINAAI_PROMPT_OS_CORE_FINAL_DECISION_LOCKED_v1.md`

---

### Loop C — Hub 10-round agent loop

**Purpose:** Hub planner writes 10 Cursor tasks from goal + prior answers.

| Item | Value |
|------|-------|
| Code | `scripts/agent_loop.py` |
| API | `POST /api/agent-loop` |
| UI | Hub → Agent hub (private maintainer page) |
| Max rounds | 10 |
| Planner | OpenRouter (vault key required) |
| Executor | **Cursor agent** (not planner) |

**Flow:**

```
Start loop → planner prompt R1 → INBOX (+ optional paste) → Cursor executes
→ Submit round → planner prompt R2 → … → R10 → idle
```

**Auto-paste:** **OFF by default** (`SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`). Loop works via app INBOX + manual paste or re-enable per `founder/ASF_CURSOR_AND_M8.md` checklist.

---

## 4. Automation levels — when can ASF "walk away"?

| Level | Requirements | Available |
|-------|--------------|-----------|
| **L1 Semi-auto** | Hub up, worker chats, pick script, optional 10-loop Submit | **NOW** |
| **L2 Post-credits** | Eval-1b live pass, dispatch Phase 2b eligible | After OpenRouter top-up |
| **L3 Zero-human** | Cursor SDK (M8b), auto submit-round, event bus, Phase 3 dispatch, controlled paste | **Not shipped** |

### L1 playbook (closest to ASF vision today)

```text
Morning:
  1. serve-sina-command.sh (if hub down)
  2. Hub Refresh (gold button)
  3. SinaPromptOS dispatch-day.sh OR plan-no-asf-run.sh pick 1

Work block:
  4. Open worker chat → implement ONE sa-XXXX → verify PASS → closeout
  5. Repeat up to 10× for "10 loop" (10 tasks, not hub rounds)

Optional parallel:
  6. Agent hub → Start 10-round loop → Submit round after each Cursor answer

Evening:
  7. Hub Refresh
  8. Track — close/shipped commercial items
```

### L3 blockers (brain reminds — route worker tasks, don't promise dates)

| # | Blocker |
|---|---------|
| 1 | OpenRouter 402 → eval_1b_gate_ok=false |
| 2 | dispatch_ready=false founder law |
| 3 | Auto-paste incident lock |
| 4 | No Cursor SDK auto-response wired to submit-round |
| 5 | auto_sync_plan=false in Prompt OS |
| 6 | Hub missing sa-1000 queue tab |
| 7 | Full 10k prompts — only SourceA 1000 + partial sibling packs |

---

## 5. Machine gates (brain verifies live)

| Gate | Expected | Unlocks when true |
|------|----------|-------------------|
| `eval_1b_gate_ok` | false (402) | Live Eval-1b ≥80% pilots |
| `dispatch_ready` (hub) | false always | Phase 3 council — not now |
| `dispatch_decision` (shadow) | dry_run true | Simulation only |
| Strict build | PASS | Hub :13020 up |
| find_critical_bugs | 0 critical | Hub up |
| Eval scaffold | 7/7 | structural mode honest |

**API:** `GET http://127.0.0.1:13020/api/dispatch-policy-v1`

---

## 6. Hub UI map — three lists

| List | Tab | Count (approx) |
|------|-----|----------------|
| Strategic pendings P0–P11 | World Target Model → Pendings | 7 non-done |
| Track commitments | Track | 12 open |
| Audit backlog | Backlog | 8 open |
| **sa-XXXX queue** | **None — CLI only** | 916 backlog |

### Hub tabs (brain navigation)

| Tab | ID | Use |
|-----|-----|-----|
| Home | command | P0 hero, bowl blockers |
| Track | track | Founder/lane commitments |
| Backlog | backlog | Audit AUD-R/Q/U — not sa-pack |
| World Target Model | system-roadmap | Pendings, missing, dispatch, eval |
| Agent hub | agent-loop | 10-round loop |
| Actions | actions | Founder enqueue (spine, etc.) |
| Council | council-room | Strategic slice |
| Scoreboard | agent-scoreboard | Fleet attests |

**Refresh:** Gold button → `POST /refresh` → rebuilds `command-data.json`

---

## 7. PLLM / runtime stack

```
scripts/pre_llm/          # D-modules: intent, graph, packet, ranking, …
scripts/runtime/          # C1–C7 + orchestrator + dispatch_policy
~/.sina/*.json            # Machine SSOT reports
llm_context_packet_v1.json  # Last step before LLM
```

**Orchestrator:** `runtime/orchestrator/orchestrator_engine.py` — shadow dispatch only.

---

## 8. Prompt pack grid (sourcea-1000)

| Phase | Theme |
|-------|-------|
| s0 | SSOT alignment |
| s1 | Eval-1b + dispatch + grounding |
| s2 | Hub build CI |
| s3 | Scoreboard + fleet |
| s4 | Spine loop |
| s5 | Commercial lanes |
| s6 | WTM / pre-llm |
| s7 | Council governance |
| s8 | Hub UI/UX |
| s9 | Research / models |

Tiers: T0 (no founder verify) → T3 (research)

---

## 9. Ports (brain reminds conflicts)

| Service | Port |
|---------|------|
| Sina Command hub | **13020** |
| SinaaiRuntime | 8000 |
| Prompt OS Streamlit | 8765 |
| Prompt OS API | 8766 |
| DevBridge desk | 3004+ |

**Law:** `PORT_NOTICE_BOARD.md`

---

## 10. Worker routing template (brain copies for ASF)

```text
Open NEW SourceA chat. Send:

MANDATORY READ: /Users/sinakazemnezhad/Desktop/SourceA/os/chat-handoffs/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md

Implement <sa-XXXX from pick script> only. sa-0110–0113 done — do not redo.
```

---

## 11. What was built (who built it)

| System | Builder | Path |
|--------|---------|------|
| Sina Command | Worker sa-XXXX chain | `agent-control-panel/` |
| 1000-pack | `generate-sourcea-1000-prompts.py` + workers | `os/plan-library/sourcea-1000/` |
| Agent 10-loop | SourceA scripts | `agent_loop.py` |
| Prompt OS 10x | Locked 2026-06-02 | `SinaPromptOS/` |
| Dispatch policy | sa-0104–sa-0113 | `runtime/dispatch_policy/` |
| PLLM modules | WTM Phase D workers | `scripts/pre_llm/` |

---

*End BRAIN FULL SYSTEM MAP v1*
