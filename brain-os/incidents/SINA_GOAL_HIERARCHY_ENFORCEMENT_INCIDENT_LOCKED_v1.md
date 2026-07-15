# Goal Hierarchy Enforcement Failure — Brain + Claude Pro (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-08-INCIDENT-004  
**Classification:** MANDATORY READ — **Brain** · **Claude Pro / external advisor** · Worker executor · CLI agents  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_GOAL_HIERARCHY_ENFORCEMENT_INCIDENT_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-07 → 2026-06-08 (founder: “CLI commercial pack vs Pre-LLM — hierarchy was obvious; why did Brain ask me to pick?”)  
**Maintainer:** ASF · Brain documents; founder is law editor  

---

## 1. Executive summary

**Locked law** (`GOAL_HIERARCHY_LOCKED_v1.md`) already defined default routing: **Goal 1 REGISTRY eval-dispatch → WTM/Pre-LLM**. Commercial `sa-050x` (RunReceipt, wire, TrustField UI) is **T2b parallel only** — not default “what is next.”

**Brain (Cursor)** and **Claude Pro (advisor chat)** both **failed to enforce** that law. Brain asked the founder to **choose between lanes** when the answer was logged. Claude Pro recommended architecture options **without reconciling** to locked hierarchy first. Executor code routed **CLI** to a **commercial queue** (`sa-0501`–`sa-0509`) while scoped loop used **Pre-LLM eval-dispatch** (`sa-0153`–`sa-0166`).

**Severity:** **Critical** — destroys founder trust in progress; creates false “two valid strategies”; splits SSOT; makes automation look broken when law was clear.

**Main problem (this incident):** **Enforcement of Agent and Brain** — law exists; mechanical obedience does not.

---

## 2. What locked law already said (no founder vote required)

| Source | Rule |
|--------|------|
| `GOAL_HIERARCHY_LOCKED_v1.md` | **Disk wins.** T0 factory + T3 WTM/Pre-LLM before T2b commercial. T5 never default routing. |
| `ALL_FILES_MAPPING_CLAUDE_PRO_MAIN_GOALS_LOCKED_v1.md` | Main goals: automation loop, WTM, **Pre-LLM**, FORGE, Dev Bridge. Commercial lanes = **parallel only**. |
| `FOUNDER_ADVISOR_PROFILE_LOCKED_v1.md` §8–§9 | Default: **FORGE + WTM + REGISTRY** — not MSB/commercial-first. |
| `MANDATORY_READ_BY_ROLE_LOCKED_v1.md` §Brain | Item 6: **`GOAL_HIERARCHY_LOCKED_v1.md`** before first reply. |
| Founder intent (2026-06-08) | **sa-500+ commercial pack = next-next-week** — not current CLI default. |

**Correct default queue (machine):** `~/.sina/healthy-queue-30-active.json` — `phase-s1-eval-dispatch` · `sa-0153`–`sa-0166`.

**Wrong queue (drift):** `brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json` — `phase-s5-commercial-lanes` · `sa-0501`–`sa-0509`.

---

## 3. Mutual failure — who did what wrong

### 3.1 Brain (Cursor Execution Core)

| Failure | Evidence |
|---------|----------|
| Asked founder to pick “Lane A vs Lane B” | Chat 2026-06-08 — hierarchy already decided |
| Treated commercial CLI pack as coequal strategy | Architecture reply framed two valid futures |
| Did not cite `GOAL_HIERARCHY` as binding default on first routing question | Should have refused commercial queue immediately |
| Did not flag `sourcea_pick_lib.py` phase order vs law | `phase-s5-commercial-lanes` ranked before `phase-s6-wtm-pre-llm` |
| Session-start gate did not include `GOAL_HIERARCHY` in hash chain | `cursor_entry_gate.py` brain role omitted hierarchy file |

### 3.2 Claude Pro (external advisor)

| Failure | Evidence |
|---------|----------|
| Recommended “pick API / n8n / cloud” without hierarchy reconcile | Bypassed locked goal numbering |
| Stated “Cursor paste is root” partially true but omitted **code contradicted GOAL_HIERARCHY** | Symptom diagnosis without law check |
| Did not read `GOAL_HIERARCHY` before reordering build priority | EXTERNAL_CRITIC class — must compare to LOCKED first |
| Implied commercial velocity path without “parallel only” label | Risks founder doubt on Pre-LLM north star |

### 3.3 Executor code (not founder)

| Failure | Evidence |
|---------|----------|
| `sourcea_pick_lib.PHASE_ORDER` promotes commercial before Pre-LLM phase | Comment: “ROA PRIORITY — path to revenue” **inverts** T2b law |
| `claude_code_agent_v1.py` prefers **repo** queue over `~/.sina` | CLI executed `sa-0501` commercial while controlled path was eval-dispatch |
| Two `healthy-queue-30-active.json` files with no single SSOT enforcement | Split ledger · red activate/sync gates |
| `cursor_entry_gate.py` missing hierarchy + this incident class | Mechanical read chain incomplete |

---

## 4. Harm — why founder doubt is rational

1. **Progress looked fake** — Hub/orchestrator said one `sa`; CLI built another.  
2. **Brain looked uninformed** — asked questions law already answered.  
3. **Pre-LLM march looked abandoned** — commercial T0 tasks jumped the queue.  
4. **Enforcement looked optional** — locked docs treated as “suggestions.”  
5. **Advisor vs Brain contradicted** — no single enforced voice.

**Line test violated:** “Would Brain make this routing choice if `GOAL_HIERARCHY_LOCKED_v1.md` were read first?” → **No.**

---

## 5. Mandatory rules (never again)

### 5.1 Brain — before ANY routing, architecture, or “what next” reply

1. Read **`GOAL_HIERARCHY_LOCKED_v1.md`** (or hash-verified via `cursor_entry_gate.py --role brain`).  
2. State active tier: **T0 factory + T3 Pre-LLM path** unless ASF explicitly triggers T5/commercial.  
3. **Forbidden:** Ask founder to pick between main-goal queue and commercial queue when hierarchy applies.  
4. **Forbidden:** Present `sa-050x` commercial as default CLI/automation pack “for this week.”  
5. On drift detection: report **INCIDENT-004 class violation** + point to correct queue — do not questionnaire.

### 5.2 Claude Pro — before ANY build-order or stack advice

1. First line when advising SourceA: **`INPUT CLASS: compare to GOAL_HIERARCHY_LOCKED_v1.md`**  
2. Verdict: main goal vs parallel lane per locked table — **never** promote T2b to T0.  
3. End: **“Worker/Brain implements logged — I hold until ASF orders.”**  
4. **Forbidden:** “Do commercial first for revenue” as default automation routing.

### 5.3 Worker / CLI / autorun — before ANY queue consume

1. **SSOT queue:** `~/.sina/healthy-queue-30-active.json` unless ASF writes otherwise.  
2. Run `python3 scripts/goal_hierarchy_enforce_v1.py --check-queue` (when shipped) — block commercial default.  
3. **Forbidden:** `brain-os/.../healthy-queue-30-active.json` with `phase-s5-commercial-lanes` as live default.

### 5.4 Mechanical gate (session start)

`cursor_entry_gate.py --role brain` **must** hash:

- `brain-os/system/GOAL_HIERARCHY_LOCKED_v1.md`  
- **This incident report**  

Missing hash = **GATE_FAILED** — no Brain reply.

---

## 6. Required remediations

| Priority | Remediation | Owner |
|----------|-------------|-------|
| P0 | Wire incident + hierarchy into `cursor_entry_gate.py` brain chain | Worker |
| P0 | Fix `sourcea_pick_lib.PHASE_ORDER` — commercial after `phase-s6-wtm-pre-llm` | Worker |
| P0 | `claude_code_agent_v1.py` — read `~/.sina` queue first | Worker |
| P1 | Quarantine repo commercial 27-pack until ASF week-3+ order | Brain ack |
| P1 | `goal_hierarchy_enforce_v1.py` validator in CI / session-start | Worker |
| P1 | Reconcile pointer / orchestrator / inbox to single `sa` | Worker |

---

## 7. Correct answer template (Brain — copy shape)

```yaml
status: BRAIN_HIERARCHY_ENFORCED
active_tier: T0_factory + T3_pre_llm
default_queue: ~/.sina/healthy-queue-30-active.json
phase: phase-s1-eval-dispatch
sa_range: sa-0153..sa-0166
commercial_sa_050x: PARALLEL_DEFERRED
founder_pick_required: false
law: GOAL_HIERARCHY_LOCKED_v1.md
incident: SA-2026-06-08-INCIDENT-004
```

---

## 8. Status

| Item | Status |
|------|--------|
| Incident documented | **LOCKED** |
| Mandatory read wired | **ACTIVE** (entry gate + MANDATORY_READ + Claude Pro guide) |
| Code remediations | **SHIPPED** (2026-06-08 — pick order, SSOT lib, CLI/autorun, quarantine) |
| Founder doubt acknowledged | **VALID** — enforcement gap, not ambiguous goals |

---

*End incident report — SA-2026-06-08-INCIDENT-004*
