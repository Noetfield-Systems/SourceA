# REBUILD_TRIGGER_MAP.md

Every path that triggers `build_payload`, `hub_after_mutation`, `write_panel_outputs`, `invalidate_hub_cache`, or `run_refresh_pipeline`.

## Core functions

| Function | Cost class | Typical runtime |
|----------|------------|-----------------|
| `invalidate_hub_cache()` | O(1) | <1ms |
| `build_payload(run_refresh_scripts=False)` | **Heavy** | 5–30s (40+ module imports, subprocesses) |
| `build_payload(run_refresh_scripts=True)` | **Very heavy** | 60–180s+ (pipeline + build) |
| `hub_after_mutation()` | **Very heavy** | Same as above + disk write + AS-01 validator (90s cap) |
| `write_panel_outputs()` | Medium | 1–5s (2–3MB JSON serialize + atomic write) |
| `run_refresh_pipeline()` | Heavy | 60–300s per subprocess |

## Tier legend

| Tier | Meaning |
|------|---------|
| T0 | Cache invalidate only |
| T1 | `build_payload` in-memory (no disk write) |
| T2 | `hub_after_mutation` / `write_panel_outputs` (full panel rebuild) |
| T3 | `run_refresh_pipeline` + T2 (`POST /refresh`) |

---

## sina-command-server.py

| Caller (route) | Callee | Tier | Reason | Fanout |
|----------------|--------|------|--------|--------|
| `main()` cold start | `hub_after_mutation(write_html=True)` | T2 | Missing `command-data.json` | 1× full rebuild at boot |
| `POST /refresh` | `hub_after_mutation(run_refresh_scripts=True, write_html=True)` | **T3** | Founder Refresh | Pipeline + panel + HTML |
| `POST /api/rule` | `hub_after_mutation(run_refresh_scripts=True)` | T3 | Rule write success | Pipeline + panel |
| `POST /todo/done` | `hub_after_mutation(run_refresh_scripts=True)` | T3 | Todo close | Pipeline + panel |
| `POST /api/action` | `hub_after_mutation()` | T2 | Branch action success | Panel |
| `POST /api/ai/advisory` | `hub_after_mutation()` | T2 | Advisory run | Panel |
| `POST /api/prompt-queue` | `hub_after_mutation()` | T2 | Queue mutation | Panel |
| `POST /api/prompt-direction` | `hub_after_mutation()` | T2 | Direction mutation | Panel |
| `POST /api/agent-loop` | `hub_after_mutation()` | T2 | start/response/select_workspace | Panel |
| `POST /api/advisor/chat` | `hub_after_mutation()` | T2 | Advisor chat | Panel |
| `POST /api/semej` | `hub_after_mutation()` | T2 | Semej actions | Panel |
| `POST /api/commitments` | `hub_after_mutation()` | T2 | add/done/pin | Panel |
| `POST /api/audit-backlog` | `hub_after_mutation()` | T2 | set_status | Panel |
| `POST /api/agent-review` | `hub_after_mutation()` | T2 | submit/set_status | Panel |
| `POST /api/agent-workspaces` | `hub_after_mutation()` | T2 | ensure | Panel |
| `POST /api/workspace-vault` | `hub_after_mutation()` | T2 | deposit/log | Panel |
| `POST /api/agent-scoreboard` | `hub_after_mutation()` | T2 | submit/verify | Panel |
| `POST /api/essay-discourse` | `hub_after_mutation()` | T2 | submit/mark_best | Panel |
| `POST /api/agent-research` | `hub_after_mutation()` | T2 | submit/promote | Panel |
| `POST /api/incident-room` | `hub_after_mutation()` | T2 | submit (non-list) | Panel |
| `POST /api/conflict-room` | `hub_after_mutation()` | T2 | mutations | Panel |
| `POST /api/founder-requests` | `hub_after_mutation()` | T2 | register/update | Panel |
| `POST /api/founder-advisor-discussion` | `hub_after_mutation()` | T2 | update_decision | Panel |
| `POST /api/order-guardian` | `hub_after_mutation()` | T2 | register/refresh_advisory | Panel |
| `POST /api/founder-agent-guide` | `hub_after_mutation()` | T2 | want/done | Panel |
| `POST /api/governance-drift` | `hub_after_mutation()` | T2 | run/refresh | Panel |
| `POST /api/council-room` | `hub_after_mutation()` | T2 | add_directive | Panel |
| `POST /api/intelligence-circle` L0 | `invalidate_hub_cache()` | **T0** | clear_session, dry chat | None |
| `POST /api/intelligence-circle` L2 | `hub_after_mutation()` | T2 | real chat/talk | Panel |
| `GET /api/hub-sync` | `build_payload(run_refresh_scripts=False)` | **T1** | Light sync (still builds in request thread!) | In-memory only |
| `POST /api/run-goal1-*` | `build_payload(run_refresh_scripts=False)` | T1 | Response payload only | No disk write |

**Estimated `hub_after_mutation` call sites in server:** ~28 conditional + 1 unconditional `/refresh` + 1 cold start.

---

## build-sina-command-panel.py

| Caller | Callee | Tier | Reason |
|--------|--------|------|--------|
| `_main_body()` | `build_payload()` + `_write_panel()` | T2 | Strict CI |
| `_sync_command_data_eval()` | `_write_panel(json_only=True)` | T2 partial | Eval win pct sync |
| Post-validators | `_write_panel(json_only=True)` | T2 partial | Feedback sync |
| `SINA_RUN_BACKEND_E2E=1` + `SINA_E2E_FORCE=1` | `audit_backend_e2e.py` | — | **Cancelled by default** |

---

## sina_command_lib.py (founder actions / branches)

`run_branch_action()` and `founder_actions_grouped` handlers internally call `build_payload` + `write_panel_outputs` for actions like:
- `hq-refresh` → `build_payload(run_refresh_scripts=True)`
- Various `pos-*` branches → `build_payload(run_refresh_scripts=False)`

Lines ~2197–2733: multiple `build_payload` / `write_panel_outputs` pairs inside branch action dispatch.

---

## Other callers

| File | Trigger | Tier |
|------|---------|------|
| `align_command_data_ui_v1.py` | CLI align | T2 json_only |
| `live-agent-cursor-reply.sh` | Maintainer reply | T2 |
| `sina-command-api.py` (legacy) | `/refresh`, `/todo/done` | T2/T3 |
| `sina_ai_advisory.py` | `run_advisory` | T1 read |

---

## Indirect / nested paths

```
hub_after_mutation
  └─ get_hub_payload(force=True)
       └─ build_payload(run_refresh_scripts=?)
            ├─ [if True] run_refresh_pipeline
            │    ├─ scan-cursor-agent-fleet.py
            │    ├─ update-program-progress.py
            │    ├─ build-sina-daily-bowl.py
            │    └─ export-master-orders-json.py
            ├─ load_json × 10+ repo files
            ├─ ecosystem_subjects.ecosystem_payload (may refresh scan)
            ├─ subprocess healthy-drain-orchestrator-v1.py status
            ├─ goal1_auto_run_payload (subprocess broker poll)
            └─ 40+ payload module calls (loop, council, scoreboard, …)
  └─ sync_sa_queue_into_payload
  └─ _apply_factory_freeze_from_lib → imports build-sina-command-panel
  └─ write_panel_outputs
       ├─ build_shell_payload
       ├─ _write_text_atomic × 2
       ├─ verify_command_data_atomic
       ├─ heal_command_data_shell_from_disk (on failure)
       └─ subprocess validate-hub-p0-no-autorun-v1.sh
```

---

## Circular / recursive risk paths

| Path | Risk |
|------|------|
| `update-program-progress` inside refresh pipeline | Was nesting bowl→panel; mitigated by `SINA_SKIP_NESTED_BOWL` |
| `build-sina-daily-bowl` | Was nesting panel build; mitigated by `SINA_SKIP_PANEL_BUILD` |
| `GET /command-data.json` on cache miss during mutation | Re-entrant `build_payload` under lock — serializes via `_HUB_LOCK` |
| E2E `POST /refresh` during concurrent audits | **SIGKILL / lock contention** — E2E now cancelled |

---

## Expensive paths ranked

1. **POST /refresh** — T3, ~230s documented (sa-0217)
2. **Any POST with `hub_after_mutation(run_refresh_scripts=True)`** — T3
3. **Cold start `hub_after_mutation(write_html=True)`** — T2+HTML
4. **GET /api/hub-sync** — T1 but still full `build_payload` in request thread
5. **POST /api/intelligence-circle chat (L2)** — T2 (was T2+15s before L0 fix)
6. **Strict `build-sina-command-panel.py`** — T2 + 40 validators, minutes
