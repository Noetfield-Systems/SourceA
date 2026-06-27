# SourceA Asset B — Buyer Policy Pack (LOCKED v1)

**Saved:** 2026-06-23T12:15:00Z  
**Version:** 1.0 — LOCKED  
**Authority:** ASF 2026-06-23 — first-invoice lever for Asset B DFY  
**Commercial law:** `brain-os/law/SOURCEA_ASSET_B_CONTROLLED_AGENTIC_AUTOMATION_LOCKED_v1.md`  
**SOW leave-behind:** `docs/asset-b-policy-pack/SOW_MAPPING_LOCKED_v1.md`  
**Machine registry:** `data/asset-b-policy-pack-v1.json`  
**Offer script:** `scripts/controlled_agentic_automation_offer_v1.py`

---

## One law

> **Three buyer-facing policies plug into `commit_intent_v1.py` + `demo-asset-b-policy-v1.sh`. Attach on outreach; run on Zoom; close SKU-DFY-001.**

Not a new kernel API. Not homepage copy (defer until cloud assess green). Not Meta flow (after first paid loop).

---

## Policies (ready to plug in)

| Key | File | Intent | SKU scope |
|-----|------|--------|-----------|
| `outreach` | `docs/asset-b-policy-pack/outreach_loop_v1.json` | `send_outreach` | SKU-DFY-001 / outreach |
| `ops` | `docs/asset-b-policy-pack/ops_spend_v1.json` | `execute_spend` | SKU-DFY-001 / ops |
| `creative` | `docs/asset-b-policy-pack/creative_publish_v1.json` | `publish_content` | SKU-DFY-001 / client agent |

Each policy defines deny/allow rules, receipt fields, `demo_steps`, and `demo_intents` paths.

---

## Demo commands

```bash
# Full Asset B screen-share (outreach default)
bash scripts/demo-asset-b-policy-v1.sh --policy outreach

# Single beat
python3 scripts/commit_intent_v1.py --asset-b-policy outreach --case block --json
python3 scripts/commit_intent_v1.py --asset-b-policy outreach --case allow --json

# Gate only
python3 scripts/asset_b_policy_gate_v1.py --policy outreach --intent demo/asset-b/outreach-block.json --json
```

---

## This week (disk-aligned)

| Day | Action |
|-----|--------|
| 1–2 | Film `demo-asset-b-policy-v1.sh --policy outreach` (30 sec) |
| 2–3 | Attach policy JSON + SOW mapping to Asset B outreach (`controlled_agentic_automation_offer_v1.py --pack`) |
| 3–7 | 5–10 warm Vancouver touches · close SKU-DFY-001 |

---

## Related (do not mix)

| Lane | Doc |
|------|-----|
| W1 Copilot enforcement demo | `scripts/demo-enforcement-5min-v1.sh` · P-001 |
| Agency / Mac Guard demo | `SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md` |
| Commercial homepage | `sites/SourceA-landing/green-unified/start.html` — **after cloud assess green** |
