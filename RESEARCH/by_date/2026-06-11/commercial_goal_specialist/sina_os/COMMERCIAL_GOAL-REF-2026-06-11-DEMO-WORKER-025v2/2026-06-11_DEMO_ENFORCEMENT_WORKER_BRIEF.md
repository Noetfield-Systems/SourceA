
**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
[COMMERCIAL_GOAL_AGENT_REF · commercial_goal_specialist · COMMERCIAL_GOAL-REF-2026-06-11-DEMO-WORKER-025v2]

| agent_name | Commercial Goal Specialist |
| agent_id | `commercial_goal_specialist` |
| ref_tag | `COMMERCIAL_GOAL-REF-DEMO-WORKER-025v2` |
| trace_id | `COMMERCIAL_GOAL-REF-2026-06-11-DEMO-WORKER-025v2` |
| parent_trace | `COMMERCIAL_GOAL-REF-2026-06-11-100M-SIGNAL-6MO-v2` · `THREE-LAYER-028` |
| execution_authority | false — Worker implements on SourceA only; Brain assigns `sa-*` |

## 0. DISK BASELINE (read before building)

**DEMO-ENF-S1 through S6 are already shipped.** Do not rebuild D1–D5 from scratch.

Verify first:

```bash
bash scripts/validate-demo-enforcement-v1.sh --tamper-test   # must PASS
python3 scripts/governance_demo_gate_v1.py --case block      # must exit ≠ 0
python3 scripts/governance_demo_gate_v1.py --case allow      # receipt + spine_event_id
```

**Your sprint focus:** S7/S9 artifacts · `validate-demo-write-path-v1.sh` · close remaining bypass paths · export bundle for portfolio lanes.

---

# SOURCEA WORKER — Governance Demo (BLOCK / ALLOW / Tamper)

**Layer:** **SourceA engine only (Layer 1)** — not Noetfield product · not TrustField product  
**Paste into Cursor on `/Users/sinakazemnezhad/Desktop/SourceA` only.**  
**Sprint ID:** `DEMO-ENF-GOVERNANCE-2026-06-11`  
**Authority:** `100M-SIGNAL-6MO-v2` · **W1 + W2 only**

---

## 1. YOUR ROLE

You are the **SourceA enforcement-demo worker**. You ship the **smallest system that cannot lie** in a 5-minute investor demo:

1. **BLOCK** — invalid **governance-demo** intent stopped at gate  
2. **ALLOW** — valid intent → execute stub → receipt + spine row  
3. **TAMPER** — hand-edited receipt → validator **FAIL** (live)

**Example intent flavor:** generic `apply_policy_change` (Copilot-like **wording only** for investor clarity) — **not** building noetfield.com or TrustField app.

**Investor sentence (do not rename product):**  
> We make AI execution impossible to bypass governance.

**You do NOT:** Trust OS / Decision Cloud naming · whitepaper · 1000-pack drain · semantic memory · cloud deploy · learning loop · full platform commit gate for entire repo.

---

## 1. MANDATORY READ (in order)

1. `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-11_100M-SIGNAL-6MO-PLAN-v2.md`
2. `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-11_THREE-LAYER-ARCHITECTURE_SSOT.md`
2. `os/plan-library/NORTH-STAR-GOV-KERNEL-INVARIANT-OS.md` (pointer only — no scope creep)
3. `brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md`
4. `brain-os/system/EVENT_CONTRACT.yaml`
5. `scripts/sourcea_execute_v1.py` · `scripts/gatekeeper_v1.py`
6. `scripts/rt_live_gate_v1.py` · `scripts/validate-universe-invariants-v1.sh`
7. `scripts/governance_event_spine_v1.py` (append + find_by_event_id)

**Maintainer P0 runs in parallel — do not block FR-003 / 1.10:** your demo path is **additive**, not a reorder.

---

## 2. WIN CONDITION (binary)

| ID | PASS when |
|----|-----------|
| **W1-DEMO** | Founder runs 5-min script live: BLOCK → ALLOW → tamper FAIL — no fake steps |
| **W2-KERNEL** | Demo-scoped actions use **only** `sourcea_execute_v1.py` (or new thin wrapper it calls) as write entry |
| **W2-RECEIPT** | Each ALLOW produces receipt JSON + spine row with matching `event_id` |
| **W2-VALIDATOR** | `validate-demo-enforcement-v1.sh` exits 0 after ALLOW, exits 1 after tamper |

---

## 3. DEMO SCENARIO (frozen — Copilot wedge for NF-001)

**Fictional intent (Noetfield buyer language):**

| Case | Intent payload | Rule | Expected |
|------|------------------|------|----------|
| **BLOCK** | `apply_copilot_policy_change` · `policy_id: COPILOT-DENY-EXTERNAL-SHARE` · `action: enable` · `risk: high` | Rule **P-001**: external share enable requires `approval_ref` | Gatekeeper **DENY** · spine event `AUTHORITY_REJECT` or `VALIDATOR_FAIL` · **no** receipt with `status: DONE` |
| **ALLOW** | Same · `policy_id: COPILOT-ALLOW-READONLY` · `action: enable` · `approval_ref: TLE-2026-001` | Rule **P-001** satisfied | Gatekeeper **PASS** · execute stub · receipt **DONE** · spine row with proof path |
| **TAMPER** | (after ALLOW) | — | Human edits receipt logged → run validator → **FAIL** |

**Stub execute:** No real M365 API — log `"EXECUTE_STUB: policy applied"` to stdout + receipt `evidence` field. Demo proves **governance**, not Microsoft integration.

---

## 4. DELIVERABLES (ship in order)

### D1 — Demo policy + intent schema

**Create:** `brain-os/demo/governance_demo_policy_v1.json`

```json
{
  "schema": "governance-demo-policy-v1",
  "rules": [
    {
      "id": "P-001",
      "description": "High-risk Copilot policy enable requires approval_ref",
      "deny_when": {
        "intent": "apply_copilot_policy_change",
        "risk": "high",
        "missing_field": "approval_ref"
      }
    }
  ]
}
```

**Create:** `brain-os/demo/governance_demo_intents_v1.json` — include `block_case` and `allow_case` payloads above.

---

### D2 — Demo gatekeeper hook

**Create:** `scripts/governance_demo_gate_v1.py`

- Input: intent JSON (file or stdin)  
- Load policy P-001  
- Return `{ "safe_to_execute": bool, "rule_id": "P-001", "reason": "..." }`  
- **Integrate** into `gatekeeper_v1.run_gatekeeper()` when env `SOURCEA_DEMO_ENFORCE=1` or flag `--demo-enforcement` on `sourcea_execute_v1.py`

**Do not** fork a second execution stack — extend gatekeeper path only.

---

### D3 — Demo execute + receipt writer

**Create:** `scripts/governance_demo_execute_v1.py`

Flow:

```text
intent → governance_demo_gate_v1 → if deny: append AUTHORITY_REJECT to spine → exit 1
       → if allow: EXECUTE_STUB → write receipt → append spine row → exit 0
```

**Receipt path:** `~/.sina/demo-enforcement/receipts/demo-{uuid}.json`  
**Schema:** extend `sourcea-sa-receipt-v1` fields + require:

- `spine_event_id`  
- `rule_id`: `P-001`  
- `intent_hash`  
- `receipt_checksum` (same pattern as `rt_live_gate_v1._verify_receipt_checksum`)

**Spine:** use `governance_event_spine_v1.append_event` with `proof` pointing at receipt path.

**Entry point for demo:** extend `sourcea_execute_v1.py`:

```bash
python3 scripts/sourcea_execute_v1.py --demo-enforcement --intent brain-os/demo/governance_demo_intents_v1.json --case block
python3 scripts/sourcea_execute_v1.py --demo-enforcement --intent ... --case allow
```

All demo writes **must** go through this path — document any exception in `brain-os/demo/DEMO_BYPASS_AUDIT_v1.md`.

---

### D4 — Append-only receipt log

**Create:** append to `~/.sina/demo-enforcement/receipt-log.jsonl` on each ALLOW (never overwrite prior rows).

Validator must reject: PASS receipt whose latest log entry checksum ≠ file checksum.

---

### D5 — Validator

**Create:** `scripts/validate-demo-enforcement-v1.sh`

Checks:

1. Latest demo receipt (if `status: DONE`) has `spine_event_id`  
2. Spine row exists via `find_by_event_id`  
3. Checksum valid (reuse rt_live patterns)  
4. `rule_id` present and matches policy file  
5. After intentional tamper test file — **must exit 1**

Wire into existing pattern from `validate-universe-invariants-v1.sh` — **reuse helpers**, don’t duplicate universe logic blindly.

---

### D6 — Demo runbook (founder one-tap later)

**Create:** `brain-os/demo/INVESTOR_DEMO_RUNBOOK_v1.md`

5-minute script (BLOCK → ALLOW → open receipt → show spine → tamper → validator FAIL).

Include exact commands — founder never copies from chat; Maintainer may wire Hub button later.

---

## 5. SUGGESTED `sa-*` SLICES (Brain assigns IDs)

Register with Brain — **VERIFY lane**, phase **demo-enforcement** (new sub-track OK if Brain agrees):

| Slice | Title | Done when |
|-------|-------|-----------|
| **S1** | D1 policy + intent fixtures | JSON committed · validator loads |
| **S2** | D2 demo gate integrated | BLOCK case exits 1 with reason P-001 |
| **S3** | D3 allow path + receipt + spine | ALLOW receipt DONE + spine row |
| **S4** | D4 append-only log | Overwrite without log → FAIL |
| **S5** | D5 validate-demo-enforcement-v1.sh | PASS/FAIL reproducible |
| **S6** | D6 runbook + internal dry-run | Maintainer witnesses 5-min dry-run |

**Receipt law:** each closed slice → `receipts/sa-XXXX-receipt.json` via normal closeout (factory law unchanged).

---

## 6. ACCEPTANCE TEST (Worker self-check before closeout)

```bash
# BLOCK
python3 scripts/sourcea_execute_v1.py --demo-enforcement --case block
test $? -ne 0

# ALLOW
python3 scripts/sourcea_execute_v1.py --demo-enforcement --case allow
test $? -eq 0

# Validator PASS
bash scripts/validate-demo-enforcement-v1.sh

# Tamper (manual step documented in runbook)
# edit latest demo receipt field → bash scripts/validate-demo-enforcement-v1.sh → must FAIL
```

---

## 7. FORBIDDEN

- Marketing rename sprint  
- Hub hero / command-data rewrite (Maintainer)  
- Real OpenAI/M365 API calls in demo  
- Bypassing gatekeeper for “speed”  
- Claiming full-repo single commit gate (demo scope only)  
- Factory drain / 1000-pack as demo metric  

---

## 8. OUT OF SCOPE (other layers — separate chats)

- **Noetfield** product/site (`NOETFIELD-LANE-029` · Mandatory Noetfield chat)  
- **TrustField** product/site (`TRUSTFIELD-LANE-030` · Mandatory TrustField chat)  
- Hub hero rewrite (Maintainer) · investor deck (Commercial)  

---

## 9. CLOSEOUT REPORT (paste back to Commercial Goal)

When done, report:

1. `sa-*` IDs closed  
2. Paths to policy, scripts, validator, runbook  
3. Screenshot or log excerpt: BLOCK / ALLOW / tamper FAIL  
4. Known bypass paths remaining (honest list)  
5. `validate-demo-enforcement-v1.sh` exit codes  

---

## 10. ONE LINE

> **Harden and film the governance demo path that already BLOCKs, ALLOWs with receipt+spine, and FAILs on tamper — do not scope-creep to NF/TF product builds.**

**Parent plan:** `COMMERCIAL_GOAL-REF-2026-06-11-100M-SIGNAL-6MO-v2` · `BIG-PICTURE-031`  
**execution_authority:** false
