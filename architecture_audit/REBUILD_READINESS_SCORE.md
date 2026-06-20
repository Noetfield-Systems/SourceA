# REBUILD_READINESS_SCORE.md

Assessment for whether the Agentic OS Control Panel Hub can be reconstructed or evolved. Scores 0–100 (higher = better for that dimension unless noted).

**Audit mode:** observation only — no fixes applied.  
**Post-N1 note (2026-06):** Scores below reflect pre-stabilization write; boot checklist and async-refresh rows amended after Phase N1 + P1–P7.

---

## Can this architecture be rebuilt?

**Yes — with effort: 72/100**

The system is fully traceable:
- Single server file (`sina-command-server.py`) with explicit path routing
- Monolithic payload assembler (`build_payload` in `sina_command_lib.py`)
- Disk artifacts (`command-data.json`, shell, `index.html`) are deterministic outputs
- UI is self-contained in `agent-control-panel/`

**Blockers to naive rebuild:**
- ~50 payload modules with implicit ordering dependencies inside `build_payload`
- Branch action dispatch spread across `sina_command_lib.py` lines 2197–2733
- SSOT files scattered across repo + `~/.sina`
- No OpenAPI spec — routes discovered only by reading handler

---

## Capability questions

| Question | Answer | Score |
|----------|--------|-------|
| Can it be modularized? | Possible — modules already exist but are called synchronously in one function; extraction needs interface contracts | 45 |
| Can payloads become lazy? | Shell split exists (`HEAVY_PAYLOAD_KEYS`) but server still builds full dict; UI lazy-load is partial | 55 |
| Can refresh become async? | **Amended:** `POST /refresh` → 202 + `hub-rebuild-queue-v1.jsonl`; worker on `:13030` coalesces rebuilds | 70 |
| Can panel become incremental? | No merge/patch layer — always full `write_panel_outputs` | 25 |
| Can builders become isolated? | Each `*_payload()` is already a file — but no DI, shared global reads, implicit order | 50 |
| Can state become normalized? | Queue/factory/progress duplicated across REGISTRY, truth, factory-now, payload | 35 |
| Can cache become authoritative? | Cache is secondary to disk; `hub-sync` bypasses cache; TTL 180s only | 40 |
| Can UI become event driven? | Polling only; no WebSocket/SSE; `applyPayload` is bulk merge | 35 |
| Can mutations become tiered? | L0 IC path proves pattern works; ~28 routes still T2/T3 | 50 |
| Can E2E become lightweight? | E2E cancelled; strict build still runs 40+ validators | 55 |

---

## Dimension scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Maintainability** | 38 | One 9k-line UI file + 4k-line lib + 1.7k-line server; path router grows linearly |
| **Coupling** | 28 | `hub_after_mutation` couples every POST to full rebuild; modules read each other's SSOT |
| **Complexity** | 32 | ~150 routes, ~50 payload builders, refresh pipeline, factory freeze, goal1 workers |
| **Testability** | 42 | Many bash validators; no unit test harness for `build_payload`; E2E was brittle (cancelled) |
| **Scalability** | 25 | Single-threaded rebuild lock; 2.7MB JSON per mutation; localhost design |
| **Reliability** | 48 | Atomic writes, cache warm on boot, FREEZE gates; but SIGKILL under concurrent heavy jobs |
| **Developer Experience** | 52 | `serve-sina-command.sh` worker-first chain; POST returns fast when four NEVER rules hold (rebuild off request thread) |
| **Technical Debt** | 22 | Legacy `sina-command-api.py`, broken POST routes in `do_GET`, hub-sync misnamed "light" |

**Overall rebuild readiness: 36/100** (rebuildable but not healthy without architectural intervention)

---

## What a rebuild engineer needs (checklist)

1. **Boot:** `serve-sina-command.sh` → `serve-hub-rebuild-worker.sh` (`:13030`) then `sina-command-server.py:main()` (`:13020`)
2. **Cold start:** missing `command-data.json` → `hub_after_mutation(write_html=True)`
3. **Payload contract:** keys in `build_payload()` return dict — document each key → module file
4. **Shell contract:** `HEAVY_PAYLOAD_KEYS` in `sina_command_lib.py` — keys stripped for shell JSON
5. **Mutation contract:** POST handler writes SSOT → `hub_after_mutation` tier decision
6. **Refresh contract:** `run_refresh_pipeline` 4 scripts before rebuild when `run_refresh_scripts=True`
7. **UI contract:** `app.js` `D` global state, `applyPayload`, `HEAVY_TAB_KEYS`, `refreshFromApi`
8. **Factory contract:** `factory-now-v1.json`, FREEZE, `healthy-drain-orchestrator`
9. **Validators:** `validate-hub-p0-no-autorun-v1.sh` post-mutation; strict CI chain in `build-sina-command-panel.py`
10. **Ports:** `:13020` hub (browser entry) + `:13030` rebuild worker (`PORT_CATALOG.json`, `SINAAI_PORT_REGISTRY_LAW_LOCKED_v1.md` §5)

---

## Risk matrix for greenfield rebuild

| Risk | Severity | Mitigation in rebuild |
|------|----------|----------------------|
| Monolithic `build_payload` | Critical | Document module order; consider registry |
| `hub_after_mutation` default | Critical | Tier router from day one |
| `hub-sync` full build | High | Read-only cache serve |
| 2.7MB JSON round-trip | High | Per-tab API from start |
| Broken POST-in-GET routes | Medium | Proper method dispatch |
| No WebSocket | Medium | SSE or poll with etag |

---

## Conclusion

The Hub **can be rebuilt from this audit** — entrypoints, state map, API map, call graph, and panel build map provide sufficient blueprint. The architecture is **not** ready for incremental extension without performance regression because mutation paths default to full synchronous rebuild. The highest-value architectural fact for a rebuilder: **separate read path (cache/disk serve) from write path (tiered mutation router)** — the codebase already has T0 (`invalidate_hub_cache`) and T3 (`/refresh`) at opposite ends; most routes sit at T2.
