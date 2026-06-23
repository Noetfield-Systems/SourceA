# SourceA — Cursor cost intelligence & local context routing (LOCKED v1)

**Version:** 1.0.0 · **Saved:** 2026-06-21T19:46:56Z · **Authority:** ASF SAVE + advisor wire  
**Path:** `brain-os/law/enforcement/SOURCEA_CURSOR_COST_INTELLIGENCE_ROUTING_LOCKED_v1.md`  
**Machine:** `data/cursor-cost-intelligence-routing-v1.json`  
**Cursor rule:** `.cursor/rules/045-cursor-cost-intelligence-routing-v1.mdc`  
**Pairs with:** `docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md` (cloud/infra ROI) · `brain-os/law/SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` (agent roles)

---

## 0. One sentence (law)

> **MacBook heat and Cursor token burn are local IDE problems — fix with bounded paths, `.cursorignore`, eight always-on rules, Auto/Composer pools, and cloud execution; never rehydrate the whole monorepo every turn.**

---

## 1. What burns tokens & CPU locally (Cursor rehydration)

| Trigger | Local effect | Fix |
|---------|--------------|-----|
| **40+ `alwaysApply: true` rules** | Full rule stack injected every turn | **8 critical rules only** — rest `@` or globs |
| **Max Mode ON** | Full context window · 1.2× API multiplier | Off by default · ship-window only |
| **Named frontier model** (Opus, GPT-5, …) | Leaves Auto+Composer pool → **$20 API pool** | Auto → Composer → API (last) |
| **Unbounded agent search** | Grep/read entire tree | Bounded `WORK:` / `EDIT ALLOWED:` + path |
| **Huge uncommitted diff** | Glass sidebar · renderer CPU | Commit/stash · close idle agent threads |
| **Heavy folders not ignored** | Index + context tax | `.cursorignore` (see §3) |
| **Validator marathons on Mac** | CPU + chat tokens | Read `~/.sina/*-receipt*.json` · INCIDENT-039 |

**Mac Law:** Mac = control panel only. Cloud/API/Railway executes factory body.

---

## 2. Cursor Pro — two pools (Auto mode daily path)

| Pool | Pro ($20/mo) | Draws when |
|------|--------------|------------|
| **Auto + Composer** | Generous included (dashboard = truth) | **Auto**, **Composer Fast / 1.5 / 2.5** |
| **API** | $20 at provider rates | **Manually selected** named models |

**Not unlimited.** Track both pools at [cursor.com/dashboard](https://cursor.com/dashboard).

### Routing (Cursor IDE — internal build)

```text
DEFAULT      → Auto
STUCK BUILD  → Composer 1.5/2.5 (same pool as Auto)
HARD ARCH    → Named model + Max Mode (API pool · time-boxed)
NEVER        → Opus/GPT-5 for receipt reads · hub copy · routine sa
```

### Role → model (SourceA)

| Role | Cursor choice | Job |
|------|---------------|-----|
| **Brain** | Auto | Route · pick · handoff · **no sa implement** |
| **Worker** | Auto → Composer | One bounded `sa-*` · files in scope |
| **Ship proof / fork** | API pool + Max | Architecture · security · complex refactor |
| **Volume research** | **Cloud** OpenRouter (Groq/Flash) | Not Cursor meter |

---

## 3. Local disk map — where new files go (`~/Desktop/SourceA/`)

Bounded paths stop context rehydration from swallowing the monorepo.

| If the file is… | Save under | Cursor rule |
|-----------------|------------|---------------|
| **Executable app / factory / product code** | `apps/<name>/` | Isolated factory · bootstrap ledger |
| **Governance · agent law · Brain SSOT** | `brain-os/` | Canonical law tree only |
| **Validators · hub · gates · executors** | `scripts/` | Machine truth |
| **Heavy raw data · logs · JSON/CSV outputs** | `receipts/` | **Ignored** — zero token cost |
| **Experiments · disposable research** | `labs/` | labs-sandbox tier · not spine |
| **Shared contracts** | `shared/types/` | Zod SSOT |
| **Product docs (non-law)** | `docs/` | Router/index · not mega-paste |
| **UI surfaces** | `agent-control-panel/` or app UI path | UI FIRST CHECK when editing |

**Founder order template:**

```text
WORK: sa-XXXX — build <what> and save ONLY under apps/my-tool-v1/.
Do not read or edit brain-os/, archive/, plan-registry/, or receipts/.
```

---

## 4. `.cursorignore` — mandatory heavy paths

Already ignored: `receipts/`, `archive/`, `*.log`, `node_modules/`, media blobs.

Also ignore for token hygiene (see `data/cursor-cost-intelligence-routing-v1.json`):

- `brain-os/plan-registry/sourcea--1000/prompts/`
- `brain-os/plan-registry/sourcea-1000/prompts/` (Worker loads one sa from inbox JSON)
- `infra/cleanup/secret-scan-report.txt`
- Large generated registries unless task explicitly names them

---

## 5. AlwaysApply slaughter — eight critical rules only

**Problem:** 35+ `alwaysApply: true` rules rehydrate full governance stack every Enter key.

**Law:** Keep **exactly eight** always-on Cursor rules. All others: `alwaysApply: false` — load via `@rule`, `@skill`, or path **globs**.

| # | Rule file | Why always on |
|---|-----------|---------------|
| 1 | `000-entry-gate.mdc` | Session · role entry |
| 2 | `000-cross-lane-edit-forbidden.mdc` | SAVE · WORK · EDIT ALLOWED |
| 3 | `000-workspace-lock.mdc` | Workspace SSOT |
| 4 | `mac-control-plane.mdc` | Mac observes · cloud executes |
| 5 | `034-mac-no-validator-stuck-red-flag.mdc` | INCIDENT-039 P0 |
| 6 | `agent-founder-intent-first.mdc` | Understand founder first |
| 7 | `agent-disk-live-wire-first.mdc` | Receipts · factory_now_line |
| 8 | `045-cursor-cost-intelligence-routing-v1.mdc` | This law · paths · pools |

**Demoted rules** (examples — load on demand):

- UI upgrade / form supremacy → **globs** on UI paths only  
- Mac Law universal wire · governance zero-drift → session gate receipt + `@` when needed  
- Portfolio account · Supabase tiers → `@044` when infra work  
- Market analog · comprehension loop → `@` when topic matches  

**Validator:** `bash scripts/validate-cursor-alwaysapply-cap-v1.sh`

---

## 6. Agent structure (cost-aware)

```text
L0   ASF + Hub (:13020) — decisions · form picks
L0.5 Machine pipeline — Python receipts (not a chat)
L1   Brain → Gov → Commercial → Brief — route only
L2   Worker → Research → Maintainer — one sa-* build
L3   Portfolio repos — TrustField · Noetfield · Forge
```

**Token rule:** Brain chat **<30s** · one light shell **≤90s** · Worker owns implementation · cloud owns proof/E2E.

---

## 7. Cloud factory stack (product runtime — not Cursor)

End-customer and heavy jobs run **outside** Cursor:

| Layer | Tool |
|-------|------|
| Orchestration | n8n · Trigger.dev · Railway FBE |
| Router | OpenRouter / LiteLLM |
| Data | Supabase (`portfolio-spine` vs `labs-sandbox`) |
| Traces | Langfuse |
| Rate limit | Upstash |
| Types | `shared/types/` Zod |

**Leader chain (cloud):** DeepSeek R1 free → Gemini Flash → Llama 70B free → GPT-4o  
**Worker chain (cloud):** Groq 8B → Flash Lite → Cerebras → OR `:free`  
**Batch:** Mistral small only

See `docs/SOURCEA_TIER_PRIORITY_COST_INTELLIGENCE_POLICY_LOCKED_v1.md` for infra ROI.

---

## 8. Task tier routing (T0–T4)

| Tier | Examples | Where | Model |
|------|----------|-------|-------|
| T0 | Read receipt · route | Cursor Brain | Auto |
| T1 | One file · one sa | Cursor Worker | Auto → Composer |
| T2 | Multi-file feature | Cloud worker bay | Flash / Groq |
| T3 | Architecture · security | Cursor API or cloud leader | Sonnet/Opus class |
| T4 | CI · E2E proof | Railway CI | No LLM / lint only |

---

## 9. Golden cost commands

```bash
# Session (once per chat — not every turn)
python3 scripts/agent_session_gate_run_v1.py --role any --json

# Validate alwaysApply cap (maintainer / ship window)
bash scripts/validate-cursor-alwaysapply-cap-v1.sh

# Machine routing line
python3 scripts/cursor_cost_intelligence_routing_v1.py --json
```

**Surfaces line:** `cursor_cost_intelligence_line` on `~/.sina/agent-live-surfaces-v1.json` after wire sync.

---

*End CURSOR COST INTELLIGENCE ROUTING v1*
