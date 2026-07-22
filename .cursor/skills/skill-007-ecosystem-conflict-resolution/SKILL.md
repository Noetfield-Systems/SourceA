---
name: skill-007-ecosystem-conflict-resolution
description: Auto conflict resolution when ecosystem rules disagree — run before first disk edit. All SourceA ecosystem agents.
disable-model-invocation: true
---

# SKILL-007 — Ecosystem auto conflict resolution

**When:** Any time two or more rules, skills, cursor rules, or founder laws disagree — **before** first disk edit.

**Authority:** R-010 (ecosystem) · INCIDENT-010 · INCIDENT-011 · `SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md`  
**Ported from:** Noetfield PR #34 · `Noetfield-All-Documents/Noetfield/.cursor/skills/SKILL-007-auto-conflict-resolution.md`

---

## Precedence ladder (highest wins)

| Tier | Source | Examples |
|------|--------|----------|
| **T0** | Founder **current message** explicit order | `SAVE TO:`, registry-resolvable `SAVE/LOCK/FILE`, `EDIT ALLOWED:` + `ACTION:`, `ASF:`, `WORK: sa-0010`, bounded implement |
| **T1** | Hard permission / ask-first | `001-founder-verbs` · SAVE/WORK/EDIT ALLOWED · cross-lane guard |
| **T2** | Open **P0/P1 incidents** | INCIDENT-010/011 · CIR-COSPRO · compendium Part A |
| **T3** | `execution_authority: false` | Research · advise · Brain read-only chats |
| **T4** | Bounded **workflow bundles** (only after T0) | RESEARCH 4-step save · Worker INBOX · Product `npm run check` scope |
| **T5** | Convenience / backlog | `plan.json`, ship-first, mandatory register paste, prior session — **never self-start** |

**Golden resolver:** *If ship-first or “mandatory register/sync” says act now but T1 says ask/permission → **T1 wins** until T0 founder order.*

---

## Auto-resolve algorithm

```
ON session start OR before first disk mutation:
  1. LOAD .cursor/agent-memory/ECOSYSTEM_HARD_RULES.yaml + open incidents
  2. PARSE founder message for T0 (intent + evidence in same message)
  3. IF workflow/mandatory paste says implement AND T0 missing:
       CONFLICT → step 5
  4. IF T0 is pathless SAVE/LOCK/FILE:
       RUN scripts/agent_filing_registry_gate_v1.py resolve --json
       IF ok:true → use route_id/path/next_steps; never ask exact path
       IF REGISTRY_NO_MATCH/AMBIGUOUS → ask category/scope, not exact path
  5. IF T0 present AND bounded:
       PROCEED inside bundle only (SKILL-006 already satisfied)
  6. CONFLICT HANDLER:
       a. Name Rule A vs Rule B (one line each)
       b. State winner (T0–T5)
       c. Propose A/B/C
       d. ASK founder — ZERO disk edits
  6. Session end: note if conflict occurred
```

---

## Known conflict pairs (ecosystem — pre-resolved)

| Rule A | Rule B | Winner | Allowed path |
|--------|--------|--------|--------------|
| RESEARCH SAVE LOCK 4-step paste | SAVE guard (INCIDENT-010) | **INCIDENT-010** | Full 4-step **only** when founder orders with `ASF:` or explicit save bundle |
| Bare **save** / save report | `001-founder-verbs` intent+evidence | **001-founder-verbs + filing registry** | Run filing registry; ask category only on `REGISTRY_NO_MATCH` / `REGISTRY_AMBIGUOUS`; never ask exact path when resolved |
| **REWRITE** / report / golden suggestion | Any disk write | **REWRITE = chat** (INCIDENT-011) | Chat only until `SAVE TO:` |
| Research lane B scope | Product SSOT (`AGENTS`, SSOT, roadmap) | **Lane ownership** | Refuse unless `EDIT ALLOWED` |
| `research_root_sync` register/sync | Explicit founder order | **T0 required** | No auto-register from refresh scripts alone |
| Worker INBOX / `sa-*` WORK | Cross-lane Brain/SSOT path | **WORK scope only** | `cross_lane_edit_guard_v1.py` |
| Brain chat | Worker execute prompt | **Brain REFUSE** (INCIDENT-003b) | Route to Worker chat |
| **agent-memory-mirror pre-ship** (`validate-law-supersession-surfaces-v1.sh`) | **INCIDENT-039 Mac founder session** | **INCIDENT-039** | Pre-ship text scan only · read receipts · reply <30s · no validate stack on Mac |
| **Daily duty W1–W10 check cart** | **INCIDENT-039 Mac founder session** | **INCIDENT-039** | Defer cart to cloud CI or ASF ship window — not pre-reply marathon |
| Noetfield ship-first / plan.json | Ask-first (SKILL-006) | **SKILL-006** | T0 ship order first |
| Mandatory SourceA file missing on disk | Any implement | **Block** (R-009 pattern) | Sync or paste; no pseudo-ACK |
| TrustField / wrong portfolio repo | Any rule | **Scope gate** | STOP always |

---

## T0 triggers (founder permission examples)

| Founder says | Bounded bundle |
|--------------|----------------|
| `SAVE TO: <path>` | One new file at path → STOP |
| `SAVE` / `SAVE AND LOCK` / `LOCK` / `FILE` with no path | Run filing registry → use `route_id` + `path` + `next_steps[]` if resolved |
| `EDIT ALLOWED: <path>` + `ACTION:` | That path/action only |
| `ASF: <phrase>` | Only what phrase authorizes |
| `WORK: sa-XXXX` / bound INBOX | Worker scope only |
| `yes` / `1` / `B` after agent ASK | Only the approved option |
| `implement: auto conflict rule` | SourceA `.cursor/skills/` + rules for SKILL-007 only |

**Not T0:** prior “save it”, RESEARCH mandatory paste alone, `plan.json`, QUICK_PICK, ship-first rule alone, summarized context.

---

## Agent output template (on conflict)

```markdown
**RULE CONFLICT** — SKILL-007 ecosystem

| Rule A | Rule B |
|--------|--------|
| <short> | <short> |

**Winner:** <T0–T5 + law id>

**I will not edit disk until you choose:**
- A) Advise only
- B) <bounded option>
- C) <alternative>

Your next move?
```

---

## Integration

| Asset | Role |
|-------|------|
| SKILL-006 | Ask step (always) |
| **SKILL-007** | This — on conflict |
| `000-cross-lane-edit-forbidden.mdc` | SAVE · WORK · EDIT ALLOWED |
| `001-founder-verbs-rewrite-save-asf-mandatory.mdc` | Zero disk without intent+evidence |
| `ecosystem-rule-conflict-resolution.mdc` | alwaysApply pointer |
| `ECOSYSTEM_HARD_RULES.yaml` | R-007–R-010 memory snippet |

---

**END**
