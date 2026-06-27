# SourceA Revenue Engine — outreach templates (LOCKED v1)

**Saved at:** 2026-06-24T17:00:00Z  
**Authority:** `docs/SOURCEA_REVENUE_ENGINE_V1_LOCKED_v1.md`  
**CRM SSOT:** `data/sourcea-revenue-engine-crm-pipeline-v1.json`  
**Sender law:** `brain-os/law/SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` — **hello@sourcea.app** only · CASL opt-out required

---

## Links (paste in every first touch)

| Asset | URL |
|-------|-----|
| PureFlow case study | https://sourcea.app/sourcea/case-studies/pureflow |
| 48h offer | https://sourcea.app/sourcea/offer |
| Live proof (PureFlow) | https://pureflow.sourcea.app/ |
| Book demo | https://cal.com/sourcea/proof-demo |

**Voice:** outcomes first — more contracts, documented service, faster close. No “deterministic runtime” in cold outreach.

**Signature (email — paste verbatim):**

```text
—
Sina Kazemnezhad
SourceA · proof-backed business systems
hello@sourcea.app
https://sourcea.app

Reply "stop" and I won't follow up.
```

---

## 1. Warm network — DM or email

**Template ID:** `warm_network_dm`  
**Segment:** warm_network · **SKU:** 48h acquisition

**Subject (email):** Quick proof — built a full acquisition system in 48h

```text
Hi [First name],

I shipped something I think you'll find useful — a live pool-service acquisition system with post-visit reports homeowners actually keep (not just a landing page).

Case study (what we built + why it closes deals):
https://sourcea.app/sourcea/case-studies/pureflow

Live site:
https://pureflow.sourcea.app/

If you or a client need something similar — offer, intake, and proof in ~48 hours — the package is here:
https://sourcea.app/sourcea/offer

Worth a 15-min look? https://cal.com/sourcea/proof-demo

[Signature]
```

---

## 2. Service operator — email

**Template ID:** `service_operator_email`  
**Segment:** service_operator (pool, cleaning, maintenance, trades)

**Subject:** 3 leaks I see in [pool/cleaning] businesses losing contracts

```text
Hi [First name],

Most [pool/cleaning/maintenance] operators I talk to lose bids for the same three reasons:

1. Prospects can't see professional pricing and tiers online
2. Homeowners aren't sure the visit actually happened
3. Nothing documented to support renewals or referrals

We built a working fix for a Vancouver pool operator — live site + a report after every visit (chemistry, actions, photo, next date). Full case study:
https://sourcea.app/sourcea/case-studies/pureflow

If that's relevant for [Company], we deploy similar proof-backed systems in 48 hours — setup typically $1,500–$5,000:
https://sourcea.app/sourcea/offer

Open to a short call this week?

[Signature]
```

---

## 3. Agency / AI consultant — email or LinkedIn

**Template ID:** `agency_consultant_email`  
**Segment:** agency_consultant

**Subject:** Client deliverable with proof attached (not another deck)

```text
Hi [First name],

Agencies I work with are tired of shipping client work without a proof artifact the buyer can forward to their boss.

We deploy proof-backed acquisition systems — positioned offer, intake, and a report/receipt pattern clients can verify. Example we just shipped:
https://sourcea.app/sourcea/case-studies/pureflow

Package for your next client or internal offer:
https://sourcea.app/sourcea/offer

Happy to walk through the live proof on a quick demo:
https://cal.com/sourcea/proof-demo

[Signature]
```

---

## 4. Follow-up — no reply (day 5–7)

**Template ID:** `follow_up_no_reply`

**Subject:** Re: [original subject]

```text
Hi [First name],

Bumping once — the PureFlow case study is the shortest way to see what "proof-backed acquisition" means in practice:
https://sourcea.app/sourcea/case-studies/pureflow

If timing's wrong, no worries. If useful, book here: https://cal.com/sourcea/proof-demo

[Signature]
```

---

## 5. Meeting confirm

**Template ID:** `meeting_confirm`

```text
Hi [First name],

Confirmed — [Day] at [Time] [TZ].

I'll show:
• Live PureFlow site + sample service report
• How the 48h package maps to [their business / client]
• Scope and fixed pricing band on discovery

Case study to skim before call (optional):
https://sourcea.app/sourcea/case-studies/pureflow

[Signature]
```

---

## 6. Proposal cover email

**Template ID:** `proposal_cover_email`  
**Attach:** scoped SOW or one-pager · deposit terms

**Subject:** Proposal — proof-backed acquisition system for [Company]

```text
Hi [First name],

As discussed — attached is the scoped proposal for [SKU name].

Summary:
• Deliverables: [offer + intake + trust report pattern + handoff]
• Timeline: 48-hour core path · [full polish date if scoped]
• Investment: CAD $[amount] setup [+ $[amount]/mo if retainer]
• Deposit: [50% / 100% per SKU]

Live reference build:
https://pureflow.sourcea.app/

Reply with questions or a go — I'll send invoice and onboarding checklist on confirmation.

[Signature]
```

---

## 7. Testimonial request (post-delivery)

**Template ID:** `testimonial_request`

**Subject:** Quick favour — 2 sentences on what shipped?

```text
Hi [First name],

Now that [deliverable] is live — would you mind 2–3 sentences on what changed for you (contracts, time saved, client reactions)?

We may use it as an anonymized win on our case study page — I'll send a draft for approval first.

Optional: permission to name [Company] with logo.

Thanks,
[Signature]
```

---

## 8. Referral ask (post-win)

**Template ID:** `referral_ask`

```text
Hi [First name],

Glad [project] is working. If you know one [agency owner / operator] who'd benefit from the same proof-backed setup, I'm happy to offer them a priority scope slot this month.

They can start here: https://sourcea.app/sourcea/offer

Thanks for thinking of us,
[Signature]
```

---

## CRM logging

After each send, log on disk:

```bash
python3 scripts/sourcea_revenue_engine_crm_v1.py init
python3 scripts/sourcea_revenue_engine_crm_v1.py add --id RE-004 --name "Alex" --segment agency_consultant --channel email
python3 scripts/sourcea_revenue_engine_crm_v1.py touch --id RE-004 --stage outreach_sent --template agency_consultant_email --note "Sent with PureFlow link"
python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json
```

**Runtime file:** `~/.sina/sourcea-revenue-engine-crm-v1.json`

---

*Revenue Engine outreach v1 · June 2026*
