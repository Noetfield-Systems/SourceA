# Sinaai — Auto-Paste / Auto-Prompt Incident Report (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-04-INCIDENT-001  
**Classification:** INTERNAL — MANDATORY READ for maintainer agent & ASF  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` · overrides any doc that says “auto-paste into Cursor”  
**Incident window:** 2026-06-04 (founder report: per-second → per-minute → queued spam in Cursor)  
**Maintainer:** ASF · executor documents; founder is only law editor  

---

## 1. Executive summary (what went wrong)

The founder closed **Sina Command** but **Cursor kept receiving unsolicited prompts** — pasted as if the user typed them. Symptoms escalated:

| Phase | Symptom |
|-------|---------|
| 1 | `[SINA_LIVE_MAINTAINER] New founder message — read inbox and reply to app.` injected into maintainer Cursor chat |
| 2 | **Every ~1 minute**, same template |
| 3 | **Every ~1 second** at peak |
| 4 | Cursor showed **“8 Queued to Send”** — TrustField dispatch text, maintainer inject, and founder’s own “KILL AUTO PASTE” lines stacked in the composer |

**Founder expectation violated:** Live agents = **in-app only**. No background copy/paste into Cursor without explicit permission. Closing the desktop app must **stop** all injection.

**Severity:** **Critical** — breaks founder trust, wastes usage quota, risks wrong repo edits, feels like malware.

---

## 2. Root causes (verified)

### 2.1 Hub outlived the UI

- `sina-command-server.py` binds **127.0.0.1:13020**.
- Closing **Sina Command.app** did **not** stop the hub → APIs kept running.
- Open browser tab on `http://127.0.0.1:13020/` could still poll and trigger actions.

### 2.2 Live agents → `inject_cursor_chat` (primary spam vector)

**File:** `~/Desktop/SourceA/scripts/intelligence_circle.py` (historical behavior, now removed)

On each Live agents send, code called:

```python
inject_cursor_chat(
    "[SINA_LIVE_MAINTAINER] New founder message — read inbox and reply to app.\n"
    f"File: {MAINTAINER_INBOX}\n"
    "Then: ~/Desktop/SourceA/scripts/live-agent-cursor-reply.sh \"your reply\""
)
```

**Mechanism:** `clipboard_safe.py` / osascript → activate Cursor → **Cmd+V** → **Return** → new user message in chat.

### 2.3 Prompt queue / direction auto-feed

- `prompt_direction.py` `confirm` could enable `auto_feed` and `deliver_next`.
- `sina_command_lib.py` Actions used `paste: True` on deliver.
- Panel `app.js` had `startAutoFeedLoop` (later disabled).

### 2.4 Backend E2E + panel builds

- `audit_backend_e2e.py` POSTed `chat` to intelligence API on panel build.
- Multiple `build-sina-command-panel.py` processes → repeated probes.

### 2.5 Agent loop reinject

- `agent_loop.py` `_deliver_round` called `inject_cursor_chat` with `[SINA_LOOP …]` prefix.
- `app.js` “Resend current prompt to Cursor” button.

### 2.6 Prompt OS — clipboard on dispatch

- `runtime/cursor_executor.py` `send_to_cursor` → **pbcopy** for primary repo when `copy_primary_to_clipboard: true`.
- `remote_ops.service` (port **8899**) auto-ran **dispatch** on file changes (e.g. `GLOBAL_BLOCKERS.json`) → regenerated paste files / clipboard.

### 2.7 Cursor UI queue (not a separate daemon)

- Repeated injects filled Cursor’s **“Queued to Send”** buffer.
- Required founder action: **Stop** → clear composer → do **not** use “Start Multitasking”.

### 2.8 Misleading “dispatch” URL routing

- `?run=pos-dispatch` sometimes launched mini-app instead of clear in-hub **Morning dispatch** log (fixed in `app.js`).

---

## 3. Fixes applied (2026-06-04)

| Layer | Fix |
|-------|-----|
| **Kill switch** | `~/.sina/auto-prompt-kill.json` · `auto_prompt_guard.py` blocks by default |
| **Opt-in only** | Paste only if `~/.sina/auto-prompt-opt-in.json` has `"enabled": true` (not created by default) |
| **clipboard_safe.py** | Blocks `[SINA_LIVE_MAINTAINER]` and `[SINA_ADVISOR]`; no osascript unless `SINA_ALLOW_CURSOR_PASTE=1` |
| **intelligence_circle.py** | `send_to_cursor_maintainer` — **never** injects; app + inbox only |
| **agent_loop.py** | `inject_cursor_chat` respects kill switch; maintainer tags forbidden |
| **prompt_queue / direction** | `deliver_next` requires founder confirm; no auto-feed on confirm |
| **app.js** | Auto-feed loop off; Live agents `inject_cursor: false`; loop UI “app only” |
| **audit_backend_e2e.py** | Dry-run only; gated by `SINA_RUN_BACKEND_E2E=1` |
| **kill-sina-command.sh** | Stops hub :13020, builds, **remote_ops**, m8, osascript; pauses scheduler; disables `copy_primary_to_clipboard` + m8 UI in settings |
| **POST /shutdown** | Hub can exit cleanly (when used) |
| **Rules** | `sina-command-maintainer.mdc`, `agent-loop.mdc` — no timer inbox reads, no auto-paste |

---

## 4. Emergency procedure (founder — one tap)

**In Sina Command app (preferred):** top bar **⛔ Stop** or **Actions → Emergency stop** — one tap, confirm, hub force-exits.

**Terminal (if app unreachable):**

```bash
~/Desktop/SourceA/scripts/emergency-stop.sh
```

(Same as `kill-sina-command.sh`.)

**In Cursor immediately if queue fills:**

1. Click **Stop** (square by progress %).
2. **Do not** click “Start Multitasking”.
3. Composer: **Cmd+A** → **Delete**.
4. Close spam-filled agent chat; start **new** chat if needed.
5. Close browser tabs on `http://127.0.0.1:13020/`.

---

## 5. Permanent law (non-negotiable)

1. **Never** auto-paste or auto-copy into Cursor from Sina Command, Live agents, prompt queue, or agent loop unless founder **explicit opt-in file** exists.
2. **Closing Sina Command** must not leave injection running — hub must stop or `/shutdown` on quit (product follow-up).
3. **Live agents** = founder sees messages in **Live agents tab** only; maintainer reads inbox **only when founder opens this chat**.
4. **No timer-driven** inbox reads in Cursor rules or panel JS.
5. **Morning dispatch** writes files only; does not inject into Cursor chats by default.
6. **remote_ops** scheduler must stay **paused** until founder explicitly resumes (after reviewing this report).

---

## 6. Files to read before any paste/inject work

| Priority | File |
|----------|------|
| 1 | This report |
| 2 | `scripts/auto_prompt_guard.py` |
| 3 | `scripts/clipboard_safe.py` |
| 4 | `scripts/kill-sina-command.sh` |
| 5 | `scripts/intelligence_circle.py` (`send_to_cursor_maintainer`) |
| 6 | `.cursor/rules/sina-command-maintainer.mdc` (SinaaiDataBase) |

---

## 7. Verification checklist (executor runs after changes)

```bash
# 1) Kill everything
~/Desktop/SourceA/scripts/kill-sina-command.sh

# 2) Port free
lsof -i :13020   # expect empty

# 3) Inject blocked
cd ~/Desktop/SourceA/scripts && python3 -c "
from agent_loop import inject_cursor_chat
print(inject_cursor_chat('[SINA_LIVE_MAINTAINER] test'))
"

# 4) remote_ops paused
python3 -c "import json; from pathlib import Path; print(json.loads(Path('~/Desktop/SinaPromptOS/logs/remote_ops_state.json').expanduser().read_text()).get('paused'))"
```

Expected: `blocked` / `skipped`, port free, `paused: True`.

---

## 8. Open follow-ups (product)

- [ ] Sina Command.app calls **POST /shutdown** on quit so hub never outlives UI.
- [ ] Rebuild panel after `app.js` changes: `python3 scripts/build-sina-command-panel.py` (executor only).
- [ ] Remove or rewrite Prompt feed copy that still says “paste into Cursor automatically” in built `command-data.json` hero text.
- [ ] Document how founder **resumes** remote_ops safely (`paused: false` only after explicit approval).

---

## 9. Incident log (founder-visible symptoms)

- “App closed but Cursor still gets spam”
- “EVERY SECOND AUTO PROMPT”
- “every mins sending [SINA_LIVE_MAINTAINER]…”
- “8 Queued to Send” with TrustField + maintainer + KILL AUTO PASTE lines
- “i dont wanna span auto copy shit”

---

**LOCKED:** Do not re-enable auto-paste in code or docs without a new version of this file and explicit ASF approval.
