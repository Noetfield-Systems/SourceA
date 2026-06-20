# Phase-strict run inbox routing (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
status: LOCKED
doc_date: 2026-06-10
sequence_id: SA-2026-06-10-PHASE-STRICT-RUN-INBOX
-->

| | |
|--|--|
| **Version** | `SOURCEA-PHASE-STRICT-RUN-INBOX-1.0-LOCKED` |
| **Trigger** | Founder says **`run inbox`** in SourceA Worker chat |
| **Machine SSOT** | `~/.sina/phase-strict-drain-v1.json` |
| **Queue builder** | `~/.sina/build-phase-strict-queue-v1.py` |
| **Activator** | `~/.sina/activate-run-inbox-phase-strict-v1.py` |

---

## Law

When **`run inbox`** and phase-strict is **enabled**, the Worker lane drains **only** this order:

1. **s1-OR-P1** — OpenRouter activation (`sa-0101` … `sa-0115` unique pack — **live eval allowed on ACT**)
2. **s7 tail** — `sa-0798` … `sa-0800`
3. **s9** — achievable (`sa-0951` … `sa-1000` minus blocked SAs)

**Skip:** s2, s3 (100% done). **s8 hub-ui-ux:** SKIPPED — Super Fast Hub archive-only. **Not in headless queue:** s4, s5, s6 founder lanes.

**OpenRouter law:** `SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md`

One turn per `run inbox` · CHECK → ACT → VERIFY per `sa` · broker advance after STOP.

---

## Worker agent on `run inbox`

1. Run `python3 ~/.sina/activate-run-inbox-phase-strict-v1.py` (builds queue if needed, delivers current turn to INBOX).
2. Run `python3 scripts/goal1_lane_broker.py pickup`.
3. Execute one turn · `WORKER_ROUND_REPORT` · `goal1_lane_broker.py worker-submit --stdin`.

Do **not** rebuild queue from `build-achievable-healthy-queue.py` lazy pick while phase-strict is enabled.

---

## Packs (manifest)

| Pack | SAs | Phase |
|------|-----|-------|
| s7-P1 | sa-0778 … sa-0787 | s7 |
| s7-P2 | sa-0788 … sa-0797 | s7 |
| s7-P3 | sa-0798 … sa-0800 | s7 |
| s9-P1 … s9-P5 | 46 achievable in sa-0951 … sa-1000 | s9 |

**Removed from Worker queue (2026-06-13):** s8-P1 … s8-P5 (hub-ui-ux) — Super Fast Hub law.

Manifest dir: `~/.sina/pack-manifests/`

---

## Related

- `SOURCEA_PHASE_PACK_PINNED_SUMMARY_LOCKED_v1.md`
- `brain-os/incidents/SINA_HEALTHY_QUEUE_PHASE_ORDER_DRIFT_INCIDENT_017_LOCKED_v1.md`
