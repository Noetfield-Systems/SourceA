# sa-0795 ACT — ASF assigns subject law · founder role not verify role crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Document the **role split**: what ASF/founder owns (assign essay subject, mark best) vs what **machine verify** owns (`auto_pass`, fleet validators, `nudge_count`) — not founder click-as-verify.

## Authority order

| Layer | Source | Role |
|-------|--------|------|
| Essay law | `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` §0–§1 | ASF assigns subject · ASF marks best |
| Scoreboard machine | `agent_scoreboard.py` | `verify_authority: auto_pass` · `verified_by: auto` |
| Scoreboard law | `AGENT_SCOREBOARD_LOCKED_v1.md` §0/§4 | **DRIFT** — still prose “ASF verifies column ✓” |
| Worker law | `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` §IMPLEMENT | No ASF verify — machine validators + `auto_pass` only |
| Hub UI | `app.js` `renderScoreboard` | “machine auto-green (not ASF verify)” |
| 1000-pack law | `SOURCEA_1000_LOCKED_PROMPT_LIBRARY_NO_ASF_v1.md` | Forbidden: ASF as verify/progress authority |

## Founder role vs verify role (canonical matrix)

| Action | Owner | Mechanism | ASF Terminal? |
|--------|-------|-----------|---------------|
| **Assign essay subject** | ASF / founder | Essay discourse law §0; `assignments.json` seed (`governance-drift-detection`) | No — hub/law edit |
| **Mark best essay** | ASF / founder | `POST /api/essay-discourse` `action: mark_best` · hub button | No — hub click |
| **Fleet compliance / green** | Machine | `auto_pass` auto-checks · `verified_by: auto` | No |
| **Essay participation nudges** | Machine | `nudge_count = len(essay_nudges)` per missing agent | No |
| **Progress / REGISTRY done** | Machine | Broker VERIFY + receipt + validators | No |
| **Force override scoreboard** | Maintainer only | `verify_force` when auto checks fail — not default ASF path | Hub maintainer |

**Law sentence (for founder):** ASF picks the **subject** and the **winner**; the factory decides **who complied** via disk validators — never the reverse.

## Essay discourse — ASF assigns subject

`AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` §0:

> When ASF assigns a subject … every registered agent writes an essay … ASF marks the best.

Workflow §1 step 1: “ASF sets subject in hub (default: `governance-drift-detection`)”.

Machine SSOT (`agent_essay_discourse.py`):

- Active assignments from `~/.sina/essay-discourse/assignments.json` (seeded from `DEFAULT_ASSIGNMENTS` if missing)
- Agents post via `submit_essay` — subject must match an active assignment or valid norm
- **No `set_assignment` API** — new subjects require maintainer disk/law edit today (CHECK gap)

## Machine verify — not ASF

`agent_scoreboard.py` header law (machine):

```
Fleet green = auto_pass from machine auto-checks only — not founder click
(verified_by: auto on auto_pass — sa-0301)
```

Live disk (ACT):

| Signal | Value |
|--------|-------|
| Active subject | `governance-drift-detection` |
| Agents posted | **8/8** |
| `nudge_count` | **0** |
| `auto_pass_count` | **8/8** |
| `verified_by` | **auto** × 8 |
| `fleet_verify_gap` | `[]` |
| `mark_best` set | **no** (founder qualitative step — optional) |

## Alignment verdict

| Check | Result |
|-------|--------|
| Essay law — ASF assigns + marks best | **ALIGNED** |
| Machine verify — `auto_pass` not ASF click | **ALIGNED** (code + UI) |
| Worker / 1000-pack — no ASF verify authority | **ALIGNED** |
| Scoreboard **law** §0/§4 vs machine | **DRIFT** — law stale; UI/code correct |
| “ASF sets subject in hub” vs API | **GAP** — no hub assignment form/API |
| `mark_best` empty | **OPEN** — founder judgment pending; not blocking fleet green |

## Distinct from adjacent surfaces

| Surface | ASF role? | Machine role? |
|---------|-----------|-----------------|
| Essay subject + best | **Yes** — assign + mark best | Nudges when agents miss essay |
| Scoreboard column ✓ | **No** (maintainer force only) | **Yes** — `auto_pass` |
| REGISTRY sa-XXXX done | **No** | Broker VERIFY + receipt |
| External GPT paste | **No** — input only (`EXTERNAL_CRITIC`) | Compare to LOCKED SSOT |

## OPEN (informational — maintainer / ASF)

1. **OPEN-1:** Update `AGENT_SCOREBOARD_LOCKED_v1.md` §0/§4 to match `auto_pass` / sa-0306 (law prose only).
2. **OPEN-2:** Hub `set_assignment` action for ASF to assign new essay subjects without disk edit.
3. **OPEN-3:** ASF may tap **Mark best** on `governance-drift-detection` when ready (8 essays on disk).

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0
- `validate-governance-event-spine-v1.sh` — PASS
- `find_critical_bugs.py` — critical 0

## Prior proof

- **sa-0770** (T2) — same task title; closed with spine-bridge + fleet validators
- **sa-0791** — essay `nudge_count` crosswalk (complementary)
