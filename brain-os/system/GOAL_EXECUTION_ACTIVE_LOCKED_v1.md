# Goal execution active — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-07  
**Authority:** ASF — reach goals via disk + Worker drain, not chat analysis  
**Parent:** `GOAL_HIERARCHY_LOCKED_v1.md` · `REGISTRY_DRAIN_RAIL_LOCKED_v1.md` · `FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md`

---

## 0. One sentence

**Goal 1 = drain `sourcea-1000` REGISTRY phase-first — Brain hands off one `pick 1`, Worker ships one sa, validators are truth.**

External advice (Claude/GPT) is **input only** — wire to disk or ignore.

---

## 1. Goal → execution map

| Goal # | Name | How we reach it (machine) |
|--------|------|---------------------------|
| **1** | Controlled automation factory | `bash scripts/plan-no-asf-run.sh pick 1` → one sa → closeout → repeat |
| **2** | WTM + Pre-LLM | Phases s6+ in pack · after Goal 1 drain in order |
| **3** | FORGE sellable app | Same SourceA Worker · `~/Desktop/forge/` when sa/FORGE task |
| **4** | Research sensor | Research L1/L2 chats — **no sa-XXXX** |
| **5** | Side SKUs (T2b) | Parallel only — RunReceipt/MergePack not north star |
| **6** | Strategic engineering | Spine phases s4+ · `dispatch_ready=false` until Eval-1b live |

**Progress report:** `python3 scripts/goal-progress-v1.py` or `python3 scripts/goal-progress-v1.py --json`

**Full health:** `bash scripts/validate-sourcea-e2e-full-v1.sh`

---

## 2. Daily loop (founder — **no Terminal**)

```text
Worker chat → RUN INBOX (one sa per turn when Brain routes)
Executor runs validators + ACT → broker receipt → STOP
Optional: Worker Hub → Safety / Next steps glance
Legacy archive Actions — maintainer only if ASF enables
```

**Founder never runs shell.** Agents/Worker execute scripts. Founder: **RUN INBOX** in Worker chat only.

| Hub Action | When |
|------------|------|
| **Deliver healthy drain → Worker INBOX** | Writes `.sina-loop/INBOX.md` + editor tab (no Brain hijack) |
| **Open Worker INBOX in editor** | Re-open INBOX tab in background while Brain stays focused |
| **Copy Worker drain (pick 1)** | Simple one-sa drain without 30-queue |
| **Advance healthy queue** | After Worker STOP |
| **Refresh panel** | After closeout |

**Forbidden:** founder Terminal · `pick 30` · batch closeout · chat-memory sa ids

**Mechanical one-sa stop:** `worker_turn_lib.py` — gate opens turn; closeout closes turn.

**Healthy pack:** `healthy-prompt-pack-100.json` + `healthy-queue-30-active.json` · law: `HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md`.

---

## 3. What “use Claude” means here

| Use | Don't use |
|-----|-----------|
| Compare external analog (RAIS, Lovable) | Let Claude invent REGISTRY order |
| Spot missing gate (we wire logged) | Trust Claude live pick counts |
| Draft Worker YAML shape (already locked) | Re-build existing `.mdc` / `prompt_router` |

**Law:** If Claude says X is missing → `test -f` or `bash scripts/validate-*` in the repository first.

---

## 4. Brain paste template (one round)

```yaml
status: BRAIN_HANDOFF
goal_1_progress: <from goal-progress-v1.py>
next_pick: <from brain-session-start.sh only>
worker_paste: Hub Action → Deliver healthy drain → Worker INBOX (not clipboard into Brain)
law: GOAL_EXECUTION_ACTIVE_LOCKED_v1.md
```

---

## 5. Gates (honest — not blockers for drain)

| Gate | Status | Unblock |
|------|--------|---------|
| `eval_1b_gate_ok` | false until live 5/5 | OpenRouter credits (founder) |
| `dispatch_ready` | false | Eval-1b live + founder confirm |
| `find_critical_bugs` | must be 0 at closeout | Fix + one sa per turn |

Drain continues in **structural/scaffold** mode until live eval.

---

*End GOAL_EXECUTION_ACTIVE*
