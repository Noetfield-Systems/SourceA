---
name: skill-node-architect-agentic-system
description: >-
  HIGH PRO SourceA node-graph architect — design, wire, validate, and upgrade
  governable autonomous systems (not fragmented pipelines). Explicit graph SSOT,
  parallel tiers, receipt cascades, edge kinds, G0–G3 change class, Wil↔SourceA
  parity, E11 N01–N20. Use when architecting nodes, wiring graph, upgrading node
  skills, n8n-style parallel connections, autonomous tiers, or founder says node
  architect, high pro, synestm, unified graph, not fragmented.
---

# Node architect — agentic autonomous system (HIGH PRO v2.0)

**Version:** 2.1.0 HIGH PRO · **Saved:** 2026-06-16  
**Charter:** `docs/SOURCEA_NODE_ARCHITECT_AGENTIC_AUTONOMOUS_SYSTEM_LOCKED_v1.md`  
**Synestm build plan:** `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md`  
**Foundation:** `.cursor/skills/skill-foundational-agentic-systems/SKILL.md` — load first  
**Parent:** `.cursor/skills/skill-architecting-pipelines-pro/SKILL.md`  
**Graph SSOT:** `data/sourcea_pipeline_node_graph_v1.json` v1.3  
**Unified bundle:** `data/sourcea_agentic_unified_bundle_v1.json`  
**Mesh catalog:** `data/sourcea_node_mesh_catalog_v1.json` v1.1  
**Directory map:** `data/sourcea_directory_node_map_v1.json`  
**Runner:** `scripts/pipeline_node_graph_runner_v1.py`  
**Cart:** `CART TASK node-mesh` · `~/.sina/cart-tasks/tasks/node-mesh-cart-v1.json`  
**Founder mirror:** `~/.cursor/skills/sina-node-architect-agentic-system/SKILL.md`  
**Wil parity:** `~/Desktop/YA5/.cursor/skills/wil-ai-node-architecture/SKILL.md` (read-only)

**Reference files (load with skill):**

| File | Contents |
|------|----------|
| [NODE_MESH_REFERENCE.md](./NODE_MESH_REFERENCE.md) | Active + planned node catalog |
| [NODE_REFERENCE.md](./NODE_REFERENCE.md) | Schema · edge kinds · receipts |
| [NODE_PATTERNS.md](./NODE_PATTERNS.md) | Copy-paste patterns A–E |
| [NODE_BUILD_PLAN.md](./NODE_BUILD_PLAN.md) | Wave tracker · N01–N20 |

---

## Core law

> **One graph · many nodes · parallel tiers · disk receipts · explicit edges · n8n glues externals only.**

**Refuse** orphan pipeline scripts, hidden imports, or chat-only “wired” without graph row + receipt.

---

## When to load

| Trigger | Action |
|---------|--------|
| User wants synestm / wired everywhere | Load skill + NODE_MESH_REFERENCE + build plan |
| New validator or live wire script | Register node · map validate-* · receipt path |
| “Fragmented pipelines” / duplicate gate steps | Audit graph vs session gate · plan N03–N04 |
| Upgrade node skills / HIGH PRO | Sync project + sina mirror · bump version |
| Autonomous / scheduled execution | Tier + n8n manifest — never Cursor auto-paste |
| Hub node canvas (N07) | Graph read-only UI on `:13020` |
| Wil↔SourceA parity question | Use §Wil parity map — do not edit Wil from SourceA |

---

## Full pro mesh — six properties

| Property | SourceA implementation |
|----------|----------------------|
| **Explicit graph** | `data/sourcea_pipeline_node_graph_v1.json` — tiers + nodes |
| **Receipt per node** | `~/.sina/*-receipt-v1.json` · graph receipt |
| **Layer discipline** | T0 Safety · T1 Truth · T2 Fleet · T3 Proof |
| **Parallel when safe** | `parallel: true` per tier · runner ThreadPool |
| **Pipeline coexistence** | Four pipelines link to node clusters (dual nav) |
| **Governance edges** | SASCIP · cross-lane · founder verb on law writes |

```text
Session start → T0 parallel → T1 parallel → T2 parallel → T3 parallel → graph receipt
```

---

## Architecting workflow (agent — copy and track)

```text
Node design progress:
- [ ] 1. Name node id (snake_case) + tier + plane
- [ ] 2. Assign cmd vector + receipt path (or embed validator)
- [ ] 3. Set required · budget_sec · skip_if
- [ ] 4. Map validate-* script or W10 bundle row
- [ ] 5. Add edges_in/out when schema v1.2 (N05)
- [ ] 6. Cross-link charter N-row if milestone
- [ ] 7. Run validate-pipeline-node-graph-v1.sh
- [ ] 8. Run pipeline_node_graph_runner_v1.py --tier <id> --json
- [ ] 9. Confirm session gate does not duplicate (N04)
- [ ] 10. Class-appropriate proof (G1/G2/G3 below)
- [ ] 11. Gap audit cross-link only — law purity
- [ ] 12. Sync sina mirror + foundational index version
```

---

## Change classification (G0–G3)

| Class | If adding… | Minimum proof |
|-------|------------|---------------|
| **G0** | Doc / explain mesh | Optional graph validate |
| **G1** | One node row + handler exists | `validate-pipeline-node-graph-v1.sh` |
| **G2** | Multi-node tier + gate interaction | Graph runner `--json` + session gate |
| **G3** | Session gate delegate · parallel tier rewrite | Full graph run + W10 + pre-ship |

**G3 rule:** Session gate must call runner for tier — not duplicate linear steps (N03–N04).

---

## Edge kinds (declare on N05+)

| Kind | Use when |
|------|----------|
| `trigger` | Session / founder starts tier |
| `wire` | Live sync disk → downstream node |
| `gate` | Must PASS before next tier |
| `fan-out` | Parallel siblings in tier |
| `data` | SSOT artifact flows (receipt → inject) |
| `alarm` | Mac Health / panic → skip nodes |
| `orchestrate` | Runner invokes tier set |
| `surface` | Hub / Mac Health visible output |
| `glue` | n8n external clock only |

Event bus topics (N06): `spine.bridge` · `founder_action` · `factory.advance` · `governance.heal`

---

## Live parallel groups (graph v1.1)

| Tier | Nodes | Budget |
|------|-------|--------|
| **T0_safety** | sascip_live_wire · mac_health_probe | 30s |
| **T1_truth_parallel** | disk_live_wire · governance_zero_drift · crawl_mirror_session | 90s |
| **T2_fleet_parallel** | agentic_layer_fast · l1_brain_wire · hub_dual_heal | 60s |
| **T3_proof_parallel** | validate_w10_vocab · validate_two_hub · n8n_p0_operational | 120s |

**Rule:** Sequential across tiers · parallel within tier · `skip_if: hub_down | panic_active`.

---

## Pipelines ↔ nodes (dual nav)

| Pipeline | Node ids (cluster) |
|----------|-------------------|
| **Safety** | sascip_live_wire · mac_health_probe |
| **Truth** | disk_live_wire · governance_zero_drift · crawl_mirror_session |
| **Fleet** | agentic_layer_fast · l1_brain_wire · hub_dual_heal |
| **Proof** | validate_w10_vocab · validate_two_hub · n8n_p0_operational |

New capability → **pipeline narrative + graph node row** (never one without the other).

---

## Wil ↔ SourceA parity (read-only)

| Wil AI | SourceA analog |
|--------|----------------|
| `NODE_GRAPH.json` | `sourcea_pipeline_node_graph_v1.json` |
| `node-runner.mjs` | `pipeline_node_graph_runner_v1.py` |
| `run:nodes:session` | `--tier T1_truth_parallel` (example) |
| L05 machine wires | T1 Truth tier |
| GOV session gate | T0 + gate delegate (N03) |
| `check:node-graph` | `validate-pipeline-node-graph-v1.sh` |
| **Orient routing** | `docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md` · `agent_orient_v1.py` |

**Never edit Wil from SourceA Worker** — repo boundary.

---

## Plan spine (N01–N20)

| Done | ID | Item |
|------|-----|------|
| ✅ | N01 | Graph + runner + validator |
| ✅ | N02 | Charter + skills v2.1 + NODE_* references |
| ✅ | N05 | edges_in/out v1.2 + parallel_groups |
| ⬜ | N03–N04 | Session gate → runner (no duplicate steps) |
| ⬜ | N06 | Event bus emit spine.bridge |
| ⬜ | N07–N08 | Hub node canvas + founder tap |
| ⬜ | N11–N12 | C1–C10 · M1–M11 subgraph |

Full table: charter §6.

---

## Proof ladder (HIGH PRO)

```bash
cd ~/Desktop/SourceA
bash scripts/validate-pipeline-node-graph-v1.sh
python3 scripts/pipeline_node_graph_runner_v1.py --dry-run --json
python3 scripts/pipeline_node_graph_runner_v1.py --json
python3 -c "import json; print(json.load(open('$HOME/.sina/pipeline-node-graph-receipt-v1.json')).get('ok'))"
python3 scripts/agent_session_gate_run_v1.py --role worker --json
```

Healthy: graph validate PASS · runner ok · gate ok · no duplicate crawl-mirror in gate+graph without N04 done.

---

## Never do

| Anti-pattern | Why |
|--------------|-----|
| Orphan script without graph row | Fragment — fails IC-019 class audit |
| n8n as law/brain SSOT | Glue tier only |
| Node `required: true` without receipt/validator | Graph lint / honest GAP |
| Skip parallel flag on mutating shared files | Race on `~/.sina` |
| Chat “wired” without JSON receipt | Not ship-ready |
| Edit YA5/Wil from SourceA | Repo boundary |

---

## References (read order)

1. `docs/SOURCEA_NODE_ARCHITECT_AGENTIC_AUTONOMOUS_SYSTEM_LOCKED_v1.md`  
2. `data/sourcea_pipeline_node_graph_v1.json`  
3. `docs/SOURCEA_ECOSYSTEM_GAP_AUDIT_AND_SYSTEM_MAP_LOCKED_v1.md`  
4. `docs/SOURCEA_FOUNDATIONAL_AGENTIC_SYSTEMS_INDEX_LOCKED_v1.md`  
5. `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`  
6. `scripts/fixtures/n8n/workflow_manifest.json`

---

**END skill-node-architect-agentic-system · HIGH PRO v2.1.0 · synestm**
