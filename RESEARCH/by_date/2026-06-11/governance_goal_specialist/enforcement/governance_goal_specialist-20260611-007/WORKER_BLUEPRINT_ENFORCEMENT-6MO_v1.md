# Worker Blueprint — ENFORCEMENT-6MO minimal kernel + investor demo

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `governance_goal_specialist-20260611-007`  
**ASF order:** `ENFORCEMENT-6MO — route Worker`  
**worker_lane:** SourceA (`~/Desktop/SourceA`) · **execution_authority:** false (Brain assigns `sa-XXXX`)  
**Maintainer parallel:** FR-003 + Phase 1.10 — do not block; Worker does not own FR-003

---

## Brain routing header (paste into Worker INBOX — one sa per turn)

```
ASF: ENFORCEMENT-6MO — route Worker

Mission: Minimal enforcement kernel provable in 5-min investor demo.
Category (frozen): "We make AI execution impossible to bypass governance."

Parent trace: governance_goal_specialist-20260611-007
Blueprint: ~/.sina/agent-workspaces/governance_goal_specialist/WORKER_BLUEPRINT_ENFORCEMENT-6MO_v1.md
Tracker slice: ~/.sina/agent-workspaces/governance_goal_specialist/ENFORCEMENT-6MO_TRACKER_SLICE_v1.md

Pre-flight (Worker):
  - Read ENFORCEMENT-6MO_TRACKER_SLICE_v1.md
  - Read os/plan-library/NORTH-STAR-GOV-KERNEL-INVARIANT-OS.md (pointer only)
  - Read scripts/sourcea_execute_v1.py · gatekeeper_v1.py · rt_live_gate_v1.py
  - Run: bash scripts/validate-universe-invariants-v1.sh (must PASS before closeout)

Scope law: enforcement strength | demo credibility | willingness to pay ONLY.
Forbidden this lane: UI-6 · REGISTRY drain · WTM modules · naming sprint · whitepaper.

Closeout: WORKER_ROUND_REPORT · broker submit · one sa only · validator PASS
```

---

## Slice E1 — Bypass inventory (first Worker turn recommended)

**Goal:** Enumerate every path that mutates demo-scope state without `run_gatekeeper()`.

**Deliverables:**
1. `docs/ENFORCEMENT-6MO-BYPASS-INVENTORY_v1.md` (or `brain-os/system/` if Brain routes)
2. Table columns: `path/script` · `mutates` · `gatekeeper?` · `severity` · `fix slice`
3. CI stub: `scripts/validate-enforcement-bypass-inventory-v1.sh` — FAIL if inventory file missing or stale date >30d

**Demo scope (minimum):**
- `~/.sina/governance-event-spine*.jsonl` append
- `~/.sina/rt-live-gate-receipt-v1.json` write
- `~/.sina/healthy-queue-state-v1.json` write
- `agent-control-panel/command-data.json` hub sync write
- Worker spawn via `start_goal1_worker_turn_v1.py` / `plan-no-asf-run.sh`

**Known partial gates today:**
- `sourcea_execute_v1.py` → gatekeeper
- `claude_api_agent_v1.py` / `claude_code_agent_v1.py` → gatekeeper
- `start_goal1_worker_turn_v1.py` → gatekeeper
- Many scripts write `~/.sina` directly — inventory must list them

**Acceptance:** Brain can pick E2 from top 3 HIGH severity bypasses.

---

## Slice E2 — Commit gate (demo scope)

**Goal:** One CLI entry: intent in → gate → spine event → receipt path out.

**Deliverables:**
1. `scripts/commit_intent_v1.py` (or extend `sourcea_execute_v1.py` with `--intent-file`)
   ```text
   python3 scripts/commit_intent_v1.py --intent demo/intent-allow.json --json
   python3 scripts/commit_intent_v1.py --intent demo/intent-deny.json  # exit 1
   ```
2. Intent schema `demo/enforcement-intent-v1.schema.json`:
   - `intent_id`, `action`, `rule_id`, `payload_hash`, `engine`, `role`
3. On PASS: append governance spine row + write receipt under `~/.sina/receipts/enforcement/`
4. On FAIL: no write · exit 1 · gatekeeper reasons in stderr

**Acceptance:**
- Ungated call to demo action without `commit_intent_v1.py` documented as bypass (E1 row)
- `bash scripts/validate-gatekeeper-v1.sh` PASS

---

## Slice E3 — Append-only receipt trail

**Goal:** Tamper of latest receipt does not erase history; validator catches edit.

**Deliverables:**
1. Append-only log: `~/.sina/receipts/enforcement/receipts.jsonl` (one JSON per line)
2. Each receipt fields:
   - `receipt_id`, `intent_id`, `rule_id`, `spine_event_id`, `gate_status`
   - `receipt_checksum`, `created_at`, `proof_path`
3. Extend `rt_live_gate_v1.py` pattern: `_verify_receipt_checksum` reusable module
4. Hand-edit latest receipt file → `validate-universe-invariants-v1.sh` or E4 script **FAIL**

**Acceptance:** `touch` + edit receipt → validator exit 1 (record in receipt).

---

## Slice E4 — Demo validator

**Goal:** Single script for investor room / CI.

**Deliverables:**
1. `scripts/validate-enforcement-demo-v1.sh`
2. Checks:
   - Demo-scope commit path exists
   - Last receipt checksum valid
   - `spine_event_id` resolves in spine
   - `rule_id` in receipt maps to existing law file path
   - Inject `--tamper-test` flag: corrupt checksum → must exit 1
3. Wire into `validate-anti-staleness-bundle-v1.sh` only after E4 stable (Brain decision)

**Acceptance:** Run live on camera: normal PASS → tamper FAIL.

---

## Slice E5 — 5-minute demo package

**Goal:** Recordable demo without narrative sprint.

**Deliverables:**
1. `docs/ENFORCEMENT-6MO-DEMO-SCRIPT_v1.md` — minute-by-minute beats
2. `demo/enforcement/` — sample intents (allow + deny)
3. Optional: Hub one panel ( **SinaaiDataBase workspace only** per edit lock) showing kill + last receipt status

**Demo beats (non-negotiable):**
| Min | Beat |
|-----|------|
| 0:30 | Ungated / deny intent → **BLOCK** |
| 1:30 | Allow intent → **commit** → receipt + spine |
| 2:30 | Hand-edit receipt → validator **FAIL** |
| 4:00 | Kill flag (`auto-run-disabled-v1.flag`) → execution stopped |

**Acceptance:** One unedited screen recording path documented.

---

## Slice E6 — Commercial (parallel — Commercial specialist, not Worker)

Worker does **not** own E6. Commercial runs from week 1 with E5 storyboard.

---

## Existing assets to reuse (do not rebuild)

| Asset | Reuse |
|-------|-------|
| `gatekeeper_v1.py` | Gate before execute |
| `sourcea_execute_v1.py` | Pattern for E2 |
| `governance_event_spine_v1.py` | Spine append |
| `rt_live_gate_v1.py` | Receipt checksum + spine bind pattern |
| `validate-universe-invariants-v1.sh` | Extend for E4 |

---

## Forbidden (Worker)

- Replacing hub P0 / STRATEGIC-SLICE headline
- FR-003 implementation (Maintainer 2)
- Full factory `commit()` for all 279 validators — **demo scope only**
- Trust OS / Decision Cloud docs
- REGISTRY bulk completion

---

## Receipt template (Worker closeout)

```markdown
# sa-XXXX — ENFORCEMENT-6MO slice EX
**trace:** governance_goal_specialist-20260611-007
**slice:** E1 | E2 | E3 | E4 | E5
**validators:** validate-enforcement-demo-v1.sh · validate-universe-invariants-v1.sh
**bypass closed:** [list]
**demo ready:** yes/no
```

---

## Brain pick order

```
E1 (bypass inventory) → E2 (commit demo) → E3 (append receipts) → E4 (validator) → E5 (demo script)
```

Maintainer in parallel: FR-003 → 1.10 seal.

---

*Advocate blueprint — Brain assigns sa-XXXX and updates Master Operating Tracker §2 parallel lane.*
