# L0 Repo Graph Memory v1 — SourceA

**Status:** ACTIVE — rolled out from the `sina-governance-SSOT` pilot
(`docs/GRAPH_TOOL_DECISION_v1.md` there records why a custom stdlib-only script
was chosen over Graphiti and Graphify: no deploy, no database, no LLM calls, no
network — the opposite of a token-cost sink).

## Why SourceA needs it

SourceA is large: **~28k files across 47 top-level subsystems**, dominated by
`brain-os` (~19.6k files) and Markdown (~21.8k `.md`). A blind "understand the
repo" or multi-agent reader pass over that is prohibitively expensive and breaks
the lane discipline in `AGENTS.md`. This layer gives agents a compact, static
subsystem + file + reference map to query **before** opening files.

## Pieces

| Piece | Path |
|---|---|
| Graph builder | `scripts/build_repo_graph_v1.py` |
| Graph query | `scripts/query_repo_graph_v1.py` |
| Compact report (committed, read this first) | `graph-out/GRAPH_REPORT.md` |
| Full index (gitignored local cache, ~20MB) | `graph-out/graph_index_v1.json` |
| Verifier | `scripts/verify_l0_repo_graph_memory_v1.sh` |
| Broad-read gate | `AGENTS.md` (§ "L0 repo graph memory — broad-read gate") |

## Commands

```
python3 scripts/build_repo_graph_v1.py                 # build/refresh (~5s, zero-token)
python3 scripts/query_repo_graph_v1.py <subsystem|keyword>
python3 scripts/query_repo_graph_v1.py --stats
bash scripts/verify_l0_repo_graph_memory_v1.sh         # PASS/FAIL receipt in receipts/
```

## SourceA-specific tuning (vs the SG pilot)

1. **`SUBSYSTEM_DIRS`** lists all 47 SourceA top-level dirs (the builder only walks
   listed subsystems; unlisted top-level dirs are skipped entirely).
2. **Symlink-hardened.** The builder skips symlinks and survives unreadable paths —
   SourceA contains broken shims (e.g. a `.bin/ffmpeg` symlink) that crash a naive
   `stat()` walk. `iter_files`/`file_record` now guard against this.
3. **Index is gitignored.** At ~20MB the full index is a local cache, rebuilt on
   demand in ~5s; only the ~15KB `GRAPH_REPORT.md` is committed. (In the smaller SG
   repo the index is small enough to commit; here it is not.)
4. **Verifier keyword check** uses `README` (present repo-wide) instead of SG's
   `founder_canon`.

## Maintenance

Point-in-time snapshot (`generated_at` in both outputs). Rebuild after adding a
subsystem or a large batch of files. Since the index is gitignored, always rebuild
once after a fresh clone before querying.

## Possible next improvement (not done)

Edges are currently best-effort path-string references (same as the SG pilot). For
SourceA's real code (`brain-os`, `scripts`, `apps` — Python/JS/TS), adding
`ast`-based Python import parsing and a JS/TS import regex would produce a truer
call/import graph. Deferred; revisit if path-string edges prove too noisy for a
real routing task.
