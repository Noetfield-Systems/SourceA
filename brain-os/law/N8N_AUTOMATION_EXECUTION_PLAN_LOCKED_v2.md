# n8n Automation — Execution Plan (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0 · **Locked:** 2026-06-14 · **Status:** LOCKED · **Implementation:** COMPLETE · **P0 operational:** COMPLETE  
**Canonical:** `~/Desktop/SourceA/N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md`  
**Law:** `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`  
**Companion:** `N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md` · `scripts/N8N_FOUNDER_RUNBOOK.md`  
**Supersedes:** `archive/attachments/N8N_WORKFLOW_120_STEP_PROMPT_PLAN_v1.md` (reference only)

---

## Executive summary

**Local glue layer** — not a second brain. n8n schedules and routes **receipts + alerts** between standalone apps:

| Surface | Port | Role |
|---------|------|------|
| **Mac Health Guard** | :13024 | Body + security truth, Cool Down, RAM live |
| **N8N Integration app** | :13026 | Founder dashboard — start n8n, read brief, ingest |
| **n8n engine** | :5678 | Cron + webhook glue |
| **Sina Command hub** | :13020 | **Quarantined** — warn-only |
| **Runtime** | :8000 | Optional — Telegram default |

**Build order:** Tier 0 → 1 → (2 ∥ 3) → 4 → 5 → 6. **All tier gates PASS** — see `~/.sina/n8n-receipts/FINAL_AUTOMATION_PASS_v2.json`.

---

## Active artifacts (in the repository)

| Artifact | Path |
|----------|------|
| Glue config | `~/.sina/n8n-glue-config-v1.json` |
| Receipts | `~/.sina/n8n-receipts/` |
| Glue runner | `scripts/n8n_glue_runner_v1.py` |
| Workflow manifest | `scripts/fixtures/n8n/workflow_manifest.json` (schema v5) |
| Workflow JSONs | `n8n/workflows/` + MonoRepo mirror |
| Tier validators | `scripts/validate-n8n-tier0-v1.sh` … `tier5` + `full-manifest` |
| Full suite | `scripts/validate-n8n.sh` |

---

## Tier model

```
TIER 0  Substrate          — PASS (tier0-pass.json)
TIER 1  Founder visibility — PASS (WF1 v2 + WF8)
TIER 2  Machine safety     — PASS (WF9, WF14, WF17)
TIER 3  Governance glue    — PASS (WF4, WF11, WF10)
TIER 4  Intelligence       — PASS (WF2, WF3)
TIER 5  Batch cadence      — PASS (WF5, WF6, WF7)
TIER 6  Extensions         — PASS (WF12–18 manifest)
```

**Parallel tracks after Tier 1:** Health (A) · Governance (B) · Intelligence (C) · Archive (D)

**OFF:** `sinaai-telegram-agents` — one listener law.

---

## Data flow

Apps emit events → n8n webhook/cron → `n8n_glue_runner_v1.py` → JSONL receipt → N8N Integration / Mac Health display.

**Never:** Cursor auto-send · prompt SSOT in n8n · hub as PASS/FAIL gate when quarantined.

---

## Unified receipt schema

`~/.sina/n8n-receipts/<track>/<workflow-id>.jsonl` — schema `n8n-glue-receipt-v1`.

---

## 110-step plan (reference)

Full step tables remain in this doc’s body for Cursor rounds. **Status:** Tiers 0–6 implemented 2026-06-14.

### TIER 0 — Substrate (Steps 1–15) — DONE

Steps 1–15: config, receipts, inventory, glue runner, quarantine-aware health_ping, validators.

### TIER 1 — Founder visibility (Steps 16–35) — DONE

WF1 v2, WF8 cooldown, Mac Health signal emit, tier1-pass.json.

### TIER 2 — Machine safety (Steps 36–50) — DONE

Queue sweeper, disk wire, CPU pause, governance-findings ingest.

### TIER 3 — Governance glue (Steps 51–68) — DONE

Governance fast, poison track, factory stuck (notify only).

### TIER 4 — Intelligence (Steps 69–82) — DONE

Product signal webhook, intelligence pipeline hub fallback.

### TIER 5 — Batch cadence (Steps 83–95) — DONE

Judge audit, thread scout, OpenRouter shadow.

### TIER 6 — Extensions (Steps 96–105) — DONE

Scoreboard sync, founder requests, SEMEJ bookend, backup archiver.

### TIER 7 — Operate (Steps 106–110) — ONGOING

Weekly ritual, monthly scout review, quarterly telegram audit.

---

## Workflow priority matrix

| Priority | WF | Tier | Status |
|----------|-----|------|--------|
| P0 | substrate + glue runner | 0 | **OPERATIONAL COMPLETE** |
| P0 | WF1 stack-health v2 | 1 | **OPERATIONAL COMPLETE** |
| P0 | WF8 mac-health-cooldown | 1 | **OPERATIONAL COMPLETE** |
| P1 | WF9, WF14, WF17 | 2 | validators PASS · crons OFF |
| P2 | WF4, WF11, WF10 | 3 |
| P3 | WF3, WF2 | 4 |
| P4 | WF5, WF6, WF7 | 5 |
| P5 | WF12–18 | 6 |
| **OFF** | telegram-agents | — |

---

## Founder action (no Terminal)

See **`N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md`**.

1. N8N Integration → Open n8n → Import `sinaai-stack-health-ping.json` → Execute once.
2. Mac Health → Cool Down or Brain heal once.
3. Confirm yellow/green in N8N Integration report (yellow OK when hub quarantined).

---

## Next Cursor prompt (operate / extend)

> Read `N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md` Tier 7. Run `bash scripts/validate-n8n.sh`. Report receipt paths and any cron the founder should enable in n8n UI.

---

## Paid n8n features — not needed

SSO/LDAP · Git sync · Environments · External Secrets UI · advanced log streaming.
