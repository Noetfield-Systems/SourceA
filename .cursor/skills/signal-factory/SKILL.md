---
name: signal-factory
description: >-
  SourceA Signal Factory v1 — classify inbound/outbound signals, score trust/risk/
  automation/commercial value, emit fixed decision reports with receipt JSON and
  memory lines. Use when triaging commercial, partner, legal, support, or governance
  signals; scoring automation vs service-pattern paths; enforcing risk≥4 route override;
  tagging sender_declared claims; or preserving Noetfield/TrustField/SourceA/WitnessBC/SG/NOOS
  entity hygiene. Architect/Fable contract — adapters are empty hooks only.
---

# Signal Factory v1 (Architect/Fable contract)

**Version:** 1.0.0 · **Saved:** 2026-07-02  
**SSOT:** `data/signal-factory-v1.json`  
**Core:** `scripts/signal_factory_core_v1.py`  
**Verifier:** `scripts/validate-signal-factory-v1.sh`

> Classify → score → decide → receipt. No Gmail, LinkedIn, website forms, UI, or adapter logic in v1 core.

---

## When to use

- Triage an inbound commercial, partner, legal, support, technical, or governance signal
- Produce a **fixed decision report** before Brain routing or Worker build
- Enforce **risk ≥ 4 → route** to human/legal review
- Gate **AUTOMATION RECIPE** / **COMMERCIAL IDEA** sections by decision only
- Tag sender assertions as **sender_declared** — never launder as facts
- Preserve entity boundaries across Noetfield · TrustField · SourceA · WitnessBC · SG · NOOS

---

## Fixed decision report (required every run)

Every analysis MUST emit these fields in order:

| Field | Type | Notes |
|-------|------|-------|
| `signal_summary` | string | Short neutral summary |
| `classification` | enum | See SSOT `classifications[]` |
| `implied_need` | string | What the signal implies |
| `trust_score` | 0–5 | Sender/corroboration trust |
| `risk_score` | 0–5 | Legal, reputational, operational risk |
| `automation_value` | 0–5 | Fit for automation recipe |
| `commercial_value` | 0–5 | Fit for service/commercial pattern |
| `decision` | enum | See SSOT `decisions[]` |
| `next_action` | string | Bounded next step |
| `receipt` | object | `signal-factory-receipt-v1` JSON |
| `memory_line` | string | One-line disk memory |

---

## Optional sections (strict gating)

| Section | Appears only when |
|---------|-------------------|
| `automation_recipe` | `decision = build_automation` |
| `commercial_idea` | `decision = create_service_pattern` |

**No score threshold. No fuzzy trigger.** Decision enum alone gates optional sections.

---

## Risk override (hard law)

```
IF risk_score ≥ 4
THEN decision = route
AND next_action MUST route to human/legal review
AND optional sections MUST NOT appear
```

---

## Sender-claim rule

All sender assertions MUST be recorded as:

```json
{ "text": "...", "tag": "sender_declared", "source": "sender" }
```

Never restate sender claims as verified facts in `signal_summary`, `implied_need`, `memory_line`, or service patterns.

---

## Entity hygiene

**Separate entities:** Noetfield · TrustField · SourceA · WitnessBC · SG · NOOS

- `receipt.entity_scope` names the owning entity for the signal
- No cross-attribution in receipts, memory lines, or service patterns
- Do not imply one entity offers another entity's capabilities

---

## Adapter hook interface (empty slots only)

Receipt `adapter_hooks` — named null slots, no logic:

```json
{
  "trustfield": null,
  "noetfield": null,
  "witnessbc": null,
  "partnermesh": null,
  "client_mvp": null
}
```

Do not implement adapter logic in v1 core.

---

## SG guardrails (by reference only — do not modify SG)

1. **TrustField** must not claim custody, settlement, MSB, PSP, or banking capability unless legally established.
2. **Entity boundaries** must be preserved.
3. **Partner/equity signals** produce bounded exploratory next action only.
4. **No-employment constraint** applies to generated outreach/service patterns.
5. **Claim ladder** for externally-facing text: **VERIFIED / DECLARED / PLANNED**.

---

## Classification enum

`commercial_inquiry` · `partner_equity` · `legal_regulatory` · `employment_recruitment` · `support_request` · `technical_integration` · `governance_internal` · `spam_noise` · `unclassified`

---

## Decision enum

`route` · `build_automation` · `create_service_pattern` · `monitor` · `archive` · `defer`

---

## Commands

```bash
cd ~/Desktop/SourceA

# Analyze one signal
python3 scripts/signal_factory_core_v1.py \
  --text "TrustField pricing demo request for enterprise pilot" --json

# Verify a decision report JSON
python3 scripts/signal_factory_core_v1.py --verify-json path/to/report.json --json

# Run six synthetic tests + write report
python3 scripts/signal_factory_core_v1.py --run-tests --json

# Structural verifier (skill package + schema + no production wiring)
bash scripts/validate-signal-factory-v1.sh

# Full E2E (verify + install sync + tick motor + negative hygiene gate)
bash scripts/validate-signal-factory-e2e-v1.sh

# 24/7 tick motor (local synthetic queue — Mac-safe)
/usr/bin/python3 scripts/signal_factory_tick_v1.py --local-only --json
bash scripts/validate-signal-factory-tick-v1.sh

# Install skill to ~/.cursor/skills/signal-factory
bash scripts/sync-signal-factory-skill-v1.sh
```

**Test report:** `.cursor/skills/signal-factory/reports/test-report-v1.json`

---

## NON-SCOPE (v1 core)

- No Gmail connection
- No LinkedIn connection
- No website form connection
- No UI
- No adapter implementations
- No NOOS modifications
- No SG modifications
- No TrustField-specific adapter content
- No waiting for real inbox messages

`receipt.production_connected` MUST remain `false`.

---

## 24/7 motor (synthetic queue · controlled autorun)

**Chain:** Cloudflare cron `*/15` → Railway `POST /api/fbe/signal-factory/tick/v1` → disk queue batch (max 5) → decision reports → tick receipt.

| Layer | Path |
|-------|------|
| Tick motor | `scripts/signal_factory_tick_v1.py` |
| Cloud body | `scripts/fbe_cloud_signal_factory_tick_v1.py` |
| Mac/Hub client | `scripts/cloud_signal_factory_client_v1.py` |
| Queue SSOT | `data/signal-factory-queue-v1.json` |
| Synthetic seed | `data/signal-factory-synthetic-seed-v1.json` |
| CF cron worker | `cloud/workers/signal-factory-tick-v1/` |
| Tick receipt | `~/.sina/signal-factory-tick-receipt-v1.json` |
| Per-signal reports | `receipts/signal-factory/<id>.json` |

**Hub glance:** `POST http://127.0.0.1:13020/api/signal-factory/tick/v1`

**L2 law:** Empty queue → `IDLE_NO_WORK` (healthy). `replenish_synthetic` re-seeds from disk fixtures — no Gmail.

**Deploy CF worker (one-time):**
```bash
cd cloud/workers/signal-factory-tick-v1
npx wrangler deploy
bash scripts/signal_factory_cf_secrets_v1.sh
```

**24/7 cron:** fires from existing `loop-specialist-tick-v1` scheduled hook every 15m (piggyback — dedicated cron quota blocked on CF account).

**One-command deploy:**
```bash
bash scripts/deploy_signal_factory_24_7_v1.sh
```

---

## Brain registration readiness

Ready when:

1. `bash scripts/validate-signal-factory-e2e-v1.sh` → PASS
2. `bash scripts/validate-signal-factory-v1.sh` → PASS
3. `python3 scripts/signal_factory_core_v1.py --run-tests --json` → `ok: true`
4. SKILL.md + SSOT + core + six tests present logged
5. `~/.cursor/skills/signal-factory/SKILL.md` installed via sync script
