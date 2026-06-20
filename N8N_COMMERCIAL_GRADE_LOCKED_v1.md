# n8n Commercial Grade — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-15  
**Authority:** ASF — sell outcomes + receipts, not “automation PASS”  
**Law:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` · `N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md` · `SOURCEA_ASSET_B_CONTROLLED_AGENTIC_AUTOMATION_LOCKED_v1.md` (DFY SKUs)  
**Engine:** `scripts/n8n_commercial_grade_v1.py` · receipt `~/.sina/n8n-commercial-grade-v1.json`

---

## Rule

n8n is **glue**. Revenue SKUs are **outcome + receipt** bundles. Founder sells **SKU name + weekly proof export** — never “we use n8n.”

---

## Sellable SKUs (client-facing: **Mac Guard**)

| SKU | Product | Setup | MRR | Buyer |
|-----|---------|-------|-----|-------|
| **SKU-OPS-002** | Ops Health Audit (lead) | $750 | — | Raising · diligence · try before subscribe |
| **SKU-SOLO-001** | Mac Guard Solo | $0 | $99/mo | Solo Cursor power user |
| **SKU-OPS-001** | Mac Guard Agency | $500 | $299/mo | Agencies · white-label weekly report |
| **SKU-SIG-001** | Signal Lane | $299 | $79/mo | SaaS · local telemetry |

**Asset B DFY (fastest cash — separate invoice ladder):** `SOURCEA_ASSET_B_CONTROLLED_AGENTIC_AUTOMATION_LOCKED_v1.md` — SKU-DFY-001 · SKU-RET-001 · SKU-COMBO-001.

**W3 tie-in:** first **$750 audit** or **$99 Solo month** = economic signal per portfolio SSOT · **AB1** = DFY ≥ $3K or retainer ≥ $2K/mo.

**Deprecated hero (do not pitch):** $2,500 + $499/mo — not ; replaced by ladder above.

---

## Client-facing assets (send these)

| Asset | Path |
|-------|------|
| Proposal | `~/.sina/n8n-commercial-client-sow-v1.html` |
| Weekly report | `~/.sina/n8n-commercial-client-weekly-v1.html` |
| One-pager | `~/.sina/n8n-commercial-client-one-pager-v1.html` |

Print → PDF. No SKU codes, no raw JSON, no internal jargon in outbound.

---

## Commercial-ready gate (machine)

PASS when all true:

1. Tier 0 + Tier 1 validators PASS  
2. WF8 `wf-mac-health-cooldown-v1` active in n8n DB  
3. `cooldown.jsonl` + `tier0-pass.json` + `tier1-pass.json` logged  
4. `n8n-commercial-grade-v1.json` → `commercial_ready: true`  
5. N8N Integration **Export commercial pack** produces `n8n-commercial-sales-pack-v1.json`

Validator: `bash scripts/validate-n8n-commercial-grade-v1.sh`

---

## Founder sales line

> **Mac Guard** — your Mac stays cool during Cursor agent work; every week you get a one-page report you can forward. Start with a $750 audit or $99/mo Solo. We fix red; you don't debug logs.

---

## Void (do not put on invoice)

- “Sina Command hub” · “Prompt feed” · “n8n tier PASS” as hero · hub :13020 daily
