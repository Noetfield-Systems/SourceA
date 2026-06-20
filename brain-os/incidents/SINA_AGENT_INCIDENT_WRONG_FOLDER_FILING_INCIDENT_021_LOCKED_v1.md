# INCIDENT-021 — Incident filed outside canonical folder (registry skip)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**Class:** Governance · incident filing hygiene · agent miss  
**Reporter:** ASF  
**Wrong agent:** **Cursor Worker** (`Auto` · SourceA Worker chat · 2026-06-10 session)  
**sequence_id:** SA-2026-06-10-INCIDENT-021  
**Opened:** 2026-06-10  
**Law violated:** `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` § One rule

---

## 1. What happened

ASF required **all incidents in the same folder**. Audit found **INCIDENT-018, 019, 020** (and a superseded S10/bash tombstone) existed **only at SourceA repo root** as full LOCKED bodies — **not** in `brain-os/incidents/`.

Meanwhile `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` already defines:

| Layer | Path |
|-------|------|
| **LOCKED body (canonical)** | `brain-os/incidents/SINA_*_INCIDENT_*_LOCKED_v1.md` |
| **Root pointer** | `SourceA/SINA_*_INCIDENT_*_REPORT_LOCKED_v1.md` (summary + path) |

**INCIDENT-017** was filed correctly (body in `brain-os/incidents/` + root pointer). **016** had body in `brain-os/incidents/` but was **missing from registry table**.

---

## 2. Who did wrong

| Agent | Role | Chat | Actions |
|-------|------|------|---------|
| **Auto** | SourceA Cursor Worker | This Worker session (S10 + monitor + bash thread) | Wrote INCIDENT-018 full body at root only; wrote INCIDENT-019/020 at root only; did not update registry; created `SINA_S10_WRONG_BASH_CWD_INCIDENT_019` at root (wrong topic + wrong layer) |

**Not a subsystem bug** — **filing procedure violation** by the executor agent.

---

## 3. Violations

| # | Rule | Violation |
|---|------|-----------|
| V1 | Canonical body in `brain-os/incidents/` | 018 · 019 · 020 bodies at root only |
| V2 | New incident → add registry row | 016–020 absent from index table |
| V3 | Session-start `ls brain-os/incidents/SINA_*INCIDENT*` | Agent skipped registry read before filing |
| V4 | INCIDENT-015 class | Filed ids without registry check (repeat pattern) |

---

## 4. Root cause

1. Agent treated **repo root** as incident home (convenience) ignoring existing **two-layer** law.  
2. **No registry update** after assigning INCIDENT-018/019/020.  
3. **Disk-first miss loop** wrote files fast without `AGENT_INCIDENTS_REGISTRY` gate.  
4. Same session also conflated topics (INCIDENT-020) — rushed filing.

---

## 5. Remediation (disk — this session)

| Action | Result |
|--------|--------|
| Move canonical bodies | `brain-os/incidents/SINA_*_INCIDENT_018/019/020_LOCKED_v1.md` |
| Thin root pointers | Root `*_REPORT_LOCKED_v1.md` → summary + path only |
| Registry rows | 016 · 017 · 018 · 019 · 020 · **021** added to index |
| Tombstone | `SINA_S10_WRONG_BASH_CWD_INCIDENT_019` → superseded pointer |
| This incident | INCIDENT-021 documents the filing miss |

---

## 6. Filing checklist (mandatory)

```
1. rg INCIDENT- brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md  → next id
2. Write FULL body → brain-os/incidents/SINA_*_INCIDENT_NNN_LOCKED_v1.md
3. Write thin pointer → SourceA/SINA_*_INCIDENT_NNN_REPORT_LOCKED_v1.md
4. Add ONE row to AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
5. Never full incident body only at root · never archive/attachments for canonical ids
```

**Verify:**

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA && ls -1 brain-os/incidents/SINA_*INCIDENT*0{16,17,18,19,20,21}*
```

---

## 7. Never forget

- **One folder for canonical incidents:** `brain-os/incidents/`  
- **Root = pointer only** (except WTM adjunct `brain-os/wtm/` per registry)  
- **Name the agent** who filed wrong — do not blame the subsystem  
- ASF: "all incidents same folder" = this rule — non-negotiable

**LOCKED** — canonical body · `brain-os/incidents/`
