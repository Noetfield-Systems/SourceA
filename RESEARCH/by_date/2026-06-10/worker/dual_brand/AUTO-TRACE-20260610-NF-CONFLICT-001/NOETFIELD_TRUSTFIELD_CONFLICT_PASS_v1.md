
**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
---
agent_tag: AGENT-AUTO-MONO
written_at: 2026-06-10
author: cursor-auto-mono
type: conflict_pass
trace_id: AUTO-TRACE-20260610-NF-CONFLICT-001
execution_authority: false
---

# Noetfield vs TrustField — conflict pass v1

**Task:** `noetfield/os/plan.json` next_tasks[0]  
**Sources read (no edits):** Noetfield governance plane · TrustField SOT · `system_registry.json` · Source B §5–6  
**Status:** Analysis only — not LOCKED until founder orders lock

---

## Public-safe joint line (unchanged)

> Noetfield defines governance and trust requirements for AI-enabled financial programs. TrustField Technologies delivers RPAA-aligned readiness and partner execution in Canada.

---

## Conflict matrix

| # | Domain | Noetfield spec / corpus | TrustField delivery SOT | Conflict? | Resolution | Owner |
|---|--------|-------------------------|-------------------------|-----------|------------|-------|
| 1 | **Brand / entity** | Separate governance company; not PSP (`NOETFIELD_GOVERNANCE_PLANE_LOCKED_v1.md`) | "Noetfield … are **not TrustField**" — no brand merge (`TRUSTFIELD_SOURCE_OF_TRUTH.md` Part I) | No | Two brands; explicit handoff in deals | Founder |
| 2 | **Product stage** | `docs_only` · 0 `.py` · spec corpus (`system_registry.json`) | `active_delivery` · trustfield.ca · Phase A pilots | Narrative only | Noetfield = before go-live spec; TrustField = commercial now | Brain registry |
| 3 | **Registry relationship** | Founder intent: Noetfield parent governance (`MEMORY.md`) | `peer_ecosystem_company` · `not_subordinate_to_noetfield: true` | **YES — OPEN** | Requires `SourceA/NOETFIELD_TRUSTFIELD_RELATIONSHIP_LOCKED_v1.md` + registry notice | **ASF only** |
| 4 | **Revenue / invoicing** | Considerations: contracts via TrustField until Noetfield entity exists | Phase A pilot $6K setup; commercial now | No | Invoice through TrustField; Noetfield = spec/license later | Founder |
| 5 | **PSP / custody claims** | Pre-execution gate; no holding funds | Does not hold/transmit funds today; RPAA path | No | Noetfield governs policy; TrustField delivers readiness/pilot | Both |
| 6 | **“Governance software” wording** | MVP pillars: audit ledger, policy gate (design) | Delivers "governance software" in Phase A pilots | Soft overlap | Noetfield = design/requirements; TrustField = deployed pilot artifacts | Marketing |
| 7 | **Mono spine :8000** | Must not merge into Runtime (`governance plane` + Source B C9) | External repo; not mono spine | No | Standalone greenfield for future Noetfield API | Worker when activated |
| 8 | **Canada AI narrative** | Trust pillar / board evidence | Opportunity / procurement / pilots | No | Noetfield lead trust story; TrustField lead SME adoption | Both |
| 9 | **Source B C5** | Cross-reference in `noetfield/corpus/` | Separate external company | Resolved in Source B | Do not re-open without ASF | ASF |
| 10 | **Engineering freeze** | Spec-only sprint | No new features until 3 demos (TrustField SOT) | No | TrustField commercial gate independent of Noetfield docs | TrustField founder |

---

## Actions taken

- This document satisfies plan task #1 (conflict listing).
- **Not done (out of scope):** edit TrustField repo, change `system_registry.json`, create SourceA relationship LOCKED doc.

---

## Next (plan.json)

1. ~~List conflicts~~ → **done** (this file)
2. **Remaining:** Phase 1B scaffold checklist (standalone API, not `:8000` route)

---

*End conflict pass v1*
