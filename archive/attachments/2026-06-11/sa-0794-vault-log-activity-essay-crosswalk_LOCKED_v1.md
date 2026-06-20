# sa-0794 ACT — vault log_activity on essay post crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Validate that `agent_essay_discourse.submit_essay()` writes **workspace vault activity** (`essay_submitted`) on every essay post, and that scoreboard auto-check `vault_activity` passes for essay agents.

## Requirement sources (authority order)

| Layer | Source | Requirement |
|-------|--------|-------------|
| Law | `AGENT_WORKSPACE_VAULT_MIDDLE_LAYER_LOCKED_v1.md` §2 | `activity.jsonl` append-only work log at `~/.sina/agent-workspaces/<agent_id>/activity.jsonl` |
| Law | `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` | 8 agents post essay (≥120 chars) per active subject via hub |
| Machine SSOT | `agent_essay_discourse.py` `submit_essay()` | After essay append: `deposit_document(..., source=essay_discourse)` + `log_activity(action=essay_submitted, kind=learn, source=essay)` |
| Vault API | `agent_workspace_vault.py` | `log_activity` → `_append_activity` · `deposit_document` also logs `document_deposited` |
| Scoreboard | `agent_scoreboard.py` | Auto requirement `vault_activity` — ≥1 activity row in report window |
| Trust ledger | `TRUST_LEDGER_SCHEMA_LOCKED_v1.md` | Event type `essay_submitted` documented |

## Code path (machine contract)

```
submit_essay(agent_id, subject, body)
  → _append_essay(row)                    # essays.jsonl
  → log_governance_event(essay_submitted) # best-effort
  → deposit_document(..., source=essay_discourse)
  → log_activity(..., action=essay_submitted, kind=learn, source=essay)
```

Both vault hooks wrapped in `try/except: pass` — failures silent (OPEN-1 below).

## Live disk proof (ACT)

| Agent | essay_submitted logs | essay_discourse deposits | vault_activity | vault_deposit |
|-------|---------------------|--------------------------|----------------|---------------|
| trustfield | 1 | 1 | PASS | PASS |
| virlux | 1 | 1 | PASS | PASS |
| ai_dev_bridge_os | 1 | 1 | PASS | PASS |
| noetfield_local | 1 | 1 | PASS | PASS |
| noetfield_cloud | 1 | 1 | PASS | PASS |
| seven77 | 1 | 1 | PASS | PASS |
| semej | 1 | 1 | PASS | PASS |
| sinaai_maintainer | 2 | 2 | PASS | PASS |

| Metric | Value |
|--------|-------|
| Essay agents | **8/8** |
| Essays logged | **9** (maintainer double-post — nudges unaffected) |
| `nudge_count` | **0** |
| Fleet `auto_pass_count` | **8/8** |
| Activity file path | `{workspace_root}/activity.jsonl` (law §2 — not inside `vault/`) |

Sample activity row:

```json
{"action": "essay_submitted", "detail": "governance-drift-detection", "kind": "learn", "source": "essay"}
```

## Alignment verdict

| Check | Result |
|-------|--------|
| Essay post → `log_activity(essay_submitted)` | **ALIGNED** — 8/8 agents |
| Essay post → `deposit_document` | **ALIGNED** — paired `document_deposited` rows |
| Scoreboard `vault_activity` auto check | **ALIGNED** — 8/8 PASS |
| Vault law path `activity.jsonl` | **ALIGNED** — matches `vault_paths()` |
| Essay law explicit vault hook | **DRIFT** — `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` silent on `log_activity` |
| Silent `try/except` on vault hook | **RISK** — not failing today |

## Distinct surfaces

| Surface | Role |
|---------|------|
| `essay_submitted` activity row | Vault work log + scoreboard `vault_activity` |
| `document_deposited` (source=essay_discourse) | Vault deposit + scoreboard `vault_deposit` |
| `log_governance_event(essay_submitted)` | Governance spine — separate from vault activity |
| Essay `nudge_count` (sa-0791) | Missing-essay fleet nudges — not vault activity |

## OPEN (informational — maintainer, not Worker code)

1. **OPEN-1:** Replace silent `try/except: pass` in `submit_essay()` with logged failure or hard fail when vault hook errors.
2. **OPEN-2:** Cross-link `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` → vault `essay_submitted` contract.
3. **OPEN-3:** 9 essays / 8 agents — optional dedupe hygiene on maintainer lane.

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0
- `validate-governance-event-spine-v1.sh` — PASS
- `find_critical_bugs.py` — critical 0

## Prior proof

- **sa-0769** (T2) — same task title; machine green at T2
- **sa-0791** — essay discourse / `nudge_count` crosswalk (complementary, not duplicate)
