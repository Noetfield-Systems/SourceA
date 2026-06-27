# SourceA Forge Terminal Living Desktop E2E (LOCKED v1)

**Saved:** 2026-06-25T18:00:00Z  
**Version:** 1.0 — LOCKED  
**App version:** 2.8.0 · port **13029**  
**Parent:** `SOURCEA_FORGE_TERMINAL_DESKTOP_E2E_LOCKED_v1.md` · `SOURCEA_FORGE_TERMINAL_QUALITY_ENGINE_E2E_LOCKED_v1.md`

---

## One law

> **Living Desktop ships only when `scripts/validate-forge-terminal-living-desktop-e2e-v1.sh` exits 0 and receipt `~/.sina/forge-terminal-living-desktop-e2e-v1.json` is fresh.**

---

## 10-step Living Desktop checklist (enforceable)

| Step | Requirement | Proof |
|------|-------------|-------|
| 1 | Living reply contract — `display_response`, `prefer_ai=True`, JSON → prose | `scripts/forge_terminal_reply_contract_v1.py` |
| 2 | Living chat layout — no 42vh cap, founder-section CSS, forge-markdown | living UI E2E CSS contract |
| 3 | Resizable workbench — dock + sidebar drag, embed mode | `terminal.js` + `#dock-resize` / `#sidebar-resize` |
| 4 | Connect shell parity — `forge-ide` tab, full iframe, sync to chat-unify-standalone | `sync-forge-connect-to-chat-unify-v1.sh` |
| 5 | Thread persistence — `quality_gate` in chat meta, chip reload | living UI E2E `chat_thread` check |
| 6 | Bundle integrity — cold-start fail-fast, living assets in bundle | `build-forge-terminal-standalone-app-v1.sh` |
| 7 | Orchestrator dedupe — quality once, living gate in desktop E2E | `validate-forge-terminal-desktop-e2e-v1.sh` |
| 8 | Auth + mesh + offline — token, mesh peers, status_light, offline banner | living UI E2E |
| 9 | Dedicated living orchestrator + registry `forge_terminal_living_desktop` | This law + overrides JSON |
| 10 | Governance v2.8 ship window — version parity server/UI/bundle | All receipts fresh |

---

## Founder one-tap verify

```bash
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-quality-desktop-e2e-v1.sh && \
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-living-desktop-e2e-v1.sh && \
bash ~/Desktop/SourceA/scripts/validate-forge-terminal-desktop-e2e-v1.sh && \
bash ~/Desktop/SourceA/scripts/build-forge-terminal-standalone-app-v1.sh && \
open ~/Desktop/Forge\ Terminal.app
```

---

## Receipt chain

| Receipt | Path |
|---------|------|
| Living UI E2E | `~/.sina/forge-terminal-living-ui-e2e-v1.json` |
| Living desktop orchestrator | `~/.sina/forge-terminal-living-desktop-e2e-v1.json` |
| Full desktop E2E | `~/.sina/forge-terminal-desktop-e2e-v1.json` |

---

## Incident template

File incidents as `SINA_FORGE_TERMINAL_LIVING_DESKTOP_<TOPIC>_INCIDENT_NNN_LOCKED_v1.md` and register in `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.
