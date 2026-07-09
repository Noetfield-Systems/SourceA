# SourceA Agent Policy

## Repo Boundary

SourceA is the repo-local shared authority boundary for kernel/eval machines, traceability, registries, reusable contracts, public API/cloud workers, and versioned exports.

SourceA must not store active files owned by other repos, products, legal processes, or entity processes. Cross-product dependencies must use contracts, exports, manifests, or public API/cloud workers, not SourceA internal scripts.

Before new work, run `git status --short`, confirm the tree state, state the target lane, state files to touch, and avoid ignored/generated/evidence/archive payload context unless explicitly assigned. Work lane-by-lane, keep each pass to 20-40 files, and make one atomic commit per coherent lane.

Generated, evidence, and backlog outputs must be preserved as snapshot + manifest artifacts, not loose repo dirt.

Machine policy: `repo-policy.json`  
Validator: `python3 scripts/check_sourcea_repo_policy.py`

## L0 repo graph memory — broad-read gate

**Read before broad reads:** `graph-out/GRAPH_REPORT.md` · query: `python3 scripts/query_repo_graph_v1.py <term>` · design: `docs/L0_REPO_GRAPH_MEMORY_v1.md`

Do not spawn a broad "understand the repo", "map subsystem X", "architecture
review", or "audit Y" task (multi-agent or single-agent) by reading files
directly as the first step. SourceA is large (~28k files, 47 subsystems;
`brain-os` alone is ~19.6k files) — a blind repo-wide read is prohibitively
expensive and violates the lane discipline above. First read
`graph-out/GRAPH_REPORT.md` (compact subsystem map, ~15KB) and, for anything it
doesn't answer, run `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`
(bounded output, no full file reads). Only open — or delegate reading of — the
specific files the graph names as relevant. Token budget: orientation (the report
plus a few targeted queries) should cost a few thousand tokens, not the hundreds
of thousands a blind multi-agent understand pass costs. The full index is a local
cache (gitignored, ~20MB); if it is missing or stale, rebuild first with
`python3 scripts/build_repo_graph_v1.py` (~5s, zero-token) rather than falling
back to a blind read. Verify wiring: `bash scripts/verify_l0_repo_graph_memory_v1.sh`.
