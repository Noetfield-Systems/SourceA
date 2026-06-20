# SourceA — Agentic enforcement stack (LOCKED v2)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0 — LOCKED  
**sequence_id:** SA-2026-06-13-AGENTIC-ENFORCEMENT-V2  
**Authority:** ASF upgrade order · extends **AGENT_MEMORY_MIRROR v1** (not replace)  
**Machine:** `scripts/agentic_conduct_gate_v1.py` · `scripts/agent_session_gate_run_v1.py` · `scripts/governance_event_spine_v1.py`  
**Parent:** `AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md` · `GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md`  
**Incidents absorbed:** 026 (validator recursion) · 027 (read order) · 028 (auto-send) · 016 (false done)

---

## 0. One sentence

> **Agents fail-closed logged law, emit spine events on every session gate, and carry conduct limits (no validator chains, scan-before-heal, commercial read order) into every chat — chat is never SSOT.**

---

## 1. Stack layers (v2)

| Layer | Gate | Machine | Fail mode |
|-------|------|---------|-----------|
| **L0 Memory mirror** | Seven-surface sync | `agent_memory_mirror_v1.py` | **HARD** — no edits |
| **L1 Session gate** | Mirror + truth + rules loop | `agent_session_gate_run_v1.py` | **HARD** — receipt `ok=false` |
| **L2 Conduct gate** | INCIDENT-026 + forbidden shells | `agentic_conduct_gate_v1.py` | **SOFT warn** · HARD on brain role violation |
| **L3 Read order** | Form → SSOT → unified index | conduct gate paths | **WARN** maintainer · **HARD** hub P0 edits |
| **L4 G7 discipline** | `--scan` before `--heal` | human + daemon law | **HARD** on blind heal |
| **L5 Spine emit** | Every session gate pass/fail | `governance_event_spine_v1.py` | **Append** — never block gate |
| **L6 Post-ship** | Closeout + lesson append | `cursor_agent_self_audit.py` | **SOFT** — maintainer substantive turns |

---

## 2. Conduct gate (INCIDENT-026 class)

### Forbidden in agent chat (any role)

```text
build-sina-command-panel.py          # unless ASF single SHIP pick
validate-anti-staleness-bundle-v1.sh # Worker/daemon only
validate-sourcea-e2e-full-v1.sh
validate-sourcea-e2e-standard-v1.sh
validate-e2e-fast-ladder-v1.sh      # Brain forbidden · Worker --require-idle only
```

### Forbidden patterns

- Chained shells: `cmd1 && cmd2 && …` combining two+ validators  
- `Await` > **90s** without founder-visible progress reply  
- Hub rebuild loop as “fix responsiveness” without ASF pick  
- Citing **blueprint v2/v3 DRAFT** as law (SSOT v3.1 wins)  
- **G7 `--heal`** without prior **`--scan`** receipt read in same session  

### Role limits

| Role | Max shell | Max reply before STOP | Allowed cheap proof |
|------|-----------|----------------------|---------------------|
| **brain** | 90s | 30s narrative | preflight · fcb FAST · factory_idle_gate |
| **maintainer** | 120s | one bounded SHIP pass | session gate · single validator per pick |
| **worker** | ladder policy | receipt + REGISTRY | `--require-idle` ladder max 1/turn |
| **any** | mirror sync | read receipt first | conduct gate JSON |

**Machine:** `python3 scripts/agentic_conduct_gate_v1.py --role <role> --json`

---

## 3. Read order gate (INCIDENT-027 class)

Before hub P0 copy or founder-facing status:

```
1. ~/.sina/live-founder-decision-form-v1.json
2. SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md
3. SINA_GOVERNANCE_ENTRY_LOCKED_v1.md
4. PROGRAM_PROGRESS.json
5. Hub projection (last · advisory)
```

Violating order = stale P0 / false “open forks” / wrong next_action.

---

## 4. G7 heal discipline

```bash
# Step 1 — always
python3 scripts/governance_self_heal_daemon_v1.py --scan --json
# Read ~/.sina/governance-self-heal-receipt-v1.json — confirm findings

# Step 2 — only if WARN/FAIL with heal_action
python3 scripts/governance_self_heal_daemon_v1.py --heal --json
# Compare before/after counts in receipt
```

**Never heal blind.**

---

## 5. Spine events (v2)

New event type: **`AGENT_SESSION_GATE`**

| Field | Value |
|-------|-------|
| `object_kind` | `system` |
| `object_id` | `agent_session_gate:<gate_id>` |
| `agent_id` | `maintainer` \| `brain` \| `worker` \| `cursor` |
| `payload` | `role`, `ok`, `conduct_warnings`, `mirror_hash8` |
| `gate` | `agent_session_gate_run_v1` |
| `proof` | `~/.sina/agent_session_gate_receipt_v1.json` |

Append on **every** session gate completion (pass or fail).

---

## 6. Session gate order (v2)

```
memory_mirror_sync → truth_bundle → rules_loop → conduct_gate → entry_gate(role) → spine_emit → receipt
```

**Receipt schema:** `agent-session-gate-receipt-v1.1` (backward compatible with v1 readers)

---

## 7. Cursor agent law (all chats)

1. Run session gate before substantive work.  
2. Read conduct block from receipt `conduct` field.  
3. On law ship: seven surfaces + `validate-law-supersession-surfaces-v1.sh`.  
4. On research: knowledge-library pipeline before chat-only synthesis.  
5. On STOP: `plan_revoked_v1.py` + cancel todos.  
6. Session close: `cursor_agent_self_audit.py session-close` on maintainer hub work.

**Rule file:** `.cursor/rules/agent-memory-mirror.mdc` (alwaysApply)

---

## 8. Verify

```bash
python3 scripts/agent_session_gate_run_v1.py --role any --json
bash scripts/validate-agentic-enforcement-stack-v2-v1.sh
bash scripts/validate-agent-memory-mirror-v1.sh
```

---

## 9. Supersession

| Prior | Status |
|-------|--------|
| `AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md` | **Retained** — L0/L1 unchanged; v2 adds L2–L6 |
| Chat-only conduct essays | **Void** — machine gates win |
| Validator marathon as progress | **Void** — INCIDENT-026 |

---

*End LOCKED v2*
