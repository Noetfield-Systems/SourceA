# SourceA Commercial Video — Hero Pipeline (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**sequence_id:** SA-2026-06-15-VIDEO-HERO  
**Locked:** 2026-06-15  
**Authority:** Founder lock · Gemini/Remotion thread · `SOURCEA_HIGH_QUALITY_COMMERCIAL_VIDEO_RESEARCH_2026-06-15_v1.md`  
**Machine receipt:** `~/.sina/enforcement/sourcea-video-hero-pipeline-plan-v1.json`

---

## One-line law (non-negotiable)

> **Gemini is right that Remotion alone isn’t cinematic and generative AI alone isn’t readable — but for SourceA, the hybrid is derivative scale, not the hero. Real product capture → polish → programmatic variants beats Runway background + Hormozi text for a governance product.**

---

## What wins (Tier S — hero)

| Step | Tool | Output | Grade target |
|------|------|--------|--------------|
| 1 | **Screen Studio** | `~/Desktop/SourceA-W1-Master.mov` | **A** |
| 2 | **Descript** (or ffmpeg pass) | Captions · −14 LUFS · trim | **A** |
| 3 | **Ingest** | `w1_film_ingest_master_v1.py` → `w1-demo.mp4` | **A** embed |
| 4 | **Gate K host** | Vercel Hobby `sourcea-landing.vercel.app` | durable URL |
| 5 | **Remotion factory** | Per-prospect CTA overlay on **real** b-roll only | **B+** scale |

**Founder one next tap:** Drop `~/Desktop/SourceA-W1-Master.mov` and say **`film`** — ingest → grade A → Remotion overlays on that master, **not** Runway fiction.

---

## What loses (never hero)

| Path | Grade | Law |
|------|-------|-----|
| Remotion `TerminalMock` alone | **F** | `SHIP_BLOCKED_MOCK` |
| Runway/Sora generative B-roll as product proof | **F** | No verifiable BLOCK receipts |
| Gemini Instagram typography reel | **F** | No real UI |
| Playwright auto-capture without Screen Studio master | **C+** | Dev preview only — not ship hero |
| ElevenLabs + Deepgram + Runway “god-mode” before master exists | **Wrong order** | Scale layer only |

---

## Stack order (locked)

```text
WRONG (rejected):
  Runway background → ElevenLabs → Remotion Hormozi text → outbound

RIGHT (locked):
  Screen Studio 4K master (real :5180 / :8090 UI)
        ↓
  Descript polish + burned-in captions
        ↓
  w1_film_ingest_master_v1.py → w1-demo.mp4 (grade A)
        ↓
  Gate K: sourcea-landing.vercel.app (Vercel Hobby · $0)
        ↓
  commercial_video_factory_v1.py → prospect JSON → overlay on real b-roll
        ↓
  (Optional later) Runway 3–5s abstract hook ONLY — never product chrome
```

---

## Lane separation

| Lane | Hero path | Reference style |
|------|-----------|-----------------|
| **SourceA W1** | Screen Studio `:5180` five beats | Linear orientation (product IS video) |
| **WitnessBC** | `linear_orientation` Playwright `:8090` | Linear Learn chapters · **B+** until Screen Studio |
| **AB1 outbound** | Real b-roll in `ProspectReel` · `broll/w1-proof.mp4` | Remotion = overlay only |

---

## Scripts (SSOT)

| Step | Command / script |
|------|------------------|
| Ingest master | `python3 scripts/w1_film_ingest_master_v1.py --json` |
| Auto fallback (dev) | `python3 scripts/w1_film_generate_v1.py` |
| Prospect reel | `python3 scripts/commercial_video_factory_v1.py --row cp-a0c7c6c607` |
| WitnessBC film | `bash witnessbc-commercial-film.sh --json` |
| Gate K publish | `python3 scripts/gate_k_vercel_start_v1.py --json` |
| Quality gate | `bash scripts/validate-demo-film-quality-v1.sh` |

---

## Grades logged (2026-06-15)

| Asset | Grade | Status |
|-------|-------|--------|
| `SourceA-W1-Master.mov` | — | **Missing — blocks grade A** |
| `w1-demo.mp4` (auto) | C+ | embed_live |
| `WitnessBC-Commercial.mp4` | B+ | linear_orientation · embed_live |
| `prospect-reel.mp4` (AB1) | B+ | real b-roll wired |
| Gate K URL | PASS | `https://sourcea-landing.vercel.app/sourcea/` |

---

## P0 → P2 queue

| ID | Action | Owner |
|----|--------|-------|
| **VH-001** | Founder drops `SourceA-W1-Master.mov` · say **film** | Founder + Worker |
| **VH-002** | Ingest → grade A receipt · replace proof embed | Worker |
| **VH-003** | Republish Gate K + refresh AB1 packs with stable URL | Worker |
| **VH-004** | ElevenLabs VO (optional P1 after master) | Worker |
| **VH-005** | Deepgram word timestamps → Remotion captions (P2 scale) | Worker |
| **VH-006** | Runway abstract 5s hook only (P2 optional) | Defer |

---

## Related (do not supersede)

- `archive/attachments/2026-06-15/SOURCEA_HIGH_QUALITY_COMMERCIAL_VIDEO_RESEARCH_2026-06-15_v1.md`
- `archive/attachments/commercial/WITNESSBC_HERO_COMMERCIAL_TOP_TIER_PLAN_2026-06-15_v1.md`
- `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` — Vercel Hobby allowed
- `commercial-video-factory/` — `SHIP_BLOCKED_MOCK` on `TerminalMock` outbound
