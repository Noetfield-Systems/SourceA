# Sina Command UI — Playful Path Design (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
| | |
|--|--|
| **Version** | `SINA-COMMAND-UI-PLAYFUL-1.0` |
| **Status** | **LOCKED** — honorary certificate of appreciation |
| **Awarded** | 2026-06-04 |
| **For** | ASF (Sina) · all Cursor agents touching the hub panel |

---

## Honorary certificate

This lock records founder appreciation for the **end-to-end UI upgrade**: Duolingo-style **path cards**, **3D buttons**, **bubble stats**, **lane tiles**, and the **Playful Path** theme — so the hub stays clean, classy, and scannable.

> **Do not regress this UI** without explicit founder request.  
> Refactors may improve behavior behind the same visual language; do not revert to flat list + underlined thread links as the default Home/Track/Ecosystem experience.

---

## Locked surface (files)

| File | Role |
|------|------|
| `agent-control-panel/assets/theme-duo.css` | Design tokens, path cards, 3D buttons, lane tiles |
| `agent-control-panel/assets/shell.html` | Fonts (Outfit + Plus Jakarta Sans), theme load order |
| `agent-control-panel/assets/app.js` | `pathCardHtml`, `subjectLaneIcon`, `statusLabel`, hub lane tiles, Home/Track/Ecosystem markup |
| `agent-control-panel/assets/app.css` | Base layout (theme-duo overrides atop this) |

**Build:** After asset changes, run `scripts/build-sina-command-panel.py` and hard-refresh (`Cmd+Shift+R`) on `:13020`.

---

## Visual contract (agents)

1. **Home “Focus now”** — vertical **path cards** from Track subjects (`home_priority_cards`), not raw ops/todo flood.
2. **Cards** — icon bubble · title · subtitle · status pill · **Continue** circle (green/blue/amber/red by status).
3. **Typography** — `Outfit` display, `Plus Jakarta Sans` UI (see `shell.html`).
4. **Buttons** — chunky radius, bottom shadow (3D), not flat 1px borders only.
5. **Explore** — `sc-lane-tile` grid with color stripe, not plain text rows.
6. **Backlog tab** — separate audit UX; do not remove when editing nav.

---

## Related product locks

- Guide: `SINA_COMMAND_GUIDE_LOCKED_v1.md`
- Vision: `SINA_COMMAND_CENTER_VISION_LOCKED_v1.md`
- Audit backlog: `scripts/command_audit_backlog.py` (AUD-F05+ UI items)

---

## Change policy

| Allowed | Not allowed without founder OK |
|---------|--------------------------------|
| Bugfix (contrast, a11y, mobile wrap) | Strip `theme-duo.css` or revert to Newsreader-only serif home |
| New tab using same path-card pattern | Replace path cards with old `sc-subject-card` list-only Home |
| Dark/light variant **in addition** | Full visual reset to pre-2026-06-04 flat dashboard |

**To intentionally unlock:** Rename this file (remove `LOCKED`) and note reason in Backlog or founder notes.

---

*Certificate text: Big great job on UI upgrade — locked as honorary appreciation.*
