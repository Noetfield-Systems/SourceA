---
name: skill-avatar-heygen-factory
description: >-
  Runs the avatar digital-twin factory: master image, ElevenLabs VO, HeyGen
  talking photo API or manual fallback, lane routing, quality tier, and blocked
  WitnessBC tier A. Use when the founder mentions avatar pipeline, HeyGen,
  digital twin, LinkedIn anchor video, D-ID, or tier C social with synthetic face.
---

# Avatar / HeyGen Factory

## When to use

- LinkedIn human anchor · TrustField/Noetfield tier C social
- HeyGen or D-ID talking photo from founder headshot
- ElevenLabs VO for avatar lanes (not hero film VO)

## Principle

**Master human asset → ElevenLabs VO → HeyGen/D-ID → mux.**  
**Never** WitnessBC tier A hero — synthetic face on trust product = blocked.

## SSOT

| File | Role |
|------|------|
| `data/avatar-pipeline-config-v1.json` | Lanes · secrets · blocked_lanes |
| `data/avatar-scripts-v1.json` | Script text per lane |
| `data/commercial-film-factory-phases-v1.json` | `identity_layers.digital_twin_factory` |
| `avatar-pipeline.sh` | Shell entry |

## Blocked lanes

```json
"blocked_lanes": ["witnessbc_hero"]
```

Routing: `commercial-film-routing-v1.json` → `tool_routing.heygen_avatar.blocked_lanes`

## Setup checklist

```bash
# 1. Master image (required for HeyGen)
ls ~/.sina/avatar-pipeline-v1/master-image.jpg \
   ~/Desktop/founder-headshot.jpg 2>/dev/null

# 2. ElevenLabs key
python3 scripts/sourcea_elevenlabs_vo_setup_v1.py --check --json

# 3. HeyGen key (required for auto; manual fallback if missing)
python3 scripts/heygen_avatar_setup_v1.py --check --json
```

## Commands

```bash
cd ~/Desktop/Noetfield-Systems/SourceA

# LinkedIn institutional anchor (~40s)
bash avatar-pipeline.sh linkedin

# TrustField top-funnel social (HeyGen test OK)
bash avatar-pipeline.sh trustfield_social

# Noetfield design-partner social
bash avatar-pipeline.sh noetfield_social

# Mux HeyGen studio export with cached VO
python3 scripts/avatar_pipeline_v1.py \
  --lane linkedin \
  --avatar-video ~/Downloads/heygen-export.mp4 --json

# Validate wiring
bash scripts/validate-avatar-pipeline-v1.sh
```

## Lanes

| Lane | Script ID | Output desktop | Avatar policy |
|------|-----------|----------------|---------------|
| `linkedin` | `linkedin_anchor_v1` | `Founder-LinkedIn-Anchor.mp4` | real or HeyGen image-to-video |
| `trustfield_social` | `trustfield_social_v1` | `TrustField-Social-Anchor.mp4` | heygen_test_ok |
| `noetfield_social` | `noetfield_social_v1` | `Noetfield-Social-Anchor.mp4` | real_founder_preferred |
| `fitness_social` | `fitness_social_v1` | `Fitness-Social-Anchor.mp4` | heygen_ugc_ok |

## Env files

| Secret | Path |
|--------|------|
| `HEYGEN_API_KEY` | `~/.sina/heygen-v1.env` |
| ElevenLabs | `~/.sina/elevenlabs-v1.env` |

Work root: `~/.sina/avatar-pipeline-v1/` (voice.mp3 · script.txt · manual pack README)

## HeyGen v3 auto (wired)

Flow in `scripts/heygen_avatar_wire_v1.py`:

1. `POST /v3/assets` — upload master image + ElevenLabs mp3
2. `POST /v3/avatars` — photo avatar (cached by image hash)
3. `POST /v3/videos` — 1080p lipsync via `audio_asset_id` · `avatar_v` engine
4. Poll + download → work dir MP4

Quality tier: `data/avatar-pipeline-config-v1.json` → `quality.tier: high`

**Manual fallback** (no key or API fail):

1. `bash avatar-pipeline.sh linkedin` → VO + manual pack in work dir
2. HeyGen/D-ID studio export → `--avatar-video` mux

## Quality recommendations

- Master image: 1024×1024+ · neutral background · even lighting · forward-facing
- LinkedIn anchor: 20–40s · outcome language · no product jargon overload
- TrustField social: RPAA urgency · demo CTA · tier C only
- Do not use avatar output on `witnessbc.com` hero slot

## Do not

- Route HeyGen output to WitnessBC tier A hero (founder_lock Path A)
- Skip master image check — pipeline writes manual README instead of failing silently
- Print full API keys in chat logs
- Replace `commercial_short_film_v1.py` Playwright capture with avatar for institutional films
