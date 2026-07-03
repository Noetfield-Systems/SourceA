# SourceA Copilot Instructions

SourceA is the repo-local authority boundary for shared contracts, public API/cloud workers, and versioned exports. Keep changes repo-local, policy-aligned, and tied to explicit tasks.

## Working rules

1. Operate only in `noetfield-systems/sourcea`.
2. Prefer atomic, lane-scoped changes and avoid unrelated rewrites.
3. Preserve snapshot/evidence/backlog artifacts; do not repurpose them as active config.
4. Run `python3 scripts/check_sourcea_repo_policy.py` when changes touch policy-governed surfaces.

## Machine process (no founder routing)

- **Copilot proposes PRs only** — Worker implements; merge requires Worker execution gate + L14/L16 validators green.
- Before Worker tasks: `python3 scripts/worker_execution_gate_v1.py --role worker --task "<summary>" --json`
- Unified validation: `bash scripts/validate-machine-process-v1.sh`
- Adversarial critique: `bash scripts/adversarial_critique_gate_v1.sh` (duplicate impl scan + conflict matrix)
- SSOT: `data/machine-process-loops-v1.json` · retirement: `data/founder-trigger-retirement-registry-v1.json`

## Active-config guardrails

- **Forbidden active-config marker:** `kazemnezhadsina144[-]dot`
- Do not introduce or retain the forbidden marker (see `docs/FORBIDDEN_MARKERS.txt`) in active configuration, code defaults, or runtime wiring.
- Use `noetfield-systems/sourcea` for SourceA repo identity in active surfaces.
