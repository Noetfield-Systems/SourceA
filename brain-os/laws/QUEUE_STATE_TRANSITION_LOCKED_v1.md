# Queue State Transition (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Authority:** ASF  
**Mechanism:** `scripts/advance-healthy-queue-v1.py` · `scripts/healthy-drain-orchestrator-v1.py`

---

## One rule

```text
ONLY healthy-drain-orchestrator complete_if_ready() may call advance-healthy-queue-v1.py
```

After **WORKER_ROUND_REPORT** logged matches bound `expected_sa` + `expected_pos`.

---

## Who may NOT advance queue

| Engine | Rule |
|--------|------|
| API scout / API agent | **NEVER** |
| CLI prep (awake) | **NEVER** |
| CLI sleep ACT | **NEVER direct** — write report → orchestrator advances |
| Sidecars | **NEVER** |
| Manual `--set-pos` | **Reconcile only** (`reconcile-queue-from-registry-v1.py`) |

---

## Worker loop (Cursor)

```text
run inbox → execute → WORKER_ROUND_REPORT → orchestrator poll → advance + deliver
```

Founder does **not** advance manually.

---

## Sleep CLI loop

```text
orchestrator deliver → CLI run_turn → WORKER_ROUND_REPORT → orchestrator complete_if_ready → advance
```

CLI **never** calls `advance()` directly.

---

## Reconcile (not skip)

When pointer lags registry:

```text
python3 scripts/reconcile-queue-from-registry-v1.py
```

Infers first position whose `sa_id` is **not** `done` in REGISTRY.json. Writes audit line. Then `--set-pos` with reason `reconcile_registry`.

---

*LOCKED — execution without state transition = drift.*
