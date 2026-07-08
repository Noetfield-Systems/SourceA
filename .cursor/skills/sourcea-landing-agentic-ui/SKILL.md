---
name: sourcea-landing-agentic-ui
description: >-
  SourceA public landing agentic UI — Brain, Tools dock, Site Pulse feedback/analytics,
  execution-first positioning. Use before any edit to sourcea.app landing HTML/CSS/JS.
  Anti-stale: always verify production + positioning SSOT. Founder law: UI sells itself;
  calls are optional escalation, never the bottleneck.
---

# SourceA landing — agentic UI upgrade skill

**Saved:** 2026-06-25T12:00:00Z  
**Live audit:** [sourcea.app](https://sourcea.app) · proof page · Brain worker  
**Rubric:** `docs/SOURCEA_UI_STANDARD_RUBRIC_LOCKED_v1.md`  
**Positioning SSOT:** `SourceA-landing/green-unified/data/sourcea-positioning-v1.json` v3.3.0  
**One-line law:** `docs/SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md`

---

## Founder law (non-negotiable)

> **If the agentic site works, strangers never need a founder call.**  
> Calls are **optional escalation** for enterprise procurement — not the primary funnel, not the hero CTA, not the bottleneck.

**Forbidden strategy (visible failure):**

- Hero/subcopy that says strangers must **book a call / screen-share / live demo with Sina** to understand the product
- Header CTA **“Book proof demo”** above **“Try Forge Terminal”**
- Tools dock skill **“Book demo · 15 min with Sina”** ranked equal to Forge Terminal
- Copy like *“We show real work on a call — not slides”* as the **main promise**

**Required strategy (agentic):**

1. **Try in browser** — Forge Terminal `/sourcea/forge/terminal`, sandbox, proof quiz, live receipt embed
2. **Ask Brain** — in-chat routing, no tab hop
3. **Report friction** — Site Pulse feedback FAB (bug / confused / idea / praise)
4. **Book call** — buried in footer or “talk to a human” after self-serve paths exhausted

**Founder objection (2026-06-25):** *“There is nothing I can do on a call that the whole bottleneck is set on that. If it works they never need a call.”* — treat as **A1 positioning denylist** input.

---

## What shipped (current — do not regress)

| Layer | Files | Production |
|-------|-------|------------|
| **Brain chat** | `sourcea-chatbot.js`, worker `sourcea-brain-chat-v1` | Execution-first greet; in-chat chips; mobile `sa-brain-head-main` |
| **Site Pulse** | `sourcea-site-pulse-v1.js`, worker `sourcea-site-pulse-v1` | Pageview + event batching; stranger feedback FAB |
| **Site Interact** | `sourcea-site-interact-v1.js`, `data/sourcea-site-interact-v1.json` | ⚡ Tools dock; guided “What brings you here?”; Cal overlay |
| **Deploy inject** | `scripts/build_sourcea_vercel_output_v1.py` | Injects pulse + interact on all HTML with chatbot |
| **Mechanical gates** | `validate-sourcea-ui-mechanical-v1.sh`, `validate-sourcea-brain-live-v1.sh` | Disk + production smoke |

### Tools dock skills (config-driven)

`data/sourcea-site-interact-v1.json` → 48h MVP · Free sandbox · **Forge Terminal** · Live receipt · Proof quiz · Book demo (demote last)

### Feedback types (strangers)

`data/sourcea-site-pulse-config-v1.json` → bug · confused · idea · praise → `POST /api/site/feedback/v1` → KV + email `forge@sourcea.app`

### Analytics (backend exists — UI gap)

Worker stores daily `pageviews`, `event:*`, `feedback_count` in KV.  
`GET /api/site/stats/v1` — **no founder dashboard yet** (ship next).

---

## Stale vs live (read before every upgrade)

| Signal | Stale (BLOCK ship) | Live (target) |
|--------|-------------------|---------------|
| Positioning | “Business Acquisition Systems”, “verify on a call”, “Book proof demo” hero | “AI execution platform powered by Forge” |
| Brain subtitle | “proof, pricing” | Execution + Forge Terminal routing |
| Primary CTA | Cal.com / screen-share | Forge Terminal → sandbox → Brain |
| `index.html` vs `founder-home.html` | `/sourcea/` = old acquisition copy; `/` = proof-first founder-home | Single execution-first hero everywhere |
| Proof page | “What you'll verify **on the call**”, “15-minute demo script” | “Try it in your browser — receipt in 5 minutes” |
| Offline banner | “I'm offline” visible when worker is up | `syncOfflineBanner()` + `aria-hidden` when online |

**Anti-staleness ritual (mandatory):**

```bash
# 1. Production truth (≤90s on Mac)
bash scripts/validate-sourcea-brain-live-v1.sh

# 2. Disk mechanical gate
bash scripts/validate-sourcea-ui-mechanical-v1.sh

# 3. Read SSOT — not chat memory
cat SourceA-landing/green-unified/data/sourcea-positioning-v1.json | head -40
```

Optional human glance: open `https://sourcea.app/sourcea/proof` — confirm Feedback + Tools + Brain FABs present.

---

## Upgrade checklist (AG-UI-0 … AG-UI-7)

| Step | Action |
|------|--------|
| AG-UI-0 | Classify: landing page / shared JS / worker / config JSON |
| AG-UI-1 | Read positioning SSOT + this skill + rubric Part A denylist |
| AG-UI-2 | `curl -sS https://sourcea.app/sourcea/data/sourcea-positioning-v1.json` — match disk version |
| AG-UI-3 | Edit **config JSON first** (`sourcea-site-interact-v1.json`, `sourcea-site-pulse-config-v1.json`, positioning) then JS/CSS/HTML |
| AG-UI-4 | CTA order: Forge Terminal → sandbox/quiz → Brain chips → pricing → call (last) |
| AG-UI-5 | Run mechanical + brain-live validators |
| AG-UI-6 | Publish: `python3 scripts/publish_sourcea_landing_v1.py --backend pages --project sourcea-com --custom-domain` |
| AG-UI-7 | Log stranger objections → `docs/ui-stranger-test-log-v1.md`; repeated → A1 denylist |

---

## Phase 4 backlog (positioning sweep — priority)

From rubric + live audit 2026-06-25:

| Surface | Replace |
|---------|---------|
| `founder-home.html` (root `/`) | “We show real work **on a call**” → “Try Forge Terminal — see a real run in your browser” |
| `index.html` (`/sourcea/`) | “verify **on a call**” → execution-first hero per positioning v3.1 |
| `proof.html` | “Book screen-share”, “demo script”, “on the call” → self-serve film + terminal + quiz |
| `data/sourcea-site-interact-v1.json` | Move `book-demo` skill to bottom; add `execution_first: true` flag; guided chip “Show me proof first” → terminal not call |
| `sourcea-site-fallback-v1.js` | `prove_summary: "…on a client call"` → “…shareable in browser” |
| Header `[data-sa-book-cta]` | Secondary ghost button; primary = “Try Forge Terminal” |

**Mechanical denylist additions (propose to `data/sourcea-ui-mechanical-gate-v1.json`):**

- `on a call` (hero/lead — not inside “optional escalation” footer)
- `Book proof demo` as **first** header CTA
- `screen-share` as primary promise
- `15 min with Sina` in Tools dock top 3

---

## Phase 5 backlog (tracking + feedback loop) ✅ v1

**Goal:** Founder sees what strangers do — without Cal.com bottleneck.

| Item | Status |
|------|--------|
| **Pulse dashboard** | ✅ `/sourcea/pulse-founder` + `GET /api/site/dashboard/v1` (founder key) |
| **Public stats strip** | ✅ `/sourcea/status` — today's pageviews + feedback + top events |
| **Event taxonomy** | `skill_click`, `guided_pick`, `brain_chat`, `feedback_submit`, `pageview`, … |
| **Feedback → ship** | Inbox table on founder dashboard · email still fires as backup |
| **Validator** | `bash scripts/validate-sourcea-site-pulse-v1.sh` |

**API (live):**

- Worker: `https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev`
- `POST /api/site/event/v1` · `POST /api/site/feedback/v1` · `GET /api/site/stats/v1` · `GET /api/site/dashboard/v1`

**Founder unlock:** `wrangler secret put FOUNDER_PULSE_KEY` → open `/sourcea/pulse-founder`

---

## UX hazards (live audit)

1. **Modal stacking** — Guided banner + Feedback panel + Brain drawer compete; Brain click blocked when feedback open. Fix: single z-index ladder + dismiss guided on feedback open.
2. **Too many floats** — Brain + Feedback + Tools + Guided = clutter on mobile. Consider merge: Brain hosts “Tools” and “Feedback” as in-panel tabs.
3. **“I'm offline”** — Still in a11y tree on some pages when worker is healthy; re-check `syncOfflineBanner()`.
4. **Call in Tools** — Undermines agentic positioning; demote or rename “Talk to a human (optional)”.

---

## File map (bounded paths)

```
SourceA-landing/green-unified/
  sourcea-chatbot.js          # Brain UI
  sourcea-site-pulse-v1.js    # Analytics + feedback FAB
  sourcea-site-interact-v1.js # Tools + guided + Cal overlay
  sourcea-site-fallback-v1.js # Instant paint strings (watch call-copy)
  sourcea.css                 # Brain header, pulse FAB, playbook dock
  data/sourcea-positioning-v1.json
  data/sourcea-site-interact-v1.json
  data/sourcea-site-pulse-config-v1.json
  founder-home.html           # Root / — high-traffic, still call-heavy
  proof.html                  # Proof feature page — not product pitch

cloud/workers/sourcea-brain-chat-v1/
cloud/workers/sourcea-site-pulse-v1/

scripts/build_sourcea_vercel_output_v1.py  # injects pulse+interact at build
scripts/publish_sourcea_landing_v1.py      # brain_live gate after deploy
```

---

## Validators (never skip)

| Script | What |
|--------|------|
| `validate-sourcea-ui-mechanical-v1.sh` | Positioning denylist, chatbot invariants, CSS |
| `validate-sourcea-brain-live-v1.sh` | Production CDN + worker stranger prompts |
| `validate-sourcea-brain-chat-v1.sh` | Worker API (disk config) |
| `validate-sourcea-modern-stack-e2e-v1.sh` | Pulse + interact files present |

---

## Ship summary template

```text
AG-UI ship · sourcea.app
- Positioning: execution-first / call demoted to optional
- CTAs: Forge Terminal primary
- Pulse: events + feedback wired
- Validators: mechanical PASS · brain-live PASS
- Founder line: strangers can try + report without a call
```

---

## Related skills

- `hub-pro-ui-upgrade` — Hub control plane (not landing)
- `hub-pro-hub-hero` — Mac Hub :13020
- Rubric Phase 3 — human stranger tests (`docs/ui-stranger-test-log-v1.md`)
