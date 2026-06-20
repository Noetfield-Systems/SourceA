# Batch 3 — critic/advisor diff packet

**Status:** DRAFT — not executed  
**Theme:** Tier-0 portfolio & governance SSOT (ASF + SINA + SOURCEA core law)  
**Root before batch 3:** 277 loose files  
**Root after (expected):** 252 loose files (−25)  
**Prior commits:** batch-1 `0cf364d8` · batch-2 `94c2dd2b`

## Rationale (for red-team)

This batch moves **authority and portfolio truth** out of root — not incidents, not Sina Command legacy UI, not WORLD_TARGET_MODEL. Goal: establish `brain-os/law/` + `brain-os/system/` + `brain-os/law/entry/` as the read plane for structural questions.

**Explicitly NOT in batch 3:** `START_HERE.md`, `ACTIVE_NOW.md`, `SINA_COMMAND_*` (8 files — legacy hub; batch 4+), incident `*_REPORT_*` files (batch 4), `data/*.json`.

## Move table (paste to Claude/Gemini)

| # | FROM (root) | TO | action | risk flag |
|---|-------------|-----|--------|-----------|
| 1 | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | `brain-os/system/` | move | **HIGH** — authority router; verify scripts don't hardcode root path |
| 2 | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | `brain-os/law/entry/` | move | **HIGH** — entry gate; update pointers in `.cursor/rules` if any cite root |
| 3 | `SINA_OS_SSOT_LOCKED.md` | `brain-os/law/` | move | **HIGH** — master SSOT; INTERNAL_LOCAL_ONLY per doc |
| 4 | `SINA_OS_SSOT_READ_ORDER_ADDENDUM_v1.md` | `brain-os/law/` | move | medium |
| 5 | `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` | `brain-os/law/` | move | **HIGH** — portfolio tier-0 |
| 6 | `SOURCEA_REPO_SSOT_LOCKED.md` | `brain-os/law/` | move | medium |
| 7 | `SOURCEA_EXECUTION_LAW_LOCKED_v1.md` | `brain-os/law/` | move | medium |
| 8 | `SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` | `brain-os/law/` | move | medium — agent conduct law |
| 9 | `SINA_ENFORCEMENT_PORTFOLIO_DECISION_FORM_LOCKED_v1.md` | `brain-os/law/` | move | medium |
| 10 | `SINA_ENFORCEMENT_6MO_LAW_SUPERSESSION_LOCKED_v1.md` | `brain-os/law/` | move | medium |
| 11 | `SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md` | `brain-os/law/` | move | medium |
| 12 | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 13 | `SINA_UNIFIED_ENGINE_STORY_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 14 | `SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 15 | `SOURCEA_FLEET_HEADLINE_READ_ORDER_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 16 | `SOURCEA_VALID_YES_PROGRESS_VERDICT_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 17 | `SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 18 | `ASF_MILESTONE_GLOSSARY_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 19 | `ASF_MASTER_ORDERS_ORGANIZED_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 20 | `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` | `brain-os/system/` | move | medium — program registry |
| 21 | `ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md` | `brain-os/system/` | move | medium |
| 22 | `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` | `brain-os/law/enforcement/` | move | low |
| 23 | `ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md` | `brain-os/law/` | move | low |
| 24 | `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md` | `brain-os/law/` | move | low |
| 25 | `SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` | `archive/root-stubs/` | archive | stub — first line says MOVED |

## git diff preview (structural)

```text
root/  →  brain-os/law/          (17 files)  portfolio + Sina OS + SourceA execution law
root/  →  brain-os/system/       (3 files)   authority index + ASF program registry
root/  →  brain-os/law/entry/        (1 file)    governance entry router
root/  →  brain-os/law/enforcement/  (1 file)    ASF full-day playbook
root/  →  archive/root-stubs/    (1 file)    WTM synthesis stub
```

## Questions for critics

1. Should `SOURCEA_UNIFIED_PORTFOLIO_*` live in `brain-os/law/` or `docs/commercial/`?
2. Does moving `SINA_AUTHORITY_INDEX_MAP` break any script with hardcoded `~/Desktop/sourceA/SINA_AUTHORITY*` path?
3. Is archiving `SINA_GPT_CLAUDE_WTM_SYNTHESIS` stub correct, or is canonical elsewhere?
4. Batch 3 intentionally skips all `SINA_COMMAND_*` — agree to defer to batch 4?

## Spot-check list (ASF — open 3 files)

- [ ] `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` — confirm tier-0 authority rows
- [ ] `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` — confirm still current v3.1/v3.2
- [ ] `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` — confirm entry router paths inside doc
