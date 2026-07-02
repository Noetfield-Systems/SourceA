# SourceA wiring — governed autorun v2

**Law mirror:** `docs/GOVERNED_AUTORUN_LAWS_v2.md`  
**Mac control:** dispatch OK · motor = CF cron only · `scripts/fbe/lib/mac_control_dispatch_v1.py`

## Boot (loop specialist session)

```bash
cd ~/Desktop/SourceA
python3 scripts/loop_specialist_tick_v1.py --json          # read-only tick receipt
python3 scripts/phase_reconciler_v1.py --json              # desired vs observed
python3 scripts/verify_autorun_zero_manual_v1.py --hours 24 --json   # ship window only
```

## Motor chain (L2)

| Layer | Path / URL |
|-------|------------|
| Scheduler | CF cron `*/10` → `data/cloud-auto-runtime-v1.json` |
| Tick worker | `cloud/workers/sourcea-cloud-auto-runtime-tick-v1/` |
| Railway motor | `POST /api/cloud-forge-run/auto-tick/v1` |
| Mac trigger (safe) | `~/.sina/sourcea-mac-v1.sh cf-tick --json` |
| Observer | `…/api/cloud-forge-run/observer/v1` |

## Receipts (L6 — repo, not ~/.sina)

| Type | Path |
|------|------|
| Cycle | `receipts/cloud/autonomous-forge-run-cycles/` |
| Heartbeat | `receipts/cloud/autonomous-forge-run-heartbeat/` |
| External verify | `receipts/cloud/external-verify/` |
| **Auto-pending** | `receipts/cloud/autorun-pending/pending-latest-v1.json` |
| Schemas | `.cursor/skills/governed-autorun/references/receipt-schemas.md` |

## Dirty deploy guard (L6)

```bash
python3 scripts/deploy_dirty_tree_guard_v1.py --scope fbe --json
python3 scripts/deploy_dirty_tree_guard_v1.py --scope landing --json
```

Scope map: `docs/SOURCEA_DEPLOY_DIRTY_TREE_SCOPE_MAP_LOCKED_v1.md`

## External verify only (L4)

Workflow: `.github/workflows/external-verify.yml`  
Agent local curls / Mac observe = **not** ship proof.

## Standing report (5 lines)

1. Last heartbeat path + date  
2. Last 3 cycle receipt IDs + states  
3. Sink invariant verdict  
4. `founder_blocked` count + oldest age  
5. Cost window + any `THROTTLED_ROI` / `BLOCKED_WITH_REASON`
6. **Pending auto-note** — `pending-latest-v1.json` count + head id (never manual "confirm in UI")

## HOLDs (founder)

- Step 10b `--autonomous-deploy` — not enabled without explicit ASF  
- Verifier criteria edits — founder-gated (L5)
