# RunReceipt artifact schema (LOCKED v1)

**Version:** 1.1  
**Date:** 2026-06-06  
**Lane:** Wire / Factory P0  
**Generator:** `scripts/runreceipt/pack_v1.py` · CLI: `scripts/runreceipt/pack.sh`

## Purpose

Turn **DevBridge wire evidence** into a portable PASS/FAIL receipt pack for Factory P0 (RunReceipt).

## Input — DevBridge evidence folder

Default path:

```text
~/Desktop/AI Dev Bridge OS/scripts/evidence/
```

| File | Role | Gate field |
|------|------|------------|
| `g1-cursor-result.json` | G1 — Cursor desktop probe | `ok` / `skipped` |
| `g2-device-result.json` | G2 — physical device | `pass` / `ok` |
| `g2-full-m8-wire-result.json` | full_m8 wire lane | `pass` |
| `G2_DEVICE_RUNBOOK.md` | Operator runbook | documentation |
| `G2_FULL_DAY_PHONE.md` | Phone full-day steps | documentation |
| `ASF_PHYSICAL_G2_CHECKLIST.md` | ASF physical checklist | documentation |

Aggregate status: **FAIL** if any JSON gate is FAIL; otherwise **PASS** (SKIP/MISSING do not alone force FAIL).

## Output artifacts (`SourceA/runreceipt/out/`)

| File | Role |
|------|------|
| `run.jsonl` | Append-only run events |
| `summary.json` | Latest pack summary + evidence counts |
| `receipt.html` | Human-readable PASS/FAIL report |
| `evidence.snapshot.json` | Frozen copy of ingested evidence metadata |
| `receipt-pack.zip` | Zip of the four files above |

## `run.jsonl` row (pack event)

| Field | Type | Required |
|-------|------|----------|
| `schema` | string | `runreceipt-pack-v1` |
| `run_id` | string | yes |
| `at` | ISO-8601 UTC | yes |
| `status` | string | `PASS` \| `FAIL` |
| `lane` | string | e.g. `wire` |
| `action_id` | string | e.g. `devbridge-evidence-pack` |
| `evidence_dir` | string | path scanned |
| `evidence_count` | int | files ingested |
| `evidence_gates` | array | `{name, gate_status}` per JSON gate |

## CLI

```bash
cd ~/Desktop/SourceA
./scripts/runreceipt/pack.sh
./scripts/runreceipt/pack.sh --evidence-dir ~/Desktop/AI\ Dev\ Bridge\ OS/scripts/evidence
./scripts/runreceipt/pack.sh --run-id wire-g3-20260606 --status PASS
```

## HQ mirror

Command HQ workspace (`~/Desktop/SinaaiDataBase/runreceipt/`) may hold stubs; **canonical generator lives in SourceA**.

Law: `PRODUCT_FACTORY_RESCORE_NO_ADS_LOCKED_v1.md` · `SINA_PROMPT_FAST_LOOP_LOCKED_v1.md`
