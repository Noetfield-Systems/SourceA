# sa-0975 — Phase s9 research index for SOURCEA-1000-LOCK bibliography (CHECK)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**SA:** sa-0975 · phase-s9-research-models · T2  
**Duplicates:** sa-0925 · sa-0950 · sa-0999 (same title — canonical here)  
**Law:** `SOURCEA_1000_LOCKED_PROMPT_LIBRARY_NO_ASF_v1.md` · `SOURCEA-1000-LOCK.md`

## Thesis

`SOURCEA-1000-LOCK.md` lists phases and constraints but **lacks a bibliography** pointing to shipped phase-s9 research attachments. Without it, agents re-research duplicate titles (sa-0921/0971 essay moat, etc.). ACT should append a **canonical index** sourced from `archive/attachments/2026-06-14/` + `SOURCEA-PRIORITY.md` evidence rows.

## Gap audit (disk)

| Item | Present | Missing |
|------|---------|---------|
| Phase table (`phase-s9-research-models`) | Yes — line 48 | — |
| Bibliography / research index | **No** | Canonical attachment paths |
| REGISTRY link | Yes | Cross-ref to done research sas |
| PRIORITY evidence | Yes — sa-0960+ rows | Not mirrored in LOCK doc |

## Proposed bibliography block (ACT append target)

Append after **Phases** section in `brain-os/plan-registry/SOURCEA-1000-LOCK.md`:

### Phase s9 research bibliography (2026-06-14 canonical)

| SA | Topic | Attachment |
|----|-------|------------|
| sa-0951 | Model workflow gaps | `archive/attachments/2026-06-14/sa-0951-model-workflow-gaps-research_LOCKED_v1.md` |
| sa-0952 | Agent verify gates spike | `archive/attachments/2026-06-14/sa-0952-agent-verify-gates-spike_LOCKED_v1.md` |
| sa-0953 | RAGAS vs Eval-1b | `archive/attachments/2026-06-14/sa-0953-ragas-vs-eval1b-research_LOCKED_v1.md` |
| sa-0955 | L0-full MCP telemetry defer | `archive/attachments/2026-06-14/sa-0955-l0-full-mcp-editor-telemetry-defer_LOCKED_v1.md` |
| sa-0956 | POS dispatch promotion | `archive/attachments/2026-06-14/sa-0956-pos-dispatch-promotion-criteria_LOCKED_v1.md` |
| sa-0957 | WTM agent-os vs D-layer | `archive/attachments/2026-06-14/sa-0957-wtm-agent-os-vs-d-layer_LOCKED_v1.md` |
| sa-0958 | Critic law wrong-rate table | `archive/attachments/2026-06-14/sa-0958-critic-law-wrong-rate-table_LOCKED_v1.md` |
| sa-0959 | Fleet scoreboard taxonomy | `archive/attachments/2026-06-14/sa-0959-fleet-scoreboard-auto-check-taxonomy_LOCKED_v1.md` |
| sa-0960 | No-ASF verify authority | `archive/attachments/2026-06-14/sa-0960-no-asf-verify-authority-pattern_LOCKED_v1.md` |
| sa-0961 | Mono vs SourceA pick workflow | `archive/attachments/2026-06-14/sa-0961-mono-sourcea-1000-pick-workflow-compare_LOCKED_v1.md` |
| sa-0962 | Hub refresh parallelize | `archive/attachments/2026-06-14/sa-0962-hub-refresh-parallelize-progress-bowl_LOCKED_v1.md` |
| sa-0963 | Eval pilot expansion tasks JSON | `archive/attachments/2026-06-14/sa-0963-eval-pilot-expansion-tasks-json-design_LOCKED_v1.md` |
| sa-0965 | Event bus topic taxonomy | `archive/attachments/2026-06-14/sa-0965-event-bus-topic-taxonomy-spine-learning-loop_LOCKED_v1.md` |
| sa-0966 | ENFORCE IDE bypass gates | `archive/attachments/2026-06-14/sa-0966-enforce-ide-bypass-industry-gate-patterns_LOCKED_v1.md` |
| sa-0967 | Two-speed clocks case study | `archive/attachments/2026-06-14/sa-0967-two-speed-clocks-strategic-slice-lane-p0-case-study_LOCKED_v1.md` |
| sa-0968 | Governance fleet FR lazy-load | `archive/attachments/2026-06-14/sa-0968-governance-fleet-validator-lazy-load-fr-rows_LOCKED_v1.md` |
| sa-0969 | Semantic diff L14 spike | `archive/attachments/2026-06-14/sa-0969-semantic-diff-l14-packet-assembly-spike_LOCKED_v1.md` |
| sa-0970 | WTM v5 vs v4 migration | `archive/attachments/2026-06-14/sa-0970-world-model-v5-v4-migration-lessons_LOCKED_v1.md` |
| sa-0971 | Essay discourse fleet moat | `archive/attachments/2026-06-14/sa-0971-agent-essay-discourse-fleet-compliance-moat_LOCKED_v1.md` |
| sa-0972 | Hub-only vs terminal-first | `archive/attachments/2026-06-14/sa-0972-founder-hub-only-vs-terminal-first-agent-products_LOCKED_v1.md` |
| sa-0973 | Spine-bridge proof matrix | `archive/attachments/2026-06-14/sa-0973-spine-bridge-founder-proof-types-matrix_LOCKED_v1.md` |
| sa-0974 | PROGRAM_PROGRESS sync incidents | `archive/attachments/2026-06-14/sa-0974-program-progress-machine-sync-vs-manual-asf-edit-incidents_LOCKED_v1.md` |

**Rule:** Duplicate-tier titles (T0/T1/T3) → cite **canonical T2** row above; do not re-research.

## Index maintenance contract (machine)

| Trigger | Action |
|---------|--------|
| sa VERIFY closeout | Append PRIORITY row (already shipped) |
| Quarterly sa-0975-class ACT | Sync bibliography table in LOCK doc |
| New attachment under `archive/attachments/YYYY-MM-DD/` | Add row on next s9 index sa |
| Validator | `validate-sourcea-1000-s9-bibliography-v1.sh` (ACT) |

## Live snapshot

| Metric | Value |
|--------|-------|
| s9 attachments indexed (2026-06-14) | **22** canonical rows |
| Factory Valid YES | **653/1000** (separate from bibliography) |
| LOCK doc bibliography section | **absent** — ACT target |

## ACT backlog

1. Append **Phase s9 research bibliography** section to `SOURCEA-1000-LOCK.md`
2. Ship `validate-sourcea-1000-s9-bibliography-v1.sh` — asserts section + min row count
3. PRIORITY evidence row

## WTM thread

- **Spine:** phase-s9-research-models · deferred OpenRouter/L8  
- **Related:** `SOURCEA-PRIORITY.md` evidence chain · duplicate title consolidation  
- **Deferred:** Auto-generate index from REGISTRY on each closeout (maintainer)

## CHECK verdict

Bibliography **content is ready** logged; `SOURCEA-1000-LOCK.md` needs ACT append to stop s9 research re-duplication.
