---
name: forge-living-ui-modern-ide
description: >-
  Modern living-chat UI for Forge Terminal + Chat Unify — Cursor/Replit/Lovable
  patterns, founder-readable replies, resizable panels, embed mode. Use when
  upgrading Forge IDE, Connect shell, chat replies, or Chat Unify founder loop UX.
---

# Forge Living UI — Modern IDE / No-Code App Patterns

**Saved:** 2026-06-25T20:00:00Z  
**App target:** Forge Terminal v2.9.1 · Quality Engine 1.1 · L2 self-improve · port **13029**

## When to use

- Forge Terminal or Chat Unify replies look robotic, JSON-like, or unreadable
- Chat area too small, static layout, no resize/move
- Connect iframe Forge IDE tab broken or cramped
- Building “living” chat UX comparable to Cursor, Replit, Lovable, Duolingo polish

## North star

> **Founder sees prose first** — four-section founder language, quality chip inline, exec blocked unless PASS — in a **Cursor-style resizable workbench**, not a static form.

---

## Reply pipeline (must stay wired)

```
chat_turn → run_terminal → translate_for_founder(prefer_ai=True)
         → response_for_display() → API display_response + response
         → terminal.js renderFounderSections() → appendChatBubble
         → quality_gate in thread meta (persist on reload)
```

| Layer | File | Rule |
|-------|------|------|
| Translate | `scripts/chat_founder_language_v1.py` | AI first; rules fallback only |
| Display | `scripts/forge_quality_gate_v1.py` `response_for_display()` | Never show raw JSON |
| API | `scripts/forge_terminal_v1.py` | Return `display_response` + `quality_gate` |
| Thread | `forge_terminal_desktop_mesh_v1.py` `append_turn` | Meta includes `quality_gate` |
| Render | `apps/forge-terminal-v1/terminal.js` | `renderFounderSections` + `.forge-markdown` |

---

## Modern UI pattern library (borrow from best apps)

### Cursor IDE

- **Workbench grid:** sidebar | editor | bottom dock (terminal/logs)
- **Living chat column:** `.forge-chat-column` — thread `flex:1` + composer pinned bottom (Lovable/Cursor)
- **Resizable dock:** drag handle + CSS `--dock-h` persisted in localStorage
- **Living chat:** thread fills center column — never `max-height: 42vh`
- **Embed mode:** hide topbar + statusbar in iframe; **keep compact workspace sidebar** + horizontal workspace strip; dock collapsed by default
- **Keyboard:** **Enter send** · Shift+Enter newline · ⌘J toggle dock · ⌘O open folder

### Replit

- **Trinity layout:** files | chat | console — all resizable
- **Status bar:** workspace, model, cost, latency always visible
- **Mesh sidebar:** live peers with green/red dots

### Lovable / v0

- **Card sections:** rounded panels, 14px body, 11px uppercase labels
- **Verdict chips:** PASS green / REVISE amber / REJECT red — never raw JSON
- **One primary CTA:** Send; secondary ghost for Clear / Re-run

### Duolingo (founder-friendly)

- **Progress feel:** quality score + layers as compact chip (not wall of PASS/FAIL)
- **Bite-sized blocks:** Bottom line → What this means → Blockers → Next step
- **Friendly tone law:** `chat_founder_language_v1.FOUNDER_SYSTEM` — no bash, no tool names

### Atom / VS Code panes

- **Split persistence:** dock height, sidebar width in localStorage keys
- **Monospace only in logs** — chat uses `--font`, not `--mono`

---

## Layout checklist (Forge IDE)

```css
/* DO */
.forge-chat-thread { flex: 1; min-height: 0; /* no max-height cap */ }
.forge-center-col { grid-template-rows: 1fr var(--dock-h); }
.forge-dock-resize { cursor: ns-resize; height: 5px; }
.forge-app.forge-embed .forge-topbar { display: none; }

/* DON'T */
max-height: 42vh on chat; max-height: 96px on founder textarea;
fixed 200px dock with no drag; duplicate Connect + IDE topbars in iframe
```

---

## Connect shell checklist

| Fix | File |
|-----|------|
| `forge-ide` in `switchTab()` tabs array | `apps/forge-terminal-connect-v1/app.js` |
| Default tab `forge-ide` not `home` | same |
| Iframe `height: 100%` + panel `flex: 1` | `forge-connect.css` |
| Token bridge parent→iframe | `forge-quality-bridge.js` |
| Verify tab quality lookup by run_id | `forgeQualityLookupRunId()` |

---

## Chat Unify founder loop

- Raise `.cu-textarea-founder` to `max-height: 320px; resize: vertical`
- Loop steps: use founder-section render, not monospace pre-wrap dumps
- Port **13023** = Chat Unify only; **13029** = Connect + Forge IDE embed

---

## Quality gate UX

- Inline chip under every assistant bubble (verdict + score + eval shadow)
- `setExecButtonsEnabled(quality_gate.execution_allowed)` on every turn
- Full layer list stays in decision panel — chat gets chip only

---

## E2E proof (Mac light)

```bash
bash ~/Desktop/Noetfield-Systems/SourceA/scripts/validate-forge-terminal-living-desktop-e2e-v1.sh
bash ~/Desktop/Noetfield-Systems/SourceA/scripts/validate-forge-terminal-desktop-e2e-v1.sh
```

Receipts:
- `~/.sina/forge-terminal-living-desktop-e2e-v1.json`
- `~/.sina/forge-terminal-living-ui-e2e-v1.json`
- `~/.sina/forge-terminal-desktop-e2e-v1.json`

Law: `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_LIVING_DESKTOP_E2E_LOCKED_v1.md`

---

## Forge Factory directory

Full map: [FORGE_FACTORY_DIRECTORY.md](./FORGE_FACTORY_DIRECTORY.md)

Quick spine:

| Area | Path |
|------|------|
| Forge IDE UI | `apps/forge-terminal-v1/` |
| Connect shell | `apps/forge-terminal-connect-v1/` |
| Terminal API | `scripts/forge_terminal_v1.py` |
| Quality gate | `scripts/forge_quality_gate_v1.py` |
| Founder language | `scripts/chat_founder_language_v1.py` |
| Connect server :13029 | `scripts/forge_terminal_connect_server_v1.py` |
| Cloud forge drain | `scripts/forge_v02_drain_v1.py` |
| Factory spike | `apps/factory-runtime-spike/` |
| Law | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_*` |
| L2 self-improve | `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_L2_SELF_IMPROVE_LOCKED_v1.md` |
| Agent kernel | `scripts/forge_agent_kernel_v1.py` |

---

## L2 self-improve (v2.9.1+)

- Checkbox **Self-improve L2** (`opt-self-improve-l2`) — auto after REVISE/REJECT
- **Self-heal** button in exec strip — manual L2
- API `agent_self_improve` · receipt `~/.sina/forge-agent-self-improve-latest-v1.json`
- Patch-only policy · max 2 rounds · re-gate via `quality_rerun`

---

## Implementation order (P0 → P2)

1. **Replies:** `prefer_ai=True`, `display_response`, founder section render
2. **Chat size:** remove 42vh cap; flex column fill
3. **Connect tab:** `forge-ide` in router; iframe full height
4. **Movable:** dock drag handle + persisted `--dock-h`
5. **Embed:** hide inner topbar in iframe
6. **Thread:** persist `quality_gate` in chat meta
7. **Polish:** sidebar resize, command palette (future)

---

## Anti-patterns (incident triggers)

- Rules-only `translate_for_founder` on live chat → generic “trim archive” boilerplate
- Raw `row.response` in bubble when JSON → founder sees garbage
- `switchTab` missing `forge-ide` → tab click falls back to Home
- Quality chip only on live turn, not reload → “static” feel
- Monospace + tiny max-height on founder inputs
