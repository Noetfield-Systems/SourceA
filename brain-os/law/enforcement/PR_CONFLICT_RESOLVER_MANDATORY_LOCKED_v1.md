# PR Conflict Resolver — MANDATORY (LOCKED v1)

**Status:** LOCKED — 2026-07-08T02:25:00Z UTC  
**Authority:** ASF  
**Machine SSOT:** `data/pr-conflict-resolver-mandatory-v1.json`  
**SG SSOT:** `~/Desktop/Noetfield-Systems/sina-governance-SSOT/data/pr_conflict_skill_lock_v1.json`

## One law

> **Governance-sensitive merge conflicts MUST follow `pr-conflict-resolver` skill before any side is picked, committed, or declared merge-ready.**

## Locked artifacts

| Artifact | Path |
|---|---|
| Canonical skill | `sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md` |
| SG lock doc | `sina-governance-SSOT/skills/pr-conflict-resolver/PR_CONFLICT_RESOLVER_SKILL_LOCKED_v1.md` |
| Eval desktop app (SSOT) | `sina-governance-SSOT/desktop-app/PR-Conflict-Resolver-Report.app` |
| Desktop shortcut | `~/Desktop/PR-Conflict-Resolver-Report.app` |
| SourceA machine SSOT | `data/pr-conflict-resolver-mandatory-v1.json` |
| First-check script | `scripts/pr_conflict_resolver_first_check_v1.py` |
| Verifier | `scripts/verify_pr_conflict_skill_v1.py` |
| Wiring validator | `scripts/validate-pr-conflict-resolver-mandatory-v1.sh` |
| Cursor rule | `.cursor/rules/pr-conflict-resolver-mandatory-v1.mdc` |

## Mandatory sequence (every agent)

1. **Wire** (session): `python3 scripts/pr_conflict_resolver_first_check_v1.py --wire --json`
2. **Ack** (before resolving): `python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json`
3. **Classify** each conflicted file (registry / receipt / LOCKED / generated / code)
4. **Resolve** per skill — structural JSON merge; STOP on L1 duplicate ownership
5. **Validate**: `bash scripts/validate-pr-conflict-resolver-mandatory-v1.sh`
6. **Receipt**: `receipts/pr-conflict-resolution-<UTC>.json` before merge-ready claim

## Machine enforcement

- `pre_write_guard_v1.py` blocks writes to governance paths with conflict markers without ack
- Session gate wires `pr_conflict_resolver_first_check` each session
- Receipt: `~/.sina/pr-conflict-resolver-first-check-receipt-v1.json`

## Eval  (locked)

With-skill **100%** · without-skill **76%** on governance cases.  
Open `~/Desktop/PR-Conflict-Resolver-Report.app` before changing skill law.

## Unlock

Founder gate only — do not weaken L1 stop rules or receipt requirements.
