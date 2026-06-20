# Agent → founder bash communication (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
status: LOCKED
doc_date: 2026-06-10
sequence_id: SA-2026-06-10-FOUNDER-BASH
topic: agent-founder-communication
-->

| | |
|--|--|
| **Version** | `AGENT-FOUNDER-BASH-1.0-LOCKED` |
| **Class** | Cross-cutting · agent communication hygiene |
| **Not** | S10 · factory drain · any single subsystem |
| **Incident** | `brain-os/incidents/SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_LOCKED_v1.md` |

**Parent:** `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md`

---

## 0. One sentence

When an agent shows shell to ASF, every line must be **cwd-safe** or **wrapper-safe** — never repo-relative alone; default is **no Terminal**.

---

## 1. Default (founder)

ASF uses **Sina Command one-tap** only. Agents run shell themselves or ship Actions (SinaaiDataBase lane).

**Forbidden:** asking ASF to copy `python3 scripts/...` from chat without cwd guard.

---

## 2. When bash is allowed in chat

ASF explicitly asks · maintainer debug doc · agent-run verify transcript (agent runs it, founder reads result).

Every block must use **one**:

1. `cd /Users/sinakazemnezhad/Desktop/SourceA && …` on **line 1**
2. Full absolute path to script/binary
3. `~/.sina/bin/<registered-wrapper>` (cwd-independent)

**Forbidden:**

```bash
python3 scripts/foo.py
bash scripts/bar.sh
```

**Required:**

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA && python3 scripts/foo.py
```

---

## 3. Wrapper registry

Machine wrappers live in `~/.sina/bin/`. Each wrapper sets fixed `ROOT` and `exec`s repo script.

Adding a wrapper ≠ changing subsystem law (e.g. S10). Wrappers are **communication ergonomics** only.

---

## 4. Incident filing (same session class)

Canonical incidents live in **`brain-os/incidents/`** only — root file is pointer. See `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` · INCIDENT-021.

---

## 5. Agent checklist before sending bash

- [ ] Is Terminal actually needed for ASF? If no → one-tap / read disk file instead.
- [ ] Line 1 has `cd` or absolute path or `~/.sina/bin/`?
- [ ] Topic is **communication** — not bundled into a subsystem incident title.

---

**LOCKED** — Founder bash communication. Subsystems (S10, drain, monitor) cite this; do not merge into subsystem law.
