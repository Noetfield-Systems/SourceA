# Evidence Flywheel — ecosystem law (LOCKED)

| | |
|--|--|
| **Version** | `EVIDENCE-FLYWHEEL-1.1-LOCKED` |
| **Locked** | 2026-06-04 (finalized) |
| **Implementation** | `mergepack/EVIDENCE_FACTORY_LOCKED.md` · API v0.4 |
| **Owner** | ASF |
| **Supersedes** | “MergePack = PDF SaaS only” mental model |

---

## One sentence (ecosystem law)

**Utilities generate events. Events become evidence. Evidence builds trust. Trust enables participation. Participation creates distribution. Distribution powers Noetfield.**

---

## Five layers (bottom → top)

| Layer | SKU / system | Primary job | Not primary job |
|-------|----------------|-------------|-----------------|
| **L1** | **MergePack** (+ future utilities) | **Public Evidence Network v1** — capture usage events | Final company / trust pitch |
| **L2** | **RunReceipt** | Vertical evidence + first $ in ops niche | Mass SEO |
| **L3** | **Participation HQ** (v0: 3 lanes) | Distribute via User · Earner · Connector | Full 7-lane OS day one |
| **L4** | **TrustField** | Enterprise trust pilots on proof | Cold SEO entry |
| **L5** | **Noetfield** | Governance & analysis **on** evidence | Acquiring anonymous traffic |

**MergePack definition (locked):** not “PDF tool,” not “SaaS destination” — **Public Evidence Network v1** that also acquires traffic.

**Acquisition** brings people in. **Evidence** is what you keep. Noetfield is worthless without the latter.

---

## Flywheel (ordered)

```text
Traffic
  ↓
Usage Events (merge, form, download, account, referral, payment, retention)
  ↓
Evidence (aggregated, attributable, auditable)
  ↓
Revenue (first $ proves demand)
  ↓
Trust (repeat use, organic arrival, paid referrers)
  ↓
Distribution (Participation v0)
  ↓
TrustField pilots
  ↓
Noetfield (governance product on evidence)
```

**Correction to traffic-only thinking:** 100k users with zero events that matter = zero evidence. Optimize the **event graph**, not vanity MAU.

---

## Event taxonomy (all layers emit)

| Event type | Source (v1) | Evidence use |
|------------|-------------|----------------|
| `merge_completed` | MergePack API | Usage proof |
| `form_pdf_completed` | MergePack API | Usage proof |
| `download` | Client (optional) | Funnel |
| `limit_hit` | API 402 | Upsell signal |
| `payment_completed` | Stripe webhook | Revenue proof |
| `account_created` | Hub / utility (hook) | Account graph |
| `referral_sent` | Hook UI | Distribution seed |
| `referral_converted` | Attributed pay | Distribution proof |
| `session_returned_7d` | Ledger | Retention |
| `feedback_submitted` | Form | Product |
| `pilot_booked` | TrustField | Enterprise |

Store: `event_id`, `ts`, `source`, `type`, `anonymous_id` / `account_id`, `ref_code`, `payload` (minimal), `ip_hash` (if needed).

---

## North-star KPI trio (before scale metrics)

Prove **demand + distribution + trust** together:

| KPI | Proves | MergePack v1 signal |
|-----|--------|---------------------|
| **KPI-1** First paying stranger | Demand | Stripe `checkout.session.completed` not founder card |
| **KPI-2** First referral-attributed payment | Distribution | `?ref=` → paid conversion |
| **KPI-3** First organic user | Trust / reach | No direct invite; attributable UTM/direct |

Only after trio: targets like 10 paid, 100 accounts, 1000 events/week.

---

## Account graph (strategic asset)

PDF margin is **fuel**, not the castle. The castle is **Account Graph** — identities that later carry Participation, TrustField, utilities.

Dropbox pattern (locked analogy):

```text
Utility (merge/form) → Accounts → Refer & earn → Business SKUs → Enterprise (Noetfield)
```

---

## Skeleton vs nervous system (unchanged)

| Skeleton | Nervous system |
|----------|----------------|
| This flywheel order | Pricing, hero tool, bounty %, missions |
| 3 lanes (User, Earner, Connector) | `adaptive_config.json` rules |
| Points ≠ equity; reputation ≠ points | Campaigns / geo focus |

No ML until **100+** active accounts with events. Rule engine only.

---

## Participation: hooks now, HQ later

| Ship now (hooks) | Defer (HQ) |
|------------------|------------|
| `?ref=` attribution + event log | Full dashboard |
| Footer “Invite → 1 mo Pro after 3 paid refs” (manual OK) | Stripe Connect mass payout |
| Email capture / magic-link account (minimal) | 7 lanes, investor gamification |
| Log KPI trio | Token, airdrop, ML routing |

**Engineering gate:** public URL + Stripe (MP-SHIP, MP-PAY) **before** scaling hooks traffic.  
**Strategy gate:** hooks are **not** Participation HQ — do not block hooks on HQ v1.

---

## 90-day execution (frozen scope)

| Window | Focus |
|--------|--------|
| 0–14d | Public MergePack + KPI-1 + event logging v0 |
| 0–30d | RunReceipt KPI-1 + hooks live on MergePack |
| 14–45d | KPI-2 + KPI-3 + 10 paid MergePack |
| 45–90d | Participation HQ v0 (3 lanes) + TrustField pilot conversation |

**Frozen:** 7 lanes, token/airdrop, investor points, adaptive ML, VIRLUX merchant portal.

---

## Implementation (shipped v1.1)

| Piece | Location |
|-------|----------|
| Ledger | SQLite `evidence_events` — `backend/app/evidence.py` |
| KPI | `GET /v1/kpi` |
| Referral | `?ref=` · `GET /v1/referral-code` · Stripe metadata |
| Hooks UI | `ParticipationHooks.tsx` · `EvidenceInit.tsx` |
| Hooks lock | `PARTICIPATION_HOOKS_LOCKED_v1.md` |

**System equation (only loop that matters):**

```text
Utilities → Events → Evidence → Revenue → Trust → Distribution → Noetfield
```

---

## Related locks

| Doc | Role |
|-----|------|
| `ACQUISITION_STACK_LOCKED_v1.md` | Layer stack + MergePack role |
| `PARTICIPATION_HOOKS_LOCKED_v1.md` | Hooks ≠ HQ |
| `MERGEPACK_SUITE_LOCKED_v1.md` | Shipped utilities (merge + FormToPDF) |
| `mergepack/EVIDENCE_FACTORY_LOCKED.md` | Repo-level evidence lock |
| `PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md` | RunReceipt factory P0 |
| `mergepack/docs/_TOPICS/08-deploy-ready/DEPLOY_READY.md` | Deploy |

---

**LOCKED.**
