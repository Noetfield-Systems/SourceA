# Agent verbs — SAVE · WORK · EDIT ALLOWED (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-09 · **Parent:** `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md`

## SAVE

Founder wants a **physical file kept for future reference**.

- If founder provides `SAVE TO:` / `SAVE AS:` with a path, write **only** that named path under `docs/` or lane vault.
- If founder gives pathless `SAVE`, `SAVE AND LOCK`, `LOCK`, `FILE`, or an `ASF:` batch phrase, run the filing registry first:

```bash
python3 scripts/agent_filing_registry_gate_v1.py resolve --agent <id> --intent "<founder message>" --json
```

- If registry returns `ok:true`, use its `route_id`, `path`, and `next_steps[]`; do **not** ask ASF for an exact path.
- Ask ASF only when registry returns `REGISTRY_NO_MATCH` or `REGISTRY_AMBIGUOUS`, and ask for category/scope, not a filesystem path.
- Never let path-asking words from an agent reply become a filename slug.
- File is **stable archive** — no follow-up edits to SSOT, registry, scripts, or other agents’ docs.
- **Stop** after the file exists.

Example: `Save golden report to docs/research/golden_site_v1.yaml` → one write → done.
Example: `SAVE_AND_LOCK site intelligence hub` → registry route `locked_product_spec_doc` → `docs/SITE_INTELLIGENCE_HUB_LOCKED_v1.md`.

## WORK

SourceA Worker or Product chat doing **assigned build**.

- Execute INBOX / `sa-*` / product code in scope.
- **No extra confirmation** for normal bound turns.
- Guard: `cross_lane_edit_guard_v1.py` allows Worker prefix paths.

## EDIT ALLOWED

Cross-lane or canonical doc change.

- Requires `EDIT ALLOWED: <path>` + `ACTION:` in same founder message.
- Rare — not part of SAVE or WORK.

## On rule conflict

Run `.cursor/skills/skill-007-ecosystem-conflict-resolution/SKILL.md` before any edit. Precedence: founder order → permission/ask-first → incidents → `execution_authority: false` → workflow bundles → ship-first/plan.json alone.

## Monitoring

```bash
bash scripts/validate-agent-filing-registry-v1.sh
bash scripts/validate-cross-lane-edit-v1.sh
```

Violations log: `~/.sina/governance-events.jsonl` (append on guard FAIL).
