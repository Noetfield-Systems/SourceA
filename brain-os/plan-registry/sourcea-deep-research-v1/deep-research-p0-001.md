# Fix public install/package claim vs PyPI reality

**Plan ID:** `sdr-p0-001` · **Tier:** P0 · **Updated:** 2026-07-06T09:17:58Z

## Problem
Homepage/eval references pip install sourcea-boot; package must resolve or copy must say GitHub-only.

## Goal
Eval page and PyPI probe agree — no false install promise

## Done when
probe_sourcea_boot_pypi_v1.py ok OR eval copy says GitHub clone pending

## Verify
```
cd ~/Desktop/SourceA && python3 scripts/probe_sourcea_boot_pypi_v1.py --json && python3 scripts/verify_client_proof_artifact_v1.py --url https://sourcea.app/eval --marker "sourcea-boot" && cd ~/Desktop/SourceA && python3 scripts/cloud_forge_run_supabase_v1.py --query --count
```

## Proof artifact
https://sourcea.app/eval

## Client demo
Open /eval — show install line matches live PyPI or honest GitHub fallback

## Work path
`SourceA-landing/green-unified/eval.html`

---
*Child plan · rolled into UP-DR upgrade wave*
