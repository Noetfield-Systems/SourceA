# Portfolio fix plan — LOCKED v1

**Version:** 1.0.0 LOCKED · **Saved:** 2026-06-19T19:26:11Z  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_PORTFOLIO_FIX_PLAN_LOCKED_v1.md`  
**Machine SSOT:** `data/portfolio-fix-plan-v1.json`  
**Pulse:** `scripts/portfolio_fix_plan_pulse_v1.py` → `~/.sina/portfolio-fix-plan-pulse-v1.json`  
**Execute:** `bash scripts/portfolio_fix_execute_v1.sh`  
**Defer law:** `data/commercial-email-send-defer-v1.json`

---

## One law

> Portfolio revenue unlock = **TrustField ladder GREEN** + **WitnessBC prod markers GREEN** → **defer lift** → MSB 15× → demos 3 → $6K pilot. **Roles never cross repos.**

**Defer line (quote every turn):** read `email_send_defer_line` from `~/.sina/agent-live-surfaces-v1.json`  
**Portfolio line:** read `portfolio_fix_line` from same surfaces file.

---

## Role separation

| Role | Repo / chat | Edits | Forbidden |
|------|-------------|-------|-----------|
| **Founder** | Hub Actions | DNS · Stripe · `--lift` · invoice | Terminal routine |
| **Brain** | Brain chat | Route · handoff · disk truth | Implement sa-* · product code |
| **SourceA Worker** | Worker · RUN INBOX | `SourceA/**` WitnessBC deploy | TrustField repo |
| **TrustField Agent** | TF workspace | `TrustField Technologies/**` | WitnessBC / SourceA |

---

## Unlock chain

```text
TF ladder 1–4 GREEN → WBC prod markers → sites=GREEN → founder lift → MSB 15× → demos 3 → $6K
```

---

## Phase P0 (parallel)

### TrustField Agent — `~/Desktop/TrustField Technologies`

| ID | Task | Command |
|----|------|---------|
| TF-P0-1 | Ladder 1–4 green | `./scripts/ui_build_and_verify.sh` |
| TF-P0-2 | Readiness stable | `VERIFY_BASE_URL=https://www.trustfield.ca ./scripts/ship_p0_first_customer.sh` |
| TF-P0-3 | E2E 12/12 | `./scripts/verify_commercial_e2e.sh` |

### SourceA Worker — `~/Desktop/SourceA`

| ID | Task | Command |
|----|------|---------|
| WBC-P0-1 | UI FIRST CHECK | `wbc-ui-first-check.sh --surface witnessbc_commercial --ack` |
| WBC-P0-2 | Guards | `wbc-guard-check.sh` |
| GOV-P0-1 | Portfolio execute | `portfolio_fix_execute_v1.sh` |

### Founder

| ID | Task |
|----|------|
| WBC-P0-3 | DNS `www.witnessbc.com` → CF Pages |
| WBC-P0-4 | Paste 11 Stripe URLs → redeploy |

---

## Phase P1 — Founder only

`python3 scripts/commercial_email_send_defer_v1.py --lift` when defer receipt `sites_online: true`.

---

## Phase P2 — TrustField Agent + Founder

MSB 15× · demos 3× · founder invoice $6K. Email law: *Your MSB remains settlement party of record.*

---

## Machine commands

```bash
bash ~/Desktop/SourceA/scripts/portfolio_fix_execute_v1.sh
bash ~/Desktop/SourceA/scripts/validate-portfolio-fix-plan-v1.sh
python3 ~/Desktop/SourceA/scripts/portfolio_fix_plan_pulse_v1.py --wire --json
```

---

## Handoffs

- TrustField: `~/.sina/agent-workspaces/trustfield/PORTFOLIO_FIX_HANDOFF_LOCKED_v1.md`
- Worker: `~/.sina/agent-workspaces/sourcea-worker/PORTFOLIO_FIX_HANDOFF_LOCKED_v1.md`
