---
name: hub-pro-mac-session
description: >-
  Hub Pro Mac founder session rules — INCIDENT-039 no validator stuck, light
  checks only, receipts as proof, cloud CI for heavy e2e. Mandatory for all
  agents on Mac during founder work.
---

# Hub Pro — Mac founder session

**INCIDENT-039 P0:** Never stuck in validators on Mac — 11+ min = harm  
**Rule:** `.cursor/rules/034-mac-no-validator-stuck-red-flag.mdc`  
**Control plane:** `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`

## Every turn on Mac

1. Reply founder in **<30s** plain English + disk path
2. **Max ONE** light shell **≤90s**
3. Proof = read `~/.sina/*-receipt*.json` — not validator marathon
4. Never chain `validate-* && validate-*`

## Allowed light checks

```bash
curl -sf http://127.0.0.1:13020/health
python3 scripts/hub_pro_skills_v1.py --app worker_hub --json
read ~/.sina/hub-form-submit-receipt-v1.json
```

## Forbidden during founder session

- `validate-all-e2e` · surfaces E2E marathon
- `build-mac-health-standalone-app-v1.sh` (heavy gate)
- `Await` validators across turns until green
- Regenerate JSON + validate loop to prove a chat answer

## Where heavy proof runs

- Railway / cloud CI ship window
- Touch `~/.sina/asf-ship-window-v1.flag` for build scripts with `_founder_session_gate`

## Hub Pro skills usage on Mac

- Read skills → light curl e2e → fix → append log
- Use **API Station** in Hub UI instead of Worker chat for ops
- Use **Hub Pro tab** for last experience per app

## Mac control plane flags

| Flag | Meaning |
|------|---------|
| `~/.sina/mac-control-plane-v1.flag` | Mac = control panel only |
| `~/.sina/cli-disabled-v1.flag` | No local CLI drain |
| `~/.sina/api-disabled-v1.flag` | **must be absent** — Mac may call cloud APIs |

Boot: `bash ~/Desktop/Noetfield-Systems/SourceA/scripts/enter-mac-control-plane-v1.sh`
