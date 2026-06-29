# SourceA Repo Policy (LOCKED v1)

**Saved:** 2026-06-29T04:19:44Z  
**Machine policy:** `repo-policy.json`  
**Cursor rule:** `.cursor/rules/sourcea-repo-boundary.mdc`  
**Validator:** `scripts/check_sourcea_repo_policy.py`

---

## One Law

SourceA is the upstream authority engine. It owns the shared authority layer for the portfolio, not active product operations.

---

## SourceA Owns

- Kernel/eval machines
- Traceability
- Registries
- Reusable contracts
- Public API/cloud workers
- Versioned exports

---

## SourceA Does Not Own

- Active Noetfield product files
- Active TrustField product files
- Legal matter files
- Entity operations files

Noetfield and TrustField must carry their own process and config ownership. SourceA can expose shared contracts, exports, manifests, or public APIs for those products to consume.

---

## Working Rule

Before new SourceA work:

1. Run `git status --short`.
2. Confirm the clean tree or name the assigned dirty lane.
3. State the target lane.
4. State files to touch.
5. Avoid ignored/generated/evidence/archive payload, `dist`, `node_modules`, SQLite/db, and queue dump context unless explicitly assigned.

Each pass stays lane-by-lane, touches at most 20-40 files, and lands as one atomic commit per coherent lane.

Generated, evidence, and backlog outputs must be preserved through snapshot + manifest artifacts, not loose repo dirt.

---

## Dependency Rule

Cross-product dependencies must use:

- Contracts
- Exports
- Manifests
- Public API/cloud workers

Cross-product dependencies must not use:

- SourceA internal scripts as product runtime dependencies
- Private runtime directories
- Loose copied generated outputs
- Active product implementation files

---

## Validation

```bash
python3 -m json.tool repo-policy.json
python3 scripts/check_sourcea_repo_policy.py
git diff --check
```

Before closeout after commit:

```bash
python3 scripts/check_sourcea_repo_policy.py --clean-tree
git status --short
```
