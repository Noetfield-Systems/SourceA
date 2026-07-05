> **ARCHIVED 2026-07-05T13:00:00Z** — lineage only. See `docs/archive/superseded-law-v1/`.

# Sinaai Agent Stack Policy — One Pager
## Runtime LLM & Agent Infrastructure (Declaration)

> **SUPERSEDED for doctrine:** `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` (§7–8).  
> Keep this file as a quick Runtime LLM cheat sheet only. Do not add new rules here.

**Version:** 1.0  
**Status:** Phase 0 — Policy declaration only (no build until Phase 1 + ASF approval)  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3  
**Scope:** `SinaaiRuntime/` only — not Noetfield, not Layer A governance  
**Location:** `/Users/sinakazemnezhad/Desktop/sourceA/SINAAI_AGENT_STACK_POLICY_v1.md`  
**Visibility:** `INTERNAL_LOCAL_ONLY` — never commit to git, never push online  
**Locked:** 2026-05-31

---

## Purpose

Declare how **SinaaiRuntime** stays online: multi-agent roles, multi-vendor failover, research tools, memory, and observability — so Telegram and the fleet **never go silent** when one API quota dies.

**North star:** Capacity + roles + failover + visibility — not one best model.

---

## Stack Layers (bottom → top)

| Layer | Component | Role |
|-------|-----------|------|
| L0 | **Upstash Ratelimit** (or local guard) | Per-provider RPM protection |
| L1 | **LiteLLM** (self-host) or **OpenRouter** | Single router in front of all LLM keys |
| L2 | **Leader chain** | One synthesis step after multi-agent discussion |
| L3 | **Worker pool** | Fast, cheap, high-volume agent tasks |
| L4 | **Research** | Tavily (keyless → free key) + Exa backup |
| L5 | **Memory** | Supabase (primary) + existing event bus / SQLite tasks |
| L6 | **Observability** | Langfuse (agent trace trees) |
| L7 | **Last resort** | Ollama local (`OLLAMA_ENABLED=false` until declared active) |

---

## Agent → Provider Map (locked intent)

| Agent | Job | Primary | Backup | Do NOT use for |
|-------|-----|---------|--------|----------------|
| **liaison / brain** | Strategy, final reply | DeepSeek R1 (OpenRouter free) | Gemini 2.5 Flash | Worker models |
| **analyst** | Interpret, patterns | Cerebras | Mistral Small (batch) | Leader chain |
| **lead_scout** | Facts, web | Tavily + Groq 8B | Exa | Leader models |
| **outreach_writer** | Drafts, volume | OpenRouter `:free` models | Mistral batch | DeepSeek R1 |
| **operator** | Execute, scripts | Groq 8B instant | Cerebras 8B | Any leader model |
| **batch / overnight** | Summarize, ingest | **Mistral Experiment** (1B tok/mo) | Ollama local | Real-time Telegram |

**Rule:** Leadership = **one designated synthesis step** after workers — not whichever agent answered first.

---

## Tier 0 — Keys & Services (implement in Phase 1)

| Priority | Service | Why |
|----------|---------|-----|
| 1 | OpenRouter | One key, many free models + failover breadth |
| 2 | Groq | Fast Telegram workers |
| 3 | Cerebras | High daily token volume |
| 4 | Google Gemini | 1–2 leader models only (not 5) |
| 5 | **Mistral Experiment** | 1B tokens/mo — batch/overnight only (2 RPM) |
| 6 | GitHub Models | Hard decisions (~50–150/day) |
| 7 | Tavily | Scout research (keyless MCP → free key) |
| 8 | Langfuse | Multi-agent debate visibility |
| 9 | LiteLLM (self-host) | Clean gateway replacing ad-hoc chain logic |
| 10 | Upstash Redis + Ratelimit | Quota guard + optional queue scale |
| 11 | Ollama | Final local fallback only |

**Already in stack (use, don’t duplicate):** Supabase, event bus, fleet orchestrator, SQLite tasks, n8n `:5678`, GitHub Lab, Telegram `@SinaaiOSbot`.

---

## Leader vs Worker Chains (policy order)

```text
LEADER (synthesis):
  openrouter:deepseek/deepseek-r1-0528:free
  → gemini:gemini-2.5-flash
  → openrouter:meta-llama/llama-3.3-70b-instruct:free
  → github-models:gpt-4o (hard cases only)

WORKER (volume):
  groq:llama-3.1-8b-instant
  → gemini:gemini-2.5-flash-lite
  → cerebras:llama-3.1-8b
  → openrouter:openrouter/free
  → mistral:mistral-small (batch)

LAST:
  ollama:qwen3:4b or llama3.2:3b
```

**Principle:** Alternate **vendors** in chain — never stack 5 models from the same provider.

---

## Multi-Agent Flow (Telegram)

```text
Human (Telegram)
  → liaison (route)
  → WORKERS in parallel (scout / analyst / writer) — cheap models
  → event_bus publish/subscribe
  → LEADER synthesis (one call)
  → reply to Telegram
```

Human approval gate (production): agent actions affecting live systems require **Telegram confirm from ASF** before execute.

---

## Absolute Rules (Runtime)

| # | Rule |
|---|------|
| R1 | Never one vendor for entire chain — quota death = silence |
| R2 | Leader models never burn on trivial worker tasks |
| R3 | Cloud-first default; Ollama = last resort unless registry changes |
| R4 | Noetfield compliance path stays isolated — Runtime agents read-only on Noetfield data |
| R5 | New providers require registry note — no ad-hoc keys without declaration |
| R6 | Observability required before scaling agent count (Langfuse or equivalent) |
| R7 | Subtraction over addition — one canonical Telegram path; freeze v1/v2/v3 |

---

## Phase Gate

| Phase | This document |
|-------|---------------|
| **Phase 0 (now)** | Declare policy only — no wiring, no new env keys in production |
| **Phase 1** | Wire `AGENT_LEADER_CHAIN` + `AGENT_WORKER_CHAIN`, map agents, verify never-silent test |
| **Phase 2** | Git-tracked governance mirror + CI enforcement |

**Phase 1 exit test:** Kill Gemini quota → system still replies via Groq/Cerebras/OpenRouter/Ollama within 30s on Telegram.

---

## Conflicts

On conflict with any other doc: **`SINA_OS_SSOT_LOCKED.md` v3 wins.**  
This file wins over README, agent memory, and prior chat outputs for **Runtime LLM ops only.**

---

## Read Order (Runtime sessions)

1. `SINA_OS_SSOT_LOCKED.md`  
2. **This file**  
3. `PHASE1_UNIFIED_BLUEPRINT_v2_3.md` (when Phase 1 starts)  
4. `SinaaiMonoRepo/AGENTS.md`

---

**ASF approval:** ___________________   **Date:** __________
