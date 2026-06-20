# Agentic W3 Outreach Workflow Spec (v1)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** Gap-fill — replaces manual-founder default in `investor/ENFORCEMENT_OUTREACH_v1.md`  
**Law:** `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` · P0 portfolio draft Pillar A  
**Precedent:** Apollo (lists) · HubSpot (sequences) · n8n (glue) · SourceA (gate + receipt)  
**6mo rating:** **P0-W3** — use now

---

## Principle

Founder does **not** send emails or schedule calls manually. Agents:

1. Build target list from template (ENFORCEMENT_OUTREACH §Who to call)  
2. Draft personalized outreach  
3. Gate through governance check (no false claims · LAG labels)  
4. Queue send via commercial tool  
5. Append spine receipt per batch  
6. Escalate **final contact** to founder hub card when reply = hot  

---

## Workflow (n8n-class)

```text
TRIGGER (cron 09:00 · Mon/Wed/Fri)
  → READ targets from CRM CSV / Apollo export
  → FOR each target (max 5/day):
       LLM draft from ENFORCEMENT_OUTREACH email template
       VALIDATE: no "24/7 live" · no "$100M" · demo scope honest
       QUEUE in HubSpot/Apollo sequence
       APPEND spine: {event: outbound_queued, target_hash, batch_id}
  → NOTIFY hub: "5 queued — Approve send batch" (one tap)
  → ON reply webhook:
       CLASSIFY hot/warm/cold
       HOT → hub card "Final contact — [org]" for ASF
```

---

## Evidence row (Pillar B)

```yaml
proposal_id: PROP-2026-06-12-W3-OUTREACH
precedent_companies:
  - name: Apollo
    product: Sequences
    pattern: list → sequence → track replies
    url: https://www.apollo.io
  - name: HubSpot
    product: Workflows
    pattern: enroll → email → pipeline stage
    url: https://www.hubspot.com
  - name: n8n
    product: Workflows
    pattern: cron → HTTP → branch
    url: https://n8n.io
our_mapping: n8n workflow W3-OUTREACH-001 · NF/TF wedge
commercial_outcome: W3
gate_test: pay
verdict: accept
```

---

## Minimum bar (Week 2)

| Check | PASS |
|-------|------|
| 5 targets identified | names in private CSV |
| 1 batch drafted | agent-generated |
| 1 spine row | outbound_queued event |
| 0 manual founder sends | hub audit |

---

## What founder sees (hub only)

- **Approve outbound batch** — one tap  
- **Final contact card** — when prospect replies positive  
- **W3 progress** — conversations logged · LOI status  

---

*End spec — Worker implements n8n map; Maintainer adds hub card when FR-003 allows*
