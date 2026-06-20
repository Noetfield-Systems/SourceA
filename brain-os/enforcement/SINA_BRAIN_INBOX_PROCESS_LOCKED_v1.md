# Sina Brain — INBOX process (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-09  
**Authority:** ASF — permanent process, not one-off hand checks  
**Parent:** `MONITOR_HONESTY_LOCKED_v1.md` · `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` · `REGISTRY_DRAIN_RAIL_LOCKED_v1.md`

---

## §0 — Two lanes (never cross)

| Lane | Chat | May implement? | May close REGISTRY? |
|------|------|----------------|---------------------|
| **Brain** | SourceA Brain / meta | **No** | **No** |
| **Worker** | SourceA Worker 1 / 2 | **Yes** (one role) | **Only VERIFY + receipt** |

**Brain hijack = INCIDENT.** Hub writes `.sina-loop/INBOX.md` — Worker executes; Brain reads status only.

---

## §1 — Brain before every progress reply (mechanical)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash enforce-registry-hygiene-v1.sh
python3 brain_validate_goal1_v1.py --json
```

**Quote only:**

| Metric | Source |
|--------|--------|
| **Valid YES** | `validate-monitor-honesty-v1` / brain_validate `progress.valid_yes` |
| **Receipts** | `audit_registry_done.honest_done` |
| **PARTIAL** | broker gap count when receipts > Valid YES |

**Forbidden:** quote receipt count as progress % · quote ~~607~~ · narrate done without running hygiene script.

---

## §2 — Worker INBOX law (every turn — same forever)

```
Hub/autoloop → INBOX.md (one role) → Worker RUN INBOX → CHECK | ACT | VERIFY → broker worker-submit → STOP
```

| Role | Worker does | Worker must NOT |
|------|-------------|-----------------|
| **CHECK** | Read prompt; run validators; gap report | Implement; closeout |
| **ACT** | Minimal fix for CHECK gap | VERIFY; closeout |
| **VERIFY** | Run verify commands; receipt; closeout | Implement new scope |

**One INBOX turn = one role = one sa.** Broker rejects batch (`ONE_SA_PER_TURN_MECHANICAL_LOCKED_v1.md`).

---

## §3 — Honest closeout recipe (VERIFY only)

1. Machine validators PASS (`critical_bugs: 0`)
2. `receipts/sa-XXXX-receipt.json` written (`worker_receipt_v1` — VERIFY only)
3. `closeout_sa_task.py` / broker auto-closeout when `orchestrator.expected_role=verify`
4. REGISTRY `done` — **never** direct edit

**Gates (CRITICAL on every build):** `validate-registry-honest-gate-v1` · `validate-closeout-gate-v1` · `validate-monitor-honesty-v1`

---

## §4 — Brain routing words (required)

When founder asks “what next?”:

> **Hub → Goal 1 loop → EXECUTE TURN** (Worker chat — not Brain)

When founder pastes Worker report in Brain:

> **Acknowledge + verify disk** (`enforce-registry-hygiene-v1.sh`) — **do not re-implement ACT** in Brain.

When Worker 2 finished ACT and INBOX says VERIFY:

> **Worker lane runs VERIFY** — Brain does not patch `system_roadmap.py` in Brain chat.

---

## §5 — Auto-hygiene (same every time)

`enforce-registry-hygiene-v1.sh` runs:

1. Honest gate (revert unproven done)
2. Quarantine BLOCKED receipts (`quarantine-blocked-receipts-v1.py`)
3. Quarantine stale batch YAML beside honest receipts
4. Repair broker audit gaps from receipts (`repair-broker-gaps-from-receipt-v1.py`)
5. Monitor honesty gate

Founder: **Actions → Enforce honest REGISTRY** (same script).

---

## §6 — Forbidden forever (INCIDENT-006)

- Batch `pack30 verify-only` closeouts
- YAML-only proof
- Brain implements sa-XXXX ACT/VERIFY
- Skip VERIFY after ACT
- Multiple roles in one Worker turn

---

## §7 — Success metrics

| Use for | Metric |
|---------|--------|
| Founder progress bar | **Valid YES / 1000** |
| Audit trail | **honest_done receipts** |
| Factory health | **critical_bugs = 0** |
| Next work | **INBOX role + sa + queue pos** |
