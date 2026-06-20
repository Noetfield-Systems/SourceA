# Three-Lane Engine Model (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Authority:** ASF  
**Parent:** `COST_SMART_ENGINE_SSOT_LOCKED_v1.md` · `FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md`

---

## One sentence

**Worker owns the boss queue in Cursor. API and CLI run side lanes — never the same turn, never the same window.**

---

## Three lanes (zero collision)

| Lane | Engine | Window | Owns | Touches `next_pos`? |
|------|--------|--------|------|---------------------|
| **A — Boss** | **Worker** | Cursor Worker chat | INBOX · CHECK · ACT · VERIFY · advance | **YES** — sole writer |
| **B — Scout** | **API** Haiku | headless background | Lookahead CHECK reports · registry gaps | **NO** |
| **C — Prep** | **CLI** Sonnet | headless background | Lookahead ACT drafts · backlog stubs | **NO** (awake) · **YES** (sleep ACT) |

**Rule:** Lanes B and C **MUST NOT** call `healthy-drain-orchestrator deliver`, write `INBOX.md`, or advance the boss queue while Lane A is active.

---

## Lane A — Worker (you)

**You only type:** `run inbox`

Worker does the real queue. One turn. STOP. Repeat.

---

## Lane B — API scout (always on while awake)

**Job:** Read **upcoming** CHECK items (lookahead). Write gap reports to:

`~/.sina/sidecar/api-scout/{sa_id}-scout.md`

**Does NOT:** implement · advance queue · touch INBOX · compete with Worker.

**Worker reads scout file on ACT turn** (optional speed-up — already knows gaps).

**Run (executor):** `python3 scripts/sidecar_scout_api_v1.py`

---

## Lane C — CLI prep (awake = draft only)

**Job:** Read **upcoming** ACT items (lookahead). Write patch plans to:

`~/.sina/sidecar/cli-prep/{sa_id}-prep.md`

**Does NOT:** ship to disk on boss queue · advance queue · open Cursor.

**Run (executor):** `python3 scripts/sidecar_prep_cli_v1.py` (writes `~/.sina/sidecar/cli-prep/`)

**Sleep:** Lane C runs boss ACT via dispatcher → `WORKER_ROUND_REPORT` → **orchestrator** advances queue.
CLI **never** writes queue state directly. Law: `QUEUE_STATE_TRANSITION_LOCKED_v1.md`.

---

## Sleep switch

| Mode | Lane A | Lane B | Lane C |
|------|--------|--------|--------|
| Awake (Phase 1) | Worker = boss | **API scout watch ON** (`start-sidecar-engines-watch-v1.sh`) | **CLI prep watch ON** |
| Sleep (Phase 2) | off | API boss CHECK/verify (dispatcher) | CLI boss ACT (dispatcher) |

**Phase 1 OFF:** only `overnight-3engine` boss-queue dispatcher — not sidecars.

---

## Founder clicks

| You want | You do |
|----------|--------|
| Drain queue | Worker: `run inbox` × N |
| Nothing else | Nothing — sidecars run in background (executor starts them) |

**No** “API take CHECK” on boss queue while awake — that was old friction. Scout lane replaces it.

---

*LOCKED — one queue writer, two side lanes, no fighting.*
