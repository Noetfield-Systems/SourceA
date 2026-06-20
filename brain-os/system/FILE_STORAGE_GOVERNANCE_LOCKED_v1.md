# FILE STORAGE GOVERNANCE LAW

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## LOCKED v1 — Canonical Storage Architecture for All SourceA Agents

**Document type:** Governance Law — Permanent  
**Owner:** ASF (structure) · Brain (enforcement)  
**Location:** `brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md`  
**Wired into:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b` (mandatory session start) · `SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md §8` · `EXECUTION_AUTHORITY_MAP_LOCKED_v1.md`  
**Validator:** `scripts/validate-file-storage-v1.sh`  
**Authored:** 2026-06-08 — ratified by ASF  
**Locked by:** Five-source convergence (Old Brain · Brain · Governance Specialist · GPT · Claude External Advisor)  

---

---

# SECTION 0 — GOVERNING LAW

## Golden Rule

> Every file, document, rule, spec, governance law, decision, receipt, or artifact created in SourceA must be saved to the correct tier immediately upon creation.  
> A file that exists only in chat history does not exist.  
> A file saved to the wrong tier is a governance violation.  
> **If it is not present locally in the correct location, it is not real.**

## Core Principle

SourceA uses a **three-tier storage model** derived from proven real-world agentic and infrastructure systems (GitOps, Temporal, Terraform, Stripe runbook model, Netflix Hollow).

| Tier | Name | What lives here | Who writes | Who reads |
|---|---|---|---|---|
| Tier 1 | SourceA repo (`~/Desktop/SourceA/`) | Governance · Strategy · Rules · Architecture · Decisions · Research | Brain · Workers · Specialists (with authority) | All agents — mandatory |
| Tier 2 | Runtime store (`~/.sina/`) | Operational state · Heartbeat · Live pointers · Event log · INBOX | Orchestrator · Brain (runtime) · Validators | Agents (machine-read only) |
| Tier 3 | External / cannot migrate | Secrets · Chat history · OS configs · External product repos | External systems | Reference only — never execute from |

**The 60% rule:** Approximately 60–65% of all SourceA information belongs in Tier 1. The remaining 35–40% is runtime state that is correct to keep in Tier 2. The goal is never 100% in one location — it is 100% of the right content in the right tier, with one index (the Master Tracker) that maps all of Tier 2 from Tier 1.

---

---

# SECTION 1 — TIER 1: SOURCEA REPO (GIT)

## What it is

The permanent, versioned, human-readable, agent-readable strategic SSOT for SourceA. Everything here is controlled, auditable, and searchable. Git history is the audit trail.

## Canonical directory structure

```
~/Desktop/SourceA/
│
├── brain-os/
│   ├── system/                   ← GOVERNANCE LAYER
│   │   ├── FILE_STORAGE_GOVERNANCE_LOCKED_v1.md   (this file)
│   │   ├── SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
│   │   ├── EXECUTION_AUTHORITY_MAP_LOCKED_v1.md
│   │   ├── authority.yaml
│   │   └── [all LOCKED system governance docs]
│   │
│   ├── laws/                     ← GOVERNANCE LAWS
│   │   └── [all LOCKED_v1.md law files]
│   │
│   ├── plan-registry/            ← EXECUTION REGISTRY
│   │   └── sourcea-1000/
│   │       ├── REGISTRY.json
│   │       └── SOURCEA-Priority.md
│   │
│   └── [other brain-os governance dirs]
│
├── scripts/                      ← VALIDATORS & AUTOMATION
│   ├── validate-authority-runtime-v1.sh
│   ├── validate-master-operating-tracker-v1.sh
│   ├── validate-file-storage-v1.sh
│   ├── goal-progress-v1.py
│   └── [all validator and automation scripts]
│
├── RESEARCH/                     ← EVIDENCE LAYER
│   ├── _GOVERNANCE/
│   │   └── WORKERS_REGISTRY.yaml   ← canonical worker registry
│   ├── by_date/
│   │   └── YYYY-MM-DD/
│   │       └── [agent]/[domain]/[trace_id]/
│   │           ├── [content files]
│   │           └── _META.yaml    (execution_authority: false — always)
│   └── vault/
│       └── [archived research by category]
│
├── receipts/                     ← PROOF LAYER
│   └── [sa-XXXX completion receipts]
│
├── agent-control-panel/          ← HUB CONFIG
│   └── command-data.json
│
└── [product repos — TrustField, Noetfield — separate, not SourceA spine]
```

## What MUST be saved to Tier 1

| Content type | Directory | Format | Who saves |
|---|---|---|---|
| Governance laws | `brain-os/system/` or `brain-os/laws/` | `*_LOCKED_v1.md` | Brain / ASF order |
| Architecture decisions | `brain-os/system/` | `*_LOCKED_v1.md` or `DECISION_REGISTRY` in tracker | Brain |
| Authority maps | `brain-os/system/` | `.yaml` + `.md` pointer | Brain |
| Task/goal registry | `brain-os/plan-registry/` | `REGISTRY.json` | Brain / orchestrator |
| Worker registry | `RESEARCH/_GOVERNANCE/` | `WORKERS_REGISTRY.yaml` | Brain |
| Validator scripts | `scripts/` | `.sh` or `.py` | Worker |
| Research saves | `RESEARCH/by_date/YYYY-MM-DD/[agent]/` | files + `_META.yaml` | Specialist / Research Acquisitor |
| Execution receipts | `receipts/` | per sa-XXXX | Worker |
| Master tracker | `brain-os/system/` | `SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md` | Brain |
| Roadmap specs | `brain-os/system/` | `.md` | Brain |
| Worker prompts / blueprints | `brain-os/` appropriate subdir | `.md` or `.yaml` | Brain |

## Rules for Tier 1

1. **All governance docs are LOCKED.** Structural changes require ASF explicit instruction + version bump (`_v2`).
2. **Content updates** (filling in goals, decisions, research) require no version bump — Brain updates in place.
3. **No secrets, credentials, or tokens** may ever be saved to Tier 1. Git history is permanent.
4. **Every research save must include `_META.yaml`** with `execution_authority: false`.
5. **No file may exist only in chat history.** If a decision was made in chat, it must be extracted and saved to the Decision Registry or appropriate LOCKED doc before the session closes.
6. **Brain verifies Tier 1 is current** before ending any session that changed system state.

---

---

# SECTION 2 — TIER 2: RUNTIME STORE (~/.sina/)

## What it is

The operational state layer. Machine-written, machine-read. Changes rapidly. Never edited by humans directly. Tier 1 (Master Tracker Section 8) holds pointers to all canonical Tier 2 files — it never duplicates their content.

## Canonical Tier 2 paths

```
~/.sina/
│
├── runtime/
│   ├── execution.json            ← current status · heartbeat · worker state
│   └── authority.yaml            ← (mirror reference — canonical is brain-os/system/)
│
├── next-execution-pointer-v1.json  ← next_sa · rail · source · updated_at
├── active-execution-rail-v1.json   ← Rail A/B · manual_fallback flag
│
├── brain/
│   └── reconciled_decision.yaml  ← Brain SYNC output · cites Tier 1 trace IDs
│
├── events/
│   └── YYYY-MM-DD.jsonl          ← append-only event log · never edited
│
├── worker-prompt-inbox-v1.json   ← live INBOX · transient · reset each turn
├── healthy-queue-30-active.json  ← runtime queue state
├── healthy-drain-orchestrator-v1.json  ← orchestrator state
├── research-root/                ← filtered research digest cache (machine registry)
└── agent-workspaces/             ← per-agent vault staging (SEMEJ / private lanes)
```

## Rules for Tier 2

1. **Only orchestrator, Brain (runtime mode), and validators may write to Tier 2.** Workers read from it; they do not write governance state to it.
2. **`next-execution-pointer-v1.json` is write-restricted** — only orchestrator / Brain pick may update it. No agent may overwrite it without a Brain handoff receipt.
3. **`active-execution-rail-v1.json` (`manual_fallback: true`)** may only be set by ASF order. Any agent that writes `manual_fallback: true` without an ASF trace is a governance violation.
4. **Event log (`events/YYYY-MM-DD.jsonl`) is append-only.** No agent may delete, edit, or truncate event entries.
5. **Tier 2 files are never committed to git.** They contain transient machine state, not strategic truth.
6. **Tier 1 Master Tracker Section 8 holds the canonical pointer list** to all Tier 2 files. If a new Tier 2 file is created, it must be registered in Section 8 before it can be used operationally.

---

---

# SECTION 3 — TIER 3: EXTERNAL / CANNOT MIGRATE

## What belongs here (and why)

| Content | Location | Rule |
|---|---|---|
| Secrets / credentials / API keys | OS keychain or env vars | Never in git · Never in Tier 1 |
| Chat history (raw) | Each AI tool's own storage | Extract decisions → Tier 1 Decision Registry. Raw history stays. |
| OS-level system configs | `~/.zshrc`, crontab, etc. | Document their existence in Tier 1 but do not move the files |
| Product repos (TrustField / Noetfield) | Separate git repos | Blueprint traces saved to Tier 1 RESEARCH/ · repos are not the SourceA spine |
| External platform data | GitHub, Vercel, etc. | Reference in Tier 1 docs · never duplicate API responses as governance |

## Rules for Tier 3

1. **Extract before closing any session.** Any decision, architectural choice, or governance rule discovered in chat or an external system must be extracted to Tier 1 before the session ends.
2. **Secrets are never Tier 1.** Even governance documents that reference credentials must use placeholder names, not actual values.
3. **Product repos reference SourceA governance; they do not replace it.** A TrustField or Noetfield build receipt must be saved to `RESEARCH/` in Tier 1.

---

---

# SECTION 4 — DECISION ROUTING RULES

When any agent creates a new artifact, it must determine the correct tier before saving:

```
Is this volatile machine state (heartbeat, pointer, queue, INBOX)?
  YES → Tier 2 (~/.sina/)
  NO  →
    Is this a secret or credential?
      YES → Tier 3 (env var / keychain) — NEVER Tier 1
      NO  →
        Is this governance, strategy, architecture, research, or receipt?
          YES → Tier 1 (SourceA repo, correct subdirectory)
          NO  → Ask Brain to classify before saving
```

**When in doubt: save to Tier 1 and register in the Master Tracker.**  
**When wrong tier is used: Brain corrects on next session — log as MISS-XXX in Missing Registry.**

---

---

# SECTION 5 — NAMING CONVENTIONS

## Tier 1 governance documents

| Type | Naming pattern | Example |
|---|---|---|
| Locked governance law | `[NAME]_LOCKED_v[N].md` | `FILE_STORAGE_GOVERNANCE_LOCKED_v1.md` |
| Authority / config | `[name]-v[N].yaml` | `authority.yaml` |
| Validator script | `validate-[name]-v[N].sh` | `validate-file-storage-v1.sh` |
| Research save | `[AGENT]-[DATE]-[DOMAIN]-[ID]/` | `governance_goal_specialist-20260608-015/` |
| Research meta | `_META.yaml` (always in save directory) | — |

## Tier 2 runtime files

| Type | Naming pattern | Example |
|---|---|---|
| Live pointer | `[name]-v[N].json` | `next-execution-pointer-v1.json` |
| Event log | `YYYY-MM-DD.jsonl` | `2026-06-08.jsonl` |
| Runtime state | `[name].json` | `execution.json` |

## Version bumping rule

- **Structural change** (new sections, enforcement rule change, threshold change) → bump version suffix (`_v1` → `_v2`) + update pointer in `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b`
- **Content change** (filling in fields, adding rows, updating timestamps) → no version bump, update `Last updated` timestamp

---

---

# SECTION 6 — ENFORCEMENT

## Validator

**Script:** `scripts/validate-file-storage-v1.sh`

**FAIL conditions:**

| # | Condition |
|---|---|
| 1 | A `_LOCKED_v1.md` governance doc exists outside `brain-os/` |
| 2 | A `_META.yaml` is missing from any `RESEARCH/by_date/` save directory |
| 3 | Any `_META.yaml` contains `execution_authority: true` |
| 4 | A `.json` runtime state file exists inside `brain-os/` or `scripts/` |
| 5 | `active-execution-rail-v1.json` contains `manual_fallback: true` without an ASF trace ID in the file |
| 6 | Master Tracker Section 8 lists a Tier 2 path that does not exist logged |
| 7 | Any new Tier 2 file exists in `~/.sina/` that is not registered in Master Tracker Section 8 |

## Enforcement failure clause

If an agent saves a file to the wrong tier, Brain logs a `MISS-XXX` entry in the Master Operating Tracker Section 5 (Missing Registry) with severity P1 and corrects the placement before the next session delivers a Worker INBOX.

**File placement is not optional. Correct tier on first save.**

---

---

# SECTION 7 — REAL-WORLD MODELS THIS FOLLOWS

This governance law is derived from proven production models operating at scale in 2025–2026:

| Model | Organization | Principle applied |
|---|---|---|
| GitOps | Kubernetes / ArgoCD | Git repo = governance SSOT · Runtime state lives separately · Git history = audit trail |
| Infrastructure as Code | HashiCorp (Terraform) | Config in git · State in separate backend · State file never edited by humans |
| Workflow definitions | Temporal / LangGraph | Workflow logic in code (git) · Execution state in runtime server · Never mixed |
| Runbook repo | Stripe (internal) | All governance, incident response, and rules in one internal git repo |
| Producer/consumer state | Netflix Hollow | Single producer writes state · Consumers read from cache · No direct state duplication |
| Monorepo governance | Google / Meta | One repo for all strategic content · Fast grep · Full history · Clear ownership |

**Common pattern across all six:** governance and strategy are versioned and human-readable; runtime operational state is separate, machine-managed, and only referenced — never duplicated — by the governance layer.

---

---

# SECTION 8 — AUTHORITY & OWNERSHIP SUMMARY

| Who | Tier 1 access | Tier 2 access | Tier 3 access |
|---|---|---|---|
| ASF | Full override — approves structural changes | Sets `manual_fallback` via Hub only | Full |
| Brain (Execution Core) | Read + write (content updates) · structural changes = ASF order | Writes reconciled_decision.yaml · pointer on Brain SYNC | Read reference only |
| SourceA Worker | Read + write (receipts, build progress, scripts) | Read only (INBOX, pointer) | Read reference only |
| Specialists (Commercial / Governance / Research) | Read + write (RESEARCH saves with _META.yaml only) | Read only | Read reference only |
| Old Brain (archive broker) | Read only — search and compare | No access | Read reference only |
| External advisors (GPT / Claude) | Read only — advise, no disk authority | No access | No access |
| Orchestrator / validators | Read (Tier 1) | Write (Tier 2 state) | No access |

---

---

# DOCUMENT INTEGRITY

**This document is LOCKED.**  
No agent may modify the structure, enforcement rules, tier definitions, or naming conventions without:
1. An explicit ASF instruction naming this document
2. A version bump to `_v2` with a pointer update in `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md §0b`
3. `validate-file-storage-v1.sh` updated to match any changed enforcement rules

**Ratified:** 2026-06-08  
**Authority:** ASF — five-source convergence ratification (Old Brain · Brain · Governance Specialist · GPT · Claude External Advisor)  
**Trace:** AUTO-TRACE-FILE-STORAGE-GOVERNANCE-LOCK-2026-06-08
