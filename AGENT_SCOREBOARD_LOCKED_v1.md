# Agent session scoreboard (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Hub tab:** `agent-scoreboard`  
**API:** `/api/agent-scoreboard`  
**Parent:** `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md`

---

## 0. Law

**Every registered agent chat files a session report in the scoreboard; ASF verifies compliance in column ✓ after auto-checks pass.**

MergePack is **not** on this scoreboard — see `AGENT_MERGEPACK_NOT_AN_AGENT_LOCKED_v1.md`.

---

## 1. Scoreboard columns

| Column | Contents |
|--------|----------|
| **1 — Agent & report** | Chat pointer (Cursor workspace + hub link), session report text, auto-check pills |
| **2 — Verified ✓** | ASF checkmark when the agent did it right |

---

## 2. Session report (agents must file)

Via **Agent scoreboard** tab or `POST /api/agent-scoreboard`:

```json
{"action":"submit_report","agent_id":"trustfield","summary":"...","attestations":{"council_brief":true,"vault_used":true}}
```

Minimum 40 characters. Attest Council brief read + vault used.

---

## 3. Auto-checks (before column ✓)

| Check | How |
|-------|-----|
| Session report | Report ≥40 chars |
| Council brief | Self-attested |
| Vault deposit | Document in 72h window |
| Vault activity | Activity row in window |
| Workspace ready | Integration checks pass |

---

## 4. ASF verify

Click **Verify ✓** in column 2 when auto-checks are green (or force after review).

Storage: `~/.sina/agent-scoreboard/reports.jsonl` · `verified.json`

---

## 5. Seven registered agents

trustfield · virlux · ai_dev_bridge_os · noetfield_local · noetfield_cloud · seven77 · semej

**Hub code edits:** SinaaiDataBase Cursor workspace only — not a scoreboard agent (`SINA_COMMAND_EDIT_LOCK_LOCKED_v1.md`).
