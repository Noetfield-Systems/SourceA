# Agent filed wrong incident ID without registry check — INCIDENT-015 (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-015  
**Classification:** MANDATORY READ — **every Cursor executor** before creating incident ids, LOCKED docs, or governance events  
**Canonical pointer:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-10 (founder: “why incident 11 when 11 already exists?”)  
**Related:** INCIDENT-010/012/013 id collision history · `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` · `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` · `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md`  
**Supersedes / wrong filing:** `~/.sina/agent-governance-events.jsonl` line `INCIDENT-011-brain-column-display-drift` — **void**; use **INCIDENT-014** for that subject  
**Tags:** `INCIDENT-015`, `governance`, `incident-registry`, `id-collision`, `fragmentation`, `brain-mistake`

---

## 1. Executive summary

After the monitor Brain PEND trust event, the Cursor **executor agent** logged a governance event and verbally labeled it **“INCIDENT-011”** for the monitor snapshot-drift subject.

**INCIDENT-011 is already assigned** logged to a **different, P0 subject**:

> **REWRITE treated as unauthorized disk edit** — `SINA_AGENT_REWRITE_UNAUTHORIZED_DISK_EDIT_INCIDENT_REPORT_v1.md`

**Severity:** **High** (governance / fragmentation) — same failure class as mistaken **INCIDENT-010** reuse for goal_progress (fixed by canonical **INCIDENT-013**).

**One-line law:**

> **Never assign `INCIDENT-NNN` without reading `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` + `rg INCIDENT-NNN brain-os/incidents/` — next free id only.**

---

## 2. What the agent did wrong

| Step | Expected (law) | What happened |
|------|----------------|---------------|
| 1 | Read `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` | **Skipped** |
| 2 | `rg 'INCIDENT-011' SourceA/brain-os/incidents/` | **Skipped** |
| 3 | Next free id = **014** (after 013; 012 superseded) | Used **011** in chat + jsonl |
| 4 | LOCKED body → `brain-os/incidents/` + root pointer | **Skipped** — chat + jsonl only |
| 5 | Add registry row | **Skipped** |

**Written artifact (wrong):**

```json
{"id": "INCIDENT-011-brain-column-display-drift", ...}
```

in `~/.sina/agent-governance-events.jsonl` — **not** canonical SSOT; **collides** with INCIDENT-011 REWRITE.

---

## 3. Why this is serious

1. **Duplication / fragmentation** — two subjects, one number (founder forbids this explicitly).  
2. **Brain role violation** — inventing governance ids without disk check (same arc as INCIDENT-005a critic-as-law).  
3. **Downstream harm** — agents read “INCIDENT-011” and load **REWRITE** law instead of **monitor Brain column** law.  
4. **Trust compounding** — followed a trust incident with a **governance incident**.

---

## 4. Correct filing (remediation)

| Subject | Correct ID | LOCKED body | Root pointer |
|---------|------------|-------------|--------------|
| Monitor Brain PEND / snapshot drift | **INCIDENT-014** | `brain-os/incidents/SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md` | `SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_REPORT_LOCKED_v1.md` |
| This id-collision mistake | **INCIDENT-015** | This file | `SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_REPORT_LOCKED_v1.md` |

**Void:** any reference to **INCIDENT-011** for monitor Brain column — cite **INCIDENT-014** only.

**jsonl:** append supersession event; do not delete history — mark `supersedes_id: INCIDENT-011-brain-column-display-drift` → `INCIDENT-014`.

---

## 5. Mandatory procedure — new incident (agents)

```bash
# 1) Registry — next free NNN
rg '^\| \*\*[0-9]' ~/Desktop/SourceA/brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
ls -1 ~/Desktop/SourceA/brain-os/incidents/SINA_*INCIDENT*.md

# 2) Collision check
rg 'INCIDENT-0XX' ~/Desktop/SourceA/brain-os/incidents/ ~/Desktop/SourceA/SINA_*INCIDENT*

# 3) Write LOCKED body in brain-os/incidents/
# 4) Write root pointer at SourceA/
# 5) Add ONE row to AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
# 6) Optional: ecosystem_incidents_index.py hub row
# 7) POST agent-review — never jsonl-only for canonical incidents
```

**Forbidden:**

- Chat-only incident ids  
- Reusing 010 / 011 / 012 (known collision history)  
- `archive/attachments/` or `RESEARCH/` as canonical incident home  
- Parallel prose in compendium without registry row  

---

## 6. Insights for next agents

### 6.1 Two incidents from one founder session

When founder reports monitor vs agent mismatch:

1. File **technical** incident (here: **014** monitor semantics).  
2. If agent mis-filed ids — file **governance** incident (**015**) separately — **never** reuse numbers.

### 6.2 Brain vs executor

- **Brain** routes and picks ids — still must **read registry** before naming.  
- **Executor** writes LOCKED bodies only with registry slot + `EDIT ALLOWED` when touching SourceA law.

### 6.3 Compendium vs registry

`SINA_ECOSYSTEM_INCIDENTS_AND_SESSION_INSIGHTS_COMPENDIUM` chronology **≠** authority to assign ids. **Registry table wins.**

---

## 7. Never-again card

```text
About to say "INCIDENT-NNN"?
  STOP → open AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md
  STOP → rg INCIDENT-NNN logged
  If taken → next free id (014, 015, …)
  Write LOCKED + pointer + registry row — same turn

Never log canonical incidents only in agent-governance-events.jsonl.
Never rename founder's trust event into a taken incident number.
```

---

## 8. Closeout checklist

- [x] INCIDENT-014 filed (monitor subject)  
- [x] INCIDENT-015 filed (this governance mistake)  
- [x] Registry updated  
- [x] Supersession note for wrong jsonl id  
- [x] `validate-incident-filing-v1.sh` machine gate (2026-06-10)  
- [ ] ASF: optional scrub mistaken chat refs to “INCIDENT-011 monitor”  

---

**END INCIDENT-015** — SA-2026-06-10-INCIDENT-015
