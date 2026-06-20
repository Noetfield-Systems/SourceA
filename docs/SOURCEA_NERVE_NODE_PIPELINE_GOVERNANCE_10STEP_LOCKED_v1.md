# SourceA Nerve · Node · Pipeline · Governance — 10-Step Live Wire — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T02:00:41Z · **Authority:** ASF SAVE TO  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_NERVE_NODE_PIPELINE_GOVERNANCE_10STEP_LOCKED_v1.md`

## One law

**Live = fresh `~/.sina` receipts synced into `agent-live-surfaces-v1.json` — every L1 Brain subordinate and L2 Worker role wired through session gate → disk live wire → nerve → hub. Chat and `command-data.json` are not SSOT.**

## Problem (baseline at save)

| Signal | Disk truth |
|--------|------------|
| `queue_sa` | `sa-1100` (SINGLE_SA · FREEZE) |
| `inbox_sa` | `sa-1101` — **mismatch** |
| Gate cart | **16/24 PASS** |
| Execution plane | **11/12 honest** |
| Zero drift | score 100 but **cross_layer / L0.5 false** |
| Loop chain | Investigator YELLOW · Judge **LOOP_DEGRADED** · specialist **observe_only** |
| W3 commercial | sina_read / mail_from / send_ready **RED** (founder-only) |

Ecosystem-connected rollup may PASS while individual nerves/nodes/gates remain RED — fail-closed fixes required.

## SSOT index

| Domain | Canonical |
|--------|-----------|
| Front door | `brain-os/law/entry/START_HERE_LOCKED_v1.md` |
| Role assignment | `brain-os/system/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md` |
| Layer stack | `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` |
| Node graph | `data/sourcea_pipeline_node_graph_v1.json` |
| Orient routing | `data/sourcea_orient_routing_v1.json` |
| Stack map | `data/commercial/stack-map-routing-v1.json` |
| Three pipelines | `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md` |
| Nerve orchestrator | `scripts/agent_nerve_system_v1.py` |
| Session gate | `scripts/agent_session_gate_run_v1.py` |
| Live surfaces | `~/.sina/agent-live-surfaces-v1.json` |
| Factory queue | `~/.sina/factory-now-v1.json` |

## Agent roles (must all be live-wired)

| Rank | Role | Builds? | Entry |
|------|------|---------|-------|
| L1-1 | Brain | Route only | `brain-session-start.sh` |
| L1-2–4 | Gov · Commercial · Brief | No | `agentic_layer_pipeline_v2.py` |
| L2-5 | SourceA Worker | **Yes** | `cursor_entry_gate.py --role worker` · RUN INBOX |
| L2-6–8 | RA L2 · Maintainers | Hub/runtime | Brain wire + live context |

Loop specialists (observe/advise — not ship authority): observatory · advisory · investigator · judge · loop specialist · routing panel.

---

## Step 1 — Truth baseline audit (read-only)

Snapshot every nerve/node/pipeline before edits.

```bash
python3 scripts/agent_session_gate_run_v1.py --role any --json
python3 scripts/governance_gate_cart_v1.py --json
python3 scripts/agent_nerve_system_v1.py --json
python3 scripts/pipeline_node_graph_runner_v1.py --json
python3 scripts/execution_plane_honesty_v1.py --json
python3 scripts/governance_zero_drift_live_wire_v1.py --role any --tier full --json
bash scripts/validate-sourcea-ecosystem-connected-v1.sh
```

**Record:** gate cart fails, `queue_sa` vs `inbox_sa`, L1/L2 counts, nerve node map, loop verdict.  
**Accept:** baseline receipt JSON under `receipts/` for post-fix diff.

---

## Step 2 — Queue SSOT unify (single `queue_sa` everywhere)

**Law:** `factory-now-v1.json` wins · anti-staleness aligns surfaces · brain · inbox · broker.

**Fix targets:**

- `scripts/anti_staleness_auto_wire_v1.py` → `queue_ssot_unify ok:true`
- `~/.sina/factory-now-v1.json` — reconcile `inbox_sa` with `queue_sa` or document brain work-order exception in `run-inbox-disk-truth-v1.json`
- `scripts/run_inbox_disk_truth_v1.py` · `scripts/outbound_queue_coherence_v1.py` — one head story
- `scripts/goal1_lane_broker.py` — broker closeout matches queue head

**Accept:** `queue_ssot_unify PASS` · single sa on `factory_now_line` · zero-drift `cross_layer=true`.

---

## Step 3 — L1 Brain + L2 Worker wire (every role live)

**Fix:** each role has receipt row, chat id, workspace, entry gate in `~/.sina/agentic-layer-pipeline-v2.json` with **L1≥3 · L2≥4 · cross_ref PASS**.

**Context receipts:**

- `~/.sina/brain-live-context-v1.json`
- `~/.sina/worker-live-context-v1.json`

**Accept:** `bash scripts/validate-agentic-layer-pipeline-v2.sh` PASS · memory mirror `inject` per role.

---

## Step 4 — Node graph full tick (T0→T3 + orient)

**Runner:** `scripts/pipeline_node_graph_runner_v1.py`  
**Graph:** `data/sourcea_pipeline_node_graph_v1.json`

Parallel groups:

| Tier | Nodes |
|------|-------|
| T0 | SASCIP live wire · mac health probe |
| T1 | disk live wire · governance zero drift · crawl-mirror session |
| T2 | agentic layer fast · L1 brain wire · hub dual heal |
| T3 | validate W10 vocab · two-hub · n8n P0 operational |
| T_lat | orient routing (orientation/hospital/maze on founder word only) |

**Accept:** `~/.sina/pipeline-node-graph-receipt-v1.json` all tiers PASS.

---

## Step 5 — Nerve system cart (all nodes honest)

**Orchestrator:** `scripts/agent_nerve_system_v1.py`  
**Map:** `data/form_official_nerve_map_v1.json`

Nerve rollup must not show `ok:true` while child nodes (e.g. `zero_drift`) are RED.

**Nodes to green:** surfaces · anti_staleness · zero_drift · better_loop · oqg · mirror_inject · worker_context · brain_context · truth_bundle · factory_now · outbound_coherence.

**Accept:** `bash scripts/validate-agent-nerve-system-v1.sh` · `validate-nerve-system-cart-v1.sh` PASS · `nerve_system_line` honest on live surfaces.

---

## Step 6 — Pipelines + loop chain routing

**Session start:** session gate only — no auto orientation/hospital/maze.

**Loop chain order** (`sina-command-server.py` `_run_loop_chain_tick`):

observatory → advisory → investigator → judge → loop specialist → routing panel → disclosure ladder → MCP stack → tool pick → anti_theater_loop → plans unified → phase0 → world model

**Orient cascade** (`data/sourcea_orient_routing_v1.json`): session_gate → disk truth → run_inbox → orient → hub projection.

**Accept:** `bash scripts/validate-loop-chain-e2e-v1.sh` PASS · E2E lines on `agent-live-surfaces-v1.json`.

---

## Step 7 — Execution plane + Worker RUN INBOX latch

**Honesty:** `scripts/execution_plane_honesty_v1.py` (12 checks)

**Fix blockers:**

- `queue_head_ready_or_done` — brain work-order vs local worker inbox
- `broker_closeout_truth` — last_sa == expected_sa
- `inbox_appropriate` — pending only when local worker head

**Accept:** execution plane **12/12** · `execution_honesty_line` OK · RUN INBOX path unambiguous in worker live context.

---

## Step 8 — Governance zero drift + gate cart 24/24

**Chain:** `governance_zero_drift_live_wire_v1.py` + paired anti-staleness/vocabulary gate.

**Known fails (baseline):** zero_drift · governance_center · nerve · zero_drift_wire · execution_queue_head_ready_or_done · commercial W3×3

**Order:** fix Steps 2+5+7 first · W3 gates stay `founder_pending` until Sina read + Mail (do not fake-green).

**Accept:** `bash scripts/validate-governance-zero-drift-live-wire-v1.sh` PASS · gate cart ≥22/24 with W3 documented founder-pending.

---

## Step 9 — Live surfaces + Hub projection (every worker slice)

**Sync:** `scripts/disk_live_wire_sync_v1.py` → `~/.sina/agent-live-surfaces-v1.json`

**Hub slices** (`worker_hub_v1.py` + H1): queue · nerve · execution honesty · anti-theater · plans unified · loop rooms · routing panel · outbound · kernel K1 · daily rooms.

**Accept:** Worker Hub Next steps populated · no load failed · `synced_at` fresh · every L1/L2 role has live context receipt.

---

## Step 10 — Close verify + stay-live pulse

```bash
python3 scripts/pipeline_node_graph_runner_v1.py --json
python3 scripts/agent_nerve_system_v1.py --json
python3 scripts/governance_gate_cart_v1.py --json
python3 scripts/disk_live_wire_sync_v1.py --json
bash scripts/validate-sourcea-ecosystem-connected-v1.sh
bash scripts/validate-governance-zero-drift-live-wire-v1.sh
bash scripts/validate-anti-staleness-vocabulary-gate-v1.sh
python3 scripts/loop_auto_graduation_v1.py --json
```

**Stay-live:** node-graph runner + nerve pulse on hub Actions or n8n P0 cron — receipts must not stale outside FREEZE.

**Accept:** ecosystem-connected PASS · honest gate cart · `factory_now_line` quoted every session gate reply.

---

## Target architecture

```text
session_gate
  └─ T0 SASCIP
       └─ T1 disk_live_wire + zero_drift + anti_staleness
            └─ T2 agentic_layer (L1 Brain + L2 Worker contexts)
                 └─ nerve_system
                      └─ loop_chain → hub slices → agent-live-surfaces
```

Founder words only (not session start): **orientation** · **hospital** · **maze**

---

## Out of scope (founder-only — never fake-green)

- W3 Sina read ≥90 · Mail send · confirm-sent
- Stripe onboarding · AUTO-RUN drain when kill flag ON
- New hub brand names · chat as SSOT

---

## Validators (close chain)

| Script | Checks |
|--------|--------|
| `validate-sourcea-ecosystem-connected-v1.sh` | worker · nerve · graph · agentic · orient · IJ loop |
| `validate-governance-zero-drift-live-wire-v1.sh` | drift chains + surfaces line |
| `validate-agent-nerve-system-v1.sh` | nerve pulse + queue alignment |
| `validate-agentic-layer-pipeline-v2.sh` | L1/L2 counts |
| `validate-loop-chain-e2e-v1.sh` | loop → routing panel → H1 UI |
| `validate-pipeline-node-graph-v1.sh` | node graph runner |
| `execution_plane_honesty_v1.py` | factory vs inbox vs broker |
| `governance_gate_cart_v1.py` | 24-gate rollup |

---

## Founder next tap

Worker Hub → **Next steps** (`http://127.0.0.1:13020/`) — confirm gate cart + nerve lines match disk — then **WORK: Step 1** (or **WORK: all 10**) in Worker chat.

W3 Mail (when queue resumes):

```bash
python3 scripts/w3_founder_review_v1.py --score fundmore 92
python3 scripts/w3_founder_review_v1.py --score ocre 92
```
