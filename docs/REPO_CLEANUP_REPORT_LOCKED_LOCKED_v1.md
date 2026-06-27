# Repo cleanup report — full closeout

**Saved:** 2026-06-27T12:30:00Z  
**Branch:** `fix/cloud-drain-queue-head-rewind`  
**Route:** `locked_product_spec_doc` → `docs/REPO_CLEANUP_REPORT_LOCKED_LOCKED_v1.md`  
**Law:** `infra/cleanup/README.md` · Batch 7 manifest · INCIDENT-039 Mac light

---

## Executive summary

| Metric | Before | After |
|--------|-------:|------:|
| Dirty paths (`git status --short`) | **1,461** | **0** |
| Root files (inventory) | 5 | **2** (`START_HERE.md`, `ACTIVE_NOW.md`) |
| Tracked runtime receipts removed | — | **483** files untracked |
| Commits this session | — | **6** |

Repo is **clean**. Root sprawl restored. Runtime churn no longer pollutes git.

---

## Phase 0 — Secret scan

- **Command:** `bash infra/cleanup/scan-secrets-v1.sh`
- **Result:** **CLEAR** — hits were plan-registry *titles* mentioning `RESEND_API_KEY`, not live secrets
- **Report:** `infra/cleanup/secret-scan-report.txt`

---

## Phase 1 — Inventory

- **Command:** `bash infra/cleanup/generate-inventory-v1.sh`
- **Before:** 5 root files (3 incident reports + compact START_HERE + keep-root)
- **After:** 2 keep-root files only

---

## Phase 2 — Runtime revert + gitignore policy

### Reverted (not committed)

- `agent-control-panel/command-data*.json` — hub runtime projections rebuilt by `disk_live_wire_sync`

### Untracked from git index (`git rm --cached`)

| Path | Files removed from index |
|------|-------------------------:|
| `receipts/bays/` | ~446 |
| `receipts/cloud-dispatch/` | ~37 |
| `agent-control-panel/command-data-{runtime,shell,canonical}.json` | 3 |

### `.gitignore` additions

```
receipts/bays/
receipts/cloud-dispatch/
receipts/cloud-forge-run/
receipts/e2e-reports/
receipts/outreach/
receipts/valid-yes-progress-verdict-lock-*.json
receipts/**/*.jsonl
receipts/*-receipt-v1.json
receipts/*.png
agent-control-panel/command-data-runtime.json
agent-control-panel/command-data-shell.json
agent-control-panel/command-data-canonical.json
```

**Policy:** Runtime receipts live logged / cloud volume / `~/.sina` — not in git. Canonical locked receipts at repo root of `receipts/` (e.g. `sa-*-receipt.json`) remain tracked where referenced by law.

---

## Phase 3 — Batch 7 root sprawl

| Source (root) | Destination | Action |
|---------------|-------------|--------|
| `SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_REPORT_LOCKED_v1.md` | `brain-os/incidents/` | move |
| `SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_REPORT_LOCKED_v1.md` | `brain-os/incidents/` | move |
| `START_HERE_COMPACT_v1.md` | `docs/START_HERE_COMPACT_v1.md` | move |

Manifest updated: `infra/cleanup/cleanup-manifest.md` — Batch 7 **APPROVED** (founder “do it all”).

---

## Phase 4 — Themed commits

| Commit | Message | Scope |
|--------|---------|-------|
| `59a46f689` | cleanup: batch 7 — root sprawl + runtime gitignore | `.gitignore`, receipts untrack, manifest, incident moves |
| `c77197927` | governance: sync brain-os law, incidents, cursor rules and skills | `.cursor/`, `brain-os/`, `agent-skills/` |
| `2df7cc1fc` | chore: sync scripts, data SSOT, docs, and plan registry drift | `scripts/`, `data/`, `docs/`, `plans/`, `infra/`, … |
| `575128674` | feat: sync product surfaces — apps, sites, hub panel | `apps/`, `sites/`, `witnessbc-site/`, hub panel |
| `9d9175ce5` | chore: misc drift — founder weekly, vscode, launch plist | `founder/`, `.vscode/`, plist removal |
| `bcc6e2426` | chore: extend receipts gitignore for session PNG/JSON | `.gitignore` tail |

**Not pushed** — local branch only. Push when ASF opens ship window.

---

## Phase 5 — What stays intentionally local

These may exist logged but are **gitignored** and will not re-dirty the tree:

- `receipts/bays/**`, `receipts/cloud-dispatch/**`
- Hub projection JSON (`command-data-runtime/shell/canonical`)
- Session receipt PNG/JSON churn

Rebuild hub projections locally:

```bash
python3 scripts/disk_live_wire_sync_v1.py  # or hub refresh path logged
```

---

## Founder next actions

1. **Review** the 6 commits on `fix/cloud-drain-queue-head-rewind` — especially the large product/governance batches.
2. **Push + PR** when ready — not done in this session per git safety law.
3. **Cloud CI** — run heavy validators on Railway/ship window, not on Mac (INCIDENT-039).

---

## Proof paths

| Artifact | Path |
|----------|------|
| This report | `docs/REPO_CLEANUP_REPORT_LOCKED_LOCKED_v1.md` |
| Manifest | `infra/cleanup/cleanup-manifest.md` |
| Root inventory | `infra/cleanup/inventory-root.tsv` |
| Progress machine | `data/cleanup-track-progress-v1.json` |
| Secret scan | `infra/cleanup/secret-scan-report.txt` |

**Status:** CLEAN · **2026-06-27T12:30:00Z**
