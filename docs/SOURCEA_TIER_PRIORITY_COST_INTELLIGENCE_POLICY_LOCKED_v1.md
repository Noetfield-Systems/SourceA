# SourceA Tier · Priority · Cost Intelligence Policy — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-18T22:45:00Z · **Authority:** ASF SAVE  
**Path:** `docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md`  
**Supersedes:** scattered tier/cost fragments — this row is the **unified pick policy**  
**Subordinate (do not duplicate prose):** `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` · `brain-os/EXECUTION_ENGINE_STRATEGY_LOCKED_v1.md` · `SINAAI_AGENT_STACK_POLICY_v1.md` · `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` · `data/fbe_quality_contract_v1.json` · `data/commercial-film-routing-v1.json` · `archive/attachments/2026-06-06/COMMERCIAL_VIDEO_COST_INTELLIGENCE_2026-06-06_v1.md`

---

## 0. One sentence (law)

> **Always exhaust free-tier paths first — then let cost intelligence pick the highest-ROI move among what remains; never pay for the wrong category.**

---

## 1. Three tier vocabularies (never mix words)

| System | Tiers | Use for | SSOT |
|--------|-------|---------|------|
| **Infra spend** | Free-only → paid (ASF gate) | Cloud · DB · APIs · credit card | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` |
| **Governance depth** | P0–P7 | Law · enforcers · noise reject | `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` |
| **Governance stack (G0–G8)** | G0 founder → G8 chat | Which layer wins on conflict | `SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md` §2.2 |
| **Queue / factory** | T0–T3 → P0–P3 | `sa-*` prompt priority | `generate-sourcea-1000-prompts.py` mapping |
| **FBE factory quality** | BRONZE → MARKET_READY | Shippable tier_achieved | `data/fbe_quality_contract_v1.json` |
| **Commercial film** | A_hero · B_proof · C_social · D_gtm | Lane × buyer × runtime | `data/commercial-film-routing-v1.json` |
| **Video cost stack** | Tier 0 bootstrap → Tier 1 default → Tier 2 scale | Monthly tool spend | `COMMERCIAL_VIDEO_COST_INTELLIGENCE_2026-06-06_v1.md` |
| **Agent LLM keys** | Tier 0 service priority 1–11 | Leader vs worker chains | `SINAAI_AGENT_STACK_POLICY_v1.md` |

**Rule:** When founder says “tier,” resolve **which table** before picking. Auto Runtime specialist · advisory circle · outbound factory use **queue tier P0–P3 + commercial ROI** — not hub founder P0 alone.

---

## 2. Priority order (deterministic)

```text
1. FREE TIER ELIGIBLE     — $0 infra · :free models · local · OSS tools
2. QUEUE TIER             — P0 before P1 before P2 before P3
3. COMMERCIAL BLOCKERS    — w3_sina_read · w3_send_ready · freeze/resume
4. ROI SCORE              — revenue_or_proof_impact ÷ marginal_cost
5. PAID ESCALATION        — only when (1) free path blocked AND (2) ROI gate PASS AND (3) ASF or revenue gate
```

**Founder infra (hard):** `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` — free-tier clouds and `:free` LLM keys only until ASF deliberately adds paid key or revenue gate opens.

**Agent stack Tier 0 key priority (implement order):** OpenRouter → Groq → Cerebras → Gemini (1–2 leaders) → Mistral Experiment (batch) → GitHub Models (hard cases) → Tavily → Langfuse → LiteLLM → Upstash → Ollama last.

---

## 3. Cost intelligence pick (ROI algorithm)

### 3.1 Filter — free first

Before any paid pick:

| Check | Pass = continue | Fail = stop or free alternate |
|-------|-----------------|-------------------------------|
| Infra | Path on free-tier allowlist | Block — see NO-CC law |
| LLM | `:free` / local / batch quota | Downgrade model chain |
| Capture | OBS · QuickTime · Screen Studio trial | No Runway/HeyGen hero without gate |
| Cloud factory | Mac control plane + CF free cron prep | No paid Worker until Phase 2b + ROI receipt |

### 3.2 Score — ROI among survivors

```text
roi_score = (proof_impact + revenue_proxy + unblock_value) / max(marginal_cost_usd, 0.01)

proof_impact:     W1 film · validator PASS · tier_achieved bump
revenue_proxy:    W3 meeting booked · outbound send-ready · design-partner ship
unblock_value:    clears commercial_red · dual_pick · ACTIVE_NOW alignment
marginal_cost:    incremental $ this pick only (not sunk stack)
```

**Budget buckets (commercial video — research SSOT):** proof 40% · acquire 35% · brand 15% · lab 10%.

**Golden insight (locked):** Top-tier B2B = real capture + pro voice + derivatives; generative AI ≤ 20% runtime.

### 3.3 Pick — one winner

1. Sort by **roi_score DESC**  
2. Tie-break: **queue tier** (P0 < P1 < P2 < P3)  
3. Tie-break: **upgrade_id** lexicographic (deterministic)  
4. Emit receipt with `deterministic_hash` — no chat as SSOT  

**Machine implementation:** `scripts/future_loop_prompt_advisory_circle_v1.py` — `confidence` from tier + blockers; `execution_authority: false`.  
**Auto Runtime specialist:** composes from advisory + observatory; dispatches only when policy + resume allow (`loop-specialist-config-v1.json`).

### 3.4 Decision gates (category — never pay wrong)

| Question | Yes → | No → |
|----------|-------|------|
| Can Screen Studio prove it? | Capture-first | No Runway unless B-roll gate |
| Need face on hero? | Product-led · tier C founder ok | HeyGen not tier-A hero |
| Need 20+ cuts? | Creatify / fal paygo | Manual Runway at scale |
| Enterprise legal? | Synthesia / HeyGen / Adobe Enterprise | Consumer gen stack |
| UI green only? | Ignore — receipt `tier_achieved` only | `fbe_quality_contract_v1.json` |

---

## 4. Execution engine cost matrix (agent turns)

Subordinate: `brain-os/EXECUTION_ENGINE_STRATEGY_LOCKED_v1.md`

| Path | Model | When | Cost band |
|------|-------|------|-----------|
| CLI act/build | Sonnet | High-tool · files · bash | ~$0.05–0.25/turn |
| API verify/check | Haiku | Low-tool · read-only | ~$0.002–0.005/turn |
| API complex verify | Sonnet | Complex audit | ~$0.02–0.05/turn |
| Cursor | manual | IDE-heavy · blocked 2× | $0 API |

**Route by tool count, not label alone.** Prefer Haiku/API for verify before Sonnet/CLI act.

---

## 5. Cloud factories + Auto Runtime specialist

**Control plane (Mac SSOT today):** `data/loop-specialist-cloud-contract-v1.json` · tick via `loop_specialist_tick_v1.py` or `POST /api/loop-specialist/tick/v1`.

**Cost order for cloud factories:**

1. Mac tick + n8n cron glue (`n8n_loop_specialist_tick_hook_v1.sh`) — free  
2. Cloudflare Worker cron POST `dispatch=false` — free tier prep  
3. Paid cloud run — only when auto_dispatch enabled + ROI receipt + ASF resume under freeze rules  

**Commercial compile order (unchanged):** SourceA Sina read → Noetfield compile → TrustField send.

---

## 6. Paid escalation gate (ASF)

Paid spend requires **all**:

1. Free path documented blocked (receipt or validator FAIL reason)  
2. `roi_score` ≥ threshold for category (default: proof moves beat polish 2:1)  
3. One of: ASF explicit paid key · revenue deposit · `FOUNDER_NO_CC` exception row updated  
4. No AUTO-RUN without resume — `~/.sina/auto-run-disabled-v1.flag` respected  

---

## 7. Machine proof (must run after policy touch)

```bash
bash scripts/validate-doc-datetime-header-v1.sh docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md
python3 scripts/future_loop_prompt_advisory_circle_v1.py --json   # deterministic ranked_prompts
python3 scripts/loop_specialist_tick_v1.py --json                 # observatory + advisory wired
bash scripts/validate-loop-specialist-v1.sh
./scripts/founder_free_verify.sh                                  # infra free path (TrustField)
```

---

## 8. Related authority rows (pointers only)

| Row id | Doc |
|--------|-----|
| `FOUNDER_NO_CC` | `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md` |
| Commercial SSOT | `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v1.md` |
| Stack map / loop | `docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md` |
| Agent stack | `SINAAI_AGENT_STACK_POLICY_v1.md` |
| Live gov tiers | `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` |

**Index row:** add on next GOV_UNIFY batch — id `TIER_COST_INTEL` → this path.

---

## 9. Founder one-liner

**Free tiers first · P0 queue · clear commercial reds · ROI pick · receipt proves the choice.**
