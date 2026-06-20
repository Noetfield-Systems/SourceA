# K1 loader hook architecture v1

**Date:** 2026-06-15  
**Resolves:** Graphify god-node report vs Claude read-path analysis

## Verdict

**Claude is right.** Hook K1 at **loaders**, not at `build_payload()`.

| Metric | `build_payload()` | `load_healthy_queue()` / `load_factory_now()` |
|--------|-------------------|-----------------------------------------------|
| Graphify rank | #1 (108 edges) | #5–#6 (42 edges each) |
| Role | Hub **projection aggregator** | **Receipt/state read choke** |
| K1 belongs here? | No — downstream consumer | **Yes — every read path passes through** |

108 edges = 108 callers of `build_payload()`. That is fan-in to the hub UI, not 108 receipt reads. `build_payload()` calls `load_json()` on many paths and imports `load_factory_now` / `healthy_queue_status` — it reads **through** the loaders.

## Loader hooks (disk)

| Loader | Script | K1 hook |
|--------|--------|---------|
| Queue SSOT | `healthy_queue_ssot_lib.load_healthy_queue()` | `k1_after_queue_read()` · phase_strict alignment |
| Factory state | `factory_control_v1.load_factory_now()` | Stale `factory-now-v1.json` → rebuild; `_k1_stale` flag |
| Active now | `active_now_v1.load_active_now()` | `active_now_file_fresh()` · `stale` / `fresh` on row |
| Overnight gate | `overnight_one_step_v1.is_overnight()` | Returns `False` when `active_now.stale` |

## Defense in depth

- **Loaders** — tamper + freshness at read (canonical)
- **`kernel_k1_payload()`** — hub Safety glance (critic_boot + tamper validator)
- **`build_payload()`** — freeze signature; heavy tests; do not refactor for edge-count

## critic_boot “self-import cycle”

Graphify reports `critic_boot_v1.py → critic_boot_v1.py`. This is a **static-analysis false positive** — subprocess / string references to `scripts/critic_boot_v1.py` in the same file (AEG terminal capture). Not a Python import cycle. `sourcea-boot` package does **not** import `critic_boot_v1.py` — portable checks only.

## Strict mode

```bash
K1_READ_STRICT=1 python3 scripts/advance-healthy-queue-v1.py
```

Fails closed when phase_strict queue head diverges from disk truth.

## Related

- `scripts/k1_read_gate_v1.py`
- `scripts/validate-enforcement-kernel-v1.sh`
- `demo/governance/AEG_PIPELINE_v1.md`
