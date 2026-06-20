# Prompt OS — two-layer model (dynamic router vs static REGISTRY)

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  
**Debate sources:** Claude dynamic routing proposal vs static 10k REGISTRY; auditor verdict  

---

## Question

Should SourceA replace the `sourcea-1000` REGISTRY with a fully dynamic `prompt_router`?

**Auditor verdict: NO — use both layers.**

---

## Layer 1 — Dynamic routing (runtime)

| Component | Path | Role |
|-----------|------|------|
| `prompt_router.py` | `scripts/prompt_router.py` | Route founder intent → template + context |
| SinaPromptOS | `SinaPromptOS/core/prompt_library.py` | Template library |
| Hub API | `:13020` | CLI + HTTP after hub up |

**Strengths:** Adaptive tasks, fast iteration, founder-facing flexibility  
**Weaknesses:** Harder to machine-verify completeness; drift without gates  

**Status:** SHIPPED — CLI + API OK (post hub restart)

---

## Layer 2 — Static REGISTRY (verify)

| Component | Path | Role |
|-----------|------|------|
| REGISTRY | `os/plan-library/sourcea-1000/REGISTRY.json` | 1000 task states |
| Pick | `scripts/plan-no-asf-run.sh` | Next `sa-XXXX` |
| Validator | `validate-sourcea-1000-pack.sh` | Pack integrity |

**Strengths:** Machine verify, do_not_redo, audit trail, worker closeout discipline  
**Weaknesses:** Slow to extend; not a product UX  

**Status:** 101 done / 899 backlog — validated

---

## Why not delete the pack

1. **Gates and honesty** depend on verify tasks (Eval-1b scaffold 7/7)  
2. **do_not_redo** prevents worker rework loops  
3. **PRIORITY evidence rows** tie to `sa-XXXX` IDs  
4. **find_critical_bugs** fleet includes pack validators  
5. Router alone cannot prove platform completeness %

---

## Recommended architecture

```
Founder intent
    ├─► Layer 1: prompt_router → template + pre_llm context  (product path)
    └─► Layer 2: sa-XXXX worker task → REGISTRY closeout     (verify path)
```

**Brain routes Layer 2 pick.** **Router serves Layer 1** when founder asks ad-hoc work inside governance.

---

## Dynamic vs static comparison

| Dimension | Dynamic router | Static REGISTRY |
|-----------|----------------|-----------------|
| Flexibility | High | Low |
| Verify | Low | High |
| Drift risk | Medium | Low |
| Founder UX | Better ad-hoc | Better queue discipline |
| Autonomy gates | Needs honest synthesis | Tied to eval tasks |

---

## Implementation notes

- Do not build 10k static prompts in REGISTRY — tasks are **verify units**, not prompt text  
- Router should **read** PRIORITY + brain rules — not invent law  
- `dispatch_ready=false` applies to **both** until Eval-1b live  

---

## Conclusion

**Keep REGISTRY.** **Ship router** (done). Integrate router as Layer 1 front-end; REGISTRY remains Layer 2 spine for worker OS and machine truth.
