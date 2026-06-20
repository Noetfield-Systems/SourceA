# FBE Factory Spec Language — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-17T16:00:00Z  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_FBE_FACTORY_SPEC_LANGUAGE_LOCKED_v1.md`  
**Machine SSOT:** `data/fbe_factory_spec_schema_v1.json` · `data/fbe_catalog_v1.json`  
**Specs:** `data/factory-specs/*.json`  
**Validator:** `bash scripts/validate-fbe-catalog-spec-v1.sh`  
**CLI:** `python3 scripts/fbe_factory_spec_v1.py --validate --json`

---

## 0. One sentence

> **Factory = product spec (data only). Kernel = FBE execution engine. Catalog = pointers. Runtime never embeds product logic.**

---

## 1. Three-layer law (permanent)

| Layer | What | Where | Forbidden |
|-------|------|-------|-----------|
| **Kernel** | Execute pipelines, federate receipts | Cloud worker · `fbe_run_job_v1.py` | Product copy · tenant branding |
| **Factory spec** | I/O schema · bay · API route · tier cap | `data/factory-specs/` | Execution · containers |
| **Catalog** | Website + sales packaging | `data/fbe_catalog_v1.json` | New kernels · duplicate engines |

---

## 2. Spec file shape (`fbe-factory-spec-v1`)

```json
{
  "factory_id": "exchange-factory-v1",
  "spec_version": "1.0.0",
  "kind": "engine",
  "kernel": { "id": "fbe-v1", "min_version": "fbe-v1.0.0" },
  "lines": ["trust_motor", "refinery", "assembly"],
  "runtime": {
    "bay_slug": "trustfield-bay",
    "api_route": "/api/fbe/run-exchange/v1",
    "cloud_entry": "--run-exchange",
    "execution_mode": "CLOUD_ONLY"
  },
  "io": {
    "input_schema": "data/schemas/exchange-input-v1.json",
    "output_artifact": "RunReceipt ZIP + partner pack",
    "certainty_report": true
  },
  "commercial": { "name": "...", "tier_label": "engine", "buyer": "..." }
}
```

**Wrappers** set `"kind": "wrapper"` + `"extends": "<engine-factory-id>"` — same kernel, different I/O.

---

## 3. Catalog tiers (v1)

| Tier | Items | Hero |
|------|-------|------|
| **engines** | web-product · exchange · forge | exchange |
| **tier_2** | compliance-kyb-wrapper | KYB wrapper |
| **sandbox** | sandbox-mock-factory | — |

Website shows per item: **Inputs · Operational nodes · Guaranteed output · Maintenance fee · 30s demo**.

---

## 4. Resolve → execute flow

```text
GET /api/fbe/catalog/v1
  → pick factory_id
resolve_execution(factory_id)
  → api_route + body (execution_mode CLOUD_ONLY)
POST api_route (Hub proxy → cloud worker)
  → execution_receipt + Certainty Report
```

---

## 5. Versioning rules

1. Bump `spec_version` on material io/runtime/commercial change  
2. Jobs carry `kernel_version` from `execution_contract_v1`  
3. Replay = same `factory_id` + `spec_version` + input hash  
4. Never market above `governance.tier_cap_honest`

---

## 6. Commands

```bash
python3 scripts/fbe_factory_spec_v1.py --validate --json
python3 scripts/fbe_factory_spec_v1.py --catalog --json
python3 scripts/fbe_factory_spec_v1.py --resolve exchange-factory-v1 --json
curl -s http://127.0.0.1:13020/api/fbe/catalog/v1
```

---

**Parent:** `docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md` · Phase B after cloud Phase A
