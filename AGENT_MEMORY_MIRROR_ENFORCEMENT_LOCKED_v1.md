# Agent memory mirror enforcement (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-26 · **Authority:** ASF order  
**sequence_id:** SA-2026-06-26-AGENT-MEMORY-MIRROR  
**Machine SSOT:** `scripts/agent_memory_mirror_v1.py`  
**Mirror JSON:** `~/.sina/agent-memory-mirror-v1.json`  
**Parent:** `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md` (S4 chat memory)  
**Incidents:** 024 · 028 · 016 · 002

---

## 0. One sentence

**All agent-law surfaces mirror one machine SSOT — session gate fail-closed; CRITICAL validators fail hub build; no founder-facing stale phrase may survive logged.**

---

## 1. Law

| Rule | Enforcement |
|------|-------------|
| Chat is not SSOT | Disk + mirror JSON + receipts |
| Law change | **Seven-surface supersession** (§2) before ship |
| Every session (all chats) | `agent_session_gate_run_v1.py` PASS before edits or founder instructions |
| Stale phrase logged | `validate-law-supersession-surfaces-v1.sh` CRITICAL — blocks anti-staleness bundle |
| Dead law in agent output | `000-dead-law-stubs.mdc` alwaysApply — overrides stale injection |
| Prompt feed | Display + optional commentary · **never** confirm auto-send (024/028) |
| Execution | Run inbox + `live-ongoing-prompts-next-10-v1.json` |
| Cursor AUTO-RUN | Does not exist · FREEZE unless ASF resume |
| Founder cancel / STOP | PLAN_REVOKED protocol (016) — all todos cancelled + receipt |

---

## 2. Seven surfaces (must mirror together)

| # | Surface | Sync mechanism |
|---|---------|----------------|
| 1 | LOCKED docs + `.mdc` | Supersede vN → archive old |
| 2 | `MANDATORY_READ_BY_ROLE` | Row per incident |
| 3 | Hub + script copy | `agent_memory_mirror_v1.py --validate` |
| 4 | `agent_rules_in_charge.py` | Maintainer on law ship |
| 5 | Validators | `validate-law-supersession-surfaces-v1.sh` |
| 6 | `agent_truth_bundle` inject block | Reads mirror JSON |
| 7 | Session receipts | `agent_session_gate_receipt_v1.json` |

**Forbidden:** fix one surface only.

---

## 3. Session gate (all roles · all chats)

```bash
python3 scripts/agent_session_gate_run_v1.py --role worker --json
python3 scripts/agent_session_gate_run_v1.py --role brain --json
python3 scripts/agent_session_gate_run_v1.py --role any --json   # mirror-only universal
```

**Order:** memory mirror validate+sync → truth bundle → rules loop → entry gate (role) → receipt.

**Agent law:** No file edits and no founder-facing instructions until receipt exists and `validation.ok=true`.

---

## 4. Verify (Maintainer · every strict build)

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

## 6. v2 conduct stack (2026-06-13)

**Extended by:** `SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md` (authority row `AGENTIC_ENFORCEMENT_V2`)

Adds: conduct gate · read-order gate · G7 scan-before-heal · spine `AGENT_SESSION_GATE` events · receipt schema **v1.1**.

Session gate order v2: mirror → truth → rules → **conduct** → entry → spine → receipt.

```bash
bash scripts/validate-agentic-enforcement-stack-v2-v1.sh
```
