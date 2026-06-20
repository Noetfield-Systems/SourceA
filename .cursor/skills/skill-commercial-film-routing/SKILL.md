---
name: skill-commercial-film-routing
description: >-
  Reads commercial film routing SSOT, advisor idea adjudication, tier A/B/C/D
  matrix, founder_lock Path A, and validate script. Use when routing advisor
  ideas, assigning lanes and tiers, adjudicating HeyGen vs product-led hero, or
  editing commercial-film-routing-v1.json.
---

# Commercial Film Routing

## When to use

- Route a new advisor idea to lane × tier
- Adjudicate tier A vs C · avatar vs product-led
- Read or update `commercial-film-routing-v1.json`
- Explain Path A founder lock vs rejected hero modes

## SSOT files

| File | Role |
|------|------|
| `data/commercial-film-routing-v1.json` | Machine routing · ledger · render_commands |
| `data/COMMERCIAL_FILM_ROUTING_LOCKED_v1.md` | Human lock summary |
| `data/commercial-film-factory-phases-v1.json` | Phase 0–5 · gpt_ideas_ledger |
| `data/COMMERCIAL_FILM_FACTORY_MASTER_PLAN_v1.md` | Unified plan |

## Founder lock — Path A

```json
"founder_lock": {
  "path": "A",
  "label": "Institutional hero finish + factory routing",
  "rejects_as_hero": ["heygen_avatar", "consumer_tiktok_tier_A", "gemini_jargon_vo"],
  "routes_not_rejects": ["tier_C_social", "heygen_trustfield_test", "founder_selfie_tier_C", "logo_wall", "sfx", "cinematic_finish"]
}
```

**Path A means:** Finish the film (frame, grade, SFX, dwell, logo wall) — **not** pivot to HeyGen or TikTok as WitnessBC hero.

**Path B (face-led social hero):** Not chosen.

## Tier definitions

| Tier | Runtime | Buyer | Avatar |
|------|---------|-------|--------|
| **A_hero** | 120–240s | CISO · GRC · platform | no_synthetic_hero |
| **B_proof** | ~300s | Investor · auditor | none |
| **C_social** | 30s | Pipeline · awareness | real_founder_ok · synthetic_discouraged |
| **D_gtm** | n/a | Prospect email | n/a |

## Lane status (2026-06-15)

| Lane | Status | Primary beats |
|------|--------|---------------|
| witnessbc | active | v1 hero · v5 queued · 30s social draft |
| sourcea | active | commercial-short-film-beats-v1.json |
| trustfield | draft | trustfield-commercial-film-beats-v1.json |
| noetfield | draft | noetfield + social 30s beats |
| fitness | placeholder | fitness-commercial-film-beats-v1.json |
| virlux | placeholder | — |

## Advisor adjudication workflow

When a new advisor idea arrives:

1. **Classify:** EXTERNAL_CRITIC — not ASF build order
2. **Check disk:** Does factory already implement it? (GPT minimal stack often = already built)
3. **Assign status:**
   - `accepted` — implement in Path A finish
   - `routed` / `routed_not_rejected` — assign lane + tier + beats file
   - `rejected_for_this_lane_only` — document in lane asset, not global delete
4. **Write row** in `advisor_ideas_ledger` + `gpt_ideas_ledger` (phases doc)
5. **Run validator** before close

## Idea status examples

| Idea | Status | Where |
|------|--------|-------|
| GPT minimal playwright+ffmpeg | accepted_already_built | phase 0 |
| GPT cinematic SFX | accepted | phase 1 · polish.sfx |
| Soonet HeyGen avatar | routed_not_rejected | tier C · trustfield only |
| n8n orchestration | routed | phase 3 |
| Film memory | routed | phase 5 |
| HeyGen WitnessBC tier A | rejected per lane | founder_lock |

## Tool routing summary

| Tool | Lanes | Blocked |
|------|-------|---------|
| Playwright + ffmpeg factory | All A/B | — |
| ElevenLabs (vo_lane split) | All | — |
| Screen Studio ingest | sourcea · witnessbc fallback | — |
| HeyGen avatar | tier C · trustfield/fitness | witnessbc.tier_A_hero |
| Remotion | title cards only | hero replacement |
| CapCut/Canva | fitness · tier C tests | — |

## Validator

```bash
cd ~/Desktop/SourceA
bash scripts/validate-commercial-film-routing-v1.sh
```

Checks: schema · beats files exist · routing_ref · required scripts · witnessbc/sourcea active.

## render_commands (from SSOT)

Key entries in `commercial-film-routing-v1.json` → `render_commands`:

- `witnessbc_hero` · `witnessbc_social_30s` · `sourcea_proof`
- `trustfield_draft` · `noetfield_draft`
- `avatar_linkedin` · `avatar_trustfield_social` · `avatar_mux`

## Do not

- Delete advisor ideas — always route to lane/tier/beats
- Replace registered product names with status words (*pending*, *live*)
- Put HeyGen hero on WitnessBC tier A without ASF Path B override
- Edit routing JSON without validator PASS
- Treat chat GPT paste as SSOT over disk routing file

## Related skills

- `skill-commercial-film-factory` — execute renders
- `skill-avatar-heygen-factory` — tier C avatar only
- `skill-cinematic-finish-v1` — Path A finish rules
- `skill-cinematic-orchestration` — Phase 3–5 future
- `skill-founder-identity-layers` — human 10–20% policy
