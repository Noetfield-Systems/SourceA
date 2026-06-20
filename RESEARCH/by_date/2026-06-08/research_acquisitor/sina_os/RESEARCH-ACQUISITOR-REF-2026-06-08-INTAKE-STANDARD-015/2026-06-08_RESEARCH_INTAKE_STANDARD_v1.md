# [Research Acquisitor · RESEARCH-ACQUISITOR-REF-2026-06-08-INTAKE-STANDARD-015]

**Saved:** 2026-06-08T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
trace:
  agent_name: Research Acquisitor
  agent_id: research_acquisitor
  trace_id: RESEARCH-ACQUISITOR-REF-2026-06-08-INTAKE-STANDARD-015
  session_transcript: 85dd7cd4-0977-4cfc-9449-ea278ea0baee
  date: 2026-06-08
  subject: sina_os
  summary: RESEARCH folder path layout + _META schema
  execution_authority: false

# RESEARCH folder — intake standard v1

**Root:** `~/Desktop/SourceA/RESEARCH/`  
**Law:** `RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md` (LOCKED — mandatory)  
**Enforcer:** `research_save_enforcer.py` · **Worker notice:** `WORKER_NOTICE_RESEARCH_SAVE_MANDATORY_v1.md`

## Layout (mandatory)

Every saved research artifact uses this path:

```
RESEARCH/by_date/{YYYY-MM-DD}/{worker_id}/{subject_slug}/{trace_id}/{filename}
RESEARCH/by_date/{YYYY-MM-DD}/{worker_id}/{subject_slug}/{trace_id}/_META.yaml
```

| Segment | Rule |
|---------|------|
| `YYYY-MM-DD` | Date of research **save** (or trace date if save is same day) |
| `worker_id` | Agent that produced the doc — see `WORKERS_REGISTRY.yaml` |
| `subject_slug` | Product/project lane — see `SUBJECTS_REGISTRY.yaml` |
| `trace_id` | Worker's full cite tag (unique folder per artifact family) |
| `filename` | Original filename; do not rename content away from vault |

## Worker IDs (use exactly)

| worker_id | Tag pattern |
|-----------|-------------|
| `research_acquisitor` | `RESEARCH-ACQUISITOR-REF-YYYY-MM-DD-*` or `RESEARCH-ACQUISITOR-YYYYMMDD-*` |
| `commercial_goal_specialist` | `COMMERCIAL_GOAL-REF-YYYY-MM-DD-*` |
| `governance_goal_specialist` | `governance_goal_specialist-YYYYMMDD-NNN` |

## Subject slugs (pick one primary)

| subject_slug | When to use |
|--------------|-------------|
| `trustfield` | trustfield.ca, RPAA/MSB, TF-P* SKUs |
| `noetfield` | noetfield.com, Copilot governance, NF-* SKUs |
| `dual_brand` | Both brands, entity boundary, invoicing split |
| `voice_ai` | Voice agents, telephony, speech stacks |
| `ai_dev` | Cloud IDE, autonomous SWE, Cursor/Devin class |
| `automation` | n8n, Make, agency workflow products |
| `mergepack` | MergePack / form-to-PDF evidence factory |
| `virlux` | VIRLUX product lane |
| `seven77` | 777 Foundation |
| `sina_os` | SourceA hub, governance spine, agent desk |
| `wire` | AI Dev Bridge, Tailscale, phone→Mac wire |
| `investor` | Deck, narrative, fundraising materials |
| `ecosystem` | Cross-portfolio landscape only |

Add a new slug only in `SUBJECTS_REGISTRY.yaml` after ASF names the product.

## _META.yaml (required on every save)

```yaml
trace_id: {full worker tag}
worker_id: {agent_id}
subject: {subject_slug}
subject_label: {human label}
thread: {THREAD-* from registry}
date: YYYY-MM-DD
source_path: {original vault or repo path}
archive_path: {path relative to RESEARCH/}
execution_authority: false
```

## Daily worker closeout checklist

1. Assign **trace_id** using your worker's tag standard (never generic prefixes).
2. Pick **one primary subject_slug**.
3. Copy artifact + write `_META.yaml` under the path above.
4. Append one line to `RESEARCH/INDEX.yaml` → `artifacts` (or run sync script when available).
5. Cite `trace_id` in worker closeout YAML — not chat.

## Routing files

- `RESEARCH/INDEX.yaml` — master manifest
- `RESEARCH/ROUTING_{SUBJECT}.yaml` — per-product lookup by worker + date
- `RESEARCH/_GOVERNANCE/` — registries and this standard

## Supersedes

- `7JUNE_ALL_RESEARCH_2026/` — migrated into `by_date/`; do not add new files there
- `archive/attachments/` for research intake — **do not use** for new research saves

## Active V3 worker handoff (portfolio)

| Brand | trace_id | subject |
|-------|----------|---------|
| trustfield.ca | `RESEARCH-ACQUISITOR-20260608-TF-001` | trustfield |
| noetfield.com | `RESEARCH-ACQUISITOR-20260608-NF-002` | noetfield |

V2 worker prompts are `superseded_by_v3` — archive only, not for new paste.
