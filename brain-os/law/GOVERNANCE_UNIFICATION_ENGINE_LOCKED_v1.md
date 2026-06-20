# Governance Unification Engine (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-GOV-UNIFY  
**Authority:** ASF · subordinate to `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md`  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §10  
**Companion:** `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md`

---

## 0. Purpose

When ASF sends **new rules, essays, governance, or docs** (single paste or batch), agents run this engine **once per intake** to:

1. **Analyze** — helpful or not vs mission, policy, roadmap, goals  
2. **Unify** — merge into existing canonical LOCKED docs (pointers, not duplicate prose)  
3. **Archive** — move superseded versions to `archive/superseded/`  
4. **Maintain in-charge registry** — authority index + machine SSOT always current  

**Chat is input. LOCKED source at root is truth. Unification reduces fragmentation.**

---
**Canonical WTM map:** `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`


## 1. In-charge registry (always know what wins)

| Need | Canonical |
|------|-----------|
| Law list | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` |
| Agent router | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` |
| Compare procedure | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` (Orders 1–12) |
| Judgment + line | `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` |
| WTM build truth | `scripts/system_roadmap.py` + `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` |
| Mission / P0 | `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` |
| Ecosystem apex | `SINA_OS_SSOT_LOCKED.md` |
| Chronology | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` |

**Rule:** After every unification pass, update **authority index row** + **registry addendum** if version bumped.

---

## 2. Intake classes

| Class | Examples | Default action |
|-------|----------|----------------|
| `ASF_ORDER` | “Lock this”, “add to authority law” | Execute unification if explicit |
| `GOVERNANCE_DRAFT` | New rule essay, policy prose | Analyze → unify or attach |
| `EXTERNAL_CRITIC` | GPT audit paste | Compare only — Orders 1–6 unless ASF adopts |
| `COMPANION` | Phase chapter, blueprint section | Pointer + cross-link — not new law |
| `DUPLICATE` | Restates existing LOCKED doc | Reject — cite canonical |
| `SUPERSEDE` | Replaces vN with vN+1 | Archive vN + bump version |

Label first line of agent reply with intake class when batch is mixed.

---

## 3. Unification pipeline (mandatory)

```
INTAKE → INVENTORY → SCORE → MAP → MERGE → ARCHIVE → SYNC → VERIFY
```

### Step 1 — INTAKE

- Collect **all** items in the batch (do not drop “smaller” sections).  
- One **intake manifest** table: id, title, claimed topic, source (ASF / GPT / other).

### Step 2 — INVENTORY

For each item, locate existing canonical doc from authority index.  
Output: `existing_canonical | none | partial_overlap`.

### Step 3 — SCORE (helpful?)

Score each item **against** (not in place of):

| Lens | Source |
|------|--------|
| Mission | SSOT + unified blueprint |
| Policy | Alignment law, authority law, critic law |
| Roadmap | `system_roadmap.py` step truth |
| Goals | Command center P0, WTM `do_now` |
| Incidents | Known failures — does this prevent repeat? |

Verdict per row: **ADOPT** · **MERGE** · **ATTACH** · **REJECT** · **DEFER**

| Verdict | Meaning |
|---------|---------|
| **ADOPT** | New topic — new LOCKED doc v1 at root |
| **MERGE** | Same topic — patch canonical doc in place |
| **ATTACH** | Unconvinced extra — `archive/attachments/<track>/` only |
| **REJECT** | Contradicts, duplicates, or wrong rank |
| **DEFER** | Needs ASF clarify before any file move |

### Step 4 — MAP

For **ADOPT** / **MERGE**: exact target file, section, and whether machine mirror updates (`system_roadmap.py`, cursor rule, audit).

**One topic → one canonical doc.** No parallel law tables.

### Step 5 — MERGE

- Edit **one** canonical file per topic.  
- Add **pointers** in companions — never restate full rule prose.  
- Expand only where SSOT gap is proven.  
- Stable step IDs and phase order **unchanged** unless ASF_ORDER + migration law.

### Step 6 — ARCHIVE

When superseding `*_LOCKED_vN.md`:

1. Move old file → `archive/superseded/<track>/vN/`  
2. Add row → `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md` (or track manifest)  
3. Root retains **only** active vN+1  
4. Update all pointer docs (governance entry, index, MAP_POINTER_DOCS in audit)

### Step 7 — SYNC

| Surface | Action |
|---------|--------|
| `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | Version + row |
| `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` | Addendum row |
| `system_roadmap.py` | `WTM_LOCKED_DOCS`, `authorities` if WTM/governance |
| `.cursor/rules/*.mdc` | Thin always-on pointer if agent-facing |
| `important_docs_index.py` | One row if hub-visible |
| `audit_hub_source_alignment.py` MAP_POINTER_DOCS | If root locked doc added |

### Step 8 — VERIFY

```bash
cd ~/Desktop/SourceA/scripts
python3 audit_hub_source_alignment.py
python3 build-sina-command-panel.py
# + topic validators if build layer touched
```

**Done** only when audit OK (or known non-blockers documented).

---

## 4. Batch output template (agent delivers to ASF)

```markdown
## Unification report — [date]

### Intake manifest
| # | Title | Class | Verdict | Target |

### In-charge after pass
| Topic | Canonical doc | Ver |

### Merged / created
- ...

### Archived
- old → archive/superseded/...

### Rejected / attached
- ...

### Machine sync
- [ ] authority index  [ ] registry  [ ] hub build  [ ] audit OK
```

---

## 5. Anti-patterns (never)

- Create a **new** root LOCKED doc when topic already has canonical — **merge** instead  
- Leave **two** active versions at root  
- Paste critic tables into hub UI (INCIDENT-002)  
- Change `CURRENT_*_STEP` from essay alone  
- “Newest file on disk wins” — **authority index wins**

---

## 6. Relation to alignment law

| Engine step | Alignment order |
|-------------|-----------------|
| SCORE 1–6 | Orders 1–6 (compare, keep, attach) |
| MERGE 7–12 | Orders 7–12 (convince → sub-step → vN+1) |

**Convince gate:** ASF explicit yes for new topics or sub-steps — enthusiasm in essay is not approval.

---

**LOCKED** — Unification engine. Run on every governance/doc batch intake.

---

## 7. Policy Reasoning Machine (brain + discover pipeline)

**Purpose:** Proactive **find** + brain **reason** about what policy to draft, merge, lock, or enforce — without new fragmented docs.

| Role | Job |
|------|-----|
| **Brain** | Read `latest-scan-v1.json` · decide DRAFT/MERGE/LOCK/ENFORCE · route to maintainer — **never** chat-only policy |
| **Machine** | `~/.sina/policy-machine/policy_reasoning_pipeline_v1.py` — DISCOVER → REASON → RECOMMEND → EMIT |

### 7.1 Pipeline (extends §3 — runs before INTAKE when no batch pasted)

```text
DISCOVER → REASON → RECOMMEND → EMIT
   ↓ (if ASF batch pasted)
INTAKE → INVENTORY → SCORE → MAP → MERGE → ARCHIVE → SYNC → VERIFY  (§3)
```

### 7.2 Machine SSOT (one home — no parallel policy docs)

| Path | What |
|------|------|
| `~/.sina/policy-machine/REGISTRY.yaml` | Machine registry |
| `~/.sina/policy-machine/policy_reasoning_pipeline_v1.py` | Pipeline |
| `~/.sina/policy-machine/latest-scan-v1.json` | Brain reads this |
| `~/.sina/policy-machine/recommendations.jsonl` | Scan history |

**Delegates (do not duplicate):** `governance_drift_engine.py` · `agent_governance_unification.py` · `agent_rules_in_charge.py`

### 7.3 Discover sensors

| Sensor | Finds |
|--------|-------|
| `fragmentation` | Parallel policy in `~/.sina/brain/*_PICK_*` · `DEVBRIDGE_WEEK1_*` |
| `dup_locked_topic` | Multiple `*_LOCKED*` on same topic stem |
| `cursor_rule_sprawl` | Always-on `.mdc` restating LOCKED prose |
| `registry_anti_fragmentation` | Machine registries missing `anti_fragmentation` |
| `event_repeat` | Repeat kinds in `agent-governance-events.jsonl` → ENFORCE gap |
| `drift_aggregate` | Score &lt; 85 → fix before new law |
| `rules_in_charge` | What governs NOW snapshot |

### 7.4 Reason lenses (brain)

Score each finding: **mission** · **policy** · **roadmap** · **goals** · **incidents**

| Verdict | Brain action |
|---------|--------------|
| **DRAFT** | Propose one new LOCKED doc — ASF yes before write |
| **MERGE** | Append existing canonical — **anti-fragmentation mandatory** |
| **LOCK** | Run §3 MERGE step — founder words → disk |
| **ENFORCE** | Policy exists unwired — route validator/hook worker |
| **DEFER** | One ASF clarify question |

### 7.5 Commands (founder never runs — agents only)

```bash
python3 ~/.sina/policy-machine/policy_reasoning_pipeline_v1.py --reason
python3 ~/.sina/policy-machine/policy_reasoning_pipeline_v1.py --status
python3 ~/.sina/policy-machine/policy_reasoning_pipeline_v1.py --scan
```

**Run when:** session_start · founder_rule_change · post-unification · brain before recommending new law.

**Meta-reasoning parent:** `META_REASONING_POLICY_STACK_LOCKED_v1.md` L0–L2 (classify before lock).

### 7.6 Governance events taxonomy (ENFORCE — Maintainer 2)

**SSOT path:** `~/.sina/agent-governance-events.jsonl`  
**Writer:** `scripts/agent_governance_events.py`  
**Schema:** every row MUST have **`kind`** (canonical). Legacy **`event`** accepted at read — dual-write until backfill.

| kind (canonical) | Source | Notes |
|------------------|--------|-------|
| `workspace_selected` | hub / command | High volume |
| `prompt_router` | prompt queue | High volume |
| `execution_state_*` | execution kernel | running · verifying · failed |
| `governance_drift` | drift engine | Score runs |
| `policy_reasoning_scan` | policy machine | §7 pipeline |
| `essay_*` | essay discourse | submitted · best_marked |
| `incident_*` | incident room | filed · remediate · consolidate |
| `governance_*` | unification / harden | lock · remediation |

**ENFORCE deliverables (Maintainer 2):**

1. `log_governance_event` writes **`kind`** + legacy **`event`** (same value) — **SHIPPED 2026-06-13**
2. `governance_event_kind_v1.py` — `normalize_kind(row)` for all readers — **SHIPPED**
3. `validate-governance-events-taxonomy-v1.sh` — last 500 rows must have resolvable kind — **SHIPPED**
4. Wire normalize into `policy_reasoning_pipeline` · `monitor_honesty_lib` · spine readers — **SHIPPED**
5. **No new LOCKED doc** — taxonomy table lives in this §7.6 only

---

