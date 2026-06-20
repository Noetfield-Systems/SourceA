# sa-0787 ACT — Paradox detection × mind share `kind: paradox` crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (validators green)

## Law ↔ backend

| Check | Result |
|-------|--------|
| `AGENT_MIND_SHARE_LOCKED_v1.md` §2 kinds (5) | Matches `MIND_KINDS` in `scripts/agent_council_room.py` |
| `share_mind()` rejects unknown kind | PASS — `kind not in MIND_KINDS` |
| `kind: paradox` stored + surfaced | PASS — `_detect_paradoxes` → `agent_flagged` cards |
| §4 auto-detect (topic + stance) | PASS — `lean_yes` + `lean_no` on same `topic_norm` → `divergent_opinions` |
| Open conflicts | PASS — `conflict_case` from `agent_conflict_room._load_cases` |
| Lane boundaries | PASS — `lane_boundary` when both lens agents present |

## Backend ↔ UI

| Check | Result |
|-------|--------|
| `council_room_payload().paradoxes[]` schema | Required keys present: `id`, `kind`, `topic`, `title`, `agents`, `detail`, `severity` |
| `app.js` `renderCouncilRoom` | `sc-paradox-card--{severity}` + badge `p.kind` |
| Mind share form `<option value="paradox">` | PASS |
| Empty paradox board copy | Mentions `opinion` + `kind paradox` |

## Live disk (2026-06-11 ACT)

- `paradox_count`: 4
- Live paradox `kind` values: `conflict_case`, `lane_boundary` (no `agent_flagged` — feed has no `kind: paradox` rows yet)
- Mind feed kinds live: `opinion`, `procedure`

## OPEN (informational — not blocking VERIFY)

1. **OPEN-1:** Empty-state says “opposing opinion tags”; auto-detect actually requires body-derived `stance_hint` `lean_yes` + `lean_no` (`_stance_hint`). Explicit `kind: paradox` always surfaces. Consider one-line UI hint later — not required for T3.

## Prior proof

- sa-0762 VERIFY DONE (same task, T2) · `receipts/sa-0762-receipt.json`
- sa-0779 VERIFY — mind-share UI gaps closed

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS
- `validate-ui-wiring-v1.sh` — PASS (pick=sa-0787)
- `validate-essay-nudges-council-v1.sh` — PASS
- Synthetic `_detect_paradoxes` — `divergent_opinions` + `agent_flagged` when fixtures include lean_yes/lean_no + `kind: paradox`
