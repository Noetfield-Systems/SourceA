# SOURCE-A — Progress Tracker & Big Picture (LOCKED v1)

**Saved:** 2026-06-24T07:56:46Z  
**Plane:** `brain-os/roadmap/` (internal · not public site copy)  
**Snapshot:** 2026-06-24 · re-verified against live `sourcea.app` + disk receipts  
**Reads against:** SSOT v3 · Master Blueprint v1 · Storefront GTM v1 · Planning Authority Card v1  
**Upgrade registry:** `brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json` (6000 canonical) · UP-888 superseded  
**Registry check:** `data/sourcea-governance-ssot-registry-v1.json`

**Law:** truth from the real surface — everything below was read from the live site, disk receipts, or registry JSON — not assumed from chat memory.

---

## 0. One-line verdict

The **engine, the storefront, and the proof mechanism are all built and live.** Proof Pack machine **#6 is sealed on disk** (truth gate **98/100**). The one thing still missing is **revenue proof** — a real closed deal and a real **client** (non-illustrative) receipt anchored as the public headline. The gap between "impressive platform" and "fundable company" is now exactly **one paying customer**.

---

## 1. What's LIVE today (verified)

| Surface | Status | Notes |
|---------|--------|-------|
| Root hub `sourcea.app/` | ✅ Live | Platform sign-in · "AI that proves its work" · products row |
| Kernel hub `sourcea.app/sourcea/` | ✅ Live | Execution Proof Infrastructure · agency + proof story |
| Pricing ladder | ✅ Live | Audit $750 · Build $3–10K · Retainer $2–5K/mo · Platform from $2K/mo · Sandbox $0 |
| Proof sandbox | ✅ Live | `/sourcea/factories/try-factory-demo` · free · no card |
| Proof surfaces | ✅ Live | Proof chain (6 beats) · forensic proof · films · `sourcea-boot` eval · status page |
| Product downloads | ✅ Live | Chat Unify `.dmg` · `hooks.sourcea.app` · integrations manifest (linked) |
| Positioning | ✅ On-message | Receipts on disk · PASS/BLOCK gates · built in Canada · self-hosted |
| Proof Pack machine #6 | ✅ **Sealed on disk** | `~/.sina/chat-unify-proof-pack-v1.json` · truth gate 98/100 · pack `pp-20260624T062343Z-0e934a1e` |
| SSOT registry | ✅ **On disk** | `data/sourcea-governance-ssot-registry-v1.json` · v3 + blueprint + GTM + kernel active |
| E2E infra | ✅ 4/4 PASS | `~/.sina/sourcea-e2e-last-report-v1.json` · 2026-06-24 |

---

## 2. Locked execution order (founder · 2026-06-24)

From `brain-os/ssot/SOURCEA_PLANNING_AUTHORITY_CARD_LOCKED_v1.md`:

| Priority | Action | Status |
|----------|--------|--------|
| **B · FIRST** | Seal 1 real Proof Pack from green run | ✅ **DONE** — 98/100 on disk · public export at `sites/SourceA-landing/green-unified/data/phase1-proof-pack-public-v1.json` |
| **A · SECOND** | **1 paying T1 client** — run factory · deliver output + client Proof Pack | 🔴 **NEXT** — no client SOW / client receipt on disk yet |
| **C · THIRD** | Executor + router hardening (after B + A) | ⏸ Blocked until A |

**Single next move:** Close one paying engagement → deliver **client** Proof Pack → promote it to site headline (replace illustrative metrics + boot-only hero).

### Noetfield Intelligence 613 (parallel · LOCKED 2026-06-24)

**Authority:** `docs/NOETFIELD_INTELLIGENCE_613_PLAN_LOCKED_v1.md` · wired in `brain-os/plan-registry/SOURCEA-PRIORITY.md`

| Signal | Status |
|--------|--------|
| 613 plan LOCKED | ✅ on disk |
| NW1 / W3 | 🔴 ❌ — no Noetfield invoice yet |
| Primary GTM shift | 🟢 Intelligence homepage + nav shipped (branch) · Copilot on `/governance/` |
| H1 target (90 days) | 🔴 2 Diagnostics @ $2.5K · $5K+ cash |
| noetfield.com hero | 🟡 shipped branch `2557f079` · merge `main` for live deploy (`NF_INTELLIGENCE_LANDING`) |

**Noetfield next move:** Invoice first **AI Diagnostic Sprint** (diaspora or RCIC wedge) — same revenue-proof gap as SourceA T1, **different buyer**.

---

## 3. Full sitemap (corrected paths)

### Root hub

| Path | Purpose |
|------|---------|
| `/` | Platform home |
| `/platform` | Sign-in / cloud runtime |
| `/start` | 48h MVP intake |
| `/mvp` | MVP landing |
| `/downloads/` · `/downloads/chat-unify-mac-v1.dmg` | Mac app |

### Kernel / proof site (`/sourcea/`)

| Path | Purpose |
|------|---------|
| `/sourcea/` | Execution Proof Infrastructure home |
| `/sourcea/platform` | Platform buyer story |
| `/sourcea/team` | 6-agent council |
| `/sourcea/growth` | Growth flywheel |
| `/sourcea/scenario` | Screen-share script |
| `/sourcea/proof` · `/sourcea/proof/live` | Proof chain + forensic proof |
| `/sourcea/compare` | Capability matrix |
| `/sourcea/pricing` | Fixed-outcome pricing |
| `/sourcea/security` | Procurement & trust |
| `/sourcea/sources` | Cited evidence |
| `/sourcea/status` | Live factory status |

### Forge · sandbox · loops

| Path | Purpose |
|------|---------|
| `/sourcea/forge/` · `/sourcea/forge/try` · `/sourcea/forge/chat-unify` | Prompt Forge hub |
| `/sourcea/factories/try-factory-demo` | Free sandbox |
| `/sourcea/loops/` · `/loops/outreach` · `/loops/ops-monitor` · `/loops/research` | Loop hubs |

### Attachments · assets · data (**path fix**)

| Path | Purpose |
|------|---------|
| `/sourcea/attach/proof-bundle-sample` | PDF sample |
| `/sourcea/attach/procurement-pack` | Procurement pack |
| `/sourcea/attach/agency-onepager` | Agency one-pager |
| `/sourcea/assets/commercial-short-demo.mp4` · `/assets/w1-demo.mp4` | Films |
| `/sourcea/data/chat-unify-integrations-v1.json` | Integrations manifest (**canonical**) |
| `/sourcea/data/n8n-template-sourcea-chat-unify-v1.json` | n8n template (**canonical**) |
| `/sourcea/data/phase1-proof-pack-public-v1.json` | Public Proof Pack export |

> **Correction:** `/data/n8n-template-…` (root) is **not** canonical — SPA fallback to root hub. Always link `/sourcea/data/…`.

### External · infra

| Resource | Purpose |
|----------|---------|
| `hooks.sourcea.app/v1/relay` | Webhook relay |
| `command.sourcea.app/team` | Command center ref |
| `github.com/kazemnezhadsina144-dot/sourcea-boot` | Public boot eval |
| `hello@sourcea.app` | Commercial contact |
| `127.0.0.1:13023` | Chat Unify local (documented on status/downloads) |

**Tech stack named publicly:** Temporal · Anthropic Claude · OpenAI · LangGraph · Cursor · Cloudflare.

---

## 4. Progress vs locked docs

| Locked principle | Status on live site / disk |
|------------------|----------------------------|
| Receipts/gates/proof (SSOT v3) | ✅ Live and central |
| Receipt = product/proof/moat (Blueprint) | ✅ Proof-first selling throughout |
| Offer ladder DFY → seat → SaaS | ✅ Audit → Build → Retainer → Platform |
| Proof Sandbox hook (GTM) | ✅ Live, free, no card |
| "Show the receipt, not the recipe" | ⚠️ **Partial** — see flag #1 |
| Proof Pack #6 (98/100) | 🟡 **Built + sealed on disk** · not yet **public headline** |
| Hybrid pricing (base + per-outcome) | 🟡 Fixed-project + retainer live; usage metering not visible |
| Market fit (vertical + governance/audit) | ✅ Dead-on June-2026 thesis |
| SSOT registry (active/superseded/stale) | ✅ **Locked on disk** · ongoing hygiene required |
| Phase 0 revenue proof (Blueprint) | 🔴 **Not met** — no paying client receipt |

---

## 5. Flags & conflicts (honest list)

1. **Recipe-exposure risk** — Site links n8n template, integrations manifest JSON, local ports (`127.0.0.1:13023`), and `sourcea-boot` source. **Founder decision:** keep stack-naming + boot eval public (credibility); reconsider public n8n template + integrations manifest (GTM firewall).
2. **Traction is illustrative** — Metrics honestly labeled; reads as zeros until a client receipt ships.
3. **Real Proof Pack not yet headline** — Disk has 98/100 seal; live hero is still `sourcea-boot` + illustrative agency metrics. **Marketing task**, not engineering blocker.
4. **Two-hub identity overlap** — Root and `/sourcea/` both say "run on proof." Track consolidation; not urgent.
5. **SSOT registry hygiene** — Registry **exists** (`saved_at` 2026-06-23). Work = promote new law rows · flag stale rule-like docs without rows · never execute from superseded paths.
6. **Brand drift** — Sandbox page title still shows "Noetfield" — minor fix in upgrade queue (`UP-WEB` slice).

---

## 6. Big picture

SourceA has, in hand and live, the three things most startups spend a year building:

- **The engine** — kernel + 6 governed machines + receipts on disk.
- **The storefront** — full multi-page commercial site with offers, films, sandbox, proof story.
- **The proof mechanism** — Proof Pack machine seals runs into buyer/investor/audit artifacts (98/100 on disk).

This lands on the June-2026 market: vertical AI agents + agent execution infrastructure + governance/audit. "Paper Governance" is the named failure SourceA structurally avoids.

**The honest gap:** capability is proven; **commercial proof is not**. The next dollar — and the first **client** Proof Pack — converts the live platform from demo to fundable.

---

## 7. Phased goals (receipt-gated)

### NOW (this week)

- [ ] Run sandbox → build motion on **one real prospect**; close one paying engagement.
- [ ] Produce **client Proof Pack** from that engagement; make it the site headline (replace illustrative).
- [ ] **Recipe-exposure** founder call (firewall n8n template / manifest if needed).
- [ ] Promote sealed Phase-1 pack OR client pack to hero on `/sourcea/` (wired in repo · not yet headline on live).

### NEXT (2–6 weeks)

- [ ] 3–5 design partners through same motion.
- [ ] Per-outcome / usage metering visible in pricing.
- [ ] Two-hub identity consolidation (canonical URLs never fork).
- [ ] Weekly proof export as retainer recurring deliverable (promised on-site).

### LATER (1–6 months)

- [ ] Audit-grade receipts (append-only, SHA-256 hash-chained, ≥6-mo retention).
- [ ] Multi-tenant + RBAC/RLS for self-serve.
- [ ] SOC 2 / NIST AI RMF mapping (each control tied to a receipt).
- [ ] Replay Viewer · Blueprint Marketplace · MCP-native registry.

---

## 8. Upgrade plans (6000 canonical)

**Canonical master:** `brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json`  
**Law:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`  
**Mapping:** `data/upgrade-888-to-sa-next-mapping-v1.json` (888 UP → sa-next rows)  
**Superseded lineage:** `brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json`

### Phase distribution (per repo, ranks 1–1000)

| Phase | Ranks | Meaning |
|-------|-------|---------|
| NOW | 1–30 | Revenue + headline proof + recipe firewall |
| NEXT | 31–120 | Productize · design partners · site consolidation |
| LATER | 121–400 | SaaS · compliance · integrations · observability |
| MOONSHOT | 401–1000 | Enterprise scale · marketplace · long-horizon |

### SourceA legacy mapping (UP-888)

| Signal | Value |
|--------|-------|
| Merged rows | `sa-next-0001` … `sa-next-0888` carry `legacy_upgrade_id` |
| Gap-fill | `sa-next-0889` … `sa-next-1000` generator-native |
| Merger | `scripts/merge_upgrade_888_into_portfolio_next_v1.py` |

### How to pick

```bash
# Phase-first sa-next picks (SourceA)
bash scripts/plan-no-asf-run.sh pick-next 3

# Any repo
python3 scripts/pick_portfolio_next_plan_v1.py --repo noetfield --any-phase --limit 3 --prompt
```

**Rule:** No plan advances to `status: done` without a disk receipt matching its `receipt_gate`. Queue head + Revenue Engine still win over registry head.

### Top open NOW plans (post-merge — run pick-next for live head)

| ID | Legacy | Title |
|----|--------|-------|
| sa-next-0001 | UP-0001 | Close T1 paying client |
| sa-next-0003 | UP-0003 | Close T1 paying client |
| sa-next-0004 | UP-0004 | Seal client Proof Pack |

---

## 9. Disk proof references (refresh weekly)

| Artifact | Path |
|----------|------|
| Proof Pack seal | `~/.sina/chat-unify-proof-pack-v1.json` |
| Phase-1 source ticket | `~/.sina/phase1-pevc-truth-ticket-v1.json` |
| Public pack export | `sites/SourceA-landing/green-unified/data/phase1-proof-pack-public-v1.json` |
| SSOT registry | `data/sourcea-governance-ssot-registry-v1.json` |
| Planning authority | `brain-os/ssot/SOURCEA_PLANNING_AUTHORITY_CARD_LOCKED_v1.md` |
| E2E last report | `~/.sina/sourcea-e2e-last-report-v1.json` |
| Live surfaces | `~/.sina/agent-live-surfaces-v1.json` |
| 6000 canonical master | `brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json` |
| UP-888 mapping manifest | `data/upgrade-888-to-sa-next-mapping-v1.json` |
| UP-888 superseded lineage | `brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json` |

---

## 10. Refresh cadence

- Re-verify against **live** `sourcea.app` after every major deploy — not from memory.
- Bump **`Saved:`** UTC timestamp on material edits.
- Promote client Proof Pack to §1 and §4 when `receipt_gate: client_proof_pack` clears.
- Sync `ROADMAP_INDEX_LOCKED_v1.md` when adding sibling roadmap docs.

---

*Progress Tracker v1 · Source-A · 2026-06-24T07:56:46Z · internal roadmap plane · public copy ships via `SourceA-landing/` only.*
