# Governance Event Spine — schema & reference graph (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-GOV-EVENT-SPINE  
**Authority:** ASF · **G1+G2** runtime governance kernel (not apex over Pack 5)  
**Parent:** `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` §5 · `TRUST_LEDGER_SCHEMA_LOCKED_v1.md`  
**Machine:** `scripts/governance_event_spine_v1.py` · `scripts/governance_reference_graph_v1.py`  
**Ledger:** `~/.sina/governance-event-spine-v1.jsonl`  
**Graph:** `~/.sina/governance-reference-graph-v1.json`  
**Row ID:** `GOV_EVENT_SPINE`

---

## 0. One sentence

> **Every governance state change emits one spine row; reference graph metadata on law objects drives impact scan and selective materialization — hub/catalog are projections only.**

**Golden rule (LOCK):** `brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md`

> *State is canonical. Events are history. Graph is intelligence. Projections are disposable. Validators are authority. Router is governor. Workers are replaceable.*

---

## 0b. Closed-loop control (runtime kernel)

```text
Intent → Pick → Event → Ledger → Router → Reference Graph → Impact Analysis
  → Execution Queue → Worker(s) → Validator → Projection Materializer
  → Monitor → Feedback → Replay / Recovery → Stable State
```

**Router pattern (small context):** Global router (governance entry · domain) → Domain router (truth bundle + one skill) → Worker (working set only).

---

## 1. G1 — Spine row schema (`governance-event-spine-v1.1`)

**15-field implementation spec** (new rows MUST use v1.1):

| Field | GPT name | Required | Notes |
|-------|----------|----------|-------|
| `event_id` | EventID | yes | `GEV-{uuid}` |
| `parent_event_id` | ParentEventID | no | chain for replay |
| `correlation_id` | CorrelationID | yes | batch / session |
| `object_id` | ObjectID | yes | authority row · `sa-XXXX` · `FR-*` · pick id |
| `version` | Version | yes | monotonic int per object_id |
| `agent_id` | AgentID | yes | `sourcea_worker` · `maintainer` · `founder` |
| `law_id` | LawID | no | authority row id e.g. `LIVE_GOV_BP` |
| `skill_id` | SkillID | no | skill or broker gate name |
| `validator_set` | ValidatorSet | yes | list of `validate-*.sh` |
| `affected_objects` | AffectedObjects | yes | impact scan object ids |
| `replay_pointer` | ReplayPointer | yes | `{event_type}:{object_id}:{version}` |
| `projection_version` | ProjectionVersion | yes | materializer generation tag |
| `status` | Status | yes | `committed` · `pending` · `failed` · `replayed` |
| `checksum` | Checksum | yes | sha256 first 16 of canonical json |
| `at` | Timestamp | yes | ISO8601 UTC |

**Also on row (wire compat):** `schema` (`governance-event-spine-v1.1`) · `event_type` · `object_kind` · `replay_key` (= `replay_pointer`) · `payload` · `projection_targets` · `gate` · `proof`

**Legacy:** rows with `schema: governance-event-spine-v1` remain valid in ledger; new appends use v1.1 only.

**Immutable:** No state change to **governance projections** without a spine row (G3 enforcement grows from here).

---

## 2. Event types (v1)

| `event_type` | Emitter | `object_kind` |
|--------------|---------|---------------|
| `FOUNDER_PICK` | live form / Canvas receipt | `pick` |
| `WORKER_ROUND` | `goal1_lane_broker` worker-submit | `task` |
| `LAW_TOUCHED` | maintainer SAVE on authority row doc | `law` |
| `PROPAGATION` | `governance_propagation_cascade` | `system` |
| `VALIDATOR_PASS` | maintainer proof scripts | `system` |
| `EXTERNAL_CRITIC_INGEST` | research pipeline | `system` |
| `RECOVERY_FOUND` | conscious-recovery | `system` |
| `IMPACT_SCAN` | reference graph | `law` |

---

## 3. G2 — Knowledge graph (not dependency list only)

**Edge kinds:** `law` —governs→ `skill` —executed_by→ `agent` —produces→ `artifact` —projected_to→ `hub`|`monitor`|`catalog`|`search`

**LAW_CHANGED flow:** emit spine → graph query → affected objects → queue → selective regeneration (not full rebuild).

Each **law object** (authority row id) may have:

```json
{
  "id": "LIVE_DECISION_FORM",
  "doc": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md",
  "skills": ["sina-conscious-recovery"],
  "rules": ["lost-link-recovery-reward.mdc"],
  "validators": ["validate-live-founder-decision-form-v1.sh"],
  "scripts": ["live_founder_decision_form_v1.py"],
  "projections": ["catalog", "live_form"],
  "materializer": "align_command_data_ui_v1.py"
}
```

**Impact scan:** `LAW_TOUCHED` on row X → traverse graph → list validators + projections → cascade **selective** materializers.

**Machine build:** `python3 scripts/governance_reference_graph_v1.py --build`

---

## 3b. G3 — LAW_CHANGED selective materialization (shipped)

```text
LAW_TOUCHED → impact_scan → projection queue → drain → materializers (hub|monitor|catalog|…)
```

| Artifact | Path |
|----------|------|
| Worker | `scripts/governance_projection_g3_v1.py` |
| Queue | `~/.sina/governance-projection-queue-v1.jsonl` |
| Write gate | `~/.sina/governance-projection-gate-v1.json` |
| Receipt | `~/.sina/governance-projection-g3-receipt-v1.json` |

**Maintainer:** after SAVE on authority row doc:

```bash
python3 scripts/governance_projection_g3_v1.py --law-touched ROW_ID --reason maintainer_save --drain
```

**Enforcement:** `write_panel_outputs` requires gate or recent spine row (`SINA_G3_ENFORCE=0` to bypass).

```bash
bash scripts/validate-governance-projection-g3-v1.sh
```

---

## 4. Projection layer rule (P1 / G3 — disposable)

| Projection (never hand-edit) | Materializer | View |
|------------------------------|--------------|------|
| `command-data-canonical.json` | `hub_projection_canonical_v1.py` | **Validator** |
| `command-data-runtime.json` | same split | Monitor only |
| `command-data.json` | `align_command_data_ui_v1.py` | Hub UI (merged) |

**Acceptance test (Track 2):** delete projections → materialize → same **canonical** fingerprint (runtime excluded by split, not exclusion list).

```bash
bash scripts/validate-hub-projection-disposable-v1.sh
```

| `ecosystem_master_catalog` JSON | `ecosystem_master_catalog_v1.py` |
| `live-founder-decision-form-v1.json` | `live_founder_decision_form_v1.py` |
| `governance-reference-graph-v1.json` | `governance_reference_graph_v1.py --build` |
| monitor mirror | `monitor_live_sync_v1.py` |

---

## 4c. G7 — Self-heal daemon (unified)

**Law:** `brain-os/law/GOVERNANCE_SELF_HEAL_G7_LOCKED_v1.md`

```text
scan (graph · canonical hub · gate · queue · monitor · S10 · inbox) → heal → G3/G4/S10 delegates
```

```bash
python3 scripts/governance_self_heal_daemon_v1.py --heal --json
bash scripts/validate-governance-self-heal-g7-v1.sh
```

**Receipt:** `~/.sina/governance-self-heal-receipt-v1.json`

---

## 5. Replay (G4 — context-aware worker)

**Not log replay only.** Pipeline:

```text
replay_pointer → load event → object snapshot at version → graph context → impact → resume queue
```

| Step | Machine |
|------|---------|
| Load event | `governance_event_spine_v1.py` — `find_by_replay_pointer` / `find_last` |
| Object snapshot | ledger `object_history` + `~/.sina/run-inbox-disk-truth-v1.json` for `sa-*` |
| Graph + impact | `governance_reference_graph_v1.py` — `impact_scan` + `knowledge_edges` filter |
| Resume queue | `WORKER_ROUND` → broker `_auto_deliver_next` · `PROPAGATION` → selective materializers |
| Receipt | `~/.sina/governance-replay-receipt-v1.json` |
| Recovery row | `RECOVERY_FOUND` spine append (`status: replayed`) |

```bash
# Dry-run (validator)
python3 scripts/governance_replay_worker_v1.py --last --event-type WORKER_ROUND --json

# Live resume
python3 scripts/governance_replay_worker_v1.py --replay-pointer 'WORKER_ROUND:sa-0791:1' --resume
```

---

## 6. Proof

```bash
cd ~/Desktop/SourceA && bash scripts/validate-governance-event-spine-v1.sh
bash scripts/validate-governance-replay-v1.sh
```

---

*End governance event spine schema*
