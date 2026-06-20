# Agent ecosystem sprint — consolidation & preservation (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-05-AGENT-CONSOLIDATION  
**Purpose:** Preserve **all good conclusions, suggestions, and ways** from the rapid agent-hub sprint so nothing is lost on the path to the **final locked ecosystem v2**.  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` · router `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`  
**Hub:** `http://127.0.0.1:13020/?tab=council-room`  
**Maintainer:** ASF / `sinaai_maintainer`

---

## 0. Law (one sentence)

**This doc is the preservation manifest — canonical conclusions stay in topic LOCKED docs; open decisions and reserved builds live here until ASF closes them into final law or ships them in the hub.**

---
**Canonical WTM map:** `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`


## 1. Permanent conclusions (the ways — do not lose)

### 1.0 ASF terminology (LOCKED — do not invert)

| Term | Meaning |
|------|---------|
| **Exclusive** | **Particular · individual · monopolized** — one agent’s lane, one private scope, one moment’s particular laws |
| **Inclusive** | **Overall · all-in · covering all** — every agent, every rule in app, whole-system view |

*Example:* Blueprint is **inclusive** (overall app + all agents) and **exclusive** (§4 particular per-agent definitions). Rules in charge: **inclusive** full index + **exclusive** particular “in charge NOW” highlights.

### 1.0a Founder First Assistant (primary Mac job)

| Conclusion | Way |
|------------|-----|
| **Never forget** | Every founder idea/request/order → `~/.sina/founder-requests/requests.jsonl` |
| **Law** | `FOUNDER_FIRST_ASSISTANT_TRACKING_LAW_LOCKED_v1.md` |
| **Surface** | Hub **Today** + **Track** · `/api/founder-requests` |
| **Orders ≠ suggestions** | Deliver in app unless explicitly research-only |

### 1.1 Sina Command is the pre-unifying hub

| Conclusion | Way |
|------------|-----|
| App before repo | Every agent session **starts in Council Room** — read whole-system brief, rules in charge, mind share, paradoxes |
| No per-chat paste | ASF does **not** re-convince each agent in separate Cursor chats — **Copy brief** once per session |
| Middle layer | App is **mandatory middle layer** — vault deposit + activity log for all significant work |
| Report channels | Hub bugs → Backlog · law forks → Conflict · safety → Incident · learning → Mind Share · session proof → Scoreboard |

### 1.2 Authority & judgment (how to decide)

| Rank | Class | Role |
|------|-------|------|
| 0 | `ASF_ORDER` | Direct imperative |
| 1 | LOCKED SOURCE | `*_LOCKED_vN.md` at SourceA root |
| 2 | MACHINE SSOT | `system_roadmap.py`, `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`, validators, audits, `~/.sina` artifacts |
| 3 | SMART JUDGMENT | Contract harden, quality, incident prevention — **same step ID only** |
| 4 | Blueprints | Inform structure — never override SOURCE |
| 5 | Attachments | `archive/attachments/` until convince gate |
| 6 | `EXTERNAL_CRITIC` | GPT paste — **compare only** — never steer build order |

**Beneficial line test:** *Would I make this change given the SSOT gap alone, with build order unchanged?*

**Self-healing loop:** `detect → classify → remediate → harden → verify → record` (near-misses get hardened).

**GPT acceptance rule (D1 lesson):** Accept critic words only where they **match SSOT scope** and fix **real contract drift** — not because GPT said so.

### 1.3 Eight registered agents (not nine)

| Fact | Way |
|------|-----|
| **8 private agents** | trustfield · virlux · ai_dev_bridge_os · noetfield_local · noetfield_cloud · seven77 · semej · sinaai_maintainer |
| **MergePack** | Semi-separate product lane (`THREAD-MERGEPACK`) — **not** on private-agent registry or scoreboard |
| **SourceA edits** | Only `sinaai_maintainer` (ASF-approved) |
| **Portfolio** | Own `repo_root` only — never SourceA / hub code |

### 1.4 Traceability (anti-mixup)

| Agent | Tag pattern | Storage |
|-------|-------------|---------|
| Maintainer | `[MAINTAINER_AGENT_REF · sinaai_maintainer · MAINT-REF-{TOPIC}-{NNN}]` | `~/.sina/agent-workspaces/sinaai_maintainer/private-reference/` |
| Other agents | **Reserved** — `{AGENT}_AGENT_REF` per lane (not rolled out yet) | Private workspace only — **never** root LOCKED without unification |

**Rule:** Agent-private insight ≠ SSOT. Adoption only via **Governance Unification Engine** + ASF convince gate.

### 1.5 Governance drift (industry + Sina reality)

**Industry (2026):** Governance drift = silent divergence from policies, metadata, controls, model behavior — continuous monitoring, not quarterly review.

**Sina already has documentary drift sensors:**

| Sensor | Catches |
|--------|---------|
| `audit_hub_source_alignment.py` | MAP ↔ payload ↔ UI ↔ `do_now` |
| `audit_agent_governance_e2e.py` | Fleet / registry / private pages |
| `DRIFT.json` + Today | Founder-visible SSOT gaps |
| ACE v3 | DESIGN / EXECUTION / DELIVERY conflict |
| Incidents + critic law | UI deletion, step rename, auto-paste steer |
| `agent-governance-events.jsonl` | Proto trust ledger |

**Gap (reserved build):** Unified drift **score**, trust ledger **schema**, ML statistical sensors (correctly **D5+**, not now).

**Do not:** Buy Galileo-class MLOps before D5 · treat vendor stats as SSOT · default auto-retrain (conflicts founder-confirm law).

### 1.6 Unification engine (batch way)

When ASF sends rules, essays, governance, or doc batches:

```
INTAKE → INVENTORY → SCORE → MAP → MERGE → ARCHIVE → SYNC → VERIFY
```

Verdicts: **ADOPT · MERGE · ATTACH · REJECT · DEFER**  
One topic → one canonical LOCKED doc. Deliver **unification report** table to ASF.

**Today:** Procedure LOCKED in `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md` — **manual agent run**; hub automation reserved (see §4).

### 1.7 Council Room phases

| Phase | What | Status |
|-------|------|--------|
| **0** | Readiness, mind share, paradox board, rules digest, essay discourse | **Live** |
| **1** | Topics, advisory votes, `topics.jsonl` / `votes.jsonl` | **Designed** — ASF “go” required |
| **2** | Formal ballots on frozen options | **Reserved** |

### 1.8 Standard agent session (locked flow)

```
1. Council Room     → read brief + rules in charge + copy brief
2. Agent hub        → pick private page
3. Private page     → log activity · vault deposit
4. Own repo         → work (allowed repo_root only)
5. Vault + report   → deposit deliverables · scoreboard session report
6. Mind share       → post insight / paradox if cross-lane learning
7. Essay discourse  → when subject assigned — post tagged essay
8. ASF verify       → scoreboard column ✓ when auto-checks green
```

---

## 2. What shipped (canonical — sprint deliverables)

| Layer | Artifact / surface |
|-------|-------------------|
| **Law** | Unification policy · Council Room · Mind Share · App-as-hub · Application blueprint · Vault middle layer · MergePack-not-agent · Scoreboard · Essay discourse · Rules in charge · Decision stack · Governance unification procedure · MergePack notice |
| **Hub tabs** | `council-room` · `agent-scoreboard` · private agents ×8 · vault UI per page |
| **APIs** | `/api/council-room` · `/api/workspace-vault` · `/api/agent-scoreboard` · `/api/essay-discourse` · `system_unified` in council payload |
| **Machine** | Registry v6 (8 agents) · governance E2E v6 · D1 code intelligence PASS · tab URL aliases |
| **Fixes** | BrokenPipe handled · Personal DB frontmatter · debug session (instrumentation removal reserved) |
| **Private** | Maintainer drift essay `MAINT-REF-GOV-DRIFT-001` · tag standard |

**Deep reference:** `AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md`

---

## 3. ASF decisions — build orders (delivery status)

| ID | Order | Status |
|----|-------|--------|
| **D-DEBUG-01** | Remove debug instrumentation from server | **SHIPPED** |
| **D-VOTE-01** | Council advisory voting (topics + vote API + UI) | **SHIPPED** |
| **D-UNIFY-01** | Governance unification batch in hub | **SHIPPED** — Council Room form + `/api/governance-unify` |
| **D-DRIFT-01** | Governance drift engine Phase 1 | **SHIPPED** — engine + validator + Today + API |
| **D-UI-01** | Blueprint navigator in Council Room | **SHIPPED** — inclusive + exclusive § buttons |
| **D-TAG-01** | Per-agent doc tag standards (8 agents) | **SHIPPED** — `DOC_TAG_STANDARD.md` per workspace |
| **D-GPT-01** | GPT paste default mode lock | **OPEN** — report-only vs apply-spec |
| **D-D2-01** | D2 Graph Fusion | **OPEN** — WTM next strategic step |

---

## 4. Reserved build queue (prioritized — feed final locked v2)

### P0 — truth & hygiene (no new features)

| ID | Build | Why |
|----|-------|-----|
| **R-P0-01** | Fix doc drift **9→8** (blueprint, authority index FLEET row, ecosystem policy mergepack row) | Machine truth is 8 agents |
| **R-P0-02** | Archive orphan `~/.sina/agent-workspaces/mergepack/` or document semi-separate-only | Registry v6 mismatch on disk |
| **R-P0-03** | Strip debug instrumentation (after D-DEBUG-01) | Production server cleanliness |

### P1 — hub features (sprint suggestions not yet in app)

| ID | Build | Source suggestion |
|----|-------|-------------------|
| **R-P1-01** | Council **blueprint navigator** panel | Blueprint delivery “If you want next” |
| **R-P1-02** | Governance **batch intake UI** + unification report surface | Unification engine prompt 5362 |
| **R-P1-03** | `governance_drift_engine.py` + `validate-governance-drift-v1.sh` + Today aggregate score | Drift essay Phase 1 |
| **R-P1-04** | Trust ledger schema v1 for `agent-governance-events.jsonl` | Drift essay |
| **R-P1-05** | Essay assignment **nudges** — 6/8 agents still owe `governance-drift-detection` | Essay discourse law |
| **R-P1-06** | Propagate **decision-stack cursor rule** to all 8 agent workspaces | Decision stack session |
| **R-P1-07** | Per-agent **doc tag standards** (7 remaining agents) | Prompt 5373 expansion |
| **R-P1-08** | **D2 Graph Fusion** | WTM SSOT next step |

### P2 — Council & scale

| ID | Build | Gate |
|----|-------|------|
| **R-P2-01** | Council Phase 1 voting (topics, votes, UI) | D-VOTE-01 = go |
| **R-P2-02** | Council Phase 2 formal ballots | After Phase 1 + discourse |
| **R-P2-03** | Lazy-load / split **COMMAND_DATA** (~2MB index) | E2E known non-blocker |
| **R-P2-04** | Import historical ASF chat rules → `founder-directives.jsonl` | Optional backlog |
| **R-P2-05** | **Supervisor dashboard** tab (traffic lights · weekly digest · links scoreboard/vault/essay) | Brainstorm — not in sprint law yet |
| **R-P2-06** | Authority index **hub visibility tile** | Earlier optional visibility ask |

### P3 — product / ML (do not invert roadmap)

| ID | Build | When |
|----|-------|------|
| **R-P3-01** | ML drift sensors (PSI/KL/embedding) | D5+ |
| **R-P3-02** | TrustField Governance Drift SKU | Phase 3 product export |

---

## 5. Anti-patterns & incidents (learned — keep)

| Do not | Why |
|--------|-----|
| Treat GPT paste as build order | `EXTERNAL_CRITIC` — compare only |
| Re-enable Cursor auto-paste inject | Incident law |
| Let portfolio agents edit SourceA | Edit lock + ecosystem policy |
| Register MergePack as private agent | Semi-separate lane only |
| Store significant work only in chat | Vault middle layer law |
| Cite `archive/superseded/` as active law | Authority index wins |
| Skip rebuild after founder directive | Council Room form → `build-sina-command-panel.py` |
| Greenfield MLOps for doc drift | Extend existing audits + ledger |

---

## 6. Essay & discourse conclusions (governance drift subject)

**Default assignment:** `governance-drift-detection`  
**Workflow:** Each of 8 agents writes in Cursor → posts via hub → read others → ASF marks best  
**Maintainer insight (private):** `MAINT-REF-GOV-DRIFT-001` — extend audits, don’t replace ASF/SSOT  
**Fleet status at consolidation:** 2/8 essays posted — **operational gap**, not missing law

---

## 7. Scoreboard conclusions

| Column | Meaning |
|--------|---------|
| 1 | Agent · chat pointer · session report · auto-check pills |
| 2 | ASF **verify ✓** when agent did it right |

**Auto-checks:** report ≥40 chars · council attested · vault deposit · activity · workspace ready  
**Chat pointer limit:** Hub private page + `cursor_workspace` hint — no Cursor deep-link API exists

---

## 8. Path to final locked ecosystem v2

```text
THIS DOC (preservation manifest)
    ↓
Close §3 decisions (ASF answers D-*)
    ↓
Ship §4 queue by priority (R-P0 → R-P1 → …)
    ↓
Run unification engine on any doc drift from sprint
    ↓
Bump topic LOCKED docs to v2 where scope changed
    ↓
AGENT_ECOSYSTEM_FINAL_LOCKED_v2.md (future — single apex handoff when queue empty)
```

**Rule:** Do not create `FINAL_LOCKED_v2` until §3 decisions closed and §4 P0+P1 complete or explicitly deferred with ASF note in this manifest addendum.

---

## 9. Quick reference — one paste for agents

```
PRESERVATION MANIFEST: AGENT_ECOSYSTEM_SPRINT_CONSOLIDATION_LOCKED_v1.md
START: Council Room → copy brief → vault → repo → report → mind share
AUTHORITY: ASF_ORDER > LOCKED SOURCE > MACHINE SSOT > smart judgment > critic
AGENTS: 8 registered · MergePack NOT an agent
OPEN: see §3 D-* IDs · BUILD: see §4 R-* IDs
```

---

**END · LOCKED · Preservation manifest — sprint conclusions & reserved builds**
