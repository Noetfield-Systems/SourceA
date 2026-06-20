# SourceA Fleet Headline Read Order (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-FLEET-READ-ORDER  
**Authority:** INCIDENT-027 · Brain · MonoRepo · Maintainer 2  
**Tag:** `MAINT-REF-INCIDENT-027-001`  
**Applies to:** Maintainer 2 (`74f5ccab`) · MonoRepo (`3369d11c`) · Brain route-only · Worker factory lane

---

## 0. One sentence

> **JSON + PROGRAM_PROGRESS + SESSION_LOG define the headline; hub/command-data is LAG — read last, label it, never ship as law.**

---

## 1. Thorn → leaf (every session)

| Order | Source | Role |
|-------|--------|------|
| 1 | `python3 scripts/live_founder_decision_form_v1.py --json` | Form gate · RT LIVE state |
| 2 | `PROGRAM_PROGRESS.json` → `SYS-INTEGRITY-100.founder_open` | Session P0 story |
| 3 | `SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md` Maintainer-next | Maintainer job |
| 4 | Live form §4 top **high** row | RT-LIVE-GATE until PASS |
| 5 | `ACTIVE_NOW.md` | FREEZE only — not queue hero |
| 6 | `command-data.json` / `factory-now` | **PROJECTION (LAG)** — footnote only |

**Generate brief:** `python3 scripts/rt_live_gate_v1.py --scan-brief`

---

## 2. Role precedence (one card)

| Role | Headline from | Never headline as P0 |
|------|---------------|----------------------|
| **Maintainer 2** | Form §4 + SESSION_LOG Maintainer-next | factory queue · Valid YES % · resume |
| **MonoRepo** | mx queue + runtime E2E | RT LIVE proof · drain metrics |
| **Worker** | healthy-queue bind + INBOX meta | RT LIVE proof work |
| **Brain** | `brain-current-action-v1.json` only | factory queue |

**Banned from headline** (unless ASF explicitly asks): `sa-XXXX` · `Valid YES %` · `resume drain` · `queue pos/total` · `Worker INBOX ready`

---

## 3. State transitions (re-derive before first reply)

- Form v2 filled (`asf_filled_at`)
- Maintainer 1 end of service
- ASF FIVE-STEP pick receipt
- Founder: *MOVE ON FROM DRAIN* (or any lane)

---

## 4. Machine mirrors

| File | Purpose |
|------|---------|
| `~/.sina/rt-live-gate-v1.json` | Gate open/pass state |
| `~/.sina/rt-live-gate-receipt-v1.json` | RT LIVE proof receipt |
| `scripts/founder_p0_next_action_v1.py` | Hub hero when gate open |
| `scripts/validate-maintainer-scan-p0-v1.sh` | No drain headline when form filled |

---

*End fleet read order — same card for M2 + Mono.*
