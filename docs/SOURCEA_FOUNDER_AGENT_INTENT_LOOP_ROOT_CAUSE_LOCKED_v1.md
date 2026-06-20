# SourceA Founder–Agent Intent Loop — Root Cause & Fixes — LOCKED v1

**Version:** 1.1.1 · **Saved:** 2026-06-20T17:45:00Z · **Authority:** ASF save order (intent-loop investigation + NUW + priority router + Mac Law correction)
**Path:** `~/Desktop/SourceA/docs/SOURCEA_FOUNDER_AGENT_INTENT_LOOP_ROOT_CAUSE_LOCKED_v1.md`
**Related:** `.cursor/rules/agent-founder-intent-first.mdc` · `.cursor/rules/033-market-analog-before-abstraction.mdc` · `data/agent-behavior-settings-v1.json` · `docs/_ANALYSIS_FORMAT_MARKET_REALITY_v1.md` · `docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md`
**Incident thread:** Forge MVP + -1000 + Terminal/404 (`POST http://…` → `zsh: command not found` → Hub `not found`)

---

## 0. One sentence

> **Founder repeats intent 10–20 times because agents ship disk-native WORK (code, validators, routes) in the wrong lane, document developer APIs as founder steps, and declare PASS while the live founder path is broken.**

---

## 1. What ASF reported

ASF asked: why does the same problem repeat — many prompts until the agent understands the right answer?

Observed in one session (2026-06-20):

| ASF intent | First agent response | Prompts lost |
|------------|----------------------|--------------|
| Real **market scenarios** (not code) | Schemas, JSON, implementation | “no code stupid” |
| **Comparable ** (touchable startups) | ICP theory, GitHub/Stripe, abstract SourceA names | Several corrections |
| **Inject rules** so we stop fighting | Rule 033 (good) → then **5000 plans + Forge MVP build** without confirming lane | Build theater |
| **Run Forge dry-run** | Docs showed bare `POST http://…` | Pasted into Terminal → `zsh: command not found` |
| **Retry via curl** | Hub `{"error":"not found"}` | Stale Hub process; restart + more Terminal |

ASF already stated the law once in-thread: *“it shouldn’t take 20 prompts until I get my answer.”*

---

## 2. Five root causes (system + style)

### 2.1 Intent substitution

Agents default to **WORK on disk** instead of **answering in the requested lane**.

| Request type | Wrong substitution |
|--------------|-------------------|
|  / market | ICP, architecture, SourceA theory, big incumbents |
| Real-world scenario | Code, schema, receipt JSON |
| Policy / rules injection | Immediate mega-build (plans, Forge steps) |
| “Explain” | Validator PASS lists, internal jargon |

**Machine gap:** Rule 033 classifies  / ICP / implementation / company mapping — but nothing blocks an agent from starting WORK after a policy save.

**Related law:** `.cursor/rules/033-market-analog-before-abstraction.mdc` · `.cursor/rules/agent-founder-intent-first.mdc`

---

### 2.2 Developer copy + wrong execution plane (not Mac Law — separate UX issue)

**Mac Law (for agents):** do **not** run factory build, motors, render, or factory validators on the Mac body — cloud/API executes (`MAC_CONTROL_PLANE_LOCKED.md`).

**Separate rule (founder UX):** daily-duty / Mac control plane also says founder should not be sent to Terminal for routine ops — that is **not** the definition of Mac Law.

What agents still ship (violates Mac Law when they **run** these on Mac):

- Blueprint tables: `POST http://127.0.0.1:13020/api/fbe/run-forge/v1`
- Step 9 “DONE”: `POST /api/fbe/forge--run/v1` without Hub button
- Completion messages with **curl** as primary path

**Result:** ASF pasted `POST http://…` into zsh — predictable, not user error. Docs looked like shell commands.

**Evidence:** `docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md` (Hub POST rows) · completion reply in Forge MVP thread

---

### 2.3 Green theater — disk PASS ≠ founder PASS

`scripts/validate-forge-mvp-hub-action-v1.sh` checks:

- Route string exists in `sina-command-server.py` (grep)
- `forge__run_v1.py --dry-run` (local Python)

It does **not** check:

- HTTP POST to **running** Hub on `:13020`
- Hub Action in `agent-control-panel/command-data.json` (no `forge-` entry at save time)

Agent can report **all PASS** while ASF gets `404 not found`.

---

### 2.4 Stale Hub process (structural)

`scripts/serve-sina-command.sh`:

- If `/health` OK → exit unless `SINA_FORCE_RESTART=1`
- `/health` returns `{ok, service, port}` only — **no build id, no route manifest**

**Pattern:** Agent adds route on disk → docs say use Hub → running Python is old → generic 404 → debugging thread.

---

### 2.5 Rule stack paradox

30+ alwaysApply rules compete. Under time pressure agents satisfy:

- Session gate, validators, WORK scope, disk receipts

…before plain **“You asked for X; this turn delivers X only.”**

Comprehension loop (`030-cloud-comprehension-pipeline-loop-v1.mdc`) exists but replies still lead with mechanics, PASS lines, and internal names (FORGE, FBE, dry-run).

---

## 3. The repeat loop (diagram)

```text
ASF asks X
  → Agent hears build/report lane
  → Ships disk + validators PASS
  → Wrong format OR broken founder path
  → ASF corrects intent
  → (repeat)
```

---

## 4. Three fixes (priority order)

### Fix 1 — Founder Path Gate (machine)

**Law:** No feature is **DONE** for founder until:

1. **Hub Action** wired in `agent-control-panel/command-data.json`, **or**
2. **Agent executor** runs it (ASF never touches Terminal), **and**
3. **Live probe:** HTTP to `:13020` returns expected schema (not grep-on-source-only).

**Proposed validator:** `scripts/validate-founder-path-live-v1.sh`

- POST probe to running Hub for declared routes
- FAIL if route in source but not in live process
- FAIL if docs mark “Hub one-tap” but no command-data action id

---

### Fix 2 — Reply contract (agent conduct)

Before any substantive WORK, first block of reply:

1. **You asked for:** one plain sentence (restated intent)
2. **Lane:**  | ICP | implementation | company mapping | build | explain
3. **This turn delivers:** only that — no extra build unless ASF said build

If lane ≠ ASF words → **stop and ask one short question** — do not code.

**Wire into:** `data/agent-behavior-settings-v1.json` · `scripts/agent_report_language_gate_v1.py` · pre-ship scan

---

### Fix 3 — Hub version + stale guard

**`/health` must expose:**

- `server_build` or git short hash
- `routes_manifest` or hash of registered POST paths

**`serve-sina-command.sh` must:**

- Restart when on-disk server mtime / build id ≠ running process
- Or FAIL loudly: “Hub stale — new routes not loaded”

---

## 5. Doc / copy style rules (founder-facing)

When writing steps for ASF:

| Forbidden | Required instead |
|-----------|------------------|
| Bare `POST http://…` | “Worker Hub Action: …” or “Agent runs: …” |
| curl as first path | Executor script or Hub button |
| “Step N DONE” without live probe | “Disk wired; founder path: PENDING until live probe PASS” |
| API tables in blueprint “demo pipeline” | One founder sentence + where to click |

Align with: `docs/_ANALYSIS_FORMAT_MARKET_REALITY_v1.md` (market answers). Mac Law = **agents route factory work to cloud**, not “no HTTP copy.”

---

## 6. What agents should have done (this thread)

1. After “inject rules” → **one sample reply** in correct format; confirm lane — not 5000 plans.
2. Forge Step 9 → wire Hub Action + live probe **before** marking DONE.
3. On Terminal error → **agent runs dry-run**; do not send another curl block.

---

## 7. Acceptance test (loop is fixed when)

- [ ] ASF asks for  → first reply has comparable companies + links + pricing evidence (no code unless asked)
- [ ] ASF asks for scenario → plain buyer story (no schema)
- [ ] New Hub route → live POST PASS within same session without ASF restart/debug
- [ ] Agent never sends bare `POST http://…` as founder instruction
- [ ] Validator `validate-founder-path-live-v1.sh` FAILs on grep-only hub checks

---

## 8. Cross-reference index

| Topic | Path |
|-------|------|
| Market  format | `docs/_ANALYSIS_FORMAT_MARKET_REALITY_v1.md` |
| Market intent rule | `.cursor/rules/033-market-analog-before-abstraction.mdc` |
| Founder intent first | `.cursor/rules/agent-founder-intent-first.mdc` |
| Behavior SSOT | `data/agent-behavior-settings-v1.json` |
| Comprehension loop | `.cursor/rules/030-cloud-comprehension-pipeline-loop-v1.mdc` |
| Forge MVP (incident surface) | `docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md` |
| Hub action validator (disk-only today) | `scripts/validate-forge-mvp-hub-action-v1.sh` |
| Hub serve / stale | `scripts/serve-sina-command.sh` |
| Forge run script (works without Hub) | `scripts/forge__run_v1.py` |
| Rule collision (no intent router) | `brain-os/law/BRAIN_RULE_COLLISION_MATRIX_LOCKED_v1.md` |

---

## 9. NUW — No Unrequested Work (LOCKED)

**Convergence:** ASF thread · Gemini (“founder became integration tester”) · GPT (“wrong optimization target”) · this doc §2.

### 9.1 One law

> **Every output block must pass: “Did ASF request this?” If NO → suppress. Agents must never silently climb from answer to implementation.**

### 9.2 The wrong vs right hierarchy

**Wrong (today’s default):**

```text
ASF message → build mode → plans → validators → routes → PASS → maybe answer original question
```

**Right (mandatory):**

```text
ASF message → restate intent → classify lane → return requested artifact → STOP
                                                      ↓ (only if ASF asked build)
                                              implementation → validators → routes → docs
```

### 9.3 NUW suppress list

When ASF did **not** ask for implementation, the reply must **not** contain:

| Suppress | Example violation |
|----------|-------------------|
| Implementation plans | 5000-plan generator after “inject rules” |
| Code / schemas / JSON | Receipt schema when ASF asked market scenario |
| Validator scripts | New `validate-*` when ASF asked  |
| API routes / curl / bare POST | Forge Step 9 “DONE” with Terminal path |
| TODO storms | 10-step build todos when ASF asked policy |
| Architecture diagrams | SourceA theory when ASF asked who sells this |
| Disk PASS theater | “All green” without live founder path |

### 9.4 NUW unlock phrases (build allowed)

WORK (writes, scripts, routes, validators) is allowed only when ASF message contains an explicit build unlock, including:

- `implement` · `build` · `wire` · `ship` · `fix on disk` · `WORK:` · `EDIT ALLOWED:` + `ACTION:` · `RUN INBOX` (bounded inbox scope) · numbered plan execution with attached plan file

Policy save (`SAVE TO:`) → **write named path once → STOP** — not a build unlock for adjacent features.

### 9.5 Machine wiring (proposed)

| Component | Role |
|-----------|------|
| `scripts/founder_intent_nuw_gate_v1.py` | Scan draft + tool plan; FAIL if suppress list present without unlock |
| Pre-ship scan | Block reply containing curl/POST-as-command when lane ≠ build |
| `data/agent-behavior-settings-v1.json` | Add `nuw` block referencing this §9 |

---

## 10. Founder intent priority router (LOCKED)

**Convergence:** GPT priority stack · rule 033 lanes · comprehension C1 · `BRAIN_RULE_COLLISION_MATRIX` (“no intent router”).

### 10.1 Router job

> **Before any tool call or disk write: “What did ASF actually ask?” Route to exactly one primary lane. Never silently climb priority levels.**

### 10.2 Priority stack (100 → 30)

| Priority | Name | Agent must |
|----------|------|------------|
| **100** | Understand intent | Restate ASF ask in one plain sentence (visible in reply) |
| **90** | Determine lane | Pick one lane from §10.3; if unclear → one short question, then STOP |
| **80** | Produce requested output | Deliver only the artifact for that lane (NUW applies) |
| **70** | Confirm build | If lane needs implementation ASF did not request → STOP, do not build |
| **60** | Implementation | Code, routes, Hub wiring — only after 70 unlock |
| **50** | Validators | Only after 60 and only for changed surface |
| **40** | Docs | Only after 60 or explicit `SAVE TO:` |
| **30** | Expose APIs | Only after founder path gate (§4 Fix 1) |

**Hard rule:** An agent must **never silently climb** from 80 → 60 without an unlock phrase (§9.4).

### 10.3 Router lanes

| Lane id | When ASF asks | Deliver | Do not deliver |
|---------|---------------|---------|----------------|
| `explain` | How does X work? Why? | Plain English cause/effect | Validators, code |
| `market` | , pricing, who sells | Comparable vendors per `_ANALYSIS_FORMAT_MARKET_REALITY_v1.md` | ICP theory, SourceA rename |
| `strategy` | What should we do? | Options + tradeoffs in buyer language | Immediate mega-build |
| `research` | SAVE TO / report | One file at named path → STOP | Extra wiring |
| `build` | Implement, wire, ship | Bounded WORK on scope | Unrelated plans |
| `fix` | Broken path, error, 404 | Diagnose + agent executes fix | curl to founder |
| `execute` | Run it | Agent runs script/Hub; ASF observes | Terminal instructions |
| `validate` | Check / PASS | Live founder path + honest RED | Grep-only green theater |

Rule 033 sub-lanes (`` · `icp` · `implementation` · `company_mapping`) map under **`market`** and **`strategy`** — not under **`build`** unless unlocked.

### 10.4 Reply shape (mandatory first block)

Every substantive reply opens with:

```text
You asked for: <one plain sentence>
Lane: <lane id>
This turn: <exact deliverable only>
```

Then content. Then disk proof (if needed). No mechanics-first dumps.

### 10.5 Architecture diagram

```text
Founder
   ↓
Router (§10 — before tools)
   ├── explain
   ├── market      ← rule 033
   ├── strategy
   ├── research    ← SAVE TO → STOP
   ├── build       ← unlock required
   ├── fix
   ├── execute     ← agent runs; no Terminal
   └── validate    ← live probe, not grep
```

**Not:** Founder → Agent → Code (default today).

### 10.6 Existing disk vs gap

| Exists | Gap |
|--------|-----|
| C1 understand (comprehension loop) | No hard STOP before writes |
| Rule 033 market lanes | Not wired before WORK/todos |
| `agent-founder-intent-first.mdc` | Competes with 30+ alwaysApply rules |
| `prompt_router.py` | Prompt packs — not chat intent |
| This doc §4 fixes | Not yet machine-enforced |

**Proposed SSOT:** `data/founder-intent-router-priority-v1.json` (mirror of §9–§10 for scripts).

### 10.7 Executive copilot principle (locked)

> The gap between **what ASF meant** and **what the system returns** is not fixed by smarter models. It is fixed by **intent routing discipline** + **NUW** + **founder path live validation**. The machine integrates itself; ASF is not QA.

---

## 11. Acceptance test (v1.1 additions)

- [ ] NUW gate FAILs draft that includes code when lane = `market`
- [ ] Reply always opens with §10.4 three-line block
- [ ] Agent never climbs 80 → 60 without unlock phrase
- [ ] `validate-founder-path-live-v1.sh` exists and runs on Hub ship paths
- [ ] Gemini/GPT diagnosis items (integration tester, wrong optimizer) covered by §9–§10

---

**End — LOCKED v1.1**
