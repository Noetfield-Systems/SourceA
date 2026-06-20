# Maintainer CHECK — RT LIVE wall time vs Q-RT-LIVE YES repair-only gate

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**At:** 2026-06-11T22:01Z · **Role:** Maintainer CHECK · **No code diff · no new D-modules**

## Form law (Q-RT-LIVE YES)

| Pick | Ruling |
|------|--------|
| **Q-RT-LIVE YES** | Hub **repair-only** until RT LIVE proven · no Cursor AUTO-RUN · no auto-prompt |
| **Q-1.10 DEFER** | Seal Phase 1 after hub RT LIVE wired |
| **Q-NEXT-WORK 10.10 D** | Pause Phases 3–10 until RT LIVE · then playbook |
| **Q-GRADE C** | Spine green · hub not RT LIVE yet (form fill time) |

**Machine gate:** `scripts/rt_live_gate_v1.py` · receipt `~/.sina/rt-live-gate-receipt-v1.json`

**Thresholds (code):**

| Metric | Pass ceiling |
|--------|----------------|
| `hub_sync_wall_ms` | **≤ 3000 ms** (3 s) |
| `cascade_wall_ms` (light cascade) | **≤ 45000 ms** (45 s) |

**Not measured by gate:** full `hub_self_refresh_v1.py` bundle (align + AS-01 + shell heal + validators).

---

## Measurements (this session)

| Path | Wall time | Gate | Notes |
|------|-----------|------|-------|
| `GET /api/hub-sync` (curl) | **750 ms** | PASS (< 3 s) | RT path only |
| `rt_live_gate_v1.py --prove` hub_sync | **418 ms** | PASS | Same endpoint |
| `governance_propagation_cascade_v1.py` (light) | **16.5 s** | PASS (< 45 s) | `real` from `/usr/bin/time` |
| `rt_live_gate_v1.py --prove` cascade | **16.4 s** | PASS | Steps sum ≈ 16.4 s |
| `align_command_data_ui_v1.py` alone | **7.7 s** | N/A | **FAIL** P0 pick drift `live='sa-0798'` |
| `hub_self_refresh_v1.py` (light, no `--full`) | **31.2 s** | N/A | Heavier repair bundle; `align_ui` FAIL |

### Cascade step breakdown (light, 2026-06-11T22:01Z)

| Step | ms | ok |
|------|-----|-----|
| `monitor_live_sync` | 480 | true |
| `brain_sync_if_changed` | 8169 | true |
| `hub_projection` (`align_command_data_ui_v1.py`) | 7582 | true* |
| `run_inbox_truth` | 266 | true |
| `completion_backlog` | 8 | true |

\* Step marked `ok: true` in cascade receipt even though `align` **returncode 1** (P0 pick drift) — cascade does not fail on align RC today.

### RT LIVE receipt (refreshed)

```json
{
  "gate": "PASS",
  "hub_sync_wall_ms": 418,
  "cascade_wall_ms": 16382,
  "hub_sync_pass_ms": 3000,
  "cascade_pass_ms": 45000
}
```

Path: `~/.sina/rt-live-gate-receipt-v1.json` · `proved_at: 2026-06-11T22:01:10Z`

---

## Verdict vs Q-RT-LIVE YES

| Question | Answer |
|----------|--------|
| Hub-sync in **seconds**? | **YES** — sub-second (~0.4–0.75 s) |
| Light cascade in **seconds not minutes**? | **YES** — ~16 s (under 45 s gate; not sub-10 s) |
| RT LIVE gate **PASS** on disk today? | **YES** — receipt `gate: PASS` |
| `hub_self_refresh` = RT LIVE metric? | **NO** — 31 s repair bundle; includes validators + shell heal + brain sync beyond gate probe |
| Repair-only satisfied? | **PARTIAL** — gate PASS; **align P0 pick drift** still FAIL (projection lag `sa-0798`) |

**Colloquial “seconds” (founder P0 copy):** hub-sync meets bar; cascade is seconds-tier (~16 s) not minutes-tier (~60–360 s full panel). Official gate allows cascade up to **45 s**.

**Out of scope (no D-modules):** tightening cascade to <10 s; wiring align RC into cascade `ok`; fixing P0 pick drift (Maintainer hub repair, not Worker).

---

## Maintainer P0 after this CHECK

1. **FR-003** wiring (form Q-CRITIC YES) — next per receipt `maintainer_p0_next`
2. **P0 pick drift** — reconcile `align_command_data_ui_v1` live pick vs factory-now (INCIDENT-027 projection class)
3. **Phase 1.10 seal** — after FR-003 + drift clean per Q-1.10 DEFER
4. Factory / `sa-XXXX` drain — **background only** per Q-RT-LIVE YES

## References

- `scripts/rt_live_gate_v1.py` · `scripts/governance_propagation_cascade_v1.py` · `scripts/hub_self_refresh_v1.py`
- `~/.sina/live-founder-decision-form-v2-answers.json`
- `SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md` §5 (propagation ladder)
- `brain-os/incidents/SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md`
