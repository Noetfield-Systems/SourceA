# WitnessBC Hero Commercial — Top Tier Only Plan

**Saved:** 2026-06-15T21:32:29Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Lane:** Witness AI (`witnessbc.com`) only  
**Law:** No trash hero · no fake terminal · no SourceA branding on WBC outbound

---

## What “top tier” means (2026 market)

From Thinkmojo, Demo Duck, Vidico, 7 Hills, VideoPulse, Screenify (June 2026 research):

| Weak (never ship as hero) | Top tier (ship) |
|---------------------------|-----------------|
| CSS motion-graphics-only “terminal” | **Real product UI** — cursor-aware, 1080p+ |
| macOS `say` / robotic VO | **ElevenLabs** or pro VO + treated room |
| 720p / &lt;2MB compressed mush | **6–12 Mbps H.264** · 1080p master · ~8–15MB for 60–90s |
| Static slides + stock music | **Mixed media** — title card + UI + proof beat |
| Feature dump | **One pain → one proof moment → CTA** |
| No tamper story | **Mandatory tamper-FAIL beat** on screen |
| Same cut for everyone | Hero master + 9:16 / 30s variants *after* hero exists |

**Agency benchmark:** Thinkmojo / Demo Duck hero films = **$15K–$150K**, 8–12 weeks, UI-led storytelling. Our disk pipeline targets **same structure**, automated capture from Proof Lab.

---

## Three tiers — use the right one

| Tier | Tool | Output | When |
|------|------|--------|------|
| **A — Hero commercial** | `witnessbc_commercial_film_v1.py` | 72s · 1080p · real `:8090` UI | Website · outbound · diligence |
| **B — Proof embed** | Same pipeline → `w1-demo.mp4` | Proof page `#w1-demo-film` | Always paired with Tier A |
| **C — Volume personalized** | Remotion (later) | 30s per pipeline row | *Only after Tier A approved* |

**VOID:** Remotion-only hero · w1_film 944KB quick cut · SourceA `:5180` captures for WitnessBC brand.

---

## WitnessBC hero spec (locked)

- **Runtime:** 72s master · 30s social cut · 15s hook GIF (from same master)
- **Resolution:** 1920×1080 · CRF 18–20 · **target 8–12 Mbps**
- **Capture:** Playwright `:8090` — home · Proof Lab · `#scenario=tamper` · pricing
- **Beats SSOT:** `data/witnessbc-commercial-film-beats-v1.json`
- **VO:** ElevenLabs (`ELEVENLABS_API_KEY` in `~/.sina/secrets.env`) — fallback macOS say only for dev
- **Captions:** Burned-in SRT from narration
- **Proof beats (mandatory on camera):** BLOCK · ESCALATE · tamper-FAIL · signed receipt hash visible

---

## Pro production checklist (from enterprise guides)

1. Browser zoom 125–150% before capture (legible text)
2. High-contrast cursor · deliberate moves · no jitter scroll
3. Synthetic demo data only · receipt hashes from `proof-scenarios-v1.json`
4. Hook in first 3 seconds (silent-autoplay safe)
5. Export H.264 MP4 · AAC 160–256 kbps · constant frame rate
6. Deliverables: 16:9 master · 9:16 cut · poster frame · SRT sidecar
7. QC: watch on phone + laptop — text readable · tamper beat unmistakable

### Linear orientation video (reference — steal structure, not SourceA)

**Source:** [Linear Learn — Intro to Linear](https://linear.app/learn/intro-to-linear) (~3:23 chapters)

| Linear chapter | WitnessBC commercial beat |
|----------------|---------------------------|
| 00:00 Introduction | Hook — problem in 5s (agents act before policy) |
| 00:11 Key features | Control plane LIVE — ALLOW/BLOCK/ESCALATE |
| 00:48 Set-up | Proof Lab — pick scenario |
| 01:24 Issues | Outbound / tool call — receipt terminal |
| 02:01 Projects | Governance loop · 6 gates |
| 03:23 Initiatives | Pricing + CTA — Book 15-min proof |

**Linear rules for WitnessBC film:**
- Product IS the video — no fake terminal, no title-card-only hero
- Speed visible on screen — snappy cuts, keyboard/click deliberate
- Structured chapters — viewer can scrub to proof beat
- Minimal narration — show tamper-FAIL, don't explain it in slides
- Dark, crisp UI — match `:8090` Proof Lab, not Remotion gradients

---

## Deploy (no paid Cloudflare)

```bash
python3 scripts/publish_witnessbc_landing_v1.py --backend tunnel
python3 scripts/publish_witnessbc_landing_v1.py --backend local
```

Local: http://127.0.0.1:8090/ · Desktop note: `WitnessBC-Landing-URL.txt`

**Avoid:** `--wrangler` / paid Cloudflare Pages unless founder explicitly opts in.

---

```bash
# Ensure Proof Lab live
bash ~/Desktop/SourceA/witnessbc-site/scripts/run-recipe.sh --serve

# Hero commercial (1080p real UI)
bash ~/Desktop/SourceA/witnessbc-commercial-film.sh --json

# Watch
open ~/Desktop/WitnessBC-Commercial.mp4
open http://127.0.0.1:8090/proof.html#w1-demo-film
```

**Receipt:** `~/.sina/enforcement/witnessbc-commercial-film-receipt-v1.json`

---

## Next upgrades (P0 → P1)

| # | Upgrade | Inspo | Effort |
|---|---------|-------|--------|
| 1 | ElevenLabs VO on every render | Demo Duck “don’t feel cheap” | S |
| 2 | Capture at 125% zoom + cursor highlight | Screenify / VideoPulse | M |
| 3 | Auto 9:16 + 30s cut from master | Thinkmojo multi-format | M |
| 4 | Screen Studio-style zoom in post | Thinkmojo UI-led | L |
| 5 | Replace Remotion hero path — volume only | Gemini programmatic | — |

---

## Reference agencies (research only — not on customer pages)

Thinkmojo · Demo Duck · Vidico · Sandwich Video · 7 Hills Mixed Media · Black Camel (deep tech)

Companion: `WITNESSBC_DEMO_VIDEO_100_UPGRADE_PLAN_2026-06-15_v1.md`
