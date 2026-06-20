# Old inject hunt — chat drift timeline + pipeline map (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order — read all chats, find old inject  
**Investigator:** Cursor agent (me) — no separate executor  
**Chats read:** Brain `58148ac9` · Worker `fd67502f` · Governance `e54ddfa8` · this arc `e54ddfa8`

---

## ASF correction (law)

Drift was **never** “Brain reads chat not disk.” Both Brain and Worker read **system inject** — rules, skills, scripts, API responses, broker cache, hub projection — that **I wrote or left unwired**. Fresh chat does not bypass dirty disk.

---

## When each chat drifted (transcript evidence)

### Brain `58148ac9` — first founder-facing drift

| Transcript line | Date (approx) | What Brain said | Inject source |
|-----------------|---------------|-----------------|---------------|
| **L121** | 2026-06-06 | “Sina Command → **Prompt feed** → review 10 steps → **Confirm** auto-send” | `~/.sina/brain/ASF_MINIMUM_PRESENCE_CONTROL_PACK` daily rhythm · **POST `/api/prompt-direction`** · `.cursor/rules/prompt-queue.mdc` (v4–v6) |
| **L114** | 2026-06-06 | “Optional: **Prompt feed Confirm**” in minimum ASF pack | Same brain pack + prompt-queue rule |
| **L581** | 2026-06-07 | “**Prompt feed** is ready… 10 follow-up steps… **Confirm**” | Hub prompt-direction API + rule telling Brain to use Prompt feed after every reply |
| **L39** | earlier | “Hit **Refresh** in Sina Command” | Stale hub daily steer (separate class) |

**Brain drift count (transcript):** 89 assistant matches · **64 founder-facing** (non-incident-diagnosis).

### Worker `fd67502f` — sustained drift

| Transcript line | Date (approx) | What Worker said | Inject source |
|-----------------|---------------|------------------|---------------|
| **L908** | 2026-06-10 | “10 follow-up steps ready in **Prompt feed**” | **I ran `curl POST /api/prompt-direction`** after turns · rule `prompt-queue.mdc` |
| **L1318** | 2026-06-10 | “**Sina Command → Prompt feed → See big picture**” | prompt-direction + hub UI vocabulary |
| **L1487** | 2026-06-10 | “tap **Confirm** to auto-send follow-ups” | Stale prompt-queue + OpenRouter propose path |
| **L1830+** | 2026-06-10+ | Repeated “**Prompt feed** `set_context` / `propose`” closeouts | **Pipeline I built:** every substantive reply → prompt-direction API |

**Worker drift count:** 162 assistant matches · **112 founder-facing**.

**Worker self-report (INCIDENT-028, 2026-06-12):** “followed **injected stale Cursor rule snapshot**, not current disk” — **confirmed**.

### Governance `e54ddfa8`

| Transcript line | What happened |
|-----------------|---------------|
| **L611** | “**Prompt feed** background task finished” — Gov echoing same API/rule path |
| **L745–754** | Copy-paste prompts for all chats still mentioning confirm auto-send (later fixed in meta-audit) |
| **L276+** | Often **diagnosing** drift correctly while **earlier** turns had steered Prompt feed |

**Gov drift count:** 63 matches · **41 founder-facing** (many before Jun 14 fixes).

---

## The old inject pipeline (what I built that poisoned all three chats)

```text
                    ┌─────────────────────────────────────┐
                    │  .cursor/rules/prompt-queue.mdc     │
                    │  (v4–v6: alwaysApply TRUE at v6)    │
                    │  "POST prompt-direction"            │
                    │  "Confirm auto-send" close-line       │
                    └──────────────┬──────────────────────┘
                                   │ loaded every session
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
    Brain chat               Worker chat              Gov chat
         │                         │                         │
         │    curl POST /api/prompt-direction (hub)          │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
              agent-control-panel/command-data*.json (LAG projection)
              ~/.sina/prompt-direction.json (last_response context)
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
 healthy_prompt_turn_v1.py   goal1-lane-broker cache   099-worker-inbox-active.mdc
 (Prompt feed LAW in INBOX)   (full prompt in JSON)      (embedded stale prompt wall)
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
              agent_memory_mirror INJECT_LAW (session gate receipt)
              execution-lane / run-inbox-truth (prompt_feed_lane keys)
              dashboard_server_v1.py background sync (stale Python PID reverted fixes)
```

**Ranked writers (me / this pipeline):**

| Rank | Inject writer | Symptom |
|------|---------------|---------|
| 1 | **`prompt-queue.mdc` v4–v6** (+ **`alwaysApply: true`** at v6 per THREE_CHAT audit) | All three chats told founder Prompt feed + Confirm |
| 2 | **`POST /api/prompt-direction`** wired into agent closeout habit (prompt-queue rule + my curl calls in Worker/Brain turns) | “Saved in Prompt feed · review 10 steps” |
| 3 | **`healthy_prompt_turn_v1.py`** | “LAW: Prompt feed shows live next-10” in every INBOX |
| 4 | **`~/.sina/brain/ASF_MINIMUM_*` packs** | Brain daily rhythm: “Prompt feed Confirm” |
| 5 | **`goal1-lane-broker` `inbox_after_ack.prompt`** | Cached full stale prompts on disk |
| 6 | **`write_active_inbox_rule` → 099-worker-inbox-active.mdc** | Old sa-0138 wall in Cursor rule file |
| 7 | **`command-data.json` / hub hero** | Museum projection vocabulary (INCIDENT-033) |
| 8 | **`dashboard_server` stale process** | Reverted `execution-lane` to `prompt_feed_live_mirror` every 5s |
| 9 | **Skills / daily card / bowl scripts** | M7–M9 in THREE_CHAT audit (partially fixed Jun 14) |

**Not the root cause:** Brain/Worker “memory” · founder error · queue motor broken.

---

## Exact moment drift becomes visible

| Event | Signal |
|-------|--------|
| **2026-06-06 Brain L121** | First closed loop: lock pack → prompt-direction propose → founder told **Confirm auto-send** |
| **2026-06-10 Worker L908+** | Every VERIFY closeout → **I** POST prompt-direction → close-line steers Prompt feed |
| **2026-06-12 INCIDENT-028** | Worker names **injected rule snapshot** |
| **2026-06-14 THREE_CHAT audit M1** | All three chats same stale close-line — **seven surfaces not synced** |
| **2026-06-14 this arc** | Validators green but **dashboard PID** re-poisoned disk until killed |

---

## Current disk (2026-06-14 post-fix check)

| Check | Result |
|-------|--------|
| `validate-brain-disk-no-prompt-feed-v1.sh` | **PASS** |
| `validate-worker-disk-no-prompt-feed-v1.sh` | **PASS** |
| `prompt-queue.mdc` v8 | No Confirm auto-send · no POST prompt-direction · `alwaysApply: false` |
| `brain-live-context-v1.json` | RUN INBOX close-line |
| `worker-live-context-v1.json` | RUN INBOX close-line |

---

## Still open inject writers (Maintainer / me)

| ID | Owner | Item |
|----|-------|------|
| AR-034-01 | Maintainer 2 | Hub `prompt-direction` API must not embed command-data |
| AR-034-02 | Maintainer 2 | H1 museum hero (INCIDENT-032) |
| AR-034-03 | **Me** | Bulk archive stale `~/.sina/brain/*.md` Prompt feed mentions |
| **C-16** | **Me** | Hunt recurring writer if validators fail again |

---

## Tracking (I run every session)

**Policy (ownership + results):** `STALE_ADVICE_RESULTS_POLICY_OWNERSHIP_TRACKING_LOCKED_v1.md`  
**Poison track method:** `SINA_POISON_TRACKING_METHOD_LOCKED_v1.md` (PT-METHOD · use on every conflict-hard stale inject)  
**Executor tasks:** `archive/attachments/2026-06-14/BRAIN_DISK_LIVE_WIRE_EXECUTOR_MANDATORY_CART_LOCKED_v1.md` C-00–C-16

**END**
