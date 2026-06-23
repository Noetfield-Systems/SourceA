# Vercel Pro migration week — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-21T00:45:00Z · **Authority:** ASF  
**Path:** `docs/VERCEL_PRO_MIGRATION_WEEK_LOCKED_v1.md`  
**Machine SSOT:** `data/vercel-pro-migration-week-v1.json`  
**Target date:** **2026-06-27** (Friday)

## One law

> **Mac CLI + Cursor agents deploy only on `the-777-foundation` (`kazemnezhadsina144@gmail.com`). Trial `noetfield-systems` is disconnected from Mac — Stripe-only lane until trial projects deleted after Pro week.**

---

## Why trial existed (still true — not forgotten)

| Reason | Account | After 2026-06-27 |
|--------|---------|------------------|
| **Stripe / Noetfield Systems billing** | `noetfield@gmail.com` | **Stays forever** — not a Vercel deploy owner |
| **Pro trial for deploy testing** | `noetfield-systems` | **End trial** — delete orphan projects |
| **Working Noetfield intake (Resend env)** | trial project `www` → `project-gc7lm.vercel.app` | **Copy env → main `noetfield`** before delete trial |
| **Cross-Gmail Vercel transfer** | impossible | Recreate from GitHub on main — never “Transfer” modal |

---

## Part A — Disconnect trial from Mac / Cursor (do anytime)

**Cursor has no separate Vercel login.** It runs the **Mac Vercel CLI** OAuth session. Trial stuck = Mac CLI still on `noetfield-6488` / `noetfield-systems`.

### A1. Log out trial (Terminal.app only — not Cursor agent)

```bash
vercel logout
```

Optional clean slate:

```bash
rm -rf ~/.vercel
```

### A2. Connect main (pick ONE — never both in a loop)

**Option 1 — OAuth once in Terminal**

```bash
bash ~/Desktop/SourceA/scripts/switch_vercel_cli_main_v1.sh --terminal
```

Sign in as **`kazemnezhadsina144@gmail.com`**. Wait until Terminal prints **PASS**. Close tab — do **not** approve new device codes from Cursor.

**Option 2 — Token (best for Cursor + CI)**

1. Main Chrome → [vercel.com/account/settings/tokens](https://vercel.com/account/settings/tokens) (logged in as `kazemnezhadsina144@gmail.com`)
2. Create token · Full Account · No expiration
3. Once:

```bash
bash ~/Desktop/SourceA/scripts/switch_vercel_cli_main_v1.sh --token 'PASTE_ONCE'
```

### A3. Verify (Terminal)

```bash
vercel whoami          # must NOT be noetfield-6488
vercel teams ls        # must list the-777-foundation
bash ~/Desktop/SourceA/scripts/switch_vercel_cli_main_v1.sh --check
```

### A4. Agent rules (locked)

- **Forbidden:** `vercel login` from Cursor agent (spawns duplicate OAuth → rate limit)
- **Allowed:** deploy with saved token or confirmed Terminal OAuth
- **Trial CLI rejected:** `scripts/sourcea_vercel_token_v1.py` fails if whoami starts with `noetfield`

### A5. Wire env for all deploy scripts

```bash
source ~/.sina/vercel-main-cli-v1.env
```

---

## Part B — Pro upgrade week (2026-06-27)

### B0. Before 27 June (prep — no Pro required)

| # | Action | Owner |
|---|--------|-------|
| 1 | GitHub green: SourceA · deploy-witnessbc · Noetfield | done / maintain |
| 2 | Main Vercel: keep **`source-a`** · delete **`source-a-ezhe`** | founder dashboard |
| 3 | Copy trial `www` **RESEND_*** env → main **`noetfield`** · redeploy · fix intake | founder dashboard |
| 4 | Import **`witnessbc-governance-main`** from deploy repo (rename law) | founder dashboard |
| 5 | Mac CLI on main (Part A) or token saved | founder Terminal once |

### B1. 2026-06-27 — Upgrade main to Pro

| Step | Where | Action |
|------|-------|--------|
| 1 | [vercel.com/the-777-foundation](https://vercel.com/the-777-foundation) | Settings → Billing → **Upgrade to Pro** |
| 2 | Same dashboard | Confirm team **`the-777-foundation`** · Gmail **`kazemnezhadsina144@gmail.com`** |
| 3 | Do **not** extend trial Pro on `noetfield-systems` as long-term home |

### B2. 2026-06-27 — Post-Pro checklist

| # | Project | Main name | GitHub | DNS |
|---|---------|-----------|--------|-----|
| 1 | SourceA | `source-a` | SourceA | source-a.vercel.app |
| 2 | WitnessBC | `witnessbc-governance-main` | deploy-witnessbc-agentic-governance | www.witnessbc.com when ready |
| 3 | Noetfield | `noetfield` or `noetfield-www-main` | Noetfield | www.noetfield.com |
| 4 | TrustField | `trustfield-personal` | (existing) | trustfield.ca |

Run:

```bash
bash ~/Desktop/SourceA/scripts/validate-vercel-deploy-urls-v1.sh
```

### B3. After all main URLs green — delete trial (`noetfield-systems`)

Delete only after founder confirms main green:

- `sourcea-landing` · `sourcea-landing-clone`
- `deploy` · `deploy-clone` · `deploy-witnessbc-agentic-governance`
- `www` · `www-clone`

**Keep:** `noetfield@gmail.com` for **Stripe** only.

### B4. Rejected

- Permanent Pro only on `noetfield@gmail.com`
- Cross-Gmail Vercel project transfer
- Cursor agent OAuth login loops
- Redeploy to trial after 2026-06-27

---

## Acceptance (2026-06-27 EOD)

- [ ] Main team **Pro** active on `kazemnezhadsina144@gmail.com`
- [ ] Mac CLI `--check` **ok: true** OR token file on main scope
- [ ] `source-a.vercel.app/sourcea/` **200**
- [ ] Noetfield intake **not 502** on www.noetfield.com
- [ ] WitnessBC on main project (not trial sooty URL)
- [ ] Trial `noetfield-systems` projects deleted or empty
- [ ] Stripe still on `noetfield@gmail.com`

---

## Related

- `data/vercel-portfolio-map-v1.json`
- `data/portfolio-account-structure-v1.json` → `vercel_pro_migration`
- `scripts/switch_vercel_cli_main_v1.sh`
- `docs/PORTFOLIO_VERCEL_CONSOLIDATION_LOCKED_v1.md`
