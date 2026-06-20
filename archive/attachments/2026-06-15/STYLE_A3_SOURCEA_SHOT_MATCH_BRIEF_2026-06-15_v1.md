# STYLE-A3 — SourceA 32s Hero Shot Match Brief

**Schema:** `style-shot-match-brief-v1`  
**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:57:49Z  
**Founder pick:** `STYLE-A3 yes` — SourceA 32s commercial hero  
**Reference:** P-007 / STYLE-A3 — [Vercel homepage deploy moment](https://vercel.com/) (~30s · homepage embed)  
**Craft bar:** P-005 — Linear 4K motion (`LinearH264Version_1 (6).mp4`)  
**Beats SSOT:** `data/commercial-short-film-beats-v1.json`  
**Routing:** `data/commercial-film-routing-v1.json#sourcea.tier_B_proof_32s`

---

## 1. What we are cloning (Vercel P-007 — not inventing)

| Dimension | Vercel reference | Steal for SourceA |
|-----------|------------------|-------------------|
| **Length** | ~30s loop on homepage | **32s** master (one loop · no chapters) |
| **Narrative** | ONE aha: **push → deploy → live** | ONE aha: **intent → gate → BLOCK → tamper proof on disk** |
| **Structure** | Single continuous arc — no chapter cards | Same — **no** six-beat WitnessBC tour |
| **Pacing** | Visual change ~every 3s · status UI readable | Tab/beat switch + terminal lines · ~3s per state |
| **Capture** | Real product UI (dashboard / deploy logs) | Real W1 player on Proof Lab — not mock terminal |
| **VO** | Minimal or none — UI labels carry meaning | Structural VO optional · **burned captions required** |
| **Sound-off** | Works muted — status text + kinetic type | BLOCK / tamper-FAIL labels + caption burn |
| **Embed** | Autoplay `muted loop playsinline` hero | 16:9 embed on `index.html` commercial-short slot |
| **Motion** | Command-center context switch (repo → build → URL) | W1 rail: ALLOW context → BLOCK → TAMPER → hold |

**Reject as substitute:** Playwright factory scroll · typography-only reel · multi-chapter commercial · logo cold open · HeyGen face.

---

## 2. SourceA “one moment” mapping

| Vercel beat | SourceA equivalent | Proof surface |
|-------------|-------------------|---------------|
| Developer **pushes** code | Agent **attempts** governed action (ops / cross-lane) | W1 terminal `sourcea-boot --json` |
| Vercel **detects** commit · build starts | Session gate **evaluates** receipt freshness | `[FAIL] receipt_fresh: last receipt verdict BLOCK` |
| Build log ~**27–30s** tension | **BLOCK** dwell — gate refuses · **no file touched** | Beat label `BLOCK` · subtitle on player |
| Deployment **ready** · preview URL | **Tamper FAIL** — hash mismatch caught live | `[FAIL] tamper_detect: hash mismatch` |
| **Live** on edge network | **Audit preserved** — replay can find verdict tomorrow | Progress rail complete · CTA |

---

## 3. URLs & surfaces (record these)

### Local capture (Screen Studio — preferred)

| Surface | URL | Notes |
|---------|-----|-------|
| **Primary record** | `http://127.0.0.1:5180/sourcea/proof.html?film_capture=1#w1-demo-film` | `film_capture=1` stops auto-rotate · use beat tabs or console |
| **Landing embed target** | `http://127.0.0.1:5180/sourcea/` → `#sourcea-films` | After master ships · replace `commercial-short-demo.mp4` |
| **Optional CTA end card** | `http://127.0.0.1:5180/sourcea/#reference` | Only if 2s hold needs homepage context |

Start landing server before record:

```bash
cd ~/Desktop/SourceA && python3 scripts/publish_sourcea_landing_v1.py --serve --port 5180
```

### Production (buyer-facing · verify after deploy)

| Surface | URL |
|---------|-----|
| Proof Lab W1 | `https://sourcea-landing.vercel.app/sourcea/proof.html#w1-demo-film` |
| Homepage films | `https://sourcea-landing.vercel.app/sourcea/#sourcea-films` |
| Domain (beats CTA) | `sourcea.com/sourcea` |

**WitnessBC Proof Lab (`:8090`)** — not this hero. SourceA lane only.

### W1 beat control during capture

With `film_capture=1`, player does not auto-cycle. Switch beats:

- Click rail buttons: `ALLOW` · `BLOCK` · `TAMPER`
- Or DevTools console: `__saW1FilmBeat('block')` · `__saW1FilmBeat('tamper')`

Beat definitions: `SourceA-landing/green-unified/sourcea-w1-player.js`.

---

## 4. Second-by-second beat sheet (0–32s)

**Aspect:** 16:9 · **2560×1440** capture → **3840×2160** master ingest  
**Cuts:** Hard cuts on beat change (Vercel-style) — no dissolves  
**Cursor:** Screen Studio smooth · **slow hover 0.5s before click**

| Sec | Shot | UI / action | Zoom | Dwell | Caption (burn) |
|-----|------|-------------|------|-------|----------------|
| **0.0–2.0** | Establish W1 section | Already scrolled to `#w1-demo-film` · player on **ALLOW** or neutral first frame | 1.0× full player | 2s | `Prove every agent move.` |
| **2.0–5.0** | Context switch (Vercel: open repo) | Cursor hovers **BLOCK** tab on W1 rail · click | 1.15× on rail | 3s | `Policy before dispatch.` |
| **5.0–9.0** | Action initiated (Vercel: git push) | **BLOCK** state: label red · title “Receipt not fresh” | 1.35× on beat label + title | 4s | `Execution stopped.` |
| **9.0–13.0** | System processing (Vercel: build log) | Terminal: `[FAIL] receipt_fresh: last receipt verdict BLOCK` | 1.5× on `[FAIL]` line | **4s dwell** | `BLOCK — pre-LLM. No file touched.` |
| **13.0–16.0** | Transition | Cursor to **TAMPER** tab · click (hard cut) | 1.2× follow cursor | 3s | `Receipt on disk.` |
| **16.0–21.0** | Proof moment (Vercel: build success) | **TAMPER** label · “Hash mismatch caught” | 1.4× on label | 5s | `Tamper FAIL.` |
| **21.0–26.0** | Live payoff (Vercel: live URL) | Terminal tamper lines + hash `expected sha256=… · got sha256=deadbeef` | 1.55× on hash mismatch | **5s dwell** | `Audit preserved. Replay tomorrow.` |
| **26.0–29.0** | Pull back | Zoom out to full W1 player · progress rail shows BLOCK+TAMPER done | 1.0× | 3s | `SourceA · governed automation` |
| **29.0–32.0** | CTA hold (Vercel: loop point) | Hold on **Play full scenario** or **Book screen-share** CTA · no new clicks | 1.1× on primary CTA | 3s | `Book 15 minutes · sourcea.com` |

**Total:** 32.0s · **one arc** · **3 hard cuts** (establish → BLOCK → TAMPER → CTA).

---

## 5. Screen Studio capture instructions

### Before record

1. **Display:** 2560×1440 or 4K · browser zoom **100%** · hide bookmarks bar.
2. **Server:** `:5180` landing live · hard refresh `proof.html?film_capture=1#w1-demo-film`.
3. **Window:** Chrome · only Proof Lab tab · crop to content (no macOS menu bar if possible).
4. **Audio:** Record **silent** — VO added in ingest (`film_elevenlabs_wire_v1.py`).
5. **Do not** run Playwright commercial factory during record.

### Screen Studio settings

| Setting | Value |
|---------|-------|
| Resolution | 4K if available · else 2560×1440 |
| Cursor | Smooth · visible · click highlights |
| Zoom | Manual timeline aligned to §4 (1.35–1.55× on terminal) |
| Padding | 0 or minimal — Vercel shows full UI, not floating PIP |
| Export | `.mov` master → `~/Desktop/SourceA-Commercial-Master.mov` |

### Performance targets (Linear / P-005 bar)

| Metric | Target |
|--------|--------|
| Bitrate (4K master) | ≥ 3000 kbps (quality bar) |
| Motion | Human-smooth scroll · no bot-speed pan |
| Readability | Every `[FAIL]` line legible for **≥3s** at 1080p downscale |

### After record — ingest only (no re-render from Playwright)

```bash
cd ~/Desktop/SourceA && python3 scripts/sourcea_commercial_film_ingest_master_v1.py --json
```

Optional VO + captions from beats file via factory polish chain.

---

## 6. VO script (minimal structural — ElevenLabs)

**Lane:** `sourcea` · **Voice:** `en-US-AndrewMultilingualNeural` (beats polish)  
**Pacing:** ~2.5 words/sec · **total VO ≤28s** · leave 2s CTA silence optional

### Option A — Structural VO (recommended for homepage embed)

| Sec | Line |
|-----|------|
| 0–4 | Your agents execute right now. Who stops the one that goes too far? |
| 4–10 | Policy violated. Execution stopped. No file touched. |
| 10–16 | The gate returns BLOCK — pre-LLM, not prompt hope. |
| 16–22 | Alter a receipt hash. Tamper FAIL is immediate. |
| 22–28 | Receipt generated. Audit preserved. |
| 28–32 | SourceA. Book fifteen minutes. *(or silence + caption only)* |

### Option B — UI-only (Figma / STYLE-A4 hybrid)

- No VO · music bed optional (low · `-18 LUFS` under UI)
- **Mandatory:** burned captions from §4 table
- SFX: subtle UI click on tab switches only (`polish.sfx` light)

---

## 7. Captions (sound-off — mandatory)

- **Mode:** `full` burn (not chapter-only)
- **Style:** Bottom third · high contrast · 2 lines max · match `sourcea.css` mono for terminal quotes
- **LinkedIn derivative:** same caption file · 30–60s organic rule (L-009)

| Time | Caption |
|------|---------|
| 0.0–2.0 | Prove every agent move. |
| 2.0–5.0 | Policy before dispatch. |
| 5.0–9.0 | Execution stopped. |
| 9.0–13.0 | BLOCK — pre-LLM. No file touched. |
| 13.0–16.0 | Receipt on disk. |
| 16.0–21.0 | Tamper FAIL. |
| 21.0–26.0 | Audit preserved. Replay tomorrow. |
| 26.0–29.0 | SourceA · governed automation |
| 29.0–32.0 | Book 15 minutes · sourcea.com |

---

## 8. Homepage embed (post-ingest)

Replace site asset (when critic PASS):

- **File:** `SourceA-landing/green-unified/assets/commercial-short-demo.mp4`
- **Poster:** `commercial-short-poster.svg` (existing)
- **Embed:** `index.html` `#sourcea-films` — first film card (~32s not ~75s)
- **Attributes:** `controls preload="metadata" playsinline` (click for sound — Vercel uses autoplay on hero; landing card stays click-to-play unless founder adds hero loop)

Update card copy from “~75s” to “~32s · one moment proof”.

---

## 9. What NOT to do

| Do not | Why |
|--------|-----|
| `bash sourcea-commercial-film.sh` Playwright capture | Tier C motion · critic blocked public ship |
| Six-beat WitnessBC chapter structure | STYLE-A3 = **one moment** only |
| Logo wall cold open / TRUST montage | Vercel opens mid-action · not brand slate |
| Record full `scenario.html` tour | Multi-chapter bloat |
| WitnessBC `:8090` Proof Lab for this slot | Wrong lane — SourceA `:5180` |
| HeyGen / avatar hook | Path A lock · trust product led |
| Ken Burns on screenshots | Vercel = crisp UI pixels |
| Fake terminal / Remotion mock | Real W1 player only |
| Ship without Screen Studio master | Factory ingest path is the gate |

---

## 10. Acceptance checklist

- [ ] Single arc 28–32s · ≤3 hard cuts
- [ ] BLOCK `[FAIL]` legible ≥4s
- [ ] Tamper hash mismatch legible ≥5s
- [ ] Captions burned · sound-off comprehensible
- [ ] 4K master ≥3000 kbps · audio present post-ingest
- [ ] Critic circle PASS after ingest
- [ ] `commercial-short-demo.mp4` on disk matches master

---

## 11. Related files

| Path | Role |
|------|------|
| `data/commercial-short-film-beats-v1.json` | Runtime · VO lines · capture URLs |
| `data/reference-board-v1.json` | STYLE-A3 founder pick |
| `archive/attachments/2026-06-15/VIDEO_REFERENCE_CATALOG_FULL_2026-06-15_v1.md` | P-007 catalog row |
| `scripts/sourcea_commercial_film_ingest_master_v1.py` | Ingest master → polish |
| `data/video-quality-bar-v1.json` | Bitrate / tier gate |

---

**Next tap (founder):** Record Screen Studio against `http://127.0.0.1:5180/sourcea/proof.html?film_capture=1#w1-demo-film` → save `~/Desktop/SourceA-Commercial-Master.mov` → say **ingest**.
