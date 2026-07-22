# Asset B — Policy Pack SOW Mapping (LOCKED v1)

**Saved:** 2026-06-23T12:15:00Z  
**Authority:** `SOURCEA_ASSET_B_GOVERNED_AGENTIC_AUTOMATION_LOCKED_v1.md` · `docs/SOURCEA_ASSET_B_POLICY_PACK_LOCKED_v1.md`  
**Demo:** `bash scripts/demo-asset-b-policy-v1.sh --policy outreach`  
**Machine:** `data/asset-b-policy-pack-v1.json`

---

## 30-second talk track (Zoom leave-behind)

> We ship your first governable agent in 48 hours. Outreach cannot send without your approval ref. Ops cannot spend over $50. Nothing posts without human handoff. Every allowed action emits a signed receipt you can export.

---

## Policy → demo moment → invoice line item

| Policy | Buyer-facing name | Demo beat (block → allow) | Receipt fields | SKU | Invoice line |
|--------|-------------------|---------------------------|----------------|-----|----------------|
| `outreach_loop_v1` | Outreach Loop — No Send Without Approval | Send without ref **BLOCKED** → add `approval_ref` **ALLOWED** | `to`, `channel`, `subject`, `approval_ref`, `actor`, `timestamp` | SKU-DFY-001 | Agent Loop Build — outreach ($3–10K) |
| `ops_spend_v1` | Ops Loop — $50 Spend Cap | $75 spend **BLOCKED** → $25 spend **ALLOWED** | `vendor`, `amount_usd`, `purpose`, `actor`, `timestamp` | SKU-DFY-001 | Agent Loop Build — ops ($3–10K) |
| `creative_publish_v1` | Creative/Post Loop — Human Handoff Required | Publish without handoff **BLOCKED** → handoff **ALLOWED** | `platform`, `asset_id`, `caption_hash`, `approver`, `timestamp` | SKU-DFY-001 | Agent Loop Build — client agent ($3–10K) |

**Retainer upsell (all policies):** SKU-RET-001 — $2–5K/mo · weekly receipt export · approval-gated changes.

---

## W1 demo flow (four beats — film this)

| Step | What buyer sees | Command |
|------|-----------------|---------|
| 1 | **BLOCK** — policy denies action | `python3 scripts/commit_intent_v1.py --asset-b-policy outreach --case block --json` |
| 2 | **ALLOW** — same policy, valid input → signed receipt | `python3 scripts/commit_intent_v1.py --asset-b-policy outreach --case allow --json` |
| 3 | **VERIFY** — receipt checksum on disk | Read `~/.sina/demo-enforcement/receipts/latest-demo-receipt.json` |
| 4 | **TAMPER FAIL** — modified receipt fails validator | `bash scripts/validate-demo-enforcement-v1.sh --tamper-test` |

Swap `outreach` for `ops` or `creative` on discovery calls scoped to that loop type.

---

## SOW scope blocks (paste into proposal)

### Outreach loop (SKU-DFY-001)

- One governed outreach loop: research → draft → **approval gate** → send/book
- Policy: `outreach_loop_v1` — no send without `approval_ref`
- Deliverable: live loop + handoff doc + 30-day fix window
- Closeout: signed receipt export + replay demo

### Ops loop (SKU-DFY-001)

- One governed ops loop: monitor → act → **spend cap** → log
- Policy: `ops_spend_v1` — deny spend over $50 USD
- Deliverable: live loop + weekly export template
- Closeout: receipt chain + tamper-checked export

### Creative/post loop (SKU-DFY-001)

- One governed publish loop: brief → generate → **human handoff** → post
- Policy: `creative_publish_v1` — deny publish without `human_handoff`
- Deliverable: live loop + lineage fields on first artifact
- Closeout: receipt + optional Meta Graph wire (week 3+)

---

## Outreach attachment order

1. Attach policy JSON matching buyer pain (outreach / ops / creative)
2. Link this SOW mapping (one scroll)
3. Offer 15-min screen-share — run `demo-asset-b-policy-v1.sh` live
4. Close on SKU-DFY-001; attach SKU-RET-001 in same thread if they want monitoring

**Do not** lead with kernel API or platform. Attach policies; run demo; invoice.

---

## Paths on disk

| Artifact | Path |
|----------|------|
| Outreach policy | `docs/asset-b-policy-pack/outreach_loop_v1.json` |
| Ops policy | `docs/asset-b-policy-pack/ops_spend_v1.json` |
| Creative policy | `docs/asset-b-policy-pack/creative_publish_v1.json` |
| Demo intents | `demo/asset-b/*.json` |
| Gate | `scripts/asset_b_policy_gate_v1.py` |
| Commit wire | `scripts/commit_intent_v1.py --asset-b-policy` |
