# Phase 1 stabilization ONLY — scope freeze (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-02-019  
**Supersedes expansion in:** `SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md` §4 Phases 2–4 (deferred, not cancelled)  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

## 1. ASF decision (verbatim intent)

After discussion (ASF + Sina OS assistant + external LLMs): **we do not proceed with Phase 2 or complex automation yet.** We stabilize **Phase 1 only.**

**Principle:** **Stability > automation.** Improve reliability of the current flow — do not redesign the system.

---

## 2. What we will NOT do (until Phase 1 exit)

| Forbidden now |
|---------------|
| New architecture files / new SSOT |
| New logging systems (e.g. `REPO_STATUS.yaml` append) |
| Daemon / 24×7 automation |
| YAML-only agent enforcement |
| Self-healing / auto re-prompt expansion |
| M8 Cursor auto-send |
| M7 WebSocket / M9 Docker pack |

Phases 2–4 in YAML ingest doc = **backlog**, not active build.

---

## 3. What we DO now (Phase 1 only)

| Keep | Single source |
|------|----------------|
| Source A law + snapshots | `~/Desktop/SourceA/` |
| Prompt OS brain | `~/Desktop/SinaPromptOS/` |
| Five repos + Lane 0 | `ASF_FIVE_REPOS_PLUS_COMMAND_CHAT_v1.md` |
| Logs | `REPO_EXECUTION_LOGS/` |
| Intent | `REPO_STATUS_REPORTS/` |
| Queues | each repo `os/plan.json` |

| Add (one layer only) |
|----------------------|
| `scripts/ingest-cursor-reply.sh` — parse optional YAML block → validate → route into **existing** submit/mark-done paths |

| Output format |
|---------------|
| Flexible: prose allowed; **optional** fenced YAML block after VERIFY (not YAML-only chat) |

| Human loop (required) |
|-----------------------|
| Paste `ready_to_paste_*.txt` |
| Agent runs VERIFY |
| ASF saves reply → ingest (assisted) OR manual submit until ingest exists |
| Weekly Sunday planning only |

---

## 4. End state for this phase

```text
Cursor output
  → (optional structured YAML block inside reply)
  → manual or assisted ingest (one script)
  → existing state (logs + truth + plan.json manual on Sunday)
  → next prompt via run-full-day.sh / dispatch-day.sh
```

## Phase 1 ingest — BUILT

```bash
./scripts/ingest-cursor-reply.sh <repo> reply.txt
# or: pbpaste | ./scripts/ingest-cursor-reply.sh <repo> -
```

Replaces manual `log.yaml` + `submit-execution-log` + `mark-done-verified` when agent includes YAML block.

**Exit criteria:** 5 execute days without manual submit (see ingest locked doc §8).

---

## 5. Discussion → decision rule (LOCKED)

Every material discussion (Cursor, ChatGPT, Claude, this chat) must produce **one final artifact**:

| Item | Where |
|------|--------|
| **Decision** (what we lock / reject) | This file or new `ASF_DECISIONS/YYYY-MM-DD-<topic>.md` |
| **What changed** | One paragraph |
| **What happens next** | Numbered steps |
| **What we are NOT doing** | Explicit list |

If there is no final decision paragraph, the discussion is **not closed** — do not start implementation.

---

## 6. Alignment check

| Topic | Aligned? |
|-------|----------|
| Agent YAML ingest (optional block) | ✅ Phase 1 ingest only |
| No-copy loop (future) | ⏸ after stability |
| 5 repos + Lane 0 | ✅ |
| Free infra / no card | ✅ |
| `run-full-day.sh` daily | ✅ |

---

## Document control

| Version | Date | seq_id |
|---------|------|--------|
| 1.0 | 2026-06-02 | SA-2026-06-02-019 |

**ASF sign-off:** __________
