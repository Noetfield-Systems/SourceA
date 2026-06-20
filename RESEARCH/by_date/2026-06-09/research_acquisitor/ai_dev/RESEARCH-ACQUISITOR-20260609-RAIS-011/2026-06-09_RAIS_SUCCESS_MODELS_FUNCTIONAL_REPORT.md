# RAIS & World Success Models — Functional Report + Golden Suggestion

**Saved:** 2026-06-09T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `RESEARCH-ACQUISITOR-20260609-RAIS-011`  
**worker:** Research Acquisitor · **execution_authority:** false  
**date:** 2026-06-09 · **subject:** ai_dev / SourceA advantage

**Cites:** Maintainer skills ship · `CONTROLLED_EXECUTION_OS_MASTER_LOCKED_v1.md` · `PREMORTEM-JUDGE-017` · `GOLDEN-010`

---

## Executive summary — golden suggestion

You asked how **RAIS-class systems** and **2026 world success models** actually function — and how SourceA turns that into a **fully functional, smart advantage**.

**Golden suggestion in one line:**

> **SourceA already built the functional core of what enterprises buy from Raia (control plane), Keon (receipt-before-effect), and RAISE (lifecycle gates) — on your disk, with honest receipts, for ~$9/681 tasks. Maintainer’s agent skills ship (2026-06-09) is the missing “playbook layer” that makes it repeatable. Your advantage is not copying Devin’s cloud rent — it is receipt-bound controlled execution + portfolio skills + Hub one-tap, sustained until Kill #6 passes, while TF/NF invoices in parallel.**

**Critical vocabulary (locked):** In SourceA law, **RAIS = external analog only** — never an internal layer name. Compare Raia / RAISE / Keon / Devin — do not rename D1–D16 or `~/.sina/` “RAIS.”

---

## Part I — What “RAIS” means in your system vs the market

| Term | What outsiders mean (June 2026) | SourceA locked meaning |
|------|--------------------------------|------------------------|
| **Raia** (raiaai.com) | Enterprise AI accelerator — Command control plane, Copilot HITL, Chat, Control campaigns | **Analog** — study Command UX + governance bundle |
| **RAISE** (theraiseframework.com) | Eight-pillar agent governance framework — inventory, monitor, guardrails, recover | **Analog** — map pillars to validators + events |
| **Keon** (keon.systems) | Controlled effect boundary — cognition free, effects receipt-bound via MCP | **Analog** — closest philosophical match to broker + receipts |
| **Agent RAI** (Nexastack) | Sovereign private-cloud agent orchestration | **Analog** — deployment model only |
| **RAIS (SourceA docs)** | External competitor / controlled-automation player to **study** | **NOT** internal stack name |

Research Acquisitor job: extract **how they function**, not adopt their branding.

---

## Part II — How they actually work (functional anatomy)

### Comparison matrix — real mechanics, not marketing

| System | Control plane | Execution surface | Human gate | Proof / audit | Primary buyer |
|--------|---------------|-------------------|------------|---------------|---------------|
| **Raia Command** | Web dashboard — agent lifecycle, knowledge pipeline, channel governance | Multi-model (OpenAI, Claude, Google) + Raia CX | Raia Copilot HITL | Platform logs + training feedback | Mid-market ops ($1K–6K/mo) |
| **RAISE framework** | Eight pillars + lifecycle gates (tool-agnostic) | Any agent stack | Gate owners + evidence before go-live | Operational controls + incident checklist | CISO / GRC teams |
| **Keon** | MCP Gateway — **no side doors** | Model-agnostic; effects cross boundary once | Policy before effect; fail-closed | **Receipt minted per action** | Regulated enterprise AI |
| **Devin Enterprise** | Cognition cloud — Brain + isolated Devbox | Cloud VM per session; GitHub/Slack | **Git PR + branch protection** (not per-tool on std plan) | Enterprise audit logs API (SOC2) | Eng teams shipping code |
| **MCP Gateway** (Tyk/Kong/TrueFoundry) | Central intercept — all tool calls | MCP servers behind gateway | RBAC/ABAC + optional HITL for writes | Immutable log per invocation | Platform teams at scale |
| **REAP+ / RiteSys** | Workflow builder + domain agents | Connectors to CRM, legal, finance | Approval stages built into flows | Versioned run histories | Marketing/legal ops |
| **Elementum** (2026 orchestration guide) | Enterprise workflow orchestration | Multi-system deterministic workflows | Configurable HITL | Auditability + data sovereignty | Fortune 500 ops |
| **SourceA (disk)** | **Hub** + Brain + broker | Cursor skills + CLI/API agents + INBOX | ASF Hub tap + CHECK/ACT/VERIFY roles + kill flags | **receipts + events jsonl + WORKER_ROUND_REPORT** | ASF + controlled REGISTRY drain |

---

### Deep dive — five models worth stealing functionally

#### 1. Raia Command — “control plane for AI workforce”

**How it really works:**
- **Command** = build, manage, monitor agents + knowledge docs
- **Copilot** = human-in-the-loop testing and feedback loop
- **Chat** = multi-channel deployment (SMS, email, voice)
- **Control** = outbound campaign orchestration
- Integrates Salesforce, HubSpot, Slack, **n8n**

**Management pattern:** Single dashboard owns lifecycle — design → train → deploy → monitor → retire.

**SourceA equivalent (already present):**

| Raia module | SourceA |
|-------------|---------|
| Command | Hub Agent hub + skills grid + goal1 loop status |
| Copilot HITL | Brain `@sina-sourcea-brain` judge + ASF Hub override |
| Knowledge pipeline | RESEARCH mirror + `research-intake` skill + Brain filtered digest |
| Control / campaigns | `autorun_dispatcher` + launchd + n8n (P2) |
| Tool governance | `prompt_feasibility_gate`, `one_sa_per_turn_gate`, hub edit lock |

**Gap:** Raia is no-code for business users; SourceA still requires Worker execution literacy (skills fix this).

**Steal:** Name and UX clarity — “Control plane for your AI workforce” maps to **Agent Hub → skills → AUTO-RUN**.

---

#### 2. RAISE framework — “govern agents like production systems”

**How it really works:**
- Eight pillars (inventory, monitoring, guardrails, recovery, etc.)
- **Lifecycle gates** — owners, evidence, go/no-go before production
- Replaces paper GRC with **runtime enforcement**

**SourceA equivalent:**

| RAISE pillar | SourceA implementation |
|--------------|------------------------|
| Agent inventory | `agent-skills/REGISTRY_LOCKED_v1.json` + 12 skills + worker registry |
| Monitoring | `~/.sina/events/*.jsonl` + batch log + Hub `/api/goal1-loop-status` |
| Runtime guardrails | `STOP_INJECT`, kill flags, `closeout_gate_v1.py`, validators |
| Recovery | `repair-broker-gaps`, quarantine scripts, `stop_goal1_loop_v1.py` |
| Lifecycle gates | CHECK → ACT → VERIFY per sa; Brain ACCEPT/REJECT |

**Steal:** Brain adds **RAISE-style gate table** to Master Operating Tracker §6 — no new code.

---

#### 3. Keon — “thoughts free; effects controlled”

**How it really works:**
- Cognition (planning) separated from **effect boundary**
- MCP traffic routes through gateway — authorization **before** action
- **Receipt** binds decision + policy + authority + outcome

**SourceA equivalent (strongest philosophical match):**

```text
Thought free:  Brain chat, Research Acquisitor, external critics
Effect boundary: broker worker-submit + closeout_sa_task + validators
Receipt:       receipts/sa-XXXX-receipt.json + TASK_CLOSED event
No side door:  hub edit lock, one-sa gate, feasibility STOP_INJECT
```

**Your advantage over Keon today:** File-based SSOT on founder machine — full inspectability without vendor SaaS. **Gap:** Keon enforces at MCP wire level; SourceA enforces at script + broker level (good enough at semi-auto L1).

---

#### 4. Devin Enterprise — cloud agent developer

**How it really works:**
- **Brain** (Cognition cloud) + **Devbox** (isolated VM per session)
- Human gate = **git workflow** (PR review, branch protection) — not per-action approval on standard plans
- Enterprise **audit logs API** for compliance teams
- Lifecycle hooks on Devin CLI: `PreToolUse`, `PostToolUse`, `PermissionRequest`

**SourceA comparison:**

| Dimension | Devin | SourceA |
|-----------|-------|---------|
| Where code runs | Cognition cloud | Local Mac + Cursor/agent CLI |
| Approval model | PR review | CHECK/ACT/VERIFY + broker + ASF Hub |
| Playbooks | AGENTS.md in repo | **Cursor SKILL.md** (just shipped) |
| Audit | Enterprise API | `events jsonl` + receipts (founder-readable) |
| Cost | Subscription + cloud | ~$9/681 tasks routing (locked strategy) |

**When Devin wins:** Large eng org, cloud-only policy, PR-centric workflow.  
**When SourceA wins:** Founder-controlled disk SSOT, compliance **evidence** as product (TrustField/Noetfield), honest semi-auto gates.

**Steal:** Devin lifecycle hooks concept → already mirrored in `WORKER_STARTED` / `WORKER_SUBMIT` events + skill session load chain.

---

#### 5. MCP Gateway (2026 enterprise consensus)

**How it really works:**
- Hub-and-spoke: every agent tool call passes through gateway
- Enforces identity, RBAC, rate limits, schema validation
- **Immutable audit trail** per invocation — compliance requirement at scale

**SourceA today:**
- Tools = Python scripts + Cursor tools — **no unified MCP gateway**
- Policy enforced by: broker, validators, feasibility gate, maintainer edit lock

**Smart path (P1, not P0):**
- High-risk tools only (`closeout`, registry write, hub deploy) through explicit gate scripts
- Full MCP gateway **after** Kill #6 sustained — not before factory proof
- Noetfield commercial angle: sell “governance boundary” story Keon uses — you **live it** logged

---

## Part III — Maintainer skills ship — what just became real

Maintainer 2 shipped **agent skills live logged** — this is SourceA’s functional answer to enterprise **playbook standardization**.

### What was built

| Skill | Cursor name | Function |
|-------|-------------|----------|
| SourceA Worker | `@sina-sourcea-worker` | INBOX drain, CHECK/ACT/VERIFY, broker, receipts |
| SourceA Brain | `@sina-sourcea-brain` | Judge, hygiene, ASF routing, acceptance |
| Registry drain | `@sina-registry-drain` | Honest closeout — receipts only |
| Research intake | `@sina-research-intake` | Pipeline before build |
| + 8 portfolio/maintainer skills | `sina-trustfield`, etc. | Parallel brand lanes |

**Registry:** `agent-skills/REGISTRY_LOCKED_v1.json` — 12 skills  
**Validator:** `validate-agent-skills-v1.sh` — PASS  
**Hub:** Agent hub tab + **◎ Sync skills to Cursor**  
**INBOX:** Every Worker turn auto-includes skill references  

### Why this matters vs Raia/Devin

| Enterprise pattern | Vendor approach | SourceA (now) |
|--------------------|-----------------|---------------|
| Agent playbooks | Raia training packages | `SKILL.md` per role, law-linked |
| Session bootstrap | Platform onboarding wizard | Skill “Load every session” → LOCKED md files |
| Honest completion | Vendor dashboard metrics | `@sina-registry-drain` — receipt or FAIL |
| Research before build | Internal review committees | `@sina-research-intake` → Hub pipeline |
| Sync to IDE | N/A (locked platform) | `founder-sync-agent-skills` one tap |

**Functional win:** Skills attack **Problem B from GPT 3.1** — fragmented mental models. Worker, Brain, and drain each load **one canonical contract** at session start.

---

## Part IV — SourceA advantage stack (how to turn research into power)

### The six-layer model (your system, fully functional)

```text
L0  HUB (ASF)           One tap · no Terminal · kill switches
L1  BRAIN + SKILLS      @sina-sourcea-brain · pick · judge · route
L2  BROKER + VALIDATORS broker=yes · one-sa · EVENT_CONTRACT
L3  SKILLS + INBOX      @sina-sourcea-worker · @sina-registry-drain
L4  EXECUTION ENGINES   API (verify) · CLI (act) · Cursor (IDE)
L5  PROOF               receipts · events jsonl · REGISTRY honest
L6  RESEARCH PIPELINE   intake → evaluate → promote (no critic reorder)
```

**This is smarter than buying Raia because:**
1. **Receipt-bound** — Keon-class proof without Keon invoice  
2. **Multi-engine routing** — Raia multi-model, you already route Haiku/Sonnet/Cursor  
3. **Portfolio parallel** — TF/NF skills while spine drains  
4. **Research firewall** — external paste (GPT, Claude, Gemini) cannot reorder roadmap  
5. **Local sovereignty** — Elementum’s “data sovereignty” criterion met by default  

**This is weaker than Devin/Raia until you fix:**
1. **Sustained AUTO-RUN** — Kill #6 (skills reduce drift; they don’t replace autorun)  
2. **First invoice** — architecture doesn’t pay bills (GPT premortem)  
3. **MCP wire-level gate** — optional P1; script gates sufficient at L1  

---

## Part V — Golden suggestion — five moves (fully actionable)

### Move 1 — Skills become session law (immediate)

**Worker manual sessions:**
```
@sina-sourcea-worker @sina-registry-drain — run INBOX
```

**Brain sessions:**
```
@sina-sourcea-brain — hygiene check before ACCEPT
```

**Research → build boundary:**
```
@sina-research-intake — submit this report before law change
```

INBOX auto-injects Worker skills on drain turns — **manual sessions must still invoke at start**.

---

### Move 2 — Map RAISE gates to disk (Brain, no code)

Add tracker §6 table:

| Gate | Event / script | Owner |
|------|----------------|-------|
| Pick authorized | DECISION_RECONCILED | Brain |
| Inject allowed | INBOX_DELIVERED + feasibility PASS | orchestrator |
| Execute started | WORKER_STARTED | start_goal1_worker_turn / CLI |
| Worker finished | WORKER_SUBMIT | broker |
| Validated | VALIDATOR_PASS | closeout_gate |
| Closed | TASK_CLOSED | closeout_sa_task |

This is what GPT 3.1 asked for — **already exists**, skills + tracker make it **believable**.

---

### Move 3 — Sustain factory (Claude Kill #6)

Skills reduce the interpretation errors that caused **WORKER_STARTED = 0** era.  
They do **not** replace Hub **▶ AUTO-RUN**.  

**Success:** 30-task pack advances with kill flag off · WORKER_STARTED scales with SUBMIT · receipts match events.

---

### Move 4 — Commercial parallel (GPT Layer 9)

Use portfolio skills:
- `@sina-trustfield` — TF-P1 demo funnel (GOLDEN-010 fear-first hero)  
- `@sina-noetfield-cloud` — Copilot governance pack pages  

**Sell what you live:**
- TrustField = Vanta-class **evidence** for RPAA (buyer fear)  
- Noetfield = Credo/RAISE-class **governance** for Copilot (Measurable Trust)  
- SourceA spine = **Keon-class receipt boundary** (internal proof for investors)

---

### Move 5 — Defer expensive vendor patterns

| Defer | Until |
|-------|-------|
| Raia / Devin subscription | After first TF/NF invoice |
| Full MCP gateway | After Kill #6 PASS |
| Supabase/pgvector at scale | After Voyage key + AUTH-LIVE habit |
| n8n production orchestration | After one clean Rail A chain |

---

## Part VI — World model cheat sheet (June 2026)

| If buyer asks… | Point to… | Proof logged |
|----------------|-----------|---------------|
| “Do you have a control plane?” | Hub Agent hub + skills + broker | 12 skills PASS |
| “How do you govern agents?” | RAISE-style gates + EVENT_CONTRACT | events jsonl |
| “Receipt before action?” | Keon analog — broker + closeout | receipts/ |
| “Human in the loop?” | ASF Hub + Brain judge + CHECK role | founder law |
| “Audit trail?” | Vanta/Drata class evidence packs | TF/NF deliverables |
| “Developer trust?” | Resend/Stripe — `/developers` + sandbox | trustfield.ca `/trade` |

---

## Part VII — What NOT to do

1. **Rename internal layers “RAIS”** — locked forbidden  
2. **Buy Raia/Devin to fix drain** — activation gap, not missing vendor  
3. **Skills without receipts** — registry-drain skill forbids  
4. **MCP gateway before broker sustains** — over-engineering trap (GPT premortem Mode #2)  
5. **Implement competitor UI before 3 TF demos** — SOT engineering freeze  
6. **Let research skip intake** — this report should flow through `@sina-research-intake` if structural  

---

## Final golden paragraph

The world’s best 2026 agent companies converged on one functional truth: **a control plane, standardized playbooks, an effect boundary, human gates where it matters, and receipts that survive the audit.** Raia sells the dashboard. Keon sells the boundary. Devin sells the cloud devbox. RAISE sells the gate vocabulary. MCP vendors sell the wire. **SourceA already has all five logged** — Hub, skills (shipped today), broker, ASF tap, receipts — plus something none of them productize for a solo founder: **honest semi-auto Level 1 on your machine with a RESEARCH firewall against AI opinion loops.** The smart move is not to become Raia. It is to **run the stack you built**: sync skills, sustain AUTO-RUN until the pack drains, sell TrustField evidence and Noetfield governance in parallel, and cite your own event chain as the demo when a CISO asks “show me controlled agents.” That is the fully functional, smart advantage — **receipt-bound civilization on a Mac**, not another subscription.

---

## Vault paths

| Artifact | Path |
|----------|------|
| YAML SSOT | `~/.sina/agent-workspaces/research-acquisitor/briefs/2026-06-09_RAIS_SUCCESS_MODELS_FUNCTIONAL_REPORT.yaml` |
| This report | `~/.sina/agent-workspaces/research-acquisitor/briefs/2026-06-09_RAIS_SUCCESS_MODELS_FUNCTIONAL_REPORT.md` |
| Skills registry | `~/Desktop/SourceA/agent-skills/REGISTRY_LOCKED_v1.json` |
| Worker skill | `~/Desktop/SourceA/agent-skills/sourcea_worker/SKILL.md` |

**execution_authority:** false
