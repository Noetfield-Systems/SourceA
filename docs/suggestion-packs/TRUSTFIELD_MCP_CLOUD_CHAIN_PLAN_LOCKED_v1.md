# TrustField MCP Cloud Chain Plan — LOCKED v1 (111 steps)

**Version:** 1.0.0 · **Saved:** 2026-06-19T12:00:00Z · **Authority:** ASF suggestion from SourceA  
**Copy target:** `~/Desktop/TrustField Technologies/os/plan-library/SOURCEA_SUGGESTION_MCP_CHAIN_LOCKED_v1.md`  
**Campus:** Compliance / MSB · FINTRAC evidence · sandbox routing  
**Motor (read-only):** SourceA FBE  
**Site:** `web/app/factory/page.tsx` → `/factory`

---

## 0. Chain position

| Role | Primary | Buyer |
|------|---------|-------|
| **Campus host** | `trustfield-compliance` MCP | MSB · compliance officers |
| **Chain provider** | `checklist_status` · `evidence_export` | FINTRAC-ready audit trail |
| **Chain consumer** | Supabase MCP · Stripe MCP · GitHub | "Works with" stack proof |

**One sentence:** MSB remains settlement party of record — we export evidence of compliant agent runs.

**Mac:** Control plane only. **Cloud:** Vercel Next.js + Railway + Supabase (TrustField portfolio lane).

---

## 1. Cloud architecture

```text
Cursor Cloud Agent
    → Supabase MCP (read MSB sandbox data)
    → Stripe MCP (checkout events — read posture)
    → trustfield-compliance MCP
        → checklist_status · evidence_export · sandbox_compliance_run
    → FINTRAC-oriented JSON/ZIP export
Mac Hub — founder Actions link only
```

---

## 2. MCP spec (`io.github.trustfield/trustfield-compliance`)

```json
{
  "tools": [
    { "name": "sandbox_compliance_run", "input": { "partner_id": "string", "mock_only": true }, "output": { "verdict": "PASS|FAIL|MOCK_ONLY", "checklist_line": "string", "demo_seconds": 30 } },
    { "name": "checklist_status", "input": { "receipt_id": "string" }, "output": { "items": [], "completion_pct": "number" } },
    { "name": "evidence_export", "input": { "receipt_id": "string", "format": "fintrac_json|audit_zip" }, "output": { "export_url": "string", "settlement_boundary": "string" } },
    { "name": "list_factories", "input": {}, "output": { "factories": [], "BOUNDARY_LINE": "string" } }
  ]
}
```

**Marketplace card:** **TrustField Compliance Factory** · Categories: **Infrastructure** · **Agent Orchestration**

**Locked copy:** Always inject `BOUNDARY_LINE` from `web/lib/company-copy.ts` — MSB settlement boundary.

---

## 3. Learn from market (applied)

| Insight | TrustField action |
|---------|-------------------|
| Cursor Marketplace Stripe plugin | Consumer — billing events witness only |
| Supabase MCP free tier | Campus data lane — not SourceA SSOT |
| Regulated buyers need export not logs | `evidence_export` first-class tool |
| Platform-neutral SaaS copy law | No "Mac only" in MCP descriptions |
| Enterprise MCP gateway audit store | Feed evidence_export format P2 |

---

## 4. Steps 001–111

### T01 Chain consumer (001–010)

| # | Cloud worker task |
|---|-------------------|
| 001 | Supabase MCP read-only — sandbox MSB tables only |
| 002 | Stripe MCP read posture — no custody claims in tools |
| 003 | GitHub MCP — `run_no_asf_verify.sh` workflow link |
| 004 | Linear issue template compliance receipt |
| 005 | `./scripts/demo_sprint_status.sh` remains local SSOT |
| 006 | MCP never writes compliance SSOT on Mac |
| 007 | `BOUNDARY_LINE` in every tool response |
| 008 | Fixture `fixtures/msb-sandbox-mock.json` |
| 009 | MOCK_ONLY default |
| 010 | `validate-trustfield-factory-catalog.sh` mcp section |

### T02 trustfield-compliance MCP (011–020)

| # | Task |
|---|------|
| 011 | `packages/mcp-compliance/` in monorepo |
| 012 | `sandbox_compliance_run` wraps compliance factory spec |
| 013 | 30s demo · checklist_line human readable |
| 014 | `checklist_status` from Supabase |
| 015 | `evidence_export` FINTRAC JSON schema |
| 016 | `list_factories` from REGISTRY.json |
| 017 | SSE route `web/app/api/mcp/sse/route.ts` |
| 018 | stdio package for local dev |
| 019 | API key per MSB partner_id |
| 020 | OpenAPI `web/openapi/mcp-compliance-v1.yaml` |

### T03 Campus catalog API (021–030)

| # | Task |
|---|------|
| 021 | `GET /api/factory/catalog` Next route |
| 022 | `/factory` page fetch API not relative `../../../os/` |
| 023 | Studio tab cloud spec URL |
| 024 | Sandbox Bay calls MCP proxy route |
| 025 | Teams tab premium API |
| 026 | `trustfield-rent-line-v1.json` P2 in catalog |
| 027 | MSB program factory card |
| 028 | Federation webhook SourceA motor |
| 029 | SITE_LAYOUT.nav Build Factory already wired |
| 030 | `bash scripts/validate-trustfield-factory-catalog.sh` mcp |

### T04 Cloud worker runtime (031–042)

| # | Task |
|---|------|
| 031 | **PICK** — deploy MCP SSE on Vercel `trustfield-web` |
| 032 | Supabase compliance receipts table |
| 033 | `emit-compliance-receipt.py` cloud mode |
| 034 | CI: tsc + validate-trustfield-factory-catalog |
| 035 | Preview PR deploy |
| 036 | Structured compliance audit logs |
| 037 | Cron retention + purge policy |
| 038 | Idempotent sandbox_compliance_run |
| 039 | p99 < 1s checklist_status |
| 040 | Degrade MOCK_ONLY if partner unknown |
| 041 | Mac docs cloud URLs |
| 042 | `bash scripts/pick_mcp_chain_step.sh N` |

### T05 Registry (043–050)

| # | Task |
|---|------|
| 043 | npm `@trustfield/mcp-compliance` |
| 044 | Official MCP Registry |
| 045 | `io.github.trustfield/trustfield-compliance` |
| 046 | Glama: "MSB compliance receipt" |
| 047 | README bilingual EN/FR stub |
| 048 | SECURITY.md settlement boundary |
| 049 | v1.0.0 tag |
| 050 | Linear MCP-PUBLISH-trustfield |

### T06 Cursor plugin (051–060)

| # | Task |
|---|------|
| 051 | Plugin manifest + Stripe/Supabase MCP bundle |
| 052 | Skills: platform-neutral copy |
| 053 | Rules: BOUNDARY_LINE injection |
| 054 | mcp.json fragment |
| 055 | Demo: sandbox run → evidence_export |
| 056 | Infrastructure category |
| 057 | Enterprise marketplace doc |
| 058 | Cloud Agent "MSB Compliance" preset |
| 059 | Allowlist read-only Supabase |
| 060 | T1 disclosure |

### T07 GitHub + Linear (061–070)

| # | Task |
|---|------|
| 061 | GitHub Action `no-asf-verify` + MCP receipt |
| 062 | PR compliance badge |
| 063 | Linear compliance issues |
| 064 | Label `fintrac-evidence` |
| 065 | GTM mirror |
| 066 | Link `last_verify_gate` in plan.json |
| 067 | Cursor↔Linear |
| 068 | No TF queue in Linear |
| 069 | Integration Leverage |
| 070 | MSB partner one-liner |

### T08 Supabase + Vercel (071–080)

| # | Task |
|---|------|
| 071 | Supabase `compliance_receipts` |
| 072 | RLS partner_id |
| 073 | Vercel deploy `/factory` + `/api/mcp` |
| 074 | Edge auth |
| 075 | Portfolio-separated from SourceA |
| 076 | Signed evidence_export URL |
| 077 | www.trustfield.ca/demo proof URL |
| 078 | Preview federation |
| 079 | Free tier |
| 080 | CAD 4K discovery ROI gate |

### T09 Receipt schemas (081–091)

| # | Task |
|---|------|
| 081 | `trustfield-compliance-receipt-v1` |
| 082 | checklist_line required |
| 083 | settlement_boundary required |
| 084 | fintrac_json export schema |
| 085 | Federation envelope |
| 086 | emit-compliance-receipt cloud |
| 087 | Fixtures from factory page mock |
| 088 | audit_zip export |
| 089 | FINTRAC mapping appendix (honest) |
| 090 | Not certified disclaimer |
| 091 | Incident on boundary omission |

### T10 Monetization (092–101)

| # | Task |
|---|------|
| 092 | Sandbox $0 |
| 093 | Freemium 10 calls/day |
| 094 | Premium FINTRAC export |
| 095 | MSB program tier |
| 096 | Team hire compliance crew |
| 097 | Rent line P2 |
| 098 | CAD 4K discovery copy |
| 099 | 30s demo |
| 100 | `/factory` MCP CTA |
| 101 | commercial_blocked flip rules |

### T11 Gateway + SHIP (102–111)

| # | Task |
|---|------|
| 102 | Composio receipt partner (support Noetfield lead) |
| 103 | evidence_export gateway format |
| 104 | Immutable audit alignment |
| 105 | Middleware branch |
| 106 | Registry Infrastructure |
| 107 | Datadog defer |
| 108 | MSB tool allowlist |
| 109 | Hash chain P2 |
| 110 | 1 MSB design partner |
| 111 | **SHIP:** Registry + demo MSB sandbox + evidence export |

---

## 5. Cloud worker first command

```bash
cd ~/Desktop/TrustField\ Technologies
bash scripts/pick_mcp_chain_step.sh 031
cd web && npx tsc --noEmit
```

**Boundary law:** Every MCP response includes settlement boundary — MSB is party of record, TrustField is infra.
