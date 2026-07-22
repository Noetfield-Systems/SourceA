# UI Upgrade Ledger — TEMPLATE — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T16:54:05Z · **Authority:** Founder — per-app UI upgrade tracking  
**Parent law:** `SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md`  
**Machine log:** `data/ui-upgrade-ledgers/<surface_id>-v1.json`  
**Path pattern:** `brain-os/law/enforcement/ui-upgrade-ledgers/<APP>_UI_UPGRADE_LEDGER_LOCKED_v1.md`

---

## Two layers (every app)

| Layer | What | Where |
|-------|------|-------|
| **General** | UP-0 … UP-7 — same for all apps | `SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md` |
| **Per-app** | Frozen inventory + app checklist + upgrade history | **This ledger** + JSON log |

Agents run **both**. Ship summary cites **general + per-app** checklists.

---

## Per-app ledger sections (copy for new app)

### A. App identity

| Field | Value |
|-------|-------|
| surface_id | `<id>` |
| label | `<human name>` |
| repo | `<repo path>` |
| root | `<UI root on disk>` |
| url | `<founder URL>` |
| ledger_json | `data/ui-upgrade-ledgers/<surface_id>-v1.json` |

### B. Frozen inventory (never drop without `UI BASELINE BUMP`)

List every section, table, CTA, script, data binding, DOM id, API hook that **must survive** every upgrade.

### C. App-specific checklist (beyond general UP-0..UP-7)

Checkboxes unique to this app — DOM markers, audit commands, forbidden patterns.

### D. Upgrade log (newest first)

Each entry **must** include:

| Field | Required |
|-------|----------|
| `upgrade_id` | `UP-<APP>-NNN` |
| `saved_at` | UTC ISO |
| `founder_trigger` | what founder said |
| `general_checklist` | UP-0..UP-7 all PASS |
| `app_checklist` | per-app items PASS |
| `preserved` | table: item · before · after · OK |
| `changed` | what moved / polished / added |
| `achieved` | quality outcome vs last version |
| `quality_vs_last` | `same` or `better` — never `downgraded` |
| `founder_approval` | `approved` · `pending` · `rejected` |
| `machine_proof` | commands + PASS/FAIL |
| `baseline_before` / `baseline_after` | version if applicable |

---

## New app bootstrap

1. Copy this template → `brain-os/law/enforcement/ui-upgrade-ledgers/<APP>_UI_UPGRADE_LEDGER_LOCKED_v1.md`
2. Create `data/ui-upgrade-ledgers/<surface_id>-v1.json` with `frozen_inventory` + bootstrap `UP-<APP>-000`
3. Add row to `data/ui-upgrade-surface-registry-v1.json` with `ledger_md` + `ledger_json`
4. Run `python3 scripts/ui_upgrade_ledger_v1.py --validate --json`

---

## Agent rule on every **up**

```text
READ general law §4 (UP-0..UP-7)
READ this app's ledger §B frozen inventory + §C app checklist
EXECUTE upgrade
APPEND upgrade entry to ledger JSON + §D in MD
PASTE ship summary with preserved + changed + achieved tables
```
