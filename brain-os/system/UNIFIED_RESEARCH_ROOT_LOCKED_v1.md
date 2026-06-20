# Unified Research Root — one intake, filtered cores (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-06  
**Parent:** `CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md` · `AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md`  
**Purpose:** Single systematic loop for **all** research (lanes, workers, Research Acquisitor, external critic) → **one registry** → **filtered digests** → **reasoning cores** — without overloading Execution Core.

---

## 0. One sentence

> **All research registers once at `~/.sina/research-root/`; cores read filtered digests only; Execution Core never loads raw matrices.**

---

## 1. Problem (why this exists)

| Failure | Fix |
|---------|-----|
| Fragmented YAML in many vaults | One `registry.jsonl` + `INDEX.yaml` |
| Main brain overloaded | **Filter layer** — max digest size per core |
| Copy-paste between chats | **Mandatory register** after every research session |
| Lane research lost (Cursor OS Pro) | `lane-imports/` + register |
| Worker research ≠ product research | Same intake, different `producer` tag |

---

## 2. Architecture (full loop)

```text
PRODUCERS (any chat — never skip register)
  Research Acquisitor · Cursor OS Pro lane · TrustField GTM · Worker closeout
  · ChatGPT paste (external_critic) · Hub POST /api/agent-research
        ↓
INTAKE — registry.jsonl row (id, producer, path, bucket, confidence)
        ↓
BRIEF — normalized YAML in producer vault OR lane-imports/
        ↓
CRITIC SLOT — optional external_critic stance (challenge | support | extend)
        ↓
FILTER — research_root_sync.py scores + builds filtered/*.yaml (≤ size cap)
        ↓
CORE FEEDS (read only these + goal vaults)
  commercial.signal.yaml      → Commercial Goal Specialist
  governance.constraints.yaml → Governance Goal Specialist
  research.backlog.yaml       → Research Acquisitor (next sectors)
  execution_core.digest.yaml  → SourceA Execution Core (routing only)
        ↓
EXECUTION CORE SYNC → reconcile → ONE worker sa-XXXX
```

**Law:** No core reads `registry.jsonl` or raw lane matrices directly — only `filtered/` + own goal vault.

---

## 3. Single root (SSOT registry)

| Path | Role |
|------|------|
| `~/.sina/research-root/registry.jsonl` | **Master intake log** — append-only |
| `~/.sina/research-root/INDEX.yaml` | Machine manifest — all active artifacts |
| `~/.sina/research-root/filtered/commercial.signal.yaml` | Filtered $ signals |
| `~/.sina/research-root/filtered/governance.constraints.yaml` | Filtered risk constraints |
| `~/.sina/research-root/filtered/research.backlog.yaml` | Next research sectors |
| `~/.sina/research-root/filtered/execution_core.digest.yaml` | Routing digest only |

### Canonical vaults (pointers — do not duplicate files)

| Producer | Write path |
|----------|------------|
| Research Acquisitor | `~/.sina/agent-workspaces/research-acquisitor/briefs/` |
| Lane: Cursor OS Pro | `~/Desktop/Cursor OS Pro/docs/research/` + mirror `research-acquisitor/lane-imports/cursor_os_pro/` |
| Lane: TrustField | `~/Desktop/TrustField Technologies/docs/gtm/` |
| Lane: Noetfield | `SinaaiMonoRepo/SinaaiDataBase/noetfield/docs/` |
| Hub pipeline | `~/.sina/agent-research/items.jsonl` (linked into registry on sync) |
| Audits (evidence) | `SourceA/docs/system-audits/` (register as `producer: audit_export`) |

---

## 4. Registry row schema (LOCKED)

```yaml
id: rr-YYYYMMDD-uuid8
at: ISO8601
producer: research_acquisitor | cursor_os_pro | trustfield | worker | external_critic | audit_export | hub_pipeline
lane: sourcea | trustfield | cursor_os_pro | noetfield | archive
bucket: voice_agent | app_composition | market | compliance |  | internal_audit
artifact_path: absolute path to YAML or JSON
title: short
confidence: low | medium | high
critic_class: null | external_critic
status: intake | brief | filtered | promoted | archived
cores_target: [commercial, governance, research, execution_core]  # filter output
```

---

## 5. Mandatory producer policy (every researcher / worker)

### After ANY research session — do these 3 steps (no exceptions)

1. **Write artifact** to canonical vault (YAML preferred).  
2. **Register:**  
   ```bash
   python3 ~/Desktop/SourceA/scripts/research_root_sync.py register --path <artifact> --producer <id> --bucket <bucket>
   ```  
3. **Run sync** (founder one-tap or agent):  
   ```bash
   python3 ~/Desktop/SourceA/scripts/research_root_sync.py sync
   ```

**Chat alone is not SSOT.** Unregistered research does not exist for cores.

### Workers

- Workers **may** produce research as closeout evidence — **must register** with `producer: worker`.  
- Workers **do not** promote to LOCKED law without maintainer lane.  
- Workers **do not** replace Research Acquisitor — they **feed** the root.

### Research Acquisitor

- Expands sectors; maintains `research.backlog.yaml`.  
- **Never** assigns `sa-XXXX`.  
- Imports lane YAML as `source_type: internal_reference` — no duplicate matrices.

### External critic (ChatGPT paste)

- `producer: external_critic` · `critic_class: external_critic`  
- Goes to critic slot — **never** direct to Execution Core as orders.

---

## 6. Filter rules (what each core receives)

| Core | Reads | Max size | Filter keeps |
|------|-------|----------|--------------|
| **Commercial** | `filtered/commercial.signal.yaml` | 5 bullets + 5 verticals | ROI, pricing, GTM, channel |
| **Governance** | `filtered/governance.constraints.yaml` | 5 constraints | legal, risk, blockers |
| **Research** | `filtered/research.backlog.yaml` | 10 sector gaps | open sectors, sources needed |
| **Execution Core** | `filtered/execution_core.digest.yaml` + goal vaults | 1 page | reconcile summary, ONE worker hint |

**Execution Core does not read:** `voice_composition_market_brain_v1` full matrix, 200-company JSON, audit Part 1–17 — only digest + drill-down on demand.

---

## 7. Automation commands

| Command | Purpose |
|---------|---------|
| `research_root_sync.py register` | Append registry row |
| `research_root_sync.py sync` | Rebuild INDEX.yaml + filtered/*.yaml |
| `research_root_sync.py status` | Print counts + last sync |
| `POST /api/agent-research` | Hub intake (existing — sync links it) |

**Schedule:** Run `sync` after any register · before Execution Core SYNC · on hub Refresh (future Action).

---

## 8. Link to Controlled Execution OS

| OS part | Research root relationship |
|---------|---------------------------|
| Research Acquisitor | Producer + consumer of `research.backlog.yaml` |
| Commercial Goal Specialist | Consumes `commercial.signal.yaml` + writes goal vault |
| Governance Goal Specialist | Consumes `governance.constraints.yaml` + writes goal vault |
| Execution Core | Consumes digest + goal vaults → SYNC |
| Worker | Implements ONE pick after SYNC only |

---

## 9. Cursor OS Pro example (voice_composition)

1. Cursor OS Pro chat writes `voice_composition_market_brain_v1.yaml`  
2. Register: `producer: cursor_os_pro` · `bucket: voice_agent`  
3. Sync builds filtered slices (voice highlights → research.backlog; IAP winners → commercial.signal if revenue-relevant)  
4. Research Acquisitor v2 **imports** lane file — does not rebuild 200 matrix  
5. Execution Core reads digest only  

---

## 10. Anti-patterns (LOCKED forbidden)

- Raw research paste into Execution Core chat as SSOT  
- Skip register because "YAML exists"  
- Worker promotes research to `*_LOCKED*.md` without maintainer  
- Duplicate company rows across voice + composition buckets  
- Load full audit pack every brain session (use README_INDEX drill-down)  

---

## 11. Related paths

| Doc | Path |
|-----|------|
| This law | `os/chat-handoffs/UNIFIED_RESEARCH_ROOT_LOCKED_v1.md` |
| Hub pipeline | `AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md` |
| Controlled OS | `CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md` |
| Research paste | `GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md` §4 |
| Script | `scripts/research_root_sync.py` |

---

*End UNIFIED RESEARCH ROOT v1*
