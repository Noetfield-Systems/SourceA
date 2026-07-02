# Deploy dirty-tree scope map (founder-reviewable)

**UTC saved:** 2026-07-02T06:45:00Z  
**Machine:** `scripts/deploy_dirty_tree_guard_v1.py` · cap `dirty_total > 200` fails every scope

## Law

Scoped deploy guards pass only when **both**:

1. No dirty files under the scope prefix list for that deploy lane
2. `dirty_total <= 200` repo-wide (forces triage before entropy becomes permanent)

## Scopes

| Scope | Prefixes | Use |
|-------|----------|-----|
| `landing` | `SourceA-landing/green-unified/`, buyer-proof inject/publish/verify scripts | Cloudflare Pages buyer surfaces |
| `fbe` | `cloud/Dockerfile.fbe-runner`, `cloud/railway.toml`, active batch JSON, FBE deploy/generate scripts | Railway Cloud Forge Run |
| `intake` | `cloud/workers/sourcea-mvp-intake-v1/`, `scripts/verify_mvp_intake_proof_v1.py` | MVP intake worker |
| `mac_dispatch` | `scripts/fbe/lib/mac_control_dispatch_v1.py`, `scripts/mac_cloud_deploy_dispatch_v1.py`, `scripts/validate-mac-control-dispatch-v1.sh`, `scripts/launchd-wrappers/`, `launch/com.sourcea.*.plist` | Mac control dispatch + TCC-safe launchd |

## Check

```bash
python3 scripts/deploy_dirty_tree_guard_v1.py --scope landing --json
python3 scripts/deploy_dirty_tree_guard_v1.py --scope fbe --json
python3 scripts/deploy_dirty_tree_guard_v1.py --scope intake --json
```

Unrelated dirty files outside scope prefixes are allowed **only** while `dirty_total <= 200`.
