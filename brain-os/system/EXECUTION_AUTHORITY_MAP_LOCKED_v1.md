# Execution authority map (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF  
**Machine SSOT:** `brain-os/system/authority.yaml` — **read this file as data; this doc is the pointer**  
**Parent:** `GOVERNED_EXECUTION_OS_MASTER_LOCKED_v1.md`

---

## One sentence

> **ASF controls · Brain routes (execution_authority: true) · Workers build · Broker gates · Disk remembers.**

---

## Layer stack

| Layer | Role | execution_authority |
|-------|------|---------------------|
| **L0** | ASF + Hub | human override |
| **L1** | SourceA Brain (Execution Core) | **true** (pick · reconcile · handoff) |
| **L2** | Broker + validators | false (broker=yes mechanical) |
| **L3** | Workers (SourceA · portfolio site · headless CLI) | false (build only) |
| **L4** | Commercial · Governance · Research Acquisitor | false (advocate / research) |
| **L5** | Old Brain broker · GPT/Claude | false (compare / EXTERNAL_CRITIC) |
| **L6** | RESEARCH mirror · Disk SSOT | false (remembers · never decides) |

---

## Runtime pointers (state — not prose)

| File | Purpose | Writers |
|------|---------|---------|
| `~/.sina/next-execution-pointer-v1.json` | **What runs next** | Brain pick · orchestrator · `sync_next_execution_pointer_v1.py` |
| `~/.sina/runtime/execution.json` | **What runs now** | orchestrator · autoloop · broker |
| `~/.sina/active-execution-rail-v1.json` | Active rail (A/B/manual) | ASF / Brain |
| `~/.sina/research-root/filtered/execution_core.digest.yaml` | Brain research intake | `research_root_sync.py` |

---

## Nuances (keep saying)

1. **Brain dual-mode** — narrator by default; executor only on `activate loop` / `execute turn` (`BRAIN_CORE_EXECUTOR_LOCKED_v1.md`).
2. **Execution authority ≠ implementation** — Brain must not become a second Worker.
3. **Headless `agent -p -f`** — same Worker class under one-sa / broker law.
4. **Portfolio site workers** — scoped builders; not Execution Core unless Brain routes.
5. **Research** — always `execution_authority: false`; Brain reads filtered digest only.

---

## Golden law

Specialists advocate · Execution Core decides · Workers act · Disk remembers · ASF controls

---

## Sync commands

```bash
python3 scripts/sync_next_execution_pointer_v1.py --json
bash scripts/validate-authority-convergence-v1.sh
```

---

## Related

| Doc | Path |
|-----|------|
| **Runtime verification (unified lock)** | `AUTHORITY_RUNTIME_VERIFICATION_LOCKED_v1.md` |
| P1 enforcement hooks | `GOVERNANCE_P1_LOOPS_LOCKED_v1.md` |
| Event contract | `EVENT_CONTRACT.yaml` |
| Governed OS master | `GOVERNED_EXECUTION_OS_MASTER_LOCKED_v1.md` |
| Workers registry | `RESEARCH/_GOVERNANCE/WORKERS_REGISTRY.yaml` |
| Governance synthesis | `governance_goal_specialist-20260608-017` in RESEARCH |

---

*End EXECUTION_AUTHORITY_MAP_LOCKED_v1*
