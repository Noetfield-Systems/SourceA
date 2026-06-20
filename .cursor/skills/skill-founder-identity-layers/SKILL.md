---
name: skill-founder-identity-layers
description: >-
  Maps founder identity to ICP presentation layers: human 10–20% vs product 80–90%,
  LinkedIn anchor, hybrid Linear hook, tier C avatar, and Canada funding credibility.
  Use when the founder asks about showing their face, digital twin, human anchor
  script, map my layers, hybrid template, or which video type per market.
---

# Founder Identity Layers

## When to use

- "Should I show my face?" · LinkedIn human video · Canada credibility
- Routing HeyGen vs real camera vs product-only per ICP
- GPT trust levels (face-first · product-first · hybrid)
- Digital twin vs institutional hero confusion

## Core rule

**One identity · three presentation layers · five ICPs map to layers — not five personas.**

```text
YOU (core: builder of AI governance systems)
  ↓
presentation layer (institutional | product | agency)
  ↓
ICP (Canada/funding | GRC | automation | etc.)
```

**Ratio lock:** Human **10–20%** · System **80–90%**.

## Three trust levels (GPT → disk)

| Level | Film type | Human | Lanes |
|-------|-----------|-------|-------|
| **1 Face-first** | Founder anchor 20–40s | Required | Canada · funding · LinkedIn inbound |
| **2 Product-first** | Playwright + ElevenLabs hero | **0%** | witnessbc tier A · sourcea proof · **Path A** |
| **3 Hybrid** | 0–3s face → product | Hook only | tier C · v6 after v5 · NOT witnessbc tier A yet |

## Presentation layers

### Institutional / Canada / funding (10–20% human)

**Assets (one-time Master Human Asset):**

1. Headshot → `~/.sina/avatar-pipeline-v1/master-image.jpg`
2. 20–40s anchor video — real phone OR HeyGen image-to-video
3. LinkedIn profile + grant/VC credibility

**Commands:**

```bash
bash avatar-pipeline.sh linkedin
# Scripts: data/avatar-scripts-v1.json → linkedin_anchor_v1
```

**Avatar policy:** Real preferred · HeyGen OK for LinkedIn volume · **never** witnessbc.com hero.

### Product GRC / enterprise (0% human hero)

**Lanes:** witnessbc · sourcea  
**Style:** Linear product-led · cinematic_finish · sync validator  
**Commands:** `witnessbc-commercial-film.sh` · `sourcea-commercial-film.sh`

### Digital twin factory (tier C volume)

**Lanes:** fitness · trustfield_social · noetfield_social · linkedin volume  
**Stack:** master image → ElevenLabs → HeyGen v3 → mux  
**Skill:** `skill-avatar-heygen-factory`

## ICP → layer quick map

| ICP / market | Layer | Video | Face |
|--------------|-------|-------|------|
| Canada grants / VC | institutional | LinkedIn anchor | Yes |
| GRC / CISO / WitnessBC | product | tier A hero | No |
| SourceA investor proof | product | tier B 32s W1 | No |
| TrustField MSB pilot | product hero + tier C social | split | Social only |
| Noetfield Copilot wedge | product + tier C | split | Social optional real |
| Fitness / consumer | tier C | HeyGen/UGC open | OK |

## LinkedIn anchor script (GPT — use for tier C only)

**0–5s:** "I build AI systems that help companies automate decisions and operations."

**5–15s:** "Right now I'm working on platforms that combine AI agents, governance, and real-time execution systems."

**15–30s:** "My focus is building working systems for real companies — compliance, automation, and infrastructure."

**30–40s:** "If you're building in this space or investing in it, I'm open to connect."

Record real OR generate via `avatar-pipeline.sh linkedin` with this script in `avatar-scripts-v1.json`.

## Hybrid template (tier C / v6 — future)

```text
0–2s  → real face or master image (trust seed)
2–5s  → transition blur / zoom
5–25s → Playwright product proof (W1 BLOCK/tamper)
25–30s → receipt + CTA
```

**Blocked:** witnessbc.tier_A_hero until v5 cinematic lands.

## Decision tree

```
Buyer = GRC / trust / runtime proof?
  YES → product-only (Level 2) — no HeyGen hero
  NO → funding / LinkedIn / consumer?
    YES → human anchor or digital twin (Level 1 or tier C)
```

## Do not

- Use HeyGen on WitnessBC tier A hero (Path A lock)
- Use one video style for all five ICPs
- Skip master headshot before avatar pipeline
- Mix LinkedIn anchor into sourcea proof cut as hero

## Related

- `skill-avatar-heygen-factory` — execute avatar lanes
- `skill-commercial-film-routing` — tier adjudication
- `data/COMMERCIAL_FILM_FACTORY_MASTER_PLAN_v1.md` § Identity layers
