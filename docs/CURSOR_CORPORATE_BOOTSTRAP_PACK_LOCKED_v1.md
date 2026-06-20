# Cursor Corporate Bootstrap Pack — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T06:34:29Z · **Authority:** ASF  
**Path:** `docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md`  
**Upgrades:** Gemini Master Blueprint · SourceA governance stack · MCP chain campuses

---

## One sentence

> **Enterprise monorepo skeleton** — cascading Cursor rules, machine ledger, context index (not mega-paste), isolated sub-factories, shared Zod contracts, Supabase migrations — wired to SourceA goals (governance receipts · commercial W3 · video factory · Apple billing).

---

## Enterprise workspace tree (SourceA-native)

```text
~/Desktop/SourceA/
├── .cursorrules                         # @context pointers (Promax compatibility)
├── .cursor/
│   ├── rules/
│   │   ├── 000-entry-gate.mdc           # session gate · RUN INBOX
│   │   ├── 000-cross-lane-edit-forbidden.mdc
│   │   ├── 024-cursor-enterprise-bootstrap.mdc   # this pack
│   │   └── … (000–023 existing law)
│   ├── skills/                          # invoke-on-demand factories
│   └── hooks.json                       # sessionStart · stop
├── docs/
│   ├── architecture_ledger.json       # @context alias → data/cursor-bootstrap-ledger-v1.json
│   ├── COMPLETE_CONTEXT.md              # router only — read CURSOR_CONTEXT_INDEX
│   ├── CURSOR_CONTEXT_INDEX_LOCKED_v1.md
│   ├── SCALE_EVOLUTION_LOCKED_v1.md
│   └── CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md   # this file
├── data/
│   ├── cursor-bootstrap-ledger-v1.json  # machine GPS (immutable contracts)
│   ├── cursor-corporate-bootstrap-master-v1.json
│   └── mcp-chain-campus-registries-v1.json
├── shared/
│   ├── types/                           # Zod + TS — single source of types
│   ├── database/migrations/             # Supabase SQL migrations
│   └── utils/                           # cloud clients (no secrets in repo)
├── apps/
│   ├── video-ad-factory/                # ElevenLabs · Fal · orchestration
│   ├── apple-store-api/                 # StoreKit 2 · push (PHASE_2)
│   └── analytics-intelligence/          # token telemetry (PHASE_3)
├── packages/
│   └── mcp-sourcea-verify/              # MCP receipt layer (shipped)
├── scripts/
│   ├── validate-cursor-bootstrap-v1.sh
│   ├── agent_session_gate_run_v1.py
│   └── pre_write_guard_v1.py
├── .env.example
└── cursor-plugin/sourcea-forge-governance/
```

---

## Global governance (root — supersedes generic `.cursorrules` prose)

1. **No local heavy AI** on Mac focus path — cloud APIs only (Fal, ElevenLabs, Supabase Edge).  
2. **Factory isolation** — `video-ad-factory` ↔ `apple-store-api` only via Supabase or typed HTTP.  
3. **Disk before chat** — session gate + ledger before substantive edits.  
4. **MCP read-only** — never write `~/.sina` from MCP tools.  
5. **Types frozen** — change `shared/types/` + ledger `epoch` together.

---

## Sub-factory map

| Factory | Path | Cursor rules | Cloud |
|---------|------|--------------|-------|
| Governance / verify | `packages/mcp-sourcea-verify` | root `000-*` | Vercel SSE |
| Video ad | `apps/video-ad-factory/` | `apps/video-ad-factory/.cursor/rules/` | Supabase Edge + Fal + ElevenLabs |
| Apple / billing | `apps/apple-store-api/` | `apps/apple-store-api/.cursor/rules/` | APNS + StoreKit server |
| Analytics | `apps/analytics-intelligence/` | reserved PHASE_3 | Supabase read models |

---

## Validate (one tap)

```bash
bash scripts/validate-cursor-bootstrap-v1.sh
```

---

## Related campuses (separate repos)

See `data/cursor-corporate-bootstrap-master-v1.json` — VIRLUX · Noetfield · TrustField each copy ledger pattern.
