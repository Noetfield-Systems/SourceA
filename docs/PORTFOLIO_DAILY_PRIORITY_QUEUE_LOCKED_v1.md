# Portfolio daily priority queue — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-20T22:30:00Z · **Authority:** ASF (#10)  
**Machine SSOT:** `data/portfolio-daily-priority-queue-v1.json`  
**Script:** `scripts/portfolio_daily_priority_queue_v1.py`  
**Surfaces line:** `portfolio_priority_line`

---

## Bottom line

Everything responds on the network — Mac cockpit, cloud FBE, and all five portfolio product URLs. The real gaps are **content/policy** (WitnessBC prod, TrustField ladder), **Supabase secrets** not on Mac for daily DB keepalive, and **lane commits**.

---

## Priority queue

| Pri | Repo | Blocker | Owner |
|-----|------|---------|--------|
| **P0** | WitnessBC | Prod = old journalism · artifact correct logged | SourceA worker + founder DNS/Stripe |
| **P0** | TrustField | Ladder RED · commercial_blocked | TrustField agent |
| **P1** | VIRLUX | POSITIONING agentic-only (payments OUT) | VIRLUX agent |
| **P1** | All | Supabase secrets missing on Mac | Founder — `setup_supabase_secrets_mac_v1.sh` |
| **P2** | VIRLUX | verify:live needs VERCEL_TOKEN | Founder + VIRLUX agent |
| **P2** | SourceA | Uncommitted batch when scoped | Founder |

---

## Supabase (both tiers)

| Project | Secrets file | Setup |
|---------|--------------|--------|
| portfolio-spine | `~/.sourcea-secrets/portfolio-spine.env` | `infra/supabase/portfolio-spine/config.example.env` |
| labs-sandbox (VIRLUX) | `~/.sourcea-secrets/labs-sandbox.env` | `infra/supabase/labs-sandbox/config.example.env` |

```bash
bash ~/Desktop/SourceA/scripts/setup_supabase_secrets_mac_v1.sh
```

Sites stay UP without secrets; **daily Supabase keepalive is skipped** until real URL + anon key are pasted.

---

## Daily command (all websites + Supabase + priority)

```bash
bash ~/Desktop/SourceA/scripts/run-portfolio-supabase-daily-v1.sh
```

Receipts: `~/.sina/portfolio-supabase-daily-pulse-v1.json` · `~/.sina/portfolio-daily-priority-queue-v1.json`

Every agent report quotes: `portfolio_supabase_daily_line` · `portfolio_account_structure_line` · `portfolio_priority_line` · `portfolio_fix_line`
