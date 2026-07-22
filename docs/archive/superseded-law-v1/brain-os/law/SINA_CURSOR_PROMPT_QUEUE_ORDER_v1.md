> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# Order for Cursor agents — Prompt queue (LOCKED)

**Version:** `SINA-PROMPT-QUEUE-1.0`  
**For:** Any Cursor agent chatting with ASF (Sina) in the **meta / Command** workspace.

---

## Rule (machine order — SSOT)

**Execution + live next-10 display:** `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md`  
Super Fast Hub (`http://127.0.0.1:13020/`) shows **queue line + task** — live next 10 on disk at `~/.sina/live-ongoing-prompts-next-10-v1.json`.  
**Legacy monolith** (Hub = Sina Command = `/legacy/`) is **archive only** — never daily founder path.

## Rule (optional): AI commentary on last reply

When meta chat needs founder-readable big picture (not execution order):

1. `POST /api/prompt-direction` with `set_context` then `propose`.
2. Summarize **direction_title** + **big_picture** in chat for Sina.
3. Sina may tap **Confirm** for optional commentary stamp — does **not** replace machine order.
4. Do **not** call `confirm` unless Sina asked in chat.

## Rule (legacy): Manual queue

When Sina is chatting with you **here** (planning, Command, multi-repo coordination), you may add **individual** prompts to the queue. Sina does **not** type them. The hub delivers each prompt into Cursor (clipboard + auto-paste).

---

## Direction API

| action | body |
|--------|------|
| `set_context` | `last_response`, optional `user_note` |
| `propose` | `{}` — needs OpenRouter |
| `confirm` | `{}` — optional commentary stamp only (`auto_feed: false`; machine order unchanged) |
| `cancel` | `{}` |

## How to add prompts manually (pick one)

### A) HTTP API (preferred)

```bash
curl -s -X POST http://127.0.0.1:13020/api/prompt-queue \
  -H "Content-Type: application/json" \
  -d '{"action":"add","title":"TrustField — verify E2E","repo":"trustfield","text":"FULL PROMPT HERE..."}'
```

Batch:

```json
{"action":"add_batch","items":[{"title":"Mono — P0","repo":"sinaai_mono","text":"..."},{"title":"Step 2","text":"..."}]}
```

### B) Shell helper

```bash
~/Desktop/SourceA/scripts/agent-queue-prompt.sh add-text "MergePack ship check" "Paste this into the MergePack chat: ..."
~/Desktop/SourceA/scripts/agent-queue-prompt.sh add "TrustField daily" trustfield ~/Desktop/SinaPromptOS/outputs/ready_to_paste/ready_to_paste_trustfield.txt
```

### C) Load today’s five-repo dispatch (after dispatch ran)

```bash
curl -s -X POST http://127.0.0.1:13020/api/prompt-queue -d '{"action":"load_dispatch"}'
```

Or use legacy queue tab `/legacy/?tab=prompt-feed` **archive only** — daily = Super Fast Hub **Next steps**.

---

## Your workflow each turn

1. **End your reply** with what you queued (titles only), e.g. “Queued 3 prompts: TrustField E2E, Mono ingest, Follow-up question.”
2. Add prompts **in run order** — first prompt = first delivered.
3. Use `repo` when the prompt belongs in a **specific repo chat** (`trustfield`, `sinaai_mono`, `virlux`, `noetfield`, `seven77`).
4. Keep each prompt **self-contained** (IMPLEMENT + scope + done criteria), same quality as `ready_to_paste_*.txt`.
5. Do **not** ask Sina to copy from markdown or run Terminal.

---

## What Sina does (zero typing)

1. Open **Super Fast Hub** — `http://127.0.0.1:13020/` (default; not `/legacy/`).
2. See **Worker task · queue · auto-heal · Judge · Thread · Safety**.
3. Machine order = disk queue — no Confirm gate · no legacy queue tab for daily ops.

**Vocabulary:** **Hub = Sina Command = legacy monolith** (`/legacy/`). Same product, archived for daily use per `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md`.

---

## After a repo chat finishes

Sina taps **Ingest clipboard** on **Daily** or **Actions** (or you run ingest via API). Then deliver the next queued prompt.

---

## API reference

| action | body |
|--------|------|
| `list` | `{}` |
| `add` | `title`, `text`, optional `repo`, `thread` |
| `add_batch` | `items: [{title, text, repo?}, ...]` |
| `load_dispatch` | `{}` |
| `deliver_next` | optional `"paste": false` (clipboard only) |
| `mark_done` | `id` |
| `skip` | `id` |
| `clear` | optional `only_pending: true` |
| `auto_feed` | `enabled: true/false` |

---

*Founder UI: Super Fast Hub `/` · Legacy archive: `/legacy/` (Hub = Sina Command) · Data: `~/.sina/live-ongoing-prompts-next-10-v1.json`*
