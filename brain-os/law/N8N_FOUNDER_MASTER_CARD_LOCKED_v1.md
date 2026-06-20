# N8N Founder Master Card (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-14 · **Status:** LOCKED  
**Canonical:** `~/Desktop/SourceA/N8N_FOUNDER_MASTER_CARD_LOCKED_v1.md`  
**Law:** `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`  
**Plan:** `N8N_AUTOMATION_EXECUTION_PLAN_LOCKED_v2.md`

**Apps:** N8N Integration (:13026) · Mac Health Guard (:13024) · n8n UI (:5678)

## Today

**P0 status:** OPERATIONAL COMPLETE — see `~/.sina/n8n-receipts/health/p0-operational-pass.json`

1. Open **N8N Integration** app on Desktop.
2. Tap **Open n8n UI** → Import `sinaai-stack-health-ping.json` → **Execute once**.
3. Tap **⚡ Activate Cooldown WF8** → toggle **Active ON** (top-right in n8n) → registers webhook.
4. Open **Mac Health Guard** → tap **Cool Down** or **Brain heal** once.
5. In N8N Integration report, confirm stack health is green or yellow (hub quarantined = yellow OK).

**If webhook 404:** Repeat step 3 — toggle Active OFF then ON once in n8n.

## What runs automatically (after you enable crons in n8n)

| Workflow | Schedule | Does |
|----------|----------|------|
| stack-health-ping-15m | 15m | Red/green dashboard |
| factory-queue-sweeper | hourly | Kill leaked queue zombies |
| disk-live-wire-watchdog | 30m | Disk wire check → Mac Health finding |
| governance-fast-15m | 15m | Fast governance audit |
| poison-track-reminder | daily | PT-C step reminders |
| run-inbox-reminder | hourly | Factory stuck notify only |

**Default:** all crons OFF until 2 manual PASS each.

## Never enable without ASF order

- `sinaai-telegram-agents` (Runtime bot is the one listener)

## Read receipts (no Terminal)

- `~/.sina/n8n-receipts/health/` — stack + cooldown
- `~/.sina/n8n-intelligence/brief-latest.md` — product brief
- `~/.sina/n8n-receipts/FINAL_AUTOMATION_PASS_v2.json` — all tiers complete

## Paid n8n features not needed

SSO · Git sync · Environments · External Secrets · advanced log streaming
