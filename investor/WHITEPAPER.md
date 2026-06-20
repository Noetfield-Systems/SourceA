# White paper — Portfolio operating system for multi-business founders

**Version:** 1.0  
**Date:** June 2026  
**Classification:** Confidential — for investors, advisors, connectors  
**Author:** ASF (founder)

---

## Abstract

This document describes a **portfolio operating system** used to run several real businesses from a single founder-led stack. The system combines (1) governance and priority law, (2) a Mac-based production environment, (3) an orchestration brain (SinaPromptOS), and (4) phone-based remote control. **Customer value** is delivered per portfolio company through live products, pilots, and contracts — not through internal connectivity tests. A separate commercial program (Cursor OS Pro) targets the App Store remote-IDE category and is intentionally excluded from the portfolio investment narrative unless the session is SKU-specific.

---

## 1. Introduction

### 1.1 Founder context

ASF operates multiple entities in parallel — including delivery-stage platforms (TrustField, VIRLUX), a runtime/control plane (Sinaai MonoRepo), a foundation (777), and a future enterprise product line (Noetfield). Traditional tooling assumes one startup, one repo, one desk. This portfolio required:

- **One ranked view** of what matters today across companies.
- **Repeatable execution** (plan → task → implement → verify → log).
- **Remote triggering** when the founder is not at the Mac.

### 1.2 What this paper is not

- Not a research paper on LAN pairing or smoke tests.
- Not the product specification for the App Store application (see `SEPARATE_PROGRAM_CURSOR_OS_PRO.md`).
- Not a public git document — governance master files are local and internal.

---

## 2. Problem statement

| Pain | Business impact |
|------|-----------------|
| Context switching across five repos | Weeks lost; nothing ships |
| Founder must be at desk | Deals and field work delayed |
| No single execution log | Investors/advisors can’t see progress |
| AI chats without governance | Drift, wrong app opened, unsafe automation |

**Investment relevance:** Capital should accelerate **customer-visible milestones**, not internal QA.

---

## 3. Solution overview

### 3.1 Three layers

| Layer | Name | Investor-facing description |
|-------|------|----------------------------|
| **0** | Capability | Phone can start Mac production (home + away). **Proven.** |
| **1** | Execution | Each company’s repo receives today’s task; work is verified and logged. **In progress.** |
| **2** | Result | Live product, pilot, contract, subscription. **What we fund.** |

### 3.2 Components (plain language)

| Component | Role |
|-----------|------|
| **Source A** | Law: priority, ports, SSOT, architect reports — what wins when docs disagree |
| **SinaPromptOS** | Brain: dispatch, ingest, orchestrator, daily manifests |
| **AI Dev Bridge** | Internal remote desk + Mac agent (not sold as v1 SKU) |
| **Per-company repos** | Where customer value is built and deployed |
| **Cursor OS Pro** | Separate commercial remote-IDE app (App Store) |

### 3.3 Golden path (internal — one sentence)

Phone → RUN SYSTEM → Mac orchestrator → reports and plan updates → (handoff to Cursor) → implement → deploy → **customer demo**.

**Known gap:** Automatic paste into all Cursor chats is paused until Mac Cursor is standardized and safe one-repo dispatch is enabled. Work orders are still **generated**; handoff may be manual or per-repo from the phone Agent screen.

---

## 4. Governance and thinking

### 4.1 Authority model

```text
ASF (human) → final override
Sina OS governance → structure and naming
Execution logs + plans → evidence for advisors
Code → implements declared structure; does not define it
```

### 4.2 Anti-patterns we reject

- Treating “PASS on phone” as a funding milestone.
- Mixing internal orchestra with App Store product in one pitch.
- Blocking company A’s ship because company B’s blocker exists (**force majeure** parallel lanes).
- Uncontrolled multi-chat UI automation (learned from production incident — safety lock).

### 4.3 How we think about AI

AI is **labor amplification**, not the product:

- **Dispatch** proposes today’s best task per repo from plans and feedback.
- **Cursor IDE** implements in repo context.
- **VERIFY** scripts and human review gate merges and deploys.
- **Ingest** turns chat outcomes into structured logs for the next cycle.

Investors should evaluate **cycle time to live URL**, not model brand.

---

## 5. Portfolio entities (customer results)

### 5.1 TrustField Technologies

- **Category:** Trust / field operations (delivery plane).
- **Near-term result:** Postgres validation → production path → client demo.
- **Customer pays for:** Reliable platform, compliance-ready workflows.

### 5.2 VIRLUX

- **Category:** Commerce / luxury stack (delivery; ecosystem rank #1).
- **Near-term result:** Staging smoke → production pilot.
- **Customer pays for:** Live storefront / B2B commerce outcomes.

### 5.3 Sinaai MonoRepo (PAIOS)

- **Category:** Runtime spine (`:8000`), governance mirror, Telegram approval gates.
- **Near-term result:** Runtime health check; wire-human approval gate on bot.
- **Customer pays for:** Platform reliability for dependent products.

### 5.4 The 777 Foundation

- **Category:** Mission, web presence, field partnerships (delivery).
- **Near-term result:** Homepage content pass; gate-0 outreach execution (founder-field).
- **Customer pays for:** Programs, partners, donors — not “automation PASS.”

### 5.5 Noetfield

- **Category:** Enterprise knowledge / audit (design → build).
- **Near-term result:** Spec sections → tenant/audit schema outline → build activation.
- **Customer pays for:** Future enterprise license — today sell **milestone + vision**.

---

## 6. Current situation (June 2026)

See `CURRENT_SITUATION.md` for detail. Summary:

| Area | Status |
|------|--------|
| Remote ops (LAN + Tailscale) | Operational |
| Multi-repo dispatch + ingest | Operational |
| Auto-paste all Cursor chats | Paused (safety); manual / one-repo dispatch |
| Per-company customer demos | **Primary focus now** |
| Cursor OS Pro TestFlight | Separate track |

---

## 7. Roadmap philosophy

- **12 months:** Each entity has at least one **showable** artifact per quarter (URL, pilot, LOI, TestFlight for Pro only).
- **Metrics:** Paying accounts, pilot LOIs, deploy frequency, founder hours at desk — not run counts.
- **Funding gates:** Release capital tranche on **named deliverable**, not “orchestrator v2.”

Full table: `ROADMAP.md`.

---

## 8. Competitive framing

| Alternative | Limitation | Our approach |
|-------------|------------|--------------|
| Single-repo Cursor | No portfolio law | Source A + ranked architect |
| Generic PM tools | No Mac execution | Direct orchestrator + agent |
| Offshore team | Slow loop | AI + VERIFY + founder override |
| No remote ops | Founder tied to desk | Phone production trigger |

---

## 9. Security and compliance (summary)

- Mac-local execution; secrets not committed to repos.
- Tailscale for remote access (private mesh).
- Explicit safety locks on UI automation.
- Per-entity compliance follows **that business’s** domain (TrustField, etc.) — not one-size-fits-all in this paper.

---

## 10. Investment thesis (portfolio)

**Thesis:** A founder operating several SMB/product lines can outperform siloed competitors by **cycle time** and **oversight** if governance + remote production are first-class.

**What capital unlocks:** Parallel customer milestones (VIRLUX pilot, TrustField prod, Mono spine), not R&D on “can the phone connect.”

**What success looks like in 12 months:** At least two entities with **non-founder revenue or binding pilot**, plus a credible Noetfield build path.

---

## 11. Appendix — glossary (for advisors)

| Term | Meaning for business audience |
|------|------------------------------|
| Dispatch | Generate today’s task files per company |
| Ingest | Record what Cursor/agents produced into logs |
| RUN SYSTEM | Phone button to start production pipeline on Mac |
| G1/G2/G3 | Internal wire phases — **do not use in investor room** |
| M8 | Mac Cursor handoff — **automation to chats** |
| Force majeure | Company blockers don’t stop other companies’ wire |

---

*End of white paper v1.0*
