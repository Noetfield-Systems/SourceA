# Gathered — Pre-LLM gate research (v1)

**Sources:** EXT-001, EXT-002, EXT-003 (see `01-extracts/MANIFEST.md`)  
**Thread:** WTM-D5

---

## Verdict (one sentence)

The gap is **one missing choke point in code**, not ideas or founder thinking.

---

## Today vs target

| Today | Target |
|-------|--------|
| Hub / agent loop → OpenRouter (raw JSON + chat) | Task → assemble packet → `validate_packet()` → `model_dispatch` → model |

---

## Shipped vs missing

| Shipped | Missing |
|---------|---------|
| Spine A–C, validators | `model_dispatch.py` |
| Packet schema + `validate_packet()` | Enforcement on OpenRouter |
| D1–D4 logged | D5–D10, D14–D15 producers |
| `gate_eligible: false` by design on stub | Retrieval in `GATE_REQUIRED_SECTIONS` when D5 ships |

---

## Golden pipeline (industry + WTM)

```text
INTENT [D4] → RETRIEVE [D5,D7] → RANK [D9] → PLAN [D10]
→ COMPRESS [D14] → ASSEMBLE [D15] → VALIDATE → MODEL [D15.1]
```

---

## Top industry ideas (gathered)

| Idea | Source |
|------|--------|
| Packet = contract, not prompt | ContextOS, AmtocSoft |
| Fail before model if no evidence | AmtocSoft |
| Declarative retrieval plan | MDP context engineering |
| Retrieve → rerank → compress | GenAI Patterns, ThynkQ |
| Plan-aware compression after D10 | PAACE arXiv:2512.16970 |
| CI golden-set gates | RAGAS, CircleCI |
| Interrupt before expensive step | LangGraph |

---

## Three gate modes

| Mode | When |
|------|------|
| OFF | Until D5 |
| SHADOW | D5 + partial D9/D10 |
| ENFORCE | D14 + D15 |

---

## Next three moves

1. Ship D5 (SSOT, API, validator, packet.retrieval)  
2. `model_dispatch.py` shadow (log, don't block)  
3. Enforce planner only after D9+D10 minimal  
