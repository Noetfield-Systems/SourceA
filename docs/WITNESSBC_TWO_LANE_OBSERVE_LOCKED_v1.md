# WitnessBC two-lane Observe — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-21T02:30:00Z · **Authority:** ASF  
**Path:** `docs/WITNESSBC_TWO_LANE_OBSERVE_LOCKED_v1.md`  
**Machine SSOT:** `data/witnessbc-two-lane-observe-v1.json`

---

## One law

**One domain · two lanes.**

| Lane | Job | Home |
|------|-----|------|
| **Commercial** | Sell & prove Witness AI | `/` |
| **Observe** | Witness & narrate AI policy truth | `/observe/` |

> **Witness** = observer of truth in society. **We observe and narrate.**

---

## Commercial lane

- Witness AI product — platform, proof, pricing, Stripe
- Toolkits — education + Pro PDF (commercial v12 shell)
- Buyers: CISO, GRC, platform eng, AI policy ops

---

## Observe lane

Specialized journalism desk on **AI policy**, **governance**, and **agentic startups**.

| Path | Purpose |
|------|---------|
| `/observe/` | Feed — policy · governance · startups |
| `/observe/principles/` | Editorial standards (AI policy reporting) |
| `/observe/corrections/` | Visible corrections log + request form |

**Not** general BC civic journalism at `/` — that positioning is retired. Archive: `archive/witnessbc-journalism-clone-v1/`.

---

## Legacy redirects (prod cutover)

| Old | New |
|-----|-----|
| `/principles/` | `/observe/principles/` |
| `/corrections/` | `/observe/corrections/` |
| `/stories/` | `/observe/` |

---

## Cross-links

- Commercial footer + Resources → Observe
- Observe header → Witness AI platform (`/`)
- Toolkits bridge both lanes — no duplicate old journalism `/toolkits/` shell on prod

---

## Build

```bash
bash witnessbc-site/scripts/run-recipe.sh
bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --skip-recipe
```

Renderer: `scripts/render_observe_v1.py` · Feed SSOT: `data/observe-feed-v1.json`
