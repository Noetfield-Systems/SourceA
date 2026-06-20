# AgentField — Controlled Automation Sprint

**Saved:** 2026-06-15T21:32:29Z · **Retrofit:** doc-datetime-law batch retrofit
### Agent loops with signed receipts — built on SourceA, not generic glue
*2026-06-15 · v1 · fast-cash lane · external-eye draft*

> **Reconciliation note.** AgentField is the **agentic ops face** on the SourceA engine (`SINA_UNIFIED_ENGINE_STORY` · portfolio SSOT §3). This is a **services SKU draft** for weeks-to-cash engagements — compare against `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` §6 (Buyer 1 product path) and Noetfield NW1. **Do not send as LOCKED law** until founder sign-off. Hook is **governance-instrumented automation**, not undifferentiated “we build agents.”

---

**The problem.** You want agentic automation — outreach loops, ops workflows, research agents — but most vendors deliver scripts with no audit trail. When something misfires, you cannot prove what ran, what was blocked, or whether logs were tampered with. You get automation; you do not get **proof**.

**What AgentField delivers.** We design and ship **one production-grade agent loop** on the same stack we run daily: policy at dispatch, brokered execution, signed receipts, replay, and tamper-evidence. You get working automation **and** a procurement-grade record of every action — not a black box.

**The proof — in under five minutes.** Before we scope, you see the chain live:

> **request → policy evaluation → decision → enforcement → signed receipt → replay → tamper-FAIL → signed audit chain**

Same proof density as Noetfield and SourceA Buyer 1 demos. One engine; three buyer surfaces.

---

## SKU: AF-SPRINT (project)

| Term | Detail |
|------|--------|
| **Price** | **CAD $3,000–$10,000** (scoped to one workflow) |
| **Duration** | **2–4 weeks** |
| **Scope** | One agent loop (e.g. outreach queue, ops handoff, research digest) wired to SourceA spine |
| **Deliverables** | Runnable workflow · policy gates at dispatch · signed receipt ledger · replay demo · export bundle (JSONL + SHA chain) · handoff doc |
| **Success metric** | One number agreed up front (e.g. *N approved sends/week*, *% actions with signed receipt*, *MTTR on failed runs*) |
| **Mode** | Shadow or parallel — no mandatory production cutover on day one |

## SKU: AF-RETAIN (ongoing)

| Term | Detail |
|------|--------|
| **Price** | **CAD $2,000–$5,000 / month** |
| **Duration** | 3-month minimum · month-to-month after |
| **Scope** | Maintain + extend 1–2 loops · monitor receipts · tune policy · monthly proof export |
| **Deliverables** | Same receipt spine · incident replay on demand · founder-approved irreversible actions only |

---

## Who this is for

- **Platform / ops teams** already running or piloting agents — need automation **and** auditability without a 6-month procurement cycle.
- **AI-native startups** (Series A–C) with a technical champion who can sign a small PO or card — aligns with SourceA **Buyer 1** profile.
- **Not for:** enterprise RFP / SOC 2-first buyers (route to Noetfield NF-RD or Buyer 3 path).

**Separation law (do not blur in pitch):**
- **AgentField** — agentic ops + scoped loops (this doc).
- **Noetfield** — Copilot / M365 compliance buyer (board PDF, TLE, procurement ZIP).
- **SourceA** — infra / SDK / embed (Buyer 1 self-serve eval).

---

## Why us vs a generic automation shop

| Generic “build you agents” | AgentField controlled sprint |
|----------------------------|----------------------------|
| Scripts + Zapier/n8n glue | Policy **before** execution · brokered dispatch |
| Logs if the vendor remembers | Signed receipt on every action |
| “Trust us” on incidents | Replay from ledger · tamper **FAIL** on export |
| No case study for your board | Same stack powers our own factory — live reference |

**ROI for you:** one founder-equivalent team delivers several scoped loops at near-fixed infra cost — you buy **leverage with proof**, not hours.

---

## Typical sprint arc

1. **Discovery (60 min)** — one workflow, one metric, shadow vs live.
2. **Live proof (15 min)** — full chain demo, cold start.
3. **Build (week 1–2)** — loop + policy gates + receipts on spine.
4. **Handoff (week 2–3)** — replay walkthrough · export bundle · runbook.
5. **Optional convert** — AF-RETAIN · Noetfield NF-RD · or SourceA Buyer 1 SDK.

---

## Next step

**15-minute live proof** + 30-minute scoping call. We quote AF-SPRINT fixed-fee or AF-RETAIN monthly after scope is one workflow and one metric.

**Parallel motion:** Noetfield Copilot governance pilots run on the same engine — ask if compliance/board packaging is the primary buyer; we route to NF-RD without losing the scoped loop.

---

*AgentField is powered by SourceA — pre-LLM controlled execution: policy at dispatch, ledger + replay, tamper-evidence. Brand only until separate legal entity (ENG-06).*
