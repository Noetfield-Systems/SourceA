# SourceA Multi-App Handoff — 2026-06-22T17:40Z

```yaml
session:
  reason: context_window_reset
  workspace: ~/Desktop/SourceA
  mac_role: control_plane_only
  factory_mode: FREEZE

apps:
  worker_hub:
    port: 13020
    health: /health
    paths: [agent-control-panel/, scripts/sina-command-server.py]
    state: LIVE
  mac_health:
    port: 13024
    health: /health
    state: LIVE
  routing_panel:
    port: 8780
    health: /api/panel/health
    state: LIVE
  mac_law:
    port: 8781
    health: /api/mac-law/health
    state: LIVE
  cloud_workers:
    ui: agent-control-panel/cloud-workers/
    machine: scripts/cloud_workers_hub_v1.py
    api: GET|POST /api/cloud-workers/v1
    state: batch_2_armed
  railway_fbe:
    url: https://sourcea-fbe-runner-production.up.railway.app
    health: /health
    observer: /observer
    motor: hub_cloud_drain_proceed_v1.py (headless)
    state: LIVE_deployed
  cf_cron:
    worker: sourcea-cloud-drain-tick-v1.witness-bc.workers.dev
    schedule: "*/10 * * * *"
    tick: POST /tick -> Railway /api/cloud-drain/proceed/v1
    state: ARMED

architecture: |
  Mac(:13020) -> proxy -> Railway FBE -> PROVE(living_system_chain) -> contract -> SHIP
  CF cron (primary) | n8n Mac (backup OFF) | auto_tick evidence_slice T2/T3 free
  Receipts: /app/receipts/cloud/ + mirror ~/.sina/autonomous-drain-cycle-receipts/

queue_batch:
  batch_1: COMPLETE locked archive data/secondary-cloud-drain-batch-1-complete-locked-v1.json
  batch_2: ACTIVE locked data/secondary-cloud-drain-batch-2-locked-v1.json
  pointer: data/cloud-drain-queue-active-v1.json
  head: CLOUD-SEC-101
  range: CLOUD-SEC-101..200
  mac_ctl: MAC-CTL-011..020
  maps: sa-mkt-0091..sa-mkt-0190
  generator: scripts/generate_secondary_cloud_drain_batch_v1.py
  path_resolver: scripts/cloud_drain_queue_path_v1.py
  control_plane: data/cloud-workers-control-plane-v1.json

mission_status:
  A_cloud_drain_mac_asleep: DONE batch1 (4+ CF cron greens server-side PROVE)
  B_root_tidy: DONE .cursorignore + symlinks + shared/types/execution-contract-v1.ts
  batch_2_feed: DONE disk locked; Railway queue reset pending founder Refresh

verified_features:
  - CF cron autonomous drain PROVE+SHIP server-side
  - Observer HTML+JSON iPhone URL
  - batch_complete detection queue_batch_complete
  - motor_timeout vs pipe_down UX fix
  - prove in-process read_head (no HTTP loopback flake)
  - auto_tick evidence_slice for T2/T3 free (Railway 60s edge)

blockers:
  P1: Railway cloud phase must match Mac — run set_head CLOUD-SEC-101 if cloud still shows 090
  P2: Hub GET /api/cloud-drain/queue/v1 on :13020 returns 404 — proxy not wired (use Railway direct)
  P3: Chains 5/7 on Mac living_system_chain — Mac localhost probes; cloud PROVE is 3/3

key_paths:
  queue_active: data/cloud-drain-queue-active-v1.json
  batch_2: data/secondary-cloud-drain-batch-2-locked-v1.json
  cloud_workers: scripts/cloud_workers_hub_v1.py
  drain_proceed: scripts/hub_cloud_drain_proceed_v1.py
  auto_runtime: data/cloud-drain-auto-runtime-v1.json
  deploy: scripts/deploy_fbe_railway_v1.py

next_actions:
  - Cloud Workers UI Refresh all → confirm head CLOUD-SEC-101 batch 2
  - POST Railway queue set_head if drift
  - Wire hub :13020 /api/cloud-drain/queue/v1 proxy (optional)
  - First CF cron green on CLOUD-SEC-101 receipt verify
```
