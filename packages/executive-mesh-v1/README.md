# @sourcea/executive-mesh-v1

Executive Mesh v1 vertical slice: Event → Role Pods (SG · Memory · Planner · Critic) → Governor (wraps ECP v0) → WorkPacket `RUNWAY_GOAL_KERNEL` → verify → canonical commit.

```bash
npm test
```

Runtime Worker: `cloud/workers/sourcea-executive-governor-v1` (Durable Object coordinator; Supabase migration `015_executive_mesh_v1.sql` is SSOT).
