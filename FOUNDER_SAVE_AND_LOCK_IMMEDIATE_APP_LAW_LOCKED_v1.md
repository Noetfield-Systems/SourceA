# Founder save & lock — immediate file + app law (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-06-SAVE-LOCK-APP  
**Parent:** `FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md` · `ORDER_GUARDIAN_AGENT_LOCKED_v1.md`

---

## 0. One sentence (law)

**When ASF says save, lock, or never forget — write a LOCKED file in SourceA or the correct Desktop/repo source, mirror to machine registry, and surface in Sina Command the same session — no chat-only memory.**

---

## 1. Where content lives (priority order)

| Tier | Where | When |
|------|-------|------|
| **1** | `~/Desktop/SourceA/*.md` LOCKED | Hub laws, founder guides, maintainer builds |
| **2** | Desktop lane repo (`Noetfield`, `SinaaiMonoRepo`, etc.) | Portfolio / product scope |
| **3** | `~/.sina/**` jsonl registries | Machine truth for hub payload |
| **4** | Online (git push, cloud doc) | After Mac LOCKED + hub — not instead of |

---

## 2. Same-session app rule (100%)

Every save/lock MUST appear in hub **before session ends**:

| Content type | Hub surface |
|--------------|-------------|
| Build orders | Order Guardian + Track + Today |
| Agent Window tasks | **Agents Window** tab + Today reminder |
| Ideas / requests | Track + founder-requests registry |
| Laws / guides | Doc library + Essentials read chain |
| Fleet activation | Order Guardian `needs_activation` |

**Relatable place:** match founder mental model — agent tasks → Agents Window tab; orders → Order Guardian; daily → Today.

---

## 3. Maintainer duty (every intake)

1. **File** — create or update LOCKED `.md` at canonical path  
2. **Registry** — append/update `~/.sina/` jsonl via python module  
3. **Wire** — `important_docs_index.py` · `hub_essentials_index.py` · `sina_command_lib.py`  
4. **UI** — tab, card, or Today strip in `app.js`  
5. **Rebuild** — `build-sina-command-panel.py` + server route if API  
6. **Audit** — `audit_essentials_nav.py` if NAV changed  

---

## 4. Reminder chain

Order Guardian + Today read live state → **point founder to the right tab** → **copy prompt for Cursor Agents Window** when task is agent-window work.

**LOCKED** — forgetting a save/lock order is a system failure equal to dropping a build order.
