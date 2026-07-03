# Governed Autorun Laws v3 — L14 + L15 (automation excerpt)

**Full doc:** restore from `main` branch · this workspace carries automation extensions only.

## L14 — Every trigger is registered before it ships

Any new schedule, cron, GitHub Action trigger, or piggyback hook **must** add a row to `data/trigger-registry-v1.json` **in the same commit**. Pre-merge: `scripts/validate-trigger-registry-v1.sh`.

## L15 — Automation lane ownership (living system parallel)

Every automation belongs to exactly **one lane** in `data/automation-lane-registry-v1.json` with **one executor** owning each **action class**.

- Parallel execution across **different lanes** is required (cloud motor + GHA truth + Worker build simultaneously).
- Duplicate execution of the **same action class** on the **same op_key** is forbidden (D1 + conflict matrix).
- **GitHub Copilot** proposes PRs — **Worker** implements — **Brain** routes — **Cloud** runs motors — **GHA** proves truth.
- **GitHub Agents** use `repository_dispatch` with `{mission_id, workflow_id, op_key}` — motor class forbidden.
- **GHA** must not schedule Cloud Forge Run motor (manual backup dispatch only).

**Governance SSOT:** `docs/GITHUB_AUTOMATION_LIVING_SYSTEM_GOVERNANCE_LOCKED_v1.md`
