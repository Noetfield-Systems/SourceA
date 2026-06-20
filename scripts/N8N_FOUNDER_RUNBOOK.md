# n8n founder runbook

**Law:** [SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md](../SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md)

## Start

1. Hub **Actions → Start n8n** (or `~/Desktop/SourceA/scripts/founder-start-n8n.sh`)
2. Hub **Run extended n8n test** (or `bash scripts/validate-n8n.sh`) — hub + n8n required; Runtime `:8000` for full extended PASS

CLI:

```bash
cd ~/Desktop/SourceA
bash scripts/validate-n8n.sh          # full suite
python3 scripts/n8n_automation.py extended
python3 scripts/n8n_automation.py validate
```

## Expected starter test

| Step | Required |
|------|----------|
| Hub :13020 | Yes |
| Runtime :8000 | No (warn if down) |
| n8n :5678 | Yes for full PASS |
| Workflow JSON on disk | Yes |

## Extended test (additional)

| Step | Required |
|------|----------|
| Workflow manifest (2 JSON files) | Yes |
| Health ping dry-run (hub + runtime HTTP) | Yes |
| n8n `/healthz` | Yes when n8n up |

Fixtures: `scripts/fixtures/n8n/workflow_manifest.json`

## Intelligence (product signals)

| Step | Command / UI |
|------|----------------|
| Capture | Hub **Capture intelligence** or `POST /api/n8n/intelligence` `{"action":"capture"}` |
| Read brief | `~/.sina/n8n-intelligence/brief-latest.md` |
| Scheduled | Import `sinaai-intelligence-pipeline.json` in n8n (6h) |
| Webhook | Import `sinaai-product-signal-webhook.json` → path `sinaai-product-signal` |

**After code changes:** restart Sina Command hub once so `:13020/api/n8n/intelligence` loads.

Doc: `SinaaiDataBase/governance/N8N_INTELLIGENCE.md`

## Policy

- **One** Telegram listener: built-in Runtime bot **or** n8n workflow — never both.
- n8n is glue only — not prompt SSOT.

## Tier gates (v2)

| Tier | Validator | What |
|------|-----------|------|
| 0 | `bash scripts/validate-n8n-tier0-v1.sh` | Config, receipts, glue runner, Mac Health + n8n up |
| 1 | `validate-n8n-tier1-v1.sh` | WF1 v2 + cooldown ingest |
| 2 | `validate-n8n-tier2-v1.sh` | Queue sweep, disk wire, CPU pause |
| 3 | `validate-n8n-tier3-v1.sh` | Governance fast, poison, factory notify |
| 4 | `validate-n8n-tier4-v1.sh` | Product signals |
| 5 | `validate-n8n-tier5-v1.sh` | Judge, thread scout, OpenRouter shadow |
| 6 | `validate-n8n-full-manifest-v1.sh` | All 18 workflows on disk |

Full suite: `bash scripts/validate-n8n.sh`

P0 operational gate: `bash scripts/validate-n8n-p0-operational-v1.sh` · close script: `python3 scripts/n8n_p0_operational_close_v1.py`

Glue runner: `python3 scripts/n8n_glue_runner_v1.py health`

Config: `~/.sina/n8n-glue-config-v1.json` (hub_mode quarantined when hub off)

Receipts: `~/.sina/n8n-receipts/`

**Founder:** N8N Integration app :13026 — no Terminal. Import workflows in n8n UI after Tier 0 PASS.

**Canonical plan:** `N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md` · **Founder card:** `N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md`
