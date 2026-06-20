# Sina Command — UI Next Steps v4

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-10  
**Status:** Round 2 shipped · Round 3+ proposed  
**Prior:** `HUB_UI_IA_UPGRADE_PROPOSAL_v3.md`

---

## Shipped in round 2 (this pass)

| ID | What | Why it matters |
|----|------|----------------|
| **UI-4** | Command palette — `⌘K`, sidebar Search, overflow Search | Any tab in ≤2 keystrokes; replaces Essentials scroll |
| **UI-2+** | Context strip chips are **clickable** | FREEZE→Run, SA→queue, progress→Home, worker→Runtime |
| **UI-5 lite** | Agent switcher dropdown in sidebar | Private agents no longer spam nav rows |
| **UX** | Nav recents in palette (localStorage) | Stripe-style “recently visited” |
| **UX** | `?` shortcut help overlay | Linear-style discoverability |
| **Home** | One STOP max; dedupe Safety in Needs you; strip emoji labels | Cleaner hero, less kid-project noise |
| **UI-6 partial** | Outfit + Plus Jakarta Sans on shell v2 | Fonts loaded in HTML finally used |

**Hard refresh:** `Cmd+Shift+R` on `http://127.0.0.1:13020`

---

## Round 3 — highest ROI (recommend next)

### UI-6 — Design token migration (2–3d)

**Problem:** Inner tab pages (`renderTrack`, `renderOrderGuardian`, …) still use rainbow card borders (gold/green/blue), emoji in heroes, and bespoke `sc-page-hero--*` classes.

**Deliver:**
- One `ScCard` surface: `--surface-raised`, single border, no per-feature accent borders
- One `ScPageHeader`: title + optional kicker + max 2 actions
- Migrate top 5 visited tabs first: **Track, Actions, Advisor, Goal1 log, Essentials**

**Approval:** `ASF: UI-6 — design tokens`

---

### UI-5 full — Agent context model (1d)

**Problem:** Agent switcher works, but loop sticky + agent-loop page still feel like separate products.

**Deliver:**
- Context strip shows active agent chip when on workspace tab
- `Agents` tier-1 opens last workspace (or hub if none)
- Remove duplicate “Agent hub” CTAs inside workspace pages

**Approval:** `ASF: UI-5 — agent switcher`

---

### UI-7 — Inbox unification (1–2d)

**Problem:** Track, Actions, Backlog are three tabs for one mental model (“what needs founder tap”).

**Deliver:**
- Single **Inbox** tab with 3 sub-filters: Commitments · One-tap · Audit
- Badge on tier-1 Inbox = sum of all three (already partial)
- Home “Needs you” pulls from same SSOT slice

**Approval:** `ASF: UI-7 — inbox unify`

---

### UI-8 — Page layout kit (2d)

**Problem:** 40+ `render*()` functions each invent their own HTML soup.

**Deliver:**
- `renderPageShell({ title, lead, actions, body })` helper
- List / detail / split layouts — pick one per view type
- Journey panel optional via flag, not appended everywhere

**Approval:** `ASF: UI-8 — page layout kit`

---

## Round 4 — polish & scale

| ID | Deliver | Benchmark steal |
|----|---------|-----------------|
| **UI-9** | Collapsible sidebar + remember width | Vercel |
| **UI-10** | Pinned nav items (founder chooses 2 extras on tier-1) | Linear |
| **UI-11** | Mobile bottom bar (Home · Inbox · ⌘K · Safety) | Vercel mobile |
| **UI-12** | Plain-English gate: no `factory-now` in default DOM | Stripe home test |
| **UI-13** | Server-driven `nav_badges` in hub-sync (one poll for all counts) | Data unify U2 |

---

## Data track (parallel — still high value)

From `HUB_UNIFY_RESEARCH_PROPOSAL_v2.md`:

1. **HUB-P0-1** — proof counter honest in hub-sync (home progress never drifts)
2. **UNIFY U2** — live client slices; stop full payload refresh
3. **UNIFY U3** — single tab registry server-side (delete triple NAV/HUB_PAGES/essentials lists)

UI and data tracks merge at **context strip** + **home_founder_view** — same poll, one truth.

---

## Success tests (v4 bar)

| Test | Pass |
|------|------|
| `⌘K` → type “advisor” → Enter | Opens Advisor track < 3s |
| Context chip FREEZE | Opens Run tab |
| Sidebar with 3 private agents | **0** extra nav rows (switcher only) |
| Home | ≤1 STOP, ≤1 Safety, no emoji in buttons |
| Compare to Linear | Same calm — sidebar dim, content bright |

---

## Recommended order

```
UI-6 (tokens on top tabs) → UI-7 (inbox) → UI-5 full → UI-8 (layout kit) → UI-9–13
```

Say **`ASF: UI-6 — design tokens`** to start round 3.
