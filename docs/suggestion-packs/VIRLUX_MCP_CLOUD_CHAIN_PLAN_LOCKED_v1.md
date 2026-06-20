# VIRLUX MCP Cloud Chain Plan — LOCKED v1 (111 steps)

**Version:** 1.0.0 · **Saved:** 2026-06-19T12:00:00Z · **Authority:** ASF suggestion from SourceA  
**Copy target:** `~/Desktop/VIRLUX/os/plan-library/SOURCEA_SUGGESTION_MCP_CHAIN_LOCKED_v1.md`  
**Campus:** Verify / delivery · certainty report · 18/18 live prove  
**Motor (read-only):** `~/Desktop/SourceA/docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md`  
**Existing:** `FACTORY_CAMPUS_BLUEPRINT_LOCKED_v1.md` · `virlux-factory-catalog/` · `/dashboard/factory`

---

## 0. Chain position

| Role | Primary | Win-win |
|------|---------|---------|
| **Campus host** | `virlux-verify` MCP | Builders get 30s certainty demo |
| **Chain provider** | `run_sandbox_verify` after GitHub/Playwright | Cursor + GitHub enterprise story |
| **Chain consumer** | GitHub MCP · Playwright · Vercel deploy proof | Badges + live URL |

**One sentence:** We prove your verify ladder — SCAN→PICK→PROVE with MOCK_ONLY honesty until premium bay.

**Mac:** Founder glances Hub only. **Cloud:** API · MCP · workers on Vercel + Railway + Supabase.

---

## 1. Cloud architecture

```text
Cursor Cloud Agent / Claude
    → GitHub MCP (PR) · Playwright MCP (E2E)
    → virlux-verify MCP (cloud)
        → run_sandbox_verify · get_certainty_report
    → Receipt → R2/Supabase → federate SourceA motor (read)
Mac Hub :13020 — read-only status card
```

---

## 2. MCP spec (`io.github.virlux/virlux-verify`)

```json
{
  "tools": [
    { "name": "run_sandbox_verify", "input": { "target_url": "string", "mock_only": true }, "output": { "verdict": "PASS|FAIL|MOCK_ONLY", "certainty_report": {}, "demo_seconds": 30 } },
    { "name": "get_certainty_report", "input": { "receipt_id": "string" }, "output": { "report": {}, "evidence_url": "string" } },
    { "name": "list_factories", "input": {}, "output": { "factories": [], "honest_labels": {} } },
    { "name": "catalog_honest_label", "input": { "factory_id": "string" }, "output": { "tier": "string", "delivery_mode": "mock_only|live" } }
  ]
}
```

**Registry publish (P1):** npm `@virlux/mcp-verify-factory` · Cursor Marketplace card **VIRLUX Verify Factory** · Categories: **Infrastructure** · **Canvas** (certainty report UI).

---

## 3. Learn from market (applied)

| Pattern | VIRLUX implementation |
|---------|----------------------|
| Cursor 3 per-agent MCP scope | Verify agent gets Playwright + virlux-verify only |
| Cloud Agents dashboard MCP | Team shared `virlux-verify` SSE URL |
| Official MCP Registry reverse-DNS | `io.github.virlux/virlux-verify` |
| After-every-action receipt (Pattern A) | Post-`verify:live` → MCP `get_certainty_report` |
| Plugin = skills + MCP | Skill: `skill-commercial-film-routing` + verify MCP |

---

## 4. Steps 001–111 (cloud worker picks)

### T01 Chain consumer (001–010)

| # | Cloud worker task |
|---|-------------------|
| 001 | Wire GitHub MCP — PR opened triggers verify issue template |
| 002 | Playwright MCP scoped to verify agent — read `verify:live` selectors |
| 003 | Vercel deploy URL as default `target_url` (`virlux-web.vercel.app`) |
| 004 | Linear Integration Leverage issue `VIRLUX-MCP-001` |
| 005 | Never replace `npm run plan:unified:pick` — MCP assists |
| 006 | Map existing `emit-verify-receipt.py` to cloud receipt bucket |
| 007 | `mock_only: true` default on all sandbox MCP calls |
| 008 | Document honest label in MCP tool descriptions |
| 009 | Consumer receipt fixture `fixtures/mcp-consumer-pr.json` |
| 010 | Validator extends `validate-virlux-factory-catalog.sh` step 001–010 |

### T02 virlux-verify MCP (011–020)

| # | Cloud worker task |
|---|-------------------|
| 011 | Create `packages/mcp-verify-factory/` in VIRLUX monorepo |
| 012 | `run_sandbox_verify` calls existing verify kernel (headless) |
| 013 | 30s demo cap enforced server-side |
| 014 | `get_certainty_report` reads `virlux-verify-factory-v1.json` schema |
| 015 | `list_factories` from `REGISTRY.json` static + API |
| 016 | SSE server on Railway `virlux-api` or new service |
| 017 | stdio for local `npx @virlux/mcp-verify-factory` |
| 018 | API key auth · 10 sandbox runs/day freemium |
| 019 | OpenAPI `apps/api/openapi/mcp-verify-v1.yaml` |
| 020 | Unit tests mirror `verify:live` 18 assertions |

### T03 Campus catalog API (021–030)

| # | Cloud worker task |
|---|-------------------|
| 021 | `GET /api/factory/catalog` — already in dashboard; expose public read |
| 022 | `GET /api/factory/spec/:id` read-only JSON |
| 023 | CORS for Cursor Cloud Agents |
| 024 | Wire `BUILD_FACTORY_TAB_IA-LOCK.md` sections to API labels |
| 025 | Teams tab premium flag in API `tier=premium` |
| 026 | `virlux-rent-line-v1.json` P2 stub in catalog `status=spec` |
| 027 | Cache catalog at edge (Vercel ISR 300s) |
| 028 | Federation POST to SourceA motor webhook (optional P1) |
| 029 | Hub deep link card data feed JSON |
| 030 | `npm run mcp:validate` script |

### T04 Cloud worker runtime (031–042)

| # | Cloud worker task |
|---|-------------------|
| 031 | **PICK** — `packages/mcp-verify-factory` deploy to Railway/Vercel |
| 032 | Env `VIRLUX_RECEIPT_BUCKET` `MCP_API_KEY_SALT` |
| 033 | Worker queue for long verify runs (BullMQ/CF Queue) |
| 034 | CI: `npm test && npm run build && bash scripts/validate-virlux-factory-catalog.sh` |
| 035 | Preview deploy per PR — certainty report URL in comment |
| 036 | Structured logs `virlux-mcp-verify-v1` |
| 037 | Cron keepalive `npm run supabase:keepalive` unchanged |
| 038 | Idempotent `run_sandbox_verify` by `client_request_id` |
| 039 | p99 < 30s for mock path |
| 040 | Degrade: return MOCK_ONLY if live URL down (honest) |
| 041 | Mac docs: cloud URL only in README |
| 042 | `npm run mcp:chain:pick -- --step N` in package.json |

### T05 Registry publish (043–050)

| # | Task |
|---|------|
| 043 | Publish `@virlux/mcp-verify-factory` npm |
| 044 | Submit Official MCP Registry metadata |
| 045 | Namespace `io.github.virlux/virlux-verify` |
| 046 | Glama listing: "verify factory receipt" |
| 047 | README chain-friendly + link to `/dashboard/factory` |
| 048 | SECURITY.md — no custody · mock_only default |
| 049 | Tag `mcp-verify-v1.0.0` |
| 050 | Close Linear `VIRLUX-MCP-PUBLISH` |

### T06 Cursor plugin (051–060)

| # | Task |
|---|------|
| 051 | Plugin `virlux-verify-factory` manifest |
| 052 | Skill bundle: commercial film routing + verify |
| 053 | Rule: honest tier labels in agent replies |
| 054 | mcp.json one-click install fragment |
| 055 | Demo: PR → verify:live → MCP report |
| 056 | Marketplace tags Infrastructure + Canvas |
| 057 | Canvas certainty report MCP Apps extension (P1) |
| 058 | Cloud Agent "VIRLUX Verify" preset |
| 059 | Allowlist `run_sandbox_verify` read-only params |
| 060 | T1 badge copy only — not T0 hero |

### T07 GitHub + Linear (061–070)

| # | Task |
|---|------|
| 061 | GitHub Action `virlux-mcp-verify.yml` on PR |
| 062 | PR badge PASS/FAIL from certainty report |
| 063 | Linear issues for 18/18 gate regressions |
| 064 | Label `verify-receipt` |
| 065 | Mirror commercial outbound not every commit |
| 066 | Link MCP receipt to `verify_last` in plan.json |
| 067 | Official Cursor↔Linear cite |
| 068 | No VIRLUX queue in Linear |
| 069 | Integration Leverage dashboard |
| 070 | Agency partner one-liner |

### T08 Supabase + Vercel (071–080)

| # | Task |
|---|------|
| 071 | Supabase bucket `virlux-mcp-receipts` |
| 072 | RLS tenant_id on receipts |
| 073 | Deploy MCP SSE on `virlux-api.vercel.app` path `/mcp` |
| 074 | Edge auth middleware |
| 075 | Separate from SourceA Supabase |
| 076 | Signed export URL for certainty ZIP |
| 077 | `verify:live` evidence URL in receipt |
| 078 | Preview federation to motor |
| 079 | Free tier first |
| 080 | ROI before Railway scale-up |

### T09 Receipt schemas (081–091)

| # | Task |
|---|------|
| 081 | `virlux-certainty-report-v1` schema |
| 082 | Witness GitHub PR number in receipt |
| 083 | Verdict MOCK_ONLY until premium |
| 084 | `evidence_url` → `#async-tracking` live |
| 085 | Federation envelope to SourceA |
| 086 | Extend `emit-verify-receipt.py` cloud mode |
| 087 | Fixtures from last 18/18 run |
| 088 | RunReceipt ZIP export |
| 089 | Agency buyer mapping |
| 090 | Honest counter copy |
| 091 | Incident on live/mock mismatch |

### T10 Monetization (092–101)

| # | Task |
|---|------|
| 092 | Sandbox $0 MOCK_ONLY |
| 093 | Freemium 5 runs/day |
| 094 | Premium bay `virlux-rent-line-v1` |
| 095 | Team hire `team-delivery-ship-it` |
| 096 | Pay on prove — first green receipt |
| 097 | Metered verify minutes P3 |
| 098 | AF-SPRINT lane copy |
| 099 | 30s demo in Marketplace video |
| 100 | `/dashboard/factory` CTA to MCP install |
| 101 | `plan:validate` includes mcp chain |

### T11 Gateway + SHIP (102–111)

| # | Task |
|---|------|
| 102 | Composio receipt-layer partner doc |
| 103 | Optional gateway middleware branch |
| 104 | Enterprise audit export format |
| 105 | Playwright MCP + virlux-verify chain demo |
| 106 | Registry card Infrastructure category |
| 107 | Datadog defer post-pilot |
| 108 | Per-agent tool allowlist doc |
| 109 | Hash chain on receipts P2 |
| 110 | 1 agency design partner |
| 111 | **SHIP:** Registry live + Cloud Agent connect + 18/18 gate |

---

## 5. Cloud worker first command

```bash
cd ~/Desktop/VIRLUX
npm run mcp:chain:pick -- --step 031
# Creates packages/mcp-verify-factory → deploy virlux-api
```

**Sync law:** Copy this file to `os/plan-library/SOURCEA_SUGGESTION_MCP_CHAIN_LOCKED_v1.md` on pick step 001.
