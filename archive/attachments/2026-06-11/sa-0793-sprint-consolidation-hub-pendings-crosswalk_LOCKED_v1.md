# sa-0793 ACT — sprint consolidation locked doc vs hub pendings crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Cross-check `AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md` (preservation manifest) against hub **pendings** surfaced in WTM / strategic synthesis panel.

## Two tracks (by design — not 1:1 IDs)

| Track | SSOT | ID scheme | Audience |
|-------|------|-----------|----------|
| **Sprint manifest** | `AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md` | **D-*** ASF build orders · **R-*** reserved queue | Ecosystem sprint conclusions + path to final v2 |
| **Hub pendings** | `scripts/strategic_synthesis_hub.py` → `pendings()` | **P0–P11** strategic slice | WTM panel · Eval-1b · dispatch · lane revenue |

Both are wired in hub:

- Sprint doc: `hub_essentials_index.py` · `agent_system_unified.py` · `audit_hub_source_alignment.py`
- Hub pendings: `/api/strategic-synthesis-v1` · `validate-strategic-synthesis-v1.sh` (≥8 rows)

**Verdict:** Complementary scopes — cross-check is **manifest internal consistency + live machine**, not forced ID merge.

## Sprint manifest — §3 ASF decisions (live)

| ID | Status |
|----|--------|
| D-DEBUG-01 · D-VOTE-01 · D-UNIFY-01 · D-DRIFT-01 · D-UI-01 · D-TAG-01 | **SHIPPED** |
| D-GPT-01 · D-D2-01 | **OPEN** |

## Sprint manifest — §4 stale vs §3 (CHECK finding)

Items still listed in **§4 reserved queue** while **§3** marks shipped:

| R-ID | Shipped as |
|------|------------|
| R-P0-03 | D-DEBUG-01 |
| R-P1-01 | D-UI-01 (blueprint navigator) |
| R-P1-02 | D-UNIFY-01 (gov unify batch UI) |
| R-P1-03 | D-DRIFT-01 (drift engine) |
| R-P1-07 | D-TAG-01 (doc tag standards) |
| R-P2-01 | D-VOTE-01 (advisory voting) |

**Recommendation (ASF/maintainer):** Reconcile §4 — mark deferred/shipped or addendum dated note; do not delete preservation history without unification engine pass.

## Essay / fleet prose stale

| Sprint prose | Live (`agent_essay_discourse`) |
|--------------|-------------------------------|
| §6: **2/8** essays | **8/8** agents posted |
| R-P1-05: **6/8** owe governance-drift essay | `nudge_count=0` |

## Hub pendings open (live)

From `strategic_synthesis_hub.pendings()`:

| ID | Status | Title (abbrev) |
|----|--------|----------------|
| P2 | partial | L0-full editor telemetry |
| P3 | open | L0/L1 deepen |
| P10 | in_progress | TrustField outreach / pilot |

**Not mirrored** in sprint §3 D-* rows: D-GPT-01, D-D2-01 (different workstreams).

## Alignment verdict

| Check | Result |
|-------|--------|
| Validators / runtime green | **PASS** |
| Sprint doc wired in hub read chain | **PASS** |
| Hub pendings payload ≥8 + P2 partial validator | **PASS** |
| §4 queue vs §3 shipped | **DRIFT** (narrative) |
| §6 / R-P1-05 vs live essays | **DRIFT** (narrative) |
| P-* vs D-/R-* ID union | **N/A** — intentional split |

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS

## Prior proof

- sa-0718 / sa-0743 / sa-0768 — same task title (queue compaction to T3 sa-0793)

## OPEN (informational)

1. **OPEN-1:** Maintainer addendum to sprint manifest §4 + §6 (no Worker code edit without ASF).
2. **OPEN-2:** Optional hub tile linking D-* OPEN decisions to related P-* pendings (UX only).
