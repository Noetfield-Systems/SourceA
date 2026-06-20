# Research intake & save — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Authority:** ASF order · sits under `UNIFIED_RESEARCH_ROOT_LOCKED_v1.md` (machine registry)  
**Human mirror SSOT:** `~/Desktop/SourceA/RESEARCH/`  
**Enforcer:** `RESEARCH/_GOVERNANCE/research_save_enforcer.py`

---

## 0. One sentence

> **Every research artifact or research-backed decision gets a worker trace tag, mirrors into `SourceA/RESEARCH/by_date/`, registers in `~/.sina/research-root/`, and passes `research_save_enforcer.py verify` before closeout — chat alone is not SSOT.**

---

## 1. Mandatory 4-step save (no exceptions)

| Step | Action | Fail if skipped |
|------|--------|-----------------|
| **1** | Write artifact to canonical worker vault (YAML/MD) with **full trace_id** in header | Unregistered research |
| **2** | Mirror to `RESEARCH/by_date/{date}/{worker_id}/{subject}/{trace_id}/` + `_META.yaml` | No founder-visible audit trail |
| **3** | `python3 RESEARCH/_GOVERNANCE/research_save_enforcer.py save --path …` (or manual mirror + `verify`) | Path/tag drift |
| **4** | `python3 ~/Desktop/SourceA/scripts/research_root_sync.py register` + `sync` | Cores cannot consume |

**Workers:** run step 3 `verify` in **pre_ship** before declaring round done.

---

## 2. Path law (LOCKED)

```
RESEARCH/by_date/{YYYY-MM-DD}/{worker_id}/{subject_slug}/{trace_id}/{filename}
RESEARCH/by_date/{YYYY-MM-DD}/{worker_id}/{subject_slug}/{trace_id}/_META.yaml
```

Registries: `RESEARCH/_GOVERNANCE/SUBJECTS_REGISTRY.yaml` · `WORKERS_REGISTRY.yaml`  
Process detail: `RESEARCH/_GOVERNANCE/RESEARCH_INTAKE_STANDARD_v1.md`

**Forbidden save locations:** `archive/attachments/` for new research · ad-hoc SourceA root folders · chat-only decisions.

---

## 3. Worker IDs & tag prefixes (LOCKED)

| worker_id | trace_id pattern |
|-----------|------------------|
| `research_acquisitor` | `RESEARCH-ACQUISITOR-REF-YYYY-MM-DD-*` or `RESEARCH-ACQUISITOR-YYYYMMDD-*` |
| `commercial_goal_specialist` | `COMMERCIAL_GOAL-REF-YYYY-MM-DD-*` |
| `governance_goal_specialist` | `governance_goal_specialist-YYYYMMDD-NNN` |
| `worker` (site/build) | cite parent blueprint trace + `producer: worker` on register |

Generic prefixes (`RA-MKT`, `GOVGS`, `TF-COMM`) are **superseded** — reject on verify.

---

## 4. Subject slugs (LOCKED list)

`trustfield` · `noetfield` · `dual_brand` · `voice_ai` · `ai_dev` · `automation` · `mergepack` · `virlux` · `seven77` · `sina_os` · `wire` · `investor` · `ecosystem`

New slug → ASF names product → update `SUBJECTS_REGISTRY.yaml` first.

---

## 5. Closeout YAML (required fields)

Every worker closeout that contains research or a research-backed decision **must** include:

```yaml
research_save:
  trace_id: {full tag}
  worker_id: {agent_id}
  subject: {subject_slug}
  vault_path: {canonical vault file}
  research_mirror_path: RESEARCH/by_date/...  # relative to SourceA
  enforcer_verify: PASS  # from research_save_enforcer.py verify
  execution_authority: false
```

**Ship gate:** `enforcer_verify` must be `PASS`. FAIL blocks closeout.

---

## 6. Enforcement commands

```bash
# Save + mirror + index (preferred)
python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py save \
  --path <vault_file> --worker <worker_id> --subject <subject_slug> --trace-id <trace_id>

# Verify one artifact folder
python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py verify \
  --trace-id <trace_id>

# Audit entire RESEARCH tree
python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py audit

# Machine registry (existing law)
python3 ~/Desktop/SourceA/scripts/research_root_sync.py register --path <vault_file> --producer <worker_id> --bucket <bucket>
python3 ~/Desktop/SourceA/scripts/research_root_sync.py sync
```

---

## 7. What counts as “research-related decision”

- Market comps, pricing, SKU naming, GTM motion  
- Legal/entity/money-flow constraints  
-  landscape, success models  
- Worker blueprints, considerations, mission outputs  
- Any doc cited as evidence in a build or GTM choice  

If it influences **what we sell, how we sell, or what we build** → full 4-step save.

---

## 8. Worker notice (paste entry)

Full paste prompt for all workers:  
`RESEARCH/_GOVERNANCE/WORKER_NOTICE_RESEARCH_SAVE_MANDATORY_v1.md` §PASTE BLOCK

---

## 9. Related law

| Doc | Path |
|-----|------|
| Unified research root | `brain-os/system/UNIFIED_RESEARCH_ROOT_LOCKED_v1.md` |
| Agent skills pipeline | `AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md` |
| Intake standard | `RESEARCH/_GOVERNANCE/RESEARCH_INTAKE_STANDARD_v1.md` |
| Cursor rule | `.cursor/rules/research-save-mandatory.mdc` |

---

*End RESEARCH INTAKE AND SAVE LOCK v1*
