# sa-0959 — Fleet 8-agent scoreboard at scale · auto-check taxonomy

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules**

## Factory today (disk truth)

| Field | Value |
|-------|--------|
| **Registered agents** | **8** (trustfield · virlux · ai_dev_bridge_os · noetfield_local · noetfield_cloud · seven77 · semej · sinaai_maintainer) |
| **Fleet green** | `auto_pass_count: 8` · `fleet_verify_gap: []` · `fleet_report_gap: []` |
| **Law** | `AGENT_SCOREBOARD_LOCKED_v1.md` · API `/api/agent-scoreboard` |
| **Storage** | `~/.sina/agent-scoreboard/reports.jsonl` · `verified.json` |
| **FR-009 target** | `auto_pass >= 6` (PRIORITY row) — **exceeded at 8/8** |

## Auto-check taxonomy (current — 5 requirements)

| ID | Check | Auto? | Machine signal | Scale note |
|----|-------|-------|----------------|------------|
| `session_report` | Report ≥40 chars filed | **Yes** | `reports.jsonl` row | O(1) per agent |
| `council_brief` | Council brief attested | **No** | Self-attest in submit | Weakest at scale — human attest |
| `vault_deposit` | Document in 72h window | **Yes** | Vault path probe | Disk-bound per lane |
| `vault_activity` | Activity row in window | **Yes** | Activity log probe | Same |
| `workspace_ready` | Integration checks pass | **Yes** | Workspace probe | Per-repo config |

**`auto_pass`** = all auto checks green (+ attest when `include_attest`) · `verified_by: auto` when machine closes (sa-0301).

## At-scale taxonomy (research — not built)

| Tier | Agent class | Proposed extra checks | Defer until |
|------|-------------|----------------------|-------------|
| **T0** | Portfolio (trustfield, virlux) | Receipt + PRIORITY row | ASF orders lane receipt bind |
| **T1** | Wire / bridge (ai_dev_bridge) | Spine validator smoke | Phase C resume |
| **T2** | Cloud field (noetfield_*) | Railway/Supabase health pill | Commercial lane P0 |
| **T3** | Chrome orchestration (semej) | SEMEJ session receipt | SEMEJ tab only |
| **T4** | Maintainer (sinaai_maintainer) | Governance drift + critic label rate | INCIDENT-005 follow-up |

**Scale rule (proposed):** New agent → register in scoreboard law §5 + one **lane-specific** optional check — never expand global auto_pass without validator.

## Compare: 8-agent MVP vs “at scale”

| Dimension | Today (8) | At scale (9+) |
|-----------|-----------|---------------|
| Fleet target | `>=6` auto_pass | Tiered: core 6 green + optional lane checks |
| Council brief | Self-attest | Machine: council_read path or brief hash |
| Verify column | Auto green pill | Same — ASF force only on exception |
| Nudges | `nudges<=2` target | Essay-nudge taxonomy per agent role |
| Hub UI | 8 rows fit panel | Pagination / lane filter — **hub deferred** (INCIDENT-031) |

## Verdict

**8-agent auto-check taxonomy is shipped and green.** “At scale” means **tiered optional checks per lane** — not more global pills. Research debt only until ASF orders agent #9 + law amend.

**One-line:** Scoreboard works for **8**; scale = **taxonomy tiers**, not duplicate scoreboards.
