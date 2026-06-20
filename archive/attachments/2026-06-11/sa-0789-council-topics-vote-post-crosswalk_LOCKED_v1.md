# sa-0789 — Advisory votes council topics POST crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 · CHECK probe + VERIFY closeout (ACT skipped by drain)

## POST → disk row

| Action | Handler | Storage | Row proof |
|--------|---------|---------|-----------|
| `create_topic` | `create_topic()` | `~/.sina/council-room/topics.jsonl` | `COUNCIL-*` id, status `open`, default options A/B |
| `vote` | `vote_topic()` | `~/.sina/council-room/votes.jsonl` | `topic_id`, `agent_id`, `option_id` |

## UI ↔ API

- `#council-topic-form` → `POST /api/council-room` `action: create_topic`
- `.sc-council-vote-btn` → `action: vote`
- Success refreshes `json.room` → `D.council_room`

## Law alignment

- `AGENT_COUNCIL_ROOM_LOCKED_v1.md` §2 topic shape + §4 storage paths — PASS
- `voting_live: true` in `council_room_payload()`

## OPEN (informational)

- Law lists POST `note` action — not implemented in `handle_post` (out of scope)

## Validators (VERIFY)

- dispatch + fleet + find_critical_bugs critical 0
