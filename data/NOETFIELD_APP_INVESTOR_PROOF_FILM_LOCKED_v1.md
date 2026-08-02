# Noetfield App Investor Proof Film — LOCKED v1

**Status:** LOCKED · **Date:** 2026-07-25 · **Authority:** ASF  
**Machine SSOT:** `data/noetfield-app-investor-proof-film-beats-v1.json`  
**Routing:** `data/commercial-film-routing-v1.json` → `lanes.noetfield.assets.tier_B_app_investor_proof`  
**Entry:** `bash noetfield-app-investor-proof-film.sh`  
**Pack:** `NOETFIELD-RUNWAY/sites/company-new/docs/investor-proof-pack.md`

---

## Verdict

This film proves the **live Company New loop** on [app.noetfield.com](https://app.noetfield.com/), not category parity with Replit / Lovable / Atoms.

**Lead claim (locked):**

> Working client-zero governed AI software factory: authorized goal → structured execution → quality gate → revisioned artifact → inspectable receipt. Raising to industrialize full-stack delivery assurance.

---

## Artifact class

| Field | Value |
|-------|--------|
| Doctrine class | `D_proof_lab` |
| Routing tier | `B_proof` |
| Runtime | ~90–120s |
| Voice | ElevenLabs via `scripts/film_elevenlabs_wire_v1.py` (`vo_lane` = sourcea cache) |
| Picture | Real product UI — Playwright and/or Screen Studio 4K master |
| Quality bar | `data/video-quality-bar-v1.json` (crisp UI, no Ken Burns blur, pro VO) |

**Forbidden lanes for this cut:** Fal / video-ad-factory generative ads · HeyGen avatar hero · expired `*.trycloudflare.com` B-roll.

---

## Pipeline (locked)

```text
classify (D_proof_lab)
  → beats JSON (this lock)
  → capture (Screen Studio preferred · Playwright secondary)
  → ElevenLabs VO + alignment
  → compose / polish to 4K
  → qualify (quality bar · critic when unfrozen)
  → deliver ~/Desktop/Noetfield-App-Investor-Proof.mp4
  → receipt ~/.sina/enforcement/noetfield-app-investor-proof-film-receipt-v1.json
```

### Preferred capture

1. Seed a clean workspace on production (New workspace).  
2. Record **4K** in Screen Studio following beats OPEN → GOAL → GATE → REVISION → CLINIC → RECEIPT → CTA.  
3. Export master to Desktop:  
   `Noetfield-App-Investor-Proof-Master.mov` or `.mp4`  
4. Run factory / ingest polish + ElevenLabs VO from beats.

### Secondary capture

Playwright via `commercial_short_film_v1.py --beats data/noetfield-app-investor-proof-film-beats-v1.json --product noetfield` when an authenticated session is available for cockpit URLs.

---

## Beat sheet (locked)

| ID | On screen | VO gist |
|----|-----------|---------|
| OPEN | app.noetfield.com | Client-zero governed factory |
| GOAL | New workspace / Front Person | Authorized goal · team roles move |
| GATE | Website Preview Ready | Quality gate · H1 is product copy, not prompt |
| REVISION | Revision / Preview | Inspectable revisioned artifact |
| CLINIC | Clinic Desk compile path | Auth · roles · appointments · audit |
| RECEIPT | `/v1/receipt` or receipt UI | Checks on disk |
| CTA | app.noetfield.com | Industrialize delivery assurance |

---

## Honest gaps (must remain in VO or end card if spoken)

- Injected defect → automatic bounded repair → requalify is **not** automated.  
- Outbound email/SMS are in-app notification stubs only.  
- No Replit / Lovable / Atoms parity claim.

---

## Commands

```bash
cd ~/Desktop/SourceA
bash scripts/validate-commercial-film-routing-v1.sh
bash noetfield-app-investor-proof-film.sh --json
# optional: --force if render guard frozen; founder only
```

ElevenLabs vault: `~/.sina/elevenlabs-v1.env`

---

## Change control

Do not edit this lock to soften the claim or add competitor-parity language.  
New cuts = new beats version (`v2`) + routing entry — do not silently mutate v1.
