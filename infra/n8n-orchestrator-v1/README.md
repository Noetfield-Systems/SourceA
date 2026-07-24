# SourceA n8n Orchestrator (Railway)

NF-SOURCEA-N8N-ORCHESTRATOR-V1 — production substrate.

## Live

| Surface | URL |
|---------|-----|
| Project | https://railway.com/project/57dae815-fd7b-4376-8dcf-65558ec18130 |
| n8n health | https://n8n-main-production-bfdc.up.railway.app/healthz |
| Services | `n8n-main` · `n8n-worker` · `Postgres` · `Redis` |

Ops Postgres is Railway-managed and separate from Supabase portfolio-spine.

## Law

n8n owns Executive Graph **lifecycle**. SourceA owns Goal/Decision/Memory/Evidence. Customer never gets this editor without OEM.

## Ops

| Item | Value |
|------|-------|
| Trigger host | `cloud` |
| `loop_id` | `sourcea_n8n_pulse_v1` |
| Deadman | `sourcea-deadman-v1` |
| Receipts | `receipts/n8n/` |

## Deploy / promote

```bash
./scripts/provision_railway_v1.sh
./scripts/promote_workflow_v1.sh ../../n8n/workflows/executive_webpage_repair_v1.json
```

Promotion path: Dev Editor → export JSON → GitHub PR → CI → merge → import Production n8n → Supabase ACTIVE pointer. Never Save to Production from editor.
