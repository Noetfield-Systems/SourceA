# sourcea-executive-governor-v1

Cloudflare Worker + Durable Object for Executive Mesh ingress.

- `GET /health`
- `POST /v1/executive/runs?org=sourcea` — idempotent event ingest (serialized per org DO)
- Rejects stale `canonical_state_version`
- Routes webpage-repair WorkPackets to Runway Goal Kernel when `MESH_SIMULATE=0` and `RUNWAY_GOAL_BASE_URL` set

```bash
npx wrangler@4 deploy
```

Deadman watch target: `loop_id=sourcea_executive_pulse_v1` (pulse cron may be added; ingress is live without it).
