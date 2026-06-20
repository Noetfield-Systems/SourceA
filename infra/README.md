# Infra — Supabase portfolio tiers

**ASF decision (2026-06-20):** Virlux is **agentic factory SaaS online** on **Labs Sandbox** Supabase — FINTRAC/payment rails **OUT of VIRLUX** (TrustField or future company).

**Virlux code/docs home:** `labs/virlux/README.md` · primary repo `~/Desktop/VIRLUX`

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

## Daily stay-up (websites + Supabase)

**Law:** Portfolio stays **online** — light daily pulse on every public site + both Supabase tiers.

```bash
bash scripts/run-portfolio-supabase-daily-v1.sh
```

| Artifact | Purpose |
|----------|---------|
| `data/portfolio-websites-supabase-daily-v1.json` | Site URLs + Supabase tier map |
| `~/.sina/portfolio-supabase-daily-pulse-v1.json` | Last receipt |
| `portfolio_supabase_daily_line` | Hub / surfaces glance line |
| `data/portfolio-account-structure-v1.json` | Gmail + service login map (all lanes) |
| `portfolio_account_structure_line` | Account map glance — wired on every daily pulse |
| `data/portfolio-daily-priority-queue-v1.json` | P0/P1/P2 blockers (#10) |
| `portfolio_priority_line` | Priority queue glance |
| `bash scripts/setup_supabase_secrets_mac_v1.sh` | Founder one-time Supabase secrets scaffold |

**Checks:** HTTP on Noetfield · TrustField · WitnessBC · VIRLUX web/API · optional SourceA landing · `GET {SUPABASE_URL}/auth/v1/health` for portfolio-spine + labs-sandbox (secrets in `~/.sourcea-secrets/`).

**Mac rule:** One script only — no validator marathon. Fix RED in the **lane agent** for that module.

## Doctrine

**Noetfield Talks · Trustfield Acts · Blockfield Settles** — governance and delivery stay on Portfolio Spine. Virlux agentic factory stays online on labs-sandbox until payment/MSB data forces graduation.
