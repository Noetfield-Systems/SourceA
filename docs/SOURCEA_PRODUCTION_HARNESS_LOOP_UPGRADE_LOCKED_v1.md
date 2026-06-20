# SourceA Production Harness Loop Upgrade — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-20T07:15:00Z · **Authority:** ASF architect memo + Chat Unify v2 wiring  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_PRODUCTION_HARNESS_LOOP_UPGRADE_LOCKED_v1.md`  
**Machine SSOT:** `data/chat-unify-founder-work-order-v1.json` · `scripts/chat_founder_loop_v1.py`  
**Receipt:** `~/.sina/chat-unify-founder-loop-v1.json` · `~/.sina/chat-unify-founder-work-order-v1.json`

---

## 0. One sentence

> **Production grade = harness + attribution + eval flywheel + human close loop with signed work-order JSON — not a smarter model alone.**

---

## 1. Evidence convergence (primary sources)

| Source | Claim | URL / disk |
|--------|-------|------------|
| Anthropic | Start simple; add agent complexity only when workflows fail | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) |
| Anthropic | Generator ≠ evaluator — self-grading agents skew positive | [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) |
| Anthropic | Eval scores mix model + infrastructure — document harness budget | [Infrastructure noise in agentic evals](https://www.anthropic.com/engineering/infrastructure-noise) |
| Anthropic | Eval = task + trials + graders + transcript + outcome + harness | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| OpenAI | Flywheel: traces → feedback → eval suite → harness change | [Agent improvement loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop) |
| SourceA | Local Cursor factory path deprecated → Brain signs, cloud executes | `data/local-worker-cloud-factory-deprecation-v1.json` (B0901) |
| SourceA | Bottleneck = Eval-1b behavioral proof + dispatch closure | `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` |
| SourceA | Every reply: C1–C7 comprehension + root cause analyst | `data/cloud-comprehension-pipeline-loop-v1.json` |
| SourceA | Chat Unify 7-step founder loop (human shell) | `scripts/chat_founder_loop_v1.py` |

---

## 2. Honest attribution caveat (verified 2026-06-20)

**Verified quote** from Anthropic infrastructure noise post (Feb 2026):

> the model-capability/infrastructure-behavior boundary is "blurrier than a single  score suggests."

**Fair mapping:** document harness budget or eval numbers mislead you — applies to SourceA eval receipts and Eval-1b reports.

**Extrapolation (not Anthropic's claim):** mapping infrastructure noise onto SourceA's **AGENT_DRAFT vs DISK_STALE vs DISK_WRONG vs MACHINE_STALE** comprehension layer (C6 output analyst). That layer is SourceA law — analogous to attribution, not a citation from Anthropic.

**Core gap (industry + disk agree):** orchestration without **verified execution closure** — task → execute → verify → state commit → loop update.

---

## 3. Target architecture — Production Harness Loop v1

```text
FOUNDER (Mac · Chat Unify :13023)
  paste / approve / form picks
       │
       ▼
┌──────────────────────────────────────────────────┐
│  FOUNDER LOOP (7 steps)                          │
│  PLAIN → THINK → PROOF(+Eval-1b) → ACT           │
│  → ADVISE → CRITIC → CLOSE(work-order JSON)      │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│  BRAIN — reason + sign fbe-work-order-v1         │
│  (replaces INBOX-as-factory — B0901)             │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│  CLOUD WORKER — one bounded action               │
│  POST /api/cloud-worker/dispatch/v1              │
│  + comprehension bay C1–C7 on output             │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│  EVAL HARNESS — Eval-1b + validators + metadata  │
└──────────────────────────────────────────────────┘
       └──► traces → eval tasks (OpenAI flywheel)
```

---

## 4. Founder loop → industry mapping

| Step | Industry analog | SourceA machine | Wired (v1) |
|------|-----------------|-----------------|------------|
| Language | Explain / benefit (C2–C3) | `chat_founder_language_v1` | yes |
| Reasoning | Planner / routing | `chat_founder_reasoning_v1` | yes |
| Proof | Outcome vs transcript | manifest · drift · **Eval-1b receipt** | **yes (this upgrade)** |
| Action | Single bounded task | one-line ACT | yes |
| Advisor | Separate role (not generator) | AI + rules fallback | yes |
| Critic | Evaluator-optimizer | AI + rules fallback | yes |
| Close | External artifacts + handoff | **work-order JSON** → Brain dispatch | **yes (this upgrade)** |

---

## 5. Work-order schema (Close step)

**Schema:** `chat-unify-founder-work-order-v1` · compatible with `fbe-work-order-v1`  
**SSOT:** `data/chat-unify-founder-work-order-v1.json`  
**Receipt:** `~/.sina/chat-unify-founder-work-order-v1.json`

| Field | Meaning |
|-------|---------|
| `id` | `wo-cu-{uuid12}` |
| `status` | `proposed` (Brain signs → `signed`) |
| `bounded_action` | From Action step — one step only |
| `execution_plane` | `cloud_api_worker` (B0901 default) |
| `control_plane` | `mac_hub` |
| `owner_role` | `brain` |
| `proof.eval_1b` | Snapshot from `~/.sina/eval_packet_v1b_report.json` |
| `proof.disk` | manifest · factory_now · drift |
| `dispatch_hint` | `POST /api/cloud-worker/dispatch/v1` |

Close does **not** auto-dispatch — founder or Brain signs before cloud execute.

---

## 6. Proof step — Eval-1b read

Proof reads `~/.sina/eval_packet_v1b_report.json` when present:

- `mode` (scaffold | live)
- `ok` / `live_ok`
- `summary` · `packet_win_pct`
- `execution_closure_line` — plain English: dispatch ready or blocked

Missing report → Proof states **Eval-1b not present locally** (execution truth gap).

---

## 7. Phased upgrade (ordered)

### Phase 0 — Seal attribution (2 weeks)

Every score/reply carries: `plane`, `harness_id`, `eval_task_ids`, `outcome`.

Proof reads Eval-1b + manifest + drift — not agent prose alone.

### Phase 1 — Work-order compiler (critical path)

Brain emits signed `fbe-work-order-v1` per turn. Chat Unify Close emits **proposed** work-order JSON feeding Brain.

Local Cursor Worker: control only (session gate, hub, form, Chat Unify, manifest-gated cleanup).

**Law:** `data/local-worker-cloud-factory-deprecation-v1.json` · B0901.

### Phase 2 — Eval flywheel

Eval-1b live CI (`SINA_EVAL_1B_LIVE=1`) before `dispatch_ready`. Expand tasks from Chat Unify close extracts and comprehension REJECTs.

### Phase 3 — Cleanup as harness state

`infra/cleanup/cleanup-manifest.md` = PROGRESS artifact. Batch APPROVED = checkpoint.

---

## 8. What NOT to build

| Temptation | Why skip |
|------------|----------|
| Multi-agent swarm on Mac | Anthropic: cost > benefit for most tasks |
| New D-modules / hub monolith | Strategic bottleneck is proof + dispatch |
| Local comprehension validator stacks | Mac Law — cloud bay primary |
| Auto-execute Batch 4 without APPROVED | Manifest + Proof gate |

---

## 9. Execution truth tests (market-grade)

| Test | PASS means |
|------|------------|
| Execution proof | Real file/state change + log + task CLOSED |
| Loop closure | submit → execute → verify → close with same state read back |
| SourceA reality | Rule change persists after reload + validator sees it |
| Client simulation | Live endpoint + reproducible run + failure injection — not diagrams alone |

**One metric:** can the system **change real state** and **read it back verified**?

---

## 10. New worker (`nw-XX`) role

| | OLD (`sa-XXXX`) | NEW (`nw-XX`) |
|--|-----------------|---------------|
| Role | One sa per turn | Autoloop + eval regression |
| Production | Control plane only | Eval flywheel on cloud — not factory body on Mac |

---

## 11. Chat Unify wiring (this ship)

| Component | Change |
|-----------|--------|
| `scripts/chat_founder_loop_v1.py` | Proof reads Eval-1b; Close emits work-order JSON + receipt |
| `scripts/chat_unify_merge.py` | Returns `work_order` on `founder_loop` action |
| `~/.sina/chat-unify-founder-work-order-v1.json` | Latest proposed work-order |
| UI | Close step shows JSON; send-back includes work-order block |

**Version bump:** Chat Unify loop `2.1.0` (Proof + Close wiring).

---

## 12. Single upgrade sentence

Wire Chat Unify's 7-step founder loop to Brain-signed cloud work-orders + Eval-1b live outcomes + harness metadata — and stop using local Worker INBOX as the factory execution path.

---

## 13. Next founder moves

1. Taxonomy A or B + Batch 4 APPROVED in manifest.  
2. Run founder loop → inspect Close work-order JSON → Brain sign path.  
3. Eval-1b live on one path (comprehension REJECT → new eval task).

---

**End LOCKED v1**
