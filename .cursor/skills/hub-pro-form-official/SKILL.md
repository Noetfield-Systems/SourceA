---
name: hub-pro-form-official
description: >-
  Hub Pro FORM_OFFICIAL — stable 5-option schema (A-D + option 5 free-text),
  founder-only submit, disk-first path, INCIDENT-037 guards. Use for form UI,
  API, and agent add-question workflows.
---

# Hub Pro — FORM_OFFICIAL

**Law:** `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` · INCIDENT-037

## Stable 5-slot schema (every agent)

**SSOT:** `data/form-official-question-schema-v1.json`  
**Normalizer:** `scripts/form_official_option_schema_v1.py`

| Slot | Key | Type |
|------|-----|------|
| 1–4 | A–D | choice |
| 5 | E | founder_free_text (always visible textarea) |

Agents add 2–4 choices only — machine adds slot 5.

## URLs + API

- UI: http://127.0.0.1:13020/form/
- GET: `/api/live-founder-decision-form-v1` → `option_slots` per row
- POST submit body:

```json
{
  "action": "submit",
  "founder_submit": true,
  "picks": { "Q-EXAMPLE": "A" },
  "founder_comments": { "Q-EXAMPLE": "only when pick is E" },
  "partial_batch": true
}
```

## Submit path (disk-first)

1. **Sync (~30ms):** `canvas_form_apply_picks_v1` → §ANSWERED + `~/.sina/canvas-form-picks-applied-v1.json`
2. **Background:** reconcile, wire, judge, governance

**Never** run full `canvas_form_submit` synchronously on founder Hub POST.

**Critical:** Start background subprocess **after** HTTP response (macOS threaded server drops connection otherwise).

## UI requirements

- Submit bar **top and bottom** (same handler)
- Option 5 textarea always visible
- `founder_submit: true` required
- `partial_batch: true` when not all rows picked

## Guards

- `~/.sina/form-agent-submit-forbidden-v1.flag` ON
- Channel must be `hub_browser` (not CLI)
- Actor: `founder` | `asf` | `human`

## E2e proof

```bash
curl -sf http://127.0.0.1:13020/api/live-founder-decision-form-v1 | python3 -c "import sys,json; q=json.load(sys.stdin)['open_questions'][0]; print(len(q['option_slots']))"
# expect 5

# submit (partial)
curl -sf -X POST http://127.0.0.1:13020/api/live-founder-decision-form-v1 \
  -H 'Content-Type: application/json' \
  -d '{"action":"submit","founder_submit":true,"picks":{"Q-ID":"B"},"partial_batch":true}'
```

Receipt: `~/.sina/hub-form-submit-receipt-v1.json`

## Ledger

`brain-os/law/enforcement/ui-upgrade-ledgers/HUB_FORM_UI_UPGRADE_LEDGER_LOCKED_v1.md`
