# Hub ↔ Source ↔ UI Alignment Procedure (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**Parent laws:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` (Order 12 — verify) · `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md`  
**Hub tab:** World Target Model → `http://127.0.0.1:13020/?tab=system-roadmap`  
**Audit:** `scripts/audit_hub_source_alignment.py` (strict on every hub build)

---

## Law (one sentence)

**Founder UI never owns roadmap truth** — locked rules live in one code SSOT, flow through one build into one payload, and the UI only renders that payload.

---

## Single chain of custody

```text
scripts/system_roadmap.py     ← CODE SSOT (steps, phases, next_move, version)
        ↓
WORLD_TARGET_MODEL_MAP_LOCKED_vN.md   ← human-readable mirror (narrative + table)
        ↓
python3 scripts/build-sina-command-panel.py
        ↓
command-data.json · index.html   ← embedded system_roadmap payload
        ↓
agent-control-panel/assets/app.js   ← RENDER ONLY (no duplicate catalogs)
        ↓
Founder hub UI (World Target Model tab)
```

**Runtime API (live refresh):** `GET /api/system-roadmap` and `POST /refresh` → same `system_roadmap_payload()` function.

---

## What you edit (and what you never edit)

| Layer | Edit when roadmap changes? | Role |
|-------|---------------------------|------|
| `scripts/system_roadmap.py` | **YES — always first** | `STEP_CATALOG`, phase subphases, `STRATEGIC_BUILD_PHASES`, `PAYLOAD_VERSION`, `MAP_DOC` |
| `WORLD_TARGET_MODEL_MAP_LOCKED_vN.md` | **YES — mirror** | Founder-readable map; step table must match payload |
| `agent-control-panel/assets/app.js` | **NO** for step lists / counts / versions | Layout + render helpers only; read `sr.ui_contract` |
| `important_docs_index.py` | **Only `MAP_DOC` path** | Index pointer — audit enforces match |
| `roadmaps_goals.py` | **Only `wtm_pointer.map_doc`** | Tab separation pointer — audit enforces match |

---

## Upgrade procedure (vN → vN+1)

Executor runs this **in order** — skipping a step causes audit failure.

1. **Convince + place** per `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` (Orders 1–9).
2. **Edit code SSOT** — `scripts/system_roadmap.py`:
   - bump `PAYLOAD_VERSION`
   - update `MAP_DOC` to `*_v{N+1}.md`
   - add/change steps in `STEP_CATALOG`, `_phases_def()` subphases, `STRATEGIC_BUILD_PHASES`
   - update `WORLD_TARGET_MAP.next_move` / `then_queue` if needed
3. **Write** `WORLD_TARGET_MODEL_MAP_LOCKED_v{N+1}.md` at SourceA root (step table = payload).
4. **Archive** old map: `mv *_vN.md` → `archive/superseded/wtm/vN/`
5. **Append** evidence row to `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md`
6. **Cross-links** — update `MAP_DOC` pointer in law + big picture + pre-LLM + alignment law (audit checks these).
7. **Rebuild hub:**
   ```bash
   python3 scripts/build-sina-command-panel.py
   ```
   Build runs `audit_hub_source_alignment.py` — **must print OK**.
8. **Restart** hub server if already running (`sina-command-server.py`) so `/refresh` serves new payload.
9. **Browser check** — World Target Model tab: version, step count, Future column, Next build panel.

**Helper script (archive only):** `scripts/archive-superseded-wtm-doc.py`

---

## What the audit enforces (automatic)

`audit_hub_source_alignment.py` fails the build if:

- `MAP_DOC` missing at root or version ≠ `PAYLOAD_VERSION`
- MAP step table ≠ Phase D steps in `system_roadmap.py`
- `STEP_CATALOG` missing any Phase D step ID
- `strategic_build_phases` IDs drift from Phase D
- `important_docs_index` or `roadmaps_goals.wtm_pointer` map path ≠ `MAP_DOC`
- Superseded `WORLD_TARGET_MODEL_MAP_LOCKED_v1/v2.md` still at root
- `command-data.json` `system_roadmap.version` / `map_doc` stale after build
- `app.js` contains forbidden hardcoded step counts or stale map paths
- `app.js` missing SSOT hooks: `srStrategicStepCount`, `ensureSystemRoadmap`, `ui_contract`

---

## UI render contract (founder tab)

Payload field `ui_contract` is the UI’s allowed fallback source:

| UI element | Data source (in order) |
|------------|------------------------|
| Step count headers | `srStrategicStepCount(sr)` → `ui_contract.strategic_build_step_count` |
| Build order span | `futurePhase.steps` or `ui_contract.phase_d.build_order_span` |
| Next build ID/title | `world_target_map.next_move` |
| Then queue | `next_move.then_queue` |
| Parallel runtime | `next_move.runtime_parallel` |
| Doc picker buttons | `sr.law_doc`, `sr.map_doc` from payload |
| Phase swimlanes / Future column | `sr.phases` / `sr.journey` / `sr.live` |

**Forbidden in app.js:** duplicate step catalogs, fixed version strings, fixed “12 steps” labels.

---

## Order 12 checklist (alignment law)

- [ ] `system_roadmap.py` updated + `PAYLOAD_VERSION` bumped  
- [ ] MAP vN+1 written; vN archived; manifest row added  
- [ ] `python3 scripts/build-sina-command-panel.py` → audit **OK**  
- [ ] Hub tab matches payload (version, steps, next build)  
- [ ] Example/analysis stays in `archive/attachments/examples/` if not canonical  

---

## Incident prevention

| Incident | Prevention |
|----------|------------|
| UI shows old step count | Audit + dynamic `srStrategicStepCount` |
| `/refresh` drops WTM | `ensureSystemRoadmap()` + preserve in `applyPayload` |
| Chat paste becomes source | Alignment law — sub-steps only after convince |
| Agent tables in founder UI | INCIDENT-002 — payload-only render |

---

**LOCKED:** One SSOT · one build · one payload · UI renders only.
