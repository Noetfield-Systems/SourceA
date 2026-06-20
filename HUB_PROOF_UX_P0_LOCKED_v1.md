# Hub proof UX P0 — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-10  
**Authority:** ASF order — ship governed proof UX on Hub Home (no third-party analog)  
**Implementer:** SinaaiDataBase workspace (Hub UI) · SourceA scripts (export CLI)  
**execution_authority:** false

---

## 0. One sentence

> **Wire disk-backed honest progress, one-sa event chain export, and founder-gated overnight verify on Hub Home — gates stay on disk; UX stays plain English.**

---

## Build order (mandatory)

| # | Build ID | Deliverable |
|---|----------|-------------|
| **1** | `HUB-P0-1` | Honest counter Hub §1 |
| **2** | `HUB-P0-2` | Event chain JSONL export |
| **3** | `HUB-P0-3` | Overnight verify (read-only CHECK) |

**Backlog:** `AR-7073a0ed55` · `AR-7b461bcca6` · `AR-774df3e0a5` (titles updated to Hub proof UX — no vendor analog)

---

## HUB-P0-1 — Honest counter

- Source: `program-1000-honest-status-v1.py`
- Payload: `home_founder_view.proof_counter` — `verified_done`, `total`, `pct`, `unproven_done`, kill RED/GREEN
- Labels: **verified_done** only — never raw REGISTRY `done` alone

## HUB-P0-2 — Event chain JSONL export

- CLI: `scripts/event_chain_export_v1.py`
- API: `GET /api/event-chain-export-v1?sa_id=…&customer=1`
- One `sa_id` · `EVENT_CONTRACT.yaml` field names · `WORKER_STARTED` required for demo-grade export

## HUB-P0-3 — Overnight verify

- `action_id`: `founder-overnight-verify-readonly`
- Haiku CHECK/VERIFY read-only · max 5 turns
- Kill RED copy: **semi-auto · founder-gated**

---

## Goals

| Goal ID | Name |
|---------|------|
| `GOAL-HUB-P0-1` | Honest counter Hub §1 |
| `GOAL-HUB-P0-2` | Event chain JSONL export |
| `GOAL-HUB-P0-3` | Overnight verify button |

---

*End HUB PROOF UX P0 LOCK v1*
