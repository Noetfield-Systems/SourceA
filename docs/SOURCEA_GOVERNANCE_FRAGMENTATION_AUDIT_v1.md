# SourceA Governance Fragmentation Audit v1

**Saved at:** 2026-07-05T12:30:00Z  
**Scope:** `.cursor/rules/` (74 files) · `brain-os/law/` (296 files) · `docs/*INDEX*`  
**Method:** Read-only scan · topic clustering · conflict tagging

---

## Summary

| Metric | Count |
|--------|-------|
| Cursor rules (`.mdc`) | 74 |
| Always-apply rules | 9 |
| Brain-os law files | 296 |
| Competing SSOT indexes | 2 |
| High-conflict topics | 6 |
| Explicitly superseded law files | 35+ (archived in Step 6) |

---

## Fragmentation matrix

| Topic | Files claiming authority | Status |
|-------|------------------------|--------|
| **Governance entry / read order** | `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md` · `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` · `brain-os/law/entry/START_HERE_LOCKED_v1.md` · `brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | **CONFLICT** → unified: `SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1.md` |
| **Brain role** | `.cursor/rules/000-brain-unified.mdc` · `brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md` · `brain-os/law/SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` · `brain-os/memory/BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md` | **CONFLICT** → unified: `SOURCEA_BRAIN_AUTHORITY_UNIFIED_LOCKED_v1.md` |
| **Worker scope** | `.cursor/rules/000-entry-gate.mdc` · `.cursor/rules/sourcea-worker-inbox.mdc` · `brain-os/law/SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1.md` · `docs/CONTROLLED_AUTORUN_LAWS_v3.md` · `brain-os/law/enforcement/RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` | **CONFLICT** → unified: `SOURCEA_WORKER_SCOPE_UNIFIED_LOCKED_v1.md` |
| **Mac vs Cloud runtime** | `data/founder-execution-model-v1.json` · `.cursor/rules/mac-control-plane.mdc` · `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` · `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md` | **FRAGMENTED** → unified: `SOURCEA_UNIFIED_RUNTIME_MODEL_LOCKED_v1.md` |
| **Conflict resolution** | `.cursor/rules/ecosystem-rule-conflict-resolution.mdc` · `brain-os/law/AUTO_CONFLICT_ENGINE_V3_LOCKED.md` · `.cursor/skills/skill-007-ecosystem-conflict-resolution/SKILL.md` | **DUPLICATE** → precedence in unified entry |
| **Cross-lane edit / SAVE WORK EDIT** | `.cursor/rules/000-cross-lane-edit-forbidden.mdc` · `brain-os/law/enforcement/AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` · `.cursor/rules/001-founder-verbs-rewrite-save-asf-mandatory.mdc` | **ACTIVE** (layered, not conflicting) |

---

## Always-apply rules (9)

| Rule | Why always-on |
|------|----------------|
| `000-entry-gate.mdc` | Session routing Brain vs Worker |
| `000-cross-lane-edit-forbidden.mdc` | SAVE · WORK · EDIT ALLOWED gate |
| `000-workspace-lock.mdc` | Repo boundary |
| `034-mac-no-validator-stuck-red-flag.mdc` | INCIDENT-039 P0 |
| `045-cursor-cost-intelligence-routing-v1.mdc` | Pool + path routing |
| `agent-disk-live-wire-first.mdc` | Receipt-first replies |
| `agent-founder-intent-first.mdc` | Autorun north star |
| `mac-control-plane.mdc` | Mac = control only |
| `sina-command-readonly.mdc` | SEMEJ lane isolation |

---

## Known conflicts (resolved in Step 3)

| Conflict | Winner |
|----------|--------|
| Brain "Implement sa-XXXX" in `SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` vs "never implement sa" in `000-brain-unified.mdc` | **Brain never implements** — route Worker on `WORK:` only |
| Dual SSOT index both claim "single entry point" | **`SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1.md`** |
| `brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.md` says "Brain implement sa" | **Superseded by** `SOURCEA_BRAIN_AUTHORITY_UNIFIED_LOCKED_v1.md` |

---

## Stale / archive candidates (Step 6)

Files with explicit SUPERSEDED markers or execution-void status:

- `brain-os/law/SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_DRAFT_v1.md`
- `brain-os/law/SINAAI_AGENT_STACK_POLICY_v1.md`
- `brain-os/law/SOURCEA_COMPANY_INFRA_BUYER_AND_POSITION_SSOT_LOCKED_v1.md`
- `brain-os/law/SINA_PROMPT_OS_CORE_v1.md`
- `brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_LOCKED_v1.md`
- `brain-os/law/ENFORCEMENT-6MO-MASTER-PLAN-v1.md`
- `brain-os/law/ENFORCEMENT-6MO-VC-ROADMAP-v1.md`
- `brain-os/law/SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md`
- `brain-os/law/SOURCEA_BLUEPRINT_COMPARISON_POSTMORTEM_v1.md`
- Plus 26 additional lineage-only files moved to `docs/archive/superseded-law-v1/` (see manifest)

---

## Do not read (for daily ops)

- `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md` — superseded by unified entry
- `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` — superseded by unified entry + runtime model
- `brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md` — superseded by Brain authority unified
- `docs/archive/superseded-law-v1/**` — lineage only

---

## Next actions (this upgrade batch)

1. ✅ This audit
2. Unified entry point
3. Brain + Worker unified docs
4. Runtime model
5. Validator script
6. Archive stale law
7. Rule template + lint
8. Role onboarding guides
9. Retire old indexes
10. Validate + receipt
