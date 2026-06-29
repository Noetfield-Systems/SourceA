# SourceA Agent Policy

## Repo Boundary

SourceA is the repo-local shared authority boundary for kernel/eval machines, traceability, registries, reusable contracts, public API/cloud workers, and versioned exports.

SourceA must not store active files owned by other repos, products, legal processes, or entity processes. Cross-product dependencies must use contracts, exports, manifests, or public API/cloud workers, not SourceA internal scripts.

Before new work, run `git status --short`, confirm the tree state, state the target lane, state files to touch, and avoid ignored/generated/evidence/archive payload context unless explicitly assigned. Work lane-by-lane, keep each pass to 20-40 files, and make one atomic commit per coherent lane.

Generated, evidence, and backlog outputs must be preserved as snapshot + manifest artifacts, not loose repo dirt.

Machine policy: `repo-policy.json`  
Validator: `python3 scripts/check_sourcea_repo_policy.py`
