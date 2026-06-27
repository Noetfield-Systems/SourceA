# SourceA Forge Terminal Desktop E2E (LOCKED v1)

**Saved:** 2026-06-25T18:00:00Z  
**Version:** 1.1 — LOCKED  
**App version:** 2.8.0 · port **13029**  
**Parent:** `SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md`

---

## One law

> **Forge Terminal desktop ships only when `scripts/validate-forge-terminal-desktop-e2e-v1.sh` exits 0 and receipt `~/.sina/forge-terminal-desktop-e2e-v1.json` is fresh.**

---

## 10-step hardening checklist (enforceable)

| Step | Requirement | Proof |
|------|-------------|-------|
| 1 | Standalone bundle includes quality + living scripts + post-build import smoke | Build script cold-start PASS (fail-fast) |
| 2 | Unified orchestrator: quality_desktop → living_desktop → main → critic → UI → matrix | `validate-forge-terminal-desktop-e2e-v1.sh` |
| 3 | UI contract: quality panel, exec buttons, auth token, living layout | `forge_terminal_ui_e2e_verify_v1.py` |
| 4 | Swift shell: single-instance, safe port recycle, retry UI | `ForgeTerminalShell.swift` + launch log |
| 5 | Localhost bind + `X-Forge-Token` on POST | `forge_terminal_local_auth_v1.py` |
| 6 | Living product loop: founder prose, resizable panels, Connect iframe | `SOURCEA_FORGE_TERMINAL_LIVING_DESKTOP_E2E_LOCKED_v1.md` |
| 7 | Quality Engine 11 layers + `quality_rerun` + eval shadow (advisory) | `SOURCEA_FORGE_TERMINAL_QUALITY_ENGINE_E2E_LOCKED_v1.md` |
| 8 | Execution matrix: reject/revise/quality/cursor/telemetry | `forge_terminal_execution_matrix_v1.py` |
| 9 | Offline banner + mesh status_light parity | Living UI E2E + UI |
| 10 | Registry bundles + weekly receipts | `forge_terminal_desktop` + overrides JSON |

---

## Founder one-tap verify

```bash
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-quality-desktop-e2e-v1.sh && \
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-living-desktop-e2e-v1.sh && \
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-desktop-e2e-v1.sh && \
open ~/Desktop/Forge\ Terminal.app
```

---

## Port routing

| Surface | Port | Use |
|---------|------|-----|
| Mac `.app` UI + API | **13029** | Desktop E2E target |
| Chat Unify / mobile | **13023** | Synced connect UI via `sync-forge-connect-to-chat-unify-v1.sh` |

---

## Incident template

File incidents as `SINA_FORGE_TERMINAL_<TOPIC>_INCIDENT_NNN_LOCKED_v1.md` and register in `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

---

## App Store track (document only)

Python-not-embedded — embed via briefcase/py2app before App Store submission.
