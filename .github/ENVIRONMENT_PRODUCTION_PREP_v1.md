# GitHub Environment `production` — founder enablement (PN-003 prep)

**Status:** PREP ONLY — founder action required in GitHub UI before enforcement blocks deploys.

## What is wired

- `.github/workflows/deploy-sourcea-buyer-surfaces-v1.yml` job uses `environment: production`
- Until reviewers are configured, GitHub may allow deploy (org policy dependent)

## Founder steps (P4 · ~5 min)

1. Open **Settings → Environments → New environment** → name: `production`
2. Enable **Required reviewers** → add founder GitHub account(s)
3. Optional: **Wait timer** 0 min · **Deployment branches** → `main` only
4. Confirm mobile GitHub notification works for approval requests

## Law

- L15 agent-D2: only cloud Loop Specialist merges to `main`; deploy approval stays founder-gated (L5/L6)
- PN-001 chain: after deploy job succeeds, `external-verify` fires via `workflow_run` (no sleep guess)

## Not enabled until founder completes UI

- Branch protection required checks — applied via `scripts/apply_github_main_branch_protection_v1.sh` (context: `validate`)
- GitHub Actions secrets — sync from `~/.sourcea-secrets/` via `scripts/sync_github_actions_secrets_v1.sh`

- CODEOWNERS (P4 before Copilot Kaizen P7)
