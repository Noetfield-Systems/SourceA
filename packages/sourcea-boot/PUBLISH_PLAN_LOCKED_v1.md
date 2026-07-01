# sourcea-boot Public Publish — Phase 0 LOCKED v1

**Saved:** 2026-07-01T22:15:00Z  
**Status:** phase_0_complete  
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

PyPI publish is **Phase 0b** — do not claim PyPI on site until `pip install sourcea-boot` resolves on PyPI.

## Scope IN

| Step | Deliverable | Acceptance |
|------|-------------|------------|
| P0-1 | Standalone public repo export from `packages/sourcea-boot/` | MIT LICENSE · CI workflow · validate script |
| P0-2 | `scripts/publish_sourcea_boot_public_v1.py` | Builds export · runs local validate · pushes to GitHub |
| P0-3 | Public repo live at `kazemnezhadsina144-dot/sourcea-boot` | `GET /repos/kazemnezhadsina144-dot/sourcea-boot` → 200 |
| P0-4 | README honest about PyPI | Clone path works; PyPI line marked pending until Phase 0b |
| P0-5 | Monorepo package unchanged behavior | `bash scripts/validate-sourcea-boot-v1.sh` still PASS |

## Scope OUT (later phases)

- PyPI publish (`pip install sourcea-boot`) — Phase 0b
- Site trust-signals auto-flip (`github.ok: true`) — after deploy probe
- Brain bundle regen — separate Worker/distill pass

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
| `/eval` verify | links `kazemnezhadsina144-dot/sourcea-boot` |
| `trust-signals.json` | `github.ok: true` |
| PyPI | not published (Phase 0b) |
| Receipt | `~/.sina/sourcea-boot-public-publish-receipt-v1.json` |

**End LOCKED v1**
