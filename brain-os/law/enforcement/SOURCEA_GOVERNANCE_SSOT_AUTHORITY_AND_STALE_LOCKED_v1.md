# Governance SSOT authority & stale rule cleanup (LOCKED v1)

**Saved:** 2026-06-26T06:50:00Z  
**Status:** LOCKED  
**Registry:** `data/sourcea-governance-ssot-registry-v1.json`  
**Law authority index:** `brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md`  
**Check:** `python3 scripts/sourcea_governance_ssot_registry_v1.py --json --write-receipt`  
**Index:** `brain-os/ssot/SSOT_PLANE_INDEX_LOCKED_v1.md`

---

## One law

> **Authority comes from registry status — not from a file simply existing.** Exactly one **operating law** (`llm_agent_operating_law` family) may be **ACTIVE**. Superseded docs are governed history. **Stale** is the only cleanup target: ambiguous authority with no declared registry row.

---

## Three states (never mix)

| State | Meaning | Agent may execute? |
|-------|---------|-------------------|
| **ACTIVE** | Registered row with `status: active` · exactly one operating-law row | **Yes** — dispatch + ORD truth gate |
| **SUPERSEDED** | Registered row with `status: superseded` · quarantine under `brain-os/ssot/superseded/` or registered `pdf_path` | **No** — lineage only · do-not-operate |
| **STALE** | Rule-like doc on disk with **no registry row** on its plane | **No** — flag for founder review · never auto-delete |

**Stale ≠ old.** A clearly-marked superseded doc is governed history, not stale.  
**Stale ≠ draft.** Draft rows exist in the registry with `status: draft` — not ambiguous.

---

## Two registry planes (do not merge)

| Plane | Registry | Governs |
|-------|----------|---------|
| **SSOT plane** | `data/sourcea-governance-ssot-registry-v1.json` | Operating law v3 · roadmap · cloud kernel · upgrade plans |
| **Law plane** | `brain-os/system/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` (+ `LAW_ROOT_INDEX` · gov-unify manifest · allowlist) | `brain-os/law/**/*_LOCKED*.md` topic laws |

A law-plane doc is **not stale** when its path appears in the authority index (or law root index / allowlist).  
An SSOT-plane doc is **not stale** when its path appears in the governance SSOT registry.

---

## Stale definition (enforcement)

A document is **STALE** when **all** of the following hold:

1. It matches a **rule-like scope** glob (registry `rule_like_globs`).
2. Its repo-relative path is **not** registered on its plane:
   - SSOT / roadmap / ssot/*.md → `entries[].path|pdf_path|symlink_path` in governance SSOT registry
   - `brain-os/law/**` → authority index · law root index · gov-unify manifest · `data/authority-root-allowlist-v1.json`
3. It is **not** excluded: `*INDEX_LOCKED*.md` · `README_LOCKED*.md` · paths under `superseded/` or `archive/`.

**Stale means ambiguous authority** — an agent could treat the file as operative law because nothing on disk declares otherwise.

**Forbidden on stale:** auto-delete · auto-archive · silent supersede. **Required:** flag in check output · founder adds authority row or SSOT registry entry · or relocates to superseded quarantine.

---

## Operating law (single active)

| Field | Value |
|-------|-------|
| **Family** | `llm_agent_operating_law` |
| **Active id** | `llm_agent_operating_law_v3` (from `active_operating_law_id`) |
| **Active path** | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` |
| **Superseded slots** | v1 · v2 — registered with `status: superseded`; `path` may be `null` until markdown recovered |

Lineage fields: `supersedes[]` · `superseded_by` on each registry entry.

---

## Rule-like scope (expanded 2026-06-26)

| Glob | Plane | Registered via |
|------|-------|----------------|
| `brain-os/ssot/*.md` | SSOT | governance SSOT registry |
| `brain-os/roadmap/SOURCEA_*.md` | SSOT | governance SSOT registry |
| `brain-os/law/**/*_LOCKED*.md` | Law | authority index (+ law root · allowlist) |

**Excluded:** `*INDEX_LOCKED*.md` · `README_LOCKED*.md` · `superseded/` · `archive/`.

**Not in scope:** `.cursor/rules/**` · `data/*-v1.json` — separate surfaces (expand only by founder order).

---

## Check contract

```bash
python3 scripts/sourcea_governance_ssot_registry_v1.py --json --write-receipt
# or: bash scripts/validate-governance-ssot-registry-v1.sh
```

| Output field | Meaning |
|--------------|---------|
| `active_count` | Must be `1` (operating-law family) |
| `stale_candidates` | Flag list — **non-empty is expected** during cleanup; review each row |
| `stale_by_plane` | `{ law, ssot_plane }` counts |
| `ok` | `true` only when zero structural issues **and** zero stale candidates |

Receipt: `~/.sina/sourcea-governance-ssot-registry-check-v1.json`

---

*Governance SSOT authority & stale cleanup v1 · law-plane expansion 2026-06-26 · mirrors Blueprint Registry status pattern.*
