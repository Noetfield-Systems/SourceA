# ENFORCEMENT-1000 — Locked prompt library (ENFORCEMENT-6MO pivot)

**Version:** 2.0 — LOCKED (tier-expanded · categorized)  
**sequence_id:** SA-2026-06-11-ENFORCEMENT-1000  
**Grid:** 10 phases × 4 tiers × 25 = **1000** unique prompts  
**IDs:** `enf-0001` … `enf-1000`  
**Trigger:** `PLAN WITH NO ASF ENFORCEMENT`  
**Category index:** `ENFORCEMENT-1000-CATEGORY-INDEX.md` (run audit to refresh)

---

## Pivot law

Optimizes **W1 + W2 + W3** by Dec 2026 — not factory REGISTRY drain.

> We make AI execution impossible to bypass governance.

**Gate test:** enforcement strength · demo credibility · willingness to pay — else DELETE.

---

## Paths

| Asset | Path |
|-------|------|
| Registry | `brain-os/plan-registry/enforcement-1000/REGISTRY.json` |
| Prompts | `brain-os/plan-registry/enforcement-1000/prompts/` |
| Generator | `scripts/generate-enforcement-1000-prompts.py` |
| Pick | `scripts/pick-enforcement-no-asf-plan.py` |
| Run | `scripts/plan-enforcement-no-asf-run.sh` |
| Validate | `scripts/validate-enforcement-1000-pack.sh` |
| Audit | `scripts/audit-enforcement-1000-v1.py` |
| Categories | `brain-os/plan-registry/ENFORCEMENT-1000-CATEGORY-INDEX.md` |
| Parent law | `brain-os/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` |

---

## Categories (win buckets)

| Category | Win | Owner | Phases |
|----------|-----|-------|--------|
| `W2_KERNEL` | W2 | worker | e0 · e1 · e2 · e8 |
| `W1_DEMO` | W1 | worker | e3 |
| `W3_MONEY` | W3 | commercial | e4 · e7 |
| `CHAOS_HARDEN` | W2 | worker | e5 |
| `NARRATIVE` | seed | commercial | e6 |
| `CLOSEOUT` | Dec | brain | e9 |

**Tier depth:** T0 ship · T1 CI+evidence · T2 chaos · T3 polish-or-DELETE

---

## Phases

| Phase | Focus |
|-------|--------|
| `phase-e0-commit-gate` | Single commit entry · bypass inventory |
| `phase-e1-receipt-integrity` | Receipt · spine bind · append-only |
| `phase-e2-validator-tamper` | HARD FAIL · tamper · universe invariants |
| `phase-e3-demo-live` | 5-min BLOCK/ALLOW/TAMPER · film |
| `phase-e4-commercial-w3` | TF/NF LOI · deposit · pilot |
| `phase-e5-bypass-chaos` | Kill/replay · failure injection |
| `phase-e6-investor-pipeline` | Seed narrative · meetings |
| `phase-e7-regulated-wedge` | Copilot · regulated verticals |
| `phase-e8-kernel-harden` | Demo-scope commit gate closure |
| `phase-e9-dec-closeout` | Dec freeze · W1+W2+W3 binary |

---

## Coexistence

- **Does not replace** `sourcea-1000` factory pack (`sa-XXXX`).
- **Parallel lane** `enforcement-6mo` — background factory stays FREEZE unless ASF resumes.
- Maintainer **FR-003 / 1.10** runs parallel — not blocked.

---

## Regenerate

```bash
cd ~/Desktop/SourceA
python3 scripts/generate-enforcement-1000-prompts.py
python3 scripts/audit-enforcement-1000-v1.py
bash scripts/validate-enforcement-1000-pack.sh
```

---

*End ENFORCEMENT-1000 lock*
