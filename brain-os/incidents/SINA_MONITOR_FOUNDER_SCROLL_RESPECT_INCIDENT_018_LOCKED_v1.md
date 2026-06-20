# INCIDENT-018 — Monitor forced auto-scroll (founder focus violation)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**Class:** UX · founder respect policy  
**Reporter:** ASF  
**Agent:** Cursor Worker (SourceA)  
**Fixed:** 2026-06-10 · `monitor.html`  
**sequence_id:** SA-2026-06-10-INCIDENT-018

---

## Violation

`:13021/monitor` called `scrollHere()` automatically on every load and every 20s refresh when filter=road. This **jumped the viewport** to the HERE row without founder consent — interrupting reading and breaking focus.

## Founder respect policy

**Law:** UI must **never** move scroll position unless founder explicitly taps **Here** or **Go**.

- No auto-scroll on load
- No auto-scroll on polling refresh
- Preserve scroll in `sessionStorage` across refreshes

## Fix

- Removed `setTimeout(scrollHere, 300)` after render
- Save/restore `scroller.scrollTop` on each `load()`
- Footer documents founder-respect scroll law

## Monitor reality upgrade (same session)

- API payload adds `factory_now` (FREEZE, queue pos, INBOX pending)
- API payload adds `phase_strict` (s7→s8→s9 order)
- Header line shows factory + PHASE_STRICT rail

**Verify:** Open monitor · scroll to top · wait 20s · scroll must stay at top.

**LOCKED** — canonical body · `brain-os/incidents/`
