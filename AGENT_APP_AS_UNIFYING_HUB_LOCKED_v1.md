# Sina Command as unifying hub (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Parent:** `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md`  
**Full blueprint:** `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` — roles, tasks, access, APIs, all 8 agents  
**Hub entry:** `http://127.0.0.1:13020/?tab=council-room`

---

## 0. Law (one sentence)

**Sina Command is the pre-unifying place for all agent chats and repos — ASF does not re-paste rules per agent; the app shows one whole-system brief.**

---

## 1. Agent session start (every time)

| Step | Tab | Why |
|------|-----|-----|
| 1 | **Council Room** | Whole-system brief + all rules visible + mind share + paradoxes |
| 2 | **Private agents** → *your page* | Lane governance, loop, repo lens |
| 3 | **Your repo** (Cursor) | Implementation only in allowed `repo_root` |
| 4 | **Back / Council** | Post insight; check conflicts; never duplicate founder paste |

**Forbidden:** Starting a repo chat without reading Council Room brief when hub is up.

---

## 2. What is visible to ALL agents (same surface)

- Essentials **read chain** (every locked law — click to open)
- **Authority index** topics (what wins on conflict)
- **Founder law** (no Terminal)
- **Edit lock** (no SourceA except maintainer)
- **Founder orders** (MASTER_ORDERS active items)
- **Founder directives** (`~/.sina/founder-directives.jsonl` — ASF additions)
- **9 repo lenses** (compare lanes)
- **Mind share** + **paradox board**
- **P0 + WTM step** (accurate progress snapshot)

No agent gets a private rule list that omits global laws.

---

## 3. Unify conflicts → progress

| Signal | Where | Action |
|--------|-------|--------|
| Law vs law | Conflict Room | ACE triage → continue work |
| Opinion vs opinion | Council paradox board | Mind share → ASF decides |
| Hub bug | Backlog agent reports | Maintainer implements |
| New ASF rule | Founder directive form in Council | Appends to unified brief on refresh |

---

## 4. One copy brief

Council Room → **Copy whole-system brief** — paste **once** at top of any Cursor agent chat. Replaces repeated founder copy-paste.

Machine source: `scripts/agent_system_unified.py` → payload `system_unified`.

---

## 5. Maintainer

When adding a rule ASF said in chat only:

1. Add via Council Room **Founder directive** (or edit canonical LOCKED doc)  
2. `python3 scripts/build-sina-command-panel.py`  
3. All agents see it on next hub open — no per-agent paste
