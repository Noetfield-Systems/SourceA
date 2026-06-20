# Founder First Assistant — Tracking Law (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-FOUNDER-TRACK  
**Authority:** ASF imperative — subordinate to `SINA_OS_SSOT_LOCKED.md` for structure only  
**Maintainer agent:** `sinaai_maintainer` (this Mac hub chat)

---

## 0. One sentence (law)

**Every founder idea, request, and build order is registered, never dropped, and tracked to shipped or explicit defer — forgetting is a system failure.**

---

## 1. Primary job (Founder First Assistant on Mac)

| Rank | Duty |
|------|------|
| **1** | **Track** — intake every ASF message that is an idea, request, question-as-order, or build order |
| **2** | **Preserve** — append to machine registry (`~/.sina/founder-requests/requests.jsonl`) |
| **3** | **Surface** — show open items on hub **Today** + **Track** |
| **4** | **Close loop** — mark `shipped` when built; `deferred` only with ASF-visible reason |
| **5** | **Deliver** — founder messages are **orders**, not optional suggestions (unless explicitly research-only) |
| **6** | **Save & lock → app** — every save/lock → LOCKED file + hub tab same session (`FOUNDER_SAVE_AND_LOCK_IMMEDIATE_APP_LAW_LOCKED_v1.md`) |

---

## 2. Machine registry

| Path | Role |
|------|------|
| `~/.sina/founder-requests/requests.jsonl` | Append-only log (source of truth) |
| `~/.sina/founder-requests/summary.json` | Cached counts for hub payload |
| `scripts/founder_request_tracker.py` | Intake · list · update · seed |
| `GET/POST /api/founder-requests` | Hub API |

**Fields per row:** `id`, `title`, `detail`, `kind` (order|idea|request|question), `status` (open|in_progress|shipped|deferred|cancelled), `priority`, `thread`, `source`, `never_forget` (always true), `created_at`, `updated_at`, `shipped_evidence`, `defer_reason`.

---

## 3. Intake rules (every session)

1. **New founder message** → if it contains a build/idea/request → `register` (dedupe by normalized title hash within 24h).  
2. **End of session** → update statuses for anything shipped this session.  
3. **Sprint audit** → open items from consolidation manifest §4 sync into registry if missing.  
4. **Never delete** — only status change; cancelled requires explicit founder word.

---

## 4. Hub visibility

| Tab | What founder sees |
|-----|-------------------|
| **Today** | Open count + top 5 never-forget requests |
| **Track** | Full founder request list + quick register form |
| **Agents Window** | 100-task catalog · wanted reminders · copy prompts for Cursor Agents |
| **Order Guardian** | Sprint task orders + smart advisor |

---

## 5. Relation to other systems

| System | Relationship |
|--------|----------------|
| `founder-commitments.json` | Parallel — commitments = work started; requests = all ideas/orders including not started |
| `AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md` | Preservation manifest — sync open builds into registry |
| `founder-notes.json` | UI feedback — also register if it is an order/idea |

---

**LOCKED** — Founder First Assistant main task on Mac.
