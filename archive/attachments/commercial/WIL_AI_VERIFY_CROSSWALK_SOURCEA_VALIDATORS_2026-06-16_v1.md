# Wil AI verify gates → SourceA validators — machine crosswalk

**Saved:** 2026-06-16T08:30:00Z · **Companion:** `WIL_AI_PORTFOLIO_GAP_MAP_AND_COMMERCIALIZATION_2026-06-16_v1.md`  
**Purpose:** Maintainer quick lookup when wiring RunReceipt / commercial-mirror-kit receipts.

---

## Orchestrator ladder

| Wil AI | Source A |
|--------|----------|
| `npm run verify:pipeline` | `python3 scripts/find_critical_bugs.py` then AS bundle |
| `npm run check:governance` | Multiple `validate-*-v1.sh` + agent system checks |
| `npm run check:staleness` | `bash scripts/validate-anti-staleness-bundle-v1.sh` |
| `npm run check:drift` | `python3 scripts/governance_drift_engine.py` |
| `npm run agent:audit-pack` | AEG pack / RunReceipt export pattern |

---

## Staleness ↔ anti-staleness latches

| Wil check ID | SourceA latch | Relationship |
|--------------|---------------|--------------|
| `governance-realtime` | AS auto-wire / drift engine | Product hook vs OS bundle |
| `governance` (embed) | mandatory reads + law purity | Charter JSON vs LOCKED md |
| `npm-scripts` | validate script targets exist | Same intent |
| `e2e-report-sync` | REPO_EXECUTION_LOGS freshness | Receipt not chat |
| `search-freshness` | derived index after mirror | Pagefind vs queue SSOT unify |
| veto-shell blocks | AS-04 spawn gate | Fail-closed both |
| `agent:memory-sync` | AS-07 brain sync | Mirror lag prevention |
| READ_CHAIN | AS-09 mandatory read paths | Dead path detection |

---

## Receipt artifact mapping

| Wil AI artifact | Suggested SourceA receipt field |
|-----------------|--------------------------------|
| `.e2e/staleness-report.json` | `product_staleness_ok` · `checks_passed` · `checks_total` |
| `.e2e/governance-report.json` | `governance_ok` · `charter_version` |
| `.e2e/browser-report.json` | `browser_passed` · `browser_total` |
| `.e2e/e2e-report.json` | `e2e_overall_ok` |
| `.e2e/audit-pack/LATEST.zip` | `audit_pack_sha256` · `manifest_path` |
| `.cursor/governance/DRIFT_STATE.json` | `drift_posture` · `last_scan_at` |
| `INSTITUTIONAL_ATTESTATION_LATEST.md` | `icf_attestation_path` (human-readable) |

**Target schema (future):** `~/.sina/commercial-mirror-receipt-v1.json` per crawl-mirror §5 Phase 1.

---

## Forbidden merges

| Action | Rule |
|--------|------|
| Map `sa-*` pick to `UP-*` plan | Different registries |
| Run Wil `brand:disk` on SourceA root | Display pass on HTML only |
| Use Wil staleness 21 as AS bundle replacement | Product extension only |
| Factory queue head from Wil `_site-state.json` | Opposite data flow |
