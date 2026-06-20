# sa-0969 — Semantic diff L14 integration with packet assembly

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research spike · **No D-modules · No code edits in CHECK**

## One-line verdict

> **L14 is partially shipped as D13** — git diff + D3 impact hydrates `packet.diff` before D15 assembly. True semantic diff (AST/LLM patch validation) is **not built**; spike documents integration depth options without new D-modules.

---

## Namespace map (do not conflate)

| Name | Internal | Status | Role |
|------|----------|--------|------|
| **L14** (WTM roadmap) | Reference layer — semantic diff + change impact | **partial** | External analog / gap tracker |
| **D13** (product) | `pre_llm/diff_intelligence/` | **shipped** | Git read-only diff + D3 impact map |
| **D14** | Context compression | **shipped** | Consumes D13 for diff layer in narrative |
| **D15** | Context assembly | **shipped** | `assemble_packet()` hydrates D1–D14 → `llm_context_packet_v1.json` |

**Law:** `system_roadmap.py` L14 note — "D13 git diff + D3 impact — no LLM patch validation yet."

---

## Fabric today (disk truth)

### D13 — Diff Intelligence

| Field | Value |
|-------|--------|
| **SSOT** | `~/.sina/diff_intelligence_v1.json` |
| **API** | `GET /api/diff-intelligence-v1` |
| **Modules** | `git_diff_reader` · `impact_mapper` · `focus_reader` · `diff_engine` |
| **Chain** | D12 validation **before** D13 build |
| **Inputs** | Git name-status + numstat · D3 `impact_index` · D9 ranked focus paths |
| **Outputs** | `changes[]` · `impact_map` · `diff_ready` · per-file `severity` |
| **Gate** | `validate-diff-intelligence-v1.sh` |

### Packet assembly path (D13 → D15)

```text
run_diff_intelligence (D13)
  → write diff_intelligence_v1.json
run_context_compression (D14) — requires D13 live
  → diff layer in compressed narrative
assemble_packet (D15)
  → hydrate_from_disk_substrate()
  → packet.diff.changes + impact_map from D13 canonical
  → validate_packet() → gate_eligible
model_dispatch.prepare_packet — planner choke uses D15 assembly
```

**Hydrate contract** (`context_packet/schema.py`):

- Loads D13 only when `diff_ready` and `changes` non-empty
- Caps at 24 changes in packet · provenance lists `D13` path
- Errors land in `provenance.d13_hydrate_error` — silent degrade

### Dispatch policy link

| Policy class | L1 | L2 | Tier |
|--------------|----|----|------|
| `pos-dispatch` | suggest | **packet-assemble** | SAFE_AUTO* |

Diff intelligence feeds **packet-assemble** substrate — not direct dispatch without Eval-1b gate.

---

## L14 gap analysis (what "semantic" still means)

| L14 capability (roadmap) | D13 today | Gap |
|--------------------------|-----------|-----|
| Intelligent diff understanding | Git path/kind/line stats | No AST / semantic hunks |
| Change impact analysis | D3 `simulate_impact` + severity | Rule-based only |
| Patch validation | — | **Missing** — no pre-LLM patch proof |
| Focus alignment | `in_ranked_focus` from D9 | Partial — boolean flag only |
| Token budget for diff | D14 compresses diff layer | Narrative summary, not semantic merge |

**STRATEGIC-SLICE lock:** Architecture through D16 shipped — bottleneck is **behavioral proof (Eval-1b)**, not new D-module from this spike.

---

## Integration spike options (research — defer implement)

### I1 — Assembly force-refresh coupling

When `assemble_packet(force_refresh=True)`, ensure D13 refresh runs **before** D14 (today via `compression_engine` only). Research: single orchestration entry avoids stale `diff_intelligence_v1.json` on assembly.

### I2 — Ranked-focus weighting

Use D9 `ranked_evidence` scores to sort `packet.diff.changes` — `in_ranked_focus` exists; extension = order + cap by intent class.

### I3 — Eval-1b diff assertions

Add structural task: `packet.diff.changes.length > 0` on grounded repo tasks — proves L14→packet wire in behavioral harness (no OpenRouter in RUN INBOX).

### I4 — Hub panel crosswalk

`/api/diff-intelligence-v1` + packet preview tab shows same `change_id` set — anti-staleness if API fresh but hydrate empty.

### Defer (ASF order required)

- AST/semantic diff engine (new module)
- LLM summarizer for diff hunks (violates pre-LLM law)
- D17+ module creation — `validate-d-module-creation-guard-v1.sh` blocks

---

## Industry compare (research only)

| Pattern | SourceA analog |
|---------|----------------|
| Cursor @codebase diff context | D13 git scope + focus paths |
| GitHub Copilot change summary | D14 narrative layer |
| Enterprise patch gates | D12 validation chain — not patch semantics |

**Honest claim:** "Diff intelligence before LLM" = **D13 rule-based** — not full L14 semantic engine.

---

## ACT — Live disk snapshot (2026-06-14)

| Artifact | Field | Value |
|----------|-------|-------|
| `~/.sina/diff_intelligence_v1.json` | `diff_ready` | unset · **0 changes** |
| `~/.sina/llm_context_packet_v1.json` | `packet.diff` | producer **None** · **0 changes** |
| Hydrate guard | `d13_hydrate_error` | none — empty diff skipped silently |

**ACT finding:** Integration **path exists** but live factory session has **no git delta** → packet ships without diff section. I3 Eval-1b assertion must use **grounded repo task with staged changes**, not idle drain turns.

---

## ACT — Maintainer implement checklist (I1 + I3 first)

| Step | Action | Owner | Gate |
|------|--------|-------|------|
| 1 | `assemble_packet(force_refresh=True)` chains D13 before D14 explicitly | Maintainer | `validate-context-assembly-v1.sh` |
| 2 | Sort `packet.diff.changes` by D9 `in_ranked_focus` then severity | Maintainer | `validate-diff-intelligence-v1.sh` |
| 3 | Add Eval-1b task `diff_hydrate_non_empty` on fixture repo | Maintainer | `validate-eval-packet-v1b-live.sh` |
| 4 | Hub crosswalk: diff API `change_id` set ⊆ packet diff | Maintainer | `audit_hub_source_alignment.py` |
| 5 | **Do not** add D17 module — guard blocks | Worker research only | `validate-d-module-creation-guard-v1.sh` |

**Soak:** 2 weeks shadow before promoting I3 to CI CRITICAL.

---

## ACT — Relation to sa-0963 (Eval pilot expansion)

sa-0963 designed Eval-1b task JSON expansion — **I3 diff assertion** belongs in that suite as structural proof:

```json
{
  "task_id": "eval-diff-hydrate-v1",
  "assertions": ["packet.diff.changes.length >= 1", "packet.diff.producer == D13"],
  "fixture": "staged_git_delta_fixture",
  "openrouter": false
}
```

Research only in this ACT — no `tasks.json` edit in RUN INBOX (feasibility gate).

---

## Duplicate sa titles

Same task at **sa-0919**, **sa-0944**, **sa-0969**, **sa-0994**. Canonical research for **sa-0969** CHECK→ACT→VERIFY closeout.

---

## Verdict

**L14 integration with packet assembly is already wired at D13→hydrate→D15** — spike value is **depth options** (I1–I4) and honest L14 gap labeling, not a new module. Maintainer implements I1/I3 after Eval-1b expansion (sa-0963 family).

**One-line:** D13 is the product face of L14 today — semantic depth deferred; packet path proven logged.
