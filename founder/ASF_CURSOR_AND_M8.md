# Cursor + M8 — ASF reference

## Icons (remember)

| Icon | App | Action |
|------|-----|--------|
| **Silver / grey** | Real **Cursor IDE** (cursor.com) | **USE** — your Pro plan is here |
| **Purple** | **IDE For Cursor** (ZUGGO App Store) | **DELETE** — not M8, not your IDE |

You had installed purple yourself. Agent **ran** it once via bad `open -a Cursor` automation — **fixed and locked**.

---

## M8 = internal plan (SinaPromptOS)

| Part | Meaning |
|------|---------|
| M8a | Paste prompt into **existing** repo chat |
| M8b | SDK per repo |
| M8c | Orchestrator (dispatch → … → ingest) |
| Phone `full_m8` | Mac stack **without** UI paste spam |

**M8 ≠ purple app.**

Incident doc: `SinaPromptOS/docs/M8_INCIDENT_2026-06-03_LOCKED.md`

---

## Safe vs forbidden

| Safe | Forbidden |
|------|-----------|
| `dispatch-day.sh` + manual paste | `m8-dispatch-ui.sh` (5-repo blast) |
| `m8-paste-one-repo.sh trustfield` (one repo, when ready) | `m8-now.sh` with UI paste (now wire-only) |
| Phone RUN SYSTEM `full_m8` | Paying purple app subscription |
| `kill-m8-spam.sh` if loops | `open -a Cursor` without `/Applications/Cursor.app` |

---

## One-time Mac fix

1. Quit Cursor (Cmd+Q)
2. Drag **silver** `Cursor.app` → **Applications**
3. Empty Trash if purple app was there
4. Optional: `~/Desktop/SinaPromptOS/scripts/install-cursor-to-applications.sh`

---

## Re-enable M8 UI paste (only when ALL true)

- [ ] `/Applications/Cursor.app` exists
- [ ] No `IDE For Cursor.app`
- [ ] `m8.ui_enabled: true` in settings **on purpose**
- [ ] `export SINA_M8_EXPLICIT_ARM=1` + `SINA_CURSOR_AUTO_PASTE=1`
- [ ] **One repo:** `./scripts/m8-paste-one-repo.sh trustfield`
