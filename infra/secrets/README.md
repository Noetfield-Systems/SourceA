# Secrets — out of workspace

**Law:** No production Supabase keys, service roles, or FINTRAC-scoped credentials inside this repository or any path Cursor agents can read by default.

## Canonical location

```text
~/.sourcea-secrets/
├── portfolio-spine.env      # Project 1 — production
├── labs-sandbox.env         # Project 2 — disposable (Virlux + labs)
└── README.md                # optional local notes
```

Create from examples:

```bash
cp infra/supabase/portfolio-spine/config.example.env ~/.sourcea-secrets/portfolio-spine.env
cp infra/supabase/labs-sandbox/config.example.env ~/.sourcea-secrets/labs-sandbox.env
# Edit with real values — never commit
```

## Load in shell

```bash
source infra/scripts/load-supabase-secrets-v1.sh portfolio-spine
# or
source infra/scripts/load-supabase-secrets-v1.sh labs-sandbox
```

## Agent rule

Autonomous agents may reference **labs-sandbox** credentials only when explicitly scoped to `infra/supabase/labs-sandbox/**`. Portfolio Spine credentials are for CI and founder-run scripts — not agent `.env` files in the repo.

## Future

When Virlux graduates from Labs, ASF may create a third ring-fenced project. That requires a new ADR and tier JSON bump — not a silent schema move.
