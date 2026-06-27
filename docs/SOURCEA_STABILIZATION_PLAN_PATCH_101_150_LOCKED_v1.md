# Stabilization Plan PATCH — STAB-101 → STAB-150

**Version:** v1.1.0 PATCH  
**Saved at:** 2026-06-24T01:00:00Z  
**Parent:** `docs/SOURCEA_CHAT_UNIFY_PLATFORM_STABILIZATION_PLAN_100_LOCKED_v1.md`  
**Machine:** `data/chat-unify-stabilization-plan-v1.json` (150 items total)

---

## Was STAB-001–100 enough?

**Mostly yes for the Ask-mode “fast stabilization” spine** — but **not 100%**. The original 100 covered:

- ✅ Public deploy, clean URLs, forge pages, anti-poison (disk)
- ✅ One commercial lane (download OR Stripe)
- ✅ Founder/ORD loops preserved + Home prominence
- ✅ MCP, n8n, webhooks, hosted demo (high level)
- ✅ Cloud mesh honesty, enterprise roadmap, ops hygiene
- ✅ Remaining Chat Unify / Connect / landing orders

**Gaps the original 100 did not spell out:**

| Gap area | Why it matters |
|----------|----------------|
| **hello@ + proof@** inboxes | P0 only named forge@ + contact@ |
| **Sales screen-share script** | Ask-mode Week 0 “one smoke path for sales” |
| **cal.com / proof booking** | Separate from generic pricing CTA |
| **Competitive compare** | LangSmith · Braintrust · Langfuse explicit |
| **Full landing surface** | platform · team · growth · loops · factories · films |
| **Mac app fleet** | Cloud Workers · Portfolio Mail · N8N · Mac Health · Routing |
| **48 MVP tools** | wire-n8n · sync-cursor · session library merge |
| **AI runtime** | OpenRouter credits · Cursor paste env · worker inbox |
| **Webhook security** | Auth on hosted relay |
| **Portfolio commercial** | NW1 onepager · WitnessBC separation · INCIDENT-042 drain |
| **Forbidden rules as items** | No UI bump without deploy |

**Patch adds 50 items (STAB-101–150)** → **~95% plan coverage** of Ask-mode + repo surface. Remaining ~5% = future product bets (multi-tenant SaaS, App Store, full SSO) intentionally deferred.

---

## Patch tiers

| Tier | Items | Week |
|------|-------|------|
| **P8** | 101–106 | Week 0 (with P0) — all four email inboxes + portfolio law |
| **P9** | 107–115 | Week 1–2 — sales demo, booking, competitive, onboarding |
| **P10** | 116–130 | Week 2–3 — full site + macOS fleet + routing |
| **P11** | 131–140 | Week 2–3 — AI/Cursor/runtime + security |
| **P12** | 141–149 | Week 3–4 — factories, films, commercial, Cloud Forge Run |
| **P7** | 150 | Monthly — full 150-item audit |

---

## Ask-mode coverage matrix

| Ask-mode recommendation | Original STAB | Patch STAB |
|-------------------------|---------------|------------|
| Deploy landing | 001 | 117, 118, 119 |
| Clean URLs live | 003 | 116, 075 |
| forge@ Workspace | 005–007 | 101–103 |
| contact@ intake | 008 | 103 |
| hello@ anti-poison live | 011–012 | 101, 106 |
| proof@ demo booking | — | 102, 108 |
| Remove fake email CTAs | 009 | 103 |
| Sales smoke path | 043–044 | **107** |
| Pick download OR subscription | 016–017 | 113 (2nd lane week 3) |
| Signed .dmg | 018 | — |
| Stripe Payment Link | 021 | 105 (entity separation) |
| Sandbox CTA works | 024 | 141 |
| MCP + Cursor plugin | 051–054 | 149 |
| n8n template | 057–058 | 125 |
| Hosted webhook | 056 | 134 |
| Hosted demo no Mac | 064 | 135 |
| Restore loops on Home | 033–034 | — |
| Portfolio Mail honest OFFLINE | 082–083 | 124 |
| Cloud Workers always-on | 081 | 123, 142, 143 |
| Do NOT validator marathon | 099 | 126 |
| Do NOT UI without deploy | (forbidden doc) | **140** |
| Do NOT more tabs first | (forbidden doc) | — |
| Compare vs market | 065 | **111** |
| Agency 48 MVP path kept | 077 | 148, 147 |
| proof/live forensic | — | **109** |
| scenario proof quiz | — | **110** |
| OpenRouter / AI advisor | — | **131** |
| Cursor paste / worker inbox | — | **132–133** |
| 48 MVP wire n8n / transcripts | — | **125, 137–138** |
| NW1 commercial send | — | **144** |
| WitnessBC / portfolio isolation | — | **145** |
| Supabase tiers doc | 087 | **146** |
| Weekly/monthly review | 100 | **150** |

---

## PATCH checklist (STAB-101 → STAB-150)

### P8 — Email & portfolio (Week 0) ☐

- [ ] STAB-101 hello@ live  
- [ ] STAB-102 proof@ live  
- [ ] STAB-103 All four inboxes verified  
- [ ] STAB-104 Portfolio account structure session line  
- [ ] STAB-105 Stripe on noetfield@gmail.com only  
- [ ] STAB-106 Signatures https://sourcea.app only  

### P9 — Sales & market (Week 1–2) ☐

- [ ] STAB-107 15-min screen-share script doc  
- [ ] STAB-108 cal.com or proof@ booking on site  
- [ ] STAB-109 proof/live linked from hero  
- [ ] STAB-110 scenario quiz post-deploy  
- [ ] STAB-111 Compare vs LangSmith/Braintrust/Langfuse  
- [ ] STAB-112 Design partner footnote  
- [ ] STAB-113 Second commercial lane week 3  
- [ ] STAB-114 Post-purchase onboarding PDF  
- [ ] STAB-115 contact@ support SLA on site  

### P10 — Full surface (Week 2–3) ☐

- [ ] STAB-116 Root routing / and /sourcea/  
- [ ] STAB-117 All green-unified pages deploy  
- [ ] STAB-118 Forge catalog in publish pipeline  
- [ ] STAB-119 Cloudflare middleware live  
- [ ] STAB-120 status.html honest RED/GREEN  
- [ ] STAB-121 proof-bundle-sample download  
- [ ] STAB-122 official-links-bar fleet sync  
- [ ] STAB-123 Cloud Workers.app bundle  
- [ ] STAB-124 Portfolio Mail stack-boot  
- [ ] STAB-125 N8N wire-n8n works  
- [ ] STAB-126 Mac Health observe-only  
- [ ] STAB-127 AG Routing + Mac Law in Connect  
- [ ] STAB-128 Mobile QA new hero  
- [ ] STAB-129 OG/meta all changed pages  
- [ ] STAB-130 forge/try.html live  

### P11 — AI & security (Week 2–3) ☐

- [ ] STAB-131 OpenRouter credits doc  
- [ ] STAB-132 SINA_ALLOW_CURSOR_PASTE doc  
- [ ] STAB-133 Worker inbox inject test  
- [ ] STAB-134 Webhook auth token  
- [ ] STAB-135 Hosted Chat Unify demo URL  
- [ ] STAB-136 live_http_verify honest in health  
- [ ] STAB-137 sync-cursor / import transcripts  
- [ ] STAB-138 Session library unify-all receipt  
- [ ] STAB-139 form founder supremacy guard  
- [ ] STAB-140 No UI bump without deploy rule  

### P12 — Commercial & cloud (Week 3–4) ☐

- [ ] STAB-141 Factories catalog + sandbox demos  
- [ ] STAB-142 INCIDENT-042 drain honest on Connect  
- [ ] STAB-143 cloud-worker dispatch receipt  
- [ ] STAB-144 NW1 MERGED EXTERNAL ready  
- [ ] STAB-145 WitnessBC / TrustField separation  
- [ ] STAB-146 Supabase spine vs labs doc  
- [ ] STAB-147 Films section loads post-deploy  
- [ ] STAB-148 growth + team consistent with hero  
- [ ] STAB-149 Cursor governance card published  

### P7 — Monthly ☐

- [ ] STAB-150 Full STAB-001–150 audit + honest_scores refresh  

---

## Updated week timeline (150 items)

```
Week 0   P0 + P8     deploy · all 4 emails · poison grep · loops on Home
Week 1   P1 + P9     commerce lane · sales script · booking · compare start
Week 2   P2 + P3 + P10 + P11   app UX · MCP · full site · AI/runtime
Week 3   P4 + P12    order closure · factories · NW1 · Cloud Forge Run
Week 4   P5 + P6     cloud mesh · enterprise docs
Always   P7          CI smoke · no validator stuck · STAB-150 monthly
```

---

## Still intentionally OUT of scope (honest)

These need product decisions later — not hidden as done:

1. **Multi-tenant hosted Chat Unify SaaS** (everyone gets cloud URL) — beyond STAB-135 read-only demo  
2. **Mac App Store listing** — STAB-018 is direct .dmg first  
3. **Full SSO/SAML ship** — P6 roadmap only (STAB-091)  
4. **SOC2 certification** — not just mapping (STAB-092)  
5. **Autonomous sales without founder** — design partners first (STAB-112)  

---

*Patch v1.1.0 — use with parent plan STAB-001–100 · total 150 items in JSON.*
