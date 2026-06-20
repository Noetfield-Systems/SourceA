# Worker notice — mandatory research save (paste to every worker chat)

**Saved:** 2026-06-14T17:02:10Z · **Retrofit:** doc-datetime-law batch retrofit
**Law:** `RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md`  
**Cross-lane:** `AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md` — **SAVE = one file, nothing else**  
**Effective:** 2026-06-08 onward · **Applies to:** all Cursor workers, goal specialists, Research Acquisitor, portfolio repo agents

---

## §SAVE ONLY (founder paste — research / reports)

```text
SAVE ONLY: docs/research/<filename>
FORBIDDEN: AGENTS.md, SSOT, roadmap, registry, sync, other agents' files
```

Agent writes **that one file** → **STOP**. No ecosystem wiring.

---

## §PASTE BLOCK — copy everything below this line into worker chat

```
[SINA MANDATORY · RESEARCH SAVE LOCK v1]

You are a governed worker. Research and research-backed decisions are NOT saved in chat.
They MUST land in SourceA RESEARCH with your worker trace tag, subject, and date.

READ FIRST (do not skip):
  ~/Desktop/SourceA/RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md
  ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/RESEARCH_INTAKE_STANDARD_v1.md
  ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/SUBJECTS_REGISTRY.yaml
  ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/WORKERS_REGISTRY.yaml

─── YOUR WORKER ID ───
Pick ONE (use exactly — never invent abbreviations):

  research_acquisitor          → RESEARCH-ACQUISITOR-REF-YYYY-MM-DD-* or RESEARCH-ACQUISITOR-YYYYMMDD-*
  commercial_goal_specialist   → COMMERCIAL_GOAL-REF-YYYY-MM-DD-*
  governance_goal_specialist     → governance_goal_specialist-YYYYMMDD-NNN
  worker (site/build executor) → cite parent blueprint trace_id; producer: worker on register

FORBIDDEN tag families (superseded): RA-MKT-* · GOVGS-* · TF-COMM · NF-COMM · generic RA-REF without agent name

─── SUBJECT (pick one primary) ───
  trustfield    noetfield    dual_brand    voice_ai    ai_dev    automation
  mergepack     virlux       seven77       sina_os     wire      investor    ecosystem

─── MANDATORY 4-STEP SAVE (every research session / decision doc) ───

STEP 1 — VAULT
  Write YAML or MD to your canonical vault with trace_id in the file header.
  Chat alone does not count.

STEP 2 — MIRROR (SourceA RESEARCH)
  Path (LOCKED):
    ~/Desktop/SourceA/RESEARCH/by_date/{YYYY-MM-DD}/{worker_id}/{subject}/{trace_id}/{filename}
    ~/Desktop/SourceA/RESEARCH/by_date/{YYYY-MM-DD}/{worker_id}/{subject}/{trace_id}/_META.yaml

  _META.yaml minimum:
    trace_id, worker_id, subject, subject_label, thread, date,
    source_path, archive_path, execution_authority: false

STEP 3 — ENFORCER (you run this — founder never runs Terminal)
  python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py save \
    --path <vault_file> \
    --worker <worker_id> \
    --subject <subject_slug> \
    --trace-id <full_trace_id>

  Then verify:
  python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py verify \
    --trace-id <full_trace_id>

  Closeout is BLOCKED unless verify returns PASS.

STEP 4 — MACHINE REGISTRY (existing unified root law)
  python3 ~/Desktop/SourceA/scripts/research_root_sync.py register \
    --path <vault_file> --producer <worker_id> --bucket <bucket>
  python3 ~/Desktop/SourceA/scripts/research_root_sync.py sync

─── CLOSEOUT YAML (required tail on every round with research/decisions) ───

research_save:
  trace_id: <your full tag>
  worker_id: <agent_id>
  subject: <subject_slug>
  vault_path: <absolute vault path>
  research_mirror_path: RESEARCH/by_date/...   # relative to SourceA
  enforcer_verify: PASS
  execution_authority: false

─── WHAT MUST BE SAVED THIS WAY ───
  Market analysis, pricing, SKU decisions, GTM copy choices
  Legal/entity/money-flow considerations
  Competitor evidence, success models, revenue assessments
  Worker blueprints, considerations, mission outputs
  Anything you cite as justification for build or commercial action

─── FORBIDDEN ───
  Saving research only in chat or repo docs without RESEARCH mirror
  Saving under archive/attachments/ or random SourceA folders
  Skipping trace_id or using another agent's tag namespace
  Marking closeout done with enforcer_verify != PASS
  Promoting research to *_LOCKED*.md without maintainer lane

─── PORTFOLIO V3 BLUEPRINT CITES (if you are TF/NF site worker) ───
  TrustField: RESEARCH-ACQUISITOR-20260608-TF-001 · subject trustfield
  Noetfield:  RESEARCH-ACQUISITOR-20260608-NF-002 · subject noetfield
  V2 prompts are superseded — do not paste V2 for new work.

ACK on first reply:
  trace_id: <your tag or parent blueprint tag>
  worker_id: <agent_id>
  research_save_lock: ACK_RESEARCH_INTAKE_AND_SAVE_LOCK_v1
```

---

## §END PASTE BLOCK

---

## Distribution

| Audience | Action |
|----------|--------|
| TrustField worker | Paste §PASTE BLOCK at chat start |
| Noetfield worker | Paste §PASTE BLOCK at chat start |
| Research Acquisitor | Paste §PASTE BLOCK at session start |
| Commercial / Governance goal specialists | Paste §PASTE BLOCK at session start |
| Any new portfolio worker | Paste before first save |

## Cursor rule

Copy or symlink: `SourceA/.cursor/rules/research-save-mandatory.mdc`  
Workers in other repos: read law path above every session (rule travels by path reference).
