# Portfolio account structure — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-20T21:45:00Z · **Authority:** ASF  
**Path:** `docs/PORTFOLIO_ACCOUNT_STRUCTURE_LOCKED_v1.md`  
**Machine SSOT:** `data/portfolio-account-structure-v1.json`  
**Source proposal:** `~/Desktop/TrustField Technologies/docs/MACLAW_PORTFOLIO_ACCOUNT_MAP_PROPOSAL.md` (founder-confirmed 2026-06-19)

---

## One law

**One brand · one identity stack · one browser profile per lane.**  
Never use WitnessBC credentials for TrustField, Noetfield, VIRLUX, or SourceA repo/DNS/email/CI work.

---

## Main lane — TrustField · Noetfield · portfolio hub · VIRLUX · SourceA

| Gmail / login | Service | Scope |
|---------------|---------|--------|
| `kazemnezhadsina144@gmail.com` | GitHub (main org) | TrustField Technologies · SourceA · VIRLUX repos |
| `kazemnezhadsina144@gmail.com` + `noetfield@gmail.com` | Vercel | trustfield.ca · noetfield.com · sourcea.com · virlux-* — **Pro target on main** |

**ASF 2026-06-20:** Upgrade **`kazemnezhadsina144@gmail.com`** from hobby → **Pro**. Migrate projects currently on **`noetfield@gmail.com`** to main Pro account **by 2026-06-27**. Rejected: permanent split with Pro only on noetfield@gmail.com.
| `sinakazemnezhad.ca@gmail.com` | Cloudflare (main) | trustfield.ca · noetfield.com · sourcea.com DNS · TrustField email tokens |
| `noetfield@gmail.com` | Stripe | Noetfield Systems billing (`NOETFIELD SYSTEMS` descriptor) |
| `kazemnezhadsina144@gmail.com` | Railway · Supabase SSO | FBE · MergePack · portfolio-spine + labs-sandbox dashboards |

**Chrome profile A** — main lane only.

### Official send-from (never personal Gmail on commercial)

| Address | Brand | Law / script |
|---------|-------|----------------|
| `hello@trustfield.ca` | TrustField Technologies | Workspace · `commercial_mail_draft_v1.py --lane TF` |
| `operation@noetfield.com` | Noetfield | Mail.app gate · also `operations@noetfield.com` for NW1 |
| `hello@sourcea.app` | SourceA | `SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` · AB1 |
| `hello@virlux.com` | VIRLUX | Product contact |

Vault keys (names only — values in `~/.sina/secrets.env` / `~/.sourcea-secrets/`):  
`GOOGLE_WORKSPACE_APP_PASSWORD` · `CF_API_TOKEN` · `CF_EMAIL_API_TOKEN` · `CF_ZONE_ID` · `VERCEL_TOKEN` · `RESEND_API_KEY`

---

## WitnessBC lane — isolated

| Gmail | Service | Scope |
|-------|---------|--------|
| `witness.bc@gmail.com` | GitHub · Vercel · Cloudflare · Stripe | witnessbc.com only |

**Chrome profile B** — WitnessBC only.

**Send-from:** `hello@witnessbc.com`

**Do not** store WitnessBC tokens in TrustField main vault rows (prefix `WITNESSBC_*` if shared file).

---

## Why this exists (MSB wave 401)

Using WitnessBC Cloudflare login or DNS-scoped `CF_API_TOKEN` as email send caused 401 on TrustField MSB wave. **Preferred path:** `hello@trustfield.ca` via Google Workspace app password — not WitnessBC CF account.

---

## Always wired (reports)

| Artifact | Role |
|----------|------|
| `data/portfolio-account-structure-v1.json` | Machine SSOT |
| `scripts/portfolio_account_structure_v1.py` | Sync receipt + surfaces line |
| `~/.sina/portfolio-account-structure-v1.json` | Pulse receipt |
| `agent-live-surfaces-v1.json` → `portfolio_account_structure_line` | Agent inject |
| Daily pulse receipt | `account_structure` block on every portfolio-daily run |

**Daily command:** `bash scripts/run-portfolio-supabase-daily-v1.sh` (includes account wire)

---

## Mandatory for all agents

**Law:** `brain-os/law/enforcement/PORTFOLIO_ACCOUNT_STRUCTURE_MANDATORY_LOCKED_v1.md`  
**Cursor:** `.cursor/rules/044-portfolio-account-structure-mandatory.mdc` (alwaysApply)

Every portfolio / cloud / repo report must include **`portfolio_account_structure_line`**.

---

## Related law

- `data/commercial-mail-from-gate-v1.json` — founder Mail.app FROM gate  
- `brain-os/law/SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` — hello@sourcea.app  
- `data/platform-neutral-world-model-v1.json` — Stripe billing entity  
- `.cursor/rules/040-workspace-supabase-core.mdc` — Supabase tier boundaries
