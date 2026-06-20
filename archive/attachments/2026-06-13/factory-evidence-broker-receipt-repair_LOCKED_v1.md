# Factory evidence repair — broker receipts backfill (2026-06-13)

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Trigger:** Founder audit — REGISTRY `done` without `receipts/sa-XXXX-receipt.json` (fake-green class INCIDENT-006/007).

## CHECK findings

| Signal | Before | After |
|--------|--------|-------|
| `done_without_full_proof` | 8+ rows (0799–0856, 0798 REGISTRY drift) | **0** |
| STALE broker | unknown | **0** |
| dual_proof | brain 616 vs live 624 GAP | **624/624 OK** |
| Queue head | sa-0798 (already done) | **sa-0951 check** |
| sa-0851 | ACT only, backlog | **done + receipt** |

## FIX applied

1. **Receipts backfill** — `receipts/sa-0798` … `sa-0856-receipt.json` from verify YAML evidence (`source: worker_inbox`)
2. **Broker audit trail** — `repair-broker-gaps-from-receipt-v1.py` appended CHECK/ACT/VERIFY events (`repair: true`)
3. **sa-0798 REGISTRY** — aligned `backlog` → `done` (verify YAML existed; REGISTRY was stale)
4. **Brain sync** — `brain_sync_lib_v1.py` light → dual_proof True
5. **Queue advance** — past sa-0798 full slice → pos 4 (sa-0951 check)
6. **sa-0851 VERIFY** — closed with receipt + broker + PRIORITY row

## Honest limits

- Backfill events are **`repair: true`** — not live per-turn `goal1_lane_broker worker-submit`
- Going forward: every VERIFY must ship **RECIPE · VALIDATION · EVIDENCE · BUILT** + live broker submit

*End repair receipt*
