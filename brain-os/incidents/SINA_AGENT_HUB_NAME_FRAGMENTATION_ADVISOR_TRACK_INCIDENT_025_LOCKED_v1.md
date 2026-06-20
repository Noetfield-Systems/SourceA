# Agent invented Hub tab name — Advisor track fragmentation (INCIDENT-025 LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-025  
**Classification:** MANDATORY READ — Brain · Maintainer · any Hub/agent UI editor  
**Agent:** Cursor Brain/Auto (SinaaiDataBase maintainer session — archive + live UI pass)  
**Window:** 2026-06-10 (founder: *"YOU CANT JUST INVENT A NEW NAME"*)  
**Related:** INCIDENT-020 (topic conflation) · INCIDENT-021 (wrong-folder) · INCIDENT-022 (stale surfaces) · `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` · `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md`

---

## 1. Executive summary

Founder asked for a **live UI** for the **existing** crisis discussion list already defined as **Advisor track** (`advisor-discussion`). The agent **did not read** the locked thread doc or prior conversation naming before shipping UI copy. It **renamed** the Hub tab to **"Pending discussions"**, added parallel hero strings (**"live pending board"**), and answered founder questions using the invented name — while the SSOT still said **Advisor track** everywhere that mattered (locked doc, master index #20, `hub_tab`, API path, state file).

Founder could not find the tab because **three different labels** competed: **Advisor track** (law) · **Pending discussions** (agent UI) · **AI Advisory** (unrelated tab `ai-advisory`).

**Severity:** **High** — governance fragmentation + founder time waste + trust (same class as INCIDENT-020 conflation).

**One-line verdict:** **One tab · one name · one id** — never rename without authority index + locked doc + `NAV_TABS` sync.

---

## 2. Canonical name (ONLY these — do not invent)

| Layer | Canonical | Never use as tab title |
|-------|-----------|----------------------|
| **Founder-facing title** | **Advisor track** | Pending discussions · Advisory tab · Crisis table (subtitle only) |
| **Hub tab id** | `advisor-discussion` | `advisor-track` (alias URL only) · `pending-discussions` |
| **API** | `GET/POST /api/founder-advisor-discussion` | — |
| **State** | `~/.sina/founder-advisor-discussion-v1.json` | — |
| **LOCKED doc** | `archive/attachments/2026-06-10/SOURCEA_FOUNDER_ADVISOR_DISCUSSION_TRACK_LOCKED_v1.md` | — |
| **Builder** | `scripts/founder_advisor_discussion_v1.py` | — |
| **Direct URL** | `http://127.0.0.1:13020/?tab=advisor-discussion` | — |

### Not the same (INCIDENT-020 class conflation)

| Name | Tab id | Purpose |
|------|--------|---------|
| **AI Advisory** | `ai-advisory` | Coach — connections, upgrades, one focus (More group) |
| **Sina Advisor chat** | Cursor IDE `[SINA_ADVISOR]` | Strategic coach via `advisor-cursor-reply.sh` — not Hub tab |
| **Advisor track** | `advisor-discussion` | Founder crisis table · D1–D4 · subjects A–E · PINNED |

---

## 3. Real reasons (why it happened)

| # | Root cause | Evidence |
|---|------------|----------|
| R1 | **Skipped SSOT read** | Agent implemented UI before re-reading `SOURCEA_FOUNDER_ADVISOR_DISCUSSION_TRACK_LOCKED_v1.md` §Hub tab line |
| R2 | **Skipped conversation thread** | Prior thread already said "Advisor track tab" + master index #20 PINNED — agent treated archive list as new product name |
| R3 | **Invented marketing title** | Renamed nav to "Pending discussions" to describe *state* (pending) instead of *registered product name* (Advisor track) |
| R4 | **Parallel subtitle drift** | Added "live pending board" hero — third label fragment |
| R5 | **AI Advisory homonym** | Founder heard "advisory" in speech; agent did not proactively disambiguate `ai-advisory` vs `advisor-discussion` every reply |
| R6 | **No unification gate** | No validator blocked forbidden tab renames; no mandatory rule to grep existing names before Hub copy edits |
| R7 | **Nav render bug** (secondary) | `go()` early-return could show Home while URL was `?tab=advisor-discussion` — compounded "can't find it" |

---

## 4. Timeline

| When | Founder / disk | Agent did | Wrong? |
|------|----------------|-----------|--------|
| 2026-06-10 early | Locked doc + Hub shipped as **Advisor track** | `founder_advisor_discussion_v1.py` · `hub_tab: advisor-discussion` | **Correct** |
| 2026-06-10 | Founder: live UI for pending discussion list | Extended payload + poll — good intent | **OK** |
| 2026-06-10 | Same session | Renamed NAV title → **Pending discussions** | **VIOLATION** |
| 2026-06-10 | Founder: can't find Advisory tab | Explained with invented name + wrong disambiguation | **STALE** |
| 2026-06-10 | Maintainer 2 Phase 1–10 ship | Correctly separate machine work; noted NAV drift | **OK** |
| 2026-06-10 | Founder: *invent new name / fragmentation* | This incident + rename revert + unification rule | **Remediation** |

---

## 5. Impact

- Founder searched sidebar for **Advisor track** — saw **Pending discussions** or missed tab entirely.
- Risk of duplicate future tabs (`pending-discussions`, `advisor-track-ui`).
- `audit_essentials_nav.py` / `find_critical_bugs` noise when copy diverges from `NAV_TABS`.
- Teaches wrong name to external advisors and future agents.

---

## 6. Law (never again)

1. **Before any Hub tab / category / thread rename:** `rg` canonical title in `SourceA/` + read `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` + locked doc for that feature.
2. **One topic → one founder-facing title** — status words (*pending*, *live*, *pinned*) go in **subtitle/desc/badge**, not replacement title.
3. **Every user-facing answer** must cite canonical name + tab id + URL: **Advisor track** · `advisor-discussion` · `?tab=advisor-discussion`.
4. **Proactively disambiguate** **AI Advisory** (`ai-advisory`) vs **Advisor track** (`advisor-discussion`) when founder says "advisory".
5. **Unification reminder** — agents MUST mention related existing rules/names/tags/links/thread/category when touching a topic (see `.cursor/rules/ecosystem-rule-conflict-resolution.mdc` §Name unification).

---

## 7. Remediation (shipped with this incident)

| Item | Action |
|------|--------|
| NAV title | Reverted to **Advisor track** only |
| Hero / tagline | Subtitle may say PINNED · D1–D4 — not replace title |
| `founder_advisor_discussion_v1.py` | `tagline` aligned to locked doc |
| Validator | `validate-hub-advisor-track-naming-v1.sh` — fails on forbidden tab renames |
| Rule | §Name unification in global `ecosystem-rule-conflict-resolution.mdc` |
| Registry | INCIDENT-025 row + this LOCKED body |
| Nav bug | `go()` re-render when same tab clicked (INCIDENT-025 secondary) |

---

## 8. Verification

```bash
cd ~/Desktop/SourceA
bash scripts/validate-hub-advisor-track-naming-v1.sh
python3 scripts/audit_essentials_nav.py
python3 scripts/founder_advisor_discussion_v1.py --json | python3 -c "import sys,json;d=json.load(sys.stdin);assert d.get('hub_tab')=='advisor-discussion'"
```

Hub: **Founder → 📌 Advisor track** · URL `?tab=advisor-discussion` · **not** AI Advisory.

---

**Status:** REMEDIATED 2026-06-10 — Advisor track canonical in Hub + validator

**END INCIDENT-025**
