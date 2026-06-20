# NewMatch Factory — LOCKED Proposal v1

**Version:** 1.2.0 · **Saved:** 2026-06-19T17:15:00Z · **Authority:** Founder SAVE  
**Path:** `data/NEWMATCH_FACTORY_PROPOSAL_LOCKED_v1.md`  
**Machine SSOT:** `data/newmatch-factory-v1.json`  
**Graph schema:** `data/newmatch-graph-schema-v1.json`  
**999-plan:** `data/newmatch-factory-999-plan-v1.json`  
**Generator:** `scripts/gen_newmatch_factory_999_plan_v1.py`

---

## One law

**NewMatch** (`newsinaaidatabase`) routes connections from dating/social/work apps into **situations**, decides **personal vs business vs defer vs block**, and runs **bounded agentic follow-up** with receipts — as a **cloud factory** under SourceA. Mac is **control panel only**. **Free-tier paths exhaust first** — Phase 0 ceiling **$0**.

---

## v1.2 enhancements

| Layer | What shipped |
|-------|----------------|
| **Graph schema** | `person` · `edge` · `signal` · `situation` · `follow_up` — scoring + API shapes |
| **T0 router** | `scripts/newmatch_situation_router_t0_v1.py` — deterministic $0 rules + demo mode |
| **Free-tier gate** | `scripts/newmatch_free_tier_check_v1.py` — Phase 0 readiness receipt |
| **MVP waves** | W1 graph → W2 router → W3 ingest → W4 follow → W5 handoff/wire |
| **999-plan metadata** | `mvp_wave` · `signal_hint` · `route_hint` · `graph_entity` · `priority` |
| **Phase 0 inventory** | P0-14 NewMatch reference surface (freemium · $0) |

---

## Free-tier policy (exhaust first)

| Authority | Path |
|-----------|------|
| Tier priority law | `docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md` |
| Tool pick | `data/tool-pick-two-phase-v1.json` — Phase 1 free before Phase 2 paid |
| MCP free stack | `data/mcp-stack-free-tier-v1.json` |
| Phase 0 reference | `data/phase0-freemium-sandbox-reference-v1.json` — `cost_ceiling_usd: 0` |

**NewMatch free stack:** local JSON + Supabase free · Python rules T0 · `:free` LLM chain · Vercel hobby / CF Pages · manual/CSV/SEMEJ ingest ($0). **Paid T2+ blocked** until free path exhausted + founder approval + NO-CC gate.

**999-plan:** `free_tier_first: true` on every row · **820+ plans** at `marginal_cost_usd: 0`.

---

## What it is

| | |
|---|---|
| **Product** | NewMatch — semi-personal · semi-business opportunity mind |
| **Sub-project** | `apps/newmatch/` under SourceA (scaffold pending WORK order) |
| **Factory ID** | `newmatch_router_cloud` (when cloud API online) |
| **Plan registry** | **999 rows** `NM-001` … `NM-999` |
| **SinaaiDataBase** | Broker/search only — **not** execution body |

---

## Architecture

```text
Apps (dating · social · calendar)
  → founder-approved ingest (SEMEJ · manual · CSV) — $0
  → Mac Hub (approve · monitor · situation inbox)
  → People graph (local JSON Phase 0 · Supabase free)
  → T0 situation router (rules · $0) → T1 :free LLM if ambiguous
  → FBE Railway /newmatch/route (cloud when online)
  → Follow-up loop (planner → executor → receipt)
  → Route: personal · hybrid · NF/TF/SourceA · defer · block · founder_gate
```

---

## Situation engine

| Signal | Route bias |
|--------|------------|
| `dating_mutual_like` | `personal_nurture` |
| `linkedin_inmail` + business keywords | `business_opportunity` |
| Dating + LinkedIn overlap | `hybrid_explore` |
| Red-flag keywords | `block` |
| Stale 30d+ | `defer` |
| Money · legal · publish | `founder_gate` |

**T0 first** — free LLM only when confidence &lt; 0.55.

```bash
python3 scripts/newmatch_situation_router_t0_v1.py --demo --json
python3 scripts/newmatch_free_tier_check_v1.py --json
```

---

## API contract (cloud when online)

| Method | Path | Tier | Cost |
|--------|------|------|------|
| POST | `/newmatch/route` | T0 | $0 |
| GET | `/newmatch/situation/{id}` | T0 | $0 |
| POST | `/newmatch/ingest/manual` | T0 | $0 |
| POST | `/newmatch/follow/plan` | T0/T1 | $0 |

Host: FBE Railway public HTTPS · Mac Hub = control panel only.

---

## Hub slices (control panel)

- **situation_inbox** — open situations · route preview  
- **follow_up_queue** — planner outputs awaiting founder  
- **cost_tier_meter** — T0/T1 $0 · T2+ blocked  
- **founder_gate_outbound** — T3 irreversible sends  

---

## Cost intelligence (free-tier first)

| Tier | Use | Cost |
|------|-----|------|
| T0 | Rules · dedup · merge · local JSON | **$0** (default NM-001..650) |
| T1 | Classify situation | **$0** — `:free` models only |
| T2 | Draft follow-up | **Blocked** until free exhaust + founder approval |
| T3 | Send / invite | **Founder approve** · NO-CC until revenue gate |

---

## MVP waves

| Wave | IDs | Ship |
|------|-----|------|
| W1 | NM-001–150 | Graph schema on disk · seed JSON |
| W2 | NM-151–300 | T0 router · FBE endpoint stub |
| W3 | NM-501–650 | Ingest paths |
| W4 | NM-301–500 | Follow-up loops |
| W5 | NM-751–999 | Handoffs · wire · scale |

**Critical path:** NM-001 · NM-150 · NM-300 · NM-500 · NM-650 · NM-750 · NM-850 · NM-950 · NM-999

---

## Guardrails

1. **Cloud factories only** — `data/cloud-factories-online-only-v1.json`
2. **No headless dating scrape** — SEMEJ = signed-in founder session only
3. **T4_internal** default disclosure for personal graph
4. **No model-as-ship** for personal outbound
5. **Zero fragmentation** — one SSOT · one factory ID · one receipt chain

---

## Commands

```bash
python3 scripts/gen_newmatch_factory_999_plan_v1.py
bash scripts/validate-newmatch-factory-v1.sh
python3 scripts/newmatch_situation_router_t0_v1.py --demo --json
python3 scripts/newmatch_free_tier_check_v1.py --json
```

---

## Promote to docs/ (founder)

`docs/NEWMATCH_FACTORY_PROPOSAL_LOCKED_v1.md` requires `EDIT ALLOWED: docs/...` + `ACTION:`.

**Scaffold apps:** `WORK P0 NM-001` or `EDIT ALLOWED: apps/newmatch/` + `ACTION: scaffold graph`.
