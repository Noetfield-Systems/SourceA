# Hub App Quality — Research Report (LOCKED v1)

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-10  
**Law:** Research input only — implementation follows `docs/HUB_UNIFY_AND_PROOF_MASTER_v1.md` + ASF order  
**Skills used:** sina-research-lessons · canvas audit · industry dashboard UX research

---

## 1. What a good founder control-panel app must do

From SaaS dashboard UX research (Grotol, Orbix 2026, Achromatic RSC patterns):

| Principle | Founder hub translation |
|-----------|-------------------------|
| **One decision per screen** | Home = status + next action only (not 40 tabs at once) |
| **Progressive disclosure** | Shell first (~400KB), heavy tabs on demand |
| **Skeleton = perceived speed** | Layout-shaped placeholders, not spinners (NN/g ~40% faster feel) |
| **Live slices, not full rebuild** | Queue/inbox/proof via hub-sync + SSE — never 8.8MB poll |
| **Role-based views** | ASF = one-tap actions; worker = INBOX; brain = pick only |
| **Performance is UX** | Blank/empty tabs = "broken" even when API is fine |

---

## 2. What Sina Command got wrong (honest)

| Anti-pattern | Evidence on disk |
|--------------|------------------|
| Monolith JSON boot | `command-data.json` 8.8MB — blocked main thread |
| Poll stacking | Advisor 5s + goal1 8s + hub-sync + tab APIs |
| Fragmented tabs | `HEAVY_PAYLOAD_KEYS` stripped data but lazy map incomplete |
| Stale live state | `mergeHubSync` skipped when `generation_id` unchanged |
| Debug ingest noise | `127.0.0.1:7675` fetches on every nav click (removed) |
| Empty states | Backlog/Fleet/Roadmaps showed "refresh" with no skeleton |
| Architecture drift | Master plan §2 `GET /api/surface/v1` + per-slice loaders not fully shipped |

---

## 3. What was fixed this session (disk)

- Slim hub-sync (~138KB) + 2s cache keyed on `queue_pos`
- SSE debounce + in-flight guard on hub-sync
- Lazy tab map expanded (backlog, fleet, roadmaps, track, guide, …)
- Live slice merge always applies goal1/inbox
- Idle prefetch (8–12s) for full bundle without boot hammer
- Tab skeleton loaders (home/backlog/roadmap shapes)
- Sync degraded indicator on meta strip

---

## 4. Still missing vs good-app bar (priority)

| P | Item | Effort |
|---|------|--------|
| P0 | Ship `GET /api/surface/v1` + `GET /api/slice/home` per master plan §2 | M |
| P0 | Per-tab slice APIs (roadmap, council, backlog) — no full JSON | L |
| P1 | Error boundary per tab (catch render throw → retry card) | S |
| P1 | Mobile: test topbar scroll + touch targets on iPhone | S |
| P2 | React/Vite split (long-term) — current vanilla OK if slices ship | XL |

---

## 5. WTM tie-in

- **Phase s8 hub UX** queue items address fragmentation + proof UX
- This report feeds **sa-0782+** verify/ACT turns — not a parallel roadmap

---

## 6. Founder test (60 seconds)

1. Hard refresh hub (Cmd+Shift+R)
2. Home loads <2s, context strip shows queue %
3. Tap Backlog — skeleton → content (not empty forever)
4. Tap World Target Model — loading → roadmap
5. Worker INBOX pending visible on Home actions

If any step fails → report tab name in Backlog UI (one tap).
