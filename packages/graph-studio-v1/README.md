# Graph Studio v1

NF-GRAPH-STUDIO-V1 — author / compile / observe layer over Executive Mesh.

**Law:** Studio authors Blueprints; Compiler freezes `plan_hash`; Mesh executes pinned plans; Verifier decides reality; React Flow is UI-only.

## Package

- `src/registry/` — Node Manifests (slice-1)
- `src/blueprints/` — semantic golden blueprint
- `src/compiler.ts` — validate + freeze hash
- `src/mesh-adapter.ts` — execute pinned plan via mesh ingest
- `src/run-graph.ts` — project mesh audit → node statuses

```bash
npm test
```
