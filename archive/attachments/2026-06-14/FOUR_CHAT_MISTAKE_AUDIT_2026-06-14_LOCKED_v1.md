# Four-chat mistake audit + permanent fixes (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order · Maintainer 2 executor  
**Chats:** Brain `58148ac9` · Commercial `6245d9dd` · Governance `e54ddfa8` · Maintainer `74f5ccab` · Worker `fd67502f`  
**Prior:** M1–M16 (`GOVERNANCE_AUTOHEAL_CHAT_AUDIT_SUMMARY_2026-06-14_LOCKED_v1.md`)

---

## Auto-heal (this session)

| Step | Result |
|------|--------|
| G7 launchd `com.sourcea.g7-governance-self-heal` | **loaded** (hourly) |
| `governance_self_heal_daemon_v1.py --scan` | **PASS** · 0 FAIL |
| `governance_self_heal_daemon_v1.py --heal` | **PASS** · inbox_truth ok |
| `governance_center_run_v1.py --tier fast` | **PASS** |
| Worker inbox drift | **aligned** · head **sa-0101** pos 1/156 |

---

## Mistake inventory (all chats)

### Already fixed (M1–M16) — do not redo

| Range | Theme | Permanent gate |
|-------|-------|----------------|
| M1–M10 | Prompt feed · AUTO-RUN · Hub daily | `000-dead-law-stubs` · mirror F09–F13 |
| M11 | Inbox stuck sa-0951 | `activate-run-inbox-phase-strict-v1.py` |
| M12 | Stale run-inbox-routing | Activator rewrite on queue rebuild |
| M13 | Chat ID swap (claimed) | **Regressed → M17** |
| M14–M16 | Queue→inbox sync · drift report | `build-phase-strict-queue` · `governance_center_run` |

### New / regressed (M17–M24) — fixed this session

| # | Mistake | Chat | Sev | Permanent fix | Status |
|---|---------|------|-----|---------------|--------|
| **M17** | `governance-chat-context-v1.json` labeled Commercial as Brain and Brain as Worker | Disk SSOT | **P0** | Corrected `role_map` + `validate-governance-chat-context-v1.sh` | **FIXED** |
| **M18** | Commercial told founder `python3 live_founder_decision_form` | Commercial | P1 | Mirror **F14** + close-line gate | **FIXED** |
| **M19** | Commercial `bash verify-vault-unified` one-liner | Commercial | P2 | Mirror **F17** | **FIXED** |
| **M20** | "Refresh Hub Track" as founder step | Commercial | P1 | Mirror **F15** | **FIXED** |
| **M21** | Brain routed founder to legacy **Backlog → Agent reports** | Brain | P1 | Mirror **F16** | **FIXED** |
| **M22** | Brain executed Maintainer SHIP (file edits) | Brain | P1 | **Law** `MANDATORY_BRAIN_CHAT` — route only; session gate | **BOUND** (law exists) |
| **M23** | Maintainer cited stale queue **sa-0798** after heal to **sa-0101** | Maintainer | P2 | Worker Hub reads live API only | **BOUND** |
| **M24** | Governance specialist shipped Worker/Maintainer code | Gov | P1 | **Law** — receipts only | **BOUND** (law exists) |

### Archaeology only (cannot edit transcripts)

| Pattern | Count (historical) | Treatment |
|---------|-------------------|-----------|
| Prompt feed / auto-send | 100+ lines | Blocked by F01–F13 |
| Hub AUTO-RUN / Rail A | 100+ lines | PAST_STALE_ONLY |
| Hub rebuild / phase-s8 | 80+ lines | Factory FREEZE · no_hub |
| Terminal / curl to founder | 18+ lines | F14–F18 · no-Terminal law |

---

## Disk truth after heal

| Signal | Value |
|--------|-------|
| Queue head | **sa-0101** CHECK · pos **1/156** |
| Worker inbox | **pending** · meta **sa-0101** · **aligned** |
| Factory | **FREEZE** |
| Form open | **2** · `Q-GOV-FAST-WIRE-v1` · `Q-CHANGE-QUORUM-v1` |
| Hub daily | **Super Fast Hub** `http://127.0.0.1:13020/` |
| Legacy hub | `/legacy/` archive only |

---

## Founder P0 (live)

1. **M1 Canvas** — answer **2 open PICKs** (governance fast wire · change quorum)
2. **Super Fast Hub** → **Safety check** (green receipt)
3. **Commercial 11.x** — not blocked by hub work

---

## Files shipped (permanent)

1. `~/.sina/governance-chat-context-v1.json` — corrected role map
2. `scripts/validate-governance-chat-context-v1.sh`
3. `scripts/agent_memory_mirror_v1.py` — F14–F18
4. `scripts/validate-anti-staleness-bundle-v1.sh` — wired chat-context validator

---

*End FOUR_CHAT_MISTAKE_AUDIT_2026-06-14_LOCKED_v1*
