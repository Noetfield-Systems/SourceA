# Factory STOP ignored — autodrain after ASF halt (INCIDENT-023 LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-10  
**sequence_id:** SA-2026-06-10-INCIDENT-023  
**Subject:** SUBJ-FACTORY · CONDUCT  
**Related:** INCIDENT-015 (ID collision only — not this conduct) · `factory_control_v1.py` · spawn gate

---

## One sentence

**ASF STOP must write stop receipt and block spawn same turn — autodrain after halt is conduct failure.**

---

## Law

| Event | Required |
|-------|----------|
| ASF_STOP | `stop_goal1_auto_run_v1.py` first · `write_stop_receipt` |
| Kill flag ON | `exit_if_spawn_blocked()` on all drain entrypoints |
| Hub | Factory STOP only — no Cursor AUTO-RUN hero |

---

## Remediation checklist

- [x] `factory_control_v1.py` spawn gate
- [x] `validate-factory-conduct-v1.sh`
- [x] Hub projection purge (AS-01)
- [ ] Close when 30-day zero STOP→drain transcripts

**Speech law:** **015** = ID collision only · **023** = STOP conduct

**Status:** REMEDIATED 2026-06-10 — D2=Accept · spawn gate proof

**END INCIDENT-023**
