# sa-0791 ACT — GPT governance drift essay requirement vs nudge_count crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Compare external/GPT-WTM governance drift **essay discourse** requirement to machine SSOT `nudge_count` from `agent_essay_discourse.py`.

## Requirement sources (authority order)

| Layer | Source | Requirement |
|-------|--------|-------------|
| Law | `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` | ASF subject `governance-drift-detection` → **8 agents** post essay (≥120 chars) via hub |
| Machine SSOT | `agent_essay_discourse.py` | `nudge_count = len(essay_nudges)` where nudges = one row per **missing agent** per active topic |
| Fleet validator | `validate-governance-fleet-v1.sh` | `nudge_count == len(essay_nudges)`; scoreboard `fleet_verify_gap` / `fleet_report_gap` aligned |
| KPI | `SOURCEA-PRIORITY.md` | essay nudges **≤ 2** (governance-fleet SSOT) |
| FR sync | `founder_request_tracker.py` | FR-008 **shipped** when `nudge_count ≤ 2` |
| GPT/WTM narrative | `brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` §6 | "Essay nudges + fleet verify" listed **in_progress** |
| Strategic hub | `strategic_synthesis_hub.py` | Lanes: scoreboard report + **governance-drift essay** (auto-green) |

## Live disk proof (ACT)

| Metric | Value |
|--------|-------|
| `nudge_count` | **0** |
| `essay_nudges` | `[]` (empty) |
| Topic `governance-drift-detection` agents posted | **8/8** |
| `missing_agents` | `[]` |
| Essays on disk | **9** (one lane double-post; does not affect nudges) |
| Scoreboard `auto_pass_count` | **8/8** |
| `fleet_verify_gap` | `[]` |
| PRIORITY KPI (≤2) | **PASS** |

## Alignment verdict

| Check | Result |
|-------|--------|
| Law essay requirement vs `nudge_count` | **ALIGNED** — all agents posted → nudges cleared |
| `nudge_count` vs fleet validator | **ALIGNED** — PASS |
| `nudge_count` vs FR-008 live sync | **ALIGNED** — shipped at 0 |
| UI `renderEssayNudgeBanner` (`app.js`) | **ALIGNED** — banner hidden when list empty |
| GPT/WTM §6 pendings table | **DRIFT** — still `in_progress` while machine green |

## How nudge_count works (for founder)

```
essay_nudges = [ {agent_id, label, subject, title, message} ... ]
  for each active topic with missing_agents
nudge_count = len(essay_nudges)
```

When any of 8 agents lacks an essay for an active assignment, `nudge_count` rises (max 8 per subject). Council/Today tabs show warn banner via `essayNudgeBanner`.

## Distinct from governance_drift_engine

| Surface | Measures |
|---------|----------|
| Essay discourse / `nudge_count` | Behavioral fleet participation — who still owes governance-drift **essay** |
| `governance_drift_engine.py` | Doc/law drift sensors (score, items) — separate validator chain |

Not the same metric — task scope is essay nudges only.

## OPEN (informational — ASF/maintainer, not Worker code)

1. **OPEN-1:** WTM synthesis §6 row should move to **done** when `nudge_count=0` and fleet 8/8 (narrative lag only).
2. **OPEN-2:** `founder_request_tracker.py` FR-008 static `detail` still says "6/8 remaining" — live `_mark` uses `nudge_count`; seed prose stale.
3. **OPEN-3:** 9 essays / 8 agents — optional dedupe or "mark best" hygiene (not blocking nudges).

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0

## Prior proof

- sa-0311 / sa-0336 / sa-0361 / sa-0386 — FR-008 vs `nudge_count` (queue compaction)
- sa-0316 / sa-0317 — council `essay_nudges` payload + banner
