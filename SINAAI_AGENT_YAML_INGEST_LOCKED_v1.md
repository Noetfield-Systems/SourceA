# Sinaai Agent YAML Ingest & Self-Healing Loop — FINAL LOCKED

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Replaces manual log glue — does NOT replace human weekly control

**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-018  
**Classification:** INTERNAL ONLY  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md`  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3  
**Implementation root:** `~/Desktop/SinaPromptOS/`  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## 1. Decision (one paragraph)

Ecosystem agents (five product Cursor chats + Lane 0 command chat) **MUST** end every IMPLEMENT/VERIFY turn with a **machine-readable YAML block** matching the locked schema below. **Prompt OS ingests** that block automatically into existing **Execution Truth** paths (`REPO_EXECUTION_LOGS`, truth re-rank, optional `plan.json` update via M5). **ASF does not** hand-create log files, hand-run submit, or daily re-prioritize. **Weekly Sunday** remains the only required human planning window. **YAML-only chat with no prose** is **forbidden** as a hard rule — parsers accept YAML inside the reply.

---

## 2. What stays locked from prior decisions

| Item | Status |
|------|--------|
| 5 product repos + Lane 0 (`ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md`) | ✅ |
| No credit card / free infra (`FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md`) | ✅ |
| `auto_sync_plan` default **OFF** until M5 with `--verified` | ✅ |
| Cursor auto-send (M8) **not required** for Phase 1 ingest | ✅ |
| TrustField equal to other repos | ✅ |

---

## 3. Agent output contract (LOCKED schema)

Every agent reply after VERIFY **must include** this block (fenced `yaml` or last `---` document):

```yaml
schema_version: 1
repo: trustfield          # one of: trustfield | sinaai_mono | virlux | noetfield | seven77
task: "<one line active task>"
status: done | blocked | partial
verify_passed: true | false
verify_command: "<command run or NONE>"
verify_output_summary: "<one line result>"
blocked_reason: "<if blocked, else empty>"
next_action: "<one line for system or ASF>"
evidence_paths: []        # optional repo-relative paths
reported_at: "<ISO8601 UTC>"
reporter: cursor
```

**Rules:**

- `repo` must match the workspace chat’s repo (no cross-repo YAML).
- If `verify_passed: false` → `status` cannot be `done`.
- Prose above/below the block is allowed; **missing block = ingest FAIL**.

**Canonical template file (do not fork):**  
`SourceA/REPO_EXECUTION_LOG_TEMPLATE.yaml` — ingest maps fields into that shape.

**Do NOT invent:** `REPO_STATUS.yaml` append-only files, new SSOT #4, or YAML-only chat mode.

---

## 4. Ingest pipeline (LOCKED phases)

### Phase 1 — Manual ingest (build first) ✅ target

| Step | Component | Behavior |
|------|-----------|----------|
| 1 | Agent | Ends reply with YAML block |
| 2 | ASF | Saves reply to `SinaPromptOS/outputs/inbox/<repo>-<timestamp>.txt` **or** pipes clipboard |
| 3 | `scripts/ingest-agent-reply.sh` | Parse → validate → write log under Source A |
| 4 | Python | Calls existing `submit-execution-log` + `mark-done-verified` logic |
| 5 | Optional | `./scripts/run-full-cycle.sh` refresh rank |

**Eliminates:** manual `log.yaml` authoring, manual submit commands.

**Keeps:** one paste into Cursor per repo (until M8).

### Phase 2 — Folder watcher

- Watch `outputs/inbox/*.txt` → auto Phase 1 on file close.
- Invalid YAML → `outputs/inbox/rejected/` + reason log.

### Phase 3 — Self-heal re-prompt

- `verify_passed: false` → bump priority, append fix micro-task to `os/plan.json` **only** if M5 flag `--verified` or ASF Sunday edit.
- Regenerate `ready_to_paste_<repo>.txt` on next `dispatch-day.sh`.

### Phase 4 — M8

- Cursor SDK sends prompt; ingest unchanged.

**FROZEN (2026-06-02):** Phase 2–4 are **deferred** until `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md` exit criteria met. Do NOT start Phase 2 until Phase 1 works on 3 real repos in production daily use.

---

## 5. Lane 0 (this Sina OS chat)

| Role | Output |
|------|--------|
| Command chat | May emit **ecosystem YAML** (optional) listing lanes completed — or run Terminal only |
| Product repos | **Required** per-task YAML block above |

Lane 0 does **not** replace five repo VERIFY YAMLs.

---

## 6. Daily + weekly loop (LOCKED)

**Mon–Sat (execute):**

```bash
cd ~/Desktop/SinaPromptOS && ./scripts/run-full-day.sh
# 5× Cursor: ready_to_paste_<repo>.txt → IMPLEMENT → VERIFY
# After each reply: ingest-agent-reply.sh <repo> <saved-reply.txt>
```

**Sun (think ~30 min):** `projects.json`, all `os/plan.json`, phase gates — **no ingest build day**.

---

## 7. Explicitly forbidden

- Requiring agents to output **only** YAML with no text (brittle).
- Paid infra or Render Postgres/Redis to “fix” ingest failures.
- 24/7 unsupervised daemon shipping code without VERIFY.
- New merged mega-blueprint superseding §2–§5 docs.
- Skipping VERIFY and marking `verify_passed: true`.

---

## 8. Success criteria (Phase 1 exit)

| # | Criterion |
|---|-----------|
| 1 | Schema validated on ingest for all 5 repo ids |
| 2 | ASF has **not** run manual `submit-execution-log` for 5 consecutive execute days |
| 3 | At least one real ingest per repo in `REPO_EXECUTION_LOGS/` |
| 4 | `run-full-cycle.sh` re-ranks using ingested truth |
| 5 | Invalid YAML rejected with readable error (no silent drop) |

---

## 9. Names (locked vocabulary)

| Term | Meaning |
|------|---------|
| **Agent Output Contract** | Schema §3 |
| **YAML Ingest** | Phase 1–2 parser + writer |
| **Self-heal** | Phase 3 re-queue on `verify_passed: false` |
| **No-copy loop** | No manual log file; paste reply once → ingest |

Do not rename to SHEE/AFES in code paths — use `yaml_ingest` module name.

---

## 10. Build order (implementation queue)

1. `SourceA/AGENT_OUTPUT_CONTRACT_v1.yaml` (machine schema)  
2. `core/yaml_ingest.py` + `scripts/ingest-agent-reply.sh`  
3. Append contract footer to `ready_to_paste_*.txt` generator  
4. Update `CURSOR_REPO_SPECIALIZED_NOTICES` — YAML block required after VERIFY  
5. Phase 2 watcher (after Phase 1 exit)  
6. Phase 3 self-heal (after M5 design)  
7. M8 (separate track)

---

## Document control

| Version | Date | seq_id | Change |
|---------|------|--------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-018 | Lock ingest + phases + forbid YAML-only |

**ASF sign-off:** __________
