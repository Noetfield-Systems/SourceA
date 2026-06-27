# Forge Core Governance — Python CLI

Wraps existing `scripts/forge_governance_kernel_v1.govern()` for the Production MVP worker.

```bash
echo '{"agent_id":"forge-worker-1","agent_role":"builder","action_type":"read_file","dry_run":true,"legal_review":false}' \
  | PYTHONPATH="$SOURCEA_ROOT/scripts" python3 apps/forge-core-governance/govern_cli.py
```

MVP defaults: `legal_review=false` (no civilization/geo arbitration on hot path), `dry_run=true` unless `FORGE_GOVERNANCE_DRY_RUN=0`.
