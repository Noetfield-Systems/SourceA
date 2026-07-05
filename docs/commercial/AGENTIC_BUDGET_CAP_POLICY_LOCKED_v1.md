# Agentic Budget Cap Policy (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-07-05T12:35:00Z  
**Authority:** SourceA delivery factory  
**Parent:** `docs/commercial/AGENTIC_COST_GOVERNANCE_AUDIT_KIT_LOCKED_v1.md`  
**Status:** Template — caps set at discovery, not preset

---

## Pricing disclaimer

> All dollar amounts are **placeholders** set during audit discovery. No guaranteed spend outcomes. Hard stops apply only after client approves pilot policy.

---

## Cap hierarchy

| Level | Placeholder | Set at |
|-------|-------------|--------|
| Org-wide monthly | `$[org_monthly_cap]` | Discovery |
| Per-team | `$[team_cap]` | Discovery |
| Per-workflow | `$[workflow_cap]` | Discovery |
| Per-tool | `$[tool_cap]` | Discovery |

---

## Enforcement flow

1. **Alert at 70%** — email team lead  
2. **Warning at 90%** — manager approval required for new Tier 2+ calls  
3. **Hard stop at 100%** — `429 Too Many Requests` + CFO escalation  

Each API call checks: `(current_spend + projected_call_cost) < cap`

---

## Escalation workflow

Team lead → Manager → CFO (if org cap exceeded or exception requested)

---

## Reporting

- Daily spend snapshot (email)
- Weekly summary to finance contact
- Monthly report in final audit deliverable
