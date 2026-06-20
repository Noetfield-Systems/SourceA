# Brain disk-before-chat session loop (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-07  
**Authority:** ASF — stable procedure when Brain ignores mandatory reads  
**Parent:** `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` · `BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md` · `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md`  
**Audience:** SourceA **Brain** chat only

---

## 0. One sentence

**Brain reads disk and runs `brain-session-start.sh` before every routing reply — chat memory is never SSOT.**

FORGE-builder drift was one **symptom**. Root cause: **mandatory read chain with no mechanical gate.**

---

## 1. Why “mandatory” was ignored

| Layer | Worker | Brain (before this file) |
|-------|--------|---------------------------|
| Read list logged | ✅ `MANDATORY_SOURCEA_WORKER_CHAT` | ✅ `MANDATORY_BRAIN_CHAT` + `BRAIN_KNOWLEDGE_INDEX` |
| Mechanical session gate | ✅ `cursor_agent_self_audit.py session-start` | ❌ honor system only |
| First reply proof | ✅ read chain path printed | ❌ `BRAIN_ACK` from chat memory |
| Validator | ✅ session-close checks `session_start` | ❌ none |
| On miss | `AGENT_MISS_DISK_FIRST` | same — but Brain skipped reads first |

**Law:** Listing files is not enforcement. Brain needs the **same class of gate** Worker has.

---

## 2. Mandatory order (Brain session start — then read receipt every turn)

```text
SESSION START: brain-session-start.sh → READ receipt → BRAIN_ACK FROM receipt ONLY → route
EVERY TURN AFTER: READ receipt JSON — do NOT re-run brain-session-start.sh mid-turn (INCIDENT-039)
```

| Step | Action | Done when |
|------|--------|-----------|
| **1 RUN** | `bash scripts/brain-session-start.sh` from `~/Desktop/SourceA` | Script exits 0; receipt at `~/.sina/brain_session_receipt_v1.json` |
| **2 READ** | Open paths printed in `disk_reads_required` — **not** prior chat turns | Assignment SSOT + machine truth + live pick from disk |
| **3 ACK** | First reply = `BRAIN_ACK` YAML — **field values copied from script JSON only** | `session_receipt_id` matches receipt file |
| **4 ROUTE** | Handoff names **SourceA Worker** only; cite `WORKER_ASSIGNMENT` for assignment questions | No invented roles · no chat-memory routing |
| **5 ON MISS** | `AGENT_MISS_DISK_FIRST` — edit root doc → wire → verify → then reply | Not apology-first |

**Forbidden before step 3:**
- Routing prose (“send to FORGE builder”, “parallel lane”, “open X workspace”)
- “Direct answers” essays
- Paraphrasing machine truth from memory
- **`pick 30` queue dumps** — Brain assigns **one** `next_pick` from `pick 1` only (`REGISTRY_DRAIN_RAIL` §PICK ORDER)

---

## 3. BRAIN_ACK contract (after script only)

```yaml
status: BRAIN_ACK
lane: brain
workspace: SourceA
session_receipt_id: <from brain-session-start.sh>
disk_ssot: true
chat_memory_used: false
machine_truth: <verbatim from script — SOURCEA-PRIORITY §Machine truth>
next_pick: <verbatim from script — plan-no-asf-run.sh pick 1>
assignment_ssot: WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md §2
one_worker: true
dispatch_ready: <from script>
ready: true
note: No implementation in brain chat — handoff SourceA Worker only
```

**Required fields:** `session_receipt_id` · `disk_ssot: true` · `chat_memory_used: false` · `next_pick` from script.

**Worker handoff:** every Brain Worker paste must cite `WORKER_ROUND_REPORT` contract (`MANDATORY_SOURCEA_WORKER_CHAT` §EVERY ROUND ORDER) — validate → act → report → stop.

If Brain cannot run the script: say so in one line and **stop** — do not route from memory.

---

## 4. Assignment questions (always cite disk)

| ASF asks | Brain must |
|----------|------------|
| Who builds X? | Open `WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md` §1–§2 — quote table |
| Is there a second worker / FORGE chat? | §22 forbidden words — **one SourceA Worker** |
| What is FORGE? | Product path `~/Desktop/forge/` — not a chat role |
| What next? | `next_pick` from script — not stale chat |

**Forbidden labels:** any term in `WORKER_ASSIGNMENT` §22 forbidden words list.

---

## 5. Relation to other loops

| Loop | When |
|------|------|
| **This file** | Brain session start + read receipt every routing reply — **not** re-run script every turn |
| `AGENT_MISS_DISK_FIRST` | After wrong answer — fix root doc then reply |
| `agent_rules_loop_orchestrator.py session_start` | Hub rules banner — run in addition, not instead |
| Worker `cursor_agent_self_audit.py session-start` | Worker only — Brain does **not** substitute worker script |

---

## 6. Wire

| File | Role |
|------|------|
| `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` | §SESSION GATE · §FIRST REPLY |
| `BRAIN_COMPLETE_TRANSFER_LOCKED_v1.md` | §PASTE BLOCK |
| `BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md` | §12 daily gate |
| `BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md` | Session-start row #0 |
| `scripts/brain-session-start.sh` | Mechanical gate |
| `scripts/validate-brain-disk-before-chat-v1.sh` | Strict-build wiring check |
| `scripts/sync-brain-pack.sh` | Mirror handoff |
| `FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md` | §7 Brain discipline |

---

## 7. ASF enforcement (one line)

If Brain’s first reply lacks `session_receipt_id` or `next_pick` does not match live script output → **reply “rerun brain-session-start”** — do not debate routing in chat.

---

*End BRAIN DISK-BEFORE-CHAT SESSION LOOP v1*
