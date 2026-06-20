# sa-0788 ACT — Council hero unification policy doc link crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Payload ↔ disk ↔ UI

| Check | Result |
|-------|--------|
| `council_room_payload().policy_doc` | `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md` |
| Law file on disk | PASS |
| `hub_essentials_index.py` entry | PASS — "Agent unification policy" |
| `AGENT_COUNCIL_ROOM_LOCKED_v1.md` parent | PASS — same policy doc |
| Council hero button (`app.js` ~7958) | `sc-open-gov-doc` + `room.policy_doc` fallback matches payload |
| Click handler | `.sc-open-gov-doc` → `openDocEditor(path, "rules")` |

## Distinct from system-unified panel

| Surface | Doc linked | Purpose |
|---------|------------|---------|
| Council hero | `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md` | Ecosystem roles, edit lock, Council phases |
| System unified panel | `AGENT_APP_AS_UNIFYING_HUB_LOCKED_v1.md` | App-as-pre-unifying-hub law |

Intentional split — not a gap.

## OPEN (informational)

1. **OPEN-1:** `council_doc` (`AGENT_COUNCIL_ROOM_LOCKED_v1.md`) in payload but no dedicated hero button — policy + mind-share buttons cover task scope.

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS
- `validate-ui-wiring-v1.sh` — PASS (council_room heavy route)

## Prior proof

- sa-0763 / sa-0738 / sa-0713 — same task title at lower tiers (queue compaction)
