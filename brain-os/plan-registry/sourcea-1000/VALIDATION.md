# SourceA 1000 — validation matrix

## Pack integrity

```bash
bash scripts/validate-sourcea-1000-pack.sh
# SOURCEA-1000 PACK VALID count=1000
```

## Tier verify gates

| Tier | Command |
|------|---------|
| T0 | `SINA_AUDIT_STRICT=1 build-sina-command-panel.py` + `find_critical_bugs.py` |
| T1 | `validate-eval-packet-v1b-live.sh` + `validate-governance-fleet-v1.sh` + `audit_hub_source_alignment.py` |
| T2 | `audit_backend_e2e.py` + `validate-spine-bridge-founder-v1.sh` |
| T3 | `find_critical_bugs.py` |

## Full hub verify (closeout)

```bash
bash scripts/plan-no-asf-run.sh verify-hub
```

## Success criteria (from v6 + synthesis)

| Milestone | Proof |
|-----------|-------|
| SSOT honest | `audit_hub_source_alignment.py` OK |
| No ASF verify | Scoreboard `auto_pass` / auto-green UI |
| Eval sustained | 5/5 live on strict build |
| UI complete | nudge banner + fleet gap + planner bridge |
| Fleet target | `auto_pass>=6` `nudges<=2` (lanes) |
| Spine loop | `spine.bridge` after founder Action |
