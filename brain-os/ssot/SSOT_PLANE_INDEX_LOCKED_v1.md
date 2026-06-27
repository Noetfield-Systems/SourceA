# Governance SSOT plane — index (LOCKED v1)

**Saved:** 2026-06-23T22:35:00Z  
**Path:** `brain-os/ssot/`  
**Authority:** Founder governance filing · SSOT v3 footer · Master Blueprint v1 §0  
**Parent index:** `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` · `brain-os/INDEX_LOCKED_v1.md`

---

## One sentence

> **Authoritative agent operating law lives here.** Runtime receipts stay in `~/.sina/` — not this folder.

---

## Current (dispatch authority)

| Doc | Path | Role |
|-----|------|------|
| **LLM Agent Operating Law SSOT v3** | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` | **ACTIVE** · dispatch authority |
| **SSOT registry** | `data/sourcea-governance-ssot-registry-v1.json` | active / superseded / stale definitions |
| **Layer scope index** | `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` | L0 Mac workbench vs L1–L8 cloud kernel · read order |
| **Cloud kernel target (PDF)** | `docs/Source-A-Cloud-Kernel-v1.3.pdf` | L1–L8 north star · symlink `docs/SOURCEA_CLOUD_KERNEL_TARGET_v1.3.pdf` |
| **Kernel ↔ disk reconciliation** | `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md` | Honest GREEN/AMBER/TARGET map |
| **Planning Authority Card** | `brain-os/ssot/SOURCEA_PLANNING_AUTHORITY_CARD_LOCKED_v1.md` | One page · plan from / ignore / do this month |
| **Planning ROI anchor** | `brain-os/ssot/SOURCEA_PLANNING_ROI_ANCHOR_LOCKED_v1.md` | Anchor sentence + ROI verdict · pair to card |
| **Disk-aligned SSOT (FA)** | `brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.md` | Founder FA architecture · pair PDF below |
| **Disk-aligned SSOT (FA PDF)** | `brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.pdf` | Founder-readable export · v1.1-style layout |

---

## Lineage — LLM Agent Operating Law

**Registry (machine):** `data/sourcea-governance-ssot-registry-v1.json`  
**Check:** `python3 scripts/sourcea_governance_ssot_registry_v1.py --json --write-receipt`

| Version | Status | Path on disk |
|---------|--------|--------------|
| **v3** | **ACTIVE** | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` |
| v2 | SUPERSEDED | `brain-os/ssot/superseded/Source-A-SSOT-v1.2.pdf` |
| v1 | SUPERSEDED | `brain-os/ssot/superseded/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v1.md` |

**Stale definition:** `brain-os/law/enforcement/SOURCEA_GOVERNANCE_SSOT_AUTHORITY_AND_STALE_LOCKED_v1.md` — rule-like doc with **no registry row on its plane** = ambiguous authority — flag only, never delete. Law plane rows live in `brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md`.  
**Superseded definition:** explicit `superseded` status + quarantine under `superseded/` — governed history, not stale.

---

## Read order (agents · ORD · Chat Unify)

1. `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` — layer boundaries  
2. `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` — dispatch law  
3. `brain-os/roadmap/SOURCEA_MASTER_BLUEPRINT_v1.md` — zero → enterprise path  
4. `docs/Source-A-Cloud-Kernel-v1.3.pdf` — cloud motor target (when executing factory body)

---

## Not in this plane

| Item | Correct home |
|------|--------------|
| Proof Pack receipts · forge run receipts | `~/.sina/` |
| Prompt Forge pipeline · Zod validators | `scripts/` · `shared/types/` (code) |
| Public page copy only | `SourceA-landing/` · `sourcea.app` (public half) |
| Binding LOCKED enforcement law | `brain-os/law/` · `brain-os/law/enforcement/` |

---

*SSOT plane index v1 · filed 2026-06-23 · update when v4 ships or v1/v2 recovered.*
