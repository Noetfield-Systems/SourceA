# Pre-Sleep Transition Mode (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Authority:** ASF  
**Parent:** `FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md` · `THREE_LANE_ENGINE_MODEL_LOCKED_v1.md` · `COST_SMART_ENGINE_SSOT_LOCKED_v1.md`

---

## One sentence

**Pre-sleep = governance handoff rehearsal: ASF still commands, all four engines prove alive; sleep = Claude team owns the map.**

---

## Governance boundary

```
┌─────────────────────────────────────────────────────────────┐
│  ASF IN CHARGE (founder_busy)                               │
│       ↓                                                     │
│  PRE-SLEEP TRANSITION  ← you are here                       │
│       ↓                                                     │
│  CLAUDE TEAM IN CHARGE (founder_absent + sleep escalation)  │
└─────────────────────────────────────────────────────────────┘
```

| Mode | Who commands | Who executes boss queue |
|------|--------------|-------------------------|
| **Awake (ASF)** | Founder + Worker paste | **Worker** |
| **Pre-sleep (transition)** | **ASF monitors** | Worker **may** continue + engines prove |
| **Sleep** | **Claude team** (CLI+API+Pro) | **CLI ACT + API CHECK/verify** |

**Pre-sleep is NOT sleep.** Overnight dispatcher stays **OFF** until `arm sleep`.

---

## Four engines — pre-sleep must prove ALL

| # | Engine | Script | Pre-sleep role | Touches boss queue? |
|---|--------|--------|----------------|---------------------|
| 1 | **Worker SourceA** | Cursor `run inbox` | Boss lane — founder may keep draining | **YES** (only legal writer) |
| 2 | **Claude Code CLI** | `claude_code_agent_v1.py` | **Prep lane** — draft plans in sidecar | **NO** |
| 3 | **Claude API** | `claude_api_agent_v1.py` / `sidecar_scout_api_v1.py` | **Scout lane** — gap reports | **NO** |
| 4 | **OpenRouter** | `eval_packet_v1b/runner.py` live arm | **Probe only** on pre-sleep — live eval tasks only | **NO** on healthy pack |

**Healthy pack 2 (sa-0167–0178):** OpenRouter **forbidden** on boss queue. Pre-sleep proves **wiring + credits probe** — not live eval drain.

---

## Pre-sleep monitor (founder verifies before leaving)

```bash
bash scripts/pre-sleep-monitor-v1.sh
```

**Approve transition → sleep only when:**

1. Worker: 3+ turns advanced without `sa_mismatch`
2. Claude API scout watch: **ALIVE** + files written
3. Claude CLI prep watch: **ALIVE** + files written
4. OpenRouter: probe PASS or honest BLOCKED (credits) — documented
5. Gatekeeper + `brain_read_state` aligned
6. Founder says: **`arm sleep`**

---

## Sleep — Claude team owns the map

| Engine | Sleep job |
|--------|-----------|
| **CLI Sonnet** | Boss ACT on queue |
| **API Haiku** | Boss CHECK + verify |
| **Claude Pro** | Advisor / critic (no queue write) |
| **Worker** | **OFF** (founder away) |
| **OpenRouter** | Only when task + ACTIVE_NOW allow live eval |

Mechanism: `arm-sleep-mode-v1.sh` → `start-overnight-3engine-v1.sh` → caretaker **post_dispatch** per turn

**Caretaker law:** `SLEEP_MAC_CARETAKER_LOCKED_v1.md` — event-driven only, no timer poll.

---

## ACTIVE_NOW fields (pre-sleep)

| Field | Value |
|-------|-------|
| `Current Founder Mode` | `founder_busy` |
| `Current Sleep Escalation` | `off` |
| `Current Sprint` | `Pre-sleep transition — monitor 4 engines` |

After `arm sleep`: `founder_absent` + `Sleep Escalation: on`

---

*LOCKED — Pre-sleep = prove the handoff. Sleep = Claude team runs the map.*
