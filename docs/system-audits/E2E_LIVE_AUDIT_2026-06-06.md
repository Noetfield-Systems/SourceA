# E2E live audit — validators, hub, APIs

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  
**Session:** Full E2E check + founder support pack verification  

---

## Environment

| Item | Value |
|------|-------|
| Hub | `http://127.0.0.1:13020` |
| Pick script | `bash scripts/plan-no-asf-run.sh pick 1` |
| PRIORITY | `os/plan-library/SOURCEA-PRIORITY.md` |
| REGISTRY | `os/plan-library/sourcea-1000/REGISTRY.json` |

---

## Validator results (hub UP)

| Command / check | Result | Notes |
|-----------------|--------|-------|
| `find_critical_bugs.py` | **0 critical** | Includes governance fleet + founder-docs CRITICAL |
| Strict build | **PASS** | |
| `validate-sourcea-1000-pack.sh` | **PASS** | 1000 tasks |
| `validate-founder-docs-no-terminal-v1.sh` | **PASS** | T0+T1 F1/F2 |

---

## Hub lifecycle finding

**Issue:** Stale `sina-command-server.py` process caused autonomy API **404**.  
**Fix:** Hub restart.  
**After restart:** `prompt_router` and execution-kernel API routes responded OK.

**Operational note:** Always confirm hub PID fresh after code changes to autonomy routes.

---

## Live pick chain

| Timestamp phase | Pick |
|-----------------|------|
| Early session | sa-0115 → sa-0118 |
| Post closeouts | **sa-0202** |
| Phase label | s2 hub-build-ci |

Queue advanced past sa-0118–sa-0201 per do_not_redo / PRIORITY evidence.

---

## Autonomy API spot checks

| Endpoint / CLI | Status | Issue |
|----------------|--------|-------|
| `prompt_router.py` CLI | OK | Shipped |
| Hub prompt_router API | OK | After restart |
| `execution-kernel-v1` API | **FAIL** | Passes `--json` to v0 which rejects flag |
| Kernel state | Active task sa-0202 | Can block new tick |

---

## Gates (honest)

```yaml
dispatch_ready: false
eval_1b_gate_ok: false
eval_1b_mode: structural_only
eval_1b_blocker: OpenRouter 402 Payment Required
```

Scaffold Eval-1b: **7/7 100%** — live blocked on credits.

---

## Hub UI gaps

| Feature | Status |
|---------|--------|
| Strategic synthesis | Present |
| Gates display | Honest (M2) |
| sa-queue tab | **NOT IMPLEMENTED** |
| Private agents (8) | Registry present |

---

## Runtime optional path

| Service | Port | Status |
|---------|------|--------|
| Runtime spine | :8000 | **DOWN** at audit |
| Impact | Optional for SourceA E2E | Hub path sufficient for control plane |

---

## ARCHITECT / ingest

- **ARCHITECT_REPORT:** 5 rejected YAML ingests noted during session  
- Action: P2 cleanup — not blocking 0 critical

---

## Founder support E2E

| Path | Works |
|------|-------|
| Hub Refresh | Yes |
| Actions (no Terminal) | Yes — law aligned post T0+T1 |
| `plan-no-asf-run.sh pick` | Yes — sa-0202 |
| Brain pack sync | `~/.sina/brain/` 6 files |
| SinaaiDataBase chat | Archive only — correct |

---

## E2E verdict

**PASS** for controlled control-plane E2E when hub is fresh: 0 critical, strict build, pack valid, honest gates.  
**FAIL/PARTIAL** for live autonomy dispatch and Eval-1b live — expected under honest gates.

**Immediate fixes:** execution-kernel `--json`; hub sa-queue tab; M4 block hook.
