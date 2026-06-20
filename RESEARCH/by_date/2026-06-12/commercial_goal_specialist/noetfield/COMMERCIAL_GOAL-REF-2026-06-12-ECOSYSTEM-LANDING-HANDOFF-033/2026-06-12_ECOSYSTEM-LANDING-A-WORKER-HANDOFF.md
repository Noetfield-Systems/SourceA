# Ecosystem Landing — Option A · Worker Handoff (deploy)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `COMMERCIAL_GOAL-REF-2026-06-12-ECOSYSTEM-LANDING-A-033`  
**parent:** `ECOSYSTEM-LANDING-SPEC-032` · `INFRA-FUNDRAISING-033`  
**execution_authority:** false · **build in:** Mandatory Noetfield chat **or** TrustField chat — **not** SourceA Worker

---

## Deliverable

| File | Purpose |
|------|---------|
| `2026-06-12_ECOSYSTEM-LANDING-A-FULL.html` | **Ship this** — self-contained landing · dark theme · trace demo block |
| `partner-attachments/sample_receipt_redacted.json` | DD attachment |
| `partner-attachments/2026-06-10_ARCHITECTURE_DIAGRAM.md` | Optional /architecture subpage |

---

## Recommended host (pick one)

| Host | Path | Why |
|------|------|-----|
| **noetfield.com** | `/ecosystem` | Copilot buyer funnel · NF-001 CTA primary |
| **trustfield.ca** | `/platform` | MSB/regulatory audience · TF legal entity |
| Neutral (later) | `sina.ai/ecosystem` | When domain ready |

**ASF PICK required** — default recommendation: **noetfield.com/ecosystem** (NF wedge first per W3-NF lane).

---

## Deploy steps (Noetfield or TrustField worker)

1. Copy `2026-06-12_ECOSYSTEM-LANDING-A-FULL.html` → site repo as `ecosystem/index.html` (or `platform/index.html`).
2. **When S7 video exists:** replace `#demo-video` placeholder with `<video controls poster="…"><source src="/assets/demo-w1.mp4" /></video>`.
3. Wire CTAs:
   - NF-001 → existing `/demo` or Calendly · tracker `booked_by: agentic`
   - TF-001 → `trustfield.ca/pilot`
   - Architecture pack → `partnerships@trustfield.ca` or hub form
4. Add nav link: **Ecosystem** (one word — not “TrustField + Noetfield”).
5. Verify mobile · Lighthouse · no merged pricing checkout.

---

## Agentic CTA (mandatory)

Founder **never** receives raw form email.

```text
Visitor → lane CTA → agentic scheduler / hub Track
→ outreach tracker row sent_by:agent OR booked_by:agentic
→ BUYER_DEBRIEF_TEMPLATE after demo
```

Skill: `@sina-agentic-commercial`

---

## Honest copy rules (do not change)

- **Headline:** We make AI execution impossible to bypass governance.
- **Three layers labeled** — never one merged product paragraph.
- **Badges:** Pre-revenue · design-partner pilots · validator PASS (not SOC2).
- **No** factory 1000-pack metrics in hero.

---

## Post-ship checklist

- [ ] Page live at chosen URL
- [ ] S7 video embedded (when ready)
- [ ] CTAs hit real booking flows
- [ ] Link in seed deck + PR draft (`PR-LAUNCH-032`)
- [ ] Hub Track tab shows first agentic booking row

---

## Verify locally

```bash
open ~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-12_ECOSYSTEM-LANDING-A-FULL.html
```

**execution_authority:** false
