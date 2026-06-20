# Commercial Film Factory — Routing SSOT (LOCKED v1)

**Machine SSOT:** `data/commercial-film-routing-v1.json`  
**Version:** 1.0.0 · **Date:** 2026-06-15  
**Validator:** `bash scripts/validate-commercial-film-routing-v1.sh`

---

**Factory phases (GPT cinematic factory — routed, not rejected):**  
`data/commercial-film-factory-phases-v1.json` — Phase 0 live → Phase 5 memory loop

**Master plan:** `data/COMMERCIAL_FILM_FACTORY_MASTER_PLAN_v1.md` — unified GPT/advisor ledger · phases · next 10 work items

**Agent skills:** `.cursor/skills/skill-commercial-film-factory` · `skill-avatar-heygen-factory` · `skill-cinematic-finish-v1` · `skill-commercial-film-routing` · `skill-cinematic-orchestration` · `skill-founder-identity-layers`

---

**Confirmed:** 2026-06-15 · **ASF**

| Path | Choice |
|------|--------|
| **A** | Institutional hero finish — product-led, Proof Lab, tier routing |
| **B** | Face-led social ad as hero — **not chosen** |

Path A means: finish the film (frame, grade, SFX, dwell, logo wall) — **not** pivot to HeyGen or consumer TikTok as WitnessBC hero. Good advisor ideas **route** to other lanes/tiers via `commercial-film-routing-v1.json`.

---

**SourceA is the factory router.** Build once (`commercial_short_film_v1.py`) · route by **lane × tier** · distribute to portfolio products. Advisor ideas are **never deleted** — they are assigned a lane, tier, and beats file.

---

## Tiers

| Tier | Runtime | Use |
|------|---------|-----|
| **A_hero** | 120–240s | Institutional product film (WitnessBC, TrustField hero) |
| **B_proof** | ~5 min | W1/W2 enforcement demo (SourceA) |
| **C_social** | 30s | LinkedIn / Meta cut — avatar tests OK on consumer lanes |
| **D_gtm** | n/a | One-pager attach |

---

## Lane index

| Lane | Status | Beats file(s) | Entry |
|------|--------|---------------|-------|
| **witnessbc** | active | `witnessbc-commercial-film-beats-v1.json` · `witnessbc-commercial-social-30s-beats-v1.json` | `witnessbc-commercial-film.sh` |
| **sourcea** | active | `commercial-short-film-beats-v1.json` | `sourcea-commercial-film.sh` |
| **trustfield** | draft | `trustfield-commercial-film-beats-v1.json` | factory `--beats` |
| **noetfield** | draft | `noetfield-commercial-film-beats-v1.json` · `noetfield-commercial-social-30s-beats-v1.json` | factory `--beats` |
| **fitness** | placeholder | `fitness-commercial-film-beats-v1.json` | tier C only |
| **virlux** | placeholder | — | TBD |

---

## WitnessBC tier A — locked accepts

- Real Proof Lab `:8090` · ElevenLabs timestamps · chapter-only captions  
- `linear_bar` · logo cold open · 4K master · extended broll dwell  
- **No** synthetic avatar hero · **no** Gemini jargon · **no** consumer TikTok as tier A  

**v5 queued:** `cinematic_finish` + SFX + logo wall + dark frame

---

## Tool routing (summary)

| Tool | Lanes |
|------|-------|
| Playwright + ffmpeg factory | All A/B |
| ElevenLabs (`vo_lane` cache split) | All |
| Screen Studio ingest | SourceA · WitnessBC fallback |
| HeyGen | Tier C only — **blocked** WitnessBC hero |
| CapCut / Canva | Fitness · tier C tests |

Full ledger: `commercial-film-routing-v1.json` → `advisor_ideas_ledger`

---

## Render (founder one-tap via executor)

```bash
bash scripts/validate-commercial-film-routing-v1.sh
bash witnessbc-commercial-film.sh --json      # WitnessBC hero
bash sourcea-commercial-film.sh --json        # SourceA W1 proof cut
```

---

*End COMMERCIAL_FILM_ROUTING_LOCKED_v1*
