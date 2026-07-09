# Premium Model Firewall — Routing Policy (LOCKED v1)

**Version:** 1.0.0 LOCKED  
**Saved at:** 2026-07-05T12:35:00Z  
**Authority:** SourceA delivery factory  
**Parent:** `docs/commercial/AGENTIC_COST_GOVERNANCE_AUDIT_KIT_LOCKED_v1.md`  
**Status:** Template — customize per client at audit time

---

## Pricing disclaimer

> Model names and rates below are **examples only**. Final routing uses **model class** (`tier1_cheap`, `tier2_standard`, `tier3_premium`) with `pricing_source: audit_time_live_lookup`. No guaranteed savings. No production enforcement without signed pilot scope.

---

## Layer 1 — Default (tier1_cheap)

| Field | Value |
|-------|-------|
| **Model class** | `tier1_cheap` |
| **Example model** | [client-defined cheap tier — e.g., org standard model] |
| **Usage** | Standard tasks · high volume · testing |
| **Rate** | `[audit_time_rate]` USD per 1K tokens |
| **Approval** | None required |
| **Budget cap** | Per-workflow limit (set at discovery) |

---

## Layer 2 — Escalation (tier2_standard)

| Field | Value |
|-------|-------|
| **Model class** | `tier2_standard` |
| **Example model** | [client-defined standard premium — e.g., analysis-tier model] |
| **Triggers** | `task_type` = analysis OR `tokens_projected` > threshold OR customer-facing |
| **Rate** | `[audit_time_rate]` USD per 1K tokens |
| **Approval** | Manager — async, within 24h |
| **Reason field** | Mandatory |

---

## Layer 3 — Premium / urgent (tier3_premium)

| Field | Value |
|-------|-------|
| **Model class** | `tier3_premium` |
| **Example model** | [client-defined high-capability model] |
| **Triggers** | Strategic · customer-critical · time-sensitive · high business impact |
| **Rate** | `[audit_time_rate]` USD per 1K tokens |
| **Approval** | VP or department head — within 4h |
| **Business case** | Mandatory |

---

## Policy enforcement

- Check task metadata before API call
- Log all escalations to `data/agentic-cost-governance-audit-log-v1.json`
- Track approval chain with immutable entries
- Client controls implementation environment — SourceA provides policy only until pilot is signed
