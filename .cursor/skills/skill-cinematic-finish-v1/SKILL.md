---
name: skill-cinematic-finish-v1
description: >-
  Applies cinematic_finish flags, polish.sfx, _cinematic_vf dark frames, logo
  wall, tamper dwell, and beats JSON patterns from the SourceA proof cut. Use
  when upgrading WitnessBC v5, SFX mix, dark-framed UI, BLOCK dwell, or
  comparing cinematic vs linear_bar film styles.
---

# Cinematic Finish v1

## When to use

- WitnessBC v5 cinematic upgrade
- Enabling SFX under VO (`_mix_vo_sfx`)
- Logo wall TRUST beat · tamper dwell · dark frame composite
- Copying patterns from SourceA proof cut to other lanes

## Enable in beats JSON

```json
{
  "cinematic_finish": true,
  "polish": {
    "sfx": true,
    "cinematic_finish": true,
    "target_bitrate_mbps": 18,
    "master_lufs": -14
  }
}
```

Top-level `cinematic_finish: true` may also appear (witnessbc v5 has both).

## Code map (`commercial_short_film_v1.py`)

| Feature | Function | Trigger |
|---------|----------|---------|
| Dark-framed UI | `_cinematic_vf()` · `_apply_cinematic_frame()` | `cinematic_finish: true` on broll |
| SFX under VO | `_mix_vo_sfx()` | `polish.sfx: true` |
| Logo wall PNG | `_built_on_wall_png()` | TRUST beat · brand config |
| Tamper dwell | `tamper_dwell_seconds` on beat | Playwright interact hold |
| BLOCK red border | `_cinematic_vf(beat_id="BLOCK")` | w1 block sequence |
| 4K master | `global_capture.master_width/height` | 3840×2160 |
| Extended broll | mux apad after VO ends | v4+ extended runtime |

## Reference cuts

| Cut | File | cinematic_finish |
|-----|------|------------------|
| SourceA proof (LIVE) | `data/commercial-short-film-beats-v1.json` | **true** — copy this |
| WitnessBC v1 (linear) | `data/witnessbc-commercial-film-beats-v1.json` | false |
| WitnessBC v5 (queued) | `data/witnessbc-commercial-film-beats-v5.json` | **true** |

## SourceA proof patterns to reuse

From `commercial-short-film-beats-v1.json`:

- **Outcome VO:** "Policy violated. Execution stopped." / "Tamper FAIL"
- **w1_sequence:** `[["block", 9]]` · `[["tamper", 9]]` with `sync_offset_event`
- **TRUST beat:** logo wall narration + short broll
- **film_style:** `linear_orientation_hero` · `proof_density: true`
- **hook_w1_sequence:** `[["allow", 1], ["block", 5]]`

## WitnessBC v5 patterns

From `witnessbc-commercial-film-beats-v5.json`:

- Six beats: CONTROL · SETUP · ISSUES · GOVERNANCE · TAMPER · PRICING
- `tamper_dwell_seconds: 9.5` on TAMPER beat
- `captions_mode: chapter_only` · `film_style: linear_bar`
- `hook_broll_seconds: 24` · extended per-beat broll

## Workflow — flip v1 → v5

```bash
cd ~/Desktop/Noetfield-Systems/SourceA

# Diff beats (v5 derived from v1 + cinematic flags)
diff <(python3 -c "import json;print(json.dumps(json.load(open('data/witnessbc-commercial-film-beats-v1.json'))['polish'],indent=2))") \
     <(python3 -c "import json;print(json.dumps(json.load(open('data/witnessbc-commercial-film-beats-v5.json'))['polish'],indent=2))")

# Render v5 (Proof Lab :8090 required)
python3 scripts/witnessbc_commercial_film_v1.py \
  --beats data/witnessbc-commercial-film-beats-v5.json --json
```

## Visual rules (Path A)

| Moment | Rule |
|--------|------|
| BLOCK | Red-tinted dark frame · 5–8s hold · SFX sting |
| TAMPER | 9.5s dwell on tamper-FAIL UI |
| TRUST / Built-on | Logo wall — "technology dependencies, not co-marketing" |
| General UI | Dark margin pad · contrast +4% · crisp product-led |

## Rejected copy (WitnessBC lane)

Do not use on witnessbc tier A:

- Gemini enterprise jargon · Certainty Report™ · Noetfield branding in VO
- Consumer TikTok framing as institutional hero

## Do not

- Enable HeyGen avatar inside cinematic_finish path for WitnessBC tier A
- Set `cinematic_finish` without Proof Lab live capture (empty broll)
- Skip audio check — SFX mix requires VO wav from ElevenLabs or edge fallback
- Hand-grade in external NLE as SSOT — change beats + re-render

## Related

- `skill-commercial-film-factory` — render entrypoints
- `data/COMMERCIAL_FILM_FACTORY_MASTER_PLAN_v1.md` § Cinematic finish rules
