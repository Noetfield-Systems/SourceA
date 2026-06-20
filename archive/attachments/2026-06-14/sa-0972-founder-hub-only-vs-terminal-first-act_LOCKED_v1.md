# sa-0972 ACT — Founder hub-only moat hardening

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T03:11Z · **Turn:** ACT · **Worker:** SourceA

## Shipped

| Piece | Change |
|-------|--------|
| `scripts/validate-founder-hub-only-moat-v1.sh` | Quarterly moat crosswalk — chains hub-copy + founder-docs validators; asserts law stack, AUTO-RUN flag, worker-hub policy |
| CHECK doc | `sa-0972-founder-hub-only-vs-terminal-first-agent-products_LOCKED_v1.md` (prior turn) |

## Moat signals enforced (machine)

| Signal | SSOT | Validator assert |
|--------|------|------------------|
| Hub copy no shell | `validate-hub-copy-no-terminal-v1` | chained PASS |
| ASF-facing docs | `validate-founder-docs-no-terminal-v1` | chained PASS |
| AUTO-RUN disabled | `~/.sina/auto-run-disabled-v1.flag` | must exist |
| Commercial law | `FOUNDER_AGENTIC_COMMERCIAL` | AUTO-RUN FORBIDDEN |
| Worker hub policy | `/api/worker-hub/v1` | `no-terminal` link + law cite |
| Architecture moat | `SOURCEA_REFERENCE_ARCHITECTURE` §5.4 | no Terminal clause |

## Validators (ACT)

| Validator | Result |
|-----------|--------|
| validate-founder-hub-only-moat-v1 | PASS |
| validate-hub-copy-no-terminal-v1 | PASS (chained) |
| validate-founder-docs-no-terminal-v1 | PASS (chained) |

## OPEN (VERIFY turn)

- PRIORITY evidence row
- Mark sa-0922 / sa-0947 / sa-0997 consolidated on VERIFY closeout

*End sa-0972 ACT*
