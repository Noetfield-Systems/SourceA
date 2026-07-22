# SourceA Chat Unify + Platform Stabilization Plan — 100 items

**Version:** v1.0.0 LOCKED  
**Saved at:** 2026-06-24T00:15:00Z  
**Machine:** `data/chat-unify-stabilization-plan-v1.json`  
**Patch (STAB-101–150):** `docs/SOURCEA_STABILIZATION_PLAN_PATCH_101_150_LOCKED_v1.md`  
**Total items:** 150 (100 core + 50 patch) · **plan coverage ~95%** of Ask-mode + repo surface  
**Scope:** Fix everything in “What is not stabilized yet” + remaining founder orders from Chat Unify / Connect / landing arc.

---

## Honest baseline (no green theater)

| Dimension | Score /10 | Today |
|-----------|-----------|--------|
| Vision / story | 8 | Strong — governed agents + proof + control plane |
| Core machines on Mac | 6.5 | Founder loop + ORD loop **still exist** (Verify & Act · Audit Trail) |
| Product UX for non-experts | 5 | Home 4.4 better; localhost + server lifecycle still friction |
| Integration platform (market) | 3.5 | Local webhooks + manifest; not marketplace-listed |
| Commercial readiness | 2.5 | mailto CTAs; no Stripe checkout / public .dmg |
| Live public proof | 3.5 | Disk ahead of sourcea.app deploy |
| Enterprise procurement | 2 | Story on site; not turnkey SKU |

**Completion estimate:** ~**68% on disk** · ~**38% live in market**

**Founder loop / ORD loop:** NOT removed. Renamed, de-emphasized on Home, moved under “48-hour MVP” collapsible. Tabs **Verify & Act** and **Audit Trail** — full 7-step pipelines unchanged in `chat_founder_loop_v1.py` / `chat_ord_loop_v1.py`.

---

## Priority tiers (wise order)

| Tier | Name | When | Rule |
|------|------|------|------|
| **P0** | Public truth | Week 0 (days 1–3) | If live site ≠ disk, nothing else counts as shipped |
| **P1** | One commercial lane | Week 1 | Pick **download** OR **subscription** — ship one end-to-end |
| **P2** | Chat Unify UX | Week 1–2 | Loops visible, server stable, smoke paths documented |
| **P3** | Market integrations | Week 2–3 | MCP, n8n, hosted demo — things buyers recognize |
| **P4** | Remaining orders | Parallel P0 | Forge, URLs, email, bundle sync — close the thread |
| **P5** | Cloud mesh | Week 3–4 | Railway / mail / workers not Mac-only |
| **P6** | Enterprise | Month 2+ | SSO, SLA, procurement — honest not fake |
| **P7** | Ops hygiene | Always | CI smoke, no Mac validator stuck, weekly review |
| **P8–P12** | **PATCH** | Weeks 0–4 | See patch doc — email fleet, sales, full site, AI runtime, commercial |

**Do NOT do first:** more tabs, more law files, validator marathons on Mac during founder sessions.

> **STAB-101–150** closes gaps the first 100 missed: hello@/proof@, sales script, full landing fleet, macOS apps, OpenRouter/Cursor paste, NW1 commercial, INCIDENT-042 drain. See patch doc.

---

## Week timeline (fast stabilization)

```
Week 0  P0 deploy + email live + poison grep
Week 1  P1 commerce lane + P2 Home/loops prominence + bundle ritual
Week 2  P3 MCP/n8n/hosted demo + P4 order closure
Week 3  P5 cloud always-on + mesh honesty
Week 4  P6 enterprise docs + P7 CI smoke + score refresh
```

---

## P0 — Public truth (15 items) · STAB-001 → STAB-015

**Goal:** What visitors see at https://sourcea.app/sourcea/ matches what you built on disk.

| ID | Check | Done when | Command / path |
|----|-------|-----------|----------------|
| STAB-001 | Deploy landing to Cloudflare | dist live | `python3 scripts/publish_sourcea_landing_v1.py --backend cloudflare` |
| STAB-002 | New founder hero live | H1 “Run your agentic startup on proof” | curl `/sourcea/` |
| STAB-003 | Clean URLs live | No `.html` in browser bar | `scripts/sourcea_clean_urls_v1.py` in build |
| STAB-004 | Forge subpages live | `/sourcea/forge/*` 200 | 7 pages in `sites/.../forge/` |
| STAB-005 | forge@ inbox exists | Google Workspace | Admin console |
| STAB-006 | forge@ app password | `~/.sina/secrets.env` | `SA-FORGE-GOOGLE_WORKSPACE_APP_PASSWORD` |
| STAB-007 | forge@ send/receive smoke | Test email round-trip | Manual |
| STAB-008 | contact@ intake live | Form submissions arrive | MVP intake config |
| STAB-009 | No fake email CTAs | Hide buttons if inbox missing | UI audit |
| STAB-010 | Deploy receipt | JSON receipt with checksum | Post-deploy script |
| STAB-011 | Anti-poison on disk | hello@sourcea.app | **partial** — law + JSON done |
| STAB-012 | Anti-poison on live site | grep sourcea.com = 0 hits | curl + grep |
| STAB-013 | _redirects synced | Cloudflare Pages rules | dist `_redirects` |
| STAB-014 | Single deploy doc | Founder one command | [`docs/SOURCEA_LANDING_DEPLOY_FOUNDER_ONE_PAGER_LOCKED_v1.md`](SOURCEA_LANDING_DEPLOY_FOUNDER_ONE_PAGER_LOCKED_v1.md) |
| STAB-015 | 24h deploy rule | Merge → ship within 1 day | **LOCKED:** landing merge same day → inject + publish; receipt `boot_verdict: PASS` |

**Founder deploy (canonical):**

```bash
cd ~/Desktop/SourceA
PYTHONPATH=packages/sourcea-boot/src python3 scripts/inject_sourcea_boot_terminal_v1.py
python3 scripts/publish_sourcea_landing_v1.py --backend cloudflare --project sourcea-com --custom-domain --skip-recipe
```

Proxy worker only when changed: `cd cloud/workers/sourcea-app-proxy-v1 && npx wrangler deploy`

---

## P1 — One commercial lane (15 items) · STAB-016 → STAB-030

**Goal:** A stranger can **buy or download** without emailing you (v1 manual provision behind Stripe OK).

| ID | Check | Done when |
|----|-------|-----------|
| STAB-016 | Decision: download-first vs sub-first | Founder picks one lane |
| STAB-017 | Alt lane documented | Second lane queued for week 3 |
| STAB-018 | Signed .dmg / notarized zip | Chat Unify 4.4+ artifact |
| STAB-019 | Hosted download URL | `sourcea.app/downloads/...` |
| STAB-020 | Replace mailto “Get app” | Real href |
| STAB-021 | Stripe Payment Link | Platform runtime from $2K/mo |
| STAB-022 | Post-checkout email | Onboarding template |
| STAB-023 | Pricing CTAs | Stripe or cal.com |
| STAB-024 | Sandbox CTA works | Factory demo + receipt |
| STAB-025 | Funnel page | sandbox → app → paid |
| STAB-026 | Release notes page | 4.4 changelog |
| STAB-027 | Update story v1 | Version check or reinstall doc |
| STAB-028 | GTM decision recorded | brain-os or founder form |
| STAB-029 | Live receipt counter | Real metric not placeholder |
| STAB-030 | Procurement PDF links | Post-deploy 200 |

---

## P2 — Chat Unify product UX (20 items) · STAB-031 → STAB-050

**Goal:** Founder loop + ORD loop feel **first-class** again; app reliable on Desktop.

| ID | Check | Status | Action |
|----|-------|--------|--------|
| STAB-031 | Founder loop backend | **partial** | Keep — `founder_loop_stage` |
| STAB-032 | ORD loop backend | **partial** | Keep — `ord_loop_stage` |
| STAB-033 | Loops on Home hero | open | Add Verify + Audit cards above fold |
| STAB-034 | Primary CTAs | open | “Verify reply” + “Audit output” on Home |
| STAB-035 | stack-boot recycle | **partial** | `chat-unify-stack-boot.sh` |
| STAB-036 | Keep-alive optional | open | LaunchAgent or menu bar |
| STAB-037 | Browser doc | open | Safari not Cursor for :13023 |
| STAB-038 | Bundle sync 3 targets | **partial** | `sync-chat-unify-bundle-v1.sh` |
| STAB-039 | Post-change ritual | open | sync → stack-boot → health 4.4+ |
| STAB-040 | Prompt Forge tab | **partial** | Wired |
| STAB-041 | Connect tab | **partial** | Wired |
| STAB-042 | Platform catalog API | **partial** | `/api/platform-catalog/v1` |
| STAB-043 | Verify smoke doc | open | 1-page founder path |
| STAB-044 | ORD smoke doc | open | 1-page founder path |
| STAB-045 | Verify ↔ ORD truth link | open | Sidebar linkage |
| STAB-046 | Proof Pack seal path | open | Export path visible |
| STAB-047 | Decisions form receipt | open | Submit → disk proof |
| STAB-048 | Tasks dispatch receipt | open | Cloud worker JSON |
| STAB-049 | First-run onboarding | open | 3 audience paths |
| STAB-050 | Offline empty state | open | Plain English + stack-boot hint |

**Tabs today (unchanged machines):**

| Tab | Machine | Steps |
|-----|---------|-------|
| Prompt Forge | prompt_forge | 4 |
| Connect | integrations | 6 lanes |
| Verify & Act | founder_loop | 7 |
| Audit Trail | ord_loop | 7 |
| Proof Pack | proof_pack | 5 |
| Decisions | form_official | — |
| Tasks | api_station | — |
| Operations | hub_pro | — |

---

## P3 — Market integrations (15 items) · STAB-051 → STAB-065

**Goal:** Buyers see SourceA next to tools they already use.

| ID | Focus |
|----|--------|
| STAB-051–054 | MCP npm + Cursor plugin marketplace + cursor-bridge page |
| STAB-055–056 | Webhook local → Cloudflare hosted relay |
| STAB-057–058 | n8n template + cloud n8n URL |
| STAB-059 | Zapier/Make event schema |
| STAB-060 | Public manifest URL on site |
| STAB-061 | Cursor Cloud dispatch doc |
| STAB-062 | GitHub Action → proof.seal sample |
| STAB-063 | Partner logo honesty |
| STAB-064 | Hosted sandbox demo (no Mac) |
| STAB-065 | Compare page + Connect positioning |

**Paths:** `packages/mcp-sourcea-verify/` · `cursor-plugin/sourcea-forge-governance/` · `data/chat-unify-cursor-plugin-v1.json`

---

## P4 — Remaining founder orders (15 items) · STAB-066 → STAB-080

| Order from thread | IDs | Disk | Live |
|-------------------|-----|------|------|
| Email .app roles | 066–067 | ✅ | ⬜ verify |
| Clean URLs | 068, 075 | ✅ | ⬜ deploy |
| Forge landing | 069, 074 | ✅ | ⬜ deploy |
| Forge in Chat Unify app | 070 | ✅ | ⬜ bundle rebuild |
| :13023 / IPv6 / stack-boot | 071, 035 | ✅ | ⬜ habit |
| UI version from health | 072 | ✅ | ⬜ |
| .app CFBundle 4.4 | 073 | ⬜ | run build script |
| Platform showcase / 48 MVP | 076–077 | ✅ disk | ⬜ deploy |
| Email vault + signatures | 078–079 | ✅ | ⬜ Workspace |
| Status if deploy blocked | 080 | ⬜ | `/sourcea/status` |

---

## P5 — Cloud mesh (10 items) · STAB-081 → STAB-090

| ID | Truth required |
|----|----------------|
| STAB-081 | Cloud Workers on Railway 24/7 |
| STAB-082 | Portfolio Mail cloud or honest OFFLINE |
| STAB-083 | Mesh pills never fake LIVE |
| STAB-084 | Hub :13020 retired doc |
| STAB-085 | Mac Health observe-only |
| STAB-086 | FBE drain via Connect → cloud |
| STAB-087 | Supabase tier buyer doc |
| STAB-088 | Weekly proof export automation |
| STAB-089 | Team seats on subscription |
| STAB-090 | sourcea-boot widget live |

---

## P6 — Enterprise (7 items) · STAB-091 → STAB-097

Honest procurement — label **roadmap** until shipped:

SSO · SOC2 mapping · procurement ZIP · Canada residency · SLA template · pen test schedule · DPA template

---

## P7 — Ops hygiene (3 items) · STAB-098 → STAB-100

| ID | Rule |
|----|------|
| STAB-098 | CI smoke on cloud only — not Mac founder session |
| STAB-099 | INCIDENT-039 — no validator marathon on Mac |
| STAB-100 | Weekly: update JSON status + honest_score |

---

## Master checklist (copy for founder)

### Week 0 — do these first ☐

- [ ] STAB-001 Deploy landing  
- [ ] STAB-003 Clean URLs live verify  
- [ ] STAB-004 Forge pages live  
- [ ] STAB-005–007 forge@ live  
- [ ] STAB-012 Grep live site for sourcea.com  
- [ ] STAB-033–034 Restore loops on Home hero  

### Week 1 — commerce + app ☐

- [ ] STAB-016 Pick download OR subscription lane  
- [ ] STAB-018–020 OR STAB-021–023 Stripe path  
- [ ] STAB-039 sync + stack-boot ritual  
- [ ] STAB-073 Rebuild Chat Unify.app 4.4  

### Week 2 — integrations ☐

- [ ] STAB-052–054 MCP + Cursor plugin  
- [ ] STAB-057 n8n template  
- [ ] STAB-064 Hosted sandbox demo  

### Ongoing ☐

- [ ] STAB-083 Mesh honesty (OFFLINE not LIVE)  
- [ ] STAB-100 Weekly plan review  

---

## What is NOT stabilized yet → plan mapping

| Gap from assessment | Plan tier | Items |
|---------------------|-----------|-------|
| Public website deploy lag | P0 | 001–015 |
| Download product (no .dmg) | P1 | 016–020 |
| Cloud subscription (no Stripe) | P1 | 021–025 |
| Integrations vs market | P3 | 051–065 |
| Always-on / server dies | P2, P5 | 035–037, 081–083 |
| forge@ Workspace | P0, P4 | 005–007, 066 |
| Loops buried on Home | P2 | 033–034 |
| Remaining orders | P4 | 066–080 |

---

## Commands reference

```bash
# Deploy public site
python3 ~/Desktop/SourceA/scripts/publish_sourcea_landing_v1.py --backend cloudflare

# Sync + boot Chat Unify
bash ~/Desktop/SourceA/scripts/sync-chat-unify-bundle-v1.sh
bash ~/Desktop/SourceA/scripts/chat-unify-stack-boot.sh

# Rebuild desktop app
bash ~/Desktop/SourceA/scripts/build-chat-unify-standalone-app-v1.sh

# Update plan status (machine)
# Edit data/chat-unify-stabilization-plan-v1.json — set status: done | partial | open
```

---

## Forbidden (slow / harmful)

1. Run all validators on Mac to “prove green” during founder session  
2. Add new tabs before P0 deploy  
3. Show LIVE on mesh when probe fails  
4. mailto-only as only commercial CTA after Week 1  
5. Claim Cursor marketplace listing before STAB-054 done  

---

*End of plan — 100 core items STAB-001 through STAB-100 · **+ patch STAB-101–150** · update STAB-100 weekly · STAB-150 monthly.*
