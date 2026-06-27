# SourceA — Cloud Forge Run + Auto Runtime vocabulary (LOCKED)

**Saved:** 2026-06-24 · **UTC:** 2026-06-24T22:00:00Z · **v2.0 physical rename**  
**SSOT:** `data/cloud-motor-founder-vocabulary-v1.json`  
**Manifest:** `data/cloud-forge-run-rename-manifest-v1.json`  
**Migration:** `scripts/cloud_forge_run_physical_rename_v1.py`

---

## One law

> **Filenames and docs use `cloud-forge-run` and `cloud-auto-runtime`. The words drain and loop are retired from paths. 50 batch files + 314 references renamed logged.**

---

## Physical names (canonical)

| Retired path pattern | New path pattern |
|---------------------|------------------|
| `cloud-drain-*` | `cloud-forge-run-*` |
| `cloud_drain_*` | `cloud_forge_run_*` or `cloud_auto_runtime_*` |
| `secondary-cloud-drain-batch-*` | `secondary-cloud-forge-run-batch-*` |
| `cloud-drain-tick-v1` (CF worker) | `cloud-auto-runtime-tick-v1` |
| `run_pack_loop` | `run_auto_runtime_pack` |
| `/api/cloud-drain/` | `/api/cloud-forge-run/` (+ legacy alias) |

---

## Key files after rename

| Role | Path |
|------|------|
| Auto Runtime motor | `scripts/cloud_auto_runtime_v1.py` |
| Forge Run proceed | `scripts/hub_cloud_forge_run_proceed_v1.py` |
| Queue SSOT | `scripts/fbe/lib/cloud_forge_run_queue_v1.py` |
| Active pointer | `data/cloud-forge-run-queue-active-v1.json` |
| Auto Runtime config | `data/cloud-auto-runtime-v1.json` |
| CF cron worker | `cloud/workers/cloud-auto-runtime-tick-v1/` |

---

## Deploy notes

- Railway env: `CLOUD_FORGE_RUN_AUTO_PROCEED=true` (legacy `CLOUD_DRAIN_AUTO_PROCEED` still read)
- CF secrets: `bash scripts/cloud_auto_runtime_cf_secrets_v1.sh`
- Dockerfile: `COPY data/secondary-cloud-forge-run-batch-*.json`

**LOCKED v2.0**
