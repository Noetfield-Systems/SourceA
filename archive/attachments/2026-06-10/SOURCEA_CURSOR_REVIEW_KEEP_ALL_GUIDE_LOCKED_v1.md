> **ARCHIVE ONLY — not canonical law.** Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

# SourceA — Cursor Review “51 Pending Changes” — Keep All guide

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Date:** 2026-06-10  
**Context:** Review tab “Verification plan discussion” · `validate-honest-score-l8-hybrid-v1.sh` visible  
**Parent index:** `SOURCEA_MASTER_INDEX_ALL_SUBJECTS_LOCKED_v1.md`

---

## 1. What the screen is

| UI element | Meaning |
|------------|---------|
| **51 Pending Changes** | Cursor agent edit queue — not git commits |
| **Keep All / Undo All** | Accept or reject batch agent edits logged |
| **Review: Verification plan discussion** | Worker chat session edits (Fix All Missing era) |
| **Source Control not configured** | SourceA has **no git repo** — Commit button non-standard |

**Not a bug in L8 validator** — that file **PASS**es when run.

---

## 2. What happened

1. Worker chat wired wrong (headless vs Verification plan) — later fixed  
2. **Fix All Missing** plan produced many file edits across SourceA  
3. Cursor piled edits into Review — founder saw chaos vs “fix for reviewing”  

---

## 3. Option A — Keep All (recommended)

1. Click **Keep All**  
2. Close Review tab  
3. No Terminal · no git commit required — **disk = SSOT**  

**You keep:** validators · L8 hybrid · hub wiring · brain_sync · E2E protection fixes  

**You do not:** auto-resume drain · trust 51 count as “done”  

---

## 4. Option B — Undo All (only if reverting whole Fix All batch)

Rolls back all 51 agent edits — **only** if you want to wipe that entire implementation pass.

---

## 5. After Keep All

- Do **not** Undo later without understanding scope  
- Loops stay **FREEZE** (flag ON) independent of Review  
- Run hub Refresh — not shell  

---

## 6. L8 validator sanity

```bash
bash scripts/validate-honest-score-l8-hybrid-v1.sh
# Expected: OK · hybrid_shipped=True
```

---

**END**
