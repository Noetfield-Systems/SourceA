# Infra — Supabase portfolio tiers

**ASF decision:** Virlux lives in **Labs Sandbox**, not Portfolio Spine or a ring-fenced production project.

**Virlux code/docs home:** `labs/virlux/README.md` — graduation trigger when real money/user data.

**Root cleanup:** `infra/cleanup/` — manifest-first; secret scan before snapshot commit.

**Machine SSOT:** `data/supabase-portfolio-tiers-v1.json`

## Two-project layout

```text
Project 1 — portfolio-spine (production)
  noetfield · trustfield · witnessbc · foundation
  Schema isolation + strict RLS + per-schema DB roles
  Cross-schema queries allowed within this project only

Project 2 — labs-sandbox (disposable)
  virlux · labs/* · research · experiments
  Agent dev keys ONLY for this project
  Safe to delete and recreate
```

## What is NOT in this repo

Production credentials never live under `infra/` or anywhere in the workspace tree.

| Secret file (local only) | Project |
|---------------------------|---------|
| `~/.sourcea-secrets/portfolio-spine.env` | Portfolio Spine |
| `~/.sourcea-secrets/labs-sandbox.env` | Labs Sandbox |

See `infra/secrets/README.md` and `scripts/infra/load-supabase-secrets-v1.sh`.

## Cross-project integration (async only)

Portfolio Spine and Labs Sandbox **do not share Postgres**. No cross-project JOINs.

**Assumption (founder must confirm):** Noetfield and TrustField consume Virlux outcomes via **signed receipts / status events**, not live DB reads. If that assumption is wrong, add an explicit integration layer (webhook or event bus) — do not collapse projects to save a join.

## Directory map

```text
infra/
├── README.md                          ← this file
├── supabase/
│   ├── portfolio-spine/               ← production schemas + migrations
│   └── labs-sandbox/                  ← virlux + labs (disposable)
├── secrets/
│   └── README.md                      ← pointer only — no secret files here
└── scripts/
    └── load-supabase-secrets-v1.sh    ← sources ~/.sourcea-secrets/*.env
```

## Doctrine

**Noetfield Talks · Trustfield Acts · Blockfield Settles** — governance and delivery stay on Portfolio Spine. Virlux experiments stay in Labs until ASF promotes a production isolation tier.
