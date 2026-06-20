# GPT + Claude WTM synthesis — insights, results, pendings (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Date:** 2026-06-06  
**Authority:** Founder ASF + SourceA LOCKED stack  
**Machine SSOT:** `scripts/system_roadmap.py`, validators, `~/.sina/*`  
**Critic law:** `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` — compare only, never steer build

---

## 0. One-sentence verdict

**Architecture through D16 is shipped; gate mode = machine `~/.sina/gate_mode_v1.txt` (**enforce** as of 2026-06-14 — live logged); remaining work is live senses depth (L0/L1), full cloud L8 embeddings (hybrid scaffold shipped), and live LLM outcome proof beyond Eval-1b — external AI was right on gaps, unreliable on operational state.**

---

## 1. GPT analysis (saved)

### What GPT got right

| Claim | Verdict |
|-------|---------|
| Phases A–C complete | ✅ Confirmed |
| D1–D16 pre-LLM stack shipped | ✅ Artifacts + validators |
| World Model → Packet → LLM pattern | ✅ Correct architecture |
| L0 user signals missing | ✅ Was missing; L0 MVP shipped 2026-06-06 |
| L1 workspace partial | ✅ Hub-fed; L1 MVP shipped 2026-06-06 |
| L8 embeddings partial (D5 token) | ✅ **Hybrid shipped** — hash-local embed + D9 blend |
| No evaluation/ layer | ✅ Eval-1b live 5/5 pilots · 5/5 wins (100% live) — machine `/Users/sinakazemnezhad/.sina/eval_packet_v1b_report.json` |
| “Complete” ≠ “proves better outcomes” | ✅ Still true for live LLM A/B; Eval-1 is structural MVP |

### GPT verdict table (accepted)

| Area | Status at analysis time |
|------|-------------------------|
| Architecture | Strong |
| Runtime stack | Strong |
| Pre-LLM stack | Strong |
| Context packet pipeline | Strong |
| User signal layer | Missing → **L0 MVP done** |
| Workspace state | Partial → **L1 hub-fed done** |
| Embedding retrieval | **Hybrid shipped** — hash-local embed + D9 blend (not full cloud) |
| Evaluation | Not shown → **Eval-1 done (structural)** |

---

## 2. Claude analysis (saved)

### What Claude got right

- 16/16 verified logged is a real engineering milestone
- Four open items (L0, L8, Eval, D15.2 UI) do not block enforce
- Pre-mortem on enforce edge cases is correct **behavior**
- Packet-as-intelligence-path is the right framing

### What Claude got wrong / stale

| Claim | Reality |
|-------|---------|
| “One env var + hub restart” to ENFORCE | **Live** — `~/.sina/gate_mode_v1.txt` = **enforce** · `/api/dispatch-policy-v1` `gate_mode` |
| D16 writeback is next | **D16 shipped** before Claude message |
| D15.2 UI not shipped | **Shipped** — packet readiness panel |
| Gate still shadow (screenshots) | **SSOT drift** — live gate was enforce |

---

## 3. Cursor agent insights (saved)

1. **Trust order:** `~/.sina` + validators > hub Refresh > external chat  
2. **ENFORCE scope:** Planner dispatch choke — Cursor IDE still bypasses  
3. **SSOT projection drift** was a recurring bug — fixed in `system_roadmap.py`  
4. **Hub perf:** 2.7MB `command-data.json` caused empty UI — fixed with shell payload  
5. **Governance moat:** Rules-in-charge loop is as important as D-layer code  
6. **Next proof layer:** Eval-1 structural → future live LLM A/B with RAGAS-style CI  

---

## 4. Recommendations (saved) — execution status

| Priority | Recommendation | Status |
|----------|----------------|--------|
| P0 | SSOT hygiene (do_now, ship_ready, honest_score) | ✅ Shipped |
| P1 | Eval-1 packet vs raw | ✅ Shipped (`eval_packet_v1/`) |
| P2 | L0 + L1 MVP | ✅ Shipped (`pre_llm/user_signals/`) |
| P3 | L8 full embeddings | ✅ Hybrid scaffold (hash-local + D9) |
| P4 | L5/L6 deepen | ✅ L5 git history + L6 feedback→D9/D16 |
| P5 | ENFORCE receipts in hub | ✅ Shipped (`gate_receipts_hub.py`) |
| P6 | Rules loop in agent-loop | ✅ Shipped |

---

## 5. Live results (2026-06-06 ship)

| Item | Result |
|------|--------|
| Phase D | 16/16 artifacts |
| Gate mode | **enforce** (`~/.sina/gate_mode_v1.txt` · `/api/dispatch-policy-v1`) |
| Packet readiness | 100% · gate_eligible |
| Eval-1 | ≥80% structural packet wins |
| L0 | `user_signals_v1.json` on hub touch |
| L1 | `workspace_state_v1.json` hub-fed |
| Rules loop | Orchestrator + validator PASS |
| Hub boot | `command-data-shell.json` ~500KB |

**APIs added:**

- `/api/eval-packet-v1` · `/api/eval-packet-v1b`
- `/api/user-workspace-signals-v1`
- `/api/gate-receipts-v1` · `/api/dispatch-policy-v1` · `/api/graph-executor-v1`
- `/api/strategic-synthesis-v1` · `/api/event-bus-v1`
- `/api/agent-rules-in-charge-v1`

**Validators added:**

- `validate-eval-packet-v1.sh` · `validate-eval-packet-v1b-live.sh`
- `validate-user-workspace-signals-v1.sh`
- `validate-gate-receipts-v1.sh` · `validate-spine-bridge-founder-v1.sh`
- `validate-verify-wire-v1.sh` · `validate-event-bus-v1.sh`
- `validate-agent-rules-in-charge-v1.sh`

---

## 6. Pendings (honest)

| ID | Item | Status |
|----|------|--------|
| L8 | Hybrid embed + D9 rank | **done** (hash-local scaffold) |
| L5 | Semantic change history | **done** (L5 git bridge → D16) |
| L6 | Execution signals in packet | **done** (feedback→D9 + D16 merge) |
| Eval-1b | 5+ live pilots + CI | **done** (5/5 pilots · 5/5 wins · 100% live) |
| L0-full | Editor open_files telemetry | **partial** (hub workspace POST) |
| Phase 2b | Founder spine Action | **eligible** — Refresh → Actions |
| RunReceipt | Pack + verify:wire | **done** (`validate-verify-wire-v1.sh`) |
| Event bus | pub/sub fabric | **done** (`/api/event-bus-v1`) |
| Commercial | TrustField pilot + lane revenue | **open** (lane P0) |
| Governance | Essay nudges + fleet verify | **done** (nudge_count 0 · fleet 8/8 auto_pass · sa-0791/0794) |

---

## 7. Founder law (unchanged)

- **No Terminal** — Refresh, Actions, hub tabs only  
- **Rules supersede** — edit existing LOCKED/`.mdc`; never duplicate  
- **External AI** — input to Track, not law  

---

## 8. How to use this doc

1. Agents read this when GPT/Claude paste arrives — **compare to §5 live results**  
2. Maintainer updates §5–§6 on each ship — bump version if pendings close  
3. WTM tab shows live panels — this doc is the **locked narrative**  
4. **Big picture + next plans:** `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` + hub `/api/strategic-synthesis-v1`

---

*Locked — supersedes informal chat summaries only. Canonical build order remains `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`. Strategic goals/phases: v2 synthesis doc.*
