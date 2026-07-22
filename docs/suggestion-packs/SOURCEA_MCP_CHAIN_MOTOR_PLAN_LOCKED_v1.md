# SourceA MCP Chain Motor Plan — LOCKED v1 (111 steps)

**Version:** 1.0.0 · **Saved:** 2026-06-19T12:00:00Z · **Authority:** ASF suggestion · SourceA motor only  
**Path:** `~/Desktop/SourceA/docs/suggestion-packs/SOURCEA_MCP_CHAIN_MOTOR_PLAN_LOCKED_v1.md`  
**Cloud worker:** Builds `packages/mcp-sourcea-verify/` · deploys to Vercel/CF Worker · Mac reads federated receipts only  
**Law:** `docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md` §2 two-plane · `docs/SOURCEA_MCP_STACK_FREE_TIER_OPTIMIZATION_LOCKED_v1.md`

---

## 0. Position in chain

| Role | Primary | Secondary |
|------|---------|-----------|
| Chain **provider** | `sourcea-verify` MCP | Receipt federation API |
| Chain **consumer** | GitHub · Linear · browser MCP | After-action verify |
| Campus **motor** | FBE compile/spawn (read-only from campuses) | Hub `:13020` control plane |

**One sentence:** Prove agent actions across any MCP host — read-only verify, never replace execution.

---

## 1. Cloud architecture (Mac = control panel)

```text
Mac (:13020 Hub · session gate · RUN INBOX)
    │ read-only poll / federation webhook
    ▼
Cloud: sourcea-verify MCP (Vercel/CF)
    │ verify_run · factory_status · form_pick_parse
    ▼
Object store: receipts/{receipt_id}.json (R2 or Supabase bucket)
    ▲
Campus MCPs (virlux · noetfield · trustfield) emit campus receipts → federate
```

---

## 2. MCP tool spec (`sourcea-verify`)

```json
{
  "server": "io.github.sinakazemnezhad/sourcea-verify",
  "transport": "stdio|sse",
  "tools": [
    {
      "name": "verify_run",
      "description": "Return PASS/FAIL + receipt JSON for a run id (read-only)",
      "input": { "receipt_id": "string", "campus": "optional enum" },
      "output": { "verdict": "PASS|FAIL|MOCK_ONLY", "receipt": "object", "export_url": "string" }
    },
    {
      "name": "factory_status",
      "description": "Read-only factory_now_line + queue head (no ~/.sina writes)",
      "input": { "surface": "enum:hub|brain|inbox" },
      "output": { "factory_now_line": "string", "queue_sa": "string", "as_of": "iso" }
    },
    {
      "name": "form_pick_parse",
      "description": "Parse ASF FIVE-STEP PICK block → structured decision JSON",
      "input": { "raw_pick": "string" },
      "output": { "subject": "string", "pick": "A|B|C|D", "effect": "string" }
    },
    {
      "name": "emit_receipt_readonly",
      "description": "Validate receipt schema only — does NOT write Mac disk",
      "input": { "receipt": "object" },
      "output": { "schema_ok": "boolean", "violations": "array" }
    }
  ]
}
```

---

## 3. Cursor plugin bundle (P1)

**Marketplace card:** `SourceA Forge Governance` · Category: **Agent Orchestration** + **Infrastructure**

```json
{
  "name": "sourcea-forge-governance",
  "mcpServers": {
    "sourcea-verify": {
      "url": "https://mcp.sourcea.app/sse",
      "headers": { "Authorization": "Bearer ${SOURCEA_MCP_TOKEN}" }
    }
  },
  "skills": ["agent-self-audit-loop", "sina-conscious-recovery"],
  "rules": [".cursor/rules/agent-disk-live-wire-first.mdc"]
}
```

**Cloud Agents:** Enable in Team dashboard · scope `sourcea-verify` to review agent only (Cursor 3 per-agent MCP scoping).

---

## 4. Implementation steps 001–111

### T01 Chain consumer (001–010)

| Step | Action | Cloud/Mac | Done when |
|------|--------|-----------|-----------|
| 001 | Enable GitHub MCP per `data/cursor-mcp-free-tier-manifest-v1.json` | Mac config | GOV-8 closed |
| 002 | Linear MCP authenticated · Integration Leverage project | Mac | Issue sync test |
| 003 | Browser MCP for pilot demo only (T2 disclosure) | Mac | One verify screenshot |
| 004 | Document post-PR hook: GitHub action → `verify_run` | Cloud | Workflow YAML in repo |
| 005 | Linear issue template `MCP-RECEIPT-{id}` | Mac | Template on disk |
| 006 | Never wire MCP to write `~/.sina/*` — lint rule | Mac | CI grep PASS |
| 007 | Session gate remains pre-ship authority | Mac | Gate receipt ok=true |
| 008 | RUN INBOX unchanged — MCP assists only | Mac | Worker audit PASS |
| 009 | Map consumer calls in `data/mcp-chain-campus-registries-v1.json` | Mac | JSON updated |
| 010 | Receipt sample in `receipts/mcp-chain-consumer-demo.json` | Mac | Valid schema |

### T02 Receipt MCP provider (011–020)

| Step | Action | Cloud | Done when |
|------|--------|-------|-----------|
| 011 | Scaffold `packages/mcp-sourcea-verify/` (TypeScript MCP SDK) | Cloud repo path | `npm run build` |
| 012 | Implement `verify_run` read from R2/Supabase bucket | Cloud | Unit test PASS |
| 013 | Implement `factory_status` via federated API (not Mac fs) | Cloud | SSE endpoint 200 |
| 014 | Implement `form_pick_parse` pure function | Cloud | 79-question fixture test |
| 015 | Implement `emit_receipt_readonly` JSON schema validate | Cloud | FAIL on bad receipt |
| 016 | SSE transport for Cursor Cloud Agents | Cloud | Cursor dashboard connect |
| 017 | stdio transport for local dev | Cloud package | `npx @sourcea/mcp-verify` |
| 018 | Auth: API key per tenant · rate limit | Cloud | 429 on abuse |
| 019 | OpenAPI spec `openapi/mcp-verify-v1.yaml` | Cloud | Published |
| 020 | Health `GET /health` + `GET /ready` | Cloud | Monitor green |

### T03 Campus catalog API (021–030) — motor aggregates

| Step | Action | Cloud | Done when |
|------|--------|-------|-----------|
| 021 | `GET /v1/campuses` lists VIRLUX·NF·TF | Cloud | JSON index |
| 022 | Proxy read-only campus `list_factories` | Cloud | 3 campuses wired |
| 023 | Honest label resolver MOCK_ONLY/freemium/premium | Cloud | Unit tests |
| 024 | CORS allow Cursor Cloud Agent origins | Cloud | Preflight PASS |
| 025 | Cache campus catalog 5m TTL | Cloud | Stale banner |
| 026 | Version pin per campus spec_version | Cloud | Breaking change detect |
| 027 | Error envelope `receipt_native_error_v1` | Cloud | Schema locked |
| 028 | Federation webhook from campus → motor | Cloud | HMAC signed |
| 029 | Mac Hub widget read-only embed URL | Mac | iframe or link |
| 030 | Validator `validate-mcp-chain-motor-v1.sh` | Mac | PASS |

### T04 Cloud worker runtime (031–042)

| Step | Action | Cloud | Done when |
|------|--------|-------|-----------|
| 031 | **PICK** — Vercel project `sourcea-mcp-verify` | Cloud | Deploy preview |
| 032 | Env: `RECEIPT_BUCKET` `MCP_API_KEYS` | Cloud | Secrets set |
| 033 | Dockerfile optional for Railway fallback | Cloud | Image builds |
| 034 | CI: test → build → deploy on main | Cloud | Green pipeline |
| 035 | Preview URL per PR | Cloud | Comment bot |
| 036 | Log drain JSON (no Mac command-server) | Cloud | Structured logs |
| 037 | Worker cron: federate poll campuses | Cloud | 15m job |
| 038 | Idempotency keys on verify_run | Cloud | Duplicate safe |
| 039 | p99 latency target <800ms read | Cloud | Dashboard |
| 040 | Graceful degrade if campus down | Cloud | Partial catalog |
| 041 | Mac control plane documents cloud URLs only | Mac | Hub card |
| 042 | `scripts/mcp_chain_pick_v1.py --step N` | Mac | Pick works |

### T05 Registry publish (043–050)

| Step | Action | Surface | Done when |
|------|--------|---------|-----------|
| 043 | npm package `@sourcea/mcp-verify` | npm | Published |
| 044 | Official MCP Registry metadata submit | registry.modelcontextprotocol.io | Namespace verified |
| 045 | Reverse DNS `io.github.sinakazemnezhad/sourcea-verify` | Registry | Listed |
| 046 | Glama/Smithery listing copy (governance receipt) | Discovery | Searchable |
| 047 | README: chain-friendly · read-only | GitHub | Partner quote |
| 048 | Security.md — no Mac disk write | GitHub | Audit readable |
| 049 | Version semver + changelog | GitHub | v1.0.0 tag |
| 050 | Linear GOV issue MCP-PUBLISH-sourcea closed | Linear | Receipt linked |

### T06 Cursor plugin bundle (051–060)

| Step | Action | Surface | Done when |
|------|--------|---------|-----------|
| 051 | Plugin manifest `cursor-plugin/sourcea-forge-governance.json` | Repo | Valid schema |
| 052 | Skills point to existing `.cursor/skills/*` | Repo | Paths relative |
| 053 | Rules: disk-live-wire + session gate reminder | Repo | No prohibition dump |
| 054 | One-click mcp.json fragment in plugin | Marketplace | Install test |
| 055 | Demo skill: verify after GitHub PR | Skill | Recording |
| 056 | Category tags: Agent Orchestration, Infrastructure | Marketplace | Approved |
| 057 | Private team marketplace doc for enterprise | Docs | T3 only |
| 058 | Cloud Agent preset "Governed Worker" | Cursor | MCP scoped |
| 059 | permissions.json allowlist verify_run read | Cursor | Auto-review safe |
| 060 | Founder disclosure ladder T1 badge copy | Docs | No T0 MCP lead |

### T07 GitHub + Linear (061–070)

| Step | Action | Done when |
|------|--------|-----------|
| 061 | GitHub Action: on PR → call verify_run | Workflow green |
| 062 | PR comment PASS/FAIL badge | Comment posts |
| 063 | Linear GOV-5..10 linked to MCP steps | Issues traceable |
| 064 | Issue label `mcp-receipt` | Label applied |
| 065 | Weekly mirror commercial cp-* not every sa-* | Policy doc |
| 066 | GitHub MCP create issue — receipt follows | Demo |
| 067 | Linear Cursor official integration cited | T1 badge |
| 068 | No second queue in Linear | Audit PASS |
| 069 | Integration Leverage project view | Dashboard |
| 070 | Partner email template one-liner | GTM doc |

### T08 Supabase + Vercel (071–080)

| Step | Action | Done when |
|------|--------|-----------|
| 071 | Receipt bucket Supabase Storage (or R2) | Bucket live |
| 072 | RLS: tenant read own receipts | Policy test |
| 073 | Vercel Gate K deploy motor MCP | URL 200 |
| 074 | Edge middleware auth | 401 without key |
| 075 | Separate from campus Supabase projects | Portfolio law |
| 076 | Export signed URL 15m TTL | Download works |
| 077 | No SourceA SSOT in Supabase | Validator PASS |
| 078 | Vercel preview for campus federation | Preview chain |
| 079 | Cost: free tier first | NO-CC law |
| 080 | ROI gate before paid tier | Receipt logged |

### T09 Receipt schemas (081–091)

| Step | Action | Done when |
|------|--------|-----------|
| 081 | `sourcea-mcp-receipt-v1` JSON schema | Schema file |
| 082 | `mcp-action-witness-v1` wraps tool call metadata | Schema file |
| 083 | Verdict enum PASS/FAIL/MOCK_ONLY | Documented |
| 084 | `export_url` for board/FINTRAC handoff | Field spec |
| 085 | Campus receipt federation envelope | Schema |
| 086 | Validator script cross-campus | PASS |
| 087 | Sample receipts ×3 campuses | Fixtures |
| 088 | Zip export RunReceipt compatible | Pilot doc |
| 089 | NIST AI RMF mapping appendix | Sales doc |
| 090 | SOC2 direction not certification | Honest copy |
| 091 | Incident row if schema drift | brain-os |

### T10 Monetization (092–101)

| Step | Action | Done when |
|------|--------|-----------|
| 092 | Free: verify_run read 100/day | Rate limit |
| 093 | Freemium: federated campus catalog | $0 |
| 094 | Premium: export_url + retention 1y | SKU doc |
| 095 | Enterprise: VPC SSE endpoint | P3 spec |
| 096 | No invoice until pilot proof | PREMORTEM-017 |
| 097 | Stripe deferred P3 | Flag |
| 098 | Price band $50K–$200K/yr positioning only | Market doc |
| 099 | Pilot demo script 90s | Recording |
| 100 | Hub CTA links cloud verify URL | UI card |
| 101 | Honest_done via goal-progress only | Script PASS |

### T11 Gateway partner P2 (102–111)

| Step | Action | Done when |
|------|--------|-----------|
| 102 | Composio partner posture doc (receipt not compete) | LOCKED md |
| 103 | Noetfield leads gateway policy pack | Cross-ref |
| 104 | Immutable audit log format | Schema |
| 105 | Optional gateway middleware PoC | Branch |
| 106 | Enterprise registry card metadata | JSON |
| 107 | Tyk/MintMCP pattern study archived | Research |
| 108 | ABAC: tool allowlist per agent | Spec |
| 109 | Tamper-evident hash chain on receipts | P2 |
| 110 | Pilot with 1 enterprise design partner | CRM row |
| 111 | **SHIP GATE:** P1 publish complete + 3 campus federates | All validators PASS |

---

## 5. Cloud worker first pick

```bash
cd ~/Desktop/SourceA
python3 scripts/mcp_chain_pick_v1.py --campus sourcea --step 031 --json
# Scaffold packages/mcp-sourcea-verify → Vercel deploy
```

**Mac forbidden:** production verify compute · writing receipts via MCP · skipping session gate.
