# Refinement unified — Agent · Machine · Founder (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md`  
**Agent pipelines:** `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md`  
**Machine pipelines:** `MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md`  
**Test ladder:** `SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md`  
**Unified router:** `scripts/refinement_unified_router_v1.py`  
**Registry:** `~/.sina/refinement-unified-registry-v1.json`

---

## One sentence

> **Everyone refines on a tier — agents learn (orientation) · heal (hospital) · prove (maze); machines map (calibrate) · tune (tune) · forge (forge); founders PICK cadence on H1 — same philosophy, separate pipelines, one unified receipt when both need care.**

---

## Why refinement is universal

| Who | Drift symptom | Tier 1 (short) | Tier 2 (medium) | Tier 3 (long · worst) |
|-----|---------------|----------------|-------------------|------------------------|
| **New agent / AI** | Does not know map | **orientation** | — | — |
| **Working agent** | Forgot role · thin context | (cert required) | **hospital** | **maze** if critical |
| **New maintainer / pipeline** | Does not know machines | **calibrate** | — | — |
| **Running factory** | Stale receipts · hub drift | (cert required) | **tune** | **forge** if critical / pre-ship |
| **Founder (you)** | Decisions in chat | H1 daily | Form PICK | H2 weekly · strict monthly |

**Rule:** Tier 1 before Tier 2. Tier 3 only on escalation or ship — never scheduled for healthy systems.

---

## Unified architecture

```text
                         ASF (one word)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
        AGENT REFINE                    MACHINE REFINE
    orientation · hospital · maze    calibrate · tune · forge
              │                               │
              ▼                               ▼
         agent receipts                  machine receipts
              │                               │
              └───────────────┬───────────────┘
                              ▼
              refinement-unified-receipt-v1.json
              (when both run: agent hospital + machine tune)
                              │
                              ▼
                    Factory · H1 · H2 · W1/W2/W3
```

---

## Trigger words (founder)

| Say | Domain | Pipeline | When |
|-----|--------|----------|------|
| **orientation** | Agent | Tier 1 | Every new Cursor / raw AI |
| **hospital** | Agent | Tier 2 | Working agent drift |
| **maze** | Agent | Tier 3 | Sick agent · critical · repeat incident |
| **calibrate** | Machine | Tier 1 | New pipeline work · new maintainer session |
| **tune** | Machine | Tier 2 | Daily/3day machine health |
| **forge** | Machine | Tier 3 | Upgrade ship · tune escalation · weekly proof |

**Both at once (example):** agent drift + machine stale after incident:

```bash
python3 scripts/refinement_unified_router_v1.py both hospital tune --role worker --json
```

---

## Test + upgrade as one system (not two documents)

| Phase | Agent | Machine | Shared disk |
|-------|-------|---------|-------------|
| **Map** | orientation reading pack | calibrate reading pack | ecosystem catalog |
| **Routine health** | hospital | tune → `machine_test_ladder_run_v1.py` | two-hub · governance · agentic |
| **Full proof** | maze passport | forge passport | find_critical_bugs · baseline before/after |
| **Upgrade plan** | Brain closeout | UP-* board + baseline | h2-pending-registry |

**Upgrade loop (machine + agent):**

1. **calibrate** (or orientation for agent-only)
2. **Baseline** — `machine_upgrade_baseline_v1.py --tag before --upgrade-id UP-XX`
3. Contract → validator → code → receipt → H1 line or H2 table
4. **forge** (or maze if agent conduct broken)
5. **Baseline after** — prove delta · W1/W2/W3 cited in PROVEN lines
6. Re-run **tune** daily tier — must stay green

---

## Escalation (machine decides — same as agent H8)

| Check | Agent path | Machine path |
|-------|------------|--------------|
| `critical_count > 0` | hospital → **maze** | tune → **forge** |
| Quarantine file | `agent-maze-quarantine-v1.json` | `machine-forge-quarantine-v1.json` |
| Exit | maze passport | forge passport |

---

## Founder vs agents

| You | Agents |
|-----|--------|
| H1 daily · Safety · Form PICK | Run tune daily · hospital weekly |
| Say one trigger word | Execute pipeline · write receipt |
| Judge W1/W2/W3 | calibrate before new machine work · forge before ship |
| Never Terminal | `refinement_unified_router_v1.py` when both need care |

---

## Validators

```bash
bash scripts/validate-agent-three-pipelines-v1.sh
bash scripts/validate-machine-three-pipelines-v1.sh
bash scripts/validate-machine-test-ladder-v1.sh
```

---

*End REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1*
