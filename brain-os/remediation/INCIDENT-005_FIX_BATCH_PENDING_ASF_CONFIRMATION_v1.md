# INCIDENT-005 Fix Batch — PENDING ASF CONFIRMATION

**sequence_id:** SA-2026-06-08-INCIDENT-005-BATCH  
**Status:** **NOT EXECUTED** — awaiting founder `ASF: confirm INCIDENT-005 batch`  
**Hard constraint (founder 2026-06-08):** **No edits to existing `*_LOCKED_v*.md` law files** until explicit confirmation.

---

## What this batch fixes (procedure + drift — not new law)

| Step | Action | Touches locked rules? | Risk |
|------|--------|----------------------|------|
| B1 | Archive `brain-os/EXECUTION_SESSION_LOCK_2026-06-08_v1.md` → `archive/superseded/EXECUTION_SESSION_LOCK_2026-06-08_SUPERSEDED_BY_INCIDENT-004_v1.md` with banner | **No** — session doc only | Low |
| B2 | Sync repo `healthy-queue-30-active.json` **from** `~/.sina` boss pack (copy + regen metadata) | **No** — data | Medium — verify sa-0153 ACT |
| B3 | Update `ACTIVE_NOW.md` blocker line after B2 (clear broker drift or state remaining gap) | **No** — scoreboard | Low |
| B4 | Add `scripts/validate-external-critic-reply-v1.sh` — checks maintainer closeout / sample reply has `INPUT CLASS: EXTERNAL_CRITIC` when `external_paste=true` flag set | **No** — new validator | Low |
| B5 | Add `scripts/incident_005_probation_gate_v1.py` — prints probation reminder + required §6 skeleton for paste turns | **No** — helper | Low |
| B6 | Register batch in `SOURCEA-PRIORITY.md` evidence row (one line) | **No** — ledger | Low |
| B7 | Private reference: `~/.sina/agent-workspaces/sinaai_maintainer/private-reference/audits/INCIDENT-005_MAINTAINER_PROCEDURE_2026-06-08.md` | **No** | Low |

---

## Explicitly OUT OF SCOPE until separate ASF order

| Item | Why deferred |
|------|--------------|
| Edit `MANDATORY_READ_BY_ROLE_LOCKED_v1.md` to add INCIDENT-005 | Locked rule — needs ASF yes |
| Edit `cursor_entry_gate.py` hash chain | Locked entry — needs ASF yes |
| New `*_LOCKED_v*.md` law for probation | Founder said no rule edits before confirm |
| Hub Action “Gatekeeper check” ship | Hub UI — confirm in second batch if wanted |
| Receipt schema enforcement on all closeouts | D6 — larger scope |

---

## Execution order (when ASF confirms)

```text
1. gatekeeper_v1.py          → must PASS before B2
2. B1 archive session lock   → remove ROA commercial drift doc from active path
3. B2 queue sync             → ~/.sina wins (healthy_queue_ssot_lib policy)
4. gatekeeper_v1.py          → must PASS after B2
5. B3 ACTIVE_NOW             → founder_busy · sa-0153 · single queue path
6. B4–B5 validators/helpers  → prevent repeat
7. B6–B7 ledger + private audit
8. validate-founder-busy-operating-model-v1.sh
9. validate-gatekeeper-v1.sh
10. validate-goal-hierarchy-enforce-v1.sh
```

---

## Rollback

| Step | Rollback |
|------|----------|
| B1 | Restore session lock from archive path |
| B2 | Restore repo queue from git or `archive/` snapshot taken pre-sync |
| B3 | Revert ACTIVE_NOW from git |
| B4–B5 | Delete new scripts only |

Pre-sync snapshot (executor runs before B2):

```bash
cp ~/.sina/healthy-queue-30-active.json ~/.sina/healthy-queue-30-active.json.bak-incident-005
cp brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json \
   archive/superseded/healthy-queue-30-active.repo.pre-incident-005.json
```

---

## Acceptance criteria

- [ ] Single boss queue: `~/.sina` and repo pack **same sa_range** (`sa-0153`–`sa-0166`)
- [ ] `EXECUTION_SESSION_LOCK` no longer in active `brain-os/` root (archived + superseded banner)
- [ ] `gatekeeper_v1.py` → PASS
- [ ] `ACTIVE_NOW.md` blocker accurate (not stale “drift” if reconciled)
- [ ] No `*_LOCKED_v*.md` files modified in this batch
- [ ] Validator B4 exists and fails on missing `INPUT CLASS` in test fixture

---

## ASF confirmation phrases (any one unlocks batch)

- `ASF: confirm INCIDENT-005 batch`
- `ASF: run incident 005 fix batch — no rule edits`
- `ASF: sync queue + archive session lock`

---

*Pending — do not execute until founder confirms.*
