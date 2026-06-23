# Agent execution discipline (LOCKED)

Saved: 2026-06-22T23:25:00Z

**SSOT:** `data/agent-execution-discipline-v1.json`  
**Cursor:** `.cursor/rules/036-agent-execution-discipline-v1.mdc` (`alwaysApply: true`)

## Rules

1. Never wait. Never observe. Never sleep.
2. Do the task. Show proof. Stop.
3. Proof = raw output only. No summaries. No reports.
4. If a command takes more than 30 seconds, kill it and report why.
5. Never run more than 3 commands per response.
6. Never say "fixed" without showing curl/log proof.
7. Never deploy unless explicitly told to.
8. Never open polling loops.
9. One task per message. No multi-step plans.
10. If you don't know, say: "I don't know." Do not guess.
