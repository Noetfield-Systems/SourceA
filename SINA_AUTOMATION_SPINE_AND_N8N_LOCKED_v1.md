# Automation spine + n8n (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-04 · **Status:** LOCKED  
**Canonical:** `~/Desktop/SourceA/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`  
**Hub:** Connected Apps → **n8n** card · Actions → **Automation & n8n**

---

## One-line policy

> **Hub orchestrates founder · Prompt OS orchestrates Cursor repos · Runtime :8000 orchestrates Telegram · n8n glues external workflows only — never SSOT for law or prompts.**

---

## Two planes (do not merge)

| Plane | Owner | n8n role |
|-------|-------|----------|
| **PROMPT_PLANE** | SinaPromptOS + Cursor | **None** — no Cursor auto-send |
| **RUNTIME_PLANE** | SinaaiRuntime :8000 | **Optional** — second Telegram path only if built-in bot disabled |

**Phase 1:** Stability > automation. No 24×7 daemon. No auto-paste into Cursor.

---

## n8n in this OS

| Item | Value |
|------|--------|
| UI | http://127.0.0.1:5678 |
| Start (Mac) | Hub **Start n8n** or `scripts/founder-start-n8n.sh` |
| Starter workflow | `~/Desktop/SourceA/n8n/workflows/sinaai-stack-health-ping.json` |
| P0 gate | `~/.sina/n8n-receipts/health/p0-operational-pass.json` |
| P0 validator | `bash scripts/validate-n8n-p0-operational-v1.sh` |
| Test flow | Hub **Run n8n starter test** |
| Default Telegram | Built-in Runtime bot — **one listener only** |

---

## Starter test flow (locked steps)

1. Hub API alive  
2. Runtime `GET /health` on :8000 (warn if down)  
3. n8n `GET /` on :5678 (start n8n if down)  
4. Runtime `GET /api/v1/liaison/status`  
5. Report workflow import path + next founder steps  

---

## Never

- n8n as brain for SourceA / five-repo ranking  
- n8n in Noetfield **ship** runtime (archived L3)  
- Parallel Telegram listeners (n8n + built-in bot)  
- Commit `ops/private/sourceA/` or secrets to git  

**Authority:** Subordinate to `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` · `SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md`

**Active execution plan:** `N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md` · Founder card: `N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md` · Runbook: `scripts/N8N_FOUNDER_RUNBOOK.md`
