# World Target Model — UI Research & P0 Fix Spec (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.2 — LOCKED (post-incident)  
**Session:** 2026-06-05 — major upgrade / World Target Model  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  
**Law:** `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md` · **Map:** `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`  
**Incident:** `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` — **read before any UI change**

---

## Agent law (never forget)

1. WTM tab = major-upgrade session only (after *we have major upgrade today*).
2. **Never delete content** — UI upgrade = shape/structure only; all tables stay. See incident report SA-2026-06-05-INCIDENT-002.
3. **Founder shell (frozen):** `Overview` · `◎ Live map` — law strip → LIVE NOW → full map dashboard → phase tables. **No Map/Blueprint/Pipeline cockpit experiment.**
4. **No agent reads in hub UI** — no misconceptions table, no session chronology, no UI research buttons on page.
5. Gold accent · status dots · tabular nums OK for polish only.
6. Next build **A1.1** visible in map dashboard + LIVE NOW, not a replacement for full content.

---

## v2 fixes (why v1 was weak)

- Page title was overwritten → tab always said generic "World Target Model"
- Double chrome (topbar desc + hero + law strip) → wasted height, forced scroll
- Next build buried in side column → not the single decision point
- Lists instead of chips → Built/Target too tall on 14" screen

## v2.1 — content restoration (founder correction)

**Mistake:** v2 cockpit removed tables from default view. Founder: *"upgrade UI but lose all contents and tables."*

**Fix:** Map stays summary; **Blueprint** restores everything:
- LIVE NOW panels
- Current vs target + built layer table
- L0–L16 full table (Layer · Target · Today · Gap)
- Target blueprint L0–L16 (capabilities)
- 12-step stepper + phase cards
- System status + architecture
- All phase step tables (goals, achievements, gates)
- Full journey rail + LLM packet schema + supplemental builds

## P0 spec (implemented in hub v2)

### Navigation
- **Map** (default) · **Blueprint** · **Live Pipeline**
- **Ops** = `<details>` (law, locked docs, phase tables)

### Map view (single viewport)
```
TOP: LIVE 13/29 · B4 + A1.1
ROW1: Built | Target
ROW2: Core gap (one line)
ROW3: Swimlane D→C→B→A | Next build A1.1
FOOTER: sync line
```

### Blueprint
1. L0–L16 table (sticky header, filters, row expand)
2. 12-step roadmap (collapsed phases)
3. Architecture diagram

### Live Pipeline
Horizontal D→C→B→A lanes · YOU ARE HERE pin · real deps only

### Visual
Surface elevation · no emoji panels · 150ms tab fade · subtle swimlane pulse

---

## Research synthesis

**Cockpit principle:** minimize time to correct operational decision.

**Map vs Blueprint:** orientation vs mechanics.

**Parallel swimlanes:** B4 + A1.1 concurrency truth.

**Surface elevation:** Linear/Vercel-style bg layers over grid borders.

---

## Code anchors

| Asset | Path |
|-------|------|
| Payload | `scripts/system_roadmap.py` |
| UI | `agent-control-panel/assets/app.js` |
| CSS | `agent-control-panel/assets/app.css` |
| Rebuild | `python3 scripts/build-sina-command-panel.py` |
