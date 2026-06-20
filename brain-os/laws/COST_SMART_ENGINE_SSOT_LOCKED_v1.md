# Cost-Smart Engine SSOT (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-08  
**sequence_id:** SA-2026-06-08-COST-SMART-002  
**Authority:** ASF  
**Parent:** `FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md` · `ACTIVE_NOW_HEARTBEAT_LOCKED_v1.md`  
**Mechanism:** `scripts/operating_mode_enforce_v1.py` · `scripts/active_now_v1.py`

---

## 1. One sentence

**Three lanes: Worker = boss queue in Cursor. API/CLI = side lanes (no collision). Sleep = CLI boss ACT.**
**Law:** `THREE_LANE_ENGINE_MODEL_LOCKED_v1.md`

---

## 2. Cost ladder (MUST pick lowest valid rung)

| Rung | Engine | Cost | When |
|------|--------|------|------|
| L0 | `validators` only | $0 | VERIFY · PASS/FAIL truth |
| L1 | **Worker** paste | Cursor sub | **Default ACT** at desk |
| L2 | **API** Haiku | ~$0.002–0.006 | **CHECK + verify anytime** (awake or sleep) · **never ACT** |
| L3 | **CLI** Sonnet | ~$0.05–0.25 | **ACT only** · sleep escalation **OR** `worker_stuck_2x` |
| L4 | **OpenRouter** live eval | variable | **Only** when task + ACTIVE_NOW allow · not default pack |

**Rule:** Skip a rung only when lower rung **cannot** complete the bound `sa_id` + `queue_role`.

---

## 3. Awake efficiency mode (`founder_busy`, sleep off)

| Role | Engine | Valid? |
|------|--------|--------|
| CHECK | Worker, API, validators | ✅ |
| ACT | **Worker** (default) | ✅ |
| ACT | CLI | ❌ (use Worker) |
| ACT | API | ❌ (no file tools) |
| VERIFY | Worker, validators, API | ✅ |

**API is NOT sleep-only.** Run API Haiku for CHECK/verify while awake — cheap parallel scout.

---

## 4. Sleep escalation (CLI ACT only)

CLI Sonnet ACT **MUST NOT** run unless **one of**:

1. `Current Sleep Escalation: on` **AND** `founder_absent` (overnight headless ACT)  
2. `worker_stuck_2x` on same `sa_id` (escape hatch while awake)

Autorun dispatcher **MUST** still require sleep escalation + `founder_absent`.

**Default:** `Current Sleep Escalation: off`.

---

## 5. Forbidden (always)

| Action | Why |
|--------|-----|
| API on ACT | No file tools |
| CLI ACT while awake without worker_stuck | Cost leak — use Worker |
| Autorun dispatcher on boss queue while `founder_busy` | Burn while at desk |
| OpenRouter on packs that forbid it | Queue law |

---

## 6. ACTIVE_NOW fields (required)

| Field | Values |
|-------|--------|
| `Current Founder Mode` | `founder_busy` \| `founder_absent` |
| `Current Sleep Escalation` | `off` \| `on` |
| `Current Cost Policy` | `cost_smart_default` |

---

## 7. Brain / advisor

- Claude Pro may **draft** scripts — Worker ships.  
- GPT **critics only** — no "CLI ACT while awake" without `worker_stuck_2x`.  
- Overnight loops **MUST** check `sleep_escalation` before `autorun_dispatcher_v1.py`.

---

*LOCKED — Awake: Worker + API. Sleep: CLI ACT when Worker cannot.*
