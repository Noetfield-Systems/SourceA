# Competitor Parity Matrix — 4 Categories × 7 Capabilities

**Saved:** 2026-06-15T20:08:53Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** v1 · **Date:** 2026-06-15 · **Plan:** PLAN-280 · **Status:** External-eye draft

> **Authority:** `COMPETITOR_LANDSCAPE_300_PLAN_2026-06-15_v1.md` · intake 30-map · research report Tier 1 L6 peers. **Sales use:** NW1 · AF-SPRINT · discovery calls — label competitor cells **HYPOTHESIS** unless verified on buyer call. **Do not** quote competitor revenue.

**Legend:** ✔️ core · ◐ partial / integration-dependent · — absent or not primary · **SA** = SourceA engine · **NF** = Noetfield face

---

## Matrix 1 — Category exemplars (30-map anchors)

| Capability | **A Gateways** (Portkey · Kong · Cloudflare) | **B GRC / Mgmt** (Credo · OneTrust · watsonx · ServiceNow) | **C AI Security** (Lakera · Cisco · Straiker · [external-design-benchmark]) | **D Observability** (AgentOps · Arize · Langfuse) | **SA / NF** |
|------------|---------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------|---------------------------------------------------|-------------|
| **Policy at dispatch (pre-execution BLOCK)** | ◐ content/PII guardrails · API traffic | ◐ policy registry · guardrails via integrations | ◐ prompt/I/O firewall · runtime detect | — observe only | **✔️** critic_boot · pre-LLM gate |
| **Per-action agent authorization (not session-only)** | — routing layer | ◐ tool permissioning (Credo GAIA) | ◐ MCP/runtime block (Straiker) | ◐ HITL pause (AgentOps) | **✔️** every dispatch |
| **Signed receipt per action** | ◐ audit trails · not tamper-evident chain | ◐ evidence packs · traces · PDFs | — detection logs | ◐ session audit trail | **✔️** spine JSONL + validators |
| **Tamper FAIL on read (validator-on-read)** | — | — | — | — | **✔️** demo wedge |
| **Replay from signed ledger** | — | ◐ via integrations | — | **✔️** AgentOps closest | **✔️** full chain replay |
| **Live demo <5 min cold start** | ◐ gateway dashboards | — slide-heavy | — red-team reports | ◐ trace UI | **✔️** BLOCK→ALLOW→tamper→replay |
| **Copilot / M365 board-grade export** | — | ◐ Purview native · Securiti readiness | **✔️** [external-design-benchmark] Studio focus | — | **✔️ NF** TLE · board PDF · proc ZIP |
| **Self-hosted / law-first disk proof** | ◐ LiteLLM OSS · else SaaS | — SaaS-first | — SaaS / appliance | ◐ OSS tiers | **✔️** founder stack |
| **Enterprise sales / SIEM / SOC2 machine** | **✔️** incumbents | **✔️** | **✔️** | ◐ | **— weak** (honest) |

**Category win lines (PLAN-283):**
- **A:** “Guardrails on prompts ≠ signed receipts on agent actions.”
- **B:** “PDF compliance and policy mapping ≠ runtime enforcement at dispatch.”
- **C:** “Prompt firewalls and detection ≠ provable action ledger.”
- **D:** “Replay and HITL pause ≠ policy enforced before the model acts.”
- **SA/NF:** “One chain: dispatch → enforce → sign → replay → tamper FAIL — live in five minutes.”

---

## Matrix 2 — Tier 1 L6 architectural peers (research report)

| Capability | Notenic | FuseGov | AgentPEP | Predicate | Microsoft Auth Fabric | **SA / NF** |
|------------|---------|---------|----------|-----------|----------------------|-------------|
| Pre-execution BLOCK | **✔️** GRE / admissibility | **✔️** boundary enforcement | **✔️** OPA/Rego PEP | **✔️** sub-ms sidecar | **✔️** Entra PEP+PDP | **✔️** |
| Signed receipt / attestation | ◐ | ◐ evidence packs | ◐ | **✔️** crypto ledger | ◐ audit log | **✔️** tamper-evident |
| SSOT re-brief on law change | — | — | — | — | — | **✔️** briefing fingerprint |
| Validator-on-read tamper FAIL | — | — | — | ◐ | — | **✔️** |
| Copilot-specific SKU | — | — | — | — | **✔️** Azure-native | **✔️ NF** |
| Self-hosted / neutral | ◐ | ◐ | **✔️** OSS | **✔️** sidecar | — Azure lock-in | **✔️** multi-lane |
| Enterprise GTM maturity | **✔️** | ◐ | — OSS | — early | **✔️** | **—** |

**Peer win line:** “Same PEP pattern — we add **validator-on-read tamper FAIL**, **LOCKED SSOT re-brief**, and **Noetfield board export** on one disk stack.”

---

## Matrix 3 — NW1 room rivals (Noetfield lane · PLAN-067)

| Capability | Securiti Copilot | [external-design-benchmark] | Microsoft Purview | Credo AI GAIA | **Noetfield NF-RD** |
|------------|------------------|--------|-------------------|---------------|---------------------|
| Copilot readiness / discovery | **✔️** data-centric | **✔️** Studio sprawl | **✔️** native | ◐ inventory | ◐ shadow deploy |
| Runtime block before action | ◐ | ◐ AIDR | ◐ Auth Fabric (separate SKU) | ◐ | **✔️** policy at dispatch |
| Cryptographic receipt + tamper FAIL | — | — | — audit metadata | ◐ traces | **✔️** |
| Board PDF / procurement ZIP | ◐ assessment | ◐ | ◐ compliance reports | ◐ | **✔️** deliverable |
| Pilot time-to-value | months | weeks–months | E5 cycle | months | **4–6 weeks** NF-RD |
| Price entry (public signals) | enterprise SaaS | enterprise | E5 bundle | mid–six fig | **$5–10K CAD** band · $2K deposit |

**NW1 win line:** “Purview tells you something happened. Noetfield proves what was **permitted**, under which **policy version**, with **tamper-evident** export for the board.”

---

## Matrix 4 — Closest replay rival (PLAN-068c · CL-029)

| Capability | AgentOps | **SourceA** |
|------------|----------|-------------|
| Session replay / time-travel | **✔️** | **✔️** replay from ledger |
| HITL approval gates | **✔️** | **✔️** founder tap gate |
| Policy enforce **at dispatch** | — | **✔️** |
| Tamper-evident signed chain | — | **✔️** |
| Loop detection | **✔️** | ◐ factory monitors |
| Live tamper FAIL demo | — | **✔️** |

**Win line:** “AgentOps lets you **pause and replay**. SourceA **blocks before execution** and proves the record wasn’t altered.”

---

## Matrix 5 — Gateway objection pack (PLAN-068a · CL-001/003/004)

| Capability | Portkey | Kong AI GW | Cloudflare AI GW | **SourceA** |
|------------|---------|------------|------------------|-------------|
| Model routing / cache | **✔️** | **✔️** | **✔️** | — (use as transport) |
| PII / content guardrails | **✔️** | **✔️** | **✔️** DLP | ◐ not primary wedge |
| Agent **action** authorization | — | — | — | **✔️** |
| Signed action ledger + replay | — | — | — | **✔️** |
| Partner pattern | **✔️** mount SA above gateway | same | same | **✔️** neutral layer |

**Win line:** “Keep your gateway. Mount governance **above** it — receipts on what agents **do**, not just what prompts contain.”

---

## Summary scorecard (category averages · qualitative)

| Category | Strongest at | Weakest vs SA/NF | Our attack angle |
|----------|--------------|------------------|------------------|
| A Gateways | Scale · routing · content filters | Action-level signed receipts | Partner + enforce layer |
| B GRC | Board trust · reg mapping · SIEM | Inline dispatch enforcement | PLAN-283 PDF ≠ runtime |
| C Security | Threat detect · MCP scan · Copilot surface ([external-design-benchmark]) | Tamper-evident ledger | Live demo · receipt artifact |
| D Observability | Replay UX · evals · traces | Pre-execution BLOCK | PLAN-068c enforce vs observe |
| L6 Peers | PEP speed · enterprise narrative | SSOT re-brief · tamper FAIL demo | Disk law · self-hosted proof |
| **SA / NF** | Proof density · law-first · pilot speed | Enterprise GTM · SIEM breadth | **Proof beats prose** |

---

## Acceptance (PLAN-280)

| Gate | Status |
|------|--------|
| 4 category columns + SA/NF column | **PASS** |
| 7+ capability rows | **PASS** (9 rows) |
| Tier 1 L6 peer table | **PASS** |
| NW1 + AgentOps + Gateway slices | **PASS** |
| Win lines per slice | **PASS** |
| Linked from 300-plan pack | **PASS** |

**Next:** PLAN-068a–d one-pagers (optional) · monthly refresh via PLAN-276 · wire win lines into NW1 battle card append.

---

## Pointers

| Doc | Path |
|-----|------|
| 300-plan pack | `COMPETITOR_LANDSCAPE_300_PLAN_2026-06-15_v1.md` |
| 30-map intake | `SOURCEA_NOETFIELD_COMPETITOR_LANDSCAPE_2026-06-15_v1_3.md` |
| Research report | `SOURCEA_COMPETITOR_LANDSCAPE_RESEARCH_REPORT_v1.md` |
| NW1 battle card | `NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` |

*End PLAN-280 artifact · external-eye draft · verify competitor cells before investor deck*
