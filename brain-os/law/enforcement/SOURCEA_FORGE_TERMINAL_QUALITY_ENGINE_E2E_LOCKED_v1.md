# SourceA Forge Terminal Quality Engine E2E (LOCKED v1)

**Saved:** 2026-06-25T12:00:00Z  
**Version:** 1.0 — LOCKED  
**App version:** 2.7.0 · Quality Engine **1.1** · port **13029**  
**Parent:** `SOURCEA_FORGE_TERMINAL_DESKTOP_E2E_LOCKED_v1.md` · `SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md`

---

## One law

> **Quality Engine ships only when `scripts/validate-forge-terminal-quality-desktop-e2e-v1.sh` exits 0 and receipt `~/.sina/forge-terminal-quality-desktop-e2e-v1.json` is fresh.**

---

## 10-step Quality Engine checklist (enforceable)

| Step | Requirement | Proof |
|------|-------------|-------|
| 1 | Layer contract lock — `QUALITY_ENGINE_VERSION=1.1`, frozen `LAYER_ORDER` (11 layers), receipt schema | `scripts/forge_quality_gate_unit_v1.py` |
| 2 | Dedicated Quality desktop orchestrator + registry bundle `forge_terminal_quality_desktop` | `validate-forge-terminal-quality-desktop-e2e-v1.sh` |
| 3 | Founder-language gate — reject JSON blobs; auto-reformat in backend + UI | `founder_language` layer + `terminal.js` display |
| 4 | Auth + iframe — `X-Forge-Token`, `GET ?auth=1`, postMessage bridge, 401 retry | UI E2E auth negative + GET |
| 5 | Living chat UX — inline quality chip, exec button sync, eval shadow badge | `terminal.css` + chat thread |
| 6 | Eval shadow critic — stable schema, SKIP when no eval key, telemetry on run | quality E2E eval shadow check |
| 7 | `quality_rerun` + REVISE loop — no-LLM rerun (`full_llm=false`), deterministic matrix | `forge_terminal_quality_matrix_v1.py` |
| 8 | Full execution block matrix — cloud/cursor/execute/rerun/missing-gate | `~/.sina/forge-terminal-quality-matrix-v1.json` |
| 9 | Connect shell parity — Verify tab reads quality receipts from `run_id` | `forge-quality-bridge.js` |
| 10 | Governance lock + v2.7.0 ship window — this law + desktop orchestrator fail-fast | Both receipts fresh |

---

## Layer verdict rules (v1.1)

- **CRITICAL_LAYERS fail** → `REJECT`
- **passed_layers ≥ 9** → `PASS` (`execution_allowed=true`)
- **passed_layers ≥ 7** → `REVISE`
- else → `REJECT`
- **eval_shadow** is advisory only — never blocks execution

---

## Founder one-tap verify

```bash
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-quality-desktop-e2e-v1.sh && \
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-desktop-e2e-v1.sh && \
open ~/Desktop/Forge\ Terminal.app
```

---

## Receipt chain

| Receipt | Path |
|---------|------|
| Per-run quality gate | `~/.sina/forge-terminal-quality/<run_id>.json` |
| Quality desktop E2E | `~/.sina/forge-terminal-quality-desktop-e2e-v1.json` |
| Quality matrix | `~/.sina/forge-terminal-quality-matrix-v1.json` |
| Full desktop E2E | `~/.sina/forge-terminal-desktop-e2e-v1.json` |

---

## Incident template

File incidents as `SINA_FORGE_TERMINAL_QUALITY_ENGINE_<TOPIC>_INCIDENT_NNN_LOCKED_v1.md` and register in `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.
