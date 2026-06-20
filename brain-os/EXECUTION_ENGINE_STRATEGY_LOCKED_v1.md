# SourceA Execution Engine Strategy — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Updated:** 2026-06-08 · **Author:** ASF

---

## THREE-ENGINE FULL STACK

All three engines are ACTIVE. Each has a job.

| Engine | Job | When |
|--------|-----|------|
| **Claude Code CLI** (`claude_code_agent_v1.py`) | Real file execution — Bash, Write, Edit, Read | High-tool tasks: implement, build, fix, patch |
| **API Agent** (`claude_api_agent_v1.py`) | Auto-run mode — headless, 24/7, no supervision | Low-tool tasks: verify, check, audit, review + when ASF is away |
| **Cursor** | IDE-heavy work — UI, complex refactors, debugging | Stuck tasks, React/CSS, multi-file IDE context needed |

---

## SMART ROUTING — tool-count intelligence

Route by expected tool complexity, not just role label.

### High-tool path → Claude Code CLI

Tasks that need real filesystem changes:
- `act`, `implement`, `build`, `fix`, `patch`, `create`, `write`
- Expected tool calls > 3
- Must write files, run bash, validate with scripts
- Use **Sonnet** (needs reasoning + tool use)

### Low-tool path → API Agent

Tasks that need reasoning only:
- `verify`, `check`, `audit`, `review`, `validate`, `read`, `assess`
- Expected tool calls: 0
- Claude reads context, reasons, returns structured report
- Use **Haiku** for simple checks, **Sonnet** only if complex reasoning needed

### IDE path → Cursor

- Heavy React/CSS/UI work
- Multi-file refactors where IDE autocomplete helps
- Tasks blocked 2+ times by CLI agent
- ASF wants to supervise / pair-program

---

## COST INTELLIGENCE MATRIX

| Path | Model | Cost/turn | Volume | Est. total |
|------|-------|-----------|--------|-----------|
| CLI — act/build | Sonnet 4.6 | ~$0.05–$0.25 | ~40% tasks | ~$6 |
| API — verify/check | Haiku 4.5 | ~$0.002–$0.005 | ~40% tasks | ~$1 |
| API — complex verify | Sonnet 4.6 | ~$0.02–$0.05 | ~20% tasks | ~$2 |
| Cursor | manual | $0 API | ~5% tasks | — |
| **Total** | | | **681 tasks** | **~$9** |

---

## AUTO-RUN MODE (when ASF is away)

API agent runs via launchd (every 90s):
- Drains verify/check tasks autonomously
- Haiku for simple, Sonnet for complex
- No file system risk — read-only reasoning
- Results saved to `~/.sina/api-agent-results/`

CLI agent runs via launchd (same daemon) for act tasks:
- Real tools, real file changes
- Receipt written to `receipts/sa-XXXX-receipt.json`
- Queue auto-advances

Kill everything: `touch ~/.sina/auto-run-disabled-v1.flag`

---

## SMART PROMPTING FOR API AGENT

The API agent prompt must be richer when no tools are available:

1. **Load the full task .md** (sa_path) — not just the instruction field
2. **Include mandatory_reads** — governance context
3. **Include verify + forbidden** fields
4. **Ask for structured output** — WORKER_ROUND_REPORT YAML with evidence
5. **Include machine state** — last receipt, last validator output if available

The API agent cannot write files — so its job is to:
- Verify existing work is correct
- Identify gaps or blockers
- Report what needs to be done next (for CLI agent to execute)

---

## ROUTING DECISION TREE

```
Queue item arrives
    ↓
role = act / implement / build / fix ?
    ├── YES → Claude Code CLI (Sonnet)
    └── NO
        ↓
        role = verify / check / audit / review ?
            ├── YES, simple → API Agent (Haiku)
            ├── YES, complex → API Agent (Sonnet)
            └── NO
                ↓
                UI / blocked / IDE-heavy ?
                    ├── YES → Cursor
                    └── NO → CLI default (Sonnet)
```

---

## RECEIPTS = TRUTH

Only the receipt logged is truth. Not chat output, not YAML blocks.
- `receipts/sa-XXXX-receipt.json` with `status: DONE` = done
- API agent verify results feed back to CLI agent act queue
- Cursor work must write a receipt too

---

Worker/Brain implements in the repository — I hold until you ask.
