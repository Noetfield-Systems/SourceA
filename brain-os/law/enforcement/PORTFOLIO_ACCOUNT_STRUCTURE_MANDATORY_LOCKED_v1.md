# Portfolio account structure — mandatory for all agents — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-20T21:45:00Z · **Authority:** ASF order 2026-06-20  
**Machine SSOT:** `data/portfolio-account-structure-v1.json`  
**Human SSOT:** `docs/PORTFOLIO_ACCOUNT_STRUCTURE_LOCKED_v1.md`  
**Cursor rule:** `.cursor/rules/044-portfolio-account-structure-mandatory.mdc` (alwaysApply)

---

## One law

> **Every agent on every portfolio, cloud, DNS, email, Vercel, GitHub, or Stripe task reads the account map first — and every portfolio report includes `portfolio_account_structure_line`.**

No exceptions. No “I assumed main lane.”

---

## ASF decisions locked this session

| Decision | Value |
|----------|--------|
| Vercel Pro owner | `kazemnezhadsina144@gmail.com` — upgrade hobby → Pro |
| Vercel migration | Move `noetfield@gmail.com` deploys to main Pro **next week** |
| TrustField GitHub | `kazemnezhadsina144-dot/TrustField-Technologies` (verify each session) |
| WitnessBC isolation | `witness.bc@gmail.com` — GitHub · Vercel · Cloudflare · Stripe |
| VIRLUX product | Agentic factory only — payments copy **forbidden** on public marketing |

---

## Agent MUST

1. Read `data/portfolio-account-structure-v1.json` before infra edits
2. Quote `portfolio_account_structure_line` in portfolio / repo / cloud reports
3. Run `bash scripts/run-portfolio-supabase-daily-v1.sh` when reporting stay-up status
4. Update SSOT when founder changes Gmail or Vercel ownership — bump **`Saved:`** UTC

## Agent MUST NOT

- Use WitnessBC credentials on main-lane repos
- Ship VIRLUX “cross-border B2B payments” marketing (TrustField lane)
- Store secrets in repo — login emails and vault key **names** only

---

## Wire chain

```text
data/portfolio-account-structure-v1.json
  → scripts/portfolio_account_structure_v1.py
  → ~/.sina/portfolio-account-structure-v1.json
  → agent-live-surfaces-v1.json (portfolio_account_structure_line)
  → portfolio-supabase-daily-pulse receipt (account_structure block)
```

---

## Related

- `data/platform-neutral-world-model-v1.json` — Stripe entity Noetfield Systems  
- `SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` — hello@sourcea.com  
- `labs/virlux/README.md` — VIRLUX agentic-only policy
