# Book outline — Pre-LLM World Model (v1)

**Field:** `pre-llm-world-model`  
**Audience:** Agents in roles — WTM builder, packet assembler, gate operator, hub planner  
**Status:** Outline — grows from unified essays only  
**First page seeded:** `04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md`

---

## Book title (working)

**Understanding Before Action: The Sina Pre-LLM World Model**

---

## Part I — Why (mindset)

| Ch | Title | Source essay | Status |
|----|-------|--------------|--------|
| 1 | No model without a packet | ESSAY_v1 | ✅ seeded |
| 2 | Substrate vs projection | (from merge §1) | outline |
| 3 | Honest score: 4/10 is spine, not failure | lessons EXT-003 | outline |

---

## Part II — Architecture (WTM Phase D)

| Ch | Title | WTM steps | Status |
|----|-------|-----------|--------|
| 4 | Code intelligence substrate | D1–D3 | outline |
| 5 | Intent engine | D4 | outline |
| 6 | Retrieval & vector index | D5, D7 | **next after D5 ship** |
| 7 | Ranking without LLM | D9 | outline |
| 8 | Planning without LLM | D10 | outline |
| 9 | Compression & budget | D14 | outline |
| 10 | The compiler: context assembly | D15 | outline |

---

## Part III — Gate (enforcement)

| Ch | Title | Sub-step | Status |
|----|-------|----------|--------|
| 11 | validate_packet and gate_eligible | schema.py | outline |
| 12 | Three modes: OFF, SHADOW, ENFORCE | D15.1 policy | outline |
| 13 | model_dispatch — one door | D15.1 | outline |
| 14 | Hub readiness UI | D15.2 | outline |
| 15 | Replay envelope & shadow logs | implementation | outline |

---

## Part IV — Industry parallels (teaching agents)

| Ch | Title | Sources |
|----|-------|---------|
| 16 | Context packs & packets | ContextOS, AmtocSoft |
| 17 | Production RAG pipeline | GenAI Patterns, ThynkQ, Nic Chin |
| 18 | Plan-aware compression | PAACE |
| 19 | Orchestration interrupts | LangGraph |
| 20 | CI golden sets | RAGAS |

---

## Part V — Playbook (90 days)

| Ch | Title | Content |
|----|-------|---------|
| 21 | Month 1 — D5 + shadow | weeks 1–4 checklist |
| 22 | Month 2 — D7–D10 rule-based | weeks 5–8 |
| 23 | Month 3 — enforce | weeks 9–12 + validators |

---

## Agent role packets (from this book)

| Role | Read first | Responsibility |
|------|------------|----------------|
| **wtm-builder** | Ch 1–10 + WTM map locked | Ship D-steps, validators |
| **gate-operator** | Ch 11–15 + schema locked | Shadow/enforce policy |
| **hub-planner** | Ch 1, 13 | Never bypass model_dispatch |
| **critic-reviewer** | Alignment law + Ch 1 | Compare, attach, don't replace |

---

## Growth rule

New chapter **only** when a new `ESSAY_vN` is unified. No chapter from raw chat. Extract → gather → merge → unify → chapter.
