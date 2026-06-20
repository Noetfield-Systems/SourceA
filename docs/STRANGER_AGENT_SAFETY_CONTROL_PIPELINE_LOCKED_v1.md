# Stranger Agent Safety Control + Identifier Pipeline (SASCIP) — LOCKED v1.2

**Version:** 1.2.0 · **Saved:** 2026-06-16T05:47:17Z · **Upgraded:** 2026-06-16  
**Path:** `~/Desktop/SourceA/docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md`  
**Orchestrator:** `scripts/stranger_agent_safety_pipeline_v1.py`  
**Lib:** `scripts/stranger_agent_safety_lib_v1.py`  
**Validator:** `scripts/validate-stranger-agent-safety-v1.sh`  
**Receipt:** `~/.sina/stranger-agent-admission-receipt-v1.json` (schema `stranger-agent-admission-v1.2`)  
**Monitor:** `~/.sina/stranger-agent-monitor-v1.json` (hub + Mac Health tile)  
**Registry:** `~/.sina/stranger-agent-registry-v1.json`  
**Watch receipt:** `~/.sina/stranger-agent-watch-receipt-v1.json`  
**Config:** `~/.sina/config/stranger-agent-safety-v1.json` (seed: `config/stranger-agent-safety-v1.default.json`)  
**Partner tokens:** `~/.sina/config/stranger-agent-external-tokens-v1.json` (seed: `config/stranger-agent-external-tokens-v1.default.json`)

**Related:** `SOURCEA_STRANGER_AGENT_DEFENSE_IN_DEPTH_FOUNDER_GUIDE_LOCKED_v1.md` · `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` · `AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md` · `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md` · `SOURCEA_ORCHESTRATOR_PARTNER_INTEGRATION_LOCKED_v1.md` · Mac Health (`mac_health_live_v1.py`)

---

## 0. One sentence

> **Every agent arriving on Mac Pro gets fingerprinted (workspace + MCP + git + fleet chat), risk-scored, trust-tiered, and receipted — strangers quarantine on write; monitor tile surfaces live posture on Mac Health Heart.**

---

## 1. Why (2026–2027 Mac Pro fleet)

| Risk | SASCIP v1.2 response |
|------|----------------------|
| Unregistered Cursor chat edits SourceA law | Cross-lane resolve + risk score + quarantine |
| Unknown MCP servers on stranger session | MCP fingerprint in IDENTIFY; unknown → risk bump |
| Portfolio agent opens wrong repo | Workspace + fleet chat hash match |
| Mac emergency + unknown python agents | T6 hostile + Mac Health `stranger_agent` block |
| External orchestrator (Temporal/LangGraph) | `--external-orchestrator` + token file admission |
| Chat memory ≠ disk SSOT | Admission + monitor + watch receipts logged |

---

## 2. Pipeline stages

```text
IDENTIFY → CLASSIFY → CONTROL → PROVE → SERVE
```

| Stage | v1.2 additions |
|-------|----------------|
| **IDENTIFY** | MCP servers, git branch/dirty, fleet chat hash, transcript hint, Playwright hog signal |
| **CLASSIFY** | Risk score 0–100, fleet chat promotion, critical risk → T6 |
| **CONTROL** | Bulk-edit intent block, high-risk MCP warnings |
| **PROVE** | Registry stats (`admit_count`, `first_seen`), governance spine |
| **SERVE** | `stranger-agent-monitor-v1.json` → live surfaces `sascip_line` + Mac Health tile |

---

## 3. Trust tiers (unchanged semantics)

| Tier | Who | Default policy |
|------|-----|----------------|
| **T0** founder_elevated | `EDIT ALLOWED` / `WORK:` / `SAVE TO:` | Full lane per explicit order |
| **T1** fleet_L1 | brain, governance, commercial, brief | `sourcea_execution_core` |
| **T2** fleet_L2 | worker, researcher, maintainer | `sourcea_worker` / `research_acquisitor` |
| **T3** portfolio | trustfield, virlux, noetfield_*, seven77 | Portfolio workspace match |
| **T4** registered_lane | Known lanes + SourceA cursor alias | Prefix allowlist writes |
| **T5** stranger_quarantine | No match | Block writes until promotion |
| **T6** hostile_block | T5 + Mac emergency or risk ≥ 85 | Block + factory freeze recommend |

---

## 4. Identifier fingerprint fields (v1.2)

| Field | Source |
|-------|--------|
| `mcp` | `~/.cursor/projects/*/mcps/*/SERVER_METADATA.json` |
| `git` | branch + dirty file count |
| `fleet_chat_match` | L1/L2 chat hash from agentic stack |
| `transcript` | latest agent-transcript id + age |
| `process_signals.playwright_zombies` | high-CPU Playwright/Chromium |
| `risk` | composite score + level + factors |

---

## 5. Risk score

| Level | Score | Typical cause |
|-------|-------|---------------|
| minimal | 0–24 | T0/T1 fleet + fresh session gate |
| low | 25–44 | T2/T4 registered |
| medium | 45–64 | stale gate or unknown MCP |
| high | 65–84 | stranger + process noise |
| critical | ≥ 85 | hostile threshold → T6 eligible |

Config: `risk_score_hostile_threshold` (default 85)

---

## 6. Integration surfaces

| Surface | Hook |
|---------|------|
| Session gate | step `stranger_agent_safety` + risk_score |
| Cross-lane guard | `resolve_cross_lane_agent()` + risk in block meta |
| Disk live wire | `sascip_line` on `agent-live-surfaces-v1.json` |
| Mac Health Heart | `stranger_agent` block on live pulse (`:13024`) |
| Governance spine | `STRANGER_AGENT_ADMISSION` → hub · monitor · mac_health |
| Partner orchestrators | `--external-orchestrator` + `--external-token` |

### CLI

```bash
# Full admission (every session)
python3 scripts/stranger_agent_safety_pipeline_v1.py --role worker --agent cursor --json

# Continuous watch pulse (re-classify recent fingerprints)
python3 scripts/stranger_agent_safety_pipeline_v1.py --watch --json

# Partner external admit
python3 scripts/stranger_agent_safety_pipeline_v1.py \
  --external-orchestrator temporal_partner \
  --external-token "$TOKEN" \
  --agent sourcea_worker --json

# Validator
bash scripts/validate-stranger-agent-safety-v1.sh
```

---

## 7. Monitor tile (v1.1 delivered in v1.2)

`~/.sina/stranger-agent-monitor-v1.json`:

- `one_line` — quoted in live surfaces + Mac Health
- `hub_tile` — title, badge (ADMIT/QUARANTINE), subtitle, url
- `stranger_active_count`, `hostile_count`, `risk_score`

---

## 8. Roadmap status

| Phase | Status |
|-------|--------|
| **v1.0** | ✅ IDENTIFY→SERVE, session gate, cross-lane, validator |
| **v1.1** | ✅ Monitor projection + hub tile + live surfaces wire |
| **v1.2** | ✅ MCP fingerprint, risk score, watch pulse, Mac Health block, partner tokens |
| **v1.3** | Partner webhook HTTP API |
| **v2.0** | launchd continuous watch daemon |

---

## 9. Acceptance

- [x] `bash scripts/validate-stranger-agent-safety-v1.sh` → OK  
- [x] Receipt schema `stranger-agent-admission-v1.2` with MCP + risk + SERVE stage  
- [x] Monitor file + Mac Health `stranger_agent` block  
- [x] `--watch` pulse writes watch receipt  
- [x] Cross-lane resolves `cursor` → `sourcea_worker` in SourceA  

**END LOCKED v1.2.0**
