# SourceA — H2 Machine Hub Plan (LOCKED v1.1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Authority:** ASF — phase-s8 backlog targets **Hub 2** (heavy machines), not Sina Command archive  
**Supersedes for backlog:** `phase-s8-hub-ui-ux` tasks scoped to **Sina Command** monolith (`app.js` · `command-data.json` · 30 tabs) — **quarantine; do not touch**  
**Parent law:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` v1.2 · `SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md`  
**Machine SSOT:** `GET /api/machine-hub/v1` · `~/.sina/h2-pending-registry-v1.json`  
**Validator:** `bash scripts/validate-machine-hub-v1.sh`

---

## Terminology law (mandatory — no confusion)

| Name | What it is | URL | Daily? | Touch? |
|------|------------|-----|--------|--------|
| **Sina Command** | **OLD** product — quarantined archive | `http://127.0.0.1:13020/legacy/` | **No** | **Never** — frozen reference only |
| **Hub 1** | **NEW** dual model — worker daily necessities | `http://127.0.0.1:13020/` | **Yes** | Light refresh · `worker-hub/v1` |
| **Hub 2** | **NEW** dual model — heavy machines + pending | `http://127.0.0.1:13020/machines/` | **No** | Scheduled receipts only |

**Forbidden labels:** calling Sina Command “Hub 1” · calling the monolith “daily hub” · patching archive for factory or daily fixes.

**Hub 1 ≠ Sina Command.** Hub 1 and Hub 2 are **siblings** built after archive quarantine.

---

## Law (one sentence)

**Hub 2 (`/machines/`) owns heavy machines and organized pending on a schedule — Hub 1 (`/`) is workers-only daily truth — Sina Command (`/legacy/`) stays quarantined archive; nobody touches it for active plans.**

---

## 0. What changed (Sina Command plan → Hub 2 plan)

| Old plan (wrong scope — Sina Command archive) | New plan (Hub 2) |
|------------------------------------------------|------------------|
| Patch `app.js` · lazy `command-data.json` | Ship **`machines/index.html`** + **`/api/machine-hub/v1`** slices |
| 30-tab monolith NAV sync | **Pending registry buckets** + tab slices from disk receipts |
| Founder Refresh → full panel rebuild | **Weekly** machine receipt bundle · **never** on Hub 1 daily refresh |
| `phase-s8` = Sina Command UI/UX | **`phase-s8` = Hub 2 Machine Hub** — sibling surface, not sub-page |
| Progress from 9MB hero | Progress from **`h2-pending-registry-v1.json`** + validators |

**Done s8 rows (sa-0801–sa-0881, 24):** historical **Sina Command lite** work (pre-dual-hub) — keep receipts; do not re-open.  
**Backlog s8 rows (sa-0807–sa-0900, 76):** execute under **this Hub 2 plan**.

---

## 1. Hub 2 scope (in)

| # | Machine | Data / API | Cadence |
|---|---------|------------|---------|
| 1 | **Pending registry** | `h2-pending-registry-v1.json` · honest `pending_total` | Daily sync · weekly review |
| 2 | **Bucket taxonomy** | `form_open` · `next_phase` · `deferred` · `ops_blocker` · `maintainer_ship` · `thread_room` · `scheduled_cadence` | On reconcile |
| 3 | **Machine hub payload** | `/api/machine-hub/v1` · `<16 KB` · no Sina Command embed | Daily health |
| 4 | **Hub 2 UI shell** | `machines/index.html` — health pill · poll · light refresh · sibling banner | Weekly SHIP |
| 5 | **Thread Room** | Second hop only — `thread-room/latest-curation-v1.json` summary | Weekly scout |
| 6 | **Judge strip** | `judge-center/latest-alarm-strip-v1.json` — one line on Hub 1, full batch Hub 2 | Weekly |
| 7 | **Tab slices** | `hub_surface_v1.py` receipts — WTM · fleet · packet · drift · council | Scheduled |
| 8 | **Staleness + heal** | `machine_hub_staleness_v1.py` · `hub_dual_heal_v1.py` | Daily |
| 9 | **Validators** | `validate-machine-hub-v1.sh` · `validate-h2-pending-honest-count-v1.sh` | Every VERIFY |
| 10 | **Form mirror** | `form_open` ↔ `live_founder_decision_form_v1.py` | On Form change |

---

## 2. Out of scope

| Item | Route |
|------|-------|
| Worker task · queue · Valid YES · Safety | **Hub 1** `/` · `/api/worker-hub/v1` |
| `command-data.json` hero · 42 tabs · `app.js` | **Sina Command** `/legacy/` · quarantine — monthly archive only |
| Full `build-sina-command-panel.py` on founder click | **Forbidden** on daily path |
| Thread Room panels inline on Hub 1 | **Forbidden** — alarm line + Hub 2 link only |
| New hub tabs before substrate | **Forbidden** per WTM law |

---

## 3. Phase-s8 execution grid (100 prompts)

**Phase id:** `phase-s8-hub-ui-ux` *(unchanged id — backlog reinterpreted for Hub 2)*  
**Phase label:** **Hub 2 Machine Hub** — pending registry · scheduled machines · sibling `/machines/`  
**URL:** `http://127.0.0.1:13020/machines/`

### Tier intent

| Tier | Depth | Verify gate |
|------|-------|-------------|
| **T0** | Critical — registry honest count · payload size · validator PASS | `validate-machine-hub-v1.sh` + `worker_verify_fast_v1.sh` |
| **T1** | Sprint — bucket row SHIP · UI parity · reconcile scripts | + `validate-h2-pending-honest-count-v1.sh` |
| **T2** | Quarterly — crossref laws · cadence docs · integration-fabric | + `hub_dual_heal_v1.py --json` |
| **T3** | Research/polish — industry compare · evidence rows only | + `find_critical_bugs.py` (no scope creep) |

### 25 slot themes (repeat per tier with escalating depth)

1. machine-hub/v1 payload size — no Sina Command embed  
2. h2-pending-registry honest pending_total  
3. machines/index.html health pill + live poll parity with Hub 1  
4. validate-machine-hub-v1.sh sibling copy gate  
5. pending bucket taxonomy vs SUPER_FAST_HUB §2a  
6. form_open mirror ↔ M1 Canvas PICK rows  
7. next_phase bucket vs PROGRAM_PROGRESS founder_open  
8. deferred vs scheduled_cadence separation  
9. thread_room summary — Hub 2 only  
10. judge alarm strip — Hub 1 one line / Hub 2 full  
11. hub_dual_heal Hub 2 sync after Hub 1 light refresh  
12. machine_hub_staleness auto-heal path  
13. maintainer_ship_closed rows off pending_total  
14. weekly machine receipt bundle cadence  
15. hub_surface_v1 tab slices without command-data hero  
16. sibling-hub navigation law — not sub-page  
17. Hub 2 light refresh — no build-sina-command-panel  
18. validate-h2-pending-honest-count after reconcile  
19. Thread Room second-hop law crossref  
20. machines banner peer-hub wording  
21. ops_blocker row contracts (MP-SHIP · WIRE-G3 · B-001)  
22. scheduled_cadence UP-01…UP-06 excluded from open pending  
23. ENFORCE / packet readiness maintainer slice on Hub 2  
24. Hub 2 evidence row after weekly SHIP pass  
25. Sina Command archive banner vs Hub 2 bookmark law  

---

## 4. Cloud Forge Run alignment

| Signal | Value |
|--------|-------|
| **Cycle** | **3** — Hub 2 machine drain |
| **Active pack** | **s8-H2-P1** (`sa-0807` → `sa-0816`) · 30 turns |
| **Phase-strict** | `s8` **active** — Sina Command quarantine unchanged |
| **Pick head** | **sa-0807** CHECK |
| **Worker law** | Hub 2 VERIFY uses `validate-machine-hub-v1.sh` — not Sina Command closeout |
| **Brain duty** | Update `h2-pending-registry-v1.json` every session |

### Hub 2 pack grid (76 backlog · 8 packs)

| Pack | SA range | Turns |
|------|----------|-------|
| s8-H2-P1 | sa-0807 → sa-0816 | 30 |
| s8-H2-P2 | sa-0817 → sa-0832 | 48 |
| s8-H2-P3 | sa-0833 → sa-0842 | 30 |
| s8-H2-P4 | sa-0843 → sa-0858 | 48 |
| s8-H2-P5 | sa-0859 → sa-0868 | 30 |
| s8-H2-P6 | sa-0869 → sa-0884 | 48 |
| s8-H2-P7 | sa-0885 → sa-0894 | 30 |
| s8-H2-P8 | sa-0895 → sa-0900 | 18 |

---

## 5. Ship order (Maintainer 2 — when ASF names Hub 2 pack)

1. **Reconcile** — `h2_pending_registry_reconcile_v1.py` · honest count PASS  
2. **Health parity** — Hub 2 poll + heal matches Hub 1  
3. **Bucket SHIP** — ops_blocker highest (MP-SHIP · WIRE-G3)  
4. **Weekly machines** — Thread Room + Judge batch receipts  
5. **Tab slices** — WTM · fleet · council from receipts  
6. **Evidence** — SOURCEA-PRIORITY rows per closed sa-08xx  

---

## 6. Proof commands

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-machine-hub-v1.sh
bash validate-h2-pending-honest-count-v1.sh
python3 h2_pending_registry_reconcile_v1.py --json
python3 hub_dual_heal_v1.py --json
curl -s http://127.0.0.1:13020/api/machine-hub/v1 | wc -c   # expect < 16384
```

---

## 7. Canonical pointers

| Topic | Doc |
|-------|-----|
| Dual-hub model | `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` |
| Hub 2 pending fix plan | `archive/attachments/2026-06-14/H2_PENDING_21_ROOT_CAUSE_AND_FIX_PLAN_LOCKED_v1.md` |
| Sibling model | `archive/attachments/2026-06-14/TWO_HUB_SIBLING_MODEL_ADVISOR_LOCKED_v1.md` |
| Form + Hub 2 order | `archive/attachments/2026-06-14/ASF_FORM_OFFICIAL_H2_PENDING_ORGANIZATION_ORDER_2026-06-14_LOCKED_v1.md` |
| 1000-pack phase | `brain-os/plan-registry/SOURCEA-1000-LOCK.md` §phase-s8 |
| Generator | `scripts/generate-sourcea-1000-prompts.py` — s8 task list = Hub 2 |

---

*End SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.1*
