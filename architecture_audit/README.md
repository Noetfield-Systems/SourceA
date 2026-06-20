# SourceA Agentic OS Control Panel Hub — Architecture Audit

**Mode:** Investigation only (read-only extraction)  
**Date:** 2026-06-10  
**Repo root:** `/Users/sinakazemnezhad/Desktop/SourceA`  
**Production hub:** `http://127.0.0.1:13020` (`scripts/sina-command-server.py`)

## Deliverables

| # | File | Contents |
|---|------|----------|
| 1 | [ARCHITECTURE_ENTRYPOINTS.md](./ARCHITECTURE_ENTRYPOINTS.md) | All startup paths, servers, builders, scripts |
| 2 | [CALL_GRAPH.md](./CALL_GRAPH.md) | Request → handler → build → disk call chains |
| 3 | [STATE_MAP.md](./STATE_MAP.md) | SSOT, cache, disk, runtime state ownership |
| 4 | [API_MAP.md](./API_MAP.md) | Full HTTP surface (~100 GET, ~50 POST) |
| 5 | [PANEL_BUILD_MAP.md](./PANEL_BUILD_MAP.md) | `build_payload`, shell, refresh pipeline |
| 6 | [REBUILD_TRIGGER_MAP.md](./REBUILD_TRIGGER_MAP.md) | Every `hub_after_mutation` / rebuild caller |
| 7 | [ACTION_TRACE.md](./ACTION_TRACE.md) | Button-click traces + sequence diagrams |
| 8 | [HOTSPOTS.md](./HOTSPOTS.md) | Performance offenders ranked |
| 9 | [DEPENDENCY_GRAPH.md](./DEPENDENCY_GRAPH.md) | Mermaid dependency graph |
| 10 | [REBUILD_READINESS_SCORE.md](./REBUILD_READINESS_SCORE.md) | Scores + rebuild feasibility |
| — | [DEPENDENCY_GRAPH.mmd](./DEPENDENCY_GRAPH.mmd) | Mermaid source |
| — | [DEPENDENCY_GRAPH.svg](./DEPENDENCY_GRAPH.svg) | Rendered dependency graph |
| — | [DEPENDENCY_GRAPH.png](./DEPENDENCY_GRAPH.png) | Rendered dependency graph (PNG) |

## Diagram export (SVG / PNG)

Pre-rendered: `DEPENDENCY_GRAPH.svg`, `DEPENDENCY_GRAPH.png`

Regenerate:

```bash
PUPPETEER_EXECUTABLE_PATH="$HOME/.cache/puppeteer/chrome-headless-shell/mac_arm-*/chrome-headless-shell-mac-arm64/chrome-headless-shell" \
  npx -y @mermaid-js/mermaid-cli -i architecture_audit/DEPENDENCY_GRAPH.mmd -o architecture_audit/DEPENDENCY_GRAPH.svg
```

## Key finding (one line)

The hub is a **monolithic in-process JSON projector**: almost every founder mutation calls `hub_after_mutation()` → full `build_payload(force=True)` → atomic write of ~2.7MB `command-data.json` + shell — while the UI already supports shell-first lazy load and per-tab `/api/*` fetches.

## E2E status (founder cancel 2026-06-10)

Backend HTTP E2E (`audit_backend_e2e.py`) is **cancelled** from `find_critical_bugs` CRITICAL chain. See `SINA_HUB_E2E_CANCELLED_LOCKED_v1.md`.
