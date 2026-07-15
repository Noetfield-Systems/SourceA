# Master system audit — Parts 1–17 (evidence-only)

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  
**Method:** Read-only inspection — validators, PRIORITY, REGISTRY, hub APIs, file counts  
**No new law.** Interpretation labeled explicitly.

---

## Part 1 — Scope and method

- **Repos in scope:** SourceA (primary), SinaPromptOS, SinaaiDataBase (archive), `~/.sina/` state  
- **Evidence:** `find_critical_bugs.py`, strict build, `validate-sourcea-1000-pack.sh`, hub `:13020`, `plan-no-asf-run.sh pick`  
- **Out of scope:** Production customer traffic, cloud deploy truth beyond file references  

---

## Part 2 — System identity

**Verdict:** Controlled multi-repo **execution OS** + **pre-LLM context compiler**.  
**Not:** Autonomous product (Lovable/Devin class).  
**Control plane** for founder-controlled worker execution with machine verify pack.

---

## Part 3 — Repository topology

```
Founder
  └── Hub :13020 (sina-command-server.py + agent-control-panel/)
  └── SourceA spine (law, validators, scripts, REGISTRY)
  └── SinaPromptOS (prompt_library, dispatch-day)
  └── ~/.sina/ (runtime closeouts, brain mirror, logs)
  └── SinaaiDataBase (archive chat — not ops lane)
```

---

## Part 4 — Law and governance

| Evidence | Finding |
|----------|---------|
| 138 `*_LOCKED*.md` | High law surface; search-first required |
| `BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md` | Brain routing index |
| `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | No Terminal law |
| `validate-founder-docs-no-terminal-v1.sh` | CRITICAL in `find_critical_bugs` |
| T0+T1 pack | **DONE** — F1/F2/M2/M4 + PRIORITY evidence row |

**Gap:** M4 `founder-reply-lint.sh` via `~/.cursor/hooks.json` — **warn only**, not block.

---

## Part 5 — Machine truth chain

1. `SOURCEA-PRIORITY.md` — evidence rows, do_not_redo, commercial  
2. `REGISTRY.json` — 1000-pack task states  
3. `plan-no-asf-run.sh pick` — live next worker ID  
4. Hub `strategic_synthesis_hub.py` — honest gates (`dispatch_ready`, `eval_1b_gate_ok`)  

**Consistency at save:** pick **sa-0202**, REGISTRY **101 done**.

---

## Part 6 — Validator fleet

| Check | Result (hub up) |
|-------|-----------------|
| `find_critical_bugs` | 0 critical |
| Strict build | PASS |
| `validate-sourcea-1000-pack` | PASS (1000 tasks) |
| Founder docs no-terminal | PASS |
| Governance fleet in FCB | Present (refactor sa-0107) |

---

## Part 7 — Hub and control panel

| Component | Status |
|-----------|--------|
| `sina-command-server.py` | UP :13020 |
| Autonomy APIs (`prompt_router`, execution kernel) | OK after hub restart |
| `agent-control-panel/` | UI present |
| sa-queue tab | **NOT IMPLEMENTED** |
| Stale process risk | 404 on autonomy routes until restart |

---

## Part 8 — REGISTRY / sourcea-1000

- **Total:** 1000 tasks validated  
- **Done:** 101  
- **Backlog:** 899  
- **Purpose:** Layer-2 machine verify — keep pack; do not replace with router alone  
- **Current pick:** sa-0202 (s2 hub-build-ci)

---

## Part 9 — Autonomy stack

| Module | Status |
|--------|--------|
| `prompt_router.py` | SHIPPED — CLI + API OK |
| `execution_kernel_v0.py` | Present; state can block new tick |
| `execution-kernel-v1` API wrapper | **BUG** — passes `--json`, v0 rejects |
| `agent_loop.py` | Hub integration |
| Level 3 zero-human | **Not shipped** |
| `dispatch_ready` | `false` (honest) |

---

## Part 10 — Pre-LLM pipeline

- Path: `scripts/pre_llm/`  
- Role: Context compiler before LLM — retrieval, packing, policy hooks  
- WTM steps A1–D16: ~30 DONE at module+validator level (see PRE_LLM_AND_WTM_EVIDENCE doc)  
- D5 embeddings: PARTIAL (hash_local)  
- C7 dispatch: shadow (`dry_run=True`)

---

## Part 11 — Eval-1b and gates

| Gate | Value | Blocker |
|------|-------|---------|
| `eval_1b_gate_ok` | false | OpenRouter 402 |
| Scaffold | 7/7 100% | PASS |
| Live eval | blocked | structural_only mode |
| Commercial lever | OpenRouter top-up | Founder action |

---

## Part 12 — Rule-breaking diagnosis

**Root causes:**
1. Law logged without pre-reply enforcement  
2. Contradictory founder docs (T0+T1 fixed)  
3. Chat ≠ persistent memory  
4. 141+ LOCKED files — easy to miss one  
5. Cursor default “run bash” reflex  

**T0+T1 status:** DONE logged. **Remaining:** M4 block (not warn), hub queue UX.

---

## Part 13 — Prompt OS architecture

**Auditor consensus:** Two-layer model  
- Layer 1: Dynamic `prompt_router` + SinaPromptOS templates  
- Layer 2: Static REGISTRY for verify  

**Do not:** Delete 1000-pack for “dynamic only” routing.

---

## Part 14 — Commercial parallel

Open threads (from PRIORITY / brain extraction):  
TrustField P10, CanadaBuys, PacifiCan/BDC LIFT, OpenRouter, G3 Tailscale, MergePack Vercel, Canada AI funding alignment.

**Gates block live dispatch** — commercial demos can proceed on structural/scaffold paths.

---

## Part 15 — Technical debt register

| ID | Item | Severity |
|----|------|----------|
| TD-1 | execution-kernel `--json` mismatch | P1 |
| TD-2 | Hub sa-queue tab missing | P1 |
| TD-3 | M4 warn-only hook | P1 |
| TD-4 | ARCHITECT_REPORT 5 rejected YAML ingests | P2 |
| TD-5 | CANADA_AI not in important_docs_index | P2 |
| TD-6 | NOETFIELD_GOVERNANCE_PLANE path missing | P2 |
| TD-7 | Runtime :8000 down | P3 (optional E2E) |

---

## Part 16 — Risk matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hub stale → API 404 | Medium | High | Restart procedure; health check |
| Founder Terminal drift | Medium | High | M4 block hook |
| Gate false negative | Low | High | Honest synthesis (shipped) |
| REGISTRY/pick drift | Low | Medium | validate pack + pick script |
| OpenRouter outage | High | Medium | Credits + fallback structural |

---

## Part 17 — CTO verdict and single lever

**Verdict:** Architecture is **real and unusually complete** for a solo-founder control plane; **autonomy and commercial live paths** lag by design (gates honest).  

**Platform:** Alpha+  
**Hub:** Beta−  
**Sites/products:** Production−  

**Single highest-leverage action:** OpenRouter credits → Eval-1b live PASS → unlock dispatch gate chain.

**Next worker:** `sa-0202` per live pick.

---

*Full detail tables: see sibling files in `docs/system-audits/`.*
