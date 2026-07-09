# SourceA UI Mechanical Gate — v2 Additions (LOCKED)

**Saved:** 2026-07-06T12:20:00Z  
**Authority:** Advisor mechanical-gate-v2-additions · site-audit-machine first receipt  
**SSOT (locked snapshot):** `data/sourcea-ui-mechanical-gate-v2-additions-locked-v1.json`  
**Merged into:** `data/sourcea-ui-mechanical-gate-v1.json` (v1.2.0+)  
**Parent rubric:** `docs/SOURCEA_UI_STANDARD_RUBRIC_LOCKED_v1.md`

---

## Law

> **L5 additive only.** Agents may ADD checks via PR; never weaken or delete a failing check.

v2 additions are **merged** into the mechanical gate JSON. The locked snapshot file is immutable reference — changes require a new `v2-additions-locked-v2` file + founder gate.

---

## What v2 adds

| Bucket | IDs | Severity |
|--------|-----|----------|
| Forbidden phrases | `{ENTITY}`, `{{`, `${` | FAIL |
| Regex | `placeholder_counter`, `unrendered_var` | FAIL |
| Structural (live E2E) | `splat_url_guard`, `spa_fallback_detect`, `live_vs_dist_diff`, `entity_consistency`, `nav_fingerprint`, `price_drift`, `receipt_hygiene` | REJECT_ROW / DRIFT / FAIL |
| Reclassify | Commercial SKU landers (`/ai-value-governance`, etc.) | `no_contact_surface` WARN → **FAIL** |

---

## Verify law (L4)

The agent that fixes failures **may not** produce the PASS receipt.

- Re-run from **Railway cron** or **founder Mac** (not the Cursor session that shipped the fix)
- Wait **≥60s** after deploy
- Full-body **sha256** per page

---

## Machines

| Role | Path |
|------|------|
| Disk gate (pre-publish) | `scripts/sourcea_ui_mechanical_gate_v1.py` |
| Live E2E audit | `scripts/sourcea_website_ui_e2e_audit_v1.py` |
| Validator | `scripts/validate-sourcea-ui-mechanical-v1.sh` |
| Receipt (disk gate) | `reports/sourcea-ui-mechanical-gate-receipt-v1.json` |
| Receipt (live E2E) | `reports/sourcea-website-ui-e2e-audit-v1.json` |

---

## Evidence basis (2026-07-06)

Confirmed live on `sourcea.app` by external fetch + `site-audit-machine` seeded receipt (`first_audit_receipt.json`).
