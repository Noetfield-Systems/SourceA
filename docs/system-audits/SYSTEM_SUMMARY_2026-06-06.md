# System summary — executive

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z · **Evidence base:** live validators, PRIORITY, REGISTRY, hub APIs  
**Classification:** Governed multi-repo execution OS + pre-LLM context compiler (control plane, not product)

---

## One sentence

A governed local execution OS with **101/1000** verify tasks done, **prompt_router** shipped, **honest gates** off live dispatch, **0 critical bugs** when hub is up — next work is **sa-0202**, kernel `--json` fix, and **OpenRouter credits** for Eval-1b live.

---

## What the system is

| Layer | Role |
|-------|------|
| **SourceA spine** | Law (`*_LOCKED*.md`), validators (`validate-*.sh`), scripts, hub, REGISTRY |
| **Pre-LLM compiler** | `scripts/pre_llm/` — context assembly before model call |
| **Hub control plane** | `:13020` — synthesis, gates, autonomy APIs, agent panel |
| **Worker lane** | One `sa-XXXX` per session via `plan-no-asf-run.sh` |
| **Brain lane** | Routes from PRIORITY + BRAIN_RULES; SinaaiDataBase = archive only |

**Not:** Lovable/Devin-style autonomous builder. **Is:** governed execution + verify pack + founder-safe hub ops.

---

## Live machine truth (save time)

| Signal | Value |
|--------|-------|
| Hub | `:13020` UP |
| `find_critical_bugs` | **0** critical |
| Strict build | **PASS** |
| REGISTRY | **101 done / 899 backlog** |
| Live pick | **sa-0202** (phase s2 hub-build-ci) |
| `dispatch_ready` | `false` |
| `eval_1b_gate_ok` | `false` (OpenRouter 402, structural_only) |
| T0+T1 enforcement | **DONE** |
| `prompt_router` | **SHIPPED** |
| Runtime `:8000` | DOWN (optional for SourceA E2E) |

---

## Scale on disk (SourceA)

| Asset | Count |
|-------|-------|
| Python | ~358 |
| Markdown | ~1260 |
| LOCKED law docs | ~138 |
| `validate-*.sh` | ~67 |
| Scripts | ~218 |
| `~/.sina/` state files | 414+ |

---

## Three automation layers (do not confuse)

1. **`plan-no-asf-run.sh`** — REGISTRY pick + worker routing  
2. **SinaPromptOS dispatch-day** — prompt factory / templates  
3. **Hub `agent_loop.py`** — synthesis + autonomy APIs  

---

## Two-layer prompt model (recommended)

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **1** | Dynamic `prompt_router.py` + templates | Runtime routing, founder tasks |
| **2** | `sourcea-1000` REGISTRY | Machine verify — **do not delete pack** |

---

## Maturity scores (interpretation, not disk facts)

| Dimension | ~Score |
|-----------|--------|
| Platform completeness | 38% |
| Architecture modules | 72% |
| Autonomy | 18% |
| Commercial | 28% |
| vs Lovable | ~10% |
| vs Atom | ~15% |

**Maturity labels:** Alpha+ (platform), Beta− (hub), Production− (individual sites)

---

## Top blockers

1. **Eval-1b live** — OpenRouter 402; gates stay false  
2. **`execution-kernel-v1`** — passes `--json` but `execution_kernel_v0.py` rejects it  
3. **Hub sa-queue tab** — not implemented (CLI only)  
4. **M4 reply hook** — warns only, does not block Terminal violations  
5. **Stale hub process** — autonomy APIs 404 until restart (operational)  

---

## Highest-leverage action

**OpenRouter top-up** → Eval-1b live PASS once → `dispatch_ready` / `eval_1b_gate_ok` can flip honest.

---

## Founder ops (no Terminal)

- Hub: Refresh, Actions, Private agents (`agent_workspace_registry.py` — 8 agents)  
- Brain: read PRIORITY + pick; route **one** `sa-XXXX`  
- Archive chat (SinaaiDataBase): audits only — ops in SourceA worker  

---

## Related saved artifacts

See [README_INDEX.md](./README_INDEX.md) for full audit pack list.
