# sourcea-boot Public Publish — Phase 0 LOCKED v1

**Saved:** 2026-07-02T03:42:00Z  
**Status:** phase_0b_complete  
**Authority:** Deep research R-01/R-02/R-03 · `SOURCEA_CHAIN_TOOLS_PUBLISH_LOCKED_v1.md`  
**Route:** `locked_product_spec_doc` → execution lives in `packages/sourcea-boot/` (WORK lane)

## Problem

Public site and eval page promise `https://github.com/kazemnezhadsina144-dot/sourcea-boot` and `pip install sourcea-boot`. Researchers received **404** on GitHub (July 1, 2026). This breaks the proof-first diligence story.

## Phase 0 goal (this execution)

Make the **public GitHub eval path real** for portable mode:

```bash
git clone https://github.com/kazemnezhadsina144-dot/sourcea-boot.git
cd sourcea-boot
pip install -e .
sourcea-boot --json
# → BOOT_REPORT.json · exit 0 PASS · exit 1 BLOCK
```

PyPI publish is **Phase 0b — COMPLETE** (2026-07-02). Site may claim `pip install sourcea-boot` when probe passes.

## Scope IN

| Step | Deliverable | Acceptance |
|------|-------------|------------|
| P0-1 | Standalone public repo export from `packages/sourcea-boot/` | MIT LICENSE · CI workflow · validate script |
| P0-2 | `scripts/publish_sourcea_boot_public_v1.py` | Builds export · runs local validate · pushes to GitHub |
| P0-3 | Public repo live at `kazemnezhadsina144-dot/sourcea-boot` | `GET /repos/kazemnezhadsina144-dot/sourcea-boot` → 200 |
| P0-4 | README honest install paths | `pip install` primary · clone alt for contributors |
| P0-5 | Monorepo package unchanged behavior | `bash scripts/validate-sourcea-boot-v1.sh` still PASS |

## Phase 0b (PyPI trusted publishing — LIVE)

| Step | Deliverable | Status |
|------|-------------|--------|
| P0b-1 | `.github/workflows/publish-pypi-v1.yml` | **LIVE** · OIDC · no secrets |
| P0b-2 | `.github/workflows/build-check-pypi-v1.yml` | **LIVE** · build + `twine check` |
| P0b-3 | `publish/PYPI_TRUSTED_PUBLISHING_SETUP_LOCKED_v1.md` | Founder checklist complete |
| P0b-4 | First PyPI upload | **DONE** · `sourcea-boot` v0.1.0 on PyPI |
| P0b-5 | GitHub Release `v0.1.0` | **DONE** · triggers publish workflow |
| P0b-6 | Eval/trust flip | **DONE** · `/eval` shows `pip install sourcea-boot` |

Export: `python3 scripts/publish_sourcea_boot_public_v1.py --push-existing`

## Scope OUT (later phases)

- `sourcea-sdk` PyPI publish — extract done; publish is separate Phase 1b
- Brain bundle mass regen — separate Worker/distill pass
- Transfer `sourcea-boot` to Noetfield PyPI org — when org request approved

## Execution command

```bash
python3 scripts/publish_sourcea_boot_public_v1.py --json
```

## Rollback

If push fails: keep export under `packages/sourcea-boot/.publish-export/` and do not flip public claims.

## Execution receipt (2026-07-01T22:11:53Z)

| Field | Value |
|---|---|
| Live repo | `https://github.com/kazemnezhadsina144-dot/sourcea-boot` |
| Canonical production | `https://sourcea.app` via Cloudflare Pages `sourcea-com` + `sourcea-app-proxy-v1` |
| Staging (non-canonical) | `https://source-a.vercel.app` — Vercel does **not** serve `sourcea.app` |
| Deploy command | `python3 scripts/publish_sourcea_landing_v1.py --backend cloudflare --project sourcea-com --custom-domain --skip-recipe` |
| `/eval` | links `kazemnezhadsina144-dot/sourcea-boot` · **`pip install sourcea-boot`** |
| `trust-signals.json` | `github.ok: true` · **`pypi.ok: true` v0.1.0** |
| PyPI | **LIVE** · `https://pypi.org/project/sourcea-boot/` v0.1.0 |
| Receipt | `~/.sina/sourcea-boot-public-publish-receipt-v1.json` |

## Execution receipt (2026-07-02T03:42:00Z · Phase 0b)

| Field | Value |
|---|---|
| PyPI probe | `scripts/probe_sourcea_boot_pypi_v1.py` → `pypi_ok: true` |
| Trusted publisher | `kazemnezhadsina144-dot/sourcea-boot` · `publish-pypi-v1.yml` · env `pypi` |
| GitHub Release | `v0.1.0` published |
| Eval flip commit | `166b1441a` on `sandbox/locked-definitions-v1` |
| Noetfield PyPI org | Request submitted — transfer optional later |

**End LOCKED v1**
