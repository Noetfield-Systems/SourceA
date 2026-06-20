# Agent memory mirror enforcement (LOCKED v1)

**Saved:** 2026-06-20T19:00:00Z · **Retrofit:** mirror poison law v1.1 (INCIDENT-034/039/040)
**Version:** 1.1 · **Locked:** 2026-06-26 · **Authority:** ASF order  
**sequence_id:** SA-2026-06-26-AGENT-MEMORY-MIRROR  
**Machine SSOT:** `scripts/agent_memory_mirror_v1.py`  
**Mirror JSON:** `~/.sina/agent-memory-mirror-v1.json`  
**Parent:** `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md` (S4 chat memory)  
**Incidents:** 024 · 028 · 016 · 002

---

## 0. One sentence

**All agent-law surfaces mirror one machine SSOT — agents READ receipts and reply in plain English; validator marathons are cloud CI / ship window only, never mandatory pre-reply poison.**

---

## 1. Law

| Rule | Enforcement |
|------|-------------|
| Chat is not SSOT | Disk + mirror JSON + receipts |
| Law change | **Seven-surface supersession** — **cloud CI / ASF ship window only** · **not** agent pre-reply bash (§7 poison law) |
| Every session (all chats) | Read session gate **receipt** · do not re-run validator stacks mid-turn |
| Stale phrase logged | Maintainer `validate-law-supersession-surfaces-v1.sh` on ship — **not** founder chat body |
| Dead law in agent output | `000-dead-law-stubs.mdc` alwaysApply — overrides stale injection |
| Prompt feed | Display + optional commentary · **never** confirm auto-send (024/028) |
| Execution | Run inbox + `live-ongoing-prompts-next-10-v1.json` |
| Cursor AUTO-RUN | Does not exist · FREEZE unless ASF resume |
| Founder cancel / STOP | PLAN_REVOKED protocol (016) — all todos cancelled + receipt |

---

## 2. Seven surfaces (maintainer ship sync — NOT pre-reply)

| # | Surface | Sync mechanism |
|---|---------|----------------|
| 1 | LOCKED docs + `.mdc` | Supersede vN → archive old |
| 2 | `MANDATORY_READ_BY_ROLE` | Row per incident |
| 3 | Hub + script copy | `agent_memory_mirror_v1.py --write` on **ship window only** |
| 4 | `agent_rules_in_charge.py` | Maintainer on law ship |
| 5 | Validators | **Ship window / cloud CI only** — never agent chat pre-reply marathon |
| 6 | `agent_truth_bundle` inject block | Reads mirror JSON |
| 7 | Session receipts | Read `agent_session_gate_receipt_v1.json` — do not re-run stack mid-turn |

**Forbidden:** fix one surface only · **forbidden:** bash validate marathon before founder reply.

---

## 3. Session gate (all roles · all chats)

```bash
python3 scripts/agent_session_gate_run_v1.py --role worker --json
python3 scripts/agent_session_gate_run_v1.py --role brain --json
python3 scripts/agent_session_gate_run_v1.py --role any --json   # mirror-only universal
```

**Order (session gate — once per chat):** memory mirror sync → truth bundle → rules loop → entry gate (role) → receipt.

**Agent law:** Read receipt if present — reply from disk. **Do not** block founder chat to re-run mirror `--validate` or bash validate stacks mid-turn (INCIDENT-039). Mirror `validation.ok` on receipt is informational — proof = Read `~/.sina/*-receipt*.json`.

---

## 4. Verify (Maintainer · cloud CI · ship window ONLY — never Mac founder chat pre-reply)

```bash
python3 scripts/agent_mirror_poison_scrub_v1.py --validate --json
bash scripts/validate-agent-law-poison-free-v1.sh
```

Full supersession stack — **maintainer ship only:**

```bash
bash scripts/validate-law-supersession-surfaces-v1.sh
bash scripts/validate-agent-memory-mirror-v1.sh
bash scripts/validate-anti-staleness-bundle-v1.sh
```

---

## 5. Supersession

This doc supersedes draft `2026-06-26_AGENT-MEMORY-FIX-PROGRAM-048.md` as **locked law**.  
Companion research: `~/.sina/.../2026-06-26_AGENT-MEMORY-RELAPSE-ROOT-CAUSE-047.md` (inform only).

---

**END LOCKED v1**

---

## 7. Mirror poison law (v1.1 — INCIDENT-034 · INCIDENT-039)

**Saved:** 2026-06-20T20:00:00Z · **ASF intent:** mirror must not order harmful agent conduct.

| Poison (FORBIDDEN in mirror inject + alwaysApply rules) | Positive replacement |
|--------------------------------------------------------|----------------------|
| `validate-law-supersession-surfaces-v1.sh` before every reply | Read `~/.sina/*-receipt*.json` · reply <30s |
| “Seven surfaces → validate → sync → reply” | Supersession validators = **cloud CI / ship window only** |
| W1–W10 check cart before chat closeout | Check cart = maintainer ship window · not founder chat body |
| Prohibition tables without read path | Positive inject: Hub · form · factory_now_line · receipts |

**Machine SSOT:** `data/agent-memory-mirror-poison-law-v1.json` · `data/agent-law-poison-registry-v1.json`  
**Cursor rule:** `.cursor/rules/agent-memory-mirror.mdc` (rewritten v1.1)

**Machine scrub:** `python3 scripts/agent_mirror_poison_scrub_v1.py --all`  
**Scan gate:** `bash scripts/validate-agent-law-poison-free-v1.sh` (repo scan — **PASS** 2026-06-20)  
**One sentence:** Mirror wires **what to read** — never **bash validate marathons** as mandatory pre-reply law.

---

## 6. v2 conduct stack (2026-06-13)

**Extended by:** `SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md` (authority row `AGENTIC_ENFORCEMENT_V2`)

Adds: conduct gate · read-order gate · G7 scan-before-heal · spine `AGENT_SESSION_GATE` events · receipt schema **v1.1**.

Session gate order v2: mirror → truth → rules → **conduct** → entry → spine → receipt.

```bash
bash scripts/validate-agentic-enforcement-stack-v2-v1.sh
```
