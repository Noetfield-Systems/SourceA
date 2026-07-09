# ACG Reconcile Plan (v1)

**Saved at:** 2026-07-05T12:45:00Z  
**Branch:** `commercial/acg-from-origin` (supersedes `preserve/acg-2026-07-05` for PR #18)

---

## Known state

| Field | Value |
|-------|-------|
| Local main HEAD | `f72703be3` |
| origin/main HEAD | `761353952` |
| Divergence | ahead 3 / behind 11 |
| ACG clean branch | `commercial/acg-from-origin` @ `f7f6181ae` |

---

## Safe sequence

1. `git fetch origin` (no merge)
2. `git log --oneline main..origin/main` and `origin/main..main`
3. `git diff --stat main...origin/main`
4. ~~Rebase preserve~~ **Done:** cherry-pick ACG commits onto `commercial/acg-from-origin` from `origin/main`
5. Open PR — PR #18 updated via force-with-lease push to `preserve/acg-2026-07-05`

## Status

- [x] fetch completed
- [x] cherry-pick ACG-only onto origin/main
- [x] PR #18 branch updated (clean, no unrelated main commits)
- [ ] CI green on updated PR
- [ ] founder merge approval

## Forbidden

Blind pull, force push to main, merge without reviewing 11 remote commits.
