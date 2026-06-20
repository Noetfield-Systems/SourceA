> **ARCHIVE ONLY — not canonical law.** Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

# SourceA — Brain repair audit + INCIDENT-014 completion

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**Date:** 2026-06-10  
**Law:** INCIDENT-014 · `brain_sync_lib_v1.py`  
**Parent index:** `SOURCEA_MASTER_INDEX_ALL_SUBJECTS_LOCKED_v1.md`

---

## 1. What INCIDENT-014 was

Monitor showed **Brain PEND on every green row** while Worker/Broker/Valid YES stayed green. **Not** redo — **one stale** `brain-goal1-validation-v1.json` vs live `valid_yes`.

---

## 2. What was shipped (verified)

| Item | Status |
|------|--------|
| `brain_sync_lib_v1.py` SSOT | ✅ |
| Hooks: closeout · advance · autodrain · orchestrator · worker batch · hub refresh | ✅ 9 sites |
| `validate-brain-snapshot-sync-v1.sh` | ✅ snapshot alignment gate |
| `validate-brain-sync-hooks-v1.sh` | ✅ wired find_critical_bugs |
| Hub `founder-brain-sync-monitor` | ✅ |
| monitor.html Brain sync column | ✅ |
| `ecosystem_incidents_index.py` row 014 + 011 | ✅ |
| Unified callers: fix-ecosystem · brain-session-start · enforce-hygiene | ✅ |
| Snapshot validator logic | ✅ fails on stale only not dual_proof alone |

---

## 3. Closeout checklist (INCIDENT-014)

- [x] brain_sync_lib wired  
- [x] Monitor UX + hub ↺  
- [x] Validators in find_critical_bugs  
- [x] ecosystem_incidents_index row  
- [x] enforce-registry uses brain_sync_lib  
- [ ] Standard E2E PASS line (separate thread)  

---

## 4. Live state (post-repair)

- brain_vy == live_vy after light sync  
- dual_proof can still GAP on hygiene/broker backlog (separate from 014)  

---

## 5. What Brain repair did NOT fix

- Conduct (015-CONDUCT)  
- Spawn gate / STOP lexicon  
- Inject parrot (013) — needs factory-now  
- Batch autodrain culture  

---

## 6. Never-again (Brain agents)

```text
Never say "verified" alone —
  Valid YES N · brain snapshot M · dual_proof OK/GAP
Brain PEND on all green rows ≠ redo — one global stale file.
```

---

**END**
