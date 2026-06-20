# sa-0889 — H2 weekly machine receipt bundle cadence integration-fabric T3 cross-ref (LOCKED v1)

**Saved:** 2026-06-17T11:23:48Z · **Version:** 1.0.0 · **Authority:** Worker ACT sa-0889  
**Date:** 2026-06-17 · **SA:** sa-0889 (T3) · **Canonical:** sa-0814 (T0) · **T1 echo:** sa-0839 · **T2 echo:** sa-0864

## Contract

T3 research spike — no re-research. Verification:

| Layer | Artifact |
|-------|----------|
| Canonical | sa-0814 · `scripts/validate-h2-weekly-receipt-bundle-cadence-v1.sh` |
| T1 echo | sa-0839 · `scripts/validate-h2-weekly-receipt-bundle-cadence-t1-crossref-v1.sh` |
| T2 echo | sa-0864 · `scripts/validate-h2-weekly-receipt-bundle-cadence-t2-crossref-v1.sh` |
| T3 echo | sa-0889 · `scripts/validate-h2-weekly-receipt-bundle-cadence-t3-crossref-v1.sh` |
| Receipt | `receipts/sa-0814-receipt.json` DONE |
| Fabric | `~/.sina/integration-fabric-registry-v1.yaml` · `build_cadence_schedule.weekly` · `h2-machine-bundle` |
| Bundle | `scripts/machine_hub_bundle_v1.py` · `schedule: weekly` · cron `0 8 * * 1` |
| Bundle receipt | `~/.sina/h2-machine-weekly-bundle-receipt-v1.json` |

## Integration-fabric cadence (weekly H2 machine receipt bundle)

```yaml
# ~/.sina/integration-fabric-registry-v1.yaml (excerpt)
build_cadence_schedule:
  weekly:
    - id: h2-machine-bundle
      hub: H2
      schedule: weekly
      cron: "0 8 * * 1"
      cli: python3 ~/Desktop/SourceA/scripts/machine_hub_bundle_v1.py --json --reason weekly
      steps:
        - h2_pending_registry_reconcile_v1.py
        - hub_dual_heal_v1.py
        - validate-machine-hub-v1.sh
        - hub_surface_v1.py
      receipt: ~/.sina/h2-machine-weekly-bundle-receipt-v1.json
      validator: validate-h2-weekly-receipt-bundle-cadence-v1.sh
      forbidden_on: [h1-light-refresh, worker_turn, founder_daily_tap, build-sina-command-panel]
```

**Law:** tier dedup only — cites canonical sa-0814 · runs validate-h2-weekly-receipt-bundle-cadence-v1.sh · no panel rebuild · not on H1 daily refresh.
