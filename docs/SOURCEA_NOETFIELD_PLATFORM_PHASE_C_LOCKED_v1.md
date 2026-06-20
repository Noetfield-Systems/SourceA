# Noetfield Platform Phase C — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-17T15:37:05Z  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_NOETFIELD_PLATFORM_PHASE_C_LOCKED_v1.md`  
**Parents:** Phase A cloud (`validate-fbe-cloud-phase1-v1.sh`) · Phase B spec (`SOURCEA_FBE_FACTORY_SPEC_LANGUAGE_LOCKED_v1.md`)

---

## 0. One sentence

> **Phase C ships Policy Marketplace, Trust Ledger, Noetfield SDK, and SourceA-landing factory catalog — platform packaging on top of FBE kernel.**

---

## 1. Four tracks

| Track | SSOT | Validator |
|-------|------|-----------|
| **POLICY** | `data/policy-packs/registry-v1.json` | `validate-fbe-policy-packs-v1.sh` |
| **LEDGER** | `data/fbe_trust_ledger_schema_v1.json` | `validate-fbe-trust-ledger-v1.sh` |
| **SDK** | `packages/noetfield/` | `validate-noetfield-sdk-v1.sh` |
| **WEBSITE** | `SourceA-landing/green-unified/factories/` | `validate-landing-factories-catalog-v1.sh` |

---

## 2. Policy packs (not separate codebases)

- Registry: `data/policy-packs/registry-v1.json`
- Wrappers: KYB (`fintrac_kyb_v1`), AML (`aml_screening_v1`), M&A (`ma_diligence_v1`)
- `execution_contract_v1` includes `policy_pack` + `policy_hash`
- Catalog tier renamed: `policy_packs` (was `tier_2`)

---

## 3. Trust ledger

- Append-only: `~/.sina/fbe-trust-ledger-v1.jsonl`
- Events: `JOB_QUEUED` → `POLICY_CHECKED` → `KERNEL_STARTED` → `JOB_COMPLETED` → `RECEIPT_FEDERATED` → `LEDGER_SIGNED`
- Hub: `GET /api/fbe/ledger/v1?job_id=`
- Bridges `FBE_JOB_SIGNED` to governance spine

---

## 4. Noetfield SDK

```python
from noetfield import Governance
gov = Governance(hub_url="http://127.0.0.1:13020")
gov.check(factory_id="compliance-kyb-wrapper-v1")
gov.execute(factory_id="exchange-factory-v1")
gov.audit(job_id="...")
gov.sign(receipt)
```

---

## 5. Landing website

- Hub: `/sourcea/factories/index.html`
- Build: `python3 scripts/build-landing-factories-catalog-v1.py`
- Static: `SourceA-landing/green-unified/data/factories-catalog.json`
- Deploy CTA: mailto book demo (prove_only honest cap)

---

## 6. Commands

```bash
bash scripts/validate-fbe-policy-packs-v1.sh
bash scripts/validate-fbe-trust-ledger-v1.sh
bash scripts/validate-noetfield-sdk-v1.sh
bash scripts/validate-landing-factories-catalog-v1.sh
python3 scripts/build-landing-factories-catalog-v1.py
```

---

**Positioning:** Noetfield = AI Factory Operating Platform · Factories = Apps · Policy packs = Install · Runtime = included
