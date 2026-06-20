# Strategic next steps — big picture synthesis (LOCKED v2)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0  
**Date:** 2026-06-06  
**Authority:** Founder ASF + maintainer ship  
**Supersedes:** Informal chat summaries; complements `SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md`  
**Council brief:** `COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md`  
**Critic law:** `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` — compare only

---

## 0. One sentence

**Architecture through D16 + ENFORCE is shipped; the bottleneck is behavioral proof (Eval-1b) and execution closure (dispatch policy) — not new D-modules; governance + lane P0 revenue run in parallel.**

---

## 1. System identity (big picture)

Four coupled planes:

1. **Governance** (~50%) — Council, rules-in-charge, 8-agent fleet, Track, Scoreboard, critic law  
2. **Hub control** — Sina Command :13020, Refresh-only founder, WTM, panels  
3. **Pre-LLM + runtime** — D1–D16 packet, ENFORCE gate, C1–C7 instruct-only, spine executes  
4. **Portfolio lanes** — TrustField delivery, AI Dev Bridge wire, Factory P0 — parallel revenue clocks  

**Pattern:** Repo → D1–D16 → packet → `gate_eligible` → hub LLM → agent in allowed repo only.

**Bottleneck (all audits agree):**

```
Context → Plan → Runtime → STOP (dispatch_ready: False)
```

D16 writeback is shipped; it does not close the loop without dispatch + behavioral outcomes.

---

## 2. Live state (physical — trust order: ~/.sina + validators → Refresh)

| Area | Status |
|------|--------|
| Phase A–D | Shipped (16/16 D artifacts) |
| Gate | **enforce** · readiness 100% |
| Eval-1 | Structural PASS |
| L0/L1 | Hub-touch MVP |
| D16 | Memory merge live |
| Rules loop | Orchestrator + validator PASS |
| Hub | Shell payload + strategic slice seeded |
| Diagnostics | No critical bugs |

---

## 3. GPT + Claude — merged verdict

| Trust | Topic |
|-------|--------|
| ✅ | Architecture gaps, dispatch dead-end, D5 token-only, structural eval only, no event bus |
| ✅ | “Prove packet > raw before auto-dispatch” |
| ❌/stale | Live ops (enforce, D16, panels), “flip ENFORCE” as next step |
| Silent | Governance moat (~50% of system) |

**Founder lock overrides critic build order:** STRATEGIC-SLICE now — not L8 primary, not new D-module.

---

## 4. Strategic goals

### Ecosystem north star
Prove packet produces measurably better outcomes than raw LLM, then close execute→measure→learn without breaking governance.

### Commercial north star
Shipped products, users, revenue — TrustField pilot, Wire RunReceipt, factory SKUs — **parallel** to ecosystem slice.

### WTM `do_now`
**STRATEGIC-SLICE** — Eval-1 sustain · L0/L1 deepen · ENFORCE bypass transparency.

---

## 5. Phase plan (engineering — maintainer only)

| Phase | Build | Gate | Owner |
|-------|--------|------|--------|
| **0** | Slice sustain + lane attests | Now | Maintainer + lanes |
| **1** | **Eval-1b** behavioral harness | **Live pass** — task grounding + path scoring | Maintainer |
| **2** | Dispatch policy + C7→spine bridge | **Eligible** — eval proof bridge `spine-smoke-echo` | Maintainer |
| **3** | L8 embedding index | Dispatch open | Maintainer |
| **4** | Learning loop (outcomes→D9/D5) | L8 + dispatch | Maintainer |
| **5** | Event bus | Parallel from Phase 3 | Maintainer |

---

## 6. Pendings (honest)

| ID | Item | Owner | Status |
|----|------|--------|--------|
| P0 | Eval-1b sustain — 5+ live tasks + CI | Maintainer | done (live pass); expand suite |
| P1 | ENFORCE bypass map LOCKED + hub | Maintainer | **done** |
| P2 | L0-full editor telemetry | Maintainer | partial (workspace POST) |
| P3 | L0/L1 deepen | Maintainer | open |
| P4 | Dispatch policy + eval gate | Maintainer | **done** (eligible) |
| P5 | graph_executor + spine_bridge | Maintainer | **done** — Founder Action ready |
| P6 | L8 embeddings hybrid | Maintainer | **done** (hash-local hybrid) |
| P7 | L5/L6 semantic history depth | Maintainer | **done** (L5+L6 packet bridge) |
| P8 | Learning loop + event bus | Maintainer | **done** |
| P9 | Lane Scoreboard + vault attests | Lanes | **done** (8/8 auto-green 2026-06-06) |
| P10 | TrustField outreach / pilot | TrustField | in_progress (vault note + outreach) |
| P11 | Wire RunReceipt / verify:wire | Wire | **done** |

---

## 7. This week — do now

### Founder (Refresh only)
1. Refresh → Council brief → Scoreboard (lanes when Command open)  
2. Track — confirm slice cards visible  

### Maintainer
1. Sustain Eval-1b live CI (`SINA_EVAL_1B_LIVE=1` on build)  
2. Founder Action: **Enqueue eval spine bridge** when loop ready  
3. Governance fleet: essay nudges + Scoreboard verify column  
4. L0-full deepen (editor hooks) — optional parallel  

### TrustField
P0 outreach → demos → pilot; hub attest ~5 min when Command open.

### AI Dev Bridge
Continue RunReceipt / `verify:wire`; hub attest when Command open; G3 on `WIRE_LANE_PROGRESS`.

---

## 8. Do not do

- New D-modules from critic paste  
- L8 as WTM primary (overridden by STRATEGIC-SLICE)  
- Lane agents editing SourceA  
- Fabricating physical G3 PASS for Track slice  
- Parallel `.mdc` law without supersession  

---

## 9. Lessons (pattern extraction)

1. Architecture without outcome proof = decision support  
2. Governance is half the product  
3. SSOT > screenshots > chat  
4. Two clocks normal (slice ∥ lane P0)  
5. Narrow bar (Track slice) ≠ wide bar (physical proof)  
6. D16 ≠ loop closure  
7. Commercial truth = lane P0 revenue  

---

## 10. Canonical references

| Doc | Role |
|-----|------|
| This doc | Big picture + next steps LOCKED |
| `COUNCIL_BRIEF_STRATEGIC_SLICE_*` | Founder build order + lane law |
| `SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md` | Critic vs live results |
| `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | 33-step map |
| Hub `/api/strategic-synthesis-v1` | Live pendings + phases for UI |

---

*LOCKED v2 — maintainer updates §6 pendings when items close; bump version on major ship.*
