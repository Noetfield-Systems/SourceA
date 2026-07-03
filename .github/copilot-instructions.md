# SourceA Copilot Instructions

SourceA is the repo-local authority boundary for shared contracts, public API/cloud workers, and versioned exports. Keep changes repo-local, policy-aligned, and tied to explicit tasks.

## Working rules

1. Operate only in `noetfield-systems/sourcea`.
2. Prefer atomic, lane-scoped changes and avoid unrelated rewrites.
3. Preserve snapshot/evidence/backlog artifacts; do not repurpose them as active config.
4. Run `python3 scripts/check_sourcea_repo_policy.py` when changes touch policy-controlled surfaces.

## Active-config guardrails

- **Forbidden active-config marker:** `kazemnezhadsina144[-]dot`
- Do not introduce or retain the forbidden marker (see `docs/FORBIDDEN_MARKERS.txt`) in active configuration, code defaults, or runtime wiring.
- Use `noetfield-systems/sourcea` for SourceA repo identity in active surfaces.
