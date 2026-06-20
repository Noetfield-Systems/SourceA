---
name: s10-eternal-self-heal
description: >-
  S10 eternal rejuvenation loop — 100 audit prompts, 10/day machine schedule,
  disk-truth self-heal, validator hardening, skills freshness, deep E2E critique.
  Use when auditing system health, eternal loops, self-healing, monitor/hub/inbox
  drift, or maintaining agent-skills after incidents.
disable-model-invocation: true
---

# S10 eternal self-heal (meta-phase)

**Law:** `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md`  
**Manifest:** `~/.sina/s10-eternal-manifest-v1.json` (100 prompts · 10 packs)  
**Receipt:** `~/.sina/s10-eternal-receipt-v1.json` + `s10-eternal-history.jsonl`

## Two lanes (never invert)

| Lane | SSOT | Role |
|------|------|------|
| Factory drain (s0–s9) | `run-inbox-disk-truth-v1.json` | `run inbox` execution |
| S10 eternal (s10) | `s10-eternal-manifest-v1.json` | Audit · heal · skills · E2E |

Prompt feed 10-batch = **advisory only**. S10 = **machine audit SSOT**.

## Daily loop

```text
detect → classify → remediate → harden → verify → record → skills_patch
```

**Pack rotation:** `pack = (day_of_year % 10) + 1` → 10 prompts/day  
**Weekly:** Sunday UTC — all 100 (`--full`)

## Commands (any directory — use wrappers)

```bash
~/.sina/bin/s10-eternal-daily          # today's 10 prompts
~/.sina/bin/s10-eternal-validate       # gate check
~/.sina/bin/s10-eternal-full           # all 100 (weekly)
```

Repo-relative (only if `cd ~/Desktop/SourceA` first):

```bash
python3 scripts/s10_eternal_audit_loop_v1.py --daily --json
python3 scripts/s10_eternal_audit_loop_v1.py --full --json
bash scripts/validate-s10-eternal-loop-v1.sh
```

## Auto-heal scope (script-owned only)

- `monitor_live_sync` refresh
- `run_inbox_disk_truth` patch / DISK TRUTH block
- `sync-cursor-agent-skills.sh`
- `build-phase-strict-queue-v1.py`
- governance-events + history touch

**Not auto-healed:** hub UI, FREEZE buttons, dual-pick — file agent-review / maintainer lane.

## 10 packs

| Pack | Domain |
|------|--------|
| P1 | Disk truth wire (monitor · inbox · queue) |
| P2 | Self-heal SH-01..10 |
| P3 | Run inbox E2E |
| P4 | Skills MD + registry sync |
| P5 | Validator chain |
| P6 | Hub real-time gaps |
| P7 | Governance + incidents |
| P8 | Phase-strict queue |
| P9 | Deep critique / laziness |
| P10 | Machine enforcement (launchd · sync) |

## Founder communication (separate topic)

S10 ≠ bash law. See `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md`.  
S10 default: headless receipt on disk — not founder Terminal.

## When to invoke

- Session start: WARN if S10 receipt >26h stale
- After incidents (monitor scroll, dual-pick, hub cache)
- Maintainer ecosystem safety pass
- Before claiming "system fixed" — S10 FAILs mean **not fixed**

## Maintainer sync checklist

1. `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md`
2. `~/.sina/s10-eternal-manifest-v1.json`
3. `scripts/s10_eternal_audit_loop_v1.py`
4. This SKILL.md
5. `validate-s10-eternal-loop-v1.sh`
6. `com.sourcea.s10-eternal-audit` launchd

*End s10-eternal-self-heal*
