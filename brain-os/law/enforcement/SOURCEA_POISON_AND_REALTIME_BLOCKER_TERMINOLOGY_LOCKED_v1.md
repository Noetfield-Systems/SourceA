# SourceA — Poison vs realtime blocker terminology (LOCKED)

**Saved:** 2026-06-23 · **UTC:** 2026-06-23T12:00:00Z  
**Unified vocabulary:** `data/sourcea-vocabulary-unified-index-v1.json` · `SOURCEA_VOCABULARY_UNIFIED_LOCKED_v1.md`  
**SSOT pair:** `data/agent-memory-mirror-poison-law-v1.json` · `.cursor/rules/agent-memory-mirror.mdc`  
**Incidents:** INCIDENT-034 · INCIDENT-039 · INCIDENT-040 · INCIDENT-041 · **INCIDENT-042** · **INCIDENT-043**

---

## One law (read this first)

> **Realtime truth wins over stale disk.** ASF founder orders from today beat yesterday’s JSON URLs. Agents answer from live receipts and Railway/HTTP proof — not from trashed apps or validator marathons.

---

## Two different words (do not merge)

| Term | What it is | Founder symptom | Fix |
|------|------------|-----------------|-----|
| **Poison** | Mirror/law text that **orders** validator marathons, audit-of-audit loops, or “run all validators before reply” on Mac founder session | Agent stuck in bash 11+ min; chat goes silent; INCIDENT-039 P0 | Scrub: `scripts/agent_mirror_poison_scrub_v1.py --all` (ship window only). Session: read receipts once, reply <30s, stop. Law: never chain `validate-*` mid-turn. |
| **Realtime blocker** | A **live** gap between what disk/rules **say** and what **works right now** (dead port, trashed app URL, RED line contradicting Railway) | UI dead, Proceed empty, form at `:13020` after Hub trash, `mandatory_next` points at ghost surface | Fix routing logged + restart the live server/app. Proof = HTTP/Railway receipt, not another validator. |

**Poison is conduct law for agents.**  
**Realtime blocker is product/routing drift after ASF moves surfaces.**

---

## Realtime wins over disk (ASF 2026-06-23)

When these conflict, **trust realtime proof**:

1. **Railway Cloud Forge Run** — `GET …/api/cloud-forge-run/queue/v1` · live queue head + `batch_id`. **Auto Runtime** arms Forge Run every ~10 min · **up to 10 proof-gated rows per turn** (INCIDENT-045). Forbidden founder words: **drain** · **loop**. SSOT: `data/cloud-motor-founder-vocabulary-v1.json`.
2. **Cockpit** — **Cloud Workers.app `:13027`** is the primary Mac glance for Proceed/full-pack. Worker Hub `:13020` was **trashed** (legacy poison surface).
3. **Official form** — Picks stay in `~/.sina/live-founder-decision-form-intake-v1.json`. UI lives at **Chat Unify `:13023/form/`** (same 5-option A–D + E, dual submit bars, POST `/api/live-founder-decision-form-v1`).
4. **Founder orders** — Recent ASF purge/trash receipts (`~/.sina/asf-hub-legacy-trash-receipt-v1.json`, `asf-anti-poison-kill-receipt-v1.json`) override boot.json or registry rows that still cite Worker Hub.

Agents must **not** treat old `eval-live-blocked-sas` or trashed `healthy-queue-blockers` files as current blockers if mirror scrub and Railway say otherwise.

---

## What is NOT a blocker right now

| Stale disk row | Why it is not realtime |
|----------------|------------------------|
| `http://127.0.0.1:13020/form/` | Hub trashed; form re-homed Chat Unify |
| `worker_connected: BLOCK` in old brain-live-context | Hub port dead by design |
| Mac Cursor AUTO-RUN / Goal 1 autorun | **Purged 2026-06-24** — deleted from disk · cloud Auto Runtime only |
| `mandatory_next` → Worker Hub → Next steps | Replaced: Cloud Workers + form on Chat Unify when batch complete |
| INCIDENT-039 validator stuck | Historical poison class — not the same as “open 119 form picks” |

---

## Mandatory next (Brain) — current shape

When **CLOUD-SEC batch complete** and next batch armed:

```
Cloud Forge Run full_pack — Cloud Workers http://127.0.0.1:13027/ ·
Queue head + batch_id from Railway /api/cloud-forge-run/queue/v1 ·
Official form N picks · http://127.0.0.1:13023/form/
```

**Never** describe batch drain as “one CLOUD-SEC per cron tick” (INCIDENT-042).

---

## Agent reply discipline (poison-free)

1. Read `~/.sina/agent_session_gate_receipt_v1.json` + `brain-live-context-v1.json` once.
2. Quote `factory_now_line` from live surfaces or truth bundle.
3. Plain English first; disk path second.
4. **One** light check ≤90s if needed (curl health, read JSON). No validator chain.

---

## Related files

- `data/sourcea-vocabulary-unified-index-v1.json` **← vocabulary spine**
- `brain-os/law/enforcement/SOURCEA_VOCABULARY_UNIFIED_LOCKED_v1.md`
- `brain-os/law/enforcement/AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md`
- `data/mac-validator-stuck-red-flag-v1.json`
- `data/cloud-motor-founder-vocabulary-v1.json`
- `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_AUTO_RUNTIME_VOCABULARY_LOCKED_v1.md`
- `data/cloud-forge-run-queue-active-v1.json`
- `data/cloud-forge-run-full-pack-pattern-v1.json`
- `data/cloud-workers-control-plane-v1.json`
- `scripts/brain_live_context_v1.py` → `~/.sina/brain-live-context-v1.json`
- `scripts/form_official_canvas_route_v1.py` → Chat Unify form URL
