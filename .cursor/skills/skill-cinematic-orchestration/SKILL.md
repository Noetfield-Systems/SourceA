---
name: skill-cinematic-orchestration
description: >-
  Plans and implements Phase 3–5 cinematic factory upgrades: n8n orchestration,
  OpenRouter script variations, multi-format distribution, film memory loop, and
  production docker-compose. Use when the founder mentions production deploy,
  n8n workflow, film memory engine, self-healing factory, distribution APIs,
  or Phase 3/4/5 from commercial-film-factory-phases.
---

# Cinematic Orchestration (Phase 3–5)

## When to use

- Founder says **production deploy version** · **build memory engine** · **n8n**
- Planning OpenRouter hook A/B · social publisher · R2 upload
- **Not** for day-to-day hero renders — use `skill-commercial-film-factory` first

## Prerequisite gate

**Do not start Phase 3+ until:**

- WitnessBC v4 extended landed on Desktop
- WitnessBC v5 cinematic receipt PASS (or SourceA sync validator PASS)
- Phase 0 compiler stable — no greenfield `witness-film/` repo

## SSOT

| File | Role |
|------|------|
| `data/commercial-film-factory-phases-v1.json` | Phase 3–5 definitions |
| `data/COMMERCIAL_FILM_FACTORY_MASTER_PLAN_v1.md` | Full GPT synthesis · incident schema |
| `data/commercial-film-routing-v1.json` | Lane publish policy |

## Phase 3 — n8n control plane

**Flow (wrap existing shells — do not rewrite compiler):**

```text
webhook trigger
  → OpenAI director (beats structure + emotion_map)
  → OpenRouter variations (hooks · CTA · multilingual)
  → selector (rule or AI rank)
  → bash witnessbc-commercial-film.sh | sourcea-commercial-film.sh
  → upload R2/S3
  → return receipt + asset URL
```

**Deploy options:** single VPS docker-compose · Railway/Fly Playwright sidecar.

**API contracts to expose (future):**

```http
POST /film/render
{ "lane": "witnessbc", "beats": "data/witnessbc-commercial-film-beats-v5.json" }

POST /capture
{ "url": "http://127.0.0.1:8090/proof.html", "w1_sequence": [["block", 8]] }
```

## Phase 4 — distribution bundle

Per run outputs:

```text
final.mp4
final_9x16.mp4
final_1x1.mp4
caption.txt
hashtags.json
title_variants.json
thumbnail.png
```

**Lane publish policy:**

| Lane | Primary channel |
|------|-----------------|
| witnessbc | LinkedIn institutional |
| trustfield | demo booking |
| noetfield | design partner email |
| fitness | TikTok/IG volume OK |

## Phase 5 — film memory loop

**Principle:** Each film is an experiment — incident report drives rule evolution.

**Incident row fields:**

- `video_id` · `dropoff_point` · `watch_time_loss` · `confusion_zone`
- `trust_peak` · `failure_reason` · `next_fix` · `rule_delta`

**Loop:**

```text
render → publish → analytics → incident → OpenAI analyzer → update beats SSOT → next render
```

**Storage:** SQLite `~/.sina/film-memory-v1.db` first · Supabase when multi-agent.

## Spike checklist (Phase 3 minimal)

```bash
# 1. Existing entrypoints still work
bash scripts/validate-commercial-film-routing-v1.sh
bash scripts/validate-commercial-film-sync-v1.sh

# 2. n8n webhook calls shell (no new Python compiler)
# POST → witnessbc-commercial-film.sh --json

# 3. Receipt path returned in webhook response
cat ~/.sina/enforcement/witnessbc-commercial-film-receipt-v1.json
```

## Do not

- Replace `commercial_short_film_v1.py` with n8n-only glue
- Add OpenRouter to hot path before deterministic heroes ship
- Auto-publish TikTok for WitnessBC tier A
- Build Supabase schema before first published film has analytics

## Related

- `skill-commercial-film-factory` — Phase 0 renders
- `skill-commercial-film-routing` — lane × tier policy
- `skill-founder-identity-layers` — human vs product ratio
