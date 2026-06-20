# Root cleanup — manifest-first workflow

**Law:** Classify → relocate → purge caches only. **Never delete-first.** **Never move without an approved manifest.**

## Phase 0 — Before any git snapshot

1. Confirm `.gitignore` blocks `.env*`, `*.local`, `~/.sourcea-secrets` patterns
2. Run secret scan:

```bash
bash infra/cleanup/scan-secrets-v1.sh
```

Clear or redact hits before `git add`.

## Phase 1 — Inventory (read-only)

```bash
bash infra/cleanup/generate-inventory-v1.sh
```

Output: `infra/cleanup/inventory-root.tsv` (path · size · first line)

**Progress receipt:** `data/cleanup-track-progress-v1.json` — refresh with:

```bash
python3 scripts/cleanup_track_sync_v1.py --json
```

## Phase 2 — Manifest (human approves)

Agent writes **`cleanup-manifest.md`** only — one row per file:

| source | size | first_heading | proposed_dest | batch | action |
|--------|------|---------------|---------------|-------|--------|

**Actions:** `move` · `archive` · `keep-root` · `delete-cache-only`

Agent **must not execute moves** until ASF marks manifest `status: APPROVED`.

## Phase 3 — Execute in batches

```bash
bash infra/cleanup/execute-manifest-v1.sh --batch 1 --dry-run
bash infra/cleanup/execute-manifest-v1.sh --batch 1
git add -A && git commit -m "cleanup: batch 1 — brain-os law relocations"
```

One batch = one revertable commit. Wrong batch → `git revert HEAD`, not `reset --hard` on everything.

## Phase 4 — Safe purge only

Agent may **delete without manifest row** only:

- `__pycache__/`
- `.pytest_cache/`
- `.DS_Store`
- `*.pyc`

Everything else — especially `*.log` — **move to `archive/`**, never delete.

## Destination planes

| Proposed dest | Contents |
|---------------|----------|
| `brain-os/law/` | LOCKED governance SSOT |
| `docs/locked/` | Product/commercial LOCKED |
| `docs/archive/` | Superseded drafts |
| `archive/logs/` | Session logs, debug output |
| `archive/root-sprawl/` | Unclassified root files pending triage |
