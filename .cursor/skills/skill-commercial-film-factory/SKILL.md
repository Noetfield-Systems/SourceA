---
name: skill-commercial-film-factory
description: >-
  Runs WitnessBC and SourceA commercial film hero renders, beats JSON, routing
  SSOT, validators, v4/v5 cinematic queue, and receipt paths. Use when the
  founder mentions commercial film, witnessbc-commercial-film, sourcea proof
  cut, beats JSON, film factory, or render_commands in routing SSOT.
---

# Commercial Film Factory

## When to use

- WitnessBC or SourceA hero / proof film render
- Beats JSON authoring or v4 → v5 cinematic upgrade
- Routing SSOT or factory phase questions
- Choosing between wrappers vs core compiler

## SSOT (read first)

| File | Role |
|------|------|
| `data/commercial-film-routing-v1.json` | Lane × tier · advisor ledger · render_commands |
| `data/commercial-film-factory-phases-v1.json` | Phase 0–5 roadmap |
| `data/COMMERCIAL_FILM_FACTORY_MASTER_PLAN_v1.md` | Unified plan |
| `data/commercial-film-render-rules-v1.json` | **R1–R8 render law** — one at a time, RAM, logs, checkpoint |
| `scripts/commercial_film_render_guard_v1.py` | acquire · release · status · finish · ram-check |

## Core vs wrapper

| Entry | Calls | Use when |
|-------|-------|----------|
| `witnessbc-commercial-film.sh` | Ensures :8090 Proof Lab · `witnessbc_commercial_film_v1.py` | Default WitnessBC hero |
| `sourcea-commercial-film.sh` | Ensures :5180 · `commercial_short_film_v1.py` | SourceA 32s W1 proof |
| `scripts/commercial_short_film_v1.py --beats …` | Direct compiler | Draft lanes (trustfield, noetfield) · custom beats |
| `scripts/witnessbc_commercial_film_v1.py --beats …` | Wrapper → core | Explicit beats path (v5 cinematic) |

**Rule:** One compiler (`commercial_short_film_v1.py`). Wrappers only ensure servers + default beats.

## Render law (mandatory — incident v4/v5)

```bash
python3 scripts/commercial_film_render_guard_v1.py machine-check --json  # Mac Guard RAM CPU GPU
python3 scripts/commercial_film_render_guard_v1.py status --json       # before ANY render
open http://127.0.0.1:13024/                                            # Mac Health Guard UI
bash witnessbc-commercial-film.sh --json                                # auto acquire + log + gate
```

| Rule | Law |
|------|-----|
| **R1** | ONE render globally — WitnessBC OR SourceA, never both |
| **R2–R14** | **Mac Guard machine gate** — RAM · CPU · disk · thermal/GPU · zombies · metrics log |
| **R3** | Full python log → `~/.sina/commercial-film-render-witnessbc.log` |
| **R4** | Checkpoint after concat → `finish` without re-capture |
| **R5** | Agents: `status --json` before start; never auto-restart running PID |
| **R6** | Separate work dirs per version (v1 vs v5 beats publish block) |
| **R7** | 4K polish ffmpeg timeout 3600s |
| **R8** | `--force` only if stale lock |

## Workflow — WitnessBC hero

```bash
cd ~/Desktop/Noetfield-Systems/SourceA

# 1. Validate routing
bash scripts/validate-commercial-film-routing-v1.sh

# 2. Proof Lab must respond
curl -sf http://127.0.0.1:8090/proof.html -o /dev/null

# 3. Render (default v1 beats)
bash witnessbc-commercial-film.sh --json

# 4. Cinematic v5 (explicit beats)
python3 scripts/witnessbc_commercial_film_v1.py \
  --beats data/witnessbc-commercial-film-beats-v5.json --json
```

**Beats files:**

| Version | Path | Notes |
|---------|------|-------|
| v1 (live) | `data/witnessbc-commercial-film-beats-v1.json` | linear_bar · chapter captions · no cinematic |
| v5 (queued) | `data/witnessbc-commercial-film-beats-v5.json` | `cinematic_finish + polish.sfx` |
| 30s social | `data/witnessbc-commercial-social-30s-beats-v1.json` | tier C · phase 2 |

## Workflow — SourceA proof cut

```bash
bash sourcea-commercial-film.sh --json
# Beats: data/commercial-short-film-beats-v1.json (cinematic + sync)
```

**Sync requirements (must PASS before publish):**

```bash
bash scripts/validate-commercial-film-sync-v1.sh --json
# Expects: hook/BLOCK/PROOF capture events w1_block · w1_tamper
```

**Sync patterns in beats JSON:**

- `hook_w1_sequence`: `[["allow", 1], ["block", 5]]` on `#w1-demo-film`
- `w1_sequence`: `[["block", 9]]` + `sync_offset_event: w1_block`
- `film_capture=1` on proof.html URLs (disables W1 auto-cycle)

Screen Studio fallback:

```bash
python3 scripts/sourcea_commercial_film_ingest_master_v1.py
# Input: ~/Desktop/SourceA-Commercial-Master.mov
```

## Receipts and outputs

| Lane | Desktop MP4 | Receipt |
|------|-------------|---------|
| WitnessBC | `~/Desktop/WitnessBC-Commercial.mp4` | `~/.sina/enforcement/witnessbc-commercial-film-receipt-v1.json` |
| WitnessBC v5 | `~/Desktop/WitnessBC-Commercial-v5.mp4` | `…-receipt-v5.json` |
| SourceA | `~/Desktop/SourceA-Commercial-Short.mp4` | `~/.sina/enforcement/commercial-short-film-receipt-v1.json` |

Work dirs: `~/.sina/witnessbc-commercial-film-work-v1/` (v5: `…-work-v5/`)

## v4 → v5 sequence

1. v4 extended runtime must complete (hook_broll · apad fix)
2. v5 beats already logged — flip `cinematic_finish: true`
3. Waiter: `~/.sina/witnessbc-commercial-v5-after-v4.sh` (if present)
4. Verify receipt + Desktop MP4 before marking routing `cinematic_finish_v5_queued: false`

## Do not

- Replace Playwright capture with HeyGen for WitnessBC tier A (Path A lock)
- Hand-edit MP4 as SSOT — change beats JSON + re-render
- Treat Remotion (`commercial-video-factory/`) as hero capture replacement
- Skip `validate-commercial-film-routing-v1.sh` before routing SSOT edits

## Related skills

- `skill-cinematic-finish-v1` — v5 flags and SFX patterns
- `skill-commercial-film-routing` — tier adjudication
- `skill-avatar-heygen-factory` — tier C human layer only
- `skill-cinematic-orchestration` — Phase 3–5 n8n · memory · distribution
- `skill-founder-identity-layers` — human vs product per ICP
