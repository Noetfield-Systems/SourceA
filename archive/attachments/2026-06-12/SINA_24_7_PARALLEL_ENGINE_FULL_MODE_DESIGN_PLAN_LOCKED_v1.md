# 24/7 Parallel Engine — Full-Mode Design + Week-1 Test Plan (LOCKED v1)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-12  
**ASF order:** Design complete big-picture automation · use all clouds/APIs · 10 parallel lines · first test before full 24/7  
**Parents:** `ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md` · `sina_engine_registry_v1.yaml` · `SOURCEA_FLEET_THREAD_ANALYSIS_MAP_LOCKED_v1.md` · `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md` · `SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md`  
**Human office:** M1 Canvas + `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` (**FORM_OFFICIAL**)  
**Note:** Disk says **Railway** (MergePack API deploy). **Raygun** (error monitoring) is optional observability — not on disk as primary SSOT.

---

## 0. One sentence

> **ONE SourceA motor governs every action; TEN parallel lanes run through a single integration fabric (n8n-first + Make/Zapier adapters + Railway/Vercel clouds); Week 1 is a bounded 24/7 *test harness* — not greenfield AUTO-RUN.**

---

## 1. What today’s messages mean (thread map)

| Today’s arc | Threads touched | Clock | Form row |
|-------------|-----------------|-------|----------|
| FORM = official human–machine conv | THREAD-INTEGRITY-100 · MAINTAINER | D | **Q-FORM-OFFICIAL** YES |
| Cross-chat alarm RIGHT/STALE/BAD | BRAIN · MAINTAINER · ECOSYSTEM | C+D | Q-M2-READ · Q-M2-FORM-SYNC |
| No Judge Chat — form + validators | BRAIN · ECOSYSTEM | C | Locked strategy |
| **This ask** — full automation · 10 lines · 24/7 test | ENFORCEMENT · AGENTFIELD · PORTFOLIO · WIRE | **C+B+E** | **New row below** |

**CLOCKS burning:** **C** (ENFORCEMENT-6MO W1–W3) · **B** (portfolio lanes) · **E** (n8n glue · COMM-PARTNER)

---

## 2. Design principles (law — do not violate)

| # | Rule | Law |
|---|------|-----|
| 1 | Motor before lanes | `sina_engine_registry_v1.yaml` L1 |
| 2 | n8n = glue · not SSOT | `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md` |
| 3 | No Cursor AUTO-RUN P0 | `auto-run-disabled-v1.flag` · INCIDENT-022 |
| 4 | Every fork on form | FORM_OFFICIAL · INCIDENT-029 |
| 5 | Receipt per ALLOW | Demo S3 · spine · W2 |
| 6 | Founder hub tap only on hot | ENFORCEMENT-6MO §3 |
| 7 | NF test first → 10-lane transfer | `SINA_THREAD_ACTIVATION` T10 gate |

---

## 3. Four-layer architecture (full mode — designed)

```text
┌─────────────────────────────────────────────────────────────┐
│ L4 FOUNDER — M1 Canvas · Hub Actions · final contact only   │
└────────────────────────────┬────────────────────────────────┘
┌────────────────────────────▼────────────────────────────────┐
│ L3 CONTROL — SourceA motor (:13020 hub · spine · validators) │
│   governance_propagation_cascade · live_founder_decision_form │
└────────────────────────────┬────────────────────────────────┘
┌────────────────────────────▼────────────────────────────────┐
│ L2 ORCHESTRATION — n8n (primary) · Make · Zapier (adapters)  │
│   schedules · webhooks · retry · observability hooks          │
└────────────────────────────┬────────────────────────────────┘
┌────────────────────────────▼────────────────────────────────┐
│ L1 INTEGRATION FABRIC — API registry (all clouds · all sites) │
│   Railway · Vercel · Apollo · HubSpot · OpenRouter · Runtime  │
└────────────────────────────┬────────────────────────────────┘
┌────────────────────────────▼────────────────────────────────┐
│ L0 TEN PARALLEL LANES — threads · workers · portfolio SKUs    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Integration fabric catalog (use everything — designed)

| Class | Tools on disk | Role in engine | SSOT? |
|-------|---------------|----------------|-------|
| **Deploy cloud** | Railway (MergePack API) · Vercel (frontends) | Health · KPI · deploy receipts | No — motor receipts |
| **Workflow glue** | n8n (:5678) · Make · Zapier | Triggers · retries · 24/7 schedules | **Glue only** |
| **Outbound** | Apollo · HubSpot pattern · Affinity | W3 sequences · CRM stages | Queue + receipt |
| **LLM transport** | OpenRouter · Cursor agent API | Worker ACT · eval | Cost-smart law |
| **Runtime** | SinaaiRuntime :8000 · Telegram liaison | Legacy bot path | Mono lane |
| **VC signal** | Crunchbase · Dealroom · Evertrace class | Thunderfield · research | P6 staging |
| **Voice (post-W3)** | Vapi · Telnyx · ElevenLabs class | FORGE-VOICE | Integrate not replace motor |
| **Observability** | Datadog patterns · **Raygun (optional)** | Error ingest → spine | Alert only |
| **Reference models** | `SINA__AND_REFERENCE_MATRIX_v1.yaml` | Precedent · not build order | Research |
| **Sites** | MergePack · TrustField · NF · 777 Vercel | Per-lane health probes | Lane receipts |

**Machine registry target:** `~/.sina/integration-fabric-registry-v1.yaml` (Maintainer ships — one row per API · env key name · webhook · receipt path)

---

## 5. Ten parallel lines (T20 — Week 1 test scope)

| # | Line ID | Thread | Primary API/cloud | 24/7 trigger (test) | Week 1 proof |
|---|---------|--------|-------------------|---------------------|--------------|
| **1** | MOTOR-ENF | THREAD-ENFORCEMENT | SourceA scripts | launchd / hub tick | write-path validator · dry-run 3× |
| **2** | LANE-NF | THREAD-NOETFIELD-W3 | Apollo/HubSpot | n8n schedule → queue | outreach batch 1 receipt |
| **3** | LANE-TF | THREAD-TRUSTFIELD | Same stack backup | standby webhook | deck + 3 conv logged |
| **4** | AGENTFIELD | THREAD-AGENTFIELD | n8n + LinkedIn prep | daily 09:00 queue | 1 agent-logged post receipt |
| **5** | FORGE | THREAD-FORGE | Forge repo · Vercel | manual + receipt | launch list row |
| **6** | MERGEPACK | THREAD-MERGEPACK | **Railway** API/KPI | health cron 15m | KPI trio JSON |
| **7** | WIRE | THREAD-WIRE | DevBridge spine | hub Action probe | G3 status receipt |
| **8** | MAINTAINER | THREAD-MAINTAINER | Hub rebuild | cascade on form change | hero = form-aware |
| **9** | RESEARCH | THREAD-RESEARCH | Acquisitor vault | weekly digest job | matrix cite in deck |
| **10** | MOTOR-STREAM | MOTOR-STREAM SKU | redis-stream pattern | spine event fanout | 1 event → 3 lane mirrors |

**Not headline Week 1:** Factory 1000 drain · GOV_UNIFY batch · full integrity 100-step · new Judge Chat.

---

## 6. n8n / Make / Zapier — division of labor

| Tool | When | Example flows |
|------|------|---------------|
| **n8n** (primary) | Mac-local · SourceA-adjacent · secrets in `~/.sina` | Health sweep · outreach queue · form-change webhook → hub refresh |
| **Make** | SaaS bridge when n8n node missing | Apollo→HubSpot stage sync |
| **Zapier** | Founder-friendly one-tap legacy | Calendar → CRM note (hub documents zap only) |

**Starter workflows (design):**

1. `wf-health-sweep-15m` — Railway + Vercel + hub :13020 + Runtime :8000  
2. `wf-w3-outreach-batch` — per `AGENTIC_W3_OUTREACH_WORKFLOW_SPEC_v1.md`  
3. `wf-form-change-cascade` — form JSON hash change → `governance_propagation_cascade_v1.py`  
4. `wf-spine-fanout` — one ALLOW receipt → 10 lane notification stubs  
5. `wf-agentfield-daily` — LinkedIn draft queue → founder hub approve  

---

## 7. Implementation phases

### Phase 0 — Design only (this doc) · 2026-06-12

- [x] 10-line map  
- [x] Integration fabric catalog  
- [x] Thread alignment  
- [ ] `integration-fabric-registry-v1.yaml` (Maintainer)  
- [ ] Form row **Q-ENGINE-TEST-01** (ASF PICK)  

### Phase 1 — Week 1 TEST harness (Jun 11–17) — **start here**

| Day | Ship | Owner |
|-----|------|-------|
| D1–D2 | `integration-fabric-registry-v1.yaml` stub (10 APIs) | Worker |
| D2–D3 | n8n `wf-health-sweep-15m` + hub **Start n8n** card test | Worker |
| D3–D4 | `wf-w3-outreach-batch` dry-run (no send without hub approve) | Worker + Commercial |
| D4–D5 | MOTOR-ENF: `validate-demo-write-path-v1.sh` + 3× dry-run | Worker |
| D5–D7 | Spine fanout stub → log only · 24/7 monitor receipt | Worker |

**Week 1 exit:** 5 workflows designed · 3 running in **test mode** · health receipt every 15m on disk.

### Phase 2 — Week 2–4 (ENFORCEMENT Phase I)

- Film W1 · Hub demo Action (S8)  
- Outreach batch 1 live (founder approve via hub)  
- Railway KPI + MergePack wired to hub card  
- Make/Zapier only if n8n gap proven  

### Phase 3 — Month 2 (bounded 24/7)

- All 10 lines have health + receipt row  
- NF lane TEST PASS → T10 transfer template  
- No new clouds until W2 green  

### Phase 4 — Full mode (post-W3 gate)

- Scale Zapier/Make for non-Mac founders  
- Raygun/Datadog optional ingest  
- FORGE-VOICE · FF-MARKET post-W3  

---

## 8. 24/7 test mode definition (Week 1)

**TEST ≠ production AUTO-RUN.** Test means:

```text
SCHEDULE (n8n/launchd) → PROBE (health) → LOG (receipt) → NOTIFY (hub/spine)
                         → STOP if validator FAIL or FREEZE flag
                         → NO outbound send without founder hub approve row
```

| Runs 24/7 Week 1 | Does NOT run 24/7 Week 1 |
|------------------|---------------------------|
| Health sweep 15m | Cursor agent factory drain |
| Form hash watcher | Auto LinkedIn post |
| Spine append | GOV_UNIFY |
| KPI pull Railway | New LOCKED law from chat |

---

## 9. API setup checklist (full mode design)

| API | Env / secret home | Receipt path | Lane |
|-----|-------------------|--------------|------|
| Railway | MergePack service vars | `mergepack_ship_status_v1.json` | 6 |
| Vercel | per frontend | hub ops card HTTP | 5,6 |
| n8n | local :5678 | `~/.sina/n8n-health-v1.json` | 4, all |
| Apollo | `~/.sina/secrets/apollo` | outreach receipt JSONL | 2,3 |
| HubSpot | pattern doc | CRM stage log | 2,3 |
| OpenRouter | existing | eval_1b_ci_mode | 1 |
| Hub :13020 | local | cascade receipt | 8 |
| Runtime :8000 | Mono | liaison status | 7 |

---

## 10. Form picks required (FORM_OFFICIAL)

| ID | Question | Recommended |
|----|----------|-------------|
| **Q-M2-FORM-SYNC** | Sync all rows to Canvas | YES |
| **Q-ENGINE-TEST-01** | Approve Week-1 24/7 **test harness** (5 n8n flows · health only · no auto-send) | YES |
| **Q-ENGINE-TEST-02** | Primary orchestrator: **n8n-first** · Make/Zapier adapters only | YES |
| **9.07 A** | W1 film + NF W3 batch 1 parallel | Already §ANSWERED |

---

## 11. Risks (honest)

| Risk | Mitigation |
|------|------------|
| “Use all APIs” = scope explosion | Integration registry · one receipt per API |
| 24/7 breaks FREEZE | Test harness stops on flag |
| Chat becomes SSOT | FORM_OFFICIAL · every lane motion → form row |
| Railway ≠ motor | Railway is lane 6 deploy · motor stays SourceA |
| Raygun confusion | Optional L1 observability — not governance SSOT |

---

## 12. Brain routing (immediate)

| Owner | Week 1 |
|-------|--------|
| **Worker** | integration registry stub · n8n wf 1–3 · write-path validator |
| **Maintainer 2** | Hub n8n cards · form-sync · regulator Action |
| **Commercial** | W3 batch 1 targets · Apollo list |
| **ASF** | PICK Q-ENGINE-TEST-01 on Canvas · hub approve batches |
| **Brain** | This plan · board assign · no implementation |

---

*END — design complete · implement Phase 1 Week 1 test only until ASF PICK*
