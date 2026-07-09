# PR Conflict Resolver Report App + Skill — MANDATORY MAC LOCKED v1

**Saved:** 2026-07-08T02:25:00Z UTC  
**Route:** `locked_product_spec_doc` · `data/agent-filing-registry-v1.json`  
**Authority:** ASF SAVE AND LOCK

## What is locked

Two desktop app copies + one skill + machine gates:

1. **SSOT app** — `~/Desktop/Noetfield-Systems/sina-governance-SSOT/desktop-app/PR-Conflict-Resolver-Report.app`
2. **Desktop shortcut** — `~/Desktop/PR-Conflict-Resolver-Report.app` (founder daily launcher)
3. **Skill** — `sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md`

The app is an **eval review surface** ( + 8 runs). The skill is the **execution law** for merge conflicts.

## High-quality outcome law

| Step | Deliverable |
|---|---|
| Classify | Every conflicted file bucketed before edit |
| Registry JSON | Structural merge — never blind `<<<<<<<` pick |
| L1 violation | Same key, different motor → STOP, escalate |
| LOCKED docs | No autonomous final merge — founder sign-off |
| Receipts | Append-only — rename on collision, never drop |
| Proof | Resolution receipt + validators PASS before merge-ready |

## Machine commands (Mac founder session)

```bash
# Session wire (automatic via agent_session_gate_run_v1.py)
python3 scripts/pr_conflict_resolver_first_check_v1.py --wire --json

# Before resolving any governance conflict
python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json

# Open eval app (founder review)
open ~/Desktop/PR-Conflict-Resolver-Report.app

# Full wiring proof
bash scripts/validate-pr-conflict-resolver-mandatory-v1.sh
```

## Pointer chain

- Law: `brain-os/law/enforcement/PR_CONFLICT_RESOLVER_MANDATORY_LOCKED_v1.md`
- SSOT: `data/pr-conflict-resolver-mandatory-v1.json`
- SG lock: `sina-governance-SSOT/data/pr_conflict_skill_lock_v1.json`
