> **ARCHIVE ONLY — not canonical law.** Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

# DRAFT — Phase pack reorganization (s2 · s3 · s6 · s7 · s8 · s9)

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** DRAFT for ASF review — not active SSOT  
**Baseline disk:** 2026-06-10 · `PROGRAM_1000_STEP_MATRIX.json` · **596/1000 honest**  
**Law:** 10 SAs per pack · 30 turns (check→act→verify) · phase-strict within achievable  
**Freeze:** DRAIN FROZEN until `ASF: resume drain PHASE_STRICT`

---

## Summary by phase

| Phase | Done | Backlog | Achievable backlog | Founder/blocked | Packs needed |
|-------|-----:|--------:|-------------------:|----------------:|-------------:|
| **s2** hub-build-ci | 100 | 0 | 0 | 0 | **0** — complete |
| **s3** scoreboard-fleet | 100 | 0 | 0 | 0 | **0** — complete |
| **s6** wtm-pre-llm | 93 | 7 | 0 | 7 | **0 headless** · 1 founder lane |
| **s7** council-governance | 27 | 73 | **23** | 50 | **3** achievable packs |
| **s8** hub-ui-ux | 0 | 100 | **50** | 50 | **5** achievable packs |
| **s9** research-models | 0 | 100 | **46** | 54 | **5** achievable + 1 founder |

**Headless achievable total:** 23 + 50 + 46 = **119 SAs** → **12 packs** (+ partials)  
**Founder/blocked lanes:** s6(7) + s7(50) + s8(50) + s9(54) = **161 SAs** — not in auto drain

---

## s2 — phase-s2-hub-build-ci

**Action:** None. 100/100 honest.

- Optional: spot audit 3 SAs not in quarantine YAML (matrix shows 97 quarantined flag, still done)
- No new pack

---

## s3 — phase-s3-scoreboard-fleet

**Action:** None. 100/100 honest.

- No new pack

---

## s6 — phase-s6-wtm-pre-llm (7 backlog — all blocked)

**Founder / deferred lane — do not headless autodrain**

| SA | Note |
|----|------|
| sa-0601 | Roadmap Phase D count — may need panel build chain |
| sa-0602–0605 | WTM packet / ENFORCE validators (check verify strings) |
| sa-0670 | OpenRouter deferred doc |
| sa-0695 | OpenRouter deferred doc |

**Pack:** `FOUNDER-s6-WTM-7` — ASF review titles in REGISTRY before run  
**Order:** after s1 eval-live gate · before s7 achievable packs

---

## s7 — phase-s7-council-governance

### Already honest (27) — do not repeat

sa-0701–0777 mix — receipt closed (includes conduct-window sa-0773–0777 — **AUDIT_RECEIPTS_69**)

### Achievable backlog (23) — **PHASE_STRICT packs**

| Pack | SAs (10 each) | Turns | Notes |
|------|---------------|------:|-------|
| **s7-P1** | sa-0778 … sa-0787 | 30 | Resume here — sa-0778 VERIFY open on frozen cursor |
| **s7-P2** | sa-0788 … sa-0797 | 30 | Council + governance validators |
| **s7-P3** | sa-0798 … sa-0800 | 9 | Only 3 SAs — **merge policy:** pair with s8-P1 first 7 OR run as short pack |

### Blocked backlog (50) — `FOUNDER-s7-COUNCIL-50`

sa-0701–0750 — mostly council E2E / essay / OpenRouter-adjacent  
**Rule:** CHECK only until feasibility green · no autodrain ACT

---

## s8 — phase-s8-hub-ui-ux

### Achievable (50) — tiers T1–T3 duplicate patterns

Use **T0 blocked** (sa-0801–0850) as founder lane later; drain **T1–T3 achievable** first (hub UI validate-only).

| Pack | SAs | Turns |
|------|-----|------:|
| **s8-P1** | sa-0851 … sa-0860 | 30 |
| **s8-P2** | sa-0861 … sa-0870 | 30 |
| **s8-P3** | sa-0871 … sa-0880 | 30 |
| **s8-P4** | sa-0881 … sa-0890 | 30 |
| **s8-P5** | sa-0891 … sa-0900 | 30 |

### Blocked (50) — `FOUNDER-s8-HUB-T0-50`

sa-0801–0850 — lazy load, command-data size, refresh pipeline, founder Actions  
**Run:** after achievable s8 packs or parallel founder Actions

---

## s9 — phase-s9-research-models

### Achievable (46)

| Pack | SAs | Turns |
|------|-----|------:|
| **s9-P1** | sa-0951 … sa-0960 | 30 |
| **s9-P2** | sa-0961 … sa-0970 | 30 |
| **s9-P3** | sa-0971 … sa-0980 | 30 |
| **s9-P4** | sa-0981 … sa-0990 | 30 |
| **s9-P5** | sa-0991 … sa-1000 | 30 |

(Gaps sa-0954, 0964, 0979, 0989 are **blocked** — skipped in pack)

### Blocked (54) — `FOUNDER-s9-RESEARCH-54`

sa-0901–0950 + gaps — GPT/Claude/Gemini compare, OpenRouter research, live models  
**Run:** founder + API credits lane only

---

## Recommended execution order (phase-strict)

```
1. [DONE] s2 s3 — skip
2. [FOUNDER] s1 eval-live 21 — parallel track (not in this draft)
3. [FOUNDER] s6-WTM-7
4. [HEADLESS] s7-P1 → P2 → P3
5. [FOUNDER] s7-blocked-50 — batched CHECK reports
6. [HEADLESS] s8-P1 → P5
7. [FOUNDER] s8-T0-50
8. [HEADLESS] s9-P1 → P5
9. [FOUNDER] s9-blocked-54
```

---

## Rules (replace machine pick_floor)

1. **No pack** may start until prior phase **achievable** backlog is zero (founder lanes may lag).
2. **Manifest SSOT** — this file + per-pack JSON under `~/.sina/pack-manifests/` (to be generated on ASF yes).
3. **Builder** loads named pack only — `build-achievable-healthy-queue.py --from-manifest s7-P1`.
4. **Receipt audit** before s7-P1: packs 41–45 + sa-0773–0777 conduct window.
5. **Freeze** stays until ASF: `resume drain PHASE_STRICT s7-P1`.

---

## Honest ceiling (achievable headless only)

| If packs run | +honest (max) |
|--------------|--------------:|
| s7 achievable 23 | +23 |
| s8 achievable 50 | +50 |
| s9 achievable 46 | +46 |
| **Subtotal** | **+119** → ~**715/1000** |

Founder lanes (+161) + s1 (+21) + s4 (+4) + s5 (+99) = path to 1000 **only with founder gates**.

---

*Draft v1 — ASF edit allowed · wire to manifest JSON on approve*
