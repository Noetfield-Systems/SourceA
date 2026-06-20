# Ecosystem Status (generated — do not edit by hand)

**Generated:** 2026-06-14 01:32 UTC  
**By:** SinaPromptOS — run `python main.py` or `./scripts/publish-ecosystem.sh`  
**All repo Cursor agents must read this file before awareness or implement.**

> Law: `SINA_OS_SSOT_LOCKED.md` · Notice prompts: `CURSOR_REPO_AGENT_NOTICE_PROMPTS_v1.md`

## FAST TRACK — FORCE MAJEURE (active)

**NO WAIT · NO BLOCK · ALL LANES PARALLEL** — `SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md`

Repo blockers below are **local only** — they do **not** stop wire, Pro, or other repos.

## Global priority (this week)

1. **VIRLUX** (`virlux`) — score 117
2. **777 Foundation** (`seven77`) — score 96
3. **TrustField** (`trustfield`) — score 75
4. **Noetfield** (`noetfield`) — score 32
5. **Sinaai PAIOS (MonoRepo)** (`sinaai_mono`) — score 22
6. **Sina Prompt OS (meta — not a daily lane)** (`sina_prompt_os`) — score 18

## Active focus

### VIRLUX [DELIVERY] — rank #1
- **Next:** staging smoke test
- **Blocked:** 2
- **Depends on:** trustfield
- **Risk:** MEDIUM

### 777 Foundation [DELIVERY] — rank #2
- **Next:** homepage content pass
- **Blocked:** 3
- **Risk:** MEDIUM

### TrustField [DELIVERY] — rank #3
- **Next:** postgres validation
- **Risk:** LOW

### Noetfield [DESIGN] — rank #4
- **Next:** spec section 3 review
- **Depends on:** sinaai_mono, trustfield
- **Risk:** LOW

### Sinaai PAIOS (MonoRepo) [DESIGN] — rank #5
- **Next:** runtime health check
- **Depends on:** trustfield
- **Risk:** LOW

### Sina Prompt OS (meta — not a daily lane) [META] — rank #6
- **Next:** Add daily scheduled snapshot (launchd or cron) writing to data/
- **Risk:** LOW


## Port notice board (mandatory)

# PORT NOTICE BOARD (live — agents read this first)

**Updated:** 2026-06-12T16:59:07Z  
**Locked rules:** `PORT_NOTICE_BOARD_LOCKED_v1.md`  
**Law:** `SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md`  

---

## SUGGESTED FREE PORTS (use these — do not guess)

| Use case | Port | Command |
|----------|------|---------|
| **DevBridge Safari desk** | **3004** | `cd ~/Desktop/AI\ Dev\ Bridge\ OS && npm run start` |
| **DevBridge Mac agent (WS)** | **8766** (already running — reuse) | `npm start` / agent :8766 |
| **Never for DevBridge desk** | **3000–3003** | Noetfield / VIRLUX / ASF reserved |

**All free desk ports:** 3004, 3005, 3006, 3007, 3008, 3009, 3010

---

## VIOLATIONS — fix before bind

- **:13020** — Port 13020 is bound by unknown_python but catalog owner is sina_command; no other product may listen here.
- **:13030** — Port 13030 is bound by unknown_python but catalog owner is hub_rebuild_worker; no other product may listen here.

**Auto-fix DevBridge desk:** `cd ~/Desktop/AI\ Dev\ Bridge\ OS && npm run fix:ports`

---

Full board: `PORT_NOTICE_BOARD.md`


## Wire lane (P2 — NOT blocked by repo work)

Checklist: `WIRE_LANE_PROGRESS.md`

**Still open for wire:**
- [ ] **full_m8 on iPhone** — `npm run proof:iphone-production` → RUN SYSTEM → log NOT `smoke: complete` only
- [ ] Record full_m8: `--lane full_m8` or one tap after full_m8 PASS
- [ ] **G3 Tailscale** — `lane=full_m8` on `100.x` URL → `npm run record:g3 -- --host ... --run-id ... --pass true`

## Global blockers (repo-only — do NOT block wire P2)

> Law: `SINAAI_PARALLEL_LANES_NO_BLOCK_PROGRESS_LOCKED_v1.md` — VIRLUX / Mono / 777 blockers are parallel; wire continues.

- **VIRLUX:** Railway virlux-api-production.up.railway.app optional — 404; use https://virlux-api.vercel.app —  _(does not block DevBridge wire)_
- **VIRLUX:** virlux.com serves /lander stub — marketing E2E uses virlux-web.vercel.app —  _(does not block DevBridge wire)_
- **777 Foundation:** gate0_outbound_send — human_outbound _(does not block DevBridge wire)_
- **777 Foundation:** board_sign_offs — board_session _(does not block DevBridge wire)_
- **777 Foundation:** resend_digests — missing_vault_key _(does not block DevBridge wire)_

## Cascade (informational)


## Global rule (ASF)

- No architecture redesign this week unless ASF approves. TrustField: ops/gates only (freeze ON).

## Files for agents

| File | Use |
|------|-----|
| `SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md` | **NO WAIT — NO BLOCK — read first** |
| `WIRE_LANE_PROGRESS.md` | P2 wire checklist |
| `SINAAI_PARALLEL_LANES_NO_BLOCK_PROGRESS_LOCKED_v1.md` | Parallel lanes |
| `PORT_NOTICE_BOARD.md` | **Suggested free ports — read first** |
| `PORT_REGISTRY.md` | Full live port table (law) |
| `PORT_REGISTRY.json` | Machine port truth |
| `SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md` | Port law (locked) |
| `ECOSYSTEM_STATUS.md` | This file |
| `GLOBAL_PRIORITY.json` | Ranks + agent_cards |
| `GLOBAL_BLOCKERS.json` | Blockers + graph |
| `ECOSYSTEM_GRAPH.json` | depends_on / affects / risk |
| `REPO_STATUS_REPORTS/*.yaml` | Agent status (intent) |
| `REPO_EXECUTION_LOGS/<repo>/*.yaml` | Execution truth (evidence) |
| `EXECUTION_TRUTH.json` | Report vs log verification |
| `FEEDBACK_AGGREGATE.json` | Last re-rank |
| `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md` | Execution evidence law |
| `SINAAI_PHASE2_AI_CONTROLLED_EXECUTION_LOCKED_v1.md` | AI control law |
| `PHASE2_EVALUATIONS.json` | Task evaluator + planner |
| `SEMANTIC_PROGRESS.json` | Semantic progress v1 |
| `SINAAI_ECOSYSTEM_FINAL_STATE_AND_NEXT_PLAN_LOCKED_v1.md` | Handoff when lost |


## Repo agent reports (feedback loop)

**Reports on disk:** 5 / 6  
**Folder:** `/Users/sinakazemnezhad/Desktop/SourceA/REPO_STATUS_REPORTS`  
**Aggregate:** `FEEDBACK_AGGREGATE.json`

| Repo | Health | Progress | Conf | Hours | Blocked |
|------|--------|----------|------|-------|---------|
| VIRLUX | yellow | 55% | 0.80 | 4.0 | 0 |
| 777 Foundation | green | 30% | 0.75 | 3.0 | 0 |
| TrustField | yellow | 72% | 0.85 | 6.0 | 1 |
| Noetfield | green | 20% | 0.60 | 12.0 | 0 |
| Sinaai PAIOS (MonoRepo) | green | 40% | 0.70 | 8.0 | 0 |
| Sina Prompt OS (meta — not a daily lane) | — | — | — | — | no report |

**Missing reports:** sina_prompt_os

Submit: `./scripts/submit-repo-report.sh <project_id> report.yaml`

## Execution truth (verified work)

**Logs:** `/Users/sinakazemnezhad/Desktop/SourceA/REPO_EXECUTION_LOGS`  
**Aggregate:** `EXECUTION_TRUTH.json`

| Repo | Verified done | Unverified claims | Last failure |
|------|---------------|-------------------|--------------|
| VIRLUX | Create or refresh os/plan.json | 0 | — |
| 777 Foundation | Review docs/c1-ops-close.md op | 0 | — |
| TrustField | Lane alignment: B-001 decision | 1 | — |
| Noetfield | Draft tenant + append-only aud | 0 | — |
| Sinaai PAIOS (MonoRepo) | AGENT-AUTO-MONO mx-0017 — curs | 0 | — |
| Sina Prompt OS (meta — not a daily lane) | — | 0 | — |

Submit: `./scripts/submit-execution-log.sh <project_id> log.yaml`