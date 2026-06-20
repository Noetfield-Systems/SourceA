# AUTO-CONFLICT Example — Agent Stack Policy v1 (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**INTERNAL ONLY — MacBook SourceA — NOT for GitHub / NOT public online**

| Field | Value |
|-------|-------|
| **Version** | 1.0 — LOCKED |
| **Status** | Worked example — how ACE v3 resolves DESIGN vs EXECUTION without fake SSOT |
| **Authority** | ASF — structural edits on Desktop only |
| **Visibility** | `INTERNAL_LOCAL_ONLY` — never commit to git, never push to remote |
| **Canonical location** | `/Users/sinakazemnezhad/Desktop/sourceA/AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md` |
| **Local mirror (gitignored)** | `Noetfield/ops/private/sourceA/AUTO_CONFLICT_EXAMPLE_AGENT_STACK_POLICY_v1_LOCKED.md` |
| **Locked** | 2026-06-01 |
| **Governs under** | `AUTO_CONFLICT_ENGINE_V3_LOCKED.md` |
| **Subject documents** | `SINAAI_AGENT_STACK_POLICY_v1.md` (DESIGN) · `SinaaiRuntime/` (EXECUTION) |

---

## Purpose

This file is a **locked reference case** for future agents and founders.

It shows a real situation where:

- A **policy doc** declares intent (leader/worker chains, Tier 0 keys, multi-agent flow).
- **Runtime** already runs a different but valid shape (single `BRAIN_MODEL_CHAIN`, working OpenRouter failover).
- An analyst might wrongly call that **“policy violation”** or **“runtime ahead / behind.”**

**ACE v3 resolution:** Each plane owns its domain. No single layer owns all truth. **Not a Type C boundary conflict.**

---

## Situation (2026-06-01)

### What looked like a conflict

| Observation | Old (wrong) reading |
|-------------|---------------------|
| Policy says Phase 0 = declare only; Phase 1 = wire chains | “Runtime broke policy by wiring `BRAIN_MODEL_CHAIN`” |
| Policy lists `AGENT_LEADER_CHAIN` + `AGENT_WORKER_CHAIN` | “Runtime is behind — only one chain exists” |
| Policy leader models differ from live OpenRouter model IDs | “Runtime is wrong — must match policy text exactly” |
| Strategic research listed 38 APIs; policy lists Tier 0 top 11 | “Policy incomplete vs research” |
| `.env` has empty Groq/Cerebras keys | “System failed policy” |

### ACE v3 re-read (correct)

| Plane | Artifact | Role in this case |
|-------|----------|-------------------|
| **DESIGN** | `SINAAI_AGENT_STACK_POLICY_v1.md` | Declares **target** LLM/agent architecture: roles, vendor diversity, never-silent north star |
| **EXECUTION** | `SinaaiRuntime/.env`, `brain_providers.py`, `ai_gateway.py` | **Proves** what works today: Gemini → OpenRouter failover, live model IDs |
| **DELIVERY** | Noetfield GitHub (when shipping) | Separate product plane — **not** controlled by mono agent-stack policy scope |

**Key line (locked):** Policy describes · Runtime proves · Repo ships.

---

## R9 tagging (mandatory language)

❌ **Wrong (plane collapse):**

> “The agent stack policy is wrong because runtime uses different models.”  
> “Runtime is ahead of policy and must be rolled back to Phase 0.”

✅ **Correct:**

> `[DESIGN]` Agent stack policy v1 declares leader/worker chains and Tier 0 key priority.  
> `[EXECUTION]` Runtime currently runs a single `BRAIN_MODEL_CHAIN` with verified OpenRouter failover (`openrouter/owl-alpha`, etc.).  
> `[DESIGN]` Phase 1 wires `AGENT_LEADER_CHAIN` + `AGENT_WORKER_CHAIN` and maps agents to providers.  
> `[EXECUTION]` Groq/Cerebras keys empty — steps skipped until keys added; not a boundary breach.

---

## Drift classification (locked for this case)

| Item | Type | Action |
|------|------|--------|
| Policy Phase 0 vs runtime wiring | **A — Informational** | None — EXECUTION may experiment under ACE Rule 1 |
| Missing leader/worker env vars vs policy intent | **A — Informational** | Phase 1 EXECUTION work when ASF approves |
| Policy OpenRouter model names vs live working IDs | **A — Informational** | Update DESIGN doc when ASF locks names; runtime keeps proof |
| Empty Groq/Cerebras keys | **A — Informational** | Add keys per Tier 0 — capacity gap, not architecture conflict |
| Runtime `BRAIN_READONLY_MODE` / caution flags | **A — Informational** | EXECUTION regime label (R7) |
| Agent stack policy scope vs Noetfield GitHub product | **Not a conflict** | Different planes — see ACE C1–C2 |

**Not Type C (boundary):** Runtime did not redefine SSOT, product identity, or registry promotions.

---

## How ACE rules apply (R1–R9 snapshot)

| Rule | Application |
|------|-------------|
| **R2** | SinaaiMonoRepo = DESIGN + EXECUTION for mono stack |
| **R4** | Runtime is reality; policy ideal documents gaps only |
| **R5** | Not “debt” unless contract, boundary, or safety broken |
| **R7** | Label topology regime (single chain vs dual leader/worker) |
| **R8** | Agents read SourceA; do not edit Desktop locks |
| **R9** | Always tag `[DESIGN]` vs `[EXECUTION]` in cross-plane statements |

---

## Locked alignment with strategic research

The **DESIGN** policy correctly compresses multi-vendor / leader-worker research into enforceable intent:

| Research theme | Policy lock |
|----------------|-------------|
| Never one vendor for entire chain | Absolute Rule R1 |
| Leader = one synthesis after workers | Agent map + multi-agent flow |
| OpenRouter breadth first | Tier 0 #1 |
| Groq workers, Cerebras volume, Gemini limited | Tier 0 #2–4 + agent map |
| Ollama last | L7 + LAST chain |
| Langfuse before scaling agents | R6 |
| ~100–200 calls/day when Tier 1 stacked | Achievable in EXECUTION when keys wired |

**Research is input. Policy is DESIGN lock. Runtime is proof.**

---

## Locked conclusions (do not re-litigate)

1. **`SINAAI_AGENT_STACK_POLICY_v1.md` is valid DESIGN** — keep as EXECUTION intent map for LLM/agent ops.
2. **Runtime experiments are valid EXECUTION** — not policy violations under ACE v3.
3. **“Ahead / behind” is the wrong frame** — use plane sovereignty and drift type A.
4. **Phase 1** = wire leader/worker chains and keys as EXECUTION catching up to DESIGN — not fixing a fake SSOT conflict.
5. **Read order for runtime LLM work:**
   - `SINA_OS_SSOT_LOCKED.md`
   - `AUTO_CONFLICT_ENGINE_V3_LOCKED.md`
   - `SINAAI_AGENT_STACK_POLICY_v1.md`
   - **This example** (when plane confusion arises)
   - `system_registry.json` (ledger)
   - `SinaaiRuntime/`

---

## When to use this example

Use this file when an agent or session claims:

- “Policy and runtime contradict — one must win.”
- “Runtime must stop until policy Phase 1 is complete.”
- “Working models in `.env` invalidate the policy.”
- “Research list and policy Tier 0 list are in conflict.”

**Response:** Apply ACE v3 — tag planes, classify drift, execute and learn.

---

## Document control

| Version | Date | Note |
|---------|------|------|
| 1.0 | 2026-06-01 | LOCKED — first ACE worked example (Agent Stack Policy v1) |

**If Desktop and `ops/private/sourceA/` mirror diverge, Desktop wins.**
