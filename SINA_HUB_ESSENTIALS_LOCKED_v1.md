# Hub Essentials — locked unified map law

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Tab:** `essentials` in Sina Command

## Purpose

One **non-repetitive** index of everything important in the app. Home stays short; Essentials holds the full map.

## SSOT

- Builder: `scripts/hub_essentials_index.py`
- Payload key: `hub_essentials` in `command-data.json`
- API: `GET /api/hub-essentials`

## Roles (no overlap)

| Surface | Use for |
|---------|---------|
| **Home** | P0 hero, Track banner, compact mandatory reads, 8 quick tiles |
| **Essentials** | Full pillars + read chain + nav coverage — when lost |
| **Personal DB** | Layer A SSOT pillar — P0 training foundation |
| **Doc library** | Search all curated docs (deduped paths) |
| **Rules** | Edit markdown law files |
| **Sources** | Tier-1 quick edit only |

## Rules

1. New important tabs/apps/docs → add **once** in `hub_essentials_index.py` pillars (dedupe enforced).
2. Mandatory reads list **must not** diverge from `READ_CHAIN`.
3. Doc library sections skip paths already indexed (global dedupe).
4. `NAV_TABS` in `hub_essentials_index.py` must match sidebar `NAV` in `app.js`; build fails E2E if any tab is missing from pillars.
