# Rules in charge — highlighted authority (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Machine:** `scripts/agent_rules_in_charge.py`  
**Hub:** Council Room + Whole-system panel → **Rules in charge NOW**

---

## 0. Law

### ASF terminology (do not invert)

| Term | Meaning |
|------|---------|
| **Exclusive** | **Particular · individual · monopolized scope** — one agent’s lane, one moment’s highlighted laws, one private workspace |
| **Inclusive** | **Overall · all-in · covering all** — every rule in the app index; every agent sees the same global laws |

**Inclusive:** full rule index in the app — **all rules, all 8 agents**, same overall visibility.  
**Exclusive:** **particular** “in charge NOW” highlights — which laws govern **this moment** for **this context**, with relatable labels (not a different ruleset per agent).

---

## 0b. Law (one sentence)

**Inclusive index for all; exclusive highlights for what governs this particular moment.**

---

## 1. Charge levels

| Level | Meaning |
|-------|---------|
| **apex** | Always wins — SSOT, governance entry, authority index |
| **founder_live** | MASTER_ORDERS active + founder directives |
| **session** | Every agent session — hub, vault, scoreboard, essay, council |
| **progress_active** | Current WTM step or open conflicts elevate WTM/ACE |
| **operational** | In charge when you touch that topic (edit lock, critic, semi-separate) |
| **reference** | Read chain background — not highlighted unless context applies |

---

## 2. Context groups (relatable)

Rules are grouped by **context_label** so agents know *when* a law governs:

- Every agent session · Middle layer · Scoreboard · Essay · Council · Edit lock · Semi-separate · WTM build · etc.

---

## 3. Supersession (founder rules stay in charge)

| Rule | Law |
|------|-----|
| **Default** | Every rule you make is **in charge** until a **newer** rule explicitly supersedes it |
| **LOCKED docs** | `FOO_LOCKED_v2.md` supersedes `FOO_LOCKED_v1.md` → move v1 to `archive/superseded/` |
| **Cursor `.mdc`** | Edit the **existing** rule file — add `supersedes: <old-name>` in frontmatter if renaming |
| **Forbidden** | Parallel duplicate alwaysApply rules on the same topic (e.g. two no-Terminal rules) |
| **Authority order** | `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` §0 — ASF_ORDER → LOCKED → SSOT → judgment |

External chat (GPT/Claude) **does not** supersede LOCKED source until ASF adopts it into a LOCKED doc or `.mdc`.

---

## 4. Loop procedure (agents MUST run every session)

**Orchestrator:** `scripts/agent_rules_loop_orchestrator.py`  
**API:** `GET/POST /api/agent-rules-in-charge-v1`  
**Receipts:** `~/.sina/agent_rules_loop_receipt_v1.jsonl`  
**Validator:** `validate-agent-rules-in-charge-v1.sh`

| Phase | When | Agent action |
|-------|------|----------------|
| `session_start` | First message in any Cursor chat | Run check; read `in_charge_now`; cite governing rule if task touches law |
| `loop_round` | Each `[SINA_LOOP` round (injected in prompt) | Re-read highlights; do not contradict in-charge laws |
| `pre_ship` | Before claiming shipped / closing hub work | Re-run check; confirm no duplicate rules added |
| `founder_rule_change` | After ASF adds or changes a law | Update LOCKED or `.mdc` with supersession — never a second parallel rule |
| `maintainer_preflight` | Maintainer audit loop start | Validator + orchestrator PASS |

### Agent affirmation (every check)

1. Fetched in-charge rules from hub SSOT — not from chat memory alone  
2. Read apex + founder_live + session highlights  
3. Will not create duplicate `.mdc` — will extend or supersede existing  
4. Founder never gets Terminal steps — `agent-loop.mdc` + `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md`

---

## 5. Maintainer

Update `RULE_CHARGE_META` in `agent_rules_in_charge.py` when adding a new LOCKED agent law.  
Wire new laws into the loop orchestrator if they are session-level or apex.

---

*Highlighted = in charge NOW. Reference = still in full index, not hidden.*
