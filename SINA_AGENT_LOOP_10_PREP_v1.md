# Agent loop — 10-round prep (v1) · founder = clicks only

| | |
|--|--|
| **Law** | **No Terminal for founder** — only Sina Command taps (1–3 clicks per step) |
| **Roles** | Executor = Cursor coding chat · Advisor + Planner = app |

---

## Founder flow (all in app)

**Important:** The loop is **10 separate rounds**, not one long chat. Round 2 only starts after you **Submit round** for round 1 (or the Cursor agent auto-submits for you).

| Step | Clicks | Where |
|------|--------|--------|
| 1 | **Refresh** (top bar) | Any tab |
| 2 | Open **Agent loop** | Sidebar ⟳ |
| 3 | Pick **3 / 5 / 10 rounds** + **Start loop with this →** | One click starts round 1 inject |
| 4 | Cursor works | `[SINA_LOOP n/N]` in coding chat |
| 5 | **Submit round** | App → paste answer → **Submit round → next prompt** (round n+1 injects) |
| 6 | Repeat until N done | Progress bar shows submitted count |
| **Stop** | **Stop loop** (red, top of page) | Anytime — confirms before abort |

If inject fails: **Resend current prompt to Cursor** (one click).

To stop: **Stop loop** (one click).

---

## What founder never does

- `agent-loop-done.sh`
- `pkill`, `curl`, `python3 scripts/…`
- Typing commands in Terminal

*(Cursor **executor** may POST via API internally — not the founder.)*

---

## After each Cursor round

1. Copy the coding agent’s **one-line summary** and **full reply** from Cursor chat.
2. Sina Command → **Agent loop** → **Submit round** card.
3. Paste → **Submit round → next prompt**.

Tell the Cursor agent: *“When done, I will submit from this agent's Private agents page — give me a one-line summary and full text to paste.”*

---

## Suggested goal (tap **Use as goal** or paste)

- **Ship path:** SEMEJ + MP-SHIP `/health` + P0 RunReceipt across 10 rounds  
- **EP-OS:** Draft `EP_OS_FOUNDATION_v1.md` in `sina-bowl/`  
- **Hub verify:** Backlog + Track + playful UI smoke (no regress)

---

## Checklist before Start

- [ ] **LIVE** pill green (if not: quit & reopen **Sina Command** from Desktop — no Terminal)
- [ ] **Agent loop** tab shows **10 seeds**
- [ ] **OpenRouter** configured (Advisor shows Online — agents set `~/.sina/secrets.env`, not founder)

---

*UI: `SINA_COMMAND_UI_PLAYFUL_LOCKED_v1.md` · Loop inbox text updated to match app Submit.*
