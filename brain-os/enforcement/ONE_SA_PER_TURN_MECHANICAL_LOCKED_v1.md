# One sa per turn — mechanical enforcement (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Law:** Claude audit 2026-06-07 — discipline gap closed logged  
**Canonical:** `os/chat-handoffs/ONE_SA_PER_TURN_MECHANICAL_LOCKED_v1.md`  
**Enforcer:** `scripts/one_sa_per_turn_gate_v1.py`

---

## 1. Problem

`one_sa_per_turn` was **law in markdown** only. Agents could still batch multiple `sa-XXXX` in one Composer turn. Honor system failed.

---

## 2. Mechanical gates (shipped)

| Layer | Enforcement |
|-------|-------------|
| **Turn state** | `~/.sina/worker_turn_state_v1.json` — `open` blocks second turn (`worker_turn_lib.turn_open_block`) |
| **Entry gate** | `cursor_entry_gate.py --role worker` — opens turn from **INBOX sa** (not live pick drift) |
| **Before agent** | `start_goal1_worker_turn_v1.py` → `guard_before_agent_turn()` — refuse if wrong open turn |
| **After agent** | `validate_agent_output()` — reject multiple `sa_focus` / multiple `WORKER_ROUND_REPORT` |
| **Broker** | `goal1_lane_broker.worker_submit` → `guard_broker_submit()` — reject batch before orchestrator advance |
| **Violations log** | `~/.sina/one-sa-violations-v1.jsonl` |

---

## 3. Reject conditions (automatic)

- `multiple_WORKER_ROUND_REPORT` (count > 1)
- `multiple_sa_focus` in one reply
- `sa_focus` ≠ INBOX `expected_sa`
- `registry_updated: [sa-A, sa-B]` with more than one id
- Turn open for `sa-A` while submitting report for `sa-B`

---

## 4. Agent wrapper (headless)

`start_goal1_worker_turn_v1.py` prompt includes:

```text
ONE SA ONLY THIS TURN: sa-XXXX — then STOP.
FORBIDDEN: batch multiple sa · second WORKER_ROUND_REPORT
```

---

## 5. Brain validation

`brain_validate_goal1_v1.py` includes `one_sa_per_turn:` block — Brain must show it in `BRAIN_VALIDATION_REPORT`.

---

## 6. Status check

```bash
python3 scripts/one_sa_per_turn_gate_v1.py --status --json
```

---

*End law*
