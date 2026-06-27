---
lane: core
updated: 2026-06-27T05:30:00Z
source_path: sites/SourceA-landing/green-unified/
public: true
---

# SourceA public site map

## Primary routes (sourcea.app)

| Path | Purpose | Lane |
|------|---------|------|
| `/` | Home — execution-first hero | buyer |
| `/sourcea/offer` | 48-hour MVP offer | buyer |
| `/sourcea/pricing` | Build · Rent · Own pricing | buyer |
| `/sourcea/forge/terminal` | Forge Terminal public demo | developer |
| `/sourcea/forge/` | Forge hub — tools, how-it-works | developer |
| `/sourcea/proof/live` | Live receipt demo | buyer |
| `/sourcea/sandbox` | Free sandbox / intake | buyer |
| `/sourcea/investors` | Investor lane | investor |
| `/sourcea/kernel/` | Kernel overview | developer |
| `/sourcea/platform` | Platform portal sign-in | developer |
| `/sourcea/scenario` | Brain scenario page | buyer |
| `/eval` | Technical overview for developers | developer |

## API hosts (public-safe mentions only)

| Host | Role |
|------|------|
| `sourcea.app` | Public www + `/api/brain/chat/v1` proxy |
| Cloudflare Worker | Brain chat OpenRouter proxy (key never in browser) |
| Hub `:13020` | Mac control panel (founder session — not stranger-facing) |

## Brain widget

Loaded via `sourcea-chatbot.js` on landing pages. Posts to same-origin `/api/brain/chat/v1`.
