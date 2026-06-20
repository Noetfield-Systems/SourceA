# SOURCEA 1000 — LOCKED agent prompt pack (NO ASF)

**Status:** LOCKED · **Count:** 1000 · **Agent:** AGENT-AUTO-SOURCEA · **Date:** 2026-06-06

## Start here

| Item | Path |
|------|------|
| **Machine index** | [`sourcea-1000/REGISTRY.json`](sourcea-1000/REGISTRY.json) |
| **Prompt files** | [`sourcea-1000/prompts/`](sourcea-1000/prompts/) `sa-0001` … `sa-1000` |
| **Validation matrix** | [`sourcea-1000/VALIDATION.md`](sourcea-1000/VALIDATION.md) |
| **Curated queue** | [`SOURCEA-PRIORITY.md`](SOURCEA-PRIORITY.md) |
| **Root law** | [`SOURCEA_1000_LOCKED_PROMPT_LIBRARY_NO_ASF_v1.md`](../../SOURCEA_1000_LOCKED_PROMPT_LIBRARY_NO_ASF_v1.md) |
| **Global pack** | `~/.cursor/plans/no-asf-library/` |
| **Sibling packs** | `mono-1000` · `noetfield-1000` · `virlux-1000` |

## When you say PLAN WITH NO ASF

```bash
bash scripts/plan-no-asf-run.sh pick 1
# read os/plan-library/sourcea-1000/<path> → Agent prompt section
# implement → verify → mark done → closeout
bash scripts/plan-no-asf-run.sh verify-hub
bash scripts/plan-no-asf-run.sh closeout
bash scripts/validate-sourcea-1000-pack.sh
```

## Regenerate (taxonomy change only)

```bash
python3 scripts/generate-sourcea-1000-prompts.py
bash scripts/validate-sourcea-1000-pack.sh
```

## Phases (SourceA hub)

| Phase | Focus |
|-------|--------|
| `phase-s0-ssot-alignment` | GPT/Claude synthesis, honest_score, strategic hub |
| `phase-s1-eval-dispatch` | Eval-1b live, dispatch policy, grounding |
| `phase-s2-hub-build-ci` | strict build, validators, backend E2E, refresh |
| `phase-s3-scoreboard-fleet` | auto-green, essays, FR sync, governance fleet |
| `phase-s4-spine-loop` | spine bridge, graph executor, event bus |
| `phase-s5-commercial-lanes` | RunReceipt, wire, TrustField, PROGRAM_PROGRESS |
| `phase-s6-wtm-pre-llm` | D1–D16, L0–L16, ENFORCE, packet |
| `phase-s7-council-governance` | Council, rules-in-charge, mind share |
| `phase-s8-hub-ui-ux` | **Hub 2 Machine Hub** — `/machines/` pending registry · scheduled receipts · **not** Sina Command archive (`SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md`) |
| `phase-s9-research-models` | Critics, world-model compare, deferred L8/OpenRouter |

## Phase s9 research bibliography (canonical · sa-0975)

**Maintainer:** append on VERIFY closeout of new s9 research · duplicate T0/T1/T3 titles cite T2 row here.

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

## Founder-only (pick script skips)

- Actions → Enqueue eval spine bridge
- Fleet 6 lane reports + governance-drift essays
- Wire G3 attest · TrustField pilot vault

## Constraints (locked)

- No ASF as verify/progress authority
- No `dispatch_ready: true` globally
- No new D-modules without explicit plan
- No fabricated G3 / Track PASS
