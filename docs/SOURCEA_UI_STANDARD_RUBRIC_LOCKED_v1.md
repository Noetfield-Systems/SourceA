# SourceA UI Standard Rubric — LOCKED v1

**Saved:** 2026-06-25T05:35:00Z  
**Version:** 1.0.0 — LOCKED  
**Authority:** Advisor + Brain stranger-chat incident (2026-06-25)  
**Positioning SSOT:** `docs/SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md` · `SourceA-landing/green-unified/data/sourcea-positioning-v1.json`  
**Machine companion (planned):** `scripts/validate-sourcea-ui-mechanical-v1.sh` · `data/sourcea-ui-mechanical-gate-v1.json`

---

## One law

> **A validator can stop your UI from being broken; only a human can tell you if it is good.**

This rubric splits every pre-ship UI decision into two halves:

| Half | Grader | Ship rule |
|------|--------|-----------|
| **A — Mechanical** | Machine | **BLOCK** publish on FAIL |
| **B — Experiential** | Human (founder / stranger) | **FLAG** only — never auto-PASS desire |

Do **not** build an “online UI critic” that claims to judge taste, conviction, or willingness to pay. That is fake progress — the same failure mode as green dashboards with zero buyers.

---

## Fixed bar (what we grade against)

### Canonical one-liner (LOCKED)

**SourceA is an AI execution platform powered by Forge — it runs real builds, automations, agent workflows, and governed development pipelines for founders and agencies.**

Supporting law: **Proof is built in; it is not the whole product.**

### Competitor / reference class (taste signal, not copy-paste)

Use these as **design bar**, not feature parity:

| Reference | Steal | Do not steal |
|-----------|-------|--------------|
| **Linear** | Calm density · chrome recedes · max ~7 primary nav items · one icon language · product UI as hero | Their issue-tracker category |
| **Vercel** | Workflow-ordered nav · context switcher · fast hero · deploy proof visible | Generic “developer platform” vagueness |
| **Cursor** | Tool-inside-workflow story · bounded mission prompts | Positioning SourceA as “just an IDE” |
| **Lovable / v0** | Instant try · living product screenshot · low friction first action | Chat-only with no execution spine |
| **Devin-class agents** | Autonomy narrative when honest | Overclaiming autonomy without gates |

**SourceA differentiation on the page:** execution desk (Forge Terminal) + governed run + proof as feature — not proof-as-product, not chat theater.

---

## Part A — Mechanical rubric (machine-gradable)

**Verdict:** PASS / BLOCK per check. Any BLOCK = no publish.

### A1 — Positioning consistency (highest ROI)

The page must not fight Brain or the locked one-liner.

| ID | Check | Method | BLOCK if |
|----|-------|--------|----------|
| A1.1 | One-liner present on commercial surfaces | grep / JSON SSOT | Primary hero/footer sells “proof records” or “verification software” as the product |
| A1.2 | Forbidden primary phrases | denylist scan | Leading copy contains (primary pitch): `ship AI work clients can verify`, `VERIFY from receipts` as hero, `proof-backed` as first noun, `audit trail software`, `records product` |
| A1.3 | Brain ↔ page alignment | paired scan | `sourcea-chatbot.js` greet/chips/placeholder contradict `sourcea-positioning-v1.json` |
| A1.4 | Brain worker alignment | API smoke | `validate-sourcea-brain-chat-v1.sh` FAIL on what-is / IDE / records recovery |
| A1.5 | Forge public surfaces | grep forge/* | Footer/CTA still proof-first after positioning lock |

**SSOT denylist (machine):** extend `data/sourcea-ui-mechanical-gate-v1.json` from positioning doc §What SourceA is NOT.

### A2 — Layout & responsive regression

| ID | Check | Method | BLOCK if |
|----|-------|--------|----------|
| A2.1 | Brain mobile header | CSS invariant + live width probe | `.sa-brain-head-brand` computed width &lt; 120px at 375–480px viewport |
| A2.2 | Brain panel opens | Playwright / CDP | FAB click → panel visible, composer reachable |
| A2.3 | Offline false positive | status GET + UI | Worker `openrouter_ready: true` but panel stuck offline &gt; 10s |
| A2.4 | Touch targets | CSS min-height | Primary chips / send &lt; 42px on mobile sheet |
| A2.5 | No horizontal scroll | viewport test | `document.documentElement.scrollWidth` &gt; viewport on key pages |

**Incident proof:** 2026-06-25 — `.sa-brain-handle { width: 100% }` inside flex row crushed brand to 32px. **Fixed** in `sourcea.css`; **A2.1** prevents recurrence.

### A3 — Token, link, and API integrity

| ID | Check | Method | BLOCK if |
|----|-------|--------|----------|
| A3.1 | Unreplaced placeholders | grep | `{ENTITY}`, `{FOUNDER}`, `{{`, `TODO:`, `lorem ipsum` in shipped HTML/JS |
| A3.2 | JSON endpoints | curl Content-Type | `/sourcea/data/*.json` returns `text/html` or 404 on publish URLs |
| A3.3 | Brain API route | curl | Config `api_worker_url` unreachable or CORS broken from `sourcea.app` origin |
| A3.4 | Dead chips / CTAs | link crawl (bounded) | Brain chips 404; primary CTA `href="#"` or mailto poison `hello@sourcea.com` |
| A3.5 | Asset 200 | HEAD key assets | `sourcea.css`, `sourcea-chatbot.js`, `boot-proof.json` not 200 on production |

### A4 — Copy gates (already on disk — wire, do not duplicate logic)

| ID | Gate | Script | Role in UI rubric |
|----|------|--------|-------------------|
| A4.1 | Commercial copy audience | `validate-landing-commercial-copy-v1.sh` | Blocks founder-internal voice on buyer pages |
| A4.2 | Copy depth / padding | `validate-landing-copy-depth-v1.sh` | Blocks padded case-study bloat |
| A4.3 | UI downgrade guard | `validate-ui-upgrade-no-downgrade-v1.sh` | Blocks CSS/JS regression vs baseline ledger |
| A4.4 | Brain landing E2E | `validate-sourcea-brain-landing-e2e-v1.sh` | Blocks chatbot mount regressions |

### A5 — Leak & trust strip (public surfaces)

| ID | Check | BLOCK if |
|----|-------|----------|
| A5.1 | Internal jargon on landing | OpenRouter, PASS/BLOCK, `sourcea-boot`, INCIDENT-, factory_now on public HTML |
| A5.2 | Fake metrics | Counts without disk receipt path cited |
| A5.3 | Noetfield leak on SourceA buyer pages | Wrong parent brand in hero |

**Existing SSOT:** `data/sourcea-landing-client-voice-v1.json` · `landing-commercial-copy-audience-v1.json`

### A6 — Chip / navigation behavior (Brain)

| ID | Check | BLOCK if |
|----|-------|----------|
| A6.1 | Try Forge Terminal chip | Must stay in chat (send message), not hard-navigate away without user intent |
| A6.2 | Pricing chip | Must not dump stranger on pricing page before value exchange in chat |
| A6.3 | Book a call | `cal.com/sourcea/proof-demo` resolves |

**Incident proof:** 2026-06-25 — chips navigated away from conversation; **fixed** to in-chat prompts.

---

## Part B — Experiential rubric (human-gradable)

**Verdict per row:** PASS / FAIL / FLAG (needs another stranger). **No machine auto-PASS.**

Run this **before distribution**, not after building another validator.

### B1 — Stranger conversation script (15 minutes)

Open `https://sourcea.app/sourcea/forge/` (or current hero URL). Open Brain. **Do not coach the tester.**

| # | Tester says | PASS if | FAIL examples (from incident) |
|---|-------------|---------|-------------------------------|
| B1.1 | “What is SourceA?” | One-line execution answer in &lt; 10s | Generic blob; proof-first; no Forge |
| B1.2 | “Do you have IDE cloud?” | Yes → Forge Terminal + browser try | Flat “No” |
| B1.3 | “Give me 3 exact examples for my agency” | Three concrete workflows | Abstract features; no verbs |
| B1.4 | “You just give me records??” | Acknowledge + reframe execution | Defensive; doubles down on records |
| B1.5 | “Why would I pay $1,500+?” | Value before price; scope-dependent | Price first; no outcome |

**Recorder:** founder notes confusion verbatim — that text becomes the next mechanical denylist candidate.

### B2 — First-impression scan (60 seconds)

| # | Question | PASS signal |
|---|----------|-------------|
| B2.1 | What does this company do? | “Runs AI work / execution platform” — not “proof company” |
| B2.2 | What can I try without a call? | Names Forge Terminal or demo URL unprompted |
| B2.3 | Does anything feel broken? | No layout crush, no “offline” distrust, no contradictory subcopy |
| B2.4 | Does anything feel cheap? | Typography, spacing, icon consistency — subjective **human only** |
| B2.5 | Would you book or bounce? | Honest — **no validator score** |

### B3 — Competitor sniff test

Show tester Linear / Vercel / Cursor marketing for 30s, then SourceA.

| # | Question | Use |
|---|----------|-----|
| B3.1 | Which feels more “real product”? | Calibrates chrome density and hero discipline |
| B3.2 | Which would you trust with client work? | Agency buyer signal |
| B3.3 | What is SourceA missing on first glance? | Backlog for **product**, not more gates |

### B4 — Hub / internal UI (separate bar)

Public landing rubric does **not** subsume Hub. Hub uses `docs/HUB_UI_IA_UPGRADE_PROPOSAL_v3.md` as research; human bar = “feels like $100M control plane” (Part B only until Hub mechanical gate scoped).

---

## Grading summary card (print this)

```
SHIP ALLOWED when:
  Part A (all mechanical checks) = PASS
  Part B (human stranger script) = PASS or explicit founder ACCEPT with logged FAIL items

SHIP FORBIDDEN when:
  Part A any BLOCK
  Part B FAIL on B1.1–B1.4 without founder waiver

NEVER:
  Ship because Part A passed while skipping Part B
  Build a bot that auto-grades Part B
```

---

## What already exists vs. what to build

### Already on disk (keep wiring)

| Asset | Status |
|-------|--------|
| Positioning one-liner + JSON SSOT | LOCKED v3.1.0 |
| Brain prompt v2.0 + worker deployed | LIVE |
| `validate-sourcea-brain-chat-v1.sh` | PASS — partial A1.4 |
| Commercial copy gate | PASS |
| Copy depth gate | PASS |
| UI upgrade baseline / no-downgrade | EXISTS |
| Brain landing Playwright E2E | EXISTS (local server) |

### Gaps (this rubric creates the work)

| Gap | Fix |
|-----|-----|
| No single UI standard doc | **This file** |
| No mechanical-only UI gate | Build `validate-sourcea-ui-mechanical-v1.sh` |
| No positioning-contradiction grep across all pages | Add to mechanical gate A1 |
| No live production Brain stranger E2E | Add `validate-sourcea-brain-live-stranger-v1.sh` (curl/API — not taste) |
| Part B not ritualized | Founder checklist card §B1 — calendar, not code |
| Hub IA debt | Separate track — `HUB_UI_IA_UPGRADE_PROPOSAL_v3.md` |

---

## Full fix plan (execute in order)

### Phase 0 — Lock the bar (DONE)

- [x] Positioning one-liner on disk
- [x] Brain worker v2.0 deployed
- [x] UI Standard rubric (this doc)
- [x] Brain mobile header + copy alignment hotfix shipped 2026-06-25

### Phase 1 — Mechanical gate (machine) — ~1 ship window

**Goal:** One script BLOCKs publish on Part A only.

| Step | Deliverable | Path |
|------|-------------|------|
| 1.1 | Gate SSOT JSON | `data/sourcea-ui-mechanical-gate-v1.json` |
| 1.2 | Python scanner | `scripts/sourcea_ui_mechanical_gate_v1.py` |
| 1.3 | Shell wrapper | `scripts/validate-sourcea-ui-mechanical-v1.sh` |
| 1.4 | Wire into publish | `publish_sourcea_landing_v1.py` after copy gates, before stage |
| 1.5 | Wire into run-recipe | `SourceA-landing/green-unified/scripts/run-recipe.sh` step 2d |
| 1.6 | Receipt | `~/.sina/enforcement/sourcea-ui-mechanical-gate-receipt-v1.json` |

**Checks in v1 script (minimal, high-signal):**

1. Positioning denylist scan (A1.1–A1.3) against `green-unified/` + `dist/`
2. Unreplaced tokens (A3.1)
3. Key JSON assets parse (A3.2)
4. Brain config + worker status (A3.3, A1.4) — delegate to existing brain validator
5. CSS invariant: mobile brain header rule present (A2.1) — grep for `flex-direction: column` under `@media (max-width: 600px)` + `.sa-brain-head`
6. Delegate A4.1–A4.3 to existing validators (chain, no duplicate logic)

**Explicitly out of scope for v1 machine gate:** B2.4 cheap feel, B2.5 willingness to pay, competitor taste.

### Phase 2 — Live production smoke (machine, not taste) — ~½ ship window

| Step | Deliverable |
|------|-------------|
| 2.1 | ✅ `scripts/validate-sourcea-brain-live-v1.sh` — curl production `sourcea.app` assets + worker GET + 3 API stranger prompts |
| 2.2 | Optional Playwright against production (ship window only, not Mac founder session) |
| 2.3 | ✅ Weekly E2E checklist: `brain_live_production` bundle in `data/sourcea-e2e-check-registry-overrides-v1.json` + `SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md` |

### Phase 5 — Founder pulse dashboard ✅ v1

| Step | Deliverable |
|------|-------------|
| 5.1 | ✅ Worker `GET /api/site/dashboard/v1` — stats range + feedback inbox (founder key) |
| 5.2 | ✅ `/sourcea/pulse-founder` — unlock UI + inbox table |
| 5.3 | ✅ `/sourcea/status` — public today stats strip |
| 5.4 | ✅ `scripts/validate-sourcea-site-pulse-v1.sh` |

### Phase 3 — Human protocol (no code) — ongoing

| Step | Deliverable |
|------|-------------|
| 3.1 | Calendar: **2 stranger tests / month** before major landing publish |
| 3.2 | Log verbatim objections to `docs/ui-stranger-test-log-v1.md` (one row per test) |
| 3.3 | Promote repeated objections → mechanical denylist (A1) within 24h |
| 3.4 | Founder rule: no “green dashboard” ship without B1 script signed |

### Phase 4 — Page-wide positioning sweep (content) — ~1–2 days ✅

**Goal:** Eliminate remaining proof-first / call-first copy outside forge pages.

| Surface | Action |
|---------|--------|
| `index.html`, `start.html`, `platform.html` | ✅ Hero/subcopy audit vs A1 denylist |
| `proof.html`, `scenario.html` | ✅ Proof as **feature** framing, not product |
| `pricing.html`, `offer.html` | ✅ Value chain before dollar amounts |
| `data/forge-catalog.json` | Replace `VERIFY from receipts` beat where it leads |
| `sync_sourcea_landing_pages_v1.py` | Footer template → execution-first line |
| Re-run publish gates + Phase 1 mechanical gate |

### Phase 5 — Hub UI (separate product) — backlog

Use `HUB_UI_IA_UPGRADE_PROPOSAL_v3.md`:

- Cap sidebar to 7 pinned + command palette
- Single icon system
- Home spec compliance
- **Human grade first**; mechanical hub gate only after rubric rows defined for Hub

### Phase 6 — Distribution gate (the real goal)

| Gate | Rule |
|------|------|
| Pre-dist checklist | Part A PASS + Part B PASS + Forge Terminal demo live |
| Post-dist | 1 stranger conversation within 48h of any landing ship |
| Failure | Objection → log → denylist → hotfix → re-test — not new AI critic |

---

## Incident registry (feeds denylist)

| Date | Finding | Class | Fix |
|------|---------|-------|-----|
| 2026-06-25 | Brain sold records not execution | B1 + A1 | Positioning v3.1 + worker v2 |
| 2026-06-25 | Page said VERIFY from receipts; Brain said execution | A1 | Forge pages + chatbot copy |
| 2026-06-25 | Mobile header 0px subtitle | A2 | CSS flex-direction fix |
| 2026-06-25 | Chips navigated away from chat | A6 | In-chat chip actions |
| 2026-06-25 | Call-first hero / Book proof demo bottleneck | A1 | Phase 4 sweep — Forge Terminal primary, Talk to a human escalation |

---

## Change control

1. **Part A rows** — Worker may add checks; founder approves new BLOCK rules.
2. **Part B rows** — Founder owns; advisor may suggest, not automate.
3. **One-liner changes** — `SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md` process only.
4. **Never** mark Part B as machine-gradable without explicit founder ASF.

---

## Next action (recommended)

1. **Founder:** Run Part B1 stranger script once on current `sourcea.app` — 15 min, log verbatim.
2. **Worker:** Implement **Phase 1** mechanical gate (`validate-sourcea-ui-mechanical-v1.sh`).
3. **Worker:** Phase 4 positioning sweep on `index.html` + `proof.html` + sync footer template.

**Hold:** Online UI critic, desire-scoring LLM, auto-“would they pay” models.

---

## Cross-links

- `docs/SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md`
- `docs/HUB_UI_IA_UPGRADE_PROPOSAL_v3.md`
- `docs/research-vault/GOLDEN_REPORT_SOURCEA_SITE_POSITIONING_v1.md`
- `brain-os/law/SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md`
- `data/landing-copy-depth-gate-v1.json`
- `data/landing-commercial-copy-audience-v1.json`
