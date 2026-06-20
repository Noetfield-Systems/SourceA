# Two-Hub Sibling Model — Advisor note (2026-06-14)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Authority:** ASF question — “H2 feels like a sub-page of H1”  
**Law:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` §0 — H1 and H2 are **siblings**, not layers.

## Advisor verdict

**You already have two hubs, not one hub with two tabs.** Same port (`13020`) is deployment convenience — not the same product surface.

| | H1 Super Fast | H2 Machine |
|---|---------------|------------|
| **URL** | `/` | `/machines/` |
| **HTML shell** | `worker-hub/index.html` (~4 KB API) | `machines/index.html` (~5.7 KB API) |
| **API** | `/api/worker-hub/v1` | `/api/machine-hub/v1` |
| **Loads 9MB monolith?** | **Never** | **Never** |
| **Cadence** | Daily | Weekly / scheduled |
| **Founder bookmark** | **Yes — default home** | Optional — Maintainer / deep work |

**What felt wrong:** cross-links in the H1 banner made H2 *look* nested. Navigation ≠ architecture. Links are peer shortcuts; payloads stay separate.

## What we did (2026-06-14)

1. H1 + H2 banners now say **sibling hub · separate URL · not a sub-page**
2. H2 opens H1 in **new tab** (peer), not inline
3. H2 shipped **health pill + live poll + sync/heal + light refresh** (parity with H1)
4. `validate-machine-hub-v1.sh` gates sibling copy + health UI
5. Dual heal + validators: **PASS**

## What founder should do

1. **Bookmark H1** (`http://127.0.0.1:13020/`) — daily Worker task, Safety, queue
2. **Bookmark H2** (`http://127.0.0.1:13020/machines/`) — pending registry, Judge, Thread Room (weekly)
3. **Never** use `/legacy/` for daily truth — archive only
4. Do **not** ask Brain to embed H2 tables on H1 — alarm line + link is the law

## When to split ports (future, not now)

Only if H2 scheduled jobs ever slow H1 API process. Today payloads are disk-receipt reads — one Python server is fine. Split would be `:13021` static H2, not “more sub-pages.”

*End TWO_HUB_SIBLING_MODEL_ADVISOR_LOCKED_v1*
