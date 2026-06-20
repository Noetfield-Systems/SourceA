#!/usr/bin/env python3
"""Generate Canada Priority A send-ready email pack + brand routing SSOT.

Outputs:
  data/commercial/canada-priority-a-emails-v1.json
  data/commercial/canada-brand-routing-v1.json
  os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md
  ~/Desktop/1 PAGER/CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md (mirror)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGER = Path.home() / "Desktop" / "1 PAGER"
SAVED = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

FOOTER_TF = """[Full name] · TrustField Technologies
hello@trustfield.ca · [Phone] · [Canadian address for CASL]
Reply **stop** — no further messages.

*Powered by SourceA governed execution — advisory only · no custody · no payment initiation.*"""

FOOTER_NF = """[Full name] · Noetfield
hello@noetfield.com · [Phone] · [Canadian address for CASL]
Reply **stop** — no further messages.

*Built on SourceA — runtime governance at dispatch · no payment rails · no custody.*"""

ACCOUNTS = [
    {
        "id": "ocree",
        "company": "Ocree Capital",
        "site": "ocree.com",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["T-P6"],
        "score": 11,
        "champion_role": "CCO · Platform · CEO",
        "signal": "OSC-registered EMD · $51.9M Winnipeg CRE on Polymesh · CSA Project Tokenization",
        "subject": "CSA Project Tokenization — evidence question for Ocree Capital?",
        "hook": "fractional commercial RE on-chain",
        "body": """Hi [First name] —

[True relationship basis only — e.g. public OSC registration, Polymesh listing, industry event.]

Saw Ocree's live tokenized CRE platform and the CSA Project Tokenization workshop (June 11, Toronto). Before Collaboratory live tests, EMDs are being asked a harder question than "can we tokenize?" — **can we prove every issuance and investor-facing ops step was governed?**

**TrustField** delivers partner-grade attestation for regulated commercial flow: Trust Brief, execution receipt chain, replay, tamper-evidence — shadow first on staging.

Not custody. Not payment initiation. Licensed partners execute settlement.

**Pilot (T-P6):** one EMD workflow · 30–60 days · one metric (e.g. partner audit replay passed) · CAD $3K deposit refunded if we miss.

Five-minute live walkthrough — ALLOW, BLOCK, tamper-FAIL, cold start?

[calendar link]""",
        "attach": "Trust Brief · T-P6 partner attestation outline",
        "send_order": 1,
        "fintrac_note": "OSC EMD — verify exempt market dealer registration",
    },
    {
        "id": "fractionvest",
        "company": "Fractionvest",
        "site": "fractionvest.ca",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["T-P6", "TF-P1-DP"],
        "score": 11,
        "champion_role": "Founder · CCO",
        "signal": "OSC sandbox RE tokenization pilot · Polymesh · dealer registration path",
        "subject": "OSC sandbox RE pilot — partner attestation for Fractionvest?",
        "hook": "sandbox fractional real estate tokenization",
        "body": """Hi [First name] —

[True relationship basis only.]

Fractionvest sits in a rare lane — OSC sandbox RE tokenization on Polymesh while dealer registration path matures. Sandbox reviewers and future investors will ask for **evidence**, not narrative: which actions were permitted, which were blocked, and whether the audit record is intact.

**TrustField** is the commercial trust lane for that proof: Trust Brief + partner receipt pack + live replay in under five minutes.

Shadow pilot · zero production risk · one agreed metric.

**Offer:** T-P6 attestation + TF-P1-DP MSB-adjacent evidence module if dealer ops touch FINTRAC scope · CAD $3K · 30 days · refund if metric missed.

Worth 15 minutes on a screen-share?

[calendar link]""",
        "attach": "Trust Brief · sandbox attestation one-pager",
        "send_order": 2,
        "fintrac_note": "Verify OSC sandbox status before citing",
    },
    {
        "id": "tetra",
        "company": "Tetra Digital Group",
        "site": "tetradg.com",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["TF-001", "T-P6"],
        "score": 10,
        "champion_role": "Chief Compliance · Product · Institutional sales",
        "signal": "CADD live May 2026 · regulated CAD stablecoin · ETF custody",
        "subject": "Bill C-15 stablecoin readiness — shadow evidence for Tetra?",
        "hook": "CADD + custody + FINTRAC MSB path",
        "body": """Hi [First name] —

[True relationship basis only.]

CADD going live puts Tetra at the centre of Canada's regulated CAD rail story — and Bill C-15 (Royal Assent Mar 26) means registry and attestation expectations are converging fast.

Partners and supervisors will ask: **where is the evidence chain for issuance, custody, and MSB-adjacent ops** — not a deck after the fact.

**TrustField** contracts the commercial evidence lane: RPAA/FINTRAC readiness artifacts, Trust Brief, partner receipt packs on governed infrastructure. We verified FINTRAC MSB context before writing — reply stop anytime.

Live demo < 5 min: policy → signed receipt → replay → tamper-FAIL.

**Pilot:** TF-001 readiness + T-P6 attestation module · 30–60 days · one metric · CAD $6K founding terms available.

Open to 15 minutes?

[calendar link]""",
        "attach": "TF-001 RPAA/FINTRAC readiness outline · Trust Brief",
        "send_order": 3,
        "fintrac_note": "FINTRAC MSB verify required — fintrac-canafe.canada.ca",
    },
    {
        "id": "stablecorp",
        "company": "Stablecorp",
        "site": "stablecorp.ca",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["TF-001"],
        "score": 10,
        "champion_role": "CEO · Partnerships · Compliance",
        "signal": "QCAD FI infrastructure · Deloitte alliance Mar 2026 · Bill C-15",
        "subject": "QCAD FI infrastructure — FINTRAC evidence chain for Stablecorp?",
        "hook": "stablecoin infrastructure for Canadian FIs",
        "body": """Hi [First name] —

[True relationship basis only.]

The Deloitte × QCAD FI infrastructure story is exactly where Bill C-15 pressure lands — FI clients will need **defensible evidence** that stablecoin rails and MSB-adjacent workflows are governable before registry rules harden (~2027).

**TrustField** delivers RPAA/FINTRAC readiness evidence and Trust Brief artifacts your FI partners can file — shadow pilot, one metric, no custody through TrustField.

We prove it live in five minutes — not slides.

**Pilot (TF-001):** 30–60 days · one workflow · CAD $6K founding · refunded if agreed metric missed.

15-minute walkthrough?

[calendar link]""",
        "attach": "TF-001 readiness pack · Bill C-15 module outline",
        "send_order": 4,
        "fintrac_note": "FINTRAC MSB verify · Stablecorp/QCAD public disclosures",
    },
    {
        "id": "atlas-parvis",
        "company": "Atlas One Digital Securities / Parvis Invest",
        "site": "atlasone.ca · parvis.com",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["T-P6"],
        "score": 10,
        "champion_role": "CEO · Head of Platform · CCO · Digital strategy",
        "signal": "Parvis LOI May 2026 · $110M+ raised · EMD consolidation",
        "subject": "Atlas One × Parvis — partner attestation pilot?",
        "hook": "digital securities EMD consolidation",
        "body": """Hi [First name] —

[True relationship basis only.]

Treating Atlas One and Parvis as one pursuit given the May 2026 LOI — digital securities EMD consolidation means **one evidence standard** across platforms before CSA tokenization scrutiny intensifies.

Investors and exempt-market reviewers ask: prove ops governance — issuance steps, disclosures, agent-assisted workflows — with replay, not chat logs.

**TrustField** delivers Trust Brief + partner receipt packs (T-P6) on governed infrastructure. Shadow first · no custody · no payment initiation.

**Pilot:** one EMD workflow · 30–60 days · one metric · CAD $3K refunded if miss.

Five-minute live proof chain?

[calendar link]""",
        "attach": "T-P6 Trust Brief · EMD attestation outline",
        "send_order": 5,
        "fintrac_note": "OSC/CSA EMD verify · single worksheet row for both entities",
    },
    {
        "id": "aquanow",
        "company": "Aquanow",
        "site": "aquanow.com",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["T-P6"],
        "score": 10,
        "champion_role": "CEO · Institutional sales · Compliance",
        "signal": "B2B plumbing for majority of Canadian crypto · Visa stablecoin settlement",
        "subject": "FINTRAC evidence chain — 15 min live demo for Aquanow?",
        "hook": "B2B digital asset plumbing for Canadian FIs",
        "body": """Hi [First name] —

[True relationship basis only.]

Aquanow powers a large share of Canadian crypto business — which means your **clients** get examined on FINTRAC evidence, not your marketing page.

The wedge: prove the **compliance chain your FI and MSB clients can show** — pre-execution governance, signed receipts, tamper-FAIL demo — in five minutes cold start.

**TrustField** (T-P6): Trust Brief + partner receipt pack · B2B attestation · shadow pilot · one metric.

Advisory only — licensed partners execute settlement.

Worth 15 minutes?

[calendar link]""",
        "attach": "T-P6 B2B partner attestation outline",
        "send_order": 6,
        "fintrac_note": "FINTRAC MSB verify · B2B — champion may be institutional sales",
    },
    {
        "id": "bitbuy",
        "company": "Bitbuy",
        "site": "bitbuy.ca",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["TF-P1-DP"],
        "score": 9,
        "champion_role": "Head of Risk · Compliance · Engineering",
        "signal": "CIRO Investment Dealer + FINTRAC · WonderFi platform",
        "subject": "CIRO 2026 + FINTRAC evidence chain — shadow pilot for Bitbuy?",
        "hook": "fastest MSB + dealer close",
        "body": """Hi [First name] —

[True relationship basis only.]

CIRO unified rules and FINTRAC 2026 amendments converge on one question for dealers: **can you explain every automated surveillance and ops step if examined?**

Dashboards are not proof. **TrustField** runs the evidence chain live — policy at dispatch → signed receipt → replay → tamper-FAIL — in under five minutes.

**TF-P1-DP:** CAD $3K · 30 days · one MSB/dealer workflow · metric: audit replay passed · refunded if miss.

We verified FINTRAC/CIRO registration context before writing. Reply stop anytime.

[calendar link]""",
        "attach": "TF-P1-DP MSB evidence pilot one-pager",
        "send_order": 7,
        "fintrac_note": "CIRO dealer + FINTRAC MSB — verify before send",
    },
    {
        "id": "ndax",
        "company": "NDAX",
        "site": "ndax.io",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["TF-P1-DP"],
        "score": 9,
        "champion_role": "Compliance · Product",
        "signal": "CIRO Investment Dealer Dec 2024 · Calgary · custody",
        "subject": "FINTRAC evidence chain — 15 min live demo for NDAX?",
        "hook": "fast MSB + CIRO dealer pilot",
        "body": """Hi [First name] —

[True relationship basis only.]

NDAX's CIRO dealer path puts you in the fastest-close segment for evidence pilots — MSB + dealer ops with a single compliance champion.

Examiners ask for **per-action proof**, not session-level policy PDFs.

**TrustField TF-P1-DP:** shadow · 30 days · CAD $3K · one workflow · metric: audit replay passed · refund if missed.

Live demo < 5 min — cold start.

[calendar link]""",
        "attach": "TF-P1-DP pilot outline",
        "send_order": 8,
        "fintrac_note": "CIRO + FINTRAC verify",
    },
    {
        "id": "newton",
        "company": "Newton Crypto",
        "site": "newton.co",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["TF-P1-DP"],
        "score": 9,
        "champion_role": "Product · Risk · Compliance",
        "signal": "CSA Restricted Dealer · Mar 2025 registration · retail spread model",
        "subject": "FINTRAC evidence chain — 15 min live demo for Newton?",
        "hook": "fastest retail dealer close",
        "body": """Hi [First name] —

[True relationship basis only.]

Newton's restricted dealer registration (Mar 2025) means FINTRAC and CSA examination readiness is live ops — not a future project.

When agentic features touch surveillance or client comms, **CIRO 2026** pressure is: prove every step.

**TrustField TF-P1-DP:** CAD $3K · 30 days · one workflow · shadow · audit replay metric · refund if miss.

Five-minute screen-share — ALLOW, BLOCK, tamper-FAIL?

[calendar link]""",
        "attach": "TF-P1-DP MSB/dealer evidence pilot",
        "send_order": 9,
        "fintrac_note": "CSA restricted dealer verify",
    },
    {
        "id": "fundmore",
        "company": "Fundmore.ai",
        "site": "fundmore.ai",
        "priority": "A",
        "lane": "Noetfield",
        "sku": ["NF-RD"],
        "score": 11,
        "champion_role": "CEO · Product · Compliance",
        "signal": "AI mortgage platform · CSA tokenization + lending convergence",
        "subject": "Copilot governance receipt — Fundmore.ai mortgage AI ops?",
        "hook": "best Noetfield fit in Canada list",
        "body": """Hi [First name] —

[True relationship basis only.]

Fundmore sits where CSA Project Tokenization meets **AI mortgage ops** — boards will ask whether Copilot and internal agents have **per-action proof**, not policy at kickoff.

**Noetfield** governs at dispatch (before the model acts): evaluate → enforce → signed Trust Ledger Entry → replay → tamper-FAIL.

Not FINTRAC KYB. Not payment rails. **Internal AI governance only** — separate from any commercial attestation thread.

**NF-RD shadow pilot:** 30–60 days · one workflow / one fleet · one metric · CAD $2K refunded if miss · board PDF in six weeks.

Five-minute live walkthrough?

[calendar link]""",
        "attach": "Noetfield founding customer one-pager · Copilot Governance Pack scope",
        "send_order": 10,
        "fintrac_note": "Noetfield lane only — never lead with TrustField FINTRAC pack",
    },
    {
        "id": "pineapple-tf",
        "company": "Pineapple Financial",
        "site": "gopineapple.com",
        "priority": "A",
        "lane": "TrustField",
        "sku": ["T-P6"],
        "score": 9,
        "champion_role": "CTO · Compliance · Product",
        "signal": "$13.7B CAD mortgage book on-chain migration · PAPL NYSE",
        "subject": "Mortgage RWA migration — execution attestation for Pineapple?",
        "hook": "TrustField lead — mortgage tokenization attestation",
        "body": """Hi [First name] —

[True relationship basis only.]

Pineapple's on-chain mortgage migration is a **commercial attestation** story first: prove each migration and investor-facing action was permitted — PDFs to chain with a receipt examiners can replay.

**TrustField (T-P6):** Trust Brief + partner receipt pack · shadow on staging · one metric.

This email is **rails and attestation only** — not internal broker AI (separate thread if you want Noetfield governance for AI ops).

No custody · no payment initiation · advisory posture.

CAD $3K pilot · 30–60 days · refund if metric missed.

15 minutes live?

[calendar link]""",
        "attach": "T-P6 mortgage RWA attestation outline",
        "send_order": 11,
        "fintrac_note": "Dual account — send Noetfield email 2 weeks later · separate SOW",
        "dual_pair": "pineapple-nf",
    },
    {
        "id": "pineapple-nf",
        "company": "Pineapple Financial",
        "site": "gopineapple.com",
        "priority": "A",
        "lane": "Noetfield",
        "sku": ["NF-RD"],
        "score": 9,
        "champion_role": "CTO · Product (AI broker ops)",
        "signal": "AI broker ops on mortgage platform · separate from tokenization story",
        "subject": "AI broker ops — board-defensible audit trail for Pineapple?",
        "hook": "Noetfield split thread — AI ops only",
        "body": """Hi [First name] —

[True relationship basis only — ideally 2+ weeks after any TrustField attestation thread.]

Separate from mortgage tokenization rails: when **AI broker ops** touch production, incident review asks *was this action governed before execution?*

**Noetfield NF-RD:** policy at dispatch → signed receipt → replay → tamper-FAIL. Shadow pilot · one metric · CAD $2K refund if miss.

Not payment rails. Not FINTRAC KYB pack. **Internal agent governance only.**

Five-minute demo?

[calendar link]""",
        "attach": "Noetfield founding one-pager",
        "send_order": 12,
        "fintrac_note": "Send 2 weeks after pineapple-tf · never blend SOWs",
        "dual_pair": "pineapple-tf",
    },
]

BRAND_ROUTING = {
    "schema": "canada-brand-routing-v1",
    "saved_at": SAVED,
    "law": "PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md",
    "brands": {
        "TrustField": {
            "question": "How does RPAA/FINTRAC/program evidence go live?",
            "skus": ["TF-001", "TF-P1-DP", "T-P6"],
            "accounts": [a["id"] for a in ACCOUNTS if a["lane"] == "TrustField"],
            "website": "trustfield.ca",
            "attach_paths": ["docs/gtm/CANADA_AI_GOVERNANCE_ONE_PAGER.md", "templates/compliance.html"],
            "never": ["FINTRAC KYB pack on Noetfield", "blended SOW with Noetfield"],
        },
        "Noetfield": {
            "question": "Should this AI action run — with proof?",
            "skus": ["NF-RD"],
            "accounts": [a["id"] for a in ACCOUNTS if a["lane"] == "Noetfield"],
            "website": "noetfield.com",
            "attach_paths": ["copilot/", "bank-pilot/"],
            "never": ["MSB cold email lead", "RWA attestation hero", "FINTRAC KYB pack"],
        },
        "SourceA": {
            "question": "Engine underneath — factory builder",
            "role": "proof demo spine only in outbound",
            "website": "sourcea.com",
            "never": ["hero in cold email subject", "replace TrustField/Noetfield brand"],
        },
    },
    "overlap_rules": [
        {"accounts": ["pineapple-tf", "pineapple-nf"], "rule": "two emails · two SOWs · 2 week gap"},
        {"accounts": ["atlas-parvis"], "rule": "one worksheet row · one pursuit"},
    ],
}


def render_markdown() -> str:
    lines = [
        "# Canada Priority A — Send-Ready Emails (12 sends · 11 accounts)",
        "",
        f"**Version:** 1.0.0 · **Saved:** {SAVED}",
        "**Path:** `~/Desktop/1 PAGER/CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md`",
        "**SSOT JSON:** `SourceA/data/commercial/canada-priority-a-emails-v1.json`",
        "**Law:** `PORTFOLIO_ALL_PATHS_BY_BRAND_LOCKED_v1.md` · `CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_v2.md`",
        "**Tone:** Winner one-pager · proof not prose · shadow · refund if metric missed · CASL",
        "",
        "---",
        "",
        "## Routing matrix (no blur)",
        "",
        "| Company | Lane | SKU | Send # |",
        "|---------|------|-----|--------|",
    ]
    for a in ACCOUNTS:
        lines.append(
            f"| {a['company']} | **{a['lane']}** | {', '.join(a['sku'])} | {a['send_order']} |"
        )
    lines.extend(
        [
            "",
            "**Dual:** Pineapple = Email 11 (TrustField) then Email 12 (Noetfield) · 2 weeks apart.",
            "",
            "---",
            "",
        ]
    )
    for a in ACCOUNTS:
        footer = FOOTER_NF if a["lane"] == "Noetfield" else FOOTER_TF
        lines.extend(
            [
                f"## {a['send_order']:02d}. {a['company']} · {a['lane']} · {', '.join(a['sku'])}",
                "",
                f"**Champion:** {a['champion_role']}  ",
                f"**Signal (Jun 2026):** {a['signal']}  ",
                f"**Verify:** {a['fintrac_note']}  ",
                f"**Attach:** {a['attach']}",
                "",
                f"**Subject:** {a['subject']}",
                "",
                a["body"].strip(),
                "",
                footer,
                "",
                "---",
                "",
            ]
        )
    lines.extend(
        [
            "## Send sequence (recommended)",
            "",
            "1. Ocree → 2. Fractionvest → 3. Tetra → 4. Stablecorp → 5. Atlas/Parvis",
            "6. Aquanow → 7–9. Bitbuy · NDAX · Newton (MSB fast-close cluster)",
            "10. Fundmore (Noetfield) → 11. Pineapple TF → 12. Pineapple NF (+2 weeks)",
            "",
            "## Before every send",
            "",
            "- [ ] FINTRAC/CSA/CIRO verify where cited",
            "- [ ] Champion name researched — **never invent**",
            "- [ ] Relationship basis filled — true only",
            "- [ ] CASL address + stop line",
            "- [ ] Correct brand attachment (Noetfield ≠ TrustField invoice)",
            "",
            "*12 sends · 0 fabricated contacts · founder approves each send.*",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    accounts_out = []
    for a in ACCOUNTS:
        row = dict(a)
        footer = FOOTER_NF if a["lane"] == "Noetfield" else FOOTER_TF
        row["body_full"] = a["body"].strip() + "\n\n" + footer
        accounts_out.append(row)
    pack = {
        "schema": "canada-priority-a-emails-v1",
        "saved_at": SAVED,
        "account_count": 11,
        "email_count": len(ACCOUNTS),
        "accounts": accounts_out,
    }
    out_json = ROOT / "data" / "commercial" / "canada-priority-a-emails-v1.json"
    route_json = ROOT / "data" / "commercial" / "canada-brand-routing-v1.json"
    out_md_os = ROOT / "os" / "commercial" / "CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md"
    out_md_pager = PAGER / "CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md"

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    route_json.write_text(json.dumps(BRAND_ROUTING, indent=2) + "\n", encoding="utf-8")

    md = render_markdown()
    out_md_os.write_text(md, encoding="utf-8")
    PAGER.mkdir(parents=True, exist_ok=True)
    out_md_pager.write_text(md, encoding="utf-8")

    print(json.dumps({"ok": True, "saved_at": SAVED, "emails": len(ACCOUNTS), "paths": [str(p) for p in [out_json, route_json, out_md_os, out_md_pager]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
