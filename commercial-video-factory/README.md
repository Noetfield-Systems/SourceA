# Commercial Video Factory (Remotion)

Programmatic **JSON in → MP4 out** for per-prospect proof reels. Wired to `commercial-pipeline-v1.jsonl` and `proof-scenarios-v1.json`.

## Stack

- **Remotion 4** — React/TypeScript motion (9:16 · 30s default)
- **Python orchestrator** — `scripts/remotion_artifact_factory_v1.py`
- **Law:** proof fields from disk SSOT — company, scenario, receipt hash, proof URL

## Commands

```bash
# Structure gate
bash scripts/validate-remotion-artifact-factory-v1.sh

# Sample reel (installs npm deps on first run)
python3 scripts/remotion_artifact_factory_v1.py --sample --json

# From pipeline row
python3 scripts/remotion_artifact_factory_v1.py --row-id cp-XXXXXXXXXX --json

# From custom JSON
python3 scripts/remotion_artifact_factory_v1.py --input commercial-video-factory/data/sample-prospect-reel-v1.json

# Props only (no render)
python3 scripts/remotion_artifact_factory_v1.py --sample --dry-run --json

# Remotion studio (preview)
cd commercial-video-factory && npm run studio
```

## Output

| Artifact | Path |
|----------|------|
| MP4 | `~/.sina/commercial-videos-v1/{company-slug}-reel-v1.mp4` |
| Render props | `~/.sina/remotion-render-input-v1.json` |
| Receipt | `~/.sina/enforcement/remotion-artifact-factory-receipt-v1.json` |

## Input schema (`remotion-prospect-reel-v1`)

See `data/sample-prospect-reel-v1.json` — `company`, `hook`, `pain`, `proof_line`, `scenario`, `verdict`, `receipt_hash`, `proof_url`, `lane`, `brand`, `accent`.

## Deal Engine loop

```text
commercial_pipeline row (researched)
    → remotion_artifact_factory_v1.py
    → personalized 30s reel + proof_url
    → transition status personalized_sent
    → outbound attach (page + video + receipt)
```

Companion: `WITNESSBC_DEMO_VIDEO_100_UPGRADE_PLAN_2026-06-15_v1.md` · `w1_film_generate_v1.py` (72s real UI B-roll)
