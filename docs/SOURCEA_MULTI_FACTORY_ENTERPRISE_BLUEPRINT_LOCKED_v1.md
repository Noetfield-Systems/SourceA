# SourceA Multi-Factory Enterprise Blueprint & Advisory — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T07:09:38Z · **Authority:** ASF SAVE TO  
**Path:** `docs/SOURCEA_MULTI_FACTORY_ENTERPRISE_BLUEPRINT_LOCKED_v1.md`  
**Machine SSOT aliases:** `data/multi-factory-enterprise-tree-advisory-v1.json` · `data/architecture-ledger-v1.json` · `data/SOURCEA_MULTI_FACTORY_ENTERPRISE_BLUEPRINT_LOCKED_v1.md`

---

## THE BIG PICTURE

SourceA is a **unified orchestration repository** running two strategic vectors:

1. **External — The Proof Layer for AI Agents** (Cursor marketplace · MCP receipts)
2. **Internal — Cloud video-ad factory** (brief → script → audio → approve → render → dispatch)

**Immutable split:**

| Plane | Role | Runs |
|-------|------|------|
| **Mac** | **Cockpit / control panel only** | Hub `:13020` · session gate · queue · approve · validators · RUN INBOX |
| **Cloud** | **Execution plane / auto-loops** | Supabase state machine · Edge workers · ElevenLabs · Fal · Vercel MCP SSE |

Law: `data/cursor-bootstrap-ledger-v1.json` → `mac_role: control_plane_only` · `cloud_role: execution_plane_headless`

**No rendering, training, or heavy multimedia on Mac.** Mac maps and governs; cloud executes on autopilot.

---

## PART 1 — EXTERNAL PRODUCT: CURSOR MARKETPLACE (PROOF LAYER)

### 1.1 Thesis

We do **not** replace MCP servers (GitHub, Linear, Vercel). We **prove** what they did: `PASS` · `FAIL` · `MOCK_ONLY` + receipt JSON.

**Partner line:** *We don't replace your MCP — we prove what your MCP did.*

### 1.2 Bundle (Card 1 only at launch)

```text
cursor-plugin/sourcea-forge-governance/   # 2 skills · 1 rule · marketplace manifest
packages/mcp-sourcea-verify/              # verify_run · factory_status · emit_receipt_readonly
cursor-plugin/.../MARKETPLACE_LISTING.md
```

**Category:** Agent Orchestration · **Do not** list VIRLUX / Noetfield / TrustField as separate cards initially.

### 1.3 Status (disk)

| Item | Status |
|------|--------|
| Disk publish | PASS · `receipts/card-1-sourcea-forge-governance-publish-v1.json` |
| npm `@sourcea/mcp-verify` | **NOT LIVE** — founder `npm login` + `bash scripts/npm_publish_mcp_chain_v1.sh` |
| Cursor marketplace submit | Founder |
| MCP registry | Founder |

---

## PART 2 — INTERNAL FACTORY: CLOUD VIDEO-AD ENGINE

### 2.1 Cloud-first orchestration

Local Python/TS in repo = **control-plane wiring + validators + cockpit simulators** until Supabase Edge is deployed. Production loop = **event-driven state machine in cloud**.

### 2.2 Deterministic spend order

```text
[1] Billing tier gate (Supabase profiles / fbe_billing_*)
         ↓
[2] BRIEF_ANALYSIS → LLM cloud → Zod script JSON
         ↓
[3] AUDIO_READY → ElevenLabs → Cloud Storage URL
         ↓
[4] HUMAN_APPROVAL_REQUIRED  ← LOOP STOPS (founder Hub /form)
         ↓
[5] APPROVED → Fal.ai rendering-bridge (paid — only after sign-off)
         ↓
[6] DISPATCHED → APNS / iOS client (Phase 2 StoreKit)
```

**Immutable rule:** Never call paid Fal.ai if state is `HUMAN_APPROVAL_REQUIRED`.

**Answer to Gemini (Fal vs StoreKit first):** Neither first — billing → orchestration → bridge → StoreKit.

### 2.3 Cloud auto-loop state table

| State | Trigger | Cloud action | Output |
|-------|---------|--------------|--------|
| `BRIEF_ANALYSIS` | New campaign row | Gemini / OEGCC → structured script | Zod-valid JSON in DB |
| `AUDIO_READY` | Script validated | ElevenLabs webhook → Storage upload | MP3 URL |
| `HUMAN_APPROVAL_REQUIRED` | Audio uploaded | **Suspend loop** — show draft in cockpit | Wait founder |
| `VIDEO_RENDERING` / `APPROVED` | Founder approve | Fal.ai bridge | MP4 on CDN |
| `DISPATCHED` | Render complete | APNS / client notify | Loop closed |

Types: `shared/types/campaign-v1.ts` · Demo: `data/video-ad-campaigns-v1/demo-campaign-v1.json`

### 2.4 Machine paths (pre-cloud deploy)

| Function | Path |
|----------|------|
| Orchestration sim | `scripts/video_ad_factory_orchestrate_v1.py` |
| ElevenLabs live wire | `scripts/film_elevenlabs_wire_v1.py` |
| Rendering bridge stub | `scripts/video_ad_rendering_bridge_v1.py` |
| Billing webhook stub | `scripts/fbe_billing_webhook_stub_v1.py` |
| Edge loop scaffold | `data/supabase-edge-loop-v1.json` |
| Chain validator | `bash scripts/validate-video-ad-factory-chain-v1.sh` |
| Gemini TS port spec | `data/video-ad-factory-gemini-port-spec-v1.json` |

---

## PART 3 — DATA SCHEMA (SUPABASE)

**SSOT SQL:** `data/supabase-migration-001-campaign-automations-v1.sql`

Tables: `profiles` · `campaign_automations` · `resource_logs`

Apply when WORK names Supabase project. Do not fork Gemini Bun monorepo.

---

## PART 4 — ARCHITECTURE LEDGER

**SSOT:** `data/architecture-ledger-v1.json` (epoch 2)

Integrations: ElevenLabs · Fal · Supabase · StoreKit (P2) · Vercel MCP SSE · OpenRouter/OEGCC (pending)

Campuses: SourceA · VIRLUX (internal engine, not marketplace card) · Noetfield · TrustField (Phase 2)

---

## PART 5 — VERIFICATION (cockpit probes)

Run on Mac **before** cloud push — not as production execution:

```bash
bash scripts/validate-video-ad-factory-chain-v1.sh
bash scripts/validate-cursor-bootstrap-v1.sh
python3 scripts/debug_e2e_governance_chain_v1.py
python3 scripts/agent_session_gate_run_v1.py --role any --json
```

Consolidation receipt: `data/chat-session-consolidation-receipt-v1.json`

---

## PART 6 — FOUNDER-ONLY REMAINING

1. `npm login` + publish Card 1 MCP  
2. Cursor marketplace + MCP registry submit  
3. Name Supabase project → `WORK: supabase-edge-loop` deploy  
4. W3 confirm-sent · OEGCC LLM hook  

---

## PART 7 — STRATEGIC RULES (no drift)

- **One marketplace card** at launch — Proof Layer only  
- **Market "Proof"** not "Governance" in buyer copy  
- **Consume** Linear · GitHub · Vercel · Supabase — partner, don't compete with Snyk/Aikido  
- **Mac cleanup Phase 1** = clean cockpit glass for Cursor context — not local render  
- **Changes** to flow or tier order require new epoch + validator receipt  

**End of LOCKED blueprint v1.**
