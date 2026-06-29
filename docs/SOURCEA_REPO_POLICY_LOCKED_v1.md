# SourceA Repo Policy (LOCKED v1)

**Saved:** 2026-06-29T04:19:44Z  
**Machine policy:** `repo-policy.json`  
**Cursor rule:** `.cursor/rules/sourcea-repo-boundary.mdc`  
**Validator:** `scripts/check_sourcea_repo_policy.py`

---

## One Law

SourceA is the repo-local shared authority boundary. It holds SourceA-owned shared authority files, not active product operations owned elsewhere.

---

## SourceA Owns

- Kernel/eval machines
- Traceability
- Registries
- Reusable contracts
- Public API/cloud workers
- Versioned exports

---

## SourceA Must Not Store

- Active files owned by other product repositories
- Active files owned by other legal processes
- Active files owned by other entity processes

SourceA can expose shared contracts, exports, manifests, or public APIs for other repos/products to consume. This policy does not define those products; it only keeps active files owned elsewhere out of SourceA changes.

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
