# Architecture synthesis — GPT meta vs Cursor audit

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  

---

## GPT meta-critique (validated)

**Claim:** Reframe from “autonomous dev product” to **“control plane for controlled execution.”**

**Auditor verdict: ACCEPT.** Evidence supports:
- 138 LOCKED law files, 67 validators — governance-first  
- Honest gates (`dispatch_ready=false`) — not fake autonomy  
- Hub + worker + REGISTRY — OS pattern, not app builder  
- Pre-LLM compiler — infrastructure, not UX wow-factor  

---

## What was overclaimed (before reframe)

| Overclaim | Disk truth |
|-----------|------------|
| “Level 3 zero-human shipped” | NOT shipped |
| “Live dispatch ready” | `dispatch_ready=false` |
| “Lovable ” | ~10% on product UX axis |
| “Devin-class agent” | ~18% autonomy score |

---

## What is underclaimed

| Underclaimed | Disk truth |
|--------------|------------|
| Validator fleet | 67 scripts, 0 critical when hub up |
| Law surface | Unusually complete for solo founder |
| 1000-pack verify | 101 done, pack validated |
| Two-layer prompt OS | Router + REGISTRY both real |
| T0+T1 enforcement | DONE logged |

---

## Control plane stack (ASCII)

```
┌─────────────────────────────────────────────────────────┐
│  Founder (No Terminal) — Hub :13020                     │
├─────────────────────────────────────────────────────────┤
│  Strategic synthesis · Gates · Actions · Private agents │
├──────────────┬──────────────────────┬───────────────────┤
│  Brain lane  │  Worker lane         │  Commercial lane  │
│  PRIORITY    │  sa-XXXX closeout    │  TrustField, etc. │
│  BRAIN_RULES │  REGISTRY update     │  parallel         │
├──────────────┴──────────────────────┴───────────────────┤
│  Pre-LLM compiler (scripts/pre_llm/)                    │
├─────────────────────────────────────────────────────────┤
│  prompt_router (L1) · execution_kernel · agent_loop     │
├─────────────────────────────────────────────────────────┤
│  Validators · LOCKED law · ~/.sina/ state               │
└─────────────────────────────────────────────────────────┘
```

---

## vs market positioning

| Comparator | Relationship |
|------------|--------------|
| Lovable | Product UX ~10% — different category |
| Devin/Atom | Autonomy ~15% — gates honest |
| Cursor | Tool inside worker lane — not the OS |
| LangSmith/LangGraph | Closest analog for pre-LLM + trace — but law-heavy |

**Category:** Controlled execution OS + context compiler.

---

## GPT vs Cursor agreement matrix

| Topic | GPT | Cursor audit | Agreement |
|-------|-----|--------------|-----------|
| Control plane framing | Yes | Yes | ✓ |
| Keep REGISTRY | Implied | Explicit | ✓ |
| Router as L1 | Yes | Yes | ✓ |
| Eval-1b blocker | Credits | 402 | ✓ |
| Hub not product | Yes | Beta− | ✓ |
| Delete LOCKED law | No | No | ✓ |

---

## Strategic implication

Invest in **gate unlock** (Eval-1b live) and **founder UX** (hub queue, M4 block) before **L3 autonomy** marketing. The architecture is ahead of the commercial story; honesty is a feature, not a bug.
