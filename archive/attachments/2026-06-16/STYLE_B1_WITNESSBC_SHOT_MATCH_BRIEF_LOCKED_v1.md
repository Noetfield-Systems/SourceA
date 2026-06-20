# STYLE-B1 — WitnessBC ~3m Hero Shot Match Brief (LOCKED)

**Saved:** 2026-06-16T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Schema:** `style-shot-match-brief-v1`  
**Locked:** 2026-06-16  
**Founder pick:** `3PICKS` pick #2 — **STYLE-B1 yes**  
**Reference:** [Vanta 3-min demo](https://www.youtube.com/watch?v=m6RPjjuLjJA) (P-020)  
**Craft bar:** STYLE-A5 — `~/Downloads/LinearH264Version_1 (6).mp4` · `data/video-quality-bar-v1.json`  
**Beats SSOT:** `data/witnessbc-commercial-film-beats-v1.json`  
**Routing:** `data/commercial-film-routing-v1.json#witnessbc.tier_A_hero`  
**Parent:** `archive/attachments/2026-06-16/CINEMATIC_REFERENCE_3PICKS_LOCKED_MASTER_v1.md`

---

## 1. What we clone (Vanta — not inventing)

| Dimension | Vanta reference | Steal for WitnessBC |
|-----------|-----------------|---------------------|
| **Length** | ~3:22 | **~180s** institutional tour |
| **Hook** | Compliance saves time/cost | Policy at dispatch — before irreversible runs |
| **Structure** | Dashboard → controls → evidence → policies → monitoring → trust | Proof Lab arc — same buyer logic |
| **Pacing** | Calm · UI readable · 5–10s per major surface | **6–10s dwell** on proof moments |
| **VO** | Pro institutional narrator | ElevenLabs structural · no hype |
| **Capture** | Real product screen tour | Screen Studio 4K · real `:8090` UI |
| **Sound-off** | Works with on-screen labels | Chapter captions + burned key lines |

**Reject:** HeyGen avatar · Playwright bot scroll · six unrelated hooks · consumer TikTok framing.

---

## 2. Beat sheet (0–180s)

**Aspect:** 16:9 · **3840×2160** master · **STYLE-A5** cursor motion

| Sec | Shot | Surface | Zoom | Dwell | Caption |
|-----|------|---------|------|-------|---------|
| 0–15 | Establish Proof Lab | `proof.html` hero | 1.0× | 5s | Policy at dispatch. |
| 15–45 | Control plane | ALLOW · BLOCK · ESCALATE rail | 1.2× | 8s | Govern before execution. |
| 45–90 | Receipt / spine | Terminal + receipt lines | 1.4× | 10s | Receipt on disk. |
| 90–120 | Tamper FAIL | Hash mismatch live | 1.5× | 10s | Tamper caught. Audit preserved. |
| 120–150 | Policy rows | Governance table / compare | 1.25× | 8s | Continuous proof. |
| 150–165 | Queue / status | Factory-now or enforcement queue | 1.2× | 8s | Always audit-ready. |
| 165–180 | CTA | pricing / book proof | 1.1× | 5s | Book 15 minutes · witnessbc.com |

---

## 3. URLs (record these)

| Surface | URL |
|---------|-----|
| Primary | `http://127.0.0.1:8090/proof.html` |
| Scenario | `http://127.0.0.1:8090/proof.html#scenario=outbound` |
| Compare / pricing | `http://127.0.0.1:8090/compare.html` · `pricing.html` |

Start WitnessBC site server before record (per `witnessbc-site` serve recipe).

---

## 4. Screen Studio capture

| Setting | Value |
|---------|-------|
| Resolution | 4K master |
| Cursor | Smooth · hover 0.5s before click |
| Zoom | Manual timeline per §2 |
| Audio | Record silent — VO in ingest |
| Export | `~/Desktop/WitnessBC-Commercial-Master.mov` |

**After record:** `bash witnessbc-commercial-film-ship.sh` or ingest master script → critic vs **STYLE-B1** + **STYLE-A5**.

---

## 5. Acceptance checklist

- [ ] ~180s · institutional pace (not 32s Vercel arc)
- [ ] Dashboard/control beats dwell ≥6s
- [ ] Tamper/hash legible ≥5s
- [ ] Motion matches Linear disk bar (A5)
- [ ] Critic PASS vs B1 pick
- [ ] Ship gate `publish_allowed` YES

---

**END LOCKED BRIEF**
