# sa-0825 — /legacy/ quarantine banner vs H2 bookmark law cross-check

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15 · **Tier:** T0 · **Hub 2** `/machines/`

## Verdict (one line)

H2 `/api/machine-hub/v1` exposes `quarantine_bookmark_slice` — cross-checks legacy `#museum-readonly-banner` on `/legacy/` against H2 museum link and bookmark law (H1 daily · H2 heavy · legacy quarantine).

## Bookmark law

| Surface | URL | Daily bookmark? |
|---------|-----|-----------------|
| **H1 Super Fast Hub** | `/` | **Yes** — founder default |
| **H2 Machine Hub** | `/machines/` | **No** — heavy machines / maintainer |
| **Sina Command archive** | `/legacy/` | **No** — quarantined museum · READ ONLY |

## Cross-check contract

| Field | Rule |
|-------|------|
| **Payload key** | `quarantine_bookmark_slice` on machine-hub API |
| **Schema** | `h2-quarantine-bookmark-slice-v1` |
| **Legacy SSOT** | `GET /legacy/` → `#museum-readonly-banner` with `READ ONLY` text |
| **H2 museum href** | Must equal `legacy_url` (`/legacy/`) — not broken alias until maintainer ships `/oldhubsinacommand/` |
| **machine_hub legacy_url** | `/legacy/` on API row |
| **cross_check_ok** | H2 museum href == legacy_url AND legacy READ ONLY banner live |
| **Legacy frozen** | Do not edit Sina Command monolith for this sa — compare only |

## Required keys

`legacy_url` · `h2_museum_href` · `h1_daily_bookmark` · `h2_is_daily_bookmark` · `legacy_banner` · `cross_check_ok` · `display_line`

## UI surface

`/machines/index.html` renders `#quarantine-line` from `quarantine_bookmark_slice`.

## Machine proof

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash validate-h2-legacy-quarantine-banner-bookmark-v1.sh
bash validate-machines-banner-sibling-v1.sh
python3 machine_hub_v1.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['quarantine_bookmark_slice']['cross_check_ok']"
```

## Law

`SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md` slot **25** · `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §0 · `h2_quarantine_bookmark_slice_v1.py`

*End sa-0825*
