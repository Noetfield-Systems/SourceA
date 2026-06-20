# SourceA UI upgrade — no downgrade — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-18T00:10:24Z · **Authority:** Founder order — machine-enforceable UI upgrade law  
**Path:** `~/Desktop/SourceA/brain-os/enforcement/SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md`  
**Enforcement:** `.cursor/rules/023-ui-upgrade-no-downgrade.mdc` · `scripts/ui_upgrade_baseline_guard_v1.py` · `scripts/validate-ui-upgrade-no-downgrade-v1.sh` · `pre_write_guard_v1.py`

---

## 0. One sentence

> **Agents must prove they hold the current controlled UI version in the repository before editing; removing baseline features while “upgrading” is a downgrade and is blocked.**

---

## 1. Problem (INCIDENT pattern)

| Failure mode | What agents do | Result |
|--------------|----------------|--------|
| Mock overwrite | Paste slimmer mock over canonical 12-page site | Lose live trust bar, E2E, films, team orbit |
| Feature amnesia | “Upgrade” without reading deployed/E2E baseline | Drop buyer toggle, chain beats, SMART-301 strip |
| Reference confusion | Treat `Downloads/*.html` or `reference/` as SSOT | Nav/deploy/E2E drift |
| No proof | Ship HTML without `run-recipe --e2e` | Silent regression until founder opens site |

---

## 2. Version SSOT (machine)

| Artifact | Role |
|----------|------|
| `SourceA-landing/green-unified/data/ui-upgrade-baseline-v1.json` | **Baseline manifest** — `must_contain` + `min_count` per file |
| `~/.sina/sourcea-landing-run-receipt-v1.json` | **Live proof** — `e2e: pass` after full recipe |
| `scripts/sourcea-landing-e2e-v1.mjs` | **Behavioral baseline** — Playwright asserts |
| `reference/sourcea-landing-mock-v1.html` | **Design reference only** — never canonical |

**Baseline version** bumps only when:

1. `bash SourceA-landing/green-unified/scripts/run-recipe.sh --e2e` → PASS  
2. New markers added to `ui-upgrade-baseline-v1.json`  
3. `version` field incremented (semver patch)

---

## 3. Controlled surfaces

```
SourceA-landing/green-unified/
  index.html · proof.html · platform.html · security.html · status.html
  sourcea.css · sourcea-trust-bar.js · sourcea-live-console.js · sourcea-motion.js
```

**Excluded:** `reference/` · `attach/` · `factories/` (alternate shells)

---

## 4. Mandatory agent pipeline (UI work)

```text
READ baseline version
  → python3 scripts/ui_upgrade_baseline_guard_v1.py baseline --json

CHECK target file matches baseline (pre-edit)
  → python3 scripts/ui_upgrade_baseline_guard_v1.py check --path "<abs-or-rel>" --json

EDIT (additive — port good patterns, keep baseline markers)

VERIFY all controlled files
  → bash scripts/validate-ui-upgrade-no-downgrade-v1.sh

PROVE live
  → bash SourceA-landing/green-unified/scripts/run-recipe.sh --e2e --json

BUMP baseline (if new markers)
  → edit ui-upgrade-baseline-v1.json + version patch
```

**Pre-write guard** runs step 2 automatically on controlled paths.

---

## 5. Machine gates

| Gate | Command | Fail closed |
|------|---------|-------------|
| Pre-edit | `ui_upgrade_baseline_guard_v1.py check --path` | `UI_BASELINE_FAIL` |
| Full surface | `validate-ui-upgrade-no-downgrade-v1.sh` | exit 1 |
| Recipe | `run-recipe.sh` step 1b baseline verify | exit 1 |
| Pre-write | `pre_write_guard_v1.py check` | blocks write |
| E2E | `run-recipe.sh --e2e` | receipt `e2e: pass` |

---

## 6. Downgrade definition (machine)

A change is a **downgrade** when, after edit, any controlled file fails `check` against the current baseline manifest — including:

- Removed CSS classes: `.sa-buyer-toggle`, `.sa-chain-beats`, `.sa-mock-panel`, trust strip markers  
- Removed live wiring: `sourcea-trust-bar.js`, `paintFactoryChip`, `dataset.saLive`  
- Reduced counts: fewer than 6 `.sa-chain-beat` on home/proof  
- Replaced CTA copy without founder order  

Downgrades require **revert** or **baseline bump** with E2E proof — not silent ship.

---

## 7. Reference vs canonical

| Source | Use |
|--------|-----|
| `green-unified/index.html` + deploy `:5180/sourcea/` | **Canonical** |
| `reference/sourcea-landing-mock-v1.html` | Copy patterns only |
| Founder `Downloads/*.html` | Review only — sync to `reference/` then port |

**Law:** Reference mocks **never** replace canonical pages wholesale.

---

## 8. Founder override

Intentional baseline reduction requires in one message:

```text
EDIT ALLOWED: SourceA-landing/green-unified/<file>
ACTION: <what>
UI BASELINE BUMP: <new version> — <reason>
```

Without `UI BASELINE BUMP`, pre-write guard treats marker removal as FAIL.

---

## 9. Related

- `SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md` — disk truth  
- `scripts/validate-sourcea-landing-e2e-v1.sh` — behavioral proof  
- `scripts/bootstrap_sourcea_desktop_deploy_v1.sh` — deploy path wiring  
- SMART-301 — trust strip live asserts in E2E

---

## 10. Changelog

| Version | Saved | Change |
|---------|-------|--------|
| 1.0.0 | 2026-06-18T00:10:24Z | Initial baseline from landing E2E pass + mock port |
