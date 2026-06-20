# INCIDENT-038 — Agent conflated Mac control · Worker · cloud · secondary plans

**Saved:** 2026-06-20T18:35:00Z · **Version:** 1.1 LOCKED (ASF correction v2)  
**Class:** Agent reasoning · execution-plane vocabulary · Mac Law misread  
**Reporter:** ASF — two corrections in same thread  
**Agent:** Cursor Auto · **sequence_id:** SA-2026-06-20-INCIDENT-038  
**Opened:** 2026-06-20 · **Amended:** 2026-06-20 (v1.1 — removes wrong “Worker runs every plan” law)  
**Related:** INCIDENT-020 · INCIDENT-003b · INCIDENT-034 · Mac Law agent execution plane lock  
**Status:** REMEDIATED v1.1 — disk vocabulary corrected to ASF final law

---

## 1. What happened (timeline)

| Step | Agent behavior | ASF correction |
|------|----------------|----------------|
| 1 | Listed 100 `sa-mkt-*`  plans as “cloud/FORGE only — no factory on Mac.” | Secondary pack — **not Mac work at all.** |
| 2 | Agent over-corrected: **“Worker on Mac runs every plan.”** | **100% wrong.** ASF: Worker **cannot factory-build on Mac.** |
| 3 | ASF: secondary 5000 plans **we don’t touch on Mac** · cloud/API free tier + affordable OpenRouter. | Mac = **control only.** |
| 4 | ASF: **“worker cant do anything in mac!!! no factory building”** | Final law locked below. |

---

## 2. ASF final law (LOCKED — agents must obey)

```text
Mac           = control panel ONLY (Hub · form · glance · optional ONE cloud dispatch · read receipts)
                NO factory building · NO plan-by-plan execution · NO secondary pack work on Mac

Secondary     = 5000  plans (5 stacks × 1000) · cloud/API batch drain ONLY
                Mac NEVER executes them · NOT Worker · NOT Cursor implement · NOT RUN INBOX per sa-mkt

Primary       = also builds on cloud/API · Mac does NOT factory-build locally

Cloud         = FORGE · Railway FBE · cloud_api_worker · free tier first · OpenRouter affordable second
```

**Founder-facing one-liner:**

> **Mac observes and controls. Cloud/API runs all factory work. Secondary 5000 never touch Mac. Worker on Mac does NOT run every plan — FORBIDDEN.**

---

## 3. Agent errors (both directions)

| Error | Wrong sentence | Why forbidden |
|-------|----------------|---------------|
| **E1** | “Cloud/FORGE only” for 100  plans | Implies Mac/chat can skip control law · treats secondary as Mac queue |
| **E2** | “Worker on Mac runs every plan” | **Opposite of ASF law** · Worker does **not** factory-build on Mac · does **not** execute secondary bulk |
| **E3** | Listing sa-mkt as “next legitimate plans for agent” in this chat | Secondary REGISTRY is **not** Mac execution queue |

---

## 4. Three lanes (never collapse)

| Lane | Mac? | Who executes |
|------|------|--------------|
| **Mac control** | YES | Hub · form · session gate · read receipts · optional Hub POST to cloud |
| **Secondary -1000** | **NO** | Cloud cron/tick · FORGE · free LLM chain · OpenRouter cap |
| **Factory body (any plan)** | **NO on Mac** | Cloud/API only |

**Forbidden forever:**

- “Worker on Mac runs every plan”
- “RUN INBOX per sa-mkt” on Mac for secondary
- “Worker picks + implements”  bulk on Mac
- Any Mac factory build (motors · render · autorun · local LLM factory spend)

---

## 5. Correct chain (secondary 5000)

```text
Mac Hub (optional one POST) → cloud tick picks batch → free tier research → affordable fallback
→ evidence + receipt in cloud/Supabase → Mac reads progress ONLY
```

Mac never enters the loop body for secondary.

---

## 6. Never again — agent checklist

```
1. SECONDARY? → cloud/API only · Mac never executes · do not list as Worker queue
2. MAC LAW? → control panel only · no factory building on Mac
3. NEVER say "Worker on Mac runs every plan" — INSTANT FAIL (INCIDENT-038)
4. NEVER say "cloud only" without "Mac control · cloud body executes · Mac does not build"
5. Plan lists for founder = cloud drain policy · not Cursor turn lists for Mac
6. READ data/mac-worker-vs-factory-vocabulary-v1.json before Mac Law + plans reply
```

---

## 7. Remediatilocally (v1.1)

| Artifact | v1.1 fix |
|----------|----------|
| `data/mac-worker-vs-factory-vocabulary-v1.json` | Removed “Worker runs every plan” · added `secondary_cloud_only` |
| `data/mac-law-agent-execution-plane-lock-v1.json` | Removed `worker_on_mac_required` · Mac control-only clarification |
| `data/founder-reply-glossary-v1.json` | Forbidden phrase registered |
| `docs/MAC_LAW_AGENT_EXECUTION_PLANE_LOCK_LOCKED_v1.md` | §1b rewritten |
| `scripts/agent_memory_mirror_v1.py` | Inject line corrected |
| `scripts/mac_law_agent_execution_plane_lock_v1.py` | Surface line: `mac-control-only` not `worker-on-mac=YES` |

| `data/secondary-cloud-drain-next-100-v1.json` | Legitimate next 100: 10 Mac control · 90 cloud secondary |

---

## 8. Legitimate next 100 (NOT Mac sa-mkt queue)

**SSOT:** `data/secondary-cloud-drain-next-100-v1.json`

| Range | Plane | Count | Mac executes plan body? |
|-------|-------|-------|-------------------------|
| 1–10 | `mac_control` | 10 | **NO** — validate · dry-run · read receipt only |
| 11–100 | `cloud_forge` | 90 | **NO** — maps `sa-mkt-0001…0090` · cloud batch drain |

**NOT legitimate:** listing `sa-mkt-*` as Mac Worker RUN INBOX implement queue.

---

## 9. Related incidents

| ID | Link |
|----|------|
| **020** | Topic conflation · slogan became whole story |
| **034** | Prohibition without positive disk wire |
| **017** | Queue phase-order drift |

---

**LOCKED v1.1** — canonical body · INCIDENT-038
