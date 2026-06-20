# Wire + iPhone — ASF reference (hub taps)

## What wire is

**AI Dev Bridge OS** — phone Safari desk → Mac agent → SinaPromptOS orchestrator → PASS/FAIL on phone.

**Not** the App Store “IDE For Cursor” purple app. **Not** Cursor OS Pro Flutter lane.

---

## Lanes on phone

| Lane | Use |
|------|-----|
| `smoke` | ~5s test only — proves phone ↔ Mac |
| `full_m8` | **Production** — real Mac stack (long run) |
| `full_day` | Dispatch without full M8 orchestrator |

Default on desk: **full_m8**.

---

## Founder steps (no Terminal)

| Step | Action |
|------|--------|
| Open desk | Maintainer starts DevBridge — or hub **Actions** when wired |
| Preflight | Maintainer runs `wire:preflight` — not ASF |
| iPhone URL | Maintainer runs `proof:iphone-production` — copy URL to phone |
| Production proof | iPhone: **RUN SYSTEM** **full_m8** → wait → **Record on Mac** (one tap) |
| G3 Tailscale | Maintainer runs `proof:g3` + `record:g3` with real Run ID from phone |

Use **exact** Run ID from phone — never paste placeholders. Incident: `AI Dev Bridge OS/docs/INCIDENT_2026-06-04_AGENT_PLACEHOLDER_RUN_ID.md`.

---

## Maintainer / agent commands (NOT for ASF)

Maintainer or wire agent runs these on Mac — never founder Terminal:

- `npm run wire:preflight`
- `npm run proof:iphone-production`
- `npm run proof:g3`
- `npm run record:g3 -- --host <tailscale-ip> --run-id <from-phone> --pass true`

Working directory: `~/Desktop/AI Dev Bridge OS`

---

## Close P2 / open G3 (proof table)

| Proof | How |
|-------|-----|
| G2 smoke iPhone | Done — `physical_iphone: pass` |
| **full_m8 iPhone** | RUN SYSTEM full_m8 + Record on Mac with `lane=full_m8` |
| **G3 Tailscale** | Same on `100.x` desk URL + maintainer `record:g3` |

Check: `AI Dev Bridge OS/config/locked_plan.json` → `wire_proof`

---

## Golden path

```text
iPhone: Connect → Home → RUN SYSTEM (full_m8)
Mac:    ~/.devbridge/runs/<runId>/stdout.log  (not only "smoke: complete")
Phone:  PASS/FAIL + Record on Mac
```

See also: `SourceA/WIRE_LANE_PROGRESS.md` · hub **Actions** tab
