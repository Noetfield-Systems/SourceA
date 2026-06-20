# SourceA UI upgrade — mandatory process — LOCKED v1

**Version:** 1.4.0 · **Saved:** 2026-06-19T20:15:00Z · **Authority:** Founder order — every UI upgrade, every app, every website  
**Path:** `~/Desktop/SourceA/brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md`  
**Enforcement:** `.cursor/rules/024-ui-upgrade-mandatory-checklist.mdc` · `.cursor/rules/025-ui-upgrade-first-check-live-wire.mdc` · `.cursor/rules/026-ui-first-check-zero-exception.mdc` · `data/ui-upgrade-surface-registry-v1.json` · `data/ui-upgrade-ledgers-index-v1.json` · `scripts/ui_upgrade_mandatory_gate_v1.py` · `scripts/ui_upgrade_first_check_v1.py` · `scripts/ui_upgrade_path_classifier_v1.py` · `scripts/ui_upgrade_ledger_v1.py` · `scripts/validate-ui-first-check-mandatory-all-agents-v1.sh`  
**Incident anchor:** `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` (SA-2026-06-05-INCIDENT-002)

---

## 0. One sentence

> **NO UI DRIFT · NO UPGRADE DRIFT — ZERO TOLERANCE.** FIRST CHECK applies **only when editing UI files** (form, app, website, hub, canvas) — **not** before every founder chat reply (INCIDENT-039). Machine blocks UI writes without ack. Baseline + ledger checks on **UI ship** — cloud CI / ship window for full validator stack.

**Flag:** `~/.sina/founder-zero-ui-drift-v1.flag`  
**Validator:** `bash scripts/validate-ui-zero-drift-v1.sh`  
**Gate cart:** `ui_zero_drift`

## 0a. FIRST CHECK (machine — live on all agents · ZERO EXCEPTION)

| Gate | Command |
|------|---------|
| Classify path | `python3 scripts/ui_upgrade_path_classifier_v1.py --path <file> --json` |
| Ack surface | `python3 scripts/ui_upgrade_first_check_v1.py --surface <id> --ack --json` |
| Print checklist | `python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface <id> --print-checklist` |
| Read ledger | `python3 scripts/ui_upgrade_ledger_v1.py --surface <id> --show --json` |
| Pre-write | `python3 scripts/pre_write_guard_v1.py check --agent cursor --path <file> --json` |
| Session wire | `ui_upgrade_first_check` step in session gate |
| Pre-write block | `UI_UPGRADE_FIRST_CHECK_REQUIRED` without ack |
| Conduct gate | `ui_edit_without_first_check` violation |
| All-agents validator | `bash scripts/validate-ui-first-check-mandatory-all-agents-v1.sh` |
| Live wire validator | `bash scripts/validate-ui-upgrade-first-check-live-wire-v1.sh` |

**8 surfaces:** `sourcea_landing` · `worker_hub` · `wtm_tab` · `mac_law_cockpit` · `routing_panel` · `mac_health` · `hub_form` · `witnessbc_commercial`  
**Unregistered UI:** `generic_app` — classify + register ledger before ship.

**Generic fallback:** `generic_app` — register new surface row after first upgrade.

---

## 0b. Two layers (general + per-app)

| Layer | What | Where |
|-------|------|-------|
| **General** | UP-0 … UP-7 — same pipeline for all UI upgrades | This doc §4 |
| **Per-app** | Frozen inventory · app checklist · upgrade history log | `brain-os/law/enforcement/ui-upgrade-ledgers/<APP>_UI_UPGRADE_LEDGER_LOCKED_v1.md` + `data/ui-upgrade-ledgers/<surface_id>-v1.json` |

**Index of all app ledgers:** `data/ui-upgrade-ledgers-index-v1.json`

Agents run **both layers**. Every upgrade **appends** one entry to that app's ledger JSON and §D in the MD ledger.

```bash
python3 scripts/ui_upgrade_ledger_v1.py --surface <id> --show --json
python3 scripts/ui_upgrade_ledger_v1.py --validate --json
```

**New app / website:** copy `UI_UPGRADE_LEDGER_TEMPLATE_LOCKED_v1.md` → register in index + registry before first upgrade.

---

## 0c. Per-app ledger entry (required fields)

Every upgrade appends:

| Field | Purpose |
|-------|---------|
| `upgrade_id` | `UP-<APP>-NNN` |
| `saved_at` | when shipped |
| `founder_trigger` | what founder said |
| `general_checklist` | UP-0..UP-7 PASS |
| `app_checklist` | per-app items PASS |
| `preserved` | what from last version stayed |
| `changed` | what actually moved/added |
| `achieved` | quality outcome |
| `quality_vs_last` | `same` · `better` — never `downgraded` |
| `founder_approval` | `approved` · `pending` |
| `machine_proof` | commands + PASS |

---

## 1. Founder trigger (agents must recognize)

When the founder says any of these, **stop and run the UP checklist** before editing UI:

| Trigger | Examples |
|---------|----------|
| **up** | "up the hub", "up UI", "up the landing" |
| **UI upgrade** | "upgrade UI", "upgrade the website", "refresh the page" |
| **redesign / polish** | "make it pro", "clean up layout", "new shell" |

**Not a UI upgrade:** backend-only, API, scripts with no visual change, copy-only typos (still diff-check).

---

## 2. What went wrong (pattern to prevent)

| Failure | Agent behavior | Founder sees |
|---------|----------------|--------------|
| **Content amnesia** | Rewrites page from mock/memory | Tables, CTAs, sections gone |
| **Cockpit swap** | Summary shell replaces full page | "content gone" / blank tab |
| **Reference confusion** | `Downloads/` or `reference/` becomes canonical | E2E, nav, trust strip break |
| **No proof** | Ships without baseline diff | Downgrade discovered days later |
| **Agent reads in UI** | Misconception tables, session logs in hub | Founder UI polluted |

**Law:** Upgrade improves **shape** (spacing, typography, nav, elevation). It does **not** remove **substance** (tables, data panels, CTAs, wiring, E2E hooks).

---

## 3. Surface registry (pick your app)

**SSOT:** `data/ui-upgrade-surface-registry-v1.json`

| Surface id | App | URL |
|------------|-----|-----|
| `sourcea_landing` | SourceA green-unified | http://127.0.0.1:5180/sourcea/ |
| `worker_hub` | Worker Hub | http://127.0.0.1:13020/ |
| `wtm_tab` | World Target Model | http://127.0.0.1:13020/?tab=system-roadmap |
| `mac_law_cockpit` | Mac Law boss | http://127.0.0.1:8781/ |
| `routing_panel` | Routing Panel | http://127.0.0.1:8780/ |
| `mac_health` | Mac Health | http://127.0.0.1:13024/ |
| `hub_form` | Hub Form (FORM_OFFICIAL) | http://127.0.0.1:13020/form/ |
| `witnessbc_commercial` | WitnessBC commercial | https://witnessbc-commercial.pages.dev/ |
| `generic_app` | Any other site/app | founder URL |

If the surface is missing from registry → use `generic_app` + **add a row** after ship.

---

## 4. Mandatory UP checklist (UP-0 → UP-7)

Agents run **in order**. Skipping a step = **invalid upgrade**.

### UP-0 — Declare surface

- [ ] Identify `surface_id` from registry  
- [ ] State target files and founder URL  
- [ ] Confirm trigger: UI upgrade (not backend-only)

```bash
python3 scripts/ui_upgrade_mandatory_gate_v1.py --surface <id> --print-checklist --json
```

### UP-1 — Read blueprint + **per-app ledger**

- [ ] Read all `blueprint` paths for that surface (law, incident, baseline JSON)  
- [ ] Read **per-app ledger MD** — frozen inventory §B + app checklist §C  
- [ ] Read **last upgrade entry** in ledger JSON (`ui_upgrade_ledger_v1.py --show`)  
- [ ] Note **frozen shell** sections (founder must not lose)

**Forbidden:** Start from a mock, ChatGPT HTML, or "cleaner" rewrite without reading in-repo canonical.

### UP-2 — Inventory last good version (baseline capture)

- [ ] List every **section**, **table**, **CTA**, **nav item**, **data binding**, **script include** in current version  
- [ ] Run surface `pre_edit` command from registry (baseline guard / audit / curl API)  
- [ ] Save `git diff` baseline or screenshot note — **proof of what existed**

| Surface | Pre-edit command |
|---------|------------------|
| landing | `ui_upgrade_baseline_guard_v1.py check --path "<file>"` |
| hub / WTM | `audit_hub_source_alignment.py` + read `app.js` render fns |
| Mac Law | `curl …/api/mac-law/surfaces` |
| generic | Manual inventory table in ship summary |

### UP-3 — Plan additive edit only

- [ ] Write **what moves** vs **what stays** (no deletions without founder `UI BASELINE BUMP`)  
- [ ] Port good patterns **into** canonical files — never wholesale replace  
- [ ] If new nav/tabs: every old section must remain reachable (same or tab)

**Allowed:** spacing, typography, sticky subnav, cards, gold accent, tabular nums  
**Forbidden:** delete table, hide table behind new tab without parity, swap page for summary-only cockpit

### UP-4 — Edit (controlled paths only)

- [ ] `pre_write_guard_v1.py` PASS on each target path  
- [ ] Landing: baseline `check` PASS before each file edit  
- [ ] Hub: edit payload SSOT first (`system_roadmap.py`) — **not** duplicate catalogs in `app.js`

### UP-5 — Verify (machine)

- [ ] Run surface `verify` from registry  
- [ ] Landing: `validate-ui-upgrade-no-downgrade-v1.sh`  
- [ ] Hub: `build-sina-command-panel.py` → audit **OK**  
- [ ] WTM: DOM must contain `sr-you-are-here`, `sr-map-layers`; must NOT contain agent reads  
- [ ] Mac surfaces: `validate-mac-law-surfaces-e2e-v1.sh`

### UP-6 — Prove live (E2E / browser)

- [ ] Run surface `e2e` command  
- [ ] Hard-refresh founder URL — visual spot-check every inventoried section  
- [ ] Landing: `run-recipe.sh --e2e` → receipt `e2e: pass`

### UP-7 — Ship summary + **append per-app ledger**

Agent **must** paste completed **Ship summary** (§5) **and** append upgrade entry:

```bash
python3 scripts/ui_upgrade_ledger_v1.py --surface <id> --append '<json entry>' --json
```

Update ledger MD §D upgrade history (same `upgrade_id`). No summary + no ledger append = upgrade **not done**.

---

## 5. Ship summary template (agents copy and fill)

```markdown
## UI UPGRADE SHIP SUMMARY

**Surface:** <id> — <label>  
**URL:** <founder URL>  
**Trigger:** up / UI upgrade  
**Checklist:** UP-0 … UP-7 complete

### Blueprint read
- [ ] <path 1>
- [ ] <path 2>

### Last version preserved (inventory)
| Item | Before | After | Status |
|------|--------|-------|--------|
| <section/table/CTA> | present | present | OK |

### Machine proof
| Step | Command | Result |
|------|---------|--------|
| Pre-edit | `<cmd>` | PASS |
| Verify | `<cmd>` | PASS |
| E2E | `<cmd>` | PASS |

### Intentional changes (additive only)
- <bullet>

### App-specific checklist (from per-app ledger)
- [ ] <APP-1> …
- [ ] <APP-N> …

### Preserved from last version
| Item | Before | After | Status |
|------|--------|-------|--------|
| <from frozen inventory> | present | present | OK |

### What changed
- <bullet>

### What we achieved (quality vs last)
- <bullet> — quality: **same** or **better**

### Founder approval
- **pending** / **approved**

### Ledger entry
- `upgrade_id`: UP-<APP>-NNN appended to `data/ui-upgrade-ledgers/<surface_id>-v1.json`
```

---

## 6. Downgrade definition (universal)

A change is a **downgrade** when any of:

1. Inventoried section/table/CTA **missing** after upgrade without founder `UI BASELINE BUMP`  
2. Machine baseline `check` fails (`UI_BASELINE_FAIL`)  
3. Hub audit fails or `app.js` hardcodes stale step counts  
4. WTM overview loses `sr-you-are-here` / `sr-map-layers`  
5. E2E / recipe receipt not `pass` after landing change  
6. Agent-only content appears in founder UI  

**Remedy:** revert or restore from pre-upgrade inventory — do not argue "cleaner."

---

## 7. Per-surface quick reference

### SourceA landing (`sourcea_landing`)

Law: `SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md`  
Baseline: `ui-upgrade-baseline-v1.json`  
Rule: `.cursor/rules/023-ui-upgrade-no-downgrade.mdc`

### Worker Hub + WTM (`worker_hub`, `wtm_tab`)

Law: `HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md`  
Incident: `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` §5 permanent law

### Mac cockpits (`mac_law_cockpit`, `routing_panel`, `mac_health`)

Law: `MAC_LAW_SSOT_LOCKED.md` · `MAC_CONTROL_PLANE_LOCKED.md`  
E2E: `validate-mac-law-surfaces-e2e-v1.sh`

---

## 8. Founder override (intentional reduction)

```text
EDIT ALLOWED: <path>
ACTION: <what>
UI BASELINE BUMP: <version> — <reason>
```

Without `UI BASELINE BUMP`, marker/section removal = FAIL.

---

## 9. Wire status (proposal → live)

| Step | Artifact | Status |
|------|----------|--------|
| SSOT law | this file | **LOCKED v1** |
| Surface registry | `data/ui-upgrade-surface-registry-v1.json` | **live** |
| Cursor rule | `.cursor/rules/024-ui-upgrade-mandatory-checklist.mdc` | **proposal — alwaysApply** |
| Gate script | `scripts/ui_upgrade_mandatory_gate_v1.py` | **live** |
| Live-wire register | `agent-rule-live-wire-registry-v1.json` | **pending founder wire** |

To fully wire: `python3 scripts/agent_rule_live_wire_v1.py --register ui_upgrade_mandatory --json`

---

## 10. Changelog

| Version | Saved | Change |
|---------|-------|--------|
| 1.1.0 | 2026-06-19T16:54:05Z | Two-layer model: general UP + per-app ledgers (6 apps) |
| 1.0.0 | 2026-06-19T16:48:57Z | Universal UP checklist + ship summary + surface registry (founder order) |
