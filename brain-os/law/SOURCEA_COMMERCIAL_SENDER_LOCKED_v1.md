# SourceA Commercial Sender — LOCKED v1.1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-15  
**Authority:** Portfolio SSOT §9 separation — SourceA lane only · CASL (Canada)  
**Law:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` · `SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md`

---

## Rule

**Never send Asset B / Buyer 1 / SW1 outreach from a personal Gmail.** Use the locked SourceA sender below.

| Layer | From address | Sign-off |
|-------|--------------|----------|
| **SourceA** (Buyer 1 · Asset B · SW1 · chain tools) | **hello@sourcea.com** | **Founder name** + SourceA line |
| Noetfield (NW1 · compliance) | operations@noetfield.com | Noetfield Systems Inc. |
| TrustField (MSB · regulated) | hello@trustfield.ca | TrustField Technologies |

**Reply-to:** hello@sourcea.com

**CASL (Canada):** identified sender (company + founder name) · one relevant prospect at a time · **opt-out line required** on commercial email.

---

## Signature block (AB1 — paste verbatim)

```text
—
Sina Kazemnezhad
SourceA · governed agentic automation
hello@sourcea.com
https://sourcea.com

Reply "stop" and I won't follow up.
```

Override founder name: `SOURCEA_FOUNDER_NAME` env var. **Do not include:** personal Gmail · internal SKU codes · runbook jargon.

---

## A/B variants (AB1)

| Variant | Subject | When |
|---------|---------|------|
| **polished_proof_led** (default) | Can you prove what your agents executed last night? | First sends |
| **short_punchy** | Receipts for your agent loops? | A/B after a few in flight |

`python3 scripts/send_ab1_single_v1.py --to … --name Alex [--variant polished_proof_led|short_punchy]`

**Law:** `--name` required — blank `Hi ,` reads like a blast.

---

## Machine

| Lane | Script | Pack dir |
|------|--------|----------|
| Asset B AB1 | `scripts/send_ab1_single_v1.py` | `~/.sina/outbound/ab1-send-001/` |
| NW1 | `scripts/send_nw1_single_v1.py` | `~/.sina/outbound/nw1-send-001/` |

Templates: `~/.sina/governed-agentic-automation-email-templates-v1.json` · refresh `governed_agentic_automation_offer_v1.py --pack`

---

**End LOCKED v1.1**
