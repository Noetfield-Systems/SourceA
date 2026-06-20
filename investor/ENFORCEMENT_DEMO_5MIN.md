# ENFORCEMENT-6MO — 5-minute investor demo (full speaker notes)

**Law:** `brain-os/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md`  
**Scenario:** NF Copilot governance wedge (Rule P-001) — stub only, no M365 API  
**Run (executor):** `bash scripts/demo-enforcement-5min-v1.sh`  
**CI:** `bash scripts/validate-demo-enforcement-v1.sh` · `--tamper-test` for tamper beat  
**Index:** `brain-os/demo/ENFORCEMENT_ARTIFACTS_INDEX_v1.md`

---

## Before the room

| Check | Command | Expect |
|-------|---------|--------|
| Copilot validator | `bash scripts/validate-demo-enforcement-v1.sh` | `OK:` |
| Universe invariants | `bash scripts/validate-universe-invariants-v1.sh` | `OK:` |
| Receipt dir | `ls ~/.sina/demo-enforcement/receipts/` | writable |

**Founder says only:** category sentence + beats. **Executor** runs commands (or Hub Action when Maintainer wires it).

**Category sentence (memorize):**

> We make AI execution impossible to bypass governance.

**Do not say:** Trust OS · Decision Cloud · AI Kernel · $100M close in 6 months · factory drain %.

---

## Minute-by-minute script

### 0:00 — Thesis (30 sec)

**Say:**

> Enterprises are deploying Copilot and agent stacks faster than they can prove what ran, what was blocked, and whether anyone bypassed policy. If AI executes without enforceable governance, the deployment fails audit — not because the model is wrong, but because there is no proof path. We built the commit gate that blocks invalid actions and records every allowed one — and the system fails if you tamper with the receipt.

**Show:** Title slide or terminal prompt only. No fake UI.

---

### 0:30 — BEAT 1: BLOCK (60 sec)

**Scenario:** High-risk Copilot policy change — enable external share — **no** `approval_ref`.

**Say:**

> First, an AI agent tries a high-risk Copilot policy change without approval. Watch the gate — not the model — stop execution.

**Executor runs:**

```bash
cd ~/Desktop/SourceA
python3 scripts/sourcea_execute_v1.py --demo-enforcement --case block
```

**Expect:** exit code **≠ 0**. Output includes `BLOCKED` and reason `high-risk enable requires approval_ref`.

**Point at screen:**

- Rule **P-001** fired  
- Outcome **BLOCKED**  
- **No** receipt with `status: DONE` on spine  

**Say:**

> No DONE receipt. No pretend success. Governance enforced before side effects.

---

### 1:30 — BEAT 2: ALLOW (60 sec)

**Scenario:** Same wedge — readonly Copilot policy — with `approval_ref: TLE-2026-001`.

**Say:**

> Same class of action — but now with compliance approval on record. One write path: commit → gate → receipt → spine.

**Executor runs:**

```bash
python3 scripts/sourcea_execute_v1.py --demo-enforcement --case allow
```

**Expect:** exit **0**. Receipt shows `COMMITTED`, `status: DONE`, `spine_event_id`, `receipt_checksum`.

**Optional — show receipt file:**

```bash
cat ~/.sina/demo-enforcement/receipts/latest-demo-receipt.json | head -20
```

**Say:**

> Every allowed action gets a receipt bound to a spine row. This is what FINTRAC and procurement ask for — not another agent framework slide.

---

### 2:30 — BEAT 3: TAMPER FAIL (90 sec)

**Say:**

> Now the attacker story. An insider or compromised agent edits the receipt file to fake PASS. In legacy stacks, the dashboard still looks green. Here, validators are authority — projections are disposable.

**Executor runs:**

```bash
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
```

**Expect:** script reports `OK: tamper detected` after injecting bad checksum.

**Say:**

> Hand-edit receipt → checksum invalid → HARD FAIL. That is the anti-fake-velocity wedge.

---

### 3:30 — BEAT 4: Trace (30 sec, optional)

**Say:**

> Receipt links to spine. Spine links to rule P-001. One audit chain.

**Executor (optional):**

```bash
python3 -c "
import json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from governance_event_spine_v1 import find_by_event_id
r = json.loads(Path.home().joinpath('.sina/demo-enforcement/receipts/latest-demo-receipt.json').read_text())
eid = r.get('spine_event_id')
row = find_by_event_id(eid) if eid else None
print('receipt rule_id:', r.get('rule_id'))
print('spine event_id:', eid)
print('spine gate:', (row or {}).get('gate'))
"
```

---

### 4:00 — BEAT 5: Kill switch (30 sec)

**Say:**

> Organization-wide freeze is in the repository — not a slide. When we flag auto-run disabled, execution stops.

**Show (if file exists):**

```bash
test -f ~/.sina/auto-run-disabled-v1.flag && head -3 ~/.sina/auto-run-disabled-v1.flag
```

If absent: say *"Kill flag available — optional beat for factory lane."*

---

### 4:30 — BEAT 6: Disk truth (30 sec)

**Say:**

> We do not inflate velocity. Factory has hundreds of controlled tasks with receipts; unproven-done is zero. We would rather show RED than lie GREEN.

**Do not lead with 616/1000** — mention only if asked. Lead with live tamper FAIL.

---

### 5:00 — Close / Ask (30 sec)

**Say:**

> We are not selling an OS essay. We are selling enforceable AI execution for regulated buyers — Copilot governance for MSBs, procurement controls for enterprise. Next step: a 90-day pilot with exportable receipt bundle. Who owns agent governance in your stack?

**Ask:** LOI · paid sandbox · design partner (CAD ≥2K) — **W3**.

---

## Q&A cheat sheet

| Question | Answer |
|----------|--------|
| Is this production M365 integration? | No — governance proof path. Integration follows pilot. |
| How is this different from agent orchestrators? | We enforce **before** side effects; receipt + spine, not chat logs. |
| SOC2 / multi-tenant? | Roadmap post-pilot; kernel hardening is current phase. |
| What's the moat? | Validator-as-authority + honest metrics + regulated wedge. |
| Revenue? | TF/NF pilot track — first deposit is the milestone. |

---

## Files (demo path)

| Path | Role |
|------|------|
| `brain-os/demo/governance_demo_policy_v1.json` | Rule P-001 |
| `brain-os/demo/governance_demo_intents_v1.json` | BLOCK / ALLOW fixtures |
| `scripts/governance_demo_gate_v1.py` | Demo gate |
| `scripts/commit_intent_v1.py --demo-enforcement` | Commit entry |
| `scripts/sourcea_execute_v1.py --demo-enforcement` | Thin wrapper |
| `scripts/validate-demo-enforcement-v1.sh` | Tamper CI |
| `~/.sina/demo-enforcement/receipt-log.jsonl` | Append-only log |

---

## W3 (Commercial — parallel)

**Targets:** NF-001 Copilot governance · TF-001 MSB wedge  
**Minimum:** signed SOW or deposit CAD ≥2K by Dec 2026  
**Outreach kit:** `investor/ENFORCEMENT_OUTREACH_v1.md`
