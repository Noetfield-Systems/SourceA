# Video ad factory — orchestration · audio · render

**Saved:** 2026-06-19T06:34:29Z · **Lane:** WitnessBC / cinematic commercial  
**Ledger:** `data/cursor-bootstrap-ledger-v1.json` → `microservices_routing.video_ad_factory`

## Layout

```text
video-ad-factory/
├── orchestration/      # LLM brief → script → shot list
├── audio-synthesis/    # ElevenLabs eleven_multilingual_v2
├── rendering-bridge/   # Fal.ai / Runway — vendor-swappable
└── loop-validator/     # HUMAN_APPROVAL_REQUIRED (PHASE_1B)
```

## Types

`shared/types/campaign-v1.ts` — Zod frozen contracts.

## Law

- Cloud only — no local Docker video render on Mac.  
- Preserve `video_prompt_loop` jsonb for iterative prompt tuning.  
- Stop at `HUMAN_APPROVAL_REQUIRED` until founder confirms.
