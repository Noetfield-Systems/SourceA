# Agent operating roles — ecosystem (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
| | |
|--|--|
| **Version** | `AGENT-ROLES-1.0-LOCKED` |
| **Locked** | 2026-06-04 |
| **Parent** | `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` |
| **Fleet monitor** | `AGENT_CONTROL_PANEL_SPEC_LOCKED_v1.md` |

---

## Role taxonomy (who does what)

| Role ID | Name | Plane | May write code? | Primary output |
|---------|------|-------|-----------------|----------------|
| `ROLE-ASF` | Founder | Law | Yes (when acting) | Locks, P0 pick, reversals |
| `ROLE-ARCHITECT` | Permanent Architect | Read-only | No | `ARCHITECT_REPORT.yaml` |
| `ROLE-ORCHESTRATOR` | SinaPromptOS dispatch | Automation | Via scripts | Day plan, repo dispatch |
| `ROLE-CURSOR-HQ` | Cursor HQ workspace (e.g. SinaaiDataBase shell) | Intelligence + cross-repo | Yes | Source A locks, fleet, SKU when threaded — see `UNDERSTANDING_ROLES_CURSOR_ECOSYSTEM_v1.md` |
| `ROLE-IMPLEMENTER` | Cursor Composer (single repo) | Delivery | Yes | Shipped diff + VERIFY block |
| `ROLE-WIRE` | AI Dev Bridge lane | Wire | Yes (agent/) | G1/G2/G3 evidence |
| `ROLE-PORTFOLIO` | Per-company delivery | Delivery | Yes (one repo) | Customer artifact |
| `ROLE-STRATEGY` | Advisor / GPT / investor narrative | Advisory | No | Memos, flywheel (→ ASF locks) |
| `ROLE-FLEET` | Agent Control Panel | Observability | Scanner only | `AGENT_FLEET_REGISTRY.json` |

**This chat agent** (Cursor in a workspace) defaults to **`ROLE-IMPLEMENTER`** unless ASF names another thread.

---

## Implementer responsibilities (upgraded v1)

### Must do every session

1. Read **command center** + run `update-program-progress.sh`
2. Confirm **one active thread** (`ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md`)
3. Ship **one primary outcome** (sub-steps OK if same outcome)
4. Append **VERIFY** block per `AGENT_OUTPUT_CONTRACT_v1.yaml`
5. Update **repo or Source A JSON** todos before end
6. **Never** conflate M8 (automation) with MP-* (MergePack revenue)

### Must not do

- Open new architecture without ASF
- Mix TrustField + MergePack + Participation HQ in one outcome
- Claim deploy/revenue without evidence (URL, KPI, payment id)
- Edit locked docs without `*-LOCKED` version bump + ASF

### Evidence duty (new — aligned with Evidence Flywheel)

When touching L1 utilities (MergePack, RunReceipt):

- Preserve **event types** and KPI trio semantics
- Report `GET /v1/kpi` or equivalent in VERIFY when relevant
- Referral/hooks changes → update `EVIDENCE_FACTORY_LOCKED.md` or hooks lock

---

## Authority (unchanged)

```text
SINA_OS_SSOT → thread LOCKED spec → repo LOCKED.md → chat memory (never)
```

---

## Session picker (opening line)

```text
Read ASF_PROGRAM_PROGRESS_COMMAND_CENTER_LOCKED_v1.md + run update-program-progress.sh.
Active thread: THREAD-_____. Role: ROLE-IMPLEMENTER.
```

---

**LOCKED.**
