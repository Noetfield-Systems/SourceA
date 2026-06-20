# Architecture the Market Pays For — Receipt-Native Agent Governance (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
status: LOCKED
doc_date: 2026-06-10
sequence_id: SA-2026-06-10-MARKET-RECEIPT-ARCH
-->

| | |
|--|--|
| **Version** | `SOURCEA-MARKET-RECEIPT-ARCH-1.0-LOCKED` |
| **Purpose** | External positioning + internal north star — what enterprises buy vs what factory drains |
| **Companions** | `SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md` · `SOURCEA_1000PACK_AUDIT_JUDGE_LOCKED_v1.md` |
| **Honest counter** | `python3 scripts/goal-progress-v1.py` → `honest_done` |
| **Validator** | `validate-sourcea-market-receipt-arch-locked-v1.sh` |

---

## The problem (June 2026)

Fast AI builders — Lovable, Bolt, Replit, vibe-coded agents — ship **speed without proof**.

Enterprises (banks, law firms, healthcare, logistics, regulated SaaS) cannot adopt them because compliance asks one question:

> **What did the AI do, when, and how do we know it was right?**

Today most tools answer with chat logs and hope. That fails NIST AI RMF audit-trail expectations, SOC 2 evidence requests, and internal risk committees.

**The gap is not “more intelligence.” It is governed execution with machine-verifiable closeout.**

---

## What the market pays for (the SKU)

| Buyers pay for | Buyers do not pay for |
|--------------|----------------------|
| Provable agent runs | A 1000-task prompt registry |
| Validator-gated closeout | WTM D-layer research maps |
| Receipt + event chain | Chat optimism and YAML `done` |
| Incident + drift history | “We used AI” slide decks |
| Exportable audit evidence | Faster codegen alone |

**Product name (internal SKUs):** **RunReceipt** · **FORGE Governance Layer** · “Receipt-native agent governance”

**Price band (positioning, not yet invoiced):** $50K–$200K/yr enterprise · $5K–$15K/mo mid-market — *after pilot proof*

---

## What SourceA already has on disk (honest)

### The spine (real — this is the product core)

```text
Worker run
  → machine validators
  → receipts/sa-XXXX-receipt.json (timestamp, status)
  → closeout_gate_v1.py (blocks fake completion)
  → VALIDATOR_PASS → TASK_CLOSED → BROKER_ACK
  → brain-os/incidents/ (documented failures + fixes)
```

| Mechanism | Path / proof |
|-----------|--------------|
| Receipt per honest task | `receipts/sa-XXXX-receipt.json` |
| Closeout gate | `scripts/closeout_gate_v1.py` |
| Event chain | `scripts/closeout_sa_task.py` |
| Honest progress | `scripts/goal-progress-v1.py` — **receipt-backed only** |
| Incidents | `brain-os/incidents/` |
| Founder UI | `http://127.0.0.1:13020` (Sina Command) |

### Scale proof (factory floor — not the invoice line item)

- **Governed automation factory** drains `sourcea-1000` to prove the spine at volume
- **152+ honest receipts** (refresh via `goal-progress-v1.py`) — not “every task ever”
- Phase-first law (018): s0→s2 immune system before celebrating s6 volume

### What is not yet enterprise-complete (say this in sales)

| Gap | Why it matters | Fix |
|-----|----------------|-----|
| **s2 hub/CI = 0%** | “Correctness” needs immune-system validators green | Phase-first drain |
| **No paying pilot on disk** | Architecture ≠ revenue (PREMORTEM-017) | 1 demo + 1 call |
| **Monitor :13021** | Often down — use **:13020** | Package L3 ops on :13020 |
| **Single-tenant Mac factory** | Enterprises need export / tenancy story | FORGE port + docs |
| **SOC2/NIST** | Directionally aligned — not certified | Pilot-driven roadmap |

---

##  frame (accurate, not arrogant)

| Player | Offers | SourceA difference |
|--------|--------|-------------------|
| Fast builders | Speed | No proof chain |
| **Microsoft Agent Governance Toolkit (Apr 2026)** | Enterprise governance patterns | You **run** receipt-native governance daily on a real factory |
| Cursor / agents | Execution | No default closeout gate |
| **SourceA spine** | **Receipt → gate → broker → incident** | Already operational — **152+ audited runs** |

**Say:** “We operationalized agent governance for our own factory first.”  
**Do not say:** “We replaced Microsoft.”

---

## The three-layer buyer story

| Layer | Buyer question | Your answer today |
|-------|----------------|-------------------|
| **L1 — Proof** | Show me one agent run | Receipt JSON + validator PASS |
| **L2 — Control** | How do you block fake “done”? | `closeout_gate_v1.py` |
| **L3 — Operations** | How does compliance monitor this? | Hub :13020 + export roadmap (s2 strengthens claim) |

**Sell L1+L2 now. Finish L3 via s2 + FORGE packaging.**

---

## 90-second demo script (make Part 1 true in a meeting)

1. Open one `receipts/sa-0084-receipt.json` — timestamp, status, sa_id  
2. Show validator command from receipt evidence row  
3. Trace `VALIDATOR_PASS → TASK_CLOSED → BROKER_ACK` in closeout flow  
4. Open one incident doc — “we document failures, not hide them”  
5. Close: **“152 governed runs on disk — not chat logs.”**

---

## Internal law (do not drift)

| Law | Meaning |
|-----|---------|
| Factory ≠ SKU | 1000-pack **proves** the spine; **receipt governance** is what you sell |
| Honest counter only | `honest_done` — never REGISTRY YAML fiction |
| Phase-first | s2 before enterprise “correctness” claims |
| Parallel revenue | TrustField demos use **same spine**, different domain — separate calendar |
| Semantic memory (014) | After AUTH-LIVE — amplifies Pre-LLM, not the first invoice |

---

## One-line gold

> **The market pays for provable agent runs. SourceA already built the receipt-native governance spine on disk — the 1000-pack is the factory floor that proves it scales; RunReceipt/FORGE is what you invoice.**

---

## Citations

- `COMMERCIAL_GOAL-REF-1000PACK-AUDIT-018` — factory vs product
- `COMMERCIAL_GOAL-REF-GPT-EMBED-CRITIC-JUDGE-014` — AUTH-LIVE before embed
- PREMORTEM-017 — architecture without pilot
- `SOURCEA_LAYERED_ADVISORY_DRAFT_v1.md` — β+ hybrid motion

---

*End SOURCEA_MARKET_RECEIPT_ARCHITECTURE_LOCKED_v1*
