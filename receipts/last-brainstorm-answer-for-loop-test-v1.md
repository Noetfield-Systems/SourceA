You want one honest picture: what you asked for, what landed on disk, what's still broken, and the best unified design—not another rules dump.

## What you've been saying (one arc)

Across the thread, your intent was stable even when agents chased side quests:

1. **Build path:** Cloud-first factories (Noetfield freemium → TrustField sandbox on Railway/OpenRouter). Mac = control panel only—not factory muscle.
2. **Decision path:** Official form (`/form/`) with batch submit → nerves/pipelines on disk—not chat theater.
3. **Compile path:** SourceA Sina read → Noetfield compile → TrustField send. Email stays off until product sites are real.
4. **Agent behavior:** When you ask a question, you want **comprehension** (helps you think)—not parroted tokens (`defer`, `sites=RED`, `PASS`, `wired`).
5. **When you say "main problem":** Agents should **prepare the next action**, not write a status report.
6. **Latest insight (critical):** Bad answers are **not always the agent**. Sometimes disk inject is **stale, wrong, or poison**—and the agent is faithfully echoing garbage.

That last point is the breakthrough of this thread.

## What we actually built on disk

| Layer | What | Status |
|--------|------|--------|
| **North star trigger** | `main problem` → PREPARE_NOT_REPORT · picks `next_action` from live disk | Locked + wired (rule 029, session gate, mirror) |
| **Language law** | understand → explain → benefit → proof | v1.2.0 + glossary + conduct gate |
| **Output pipeline** | C1→C7: bug signals + **analyst** + quality gate | Locked (rule 030, validator PASS) |
| **Analyst verdicts** | ACCEPT · RETURN_TO_AGENT · **FIX_DISK** · **FIX_MACHINES** | Live—parrot + stale disk → FIX_DISK, not "write better" |
| **Form** | Sidebar + batch submit (partial PICKs OK) | Code shipped · **116 PICKs still open** |
| **Cloud FBE** | Railway URL · health PASS | Disk says green |
| **NF/TF bays** | Bay receipts ok | Disk says green |
| **Commercial defer** | Email blocked until sites pass | WitnessBC prod still old content (parallel blocker) |

**Disk right now (honest):**

- Cloud factories: **look green** (FBE, NF bay, TF sandbox).
- **Main north-star next action:** P3 — form (116 open PICKs).
- **Session gate:** FAIL (`entry_gate_worker` among others).
- **Anti-staleness / surfaces:** ~50+ minutes stale under focus freeze.
- **Output analyst:** correctly flags **DISK_STALE** when agents parrot labels.
- **Cloud-300 plan:** disk claims `300/300 done` — that may be **completion theater** vs your "real market traction" goal (worth auditing separately).

## Deep diagnosis: why agents keep failing you

Three root causes—not one: Agent writes lazy draft; Disk stale old inject; Disk wrong queue mismatch; Disk poison label soup inject; Wrong priority rules not execution. Pattern: Ship rules and gates while execution and disk freshness lagged.

## Recommended best solution (synthesis)

**Short term:** Main problem + output pipeline as one system. Auto-heal on FIX_DISK/FIX_MACHINES. Execution priority: form PICKs, then WitnessBC prod parallel. Collapse rule proliferation.

**Medium term:** Unified sourcea_unified_loop_v1.py and system-health-backlog-v1.json.

**One sentence north star:** One loop: disk tells next bounded cloud/form action; workers execute; every reply analyzed; analyst fixes stale/poison disk before blaming agent; only ACCEPT reaches you; backlog makes system healthier over time.
