# Brain — end-of-turn prompt (paste every turn · LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Law:** `BRAIN_NO_LEFTOVER_PROCESS_LOCKED_v1.md`

---

## Paste to Brain (after every reply that touched loop / spawn / overnight / workers)

```text
END TURN — NO LEFTOVERS (mandatory):

cd /Users/sinakazemnezhad/Desktop/SourceA
python3 scripts/cleanup-goal1-leftovers-v1.py --json

Rules:
- If remaining_count > 0 → STOP. Report remaining_pids. Do NOT say loop is running.
- If you spawned anything → you MUST run cleanup before final STOP.
- Do NOT start start-overnight-3engine-v1.sh from Brain unless ASF explicitly orders sleep overnight AND founder_absent is on disk.
- Cursor must NOT autorun overnight. Kill flag ON after cleanup is correct default.

Reply footer (required):
```yaml
brain_leftover_cleanup:
  ran: true
  remaining_count: <from json>
  kill_flag: <true|false>
  ok: <true|false>
```
```

---

## One-line ASF version

```text
End turn: cleanup-goal1-leftovers-v1.py --json · remaining_count must be 0 · else STOP.
```

---

*End BRAIN END TURN NO LEFTOVER PROMPT v1*
