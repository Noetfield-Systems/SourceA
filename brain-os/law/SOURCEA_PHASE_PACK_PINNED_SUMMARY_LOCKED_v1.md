# Phase pack reorg — pinned very short summary (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
status: LOCKED
doc_date: 2026-06-10
sequence_id: SA-2026-06-10-PHASE-PACK-PIN
-->

| | |
|--|--|
| **Version** | `SOURCEA-PHASE-PACK-PIN-1.0-LOCKED` |
| **Purpose** | Pin the achievable phase-pack order for ASF + monitor |
| **Baseline** | 2026-06-10 · **596/1000 honest** · **FREEZE_DRAIN** ON |
| **Full draft** | `archive/attachments/2026-06-10/PHASE_PACK_REORG_DRAFT_s2-s9_ACHIEVABLE_v1.md` |
| **Incident** | `brain-os/incidents/SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_LOCKED_v1.md` |
| **Machine pin** | `~/.sina/PHASE_PACK_REORG_PINNED_v1.json` |

**Law:** s2 and s3 are **100% done — do not touch**. Headless drain resumes only after ASF: `Cloud Forge Run PHASE_STRICT`.

---

## Very short summary (pin this)

| Phase | Status | Your packs |
|-------|--------|------------|
| **s2** | 100% done | None — skip |
| **s3** | 100% done | None — skip |
| **s6** | 93 done, 7 blocked | 1 founder pack (no headless) |
| **s7** | 27 done, 23 achievable + 50 blocked | 3 headless packs (0778→0800) + founder batch |
| **s8** | 0 done, 50 achievable + 50 blocked | 5 headless packs (0851→0900) + founder T0 |
| **s9** | 0 done, 46 achievable + 54 blocked | 5 headless packs (0951→1000 gaps) + founder research |

**Headless order:** s7-P1→P3 → s8-P1→P5 → s9-P1→P5 (~119 SAs, ~12 packs)

**Max honest after headless:** ~596 + 119 ≈ **715/1000** (founder lanes excluded)

**Resume point:** **s7-P1** at **sa-0778** (frozen cursor) — only after ASF approves manifest + `Cloud Forge Run PHASE_STRICT`

---

## s1 clarification (do not confuse with s2)

| Phase | Honest | Backlog | Note |
|-------|-------:|--------:|------|
| s1 eval-dispatch | 79 | **21** | Founder lane — live eval; not headless |
| s2 hub-build-ci | **100** | **0** | **DONE** |
| s3 scoreboard-fleet | **100** | **0** | **DONE** |

---

## Repair mode (INCIDENT-017)

System **laziness** (forward-only achievable pick, no phase re-heal) caused phase-order drift → **FREEZE_DRAIN** + manual pack manifest. Do not autodrain until manifest approved.
