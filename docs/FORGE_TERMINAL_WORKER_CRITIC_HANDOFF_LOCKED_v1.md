# Forge Terminal — Worker + Critic Handoff (LOCKED v1)

**Saved:** 2026-06-25T03:49:22Z  
**Version:** 1.0 — LOCKED  
**App version:** Forge Terminal **4.0.0-alpha** · port **13029**  
**Authority:** `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md`  
**Parent:** Forge stack product layer · Chat Unify integration · desktop mesh

---

## One law

> **Forge Terminal (`:13029`) is the founder's daily build desk. Chat Unify (`:13023`) is the parallel platform shell. They share one Python engine — two servers, one prompt-forge pipeline, wired by desktop mesh.**

---

## 1) Main app: Forge Terminal or Chat Unify?

| | **Forge Terminal** `:13029` | **Chat Unify** `:13023` |
|---|---|---|
| **Role** | **Product** — idea → forge → decide → execute | **Platform** — 10 machines, paste/save, integrations |
| **UI** | `apps/forge-terminal-v1/` (v4.0.0-alpha IDE) | `scripts/chat-unify-standalone/` (v4.6.4) |
| **Shell** | `apps/forge-terminal-connect-v1/` | Chat Unify own tab shell |
| **Completeness** | **More complete for building** (swarm, governance, quality, civilization v4–v8) | **More complete for multi-machine tabs** (platform home, ORD atoms, live HTTP verify) |
| **API** | `POST /api/forge-terminal/v1` | `POST /api/chat-unify` |

**Founder default URL:** `http://127.0.0.1:13029/` → **Forge IDE** tab.

**Alternate Forge IDE entry:** `http://127.0.0.1:13023/terminal/` (same live UI when `FORGE_TERMINAL_USE_LIVE_UI=1`).

### Independent or integrated?

**Both — two servers, one engine.**

```
Founder UI
  Forge Terminal Connect :13029  ──┐
  Chat Unify standalone  :13023  ──┼──► forge_terminal_v1.handle_post
                                   │
Shared engine                    │
  chat_unify_prompt_forge_v1 ◄───┘
  chat_founder_language_v1
  model_dispatch
  forge_terminal_desktop_mesh_v1  ── probes + peer_dispatch both ports
```

- **Independent:** separate processes, ports, UIs. Either can run alone.
- **Integrated:** same Python modules; desktop mesh probes both; Forge Connect embeds Chat Unify machines (`chat_unify_machines` feature in connect server).
- **Product north star:** founder lives on **Forge Terminal** for chat, advisor, quality gate, decision card, Cursor/Cloud execute.

---

## 2) Worker handoff (paste into Worker chat)

```
WORK: forge-terminal-v4 — maintain + extend only (no new kernel)

GATE:
  cd ~/Desktop/SourceA && python3 scripts/cursor_entry_gate.py --role worker
  python3 scripts/cursor_agent_self_audit.py session-start

NORTH STAR:
  Autorun alive · Forge Terminal product layer works · Chat Unify prompt forge on every chat send.
  Mac = control plane only. Heavy body → cloud (:13027 / Railway). dry_run=true on Mac.

MAIN APP (founder opens this):
  http://127.0.0.1:13029/          ← Forge Terminal Connect shell
  Tab: Forge IDE                   ← apps/forge-terminal-v1/ (4.0.0-alpha)

SECONDARY (platform / machines):
  http://127.0.0.1:13023/          ← Chat Unify standalone
  http://127.0.0.1:13023/terminal/ ← same Forge IDE (alternate entry)

READ FIRST (in order):
  1. brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md
  2. docs/FORGE_TERMINAL_WORKER_CRITIC_HANDOFF_LOCKED_v1.md (this file)
  3. .cursor/skills/forge-living-ui-modern-ide/SKILL.md
  4. .cursor/skills/hub-pro-hub-hero/SKILL.md
  5. .cursor/skills/hub-pro-cloud-api/SKILL.md
  6. ~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md

KEY PATHS:
  UI:        apps/forge-terminal-v1/{index.html, terminal.js, terminal.css}
  Connect:   apps/forge-terminal-connect-v1/
  API:       scripts/forge_terminal_v1.py
  Server:    scripts/forge_terminal_connect_server_v1.py  (:13029)
  Chat Srv:  scripts/chat-unify-server.py               (:13023)
  Mesh:      scripts/forge_terminal_desktop_mesh_v1.py
  Prompt:    scripts/chat_unify_prompt_forge_v1.py
  E2E:       scripts/forge_terminal_living_ui_e2e_verify_v1.py

RECENT REGRESSIONS FIXED (do not reintroduce):
  ✗ reloadUI() must use UI_VERSION "4.0.0-alpha" — NOT "3.0.0"
  ✗ chat_turn must default fast=false — runs chat_unify_prompt_forge_v1 before LLM
  ✗ Default mode = Chat (not Advisor) for living chat
  ✗ Connect tab needs Chat Unify open/ping — not dead btn-mesh-* IDs

CHAT PIPELINE (must stay wired):
  chat_turn → run_terminal(fast=false) → chat_unify_prompt_forge_v1
           → model_dispatch / LLM → founder_language → quality_gate
           → display_response → terminal.js renderFounderSections()

FORGE MODES (terminal.js):
  chat      → chat_turn (prompt forge + LLM + quality gate)
  advisor   → advisor_run (swarm orchestrator)
  selfheal  → agent_self_improve (L2 patch loop)

API QUICK REF (POST :13029/api/forge-terminal/v1):
  {"action":"chat_turn","text":"...","fast":false,"full_llm":true}
  {"action":"advisor_run","goal":"...","swarm":true,"dry_run":true}
  {"action":"desktop_mesh_status"}
  {"action":"peer_dispatch","peer":"chat_unify","dry_run":true}
  {"action":"agent_swarm_run","goal":"...","dry_run":true}

PROOF (one light check, Mac OK):
  python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
  Target: 167/167 · receipt ~/.sina/forge-terminal-living-ui-e2e-v1.json

FORBIDDEN:
  - New kernel / orchestrator / memory system
  - Validator marathons on Mac (INCIDENT-039)
  - fast:true on chat_turn by default (skips Chat Unify)
  - Downgrading UI version strings
  - Mac factory body (route to cloud)

CLOUD DISPATCH:
  Hub POST /api/cloud-forge-run/proceed/v1 OR :13027 cloud workers
  NOT fbe_motor_delegate on Mac
```

---

## 3) Port map

| Port | Service | URL |
|------|---------|-----|
| 13029 | Forge Terminal Connect + IDE | `http://127.0.0.1:13029/` |
| 13029 | Forge API | `http://127.0.0.1:13029/api/forge-terminal/v1` |
| 13029 | Health + local token | `http://127.0.0.1:13029/health` |
| 13023 | Chat Unify standalone | `http://127.0.0.1:13023/` |
| 13027 | Cloud Workers | `http://127.0.0.1:13027/api/cloud-workers/v1` |
| 13020 | Hub (legacy glance) | `http://127.0.0.1:13020/` |

---

## 4) System layers (knowledge map)

```
Founder UI (:13029)
  apps/forge-terminal-v1/          terminal.js · index.html · terminal.css
  apps/forge-terminal-connect-v1/  Connect shell · forge-quality-bridge.js

API Gateway
  scripts/forge_terminal_connect_server_v1.py   UI_VERSION 4.0.0-alpha
  POST /api/forge-terminal/v1                   → forge_terminal_v1.handle_post

Worker / Agent execution
  scripts/forge_agent_kernel_v1.py              L1 + L2
  scripts/forge_agent_kernel_v3_swarm.py        v3 parallel swarm
  scripts/forge_advisor_orchestrator_v1.py      Advisor mode

Swarm orchestration
  scripts/forge_swarm_blackboard_v1.py
  scripts/forge_execution_mesh_v1.py
  scripts/forge_swarm_cloud_dispatch_v1.py

Memory + civilization
  scripts/forge_civilization_memory_v1.py
  scripts/forge_agent_registry_v1.py
  scripts/forge_civilization_loop_v1.py

Repo intelligence
  scripts/forge_repo_intel_v1.py

Cloud execution body (not Mac)
  scripts/cloud_workers_hub_v1.py               :13027
  scripts/cloud_auto_runtime_v1.py
  Railway FBE via fbe.lib.hub_cloud_proxy_v1
```

---

## 5) Chat pipeline (living UI — do not break)

```
chat_turn → run_terminal → translate_for_founder(prefer_ai=True)
         → response_for_display() → API display_response + response
         → terminal.js renderFounderSections() → appendChatBubble
         → quality_gate in thread meta (persist on reload)
```

| Layer | File | Rule |
|-------|------|------|
| Prompt forge | `scripts/chat_unify_prompt_forge_v1.py` | lint → extract → compile → emit |
| Translate | `scripts/chat_founder_language_v1.py` | AI first; rules fallback only |
| Display | `scripts/forge_quality_gate_v1.py` `response_for_display()` | Never show raw JSON |
| API | `scripts/forge_terminal_v1.py` | Return `display_response` + `quality_gate` |
| Thread | `forge_terminal_desktop_mesh_v1.py` `append_turn` | Meta includes `quality_gate` |
| Render | `apps/forge-terminal-v1/terminal.js` | `renderFounderSections` + `.forge-markdown` |

**`chat_turn` contract:** `fast` defaults **false** in API and UI — prompt forge runs before LLM. E2E explicitly tests both `fast:true` (smoke) and `fast:false` (prompt forge path).

---

## 6) Desktop mesh

**Module:** `scripts/forge_terminal_desktop_mesh_v1.py`  
**Receipt:** `~/.sina/forge-terminal-desktop-mesh-v1.json`  
**Thread store:** `~/.sina/forge-terminal-chat-thread-v1.json`

Peers probed:

| Peer | Port | Role |
|------|------|------|
| `chat_unify` | 13023 | Prompt forge platform · founder loop |
| `cloud_workers` | 13027 | Cloud forge run body |
| `hub` | 13020 | Legacy glance |
| `forge_terminal` | 13029 | Self |

**UI wiring:** sidebar mesh list + Connect tab open/ping buttons. Pills `pill-chat-unify` and `pill-cloud` open peer URLs.

---

## 7) Critic handoff

Critics are **not a separate app** — they are agents + verification layers inside Forge.

### 7.1 Critic agents (registry)

| ID | Focus |
|----|--------|
| `critic-001` | review, quality |
| `critic-002` | security |
| `critic-003` | tests |

**Registry:** `scripts/forge_agent_registry_v1.py` → `~/.sina/forge-agent-registry-v1.json`

### 7.2 Where critics run

```
Advisor/Swarm run
  → parallel builders (execution mesh)
  → parallel critics (_parallel_critics, count=3)
  → aggregate_critic_verdicts()
  → repair agent if fail
  → verify harness + quality gate
  → record_run() + reputation update
```

| Layer | Module | What critics check |
|-------|--------|-------------------|
| Swarm critics | `forge_agent_kernel_v3_swarm.py` | Blackboard snapshot, goal alignment, patch quality |
| Quality gate | `forge_quality_gate_v1.py` | 11 layers — blocks Execute unless PASS |
| Static harness | `run_verify_harness_static()` in kernel | Syntax/structure checks |
| Critic suite | `forge_terminal_critic_verify_v1.py` | 5-check HTTP suite against live `:13029` |
| Governance | `forge_governance_kernel_v1.py` | ALLOW/DENY before tool actions |

### 7.3 Critic law

> **No change is valid unless critic aggregate approved + harness ok + quality gate PASS for execute paths.**

### 7.4 Critic boot read order

1. `brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_AGENT_OPERATING_MANUAL_LOCKED_v1.md` §9–10
2. `scripts/forge_agent_kernel_v3_swarm.py` — `_critic_swarm`, `_parallel_critics`, `aggregate_critic_verdicts`
3. `scripts/forge_quality_gate_v1.py`
4. `scripts/forge_terminal_critic_verify_v1.py`
5. Blackboard: `~/.sina/forge-swarm-blackboard-v1.json` → `critic_verdicts[]`
6. Memory: `~/.sina/forge-civilization-memory-v1.json` → `failure_patterns[]`

### 7.5 Critic verify commands

```bash
# Server must be on :13029
python3 scripts/forge_terminal_critic_verify_v1.py

# Living UI E2E (disk + CLI + optional HTTP)
cd ~/Desktop/SourceA
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
# Receipt: ~/.sina/forge-terminal-living-ui-e2e-v1.json
```

### 7.6 What critics should flag (known regression patterns)

| Issue | Critic check |
|-------|----------------|
| UI version downgrade (`ui=3.0.0` reload) | E2E `ui reload version` |
| Chat Unify bypass (`fast:true` on chat_turn default) | E2E `chat_turn prompt forge` |
| Dead mesh buttons (JS refs missing from HTML) | Connect panel must have working open/ping |
| Raw JSON in founder chat | E2E `display not json blob` |
| Execute without quality PASS | Quality gate `execution_allowed: false` |

### 7.7 Critic vs Worker split

| Role | Job |
|------|-----|
| **Worker** | Implement in bounded paths · wire UI · keep E2E green |
| **Critic** | Review diff · run critic verify + living UI E2E · block ship if swarm critics or quality gate fail |

---

## 8) Skills index (Forge-specific)

| Skill | Path |
|-------|------|
| Forge Living UI / Modern IDE | `.cursor/skills/forge-living-ui-modern-ide/SKILL.md` |
| Forge factory directory map | `.cursor/skills/forge-living-ui-modern-ide/FORGE_FACTORY_DIRECTORY.md` |
| Hub Pro cloud API | `.cursor/skills/hub-pro-cloud-api/SKILL.md` |
| Hub Pro master | `.cursor/skills/hub-pro-master/SKILL.md` |
| Hub Pro app E2E | `.cursor/skills/hub-pro-app-e2e/SKILL.md` |
| Hub Pro hub hero | `.cursor/skills/hub-pro-hub-hero/SKILL.md` |

---

## 9) Mac founder session rules

- `dry_run=true` default for swarm / cloud dispatch on Mac
- **One** light E2E ≤90s OK; no validator marathons (INCIDENT-039)
- Proof = read receipts (`~/.sina/*-receipt*.json`), not bash chains
- Factory mode **FREEZE** — route ACT/implement to cloud workers

---

## 10) One-sentence summary

**Forge Terminal (`:13029`) is main and more complete for daily build work; Chat Unify (`:13023`) is the parallel platform shell — they share the same prompt-forge/founder-language engine and are wired via desktop mesh, but Forge Terminal is where the founder lives, decides, and executes.**

---

## 11) Public demo (sourcea.app)

| Resource | URL |
|----------|-----|
| Live demo | `https://sourcea.app/sourcea/forge/terminal` |
| Short alias | `https://sourcea.app/forge/terminal` → 302 canonical |
| Demo JS | `SourceA-landing/green-unified/sourcea-forge-terminal-demo.js` (v1.1.0) |
| Demo HTML | `SourceA-landing/green-unified/forge/terminal.html` |
| Brain worker | `cloud/workers/sourcea-brain-chat-v1` — `product: "forge_terminal"` |
| Config | `SourceA-landing/green-unified/data/sourcea-brain-chat-config-v1.json` |

**E2E (Mac OK):**

```bash
bash scripts/validate-forge-terminal-public-demo-v1.sh          # disk + worker + URL smoke
bash scripts/validate-forge-terminal-public-demo-e2e-v1.sh    # + Playwright live chat
```

Receipt: `~/.sina/forge-terminal-public-demo-e2e-v1.json`

**Deploy chain:** `python3 scripts/build_sourcea_vercel_output_v1.py` → landing publish · `wrangler deploy` in `cloud/workers/sourcea-brain-chat-v1/` for forge founder-language system prompt.
