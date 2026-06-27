# Portfolio Upgrade Plans — Canonical (LOCKED v1)

**Saved at:** 2026-06-24T20:00:00Z  
**Canonical master:** `brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json`  
**Mapping:** `data/upgrade-888-to-sa-next-mapping-v1.json`  
**Merger:** `scripts/merge_upgrade_888_into_portfolio_next_v1.py`

---

## One law

> **6000 next plans are the single canonical upgrade registry. UP-888 is superseded lineage mapped into SourceA `sa-next-0001`…`sa-next-0888`.**

---

## Supersession

| Registry | Status | Path |
|----------|--------|------|
| Portfolio next 6000 | **active** | `brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json` |
| UP-888 upgrade plans | **superseded** | `brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json` |
| Roadmap redirect stub | redirect only | `brain-os/roadmap/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json` |

Governance rows: `portfolio_next_6000` (active) · `upgrade_plans_888` (superseded) in `data/sourcea-governance-ssot-registry-v1.json`.

---

## Mapping law

| Legacy | Canonical |
|--------|-----------|
| `UP-0001` | `sa-next-0001` |
| `UP-0888` | `sa-next-0888` |
| `sa-next-0889`…`1000` | Generator-native gap-fill (no UP lineage) |

Each merged row carries `legacy_upgrade_id` in `portfolio-next-6000/sourcea/REGISTRY.json`.

---

## Pick authority (unchanged)

1. `SOURCEA-PRIORITY.md` **queue_sa** + Revenue Engine open CRM rows  
2. `sa-next-*` phase-first (`NOW` → `NEXT` → `LATER` → `MOONSHOT`)  
3. Frozen `sourcea-1000` (`sa-*`) — historical only  

```bash
cd ~/Desktop/SourceA
bash scripts/plan-no-asf-run.sh pick-next 3
python3 scripts/pick_portfolio_next_plan_v1.py --repo sourcea --any-phase --limit 3 --prompt
```

**Cash law:** Revenue Engine + T1 client beat rank-1 plan pick until W3/SW2 fire (`SOURCEA_PLANNING_AUTHORITY_CARD_LOCKED_v1.md`).

---

## Validate

```bash
bash scripts/validate-portfolio-upgrade-canonical-v1.sh
bash scripts/validate-portfolio-next-6000-v1.sh
```

---

## Re-merge (idempotent)

```bash
python3 scripts/merge_upgrade_888_into_portfolio_next_v1.py --supersede
```

Does **not** call `generate_portfolio_next_6000_plans_v1.py` (would wipe merges).

---

*Portfolio upgrade canonical v1 · June 2026*
