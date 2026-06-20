# Agent miss → disk-first correction loop (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-07  
**Authority:** ASF order — mandatory every session  
**Parent:** `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` §5 · `BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md`  
**Audience:** Brain · Worker · any agent that routes or advises ASF

---

## 0. One sentence

**When you notice a miss, confusion, or mistake — fix the disk source that caused it before you tell ASF the answer was wrong.**

Chat corrections without doc hardening **do not count** as done.

---

## 1. Triggers (run loop immediately)

| Trigger | Examples |
|---------|----------|
| ASF corrects you | “SinaaiDataBase is retired” · “we have one worker” · “no prompt 13” |
| You catch drift mid-reply | Wrong chat assigned · invented lane · stale handoff |
| User confusion from your last message | “who is prompt 10 for?” · “what is FORGE builder?” |
| Near-miss | Almost routed work to archive chat or parallel lane as default |

**Do not** open with apology-only or “correction of last message” prose. **Do** run §2 first.

---

## 2. Mandatory order (disk first — every time)

```text
IDENTIFY → EDIT DISK → WIRE → VERIFY → THEN REPLY TO ASF
```

| Step | Action | Done when |
|------|--------|-----------|
| **1 IDENTIFY** | Name the **root cause file(s)** — handoff, index, notice, rule, stale table | Path list written (internal or in closeout) |
| **2 EDIT DISK** | Rewrite / refine / supersede the confusing source — minimal diff, one canonical home | LOCKED or index updated; no parallel prose in chat |
| **3 WIRE** | Pointer rows in: index · brain read chain · `sync-brain-pack.sh` · `SOURCEA-PRIORITY.md` evidence if material | No orphan doc |
| **4 VERIFY** | `sync-brain-pack.sh` if brain handoff touched; pack validator if REGISTRY law touched | Mirror matches repo |
| **5 REPLY ASF** | Short user message per §4 template only **after** steps 1–4 | User sees what changed logged |

**Forbidden sequence:** `sorry → corrected answer` **without** step 2.

---

## 3. What to edit (where confusion lives)

| Confusion type | Fix target (priority) |
|----------------|----------------------|
| Wrong chat / lane assignment | `WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md` · `MANDATORY_CHAT_HANDOFF_INDEX` · `ECOSYSTEM_BRAIN_ROLLOUT` |
| Retired chat still assigned work | `SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF` · `REPO_NOTICE_*` · `SINA_COMMAND_EDIT_LOCK` |
| Brain routing behavior | `MANDATORY_BRAIN_CHAT` · `BRAIN_COMPLETE_TRANSFER` §PASTE BLOCK |
| Worker scope | `MANDATORY_SOURCEA_WORKER_CHAT` §BUILD SCOPE |
| Founder daily rhythm | `FOUNDER_DAILY_OPERATING_MODEL` |
| General agent judgment | `AGENT_DECISION_STACK` · `.cursor/rules/agent-smart-judgment.mdc` (pointer only) |

**Law:** One topic → one canonical LOCKED doc. Extend or supersede — never a third chat-only rule.

---

## 4. Reply template (after disk fix only)

```yaml
---
status: DISK_FIX_CLOSEOUT
loop: AGENT_MISS_DISK_FIRST_CORRECTION
root_cause_docs: [<paths edited>]
wired_into: [<index / brain-pack / PRIORITY>]
user_reply_was_wrong_on: <one line>
disk_now_says: <one line>
---
```

Then **≤1 screen** for ASF:

1. What was wrong in the **last answer** (one line)  
2. Which **files were fixed** (paths)  
3. What **disk now says** (one line) — not a re-litigation of the old message  

---

## 5. Daily mandatory hooks

| When | Requirement |
|------|-------------|
| **Brain session start** | Read this file after `WORKER_ASSIGNMENT_AND_CHAT_ROUTING` · ack loop in first YAML note |
| **Worker session start** | `cursor_agent_self_audit.py session-start` · obey wired handoffs only |
| **Before any “I was wrong” reply** | Steps 1–4 complete |
| **Session close (material miss)** | `session-close` + `~/.sina/agent-governance-events.jsonl` row · optional PRIORITY evidence |
| **End of day (Brain)** | If any miss was fixed today, confirm `sync-brain-pack.sh` ran after last handoff edit |

---

## 6. Relation to self-healing

Extends `AGENT_DECISION_STACK` §5:

```text
detect → classify → remediate (DISK FIRST) → harden → verify → record → then user reply
```

**Harden** = edit the doc that caused the miss, not a longer chat correction.

---

## 7. Wire

| File | Role |
|------|------|
| `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` | §5b pointer |
| `BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md` | §Daily loops |
| `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` | Read chain |
| `FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md` | §Brain agent discipline |
| `scripts/sync-brain-pack.sh` | Mirror |

---

*End AGENT MISS DISK-FIRST CORRECTION LOOP v1*
