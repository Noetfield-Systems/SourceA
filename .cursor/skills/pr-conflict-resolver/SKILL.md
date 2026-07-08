---
name: pr-conflict-resolver
description: >
  Resolve git merge conflicts on pull requests within the sina-governance-SSOT
  (SG) multi-lane governance system, and any venture repo that follows the
  same lane/motor law (SourceA, TrustField, NOOS, Noetfield website). Use this
  whenever a PR shows conflicting files, a branch is behind main and won't
  fast-forward, two lanes touched the same registry/ledger file, or the user
  says things like "resolve this PR conflict," "this branch won't merge,"
  "merge main into my branch," "two agents edited the same JSON," or pastes a
  git conflict marker block. MANDATORY on SourceA — machine gate via
  pr_conflict_resolver_first_check_v1.py. Eval app: ~/Desktop/PR-Conflict-Resolver-Report.app
compatibility: >
  Requires read access to the repo's AGENTS.md, ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md,
  and data/github_automation_registry_v1.json for lane/motor context. Assumes
  git CLI. SourceA: run python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json before resolving.
---

# PR Conflict Resolver — pointer to SG SSOT

**Canonical skill (read this):**  
`~/Desktop/Noetfield-Systems/sina-governance-SSOT/skills/pr-conflict-resolver/SKILL.md`

**Machine law:** `brain-os/law/enforcement/PR_CONFLICT_RESOLVER_MANDATORY_LOCKED_v1.md`  
**SSOT:** `data/pr-conflict-resolver-mandatory-v1.json`  
**Eval app:** `open ~/Desktop/PR-Conflict-Resolver-Report.app`

## Session commands

```bash
python3 scripts/pr_conflict_resolver_first_check_v1.py --wire --json
python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json
bash scripts/validate-pr-conflict-resolver-mandatory-v1.sh
```

Do not duplicate skill prose here — SG skill is authoritative.
