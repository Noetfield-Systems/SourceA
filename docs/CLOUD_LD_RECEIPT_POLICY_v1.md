# CLOUD-LD receipt policy

**Saved:** 2026-06-21T12:00:00Z

LaunchDarkly  drain receipts (`CLOUD-LD-001` … `CLOUD-LD-010`) live under `receipts/cloud-dispatch/`.

## Newest `at` wins

When multiple JSON files share the same `plan_id`, validators and humans treat the row with the **latest** `at` timestamp as authoritative. Older duplicates are archive noise — not failures.

Machine enforcement: [`scripts/validate-cloud-ld-drain-archive-v1.sh`](../../scripts/validate-cloud-ld-drain-archive-v1.sh).

## Archive vs live

| Script | When | Network |
|--------|------|---------|
| `validate-cloud-ld-drain-archive-v1.sh` | Mac-light / ship | No — disk only |
| `validate-cloud-ld-drain-live-v1.sh` | Cloud-CI | Yes — one fetch for CLOUD-LD-001 |

Set `CLOUD_LD_LIVE=0` to skip the live fetch in CI.

## Optional cleanup

Duplicate dispatch JSON may be moved to `archive/logs/` during manifest-gated cleanup — never delete without [`infra/cleanup/cleanup-manifest.md`](cleanup-manifest.md) approval.
