# SourceA Governance Entry — Unified (LOCKED v1)

**Saved at:** 2026-07-05T12:35:00Z  
**Version:** 1.0.0 LOCKED  
**Supersedes:** `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md` · `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` (as primary entry)  
**Audit:** `docs/SOURCEA_GOVERNANCE_FRAGMENTATION_AUDIT_v1.md`

---

## One sentence

> **Start here.** One read order for every SourceA agent session — Mac control, rules, roles, law pointers. No mega-paste.

---

## Mandatory read order (once per session)

| # | Layer | Path | Why |
|---|-------|------|-----|
| 1 | **This file** | `docs/SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1.md` | Entry + read order |
| 2 | **L0 Mac control** | `data/founder-execution-model-v1.json` · `.cursor/rules/mac-control-plane.mdc` | Mac = control only |
| 3 | **Session gate** | `python3 scripts/agent_session_gate_run_v1.py --role <role> --json` | Receipt sync |
| 4 | **L1 Rules in charge** | `.cursor/rules/000-entry-gate.mdc` · `.cursor/rules/000-cross-lane-edit-forbidden.mdc` | SAVE · WORK · EDIT ALLOWED |
| 5 | **L2 Your role** | Brain → `docs/SOURCEA_BRAIN_AUTHORITY_UNIFIED_LOCKED_v1.md` · Worker → `docs/SOURCEA_WORKER_SCOPE_UNIFIED_LOCKED_v1.md` | Role boundary |
| 6 | **L3 Runtime model** | `docs/SOURCEA_UNIFIED_RUNTIME_MODEL_LOCKED_v1.md` | 5-layer SSOT map |
| 7 | **L4 Role onboarding** | `docs/SOURCEA_ONBOARDING_<ROLE>_ROLE_LOCKED_v1.md` | <5 min role card |

---

## Always-apply rules (9) — why each is on

| Rule | Why always-on |
|------|----------------|
| `000-entry-gate.mdc` | Brain vs Worker routing |
| `000-cross-lane-edit-forbidden.mdc` | Disk write gate |
| `000-workspace-lock.mdc` | Repo = `~/Desktop/SourceA` |
| `034-mac-no-validator-stuck-red-flag.mdc` | No validator marathon on Mac |
| `045-cursor-cost-intelligence-routing-v1.mdc` | Auto/Composer pool · path map |
| `agent-disk-live-wire-first.mdc` | Receipts over chat memory |
| `agent-founder-intent-first.mdc` | Autorun north star |
| `mac-control-plane.mdc` | Cloud executes · Mac observes |
| `sina-command-readonly.mdc` | SEMEJ isolation |

---

## Top law pointers (10 max — drill only when in scope)

| Topic | Canonical path |
|-------|----------------|
| Start / role picker | `brain-os/law/entry/START_HERE_LOCKED_v1.md` |
| Governance router | `brain-os/law/entry/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` |
| Agent verbs SAVE/WORK/EDIT | `brain-os/law/enforcement/AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` |
| Brain unified (legacy) | `brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md` → use `SOURCEA_BRAIN_AUTHORITY_UNIFIED_LOCKED_v1.md` |
| Worker inbox | `brain-os/law/enforcement/RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` |
| Autorun laws | `docs/CONTROLLED_AUTORUN_LAWS_v3.md` |
| Conflict resolution | `.cursor/rules/ecosystem-rule-conflict-resolution.mdc` |
| No fake progress | `brain-os/law/SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` |
| Mac workbench | `docs/SOURCEA_HARDENED_MACHINE_WORKBENCH_ARCHITECTURE_LOCKED_v1.md` |
| Cloud kernel target | `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md` |

---

## Do not read (daily ops)

| Path | Use instead |
|------|-------------|
| `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md` | This file |
| `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` | `SOURCEA_UNIFIED_RUNTIME_MODEL_LOCKED_v1.md` |
| `docs/COMPLETE_CONTEXT.md` | This file (thin router only) |
| `docs/archive/superseded-law-v1/**` | Lineage only — never cite as active law |
| `brain-os/law/ENFORCEMENT-6MO-MASTER-PLAN-v1.md` | Archived — void for execution |

---

## Conflict precedence (short)

1. Founder current message (`ASF:` · `WORK:` · `EDIT ALLOWED:` + `ACTION:` · `SAVE TO:`)
2. This unified entry + role unified docs
3. Always-apply rules (9)
4. LOCKED law at cited path
5. Machine SSOT (`data/*-v1.json`, validators)
6. Chat / attachments — never authority

Full algorithm: `.cursor/skills/skill-007-ecosystem-conflict-resolution/SKILL.md`

---

## Validator

```bash
bash scripts/validate-governance-consistency-v1.sh
```
