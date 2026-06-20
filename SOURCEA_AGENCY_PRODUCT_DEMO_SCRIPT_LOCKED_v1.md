# SourceA Agency Product Demo Script — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-15  
**Product:** **SourceA** — controlled agent execution infrastructure (Buyer 1 · agency lane)  
**Commercial package:** **Mac Guard** — invoice SKU for AAA automation shops (`N8N_COMMERCIAL_GRADE_LOCKED_v1.md`)  
**Authority:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` §6 Buyer 1 · §14.2  
**Runner:** `bash scripts/run_sourcea_agency_product_demo_v1.sh`

**Audience:** Platform eng / agency founder running Cursor agents for clients (AAA automation shops)

---

## What you are selling

| Layer | What it is | On this demo |
|-------|------------|-------------|
| **SourceA (product)** | Pre-LLM governance engine — boot gate, receipts, merge audit, export | **Hero** |
| **Mac Guard (package)** | Agency commercial skin — audit PDF + weekly report + Mac ops receipts | **Invoice name** |
| **Noetfield / TrustField** | Other vertical faces on same engine | **Do not pitch** on this call |

**One working proof** (SSOT §14): this demo path is SourceA Buyer 1 — not a separate Mac utility pitch.

---

## Pitch (say this once)

> **SourceA** is controlled agent execution for teams shipping Cursor agents in production.  
> Agents don't run until the machine says **PASS** — every merge gets audited before it becomes law, and every run leaves a receipt logged.  
> For agencies we package it as **Mac Guard**: $750 ops audit, then $299/mo white-label weekly proof your clients can forward.

**Do not pitch:** Sina Command hub · raw n8n · “Mac cooling app” · TrustField MSB · Noetfield Copilot (parallel lanes).

---

## SKUs (client invoice — Mac Guard package)

| SKU | Price | SourceA value |
|-----|-------|----------------|
| **SKU-OPS-002** Ops Health Audit | **$750** | SourceA spine audit + Mac receipts + export PDF |
| **SKU-OPS-001** Mac Guard Agency | **$500** + **$299/mo** | Weekly controlled-ops report · white-label |
| **SKU-SOLO-001** Mac Guard Solo | **$99/mo** | Solo Buyer 1 · same engine, smaller seat |

---

## Pre-flight (founder · 2 min)

```bash
cd ~/Desktop/SourceA
bash scripts/run_sourcea_agency_product_demo_v1.sh --prep-only
```

| Check | Proof |
|-------|--------|
| Chat Unify `:13023` | `curl -sf http://127.0.0.1:13023/health` |
| Mac Health `:13024` | `curl -sf http://127.0.0.1:13024/health` |
| N8N Integration `:13026` | `curl -sf http://127.0.0.1:13026/health` |
| AI critique provider | `~/.sina/secrets.env` · OpenRouter `google/gemini-2.5-flash` fallback |
| Client PDF assets | `~/.sina/n8n-commercial-client-sow-v1.html` |

Hub `:13020` **not required** — standalone mini-apps only.

---

## 5-minute click path (SourceA product proof)

| Step | Buyer sees | Action | SourceA proof |
|------|------------|--------|----------------|
| **1** | Session **BLOCKED** | `~/.sina/critic-boot-v1.json` or live boot | Layer 1 · `critic_boot_v1.py` · 4 disk checks |
| **2** | Fix → **PASS** | `python3 scripts/critic_boot_v1.py --json` | Receipt · `CRITIC BOOT PASS` |
| **3** | Merge + **contradiction** | `http://127.0.0.1:13023/` | Layer 2 · Chat Unify · local brief |
| **4** | **AI critique** verdict | Chat Unify → AI critique | External critic wire · governance language |
| **5** | **Audit PDF** ($750) | `n8n-commercial-client-sow-v1.html` → Print PDF | Mac Guard package deliverable |

**Bridge line:** “Mac Guard is how agencies **buy** SourceA — the engine is the same stack we use for regulated verticals.”

---

## Terminal backup

```bash
python3 scripts/critic_boot_v1.py --json
curl -sf http://127.0.0.1:13024/api/mac-health/live | python3 -m json.tool | head -15
python3 scripts/n8n_commercial_grade_v1.py --pack --json
open ~/.sina/n8n-commercial-client-sow-v1.html
```

---

## Optional BLOCK wow

Stale SSOT or briefing → boot BLOCK → fix → PASS. See `critic_boot_v1.py` checks: `ssot_brief` · `voyage_provider` · `truth_match` · `gate_fresh`.

---

## Close

1. **$750 SourceA Ops Audit** (Mac Guard invoice) — we run boot gate + receipts on your agency Mac, deliver PDF.
2. **$299/mo Agency** — weekly export bundle, white-label for clients.
3. Attach proposal + weekly sample PDF — never raw JSON.

**Buyer 1 path:** credit card · no enterprise RFP · engineer evaluates in the room.

---

## Void on this demo

- “SourceA is internal only / not a product” (void — SSOT v3.1)
- Hub-as-hero · prompt feed · n8n license resale
- Mixing TrustField / Noetfield buyer stories

---

## W3 signal

First **$750 audit** or **$99 Solo month** = economic signal · log vault activity after verbal yes.

---

**Supersedes:** `MAC_GUARD_AGENCY_DEMO_SCRIPT_LOCKED_v1.md` (Mac Guard skin only — this doc is SourceA product-first)

**End LOCKED v1**
