---
name: hub-pro-ui-upgrade
description: >-
  Hub Pro UI upgrade checklist — general UP-0..UP-7 plus per-app ledger for
  Worker Hub, Mac Health, Form, and all registered surfaces. Use before any
  HTML/CSS/JS edit on Hub apps.
---

# Hub Pro — UI upgrade checklist

**Law:** `brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md`  
**Rule:** `.cursor/rules/024-ui-upgrade-mandatory-checklist.mdc`  
**Registry:** `data/ui-upgrade-surface-registry-v1.json`

## Two layers (both mandatory)

### Layer A — General UP-0 … UP-7 (every app)

| Step | Action |
|------|--------|
| UP-0 | Classify surface: `ui_upgrade_path_classifier_v1.py --path` |
| UP-1 | FIRST CHECK ack: `ui_upgrade_first_check_v1.py --surface <id> --ack` |
| UP-2 | Read per-app ledger MD — frozen inventory |
| UP-3 | Inventory current DOM/routes/CTAs vs frozen |
| UP-4 | Edit additive only — no silent removals |
| UP-5 | Verify: surface `verify` script from registry |
| UP-6 | E2E: surface `e2e` from registry (cloud CI if heavy) |
| UP-7 | Append ledger entry + ship summary |

```bash
python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface worker_hub --print-checklist
python3 scripts/ui_upgrade_ledger_v1.py --surface mac_health --show --json
```

### Layer B — Per-app ledger

| surface_id | Ledger |
|------------|--------|
| `worker_hub` | `ui-upgrade-ledgers/WORKER_HUB_UI_UPGRADE_LEDGER_LOCKED_v1.md` |
| `mac_health` | `ui-upgrade-ledgers/MAC_HEALTH_UI_UPGRADE_LEDGER_LOCKED_v1.md` |
| `hub_form` | `ui-upgrade-ledgers/HUB_FORM_UI_UPGRADE_LEDGER_LOCKED_v1.md` |
| `wtm_tab` | `ui-upgrade-ledgers/WTM_TAB_UI_UPGRADE_LEDGER_LOCKED_v1.md` |

Prefix: `brain-os/law/enforcement/`

## Founder glance contract (Mac Health, Chat Unify, n8n)

When `ui_mode: founder_glance`:

- `tab_count: 0` — no tab bar
- One primary CTA id (e.g. `btn-heal`, `btn-submit`)
- Advanced tools inside `<details id="panel-more">`
- Machine contract JSON in `data/*-founder-glance-ui-contract-v1.json`
- `dom_must_not_contain` items must stay absent

**Jun 2026 lesson:** Removing DOM nodes without updating `app.js` → `null is not an object` → whole app shows OFFLINE. Grep all `$("…")` and add `if (!el) return`.

## Ship summary template

```text
Preserved: [frozen inventory items still present]
Changed: [what moved]
Achieved: [founder-visible outcome]
quality_vs_last: same | better (never downgraded)
founder_approval: pending | approved
upgrade_id: UP-XX-NNN
```

## Forbidden

- UI edit without FIRST CHECK ack
- Ship without ledger append
- Remove frozen inventory item without `UI BASELINE BUMP`
- Add tab bar to founder_glance surfaces
