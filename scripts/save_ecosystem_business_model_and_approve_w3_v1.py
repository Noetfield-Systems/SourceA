#!/usr/bin/env python3
"""SAVE + LOCK ecosystem fast business model v2 · founder approve Ocree + Fundmore."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parents[1]
PAGER = Path.home() / "Desktop" / "1 PAGER"
OS_COMM = ROOT / "os" / "commercial"
DATA_COMM = ROOT / "data" / "commercial"
W3_QUEUE = PAGER / "portfolio-300-locked" / "W3_FIRST_QUEUE.yaml"
DRAFT_OCREE = PAGER / "portfolio-300-locked" / "artifacts" / "w3-first" / "EMAIL_OCREE_TRUSTFIELD_DRAFT.md"
DRAFT_FUNDMORE = PAGER / "portfolio-300-locked" / "artifacts" / "w3-first" / "EMAIL_FUNDMORE_NOETFIELD_DRAFT.md"
EMAILS_JSON = DATA_COMM / "canada-priority-a-emails-v1.json"
APPROVALS_JSON = DATA_COMM / "w3-canada-send-approvals-v1.json"
DOC_NAME = "SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def business_model_body(saved: str) -> str:
    return f"""# SourceA Ecosystem — Fast Business Model & Growth Routing — LOCKED v2

**Version:** 2.0.0 · **Saved:** {saved} · **Status:** LOCKED
**Path:** `~/Desktop/1 PAGER/{DOC_NAME}`
**Authority:** Founder SAVE + lock · deep analysis upgrade · W3 send approvals recorded
**Law:** `PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md` · `SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md` · `CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md`

---

## 0. Executive verdict

**Category:** Agentic trust infrastructure — prove every agent action before the model runs, after it ships.

**Stage:** Post-architecture · pre-revenue. Moat is real (pre-LLM policy + controlled execution + factory compiler). Gap is **one human deposit** and **routing discipline** — not more blueprints.

**June 2026 W3 approvals (founder):**
| Account | Lane | SKU | Status |
|---------|------|-----|--------|
| **Ocree Capital** | TrustField | T-P6 / TF-001 | **APPROVED** — send when champion + relationship basis filled |
| **Fundmore.ai** | Noetfield | NF-RD | **APPROVED** — send when champion + relationship basis filled |

---

## 1. Four-layer stack (reconciled — Gemini · GPT · Claude · disk)

```text
L4  Deployed App / Policy Pack     ← what buyer installs (exchange, KYB wrapper)
L3  FBE Runtime (76-node kernel)    ← stateless Python job engine
L2  Noetfield Control Plane         ← pre-LLM policy · Certainty Report™
L1  SourceA Factory Builder         ← compiles specs · engineer campuses
L0  LLM (Claude/GPT/Gemini)         ← commodity inside nodes — never the hero
```

---

## 2. What we are NOW (honest inventory)

| Layer | Built? | Revenue? |
|-------|--------|----------|
| Governance spine (session gate, receipts, verification) | **Yes** — Valid YES | No external buyer yet |
| FBE W0–W2 + Phase A/B/C | **Yes** — validators PASS | Catalog live · zero paid installs |
| Noetfield NF-RD | Shipped surface | No founding deposit closed |
| TrustField TF-001 / TF-P1-DP | Program + Canada emails LOCKED | Ocree **approved** · send pending champion |
| SourceA agency landing | Films + live forensic proof | Pipeline only |
| WitnessBC / 777 | Sites + plans | Non-commercial lanes |
| Cloud worker 24/7 | Docker + API skeleton | `FBE_CLOUD_WORKER_URL` empty |
| 300 portfolio plans | pf-0001–pf-0300 | W3 queue · 2 accounts approved |

**Commercial film:** `~/Desktop/1 PAGER/SourceA-Commercial-Short.mp4` — Tier B proof · SourceA/agency lane only · 32s · BLOCK · Receipt · policy · routes to 15-min screen-share.

---

## 3. Founder routing panel (weekly SSOT)

| If they say… | Route to | SKU | Film / asset |
|--------------|----------|-----|--------------|
| Prove our Copilot actions | **Noetfield** | NF-RD | Noetfield hero · founding one-pager |
| Tokenization / MSB / EMD evidence | **TrustField** | TF-001 / T-P6 | TrustField beats |
| Build our agent loop | **SourceA** | Agency $3–10K | SourceA-Commercial-Short.mp4 |
| Install exchange/KYB factory | **Catalog** | FBE SKU | Demo + certainty report |
| Publish with accountability | **WitnessBC** | W-P1 | WitnessBC STYLE-B1 |
| Nonprofit navigation | **777** | Gate 0 | No commercial cross-pollution |

**Law:** One brand per email · separate SOWs · CAD ≥ $2K = first economic signal · never blend TrustField + Noetfield in one thread.

---

## 4. Fast business model — three phases

### Phase 1 — Proof-to-deposit (30 days) · target $6K–15K CAD

| Lane | Offer | Price | Motion |
|------|-------|-------|--------|
| **TrustField** | MSB/RWA evidence shadow | $3K CAD · 30d | **Ocree approved** · Canada Priority A |
| **Noetfield** | Copilot Governance Pack | $2K deposit refundable | **Fundmore approved** |
| **SourceA agency** | Scoped loop build | $3–10K fixed | Film → forensic page |

### Phase 2 — Factory catalog (days 31–90) · target $2.5K–7.5K/mo maintenance

| SKU | Buyer | Motion |
|-----|-------|--------|
| `exchange-factory-v1` | TrustField design partners | Hero catalog item |
| `compliance-kyb-wrapper-v1` | MSB-adjacent | Policy pack upsell |
| `sandbox-mock-factory-v1` | Website visitors | Free → upgrade |

**Requires:** Fly worker deploy · one MARKET_READY receipt · optional Supabase job queue.

### Phase 3 — Platform ARR (month 4+) · target $10K+ MRR path

Noetfield founding contracts · TrustField RPAA retainers · factory maintenance · policy marketplace.

**Investor narrative:** Enterprise AI control plane **with** deployable factory apps — both true.

---

## 5. Three horizons

### NOW (June 2026)
Factory compiler works · cloud skeleton works · catalog on website · **no paying external human validated end-to-end** · Canada regulatory moment = TrustField timing · Copilot governance = Noetfield timing.

### COULD BE (12 months)
Noetfield = default pre-LLM layer for Canadian FIs · TrustField = evidence partner for tokenization/MSB · SourceA = factory builder OS for agencies · Revenue mix: 40% pilots · 35% maintenance · 25% agency.

### COULD DO (already in the repository)
Non-custodial factory hosting · policy marketplace (30 packs) · MSP white-label · CREED campus import · WitnessBC correction discipline · 777 mirror receipts · NVIDIA/Microsoft badges.

---

## 6. Factory + pre-LLM policy moat

```text
Trigger (Mac or API)
  → Pre-LLM policy gate (Trust Motor — NOT the LLM)
  → Kernel executes 76-node graph
  → Output + RunReceipt ZIP
  → Human reality checkpoint
  → Federate to Hub
  → Destroy / sleep (Fly)
```

**Why 2026:** FINTRAC · CIRO · OSFI E-23 · CSA tokenization require *explain every automated step*.

**Honest gap:** One living customer proves the whole stack.

---

## 7. Growth flywheel

```text
ATTRACT → PROVE → CLOSE → EXPAND
Canada email → 5-min chain → $2-3K deposit → annual / factory maint
Commercial film → forensic page → $3-10K build → retainer
Catalog demo → certainty report → install → policy pack upsell
```

---

## 8. STOP list (fast business)

| Stop | Why |
|------|-----|
| More architecture before first deposit | Post-architecture stage |
| Blended portfolio emails | Kills trust |
| SourceA hero on MSB cold email | Wrong brand |
| FINTRAC KYB on Noetfield | Wrong SKU |
| 24/7 Railway always-on | Burn cash — Fly auto_stop |
| Picking from 300 plans without W3 queue | Use W3_FIRST_QUEUE.yaml |

---

## 9. 14-day execution board

| Day | Action | Brand |
|-----|--------|-------|
| D1 | Send **Ocree** (approved) | TrustField |
| D2 | Send **Fundmore** (approved) | Noetfield |
| D3 | Deploy Fly FBE worker | SourceA |
| D4 | 3 screen-shares with film | SourceA |
| D5 | One MARKET_READY job | SourceA |
| D6–7 | Follow-up on human replies only | All |

**June success metric:** 1 deposit ≥ $2K CAD + 1 shadow pilot scoped.

---

## 10. One sentence per audience

| Audience | Say |
|----------|-----|
| Copilot buyer | Your agents act alone. Noetfield enforces your rules before they act — and proves it after. |
| RWA/MSB buyer | You need evidence examiners can replay — not another tokenization pitch. |
| Agency buyer | Fifteen minutes of live BLOCK and receipt closes deposits. |
| Investor (later) | Pre-LLM governance runtime with deployable factory apps. |
| Founder | Mac manages business. Cloud runs factories. One deposit proves the stack. |

---

## Cross-refs

| Artifact | Path |
|----------|------|
| Canada send pack | `CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` |
| W3 queue | `portfolio-300-locked/W3_FIRST_QUEUE.yaml` |
| Approvals receipt | `SourceA/data/commercial/w3-canada-send-approvals-v1.json` |
| FBE charter | `docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md` |
| Portfolio routing | `PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md` |
| Commercial film | `~/Desktop/1 PAGER/SourceA-Commercial-Short.mp4` |

*LOCKED v2 — founder SAVE + upgrade + Ocree/Fundmore hub approve.*
"""


def _patch_draft(path: Path) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace("- [ ] Hub approve = Y", "- [x] Hub approve = Y")
    if "**Hub approve:**" not in text:
        text = text.replace(
            "**Law:** Hub approve before send",
            f"**Hub approve:** Y · **Approved at:** {_utc()} · founder tap\n**Law:** Hub approve before send",
        )
    path.write_text(text, encoding="utf-8")


def _patch_w3_queue() -> None:
    saved = _utc()
    text = W3_QUEUE.read_text(encoding="utf-8")
    text = text.replace('updated_at: "2026-06-17"', f'updated_at: "{saved[:10]}"')
    for company in ("Ocree Capital", "Fundmore.ai"):
        pending = f"""  - company: {company}
    lane:"""
        if f"company: {company}" not in text:
            continue
        text = text.replace("    hub_approve_slot: pending", "    hub_approve_slot: approved", 1)
    # Idempotent block replace for Ocree and Fundmore
    replacements = [
        (
            """  - company: Ocree Capital
    lane: TrustField
    sku: TF-001
    plan_refs: [pf-0091, pf-0243]
    hub_approve_slot: pending""",
            f"""  - company: Ocree Capital
    lane: TrustField
    sku: TF-001
    plan_refs: [pf-0091, pf-0243]
    hub_approve_slot: approved
    hub_approved_at: "{saved}"
    hub_approved_by: founder""",
        ),
        (
            """  - company: Fundmore.ai
    lane: Noetfield
    sku: NF-RD
    plan_refs: [pf-0244]
    hub_approve_slot: pending""",
            f"""  - company: Fundmore.ai
    lane: Noetfield
    sku: NF-RD
    plan_refs: [pf-0244]
    hub_approve_slot: approved
    hub_approved_at: "{saved}"
    hub_approved_by: founder""",
        ),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
    W3_QUEUE.write_text(text, encoding="utf-8")


def _patch_emails_json(saved: str) -> None:
    data = json.loads(EMAILS_JSON.read_text(encoding="utf-8"))
    data["saved_at"] = saved
    data["w3_approvals"] = {
        "schema": "w3-canada-send-approvals-v1",
        "approved_at": saved,
        "approved_by": "founder",
        "send_policy": "no_auto_send · founder sends manually · CASL relationship basis required",
        "accounts": [
            {"id": "ocree", "company": "Ocree Capital", "lane": "TrustField", "sku": ["T-P6"], "hub_approve_slot": "approved"},
            {"id": "fundmore", "company": "Fundmore.ai", "lane": "Noetfield", "sku": ["NF-RD"], "hub_approve_slot": "approved"},
        ],
    }
    for acct in data.get("accounts", []):
        if acct.get("id") in ("ocree", "fundmore"):
            acct["hub_approve_slot"] = "approved"
            acct["hub_approved_at"] = saved
            acct["hub_approved_by"] = "founder"
            acct["send_ready"] = True
    EMAILS_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_approvals_receipt(saved: str) -> None:
    receipt = {
        "schema": "w3-canada-send-approvals-v1",
        "saved_at": saved,
        "founder_approved": True,
        "approved_by": "founder",
        "law": "no_send_without_hub_approve · founder_never_sends = manual send after approve",
        "send_policy": "approved_not_sent — fill champion + relationship basis before Gmail/Outlook send",
        "accounts": [
            {
                "id": "ocree",
                "company": "Ocree Capital",
                "lane": "TrustField",
                "sku": "T-P6",
                "plan_refs": ["pf-0091", "pf-0243"],
                "hub_approve_slot": "approved",
                "approved_at": saved,
                "email_source": "CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md#01",
                "verify_before_send": [
                    "OSC EMD registration verified",
                    "relationship basis for CASL filled",
                    "champion name filled — no invented contacts",
                ],
            },
            {
                "id": "fundmore",
                "company": "Fundmore.ai",
                "lane": "Noetfield",
                "sku": "NF-RD",
                "plan_refs": ["pf-0244"],
                "hub_approve_slot": "approved",
                "approved_at": saved,
                "email_source": "CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md#10",
                "verify_before_send": [
                    "relationship basis for CASL filled",
                    "no FINTRAC KYB pack claims",
                    "champion name filled — no invented contacts",
                ],
            },
        ],
        "next_send_order": ["ocree", "fundmore"],
        "cross_ref": {
            "w3_queue": str(W3_QUEUE),
            "emails_json": str(EMAILS_JSON),
            "business_model": f"~/Desktop/1 PAGER/{DOC_NAME}",
        },
    }
    APPROVALS_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def _append_governance_event(saved: str) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        append_event(
            event_type="FOUNDER_SIGNAL",
            object_id="W3-CANADA-SEND-APPROVE-001",
            object_kind="commercial",
            agent_id="founder",
            payload={
                "event": "w3_canada_send_approved",
                "approved_at": saved,
                "accounts": ["ocree", "fundmore"],
                "lanes": {"ocree": "TrustField", "fundmore": "Noetfield"},
                "send_policy": "no_auto_send",
            },
            gate="W3-CANADA",
            proof="founder_chat_approve",
            validator_set=["validate-canada-priority-a-pack-v1.sh"],
        )
    except Exception as exc:
        print(json.dumps({"governance_spine_warning": str(exc)}))


def main() -> int:
    saved = _utc()
    body = business_model_body(saved)
    dests = [
        PAGER / DOC_NAME,
        ROOT / "docs" / DOC_NAME,
        OS_COMM / DOC_NAME,
    ]
    for dest in dests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")

    _patch_w3_queue()
    _patch_draft(DRAFT_OCREE)
    _patch_draft(DRAFT_FUNDMORE)
    _patch_emails_json(saved)
    _write_approvals_receipt(saved)
    _append_governance_event(saved)

    manifest_path = DATA_COMM / "canada-portfolio-lock-manifest-v1.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["locked_at"] = saved
        manifest.setdefault("files", [])
        for p in dests:
            sp = str(p)
            if sp not in manifest["files"]:
                manifest["files"].append(sp)
        manifest["w3_approvals"] = str(APPROVALS_JSON)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "saved_at": saved,
                "business_model": [str(d) for d in dests],
                "approvals": str(APPROVALS_JSON),
                "approved": ["Ocree Capital · TrustField", "Fundmore.ai · Noetfield"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
