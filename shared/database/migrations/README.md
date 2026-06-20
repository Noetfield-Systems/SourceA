# Supabase migrations — video-ad + governance receipts

**Saved:** 2026-06-19T06:34:29Z

Place SQL migrations here. Apply via Supabase CLI:

```bash
supabase db push
```

Starter schema (campaign factory) — see Gemini blueprint §2; implement in `001_campaign_automations.sql` when PHASE_1 ships.

Tables (reserved):

- `profiles` — multi-tenant + StoreKit transaction id  
- `campaign_automations` — brief → render loop (`video_prompt_loop` jsonb)  
- `resource_logs` — token + API cost telemetry  

Receipt bucket: `data/mcp-receipts-bucket-spec-v1.json`
