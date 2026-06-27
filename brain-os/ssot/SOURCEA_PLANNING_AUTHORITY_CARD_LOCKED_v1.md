# SourceA — Planning Authority Card (LOCKED v1)

**Saved:** 2026-06-24T05:00:00Z · **Plane:** `brain-os/ssot/` (authored law) · **Not:** `~/.sina/` (receipts) · **Not:** `docs/` (public index)  
**Registry check:** `data/sourcea-governance-ssot-registry-v1.json` · `python3 scripts/sourcea_governance_ssot_registry_v1.py --json`

---

## Anchor (read before any plan)

> **Plan from SSOT v3 + Master Blueprint + reconciliation map; execute from blueprints + FBE + Cloud Forge Run; use v1.1/v1.3 PDFs as target shape, not as a rebuild spec.**

**ROI (one line):** Current stack beats finishing v1.1’s CF/Neon/SQL checklist — gap = Proof Pack + T1, then executor/router hardening · not replace what’s built.  
**Full anchor:** `brain-os/ssot/SOURCEA_PLANNING_ROI_ANCHOR_LOCKED_v1.md`

---

## PLAN FROM (ranked — authoritative)

| # | What | Path |
|---|------|------|
| 1 | Agent dispatch law | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` |
| 2 | Revenue + phase path | `brain-os/roadmap/SOURCEA_MASTER_BLUEPRINT_v1.md` |
| 3 | Layer boundaries + read order | `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` |
| 4 | Honest GREEN / AMBER / TARGET | `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md` |
| 5 | Cloud motor north star (target) | `docs/Source-A-Cloud-Kernel-v1.3.pdf` |
| 6 | Queue head + machine truth | `brain-os/plan-registry/SOURCEA-PRIORITY.md` · `data/forge-real-blueprints-v01.json` |

**Consult when blocked only:** `brain-os/roadmap/SOURCEA_STOREFRONT_GTM_v1.md` · `brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.md` (founder FA summary)

---

## IGNORE / SUPERSEDED (never rebuild from these)

**Machine authority:** `data/sourcea-governance-ssot-registry-v1.json` — rows with `"status": "superseded"` only.

| Registry id | Status | Path | Rule |
|-------------|--------|------|------|
| `llm_agent_operating_law_v1` | superseded | `brain-os/ssot/superseded/Source-A-SSOT-v1.1.pdf` · `…/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v1.md` | Lineage · shape reference only |
| `llm_agent_operating_law_v2` | superseded | `brain-os/ssot/superseded/Source-A-SSOT-v1.2.pdf` | Lineage · shape reference only |

**Active law rows (do not confuse with above):** `llm_agent_operating_law_v3` · `master_blueprint_v1` · `storefront_gtm_v1` · `cloud_kernel_v1_3` — all `"status": "active"` in registry.

**Explicit non-starts (reconciliation LOCKED):** Neon migration · CF Worker motor rewrite · full SQL graph before Proof Pack proof · validator marathon on Mac (INCIDENT-039).

---

## DO THIS MONTH (execution head — not a reading list)

| Priority | Action | Done = |
|----------|--------|--------|
| **B** · **FIRST** | **Seal 1 real Proof Pack** from green run (`phase1-pevc-truth-ticket-v1.json` or next GREEN Cloud Forge Run) | `~/.sina/chat-unify/proof-packs/` + re-verify PASS |
| **A** · **SECOND** | **1 paying T1 client** — run factory · deliver output | SOW + client Proof Pack receipt logged |
| **C** · **THIRD** | **Executor + router hardening** (after B + A) | 3 consecutive Cloud Forge Run PASS · idempotency on FBE paths |

**Everything else this month:** consult-when-blocked only (SQL migration · OTel · Neon · CF Queues · registry beyond queue head).

**Founder fork (LOCKED 2026-06-24):** `Proof Pack seal` **first** → `T1 client` → **C** hardening.

**Disk check (B — LOCKED first):** `~/.sina/chat-unify-proof-pack-v1.json` → Phase-1 ticket seal **PASS** · pack `pp-20260624T052230Z-c3857002` · truth gate 98/100 · source `phase1-pevc-truth-ticket-v1.json`. Re-run:  
`python3 scripts/chat_unify_proof_pack_v1.py --receipt-path ~/.sina/phase1-pevc-truth-ticket-v1.json --json`

---

## EXECUTE FROM (motor — code plane, not law folder)

| Layer | Path |
|-------|------|
| Blueprint queue | `data/forge-real-blueprints-v01.json` (100 rows) |
| Contract gate | `data/fbe_execution_contract_v1.json` |
| Cloud motor | `scripts/fbe_run_job_v1.py` · `scripts/hub_cloud_forge_run_proceed_v1.py` |
| Proof machine (code) | `scripts/chat_unify_proof_pack_v1.py` |
| Live proof | `~/.sina/phase1-pevc-truth-ticket-v1.json` · `~/.sina/agent-live-surfaces-v1.json` |

---

## Registry cross-check (must match disk)

| id | registry `status` | path in registry |
|----|-------------------|------------------|
| `llm_agent_operating_law_v3` | **active** | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` |
| `master_blueprint_v1` | **active** | `brain-os/roadmap/SOURCEA_MASTER_BLUEPRINT_v1.md` |
| `storefront_gtm_v1` | **active** | `brain-os/roadmap/SOURCEA_STOREFRONT_GTM_v1.md` |
| `cloud_kernel_v1_3` | **active** | `docs/Source-A-Cloud-Kernel-v1.3.pdf` |
| `llm_agent_operating_law_v2` | superseded | `brain-os/ssot/superseded/Source-A-SSOT-v1.2.pdf` |
| `llm_agent_operating_law_v1` | superseded | v1.1 PDF + v1 md under `brain-os/ssot/superseded/` |

*This card does not add registry rows — it points at them. Supersede card only via versioned v2 + registry update.*

---

*Planning Authority Card v1 · one page · receipts/revenue over reading · brain-os = authored truth · ~/.sina = proven truth.*
