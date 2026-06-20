# ATTACHMENT — Claude AI · Pre-LLM gate hardening (v1)

**Saved:** 2026-06-06T18:42:40Z · **Retrofit:** doc-datetime-law batch retrofit
**Type:** STAGING ATTACHMENT — beneficial extras from **Claude chat** (Claude AI) external critic session  
**Status:** Attached to WTM payload · **Orders 7–12 partial** — sub-steps placed under D15 + D5 (founder attach request 2026-06-05)  
**Parent law:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` Orders 1–6 applied · Orders 7–12 for hardening items below  
**Critic class:** `EXTERNAL_CRITIC` per `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` — source: **Claude** (not ChatGPT; not “cloud”)  
**Supersedes mislabel:** `CLOUD_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md` (wrong name — was always Claude)  
**Source kept:** `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` · D1–D16 IDs unchanged · Phase order unchanged  
**Machine SSOT:** `scripts/system_roadmap.py` → `roadmap_attachments` + `implementation_hardening`  
**Analyzed:** 2026-06-05  

---

## 1. Verdict (compare table — Order 2–3)

| Analyst claim | Verdict | Locked source alignment |
|---------------|---------|-------------------------|
| Execution spine is real (validators, queue, workspaces) | **TRUE** | Phase A–C done · 24+ validate scripts |
| 4/10 = pre-LLM incomplete, not broken | **TRUE** | `honest_score` in WTM map |
| Model calls bypass structure today | **TRUE** | `agent_loop` → OpenRouter without `validate_packet()` |
| One pipeline to 7/10: intent→retrieval→ranking→plan→packet→model | **TRUE** | D4–D16 catalog unchanged |
| Design packet schema **before** D4–D15 code | **CORRECT** | `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` shipped first |
| Refactor execution spine | **REJECT** | Violates §0 — build pre-LLM on top |
| Replace D-step IDs with analyst list | **REJECT** | Rename-only / replace — attachment law §4 |

---

## 2. Lessons learned (what we know now)

### 2.1 Founder vs system

| Misread | Truth |
|---------|-------|
| “We didn’t think enough” | Founder thinking is fine — **system** does not **force** structured context before every model call |
| “4/10 = broken” | **4/10 = spine strong, pre-LLM ~25%** (4/16 steps: D1–D4) |
| “Heavy hub = heavy OS” | Hub JSON weight ≠ intelligence; **missing gate** = intelligence gap |

### 2.2 Architecture (substrate vs projection)

Industry + analyst align with WTM:

- **Substrate:** `~/.sina/*`, D1–D3 graphs, intent SSOT — persists between calls  
- **Projection:** `llm_context_packet_v1.json` — **one assembled view per model call**, discarded after  
- **Assembly engine:** D15 is the **compiler**, not another feature  
- **Stable prefix + dynamic chunks:** `constraints` + `compressed_context` + task last  

### 2.3 What is shipped vs what is not

| Shipped | Not wired yet |
|---------|----------------|
| Packet schema + `validate_packet()` | `gate_eligible` enforcement on OpenRouter |
| D1–D4 producers | D5–D10, D14–D15 fill gate sections |
| C5 fabric handles (stateless) | D15 assembly at runtime |
| Rule-based D4 intent | LLM-based ranking/plan (D9/D10 can start rule-based) |

---

## 3. Recommendations (convinced — placed as sub-steps)

### 3.1 Three gate modes (implementation policy)

| Mode | When | Behavior |
|------|------|----------|
| **OFF** | Until D5 PASS | Models run as today (transition) |
| **SHADOW** | D5 + partial D9/D10 | Assemble packet + log `gate_eligible`; **still** call model |
| **ENFORCE** | D14 + D15 PASS | **Block** hub OpenRouter if `gate_eligible` false |

**Receipt:** `validate-model-gate-enforced-v1.sh` when ENFORCE ships.

### 3.2 Single choke point — `model_dispatch.py`

All hub-side OpenRouter calls route through **one module**:

```
task → assemble_packet (D15) → validate_packet() → model_dispatch → OpenRouter
```

**First wire target:** `agent_loop._planner_chat` only (not Cursor executing agent).

### 3.3 Do NOT gate (Month 3 scope)

| Gate | Month 3 |
|------|---------|
| Agent loop **planner** OpenRouter | **YES** |
| Live agents / Advisor OpenRouter | **YES** (after planner proof) |
| Cursor **executing** agent | **NO** — execution spine stays |

### 3.4 Rule-based before LLM-based

D9 ranking + D10 plan can use **graph scores + D4 decomposition** first. LLM polish is optional later.

### 3.5 Hub visibility

Show **packet readiness %** on Agent loop + WTM (from `validate_packet(hydrate(task))`).

---

## 4. Placement analysis (Order 8 — convinced extras)

| Extra | Phase | Parent | New ID | Before/after |
|-------|-------|--------|--------|--------------|
| Model dispatch choke point | D | **D15** | **D15.1** | After D15 assembly spec, before D16 |
| Gate modes + shadow/enforce policy | D | **D15** | **D15.1** (same) | Implementation policy |
| Hub packet readiness UI | D | **D15** | **D15.2** | After D15.1 stub |
| Local vector index (no Ollama) | D | **D5** | *(existing D5)* | Harden: local-only law in D5 goal |

**No new top-level D17.** Cross-cutting gate = D15 family only.

---

## 5. 90-day hardened build order

| Month | Ship | Receipt | Gate mode |
|-------|------|---------|-----------|
| **1** | **D5** retrieval + D15.1 shadow stub (`model_dispatch` logs only) | `validate-vector-retrieval-v1.sh` | OFF → SHADOW start |
| **2** | D7–D10 rule-based ranking + plan | D9/D10 validators | SHADOW |
| **3** | D14 compress + D15 assemble + **ENFORCE** on agent-loop planner | `validate-model-gate-enforced-v1.sh` | ENFORCE |

---

## 6. Do not touch (locked)

- Execution spine A1–A4  
- Intelligence B1–B6 (frozen)  
- Runtime C1–C7 (complete)  
- C5 bridge law (handles only)  
- B-layer memory truth vs D6 retrieval  

---

## 7. Rejected from analyst session

| Item | Reason |
|------|--------|
| New 13-step top-level roadmap | Replaces locked D1–D16 |
| “Start over” / refactor spine | Contradicts alignment law |
| Local Ollama as default | Founder removed; D5 = local index, cloud/embed API optional |
| Gate Cursor executor on day one | Breaks founder workflow; planner first |

---

## 8. Pointer for hub

- Attachment path: `archive/attachments/wtm/CLAUDE_ANALYST_PRE_LLM_GATE_HARDENING_ATTACHMENT_v1.md`  
- Payload keys: `roadmap_attachments[]`, `implementation_hardening`  
- Next build: **D5** · Sub-steps **D15.1**, **D15.2** when D15 track starts  

---

## 9. Convince gate (Order 7)

- [x] Extra improves **gate clarity** — not cosmetic  
- [x] Does not duplicate D15/D5 titles — extends implementation  
- [x] Founder explicit attach request (2026-06-05)  
- [x] Placement memo written (§4)  

**Result:** Machine SSOT updated · MAP v5.2 unchanged · payload v5.2 extension · attachment + sub-step IDs D15.1/D15.2 in `system_roadmap.py` + hub WTM panel.
