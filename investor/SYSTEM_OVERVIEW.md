# System overview — for non-technical readers

**Question this answers:** “How does ASF run several businesses without chaos?”

---

## The picture

```text
                    ┌──────────────────┐
                    │  ASF (founder)   │
                    │  final decisions │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ Source A   │ │ iPhone     │ │ Advisors   │
       │ law/priority│ │ remote desk│ │ milestones │
       └─────┬──────┘ └─────┬──────┘ └────────────┘
             │              │
             ▼              ▼
       ┌─────────────────────────────────┐
       │ Mac — production floor           │
       │  • Agent (files, terminal)       │
       │  • SinaPromptOS (brain)          │
       │  • Cursor IDE (build)          │
       └─────────────┬───────────────────┘
                     │
     ┌───────┬───────┼───────┬───────┐
     ▼       ▼       ▼       ▼       ▼
 TrustField VIRLUX  Mono   777   Noetfield
     │       │       │       │       │
     └───────┴───────┴───────┴───────┘
                     │
                     ▼
            Customer-visible result
            (URL, app, contract)
```

---

## Five parts (remember five words)

| Part | Word | What it does |
|------|------|--------------|
| 1 | **Law** | Source A — who is priority today, which ports, what is locked |
| 2 | **Brain** | SinaPromptOS — dispatch tasks, ingest results, architect refresh |
| 3 | **Remote** | Phone desk — start production, see PASS/FAIL, dispatch one repo |
| 4 | **Build** | Cursor + repos — real code and deploy |
| 5 | **Result** | Live product per company — **only thing investors fund** |

---

## A day in the life (result-oriented)

1. **Morning:** Brain ranks companies (e.g. VIRLUX #1 today).
2. **Dispatch:** Today’s task files written for each repo.
3. **Founder:** From desk or phone — start pipeline or send one company’s task to Cursor.
4. **Build:** Cursor implements in that repo.
5. **Verify:** Scripts + human check.
6. **Deploy / demo:** Staging or prod URL.
7. **Advisor update:** “VIRLUX staging live” — not “we ran automation.”

---

## What the phone is

A **remote control for the production floor** — like starting a factory shift from your car.

Not the factory output. Not what you invoice.

---

## What is intentionally separate

**Cursor OS Pro** = product for **App Store buyers** (remote IDE).  
**This system** = how **ASF runs owned businesses**.

Same Mac can host both; **story must not mix** in one investor meeting.

---

## One paragraph for a connector email

ASF operates multiple technology businesses under one governance and execution stack. The founder can trigger the same Mac-based production pipeline from a phone, including off-network, while each company moves toward its own live product and revenue. We are now focused on customer-visible milestones (staging pilots, production demos, foundation programs), not internal connectivity proofs.
