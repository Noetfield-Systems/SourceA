# Merged — Pre-LLM gate synthesis (v1)

**Merged from:** `GATHER_v1_GATE_RESEARCH.md` + Claude trigger (Layer A) + Cursor agent synthesis (Layer B)  
**Provenance:** EXT-001 (trigger), EXT-002/003/007 (agent synthesis)  
**Duplicates removed:** Repeated “4/10 = broken” misread; repeated D-step list (pointer to WTM map instead)

---

## 1. Architecture (substrate → projection → compiler)

| Layer | Sina | Industry name |
|-------|------|---------------|
| Substrate | `~/.sina/*`, D1–D3 graphs, D4 intent SSOT | Long-lived knowledge store |
| Projection | `llm_context_packet_v1.json` per task | Context packet / compiled context |
| Compiler | D15 assemble + D15.1 dispatch | Context pack compiler + LLM gateway |
| Gate | `validate_packet()` → `gate_eligible` | Evaluation gate / interrupt |

**Merge insight:** Zylos/Google ADK “substrate vs projection,” ContextOS “pack upstream of prompt,” and Sina WTM are the same shape.

---

## 2. Compiler stages → packet sections

| Stage | Step | Packet field |
|-------|------|--------------|
| Intent | D4 | `intent` |
| Evidence | D5, D6, D7 | `retrieval` |
| Salience | D9 | `ranking` |
| Action graph | D10 | `plan` |
| Budget | D14 | `compression`, `compressed_context` |
| Manifest | D15 | `provenance` |
| Door | D15.1 | (not a field — choke point) |

---

## 3. Enforcement diagram (merged)

```text
                    ┌─────────────────────┐
  All hub tasks ───►│  assemble_packet()  │  D15
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │  validate_packet()  │
                    └──────────┬──────────┘
                               │
                    gate_eligible?
                    ┌──────────┴──────────┐
                   NO                    YES
                    │                      │
              Hub: readiness %      model_dispatch()
              + missing list           → OpenRouter
                    │
              Cursor executor OK (ungated)
```

---

## 4. Do / don't (merged from analyst + lessons)

| Don't | Do |
|-------|-----|
| Refactor spine | Pre-LLM on top |
| Big-bang enforce | OFF → SHADOW → ENFORCE |
| Scatter OpenRouter calls | One `model_dispatch` |
| LLM rank/plan first | Rule-based D9/D10, LLM last |
| Dump hub JSON to model | `compressed_context.narrative` |

---

## 5. 90-day merge (single checklist)

| Weeks | Ship | Gate |
|-------|------|------|
| 1–4 | D5 + D15.1 shadow | SHADOW start |
| 5–8 | D7–D10 rule-based | SHADOW |
| 9–12 | D14–D15 + enforce planner | ENFORCE |

**Receipt:** `validate-model-gate-enforced-v1.sh` at enforce.

---

## 6. Schema gap (merge action item)

When D5 PASS: add `retrieval` to gate (conditional on semantic intent). Locked doc §3 already says yes; `schema.py` omits today.

---

## 7. Reference index (full URLs in golden report)

Anthropic · ContextOS · AmtocSoft · MDP · GenAI Patterns · PAACE · LangGraph · RAGAS — see `archive/attachments/wtm/GOLDEN_PRE_LLM_GATE_RESEARCH_REPORT_v1.md` §3.
