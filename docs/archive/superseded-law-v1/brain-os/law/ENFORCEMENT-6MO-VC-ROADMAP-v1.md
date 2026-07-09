> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# ENFORCEMENT-6MO — VC-GRADE EXECUTION ROADMAP

## SourceA · AI Governance Execution Layer · June–December 2026

> **⚠ SUPERSEDED FOR EXECUTION (2026-06-12):** Week 1–6 engineering rows **void**. **Preserved:** capital tiers · failure modes · fastest W3 · pricing · investor one-liner → `SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md`. Active weeks: weekly plan v1.1 + Annex A.

**Mission:** We make AI execution impossible to bypass governance.
**Format:** Operator + investor grade · table-first · no narrative fluff
**Compiled:** 2026-06-11 · Supersedes: draft money sections in prior plans

---

## ASSUMPTIONS (STATED EXPLICITLY)


| Assumption            | Value                                                                         |
| --------------------- | ----------------------------------------------------------------------------- |
| Receipt system        | Partially exists — RT LIVE receipt + spine_event_id + checksum                |
| Spine event ledger    | Exists — governance-event-spine-v1.jsonl                                      |
| Validator             | Exists — universe invariants PASS; demo enforcement validator NOT YET shipped |
| sourcea_execute_v1.py | Exists — partial commit gate skeleton                                         |
| Demo                  | Kernel shipped (S1–S6 PASS) — **W1 film + Hub button open**                   |
| W3 revenue today      | $0                                                                            |
| Team                  | Solo founder (ASF) + Cursor-based agent fleet                                 |
| Target pilot buyer    | TF-001 (TrustField / regulated MSB) · NF-001 (Noetfield / Copilot governance) |
| Minimum W3            | CAD $2,000 deposit or signed LOI with named organization                      |
| Currency              | CAD unless noted                                                              |
| Exchange rate         | CAD/USD ~0.73                                                                 |


---

## 26-WEEK EXECUTION TABLE


| Wk        | Engineering Deliverable                                                                                                                                                                                                                                                    | Demo Capability                            | Commercial Action                                                                                                                                                               | Money Target (Cumulative)                                     | Risk                                                         | Exit Criteria                                                                |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| **1**     | D1: `governance_demo_policy_v1.json` (rule P-001) · D2: intent fixtures (BLOCK/ALLOW) · Bypass inventory (`BYPASS_INVENTORY_v1.md`)                                                                                                                                        | BLOCK path scripted (not yet executable)   | Identify 10 TF/NF contacts · Draft outreach line: *"We make AI execution impossible to bypass — 15-min pilot call?"*                                                            | $0 · 0 signals                                                | Outreach delayed past week 1 → W3 clock dies                 | D1+D2 logged · 10 targets listed · Outreach sent to ≥5                      |
| **2**     | D3-A: `demo_commit_v1.py` BLOCK path hooked into `gatekeeper_v1` · Invalid intent → exit ≠ 0 · No DONE receipt written                                                                                                                                                     | **BLOCK works in terminal**                | Batch 1 outreach (5 targets) sent · Goal: 1 discovery call booked                                                                                                               | $0 · 1 interested signal                                      | Zero replies to outreach                                     | BLOCK exits ≠ 0 · 1 call scheduled                                           |
| **3**     | D3-B: ALLOW path + `commit-receipt-v1.json` schema (intent · gate_result · law_id · spine_event_id · checksum · timestamp) · Spine row appended on ALLOW                                                                                                                   | **BLOCK + ALLOW in terminal**              | Batch 2 outreach (5 targets) · 1 discovery call completed · Pilot concept described verbally: *"Every AI action gets a receipt — invalid actions blocked before execution"*     | $0 · Pilot interest verbal only                               | Call goes cold after first contact                           | Receipt logged with `spine_event_id` · 1 call done                          |
| **4**     | D4: `~/.sina/demo-enforcement-receipts-v1.jsonl` append-only · No single-file overwrite · Hand-edit breaks checksum on next read                                                                                                                                           | BLOCK + ALLOW + **tamper breaks checksum** | Pilot proposal draft sent to 1 lead · Scope: 90-day Copilot governance · Pricing placeholder: CAD $5K–$10K design partner                                                       | $0–$2K potential (verbal)                                     | Proposal ignored · Tamper not clean                          | Proposal in ≥1 hand · Append-only confirmed                                  |
| **5**     | D5: `validate-demo-enforcement-v1.sh` · PASS on valid ALLOW · exit 1 on hand-edit · Checks: spine_event_id present + checksum matches + ledger row exists                                                                                                                  | **BLOCK + ALLOW + TAMPER FAIL (terminal)** | Follow-up all discovery calls · 1 concept pitch to TF or NF contact                                                                                                             | $0–$2K                                                        | Validator too brittle for live demo                          | Validator exits 1 on tamper in <5s                                           |
| **6**     | D6: `INVESTOR_DEMO_RUNBOOK_v1.md` (speaker notes + terminal commands) · Internal dry run: all 5 beats in <6 min solo                                                                                                                                                       | **Full 5-min terminal demo runnable**      | 2 pilot proposals active · Pricing final: CAD $2K min deposit OR $5K–$10K design partner                                                                                        | $2K–$5K pipeline                                              | Demo >6 min · Terminal errors under pressure                 | Founder runs demo solo <6 min · No notes needed                              |
| **7**     | Hub "Commit" button → calls `sourcea_execute_v1.py --demo-enforcement` · BLOCK/ALLOW/TAMPER accessible from browser · No terminal visible to investor                                                                                                                      | Demo from **browser (no terminal)**        | Video pitch to warm leads · Pilot follow-up · 1 LOI conversation initiated                                                                                                      | $2K–$10K pipeline                                             | Hub button fails · Investor asks for terminal anyway         | Demo runs from browser · All 3 beats                                         |
| **8**     | Demo script frozen (`ENFORCEMENT_DEMO_5MIN.md`) · Adversarial v1: 3 hostile Qs survived (*"What if engineer bypasses?" "Can you fake a receipt?" "What if process crashes?"*) · **Probe pack:** `SOURCEA_ADVERSARIAL_PROBE_PACK_LOCKED_v1.md` §2 (tamper · bypass · crash) | Demo survives **3 adversarial questions**  | Proposal follow-up + pricing negotiation · Target: verbal commit from 1 org                                                                                                     | $5K–$15K pipeline                                             | No follow-up reply · Bypass found in Q&A                     | Script frozen · 3 Qs survived without workaround                             |
| **9**     | Film demo v1 · 2 takes max · TAMPER FAIL must be visible uncut · Runtime <6 min · Stored at `investor/ENFORCEMENT_DEMO_v1.mp4`                                                                                                                                             | **Demo filmed and sendable**               | Video sent to all active prospects (≥5) · Goal: 1 *"we want a proposal"* response                                                                                               | $5K–$25K pipeline                                             | Video quality poor · TAMPER beat not clearly visible         | Video logged · TAMPER FAIL on screen · Can send in <1h                      |
| **10**    | Adversarial hardening v2 · 5 hostile Qs · Bypass scan = 0 results · Partial receipt → validator FAIL on next read · Spine audit clean · **Probe pack:** full §2 matrix + Eval-1b behavioral                                                                                | Demo survives **5 adversarial questions**  | 2+ active pilot conversations · LOI draft sent to warmest lead                                                                                                                  | $10K–$30K pipeline                                            | Bypass found · No LOI response                               | Zero bypasses survive · 1 LOI draft sent                                     |
| **11**    | `validate-enforcement-kernel-v1.sh`: merged universe + closeout + gatekeeper + demo enforcement · Runs in <30s · Investor-runnable                                                                                                                                         | **Investor can run validator themselves**  | Pilot proposal + final pricing sent · CAD $5K design partner OR CAD $2K deposit                                                                                                 | $10K–$40K pipeline                                            | Validator fails on fresh machine                             | Validator <30s · Clean on cold run                                           |
| **12**    | **Phase checkpoint:** W2 bypass inventory = 0 · Receipt validator PASS · Hub button live · FR-003 + 1.10 (Maintainer)                                                                                                                                                      | **Full demo filmable on demand**           | **LOI draft or deposit conversation active with ≥1 org**                                                                                                                        | **$10K–$50K pipeline (1 active close)**                       | No active close · W2 bypass still open → freeze new features | W2 gates all green · ≥1 LOI/deposit actively negotiated                      |
| **13–14** | Receipt JSONL export: `python3 scripts/export-demo-receipts-v1.py` → CSV/JSONL · Makes "controlled transactions" tangible for compliance buyer                                                                                                                               | Demo + **exportable receipt bundle**       | Demo video to 5+ leads · Export API shown in proposal · Target: CAD $2K deposit within this window                                                                              | **$2K–$25K (first deposit target)**                           | No conversion after video · Export too complex               | ≥1 deposit/LOI signed OR deposit conversation in final stage                 |
| **15–16** | RPAA stub (regulated procurement AI governance, TF fallback if Copilot not landing) · 2nd demo scenario scripted                                                                                                                                                           | **2 demo scenarios available**             | LOI negotiation active · Pricing: CAD $5K–$25K pilot OR CAD $2K minimum · Follow-up cadence: every 5 business days                                                              | $2K–$50K (close in progress)                                  | LOI stalls · Single scenario too narrow                      | LOI draft with named org OR deposit received                                 |
| **17–18** | **Scope freeze** — engineering only serves active pilot requirements                                                                                                                                                                                                       | Demo stable · No new features              | **CLOSE W3** · Target: signed LOI, paid deposit, or SOW                                                                                                                         | **W3 PASS: CAD $2K–$25K signed**                              | W3 misses → reassess outreach channel                        | Written deposit / LOI / SOW from named organization                          |
| **19–20** | Pilot support only · Any gaps that block pilot execution fixed same-day                                                                                                                                                                                                    | —                                          | 90-day pilot execution · Document every controlled transaction · Collect: blocked count + receipt export + anonymized compliance quote                                            | $25K–$50K pilot revenue (if SOW) · **ARR trajectory started** | Pilot scope expands uncontrolled                             | ≥10 controlled transactions · Exportable receipt bundle · Client quote secured |
| **21**    | —                                                                                                                                                                                                                                                                          | —                                          | **3-slide seed deck complete** · Slide 1: Problem · Slide 2: Proof (demo + client metric) · Slide 3: Wedge + ask · One-liner: *"If it can bypass, it doesn't exist."*           | $25K–$50K realized + seed pipeline starts                     | Deck polish takes >1 week                                    | Deck sendable in <24h · Logo on slide (anonymized OK)                        |
| **22–23** | —                                                                                                                                                                                                                                                                          | —                                          | **10 investor meetings** · Priority: AI governance/safety thesis VCs · Canadian VCs if TF/NF are MSB · Compliance-focused family offices · Strategic CVCs (banking, healthcare) | $50K–$100K realized + **$500K–$3M IOI pipeline**              | No warm intros · Demo not credible for tier-1                | ≥5 meetings booked · Demo sent to all                                        |
| **24–25** | —                                                                                                                                                                                                                                                                          | —                                          | Pipeline heat · $500K+ verbal interest target · Follow-up: demo + case study + receipt export · 1 term sheet conversation or strong IOI                                         | $100K–$500K+ verbal + **seed close in progress**              | IOI too soft · No follow-through                             | ≥1 strong IOI or term sheet requested                                        |
| **26**    | —                                                                                                                                                                                                                                                                          | —                                          | **Outcome assessment** · Tier A/B/C declared honestly                                                                                                                           | **Target: seed $3M–$10M OR $100M signal credible**            | <10% $100M close in 26 weeks                                 | Tier declared with evidence — no inflation                                   |


---

## 6-MONTH CAPITAL TRAJECTORY SUMMARY

### Month-by-Month Expectations


| Month                   | Engineering State                                             | Commercial State                          | Revenue / Capital                               | Narrative Tier                                        |
| ----------------------- | ------------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------- | ----------------------------------------------------- |
| **Month 1** (Wks 1–4)   | Kernel build · BLOCK/ALLOW in terminal                        | Outreach live · 2–5 conversations started | $0 cash · $0–$5K pipeline signal                | *"Building enforcement kernel"*                       |
| **Month 2** (Wks 5–8)   | Demo hardening · tamper FAIL reliable                         | Proposals sent · 1 LOI conversation       | $0–$5K cash · $5K–$25K pipeline                 | *"Demo is live, tamper fails"*                        |
| **Month 3** (Wks 9–12)  | Demo filmed · adversarial clean · validator investor-runnable | LOI draft active · deposit negotiation    | $0–$10K cash · $10K–$50K pipeline               | *"Demo sent to buyers, LOI in negotiation"*           |
| **Month 4** (Wks 13–16) | Receipt export API · RPAA stub                                | **W3 close (target: CAD $2K–$25K)**       | **$2K–$25K cash · $50K–$100K pipeline**         | *"Paid design partner / pilot signed"*                |
| **Month 5** (Wks 17–20) | Scope freeze · pilot support                                  | Pilot executing · case study in progress  | **$25K–$50K realized · ARR trajectory visible** | *"Client controlled N transactions, zero bypasses"*     |
| **Month 6** (Wks 21–26) | —                                                             | 10 investor meetings · seed raise         | **$3M–$10M seed OR $100M signal pipeline**      | *"Governance infra layer · one logo · enforced demo"* |


### Capital Progression Path

```
Week 1–4:    $0 cash ─── Outreach live ──────────────────► Signal: interest
Week 5–8:    $0 cash ─── Proposals sent ─────────────────► Signal: LOI draft
Week 9–12:   $0–$5K ──── Demo filmed ───────────────────► Signal: deposit negotiation
Week 13–16:  $2K–$25K ── W3 PASS target ────────────────► Milestone: first paid proof
Week 17–20:  $25K–$50K ─ Pilot revenue ─────────────────► Milestone: ARR trajectory
Week 21–24:  Seed round ─ $3M–$10M raise initiated ─────► Milestone: credible narrative
Week 25–26:  $100M sig ─ Term sheet or IOI ─────────────► Outcome: Tier B/C
```

### Credibility Tiers Toward $100M


| Tier                         | Requirements                          | Valuation Range | Probability |
| ---------------------------- | ------------------------------------- | --------------- | ----------- |
| **Seed**                     | W1 filmed + W2 clean + W3 deposit     | $10M–$40M       | 30–40%      |
| **Strong Seed / Early-A**    | Seed + 2nd pilot + export API         | $40M–$100M      | 15–25%      |
| **$100M narrative credible** | Above + tier-1 lead + regulated logo  | $100M–$300M     | 10–15%      |
| **$100M round closed**       | Above + revenue run rate or strategic | $300M+          | <10%        |


---

## CRITICAL PATH BOTTLENECK (ONE ONLY)

> **W3 conversion timeline — not engineering.**

Engineering to W1+W2 takes 10–12 weeks. W3 (first paid signal) requires:

- Week 1: Outreach sent
- Week 2–3: Discovery call
- Week 4–6: Proposal sent
- Week 8–12: LOI negotiation
- Week 13–16: Close

That is a **13–16 week minimum sales cycle** from cold outreach to signed deposit — assuming one conversation works on the first try. If outreach starts week 3 instead of week 1, W3 misses December.

**The bottleneck is not the demo. It is the outreach start date.**

Every week the founder delays W3 outreach = one week less time to recover from a stalled pipeline.

---

## TOP 3 FAILURE MODES

### Failure Mode 1 — W3 Outreach Starts After Demo Is Filmed (Probability: ~50%)

**What happens:** Founder waits for a "perfect demo" before contacting TF/NF. Demo ships week 9. First call is week 10. LOI negotiation is week 16. W3 closes week 22 at best. No time for seed raise by December.

**Why it's fatal:** Investors want a logo *at the time of the meeting* — not a promised pilot. If meetings are weeks 22–23 and W3 closes week 22, the logo is too fresh to be credible.

**Prevention:** W3 outreach starts week 1 using concept alone. Demo follows the first call, not precedes it.

---

### Failure Mode 2 — Demo Bypassed in Investor Q&A (Probability: ~40%)

**What happens:** Investor asks *"What if your engineer writes directly to the file?"* or *"What if the agent spawns without calling gatekeeper?"* — demo crumbles. No second meeting.

**Why it's fatal:** The entire W1 thesis is *"cannot be bypassed."* One bypass answer destroys the category claim.

**Prevention:** Adversarial hardening is mandatory by week 10 — not optional polish. Bypass inventory must reach zero before any investor meeting.

---

### Failure Mode 3 — Scope Creep Reopens Architecture Discussion (Probability: ~50%)

**What happens:** A GPT/Claude/Brain paste introduces "Decision Cloud" or "Object-Centric OS" or Phase 3–10 work. Founder allocates 2–3 weeks to naming or architecture instead of demo + outreach. Clock resets.

**Why it's fatal:** At 5–10% probability regime, every week of non-W3 work reduces the outcome probability proportionally.

**Prevention:** DELETE list is law. Brain enforces gate test before every task: *"Does this increase W1, W2, or W3?"* If no → reject.

---

## FASTEST PATH TO FIRST PAID PILOT (W3)

**Minimum viable W3 close: 4–5 weeks from today if outreach starts immediately.**


| Day           | Action                                                                                                                                                                     | Outcome                      |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| **Day 1**     | Send outreach to 5 TF/NF contacts: *"We make AI execution impossible to bypass governance — 15 min to discuss a Copilot governance pilot?"*                                | 0–2 replies                  |
| **Day 3–5**   | Follow up non-replies with 1-line value: *"Every AI action your Copilot takes would have a receipt. Invalid actions blocked before execution. Exportable for compliance."* | 1 call booked                |
| **Day 7–10**  | Discovery call: present concept + share terminal BLOCK demo (week 2 state is sufficient)                                                                                   | Interest confirmed OR closed |
| **Day 14–21** | Send pilot proposal: 90 days · CAD $2K deposit (minimum) · Scope: Copilot governance enforcement                                                                           | Proposal under review        |
| **Day 28–35** | Follow up · handle objections · push to deposit or LOI                                                                                                                     | **W3 PASS**                  |


**The demo does not need to be filmed for W3.** A terminal demo of BLOCK/ALLOW is sufficient for an initial proposal. The filmed demo is for investor meetings (week 22+), not pilot close.

**If TF-001 and NF-001 both go cold:** Escalate to MSB compliance officers in Canada who have FINTRAC audit exposure. The wedge: *"FINTRAC requires audit trails for automated decisions — we produce cryptographic receipts for every AI action."*

---

## INVESTOR ONE-LINER (USE THIS ONLY)

> *"AI agents are executing actions in enterprise environments with no enforceable governance layer. We are the commit gate — every action has a receipt, invalid actions are blocked before execution, and tampering is detected immediately. One regulated pilot is live. The receipt is the product."*

**Do not say:** Trust OS · Decision Cloud · Agent Platform · 1000-pack · Kernel Company · OS

---

## DELETE FOR 6 MONTHS (ENFORCED)


| Forbidden                                     | Enforcement                                   |
| --------------------------------------------- | --------------------------------------------- |
| Trust OS / Decision Cloud / AWS-for-AI naming | Brain gate rejects any task with these labels |
| Architecture expansion beyond demo surface    | Any task not on W1/W2/W3 path → DELETE        |
| Whitepaper before W3 close                    | Not needed until month 5                      |
| Phases 3–10 SourceA REGISTRY                  | Paused per Q-NEXT-WORK D                      |
| Naming sprint / category debate               | Category sentence is frozen                   |
| Learning loops / digital twin / causal graph  | North star only — not sprint                  |
| $100M close framing to investors pre-W3       | Kills credibility                             |


---

## FINAL RULE

> **Speed > completeness. Proof > narrative. Enforcement > intelligence. Failure detection > optimization.**
>
> Ship the smallest system that cannot lie on camera. Then sell that recording to one regulated buyer until someone pays. Then raise.

---

*Tag: ENFORCEMENT-6MO · VC-GRADE · 2026-06-11 · Money trajectory explicit · Critical path: W3 outreach starts today*