# Forge Factory — Three Offers + Existing-Chain Flows (LOCKED)

**Saved:** 2026-06-25 · **UTC:** 2026-06-25T04:30:00Z  
**Engine (canonical):** FBE/Railway Forge Runtime + governance v4 + receipts — **extend by paid demand only**  
**Rule:** No multi-tenant IDE · no Redis kernel · no v6/v7/v8 product work until a paying job requires it

---

## Shared engine (all three offers)

```
Intake (web/email/scope call)
  → Scope lock (one bounded job · written DONE/VERIFY)
  → Governance gate (forge_governance_kernel_v1 · ALLOW/BLOCK)
  → Execution body (Railway FBE · NOT Mac factory)
  → VALIDATE + receipt (artifact · evidence · decision)
  → Client delivery (output + replayable proof)
```

| Layer | On disk today |
|-------|----------------|
| Motor | `scripts/hub_cloud_forge_run_proceed_v1.py` · `scripts/cloud_auto_runtime_v1.py` · Railway `sourcea-fbe-runner-production.up.railway.app` |
| Governance | `scripts/forge_governance_kernel_v1.py` (v4) · PROVE: `scripts/living_system_chain_validate_v1.py` |
| Founder desk (internal) | Forge Terminal Connect `:13029` · Mac control plane only |
| Public human surface | https://sourcea.app/forge/terminal · https://sourcea.app/sandbox · https://sourcea.app/offer |
| Cloud dispatch | Cloud Workers `:13027` · Cloudflare cron → auto-tick |

**Mac:** observe · scope · deliver — **never** the execution body for client jobs.

---

# 1. Specialist — 48h MVP (sell first)

## One-page offer (buyer-facing)

**Headline:** We ship your 48-hour MVP — scoped, governed, with proof you can show stakeholders.

**You get**
- One bounded outcome (landing + form, intake funnel, or single workflow — agreed in writing)
- Fixed scope doc: GOAL · DONE · VERIFY · IF BLOCKED
- Deliverable on your stack or ours (Cloudflare Pages / Supabase / Railway — scoped at kickoff)
- **Proof pack:** what ran, what passed, what shipped (shareable on a client call)

**You don’t get**
- Open-ended “build whatever” agent hours
- A self-serve IDE login (that’s later)
- Tier-1 IDE replacement — we ship the **outcome**, not a coding tool

**Timeline:** 48–72h from signed scope (business days)  
**Price:** Quote on scope call — bands on https://sourcea.app/offer (setup + optional retainer)  
**Start:** https://sourcea.app/sandbox (free intake) or https://cal.com/sourcea/proof-demo  
**Contact:** contact@sourcea.app · proof@sourcea.app

**Why us vs Cursor/Lovable alone:** They generate. We **scope, gate, run, and receipt** — so you can sell or renew on proof, not trust-me chat.

---

## Single-client flow (existing chain)

| Step | Who | Action | System |
|------|-----|--------|--------|
| 1 | Prospect | Submits job | https://sourcea.app/sandbox → `scripts/sourcea_mvp_intake_submit_v1.py` / Cloudflare intake worker |
| 2 | Founder | 15-min scope call | Lock one page in writing: deliverable · stack · DONE · VERIFY |
| 3 | Founder | Creates work order | Registry row or CLOUD-SEC-style plan · maps to `portfolio__forge_dispatch_v1` lane |
| 4 | Cloud | Executes body | Railway FBE `proceed_on_cloud` · PLAN→BUILD→VALIDATE→RECEIPT via `cloud_forge_seed_v1` |
| 5 | Gate | PROVE + contract | `living_system_chain_validate_v1` · halt if red |
| 6 | Founder | QA + ship | Deploy via `publish_sourcea_landing_v1.py` or client repo · Pages/Railway |
| 7 | Client | Receives | Live URL + proof JSON/PDF + 15-min walkthrough |

**Internal URLs (founder only):** Hub `:13020` glance · Cloud Workers `:13027` proceed · Observer `…/api/cloud-forge-run/observer/v1`

**Receipt path:** Railway volume + `~/.sina/hub-cloud-forge-run-proceed-receipt-v1.json` → client-facing proof pack from `phase1-proof-pack-public-v1.json` pattern

**Do NOT build for this offer:** tenant auth · web Forge IDE · new queue kernel

---

# 2. Agent-for-hire — Governed bounded run + receipt

## One-page offer (buyer-facing)

**Headline:** Send one bounded agent job. Get output + a replayable receipt.

**You get**
- One mission (prompt-forged to GOAL / CONTEXT / DONE / VERIFY)
- Governed execution on our Forge Runtime (ALLOW/BLOCK before heavy work)
- Output artifact (code patch, doc, audit, research pack — as scoped)
- **Receipt:** verdict · layers checked · run id · what executed (sanitized for your stakeholders)

**You don’t get**
- Unlimited agent subscription
- Your own Railway/Redis tenant (yet)
- Raw model dump without quality gate summary

**Timeline:** 24–48h typical for bounded jobs  
**Price:** Per job or small pack (3 runs) — quote after scope  
**Try the spine:** https://sourcea.app/forge/terminal (browser demo — books full run)  
**Contact:** forge@sourcea.app · proof@sourcea.app

**Positioning:** Not “another AI agent.” **Agent execution with proof** — the trust layer Tier-1 agents don’t sell.

---

## Single-client flow (existing chain)

| Step | Who | Action | System |
|------|-----|--------|--------|
| 1 | Client | Emails mission or uses sandbox | forge@sourcea.app · or sandbox intake with “governed run” tag |
| 2 | Founder | Prompt forge + scope lock | `scripts/chat_unify_prompt_forge_v1.py` → bounded mission doc |
| 3 | Founder | Dry-run gate | `forge_governance_kernel_v1.govern()` · quality gate shape |
| 4 | Cloud | Run job | Railway `proceed_on_cloud` / `portfolio__forge_dispatch_v1` · `full_motor` as scoped |
| 5 | Worker mesh | LLM + tools | OpenRouter/Gemini on cloud · Cursor handoff only if client opts in |
| 6 | Validate | Quality + PROVE | `scripts/forge_quality_gate_v1.py` · `living_system_chain_validate_v1` |
| 7 | Client | Delivery | `display_response`-style founder language + receipt JSON + artifact link |

**Demo → paid:** `sourcea.app/forge/terminal` proves prompt-forge-on-send; paid run uses same spine on Railway with real scope.

**Receipt fields (client-facing):** run_id · verdict · execution_allowed · artifact path · observer summary line

**Do NOT build for this offer:** BullMQ `apps/forge-core*` as production motor · multi-tenant Supabase RLS (until 5+ paying clients ask)

---

# 3. Integration — Orchestrate their stack + our trust layer

## One-page offer (buyer-facing)

**Headline:** Keep Cursor, Claude Code, and your LLMs. We add governance, routing, and receipts.

**You get**
- **Integration map:** your tools (Cursor · Claude Code · Codex · n8n · webhooks) wired to one governed spine
- Policy before execution (what agents may/may not do in your repo)
- Orchestrated handoffs: mission → agent → validate → receipt
- Optional: Cloud Workers proceed + scheduled auto-runtime for batch ops (not Mac cron)

**You don’t get**
- Migration off your existing IDE
- Us replacing your dev team
- Opaque “AI magic” — every handoff is logged

**Best for:** Agencies and dev shops already on Cursor/Claude who need **client-facing proof** and scope discipline  
**Timeline:** 1–2 week integration sprint + ongoing retainer  
**Contact:** hello@sourcea.app · proof@sourcea.app · https://sourcea.app/forge/cursor-bridge

**Wedge:** We sit **on** Tier-1 tools. They generate; we **conduct and prove**.

---

## Single-client flow (existing chain)

| Step | Who | Action | System |
|------|-----|--------|--------|
| 1 | Client | Integration call | Inventory: Cursor workspace · repos · CI · LLM keys policy |
| 2 | Founder | Manifest + hooks | `data/chat-unify-cursor-plugin-v1.json` · Connect tab · `scripts/forge_terminal_desktop_mesh_v1.py` |
| 3 | Setup | Cursor bridge | Forge mission → Worker INBOX · `send_founder_to_cursor` path in Connect |
| 4 | Setup | Webhooks / n8n | `sourcea-hook-relay-v1` worker · `:13026` n8n glance · inbound hook URL |
| 5 | Runtime | Governed dispatch | Mac `:13029` control · execution `POST :13027` or Railway proceed · **dry_run=false on cloud only** |
| 6 | Per job | Gate → execute → receipt | Same as Agent-for-hire steps 3–7 |
| 7 | Client | Ops view | Observer URL + periodic proof pack · optional Slack/email on PASS/BLOCK |

**Reference docs (public):** https://sourcea.app/forge/cursor-bridge · https://sourcea.app/forge/chat-unify

**Mesh peers (disk):** Chat Unify `:13023` · Cloud Workers `:13027` · Hub `:13020` · Forge Terminal `:13029`

**Do NOT build for this offer:** custom MCP server farm · new IDE · Redis queue as integration backbone (FBE proceed stays canonical)

---

## Which to lead with (founder default)

| Priority | Offer | Why |
|----------|-------|-----|
| **1 — This month** | **Specialist (48h MVP)** | Tangible · landing/intake live · easiest first “yes” |
| **2 — Next** | **Agent-for-hire** | Same engine · stronger moat · upsell after MVP trust |
| **3 — When they have Cursor** | **Integration** | Highest differentiation · needs their stack access |

---

## Engine upgrade rule (all offers)

> Extend Forge Runtime **only** when a **paid** client job hits a wall.  
> Examples: need tenant row → Supabase RLS slice · need self-serve status → one job lookup URL · need video lane → `apps/video-ad-factory` dispatch hook.

**Frozen until demand:** multi-tenant web IDE · `apps/forge-core` Redis motor · consciousness v6–v8 · Lovable-class UI rebuild

---

## Human test (all offers)

1. Send link: https://sourcea.app/forge/terminal  
2. Book: https://cal.com/sourcea/proof-demo  
3. Capture: what they’d call it · would they pay · where confused  
4. Close on **one** offer above — not three

**Agents verify truth. Humans judge sellability.**
