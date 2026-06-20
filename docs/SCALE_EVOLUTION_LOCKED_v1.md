# Scale evolution — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T06:34:29Z · **Authority:** ASF  
**Path:** `docs/SCALE_EVOLUTION_LOCKED_v1.md`  
**Parent:** `docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md`

---

## Phases (extend without rewriting base)

| Phase | Focus | Adds | Must not break |
|-------|--------|------|----------------|
| **P0** (now) | Governance + MCP receipt chain | `packages/mcp-sourcea-verify` · hub `:13020` · session gate | `000-*` rules · `~/.sina` receipts |
| **P1** | Video ad factory orchestration | `apps/video-ad-factory/orchestration` · ElevenLabs edge | Factory isolation · Zod types |
| **P1B** | Human-in-the-loop prompt tuning | `apps/video-ad-factory/loop-validator` | `HUMAN_APPROVAL_REQUIRED` state machine |
| **P2** | Apple StoreKit + push | `apps/apple-store-api/billing` | No AI code in billing package |
| **P3** | Analytics intelligence | `apps/analytics-intelligence/telemetry` | Read-only from `resource_logs` |

---

## Vendor swap rule (rendering-bridge)

If Fal.ai → Runway/Sora: change **only** `apps/video-ad-factory/rendering-bridge/`. Ledger `service_integrations.fal_ai` row bumps `epoch`.

---

## Cross-platform rule

New client (`web-app-api`, Android): new `apps/<client>-api/` with own `.cursor/rules/`. **Never** import `video-ad-factory` into billing.

---

## Corporate Promax migration

1. Mac cleanup (no `~/.sina` delete)  
2. Cursor corporate login + Resync Index  
3. `bash scripts/validate-cursor-bootstrap-v1.sh`  
4. Team MCP SSE + plugin bundles from `cursor-plugin/`
