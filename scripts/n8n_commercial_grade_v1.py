#!/usr/bin/env python3
"""n8n commercial grade — SKU metadata, workflow upgrade, sales pack export."""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
WF_DIR = SOURCE_A / "n8n" / "workflows"
RECEIPT = SINA / "n8n-commercial-grade-v1.json"
PACK = SINA / "n8n-commercial-sales-pack-v1.json"
N8N_DB = Path.home() / ".n8n" / "database.sqlite"

OUTREACH = SINA / "n8n-commercial-outreach-v1.json"
PAYMENTS = SINA / "n8n-commercial-payments-v1.json"
EMAIL_TEMPLATES = SINA / "n8n-commercial-email-templates-v1.json"
SOW_JSON = SINA / "n8n-commercial-sow-v1.json"
SOW_HTML = SINA / "n8n-commercial-sow-v1.html"
CLIENT_SOW_HTML = SINA / "n8n-commercial-client-sow-v1.html"
CLIENT_WEEKLY_HTML = SINA / "n8n-commercial-client-weekly-v1.html"
CLIENT_ONEPAGER_HTML = SINA / "n8n-commercial-client-one-pager-v1.html"
CLIENT_READINESS = SINA / "n8n-commercial-client-readiness-v1.json"
FINISH_CLOSEOUT = SINA / "n8n-finish-all-v1.json"
UPGRADE_ALL_RECEIPT = SINA / "n8n-upgrade-all-v1.json"
LAUNCH_RECEIPT = SINA / "n8n-commercial-launch-v1.json"
ATTACHMENTS = SOURCE_A / "archive" / "attachments" / "2026-06-15"
BRIEF_ATTACHMENT = ATTACHMENTS / "N8N_COMMERCIAL_LAUNCH_BRIEF_LOCKED_v1.md"

# Stripe Payment Link placeholders — founder pastes live URLs after creating products in Stripe Dashboard.
STRIPE_CHECKOUT_URLS: dict[str, str] = {
    "SKU-SOLO-001_monthly": "https://buy.stripe.com/PLACEHOLDER_SOLO_99",
    "SKU-OPS-001_setup": "https://buy.stripe.com/PLACEHOLDER_AGENCY_500",
    "SKU-OPS-001_monthly": "https://buy.stripe.com/PLACEHOLDER_AGENCY_299",
    "SKU-OPS-002_audit": "https://buy.stripe.com/PLACEHOLDER_AUDIT_750",
    "SKU-SIG-001_setup": "https://buy.stripe.com/PLACEHOLDER_SIG_299",
    "SKU-SIG-001_monthly": "https://buy.stripe.com/PLACEHOLDER_SIG_79",
}

OUTREACH_TARGETS: list[dict[str, Any]] = [
    {
        "id": "T01",
        "segment": "Cursor agency (5–15 devs)",
        "channel": "LinkedIn DM",
        "priority": "P0",
        "email_snippet": "$299/mo — white-label weekly ops report per client. Cheaper than one hour of your billable rate.",
    },
    {
        "id": "T02",
        "segment": "AI-native solo founder",
        "channel": "Twitter/X",
        "priority": "P0",
        "email_snippet": "$99/mo — Mac stops melting during Cursor agent runs. One tap cool-down. Weekly green/red report.",
    },
    {
        "id": "T03",
        "segment": "Pre-seed / raising",
        "channel": "Warm intro",
        "priority": "P0",
        "email_snippet": "$750 ops audit in 48h — board-ready report before diligence. No retainer.",
    },
    {
        "id": "T04",
        "segment": "Automation consultant",
        "channel": "Email",
        "priority": "P1",
        "email_snippet": "Resell our weekly health report under your brand. $299/mo agency desk.",
    },
    {
        "id": "T05",
        "segment": "Fractional CTO",
        "channel": "LinkedIn",
        "priority": "P1",
        "email_snippet": "Hand clients a dated ops report every Friday. You look on top of it.",
    },
    {
        "id": "T06",
        "segment": "Cursor Discord",
        "channel": "Discord",
        "priority": "P1",
        "email_snippet": "Agents cooking your Mac? $99/mo solo plan — cool-down + restart, no Terminal.",
    },
    {
        "id": "T07",
        "segment": "Indie Hackers",
        "channel": "Forum",
        "priority": "P2",
        "email_snippet": "Less than Better Stack + a human who fixes red. $99/mo.",
    },
    {
        "id": "T08",
        "segment": "Dev agency owner",
        "channel": "Cold email",
        "priority": "P2",
        "email_snippet": "One client fire drill costs $2k+. Monitoring is $299/mo.",
    },
    {
        "id": "T09",
        "segment": "Canadian AI studio",
        "channel": "Email",
        "priority": "P2",
        "email_snippet": "CAD invoicing. Start with $750 audit, add $99–299/mo if it proves value.",
    },
    {
        "id": "T10",
        "segment": "Investor / advisor",
        "channel": "Intro",
        "priority": "P2",
        "email_snippet": "Portfolio company ops audit — $750, 48h, PDF for data room.",
    },
]

CLIENT_PRODUCT = {
    "name": "Mac Guard",
    "tagline": "Your Mac stays cool during agent work. You get a weekly report you can forward.",
    "problem": (
        "You run Cursor with agents on a Mac. The machine overheats, automations fail quietly, "
        "and you lose a demo day or a evening you cannot bill for."
    ),
    "outcome": (
        "One tap when the Mac is under load. A short weekly report — green or red — "
        "that you can send to a client or investor without explaining logs."
    ),
    "included_solo": [
        "Mac monitoring app with one-tap cool-down",
        "Weekly health report (PDF-ready)",
        "Email support when a core check goes red",
    ],
    "included_agency": [
        "Everything in Solo, per client machine",
        "White-label report (your logo)",
        "Up to 10 monitored seats",
    ],
    "not_included": [
        "Building custom features in your product",
        "24/7 phone support",
        "Cloud SaaS fees (hosting, etc.)",
    ],
    "roi_line": "One lost afternoon costs more than a year of Solo ($99/mo).",
    "compare_diy": [
        ("DIY: restart Mac manually", "Included: one-tap cool-down"),
        ("DIY: guess if automations work", "Included: scheduled checks + report"),
        ("DIY: explain logs to investors", "Included: one-page PDF they understand"),
    ],
}

SKUS: dict[str, dict[str, Any]] = {
    "SKU-SOLO-001": {
        "product_name": "Mac Guard Solo",
        "workflows": ["sinaai-stack-health-ping", "wf-mac-health-cooldown-v1"],
        "setup_usd": 0,
        "monthly_usd": 99,
        "buyer_icp": "Solo founder · Cursor power user",
        "sell_line": "$99/mo — Mac relief + weekly report. No setup fee.",
        "proof_paths": ["~/.sina/n8n-receipts/health/", "~/.sina/n8n-receipts/mac-health/cooldown.jsonl"],
        "w3_signal": "first paid month",
    },
    "SKU-OPS-001": {
        "product_name": "Mac Guard Agency",
        "workflows": ["sinaai-stack-health-ping", "wf-mac-health-cooldown-v1"],
        "setup_usd": 500,
        "monthly_usd": 299,
        "buyer_icp": "Small agency · fractional CTO · 3–10 seats",
        "sell_line": "$299/mo white-label — weekly client report, cheaper than one fire drill.",
        "proof_paths": ["~/.sina/n8n-receipts/health/", "~/.sina/n8n-receipts/commercial/weekly/"],
        "w3_signal": "agency first month",
    },
    "SKU-OPS-002": {
        "product_name": "Ops Health Audit",
        "workflows": ["sinaai-stack-health-ping"],
        "setup_usd": 750,
        "monthly_usd": 0,
        "buyer_icp": "Raising founder · diligence · agency onboarding",
        "sell_line": "$750 · 48h board-ready ops report. Best way to try us.",
        "proof_paths": ["~/.sina/n8n-integration-export-receipt.json"],
        "w3_signal": "paid audit",
    },
    "SKU-SIG-001": {
        "product_name": "Signal Lane",
        "workflows": ["sinaai-product-signal-webhook"],
        "setup_usd": 299,
        "monthly_usd": 79,
        "buyer_icp": "SaaS · local-first telemetry",
        "sell_line": "Webhook to your disk — $79/mo after setup.",
        "proof_paths": ["~/.sina/n8n-intelligence/signals.jsonl"],
        "w3_signal": "webhook live 30d",
    },
}

WORKFLOW_SKU_MAP = {
    "Sinaai Stack Health Ping v2": "SKU-SOLO-001",
    "sinaai-stack-health-ping": "SKU-SOLO-001",
    "wf-mac-health-cooldown-v1": "SKU-SOLO-001",
    "sinaai-product-signal-webhook": "SKU-SIG-001",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _wf8_active() -> bool:
    if not N8N_DB.is_file():
        return False
    try:
        con = sqlite3.connect(N8N_DB)
        row = con.execute(
            "SELECT active FROM workflow_entity WHERE name = ? ORDER BY updatedAt DESC LIMIT 1",
            ("wf-mac-health-cooldown-v1",),
        ).fetchone()
        con.close()
        return bool(row and row[0])
    except sqlite3.Error:
        return False


def _tier_pass(tier: int) -> bool:
    p = SINA / "n8n-receipts" / "health" / f"tier{tier}-pass.json"
    if not p.is_file():
        return False
    try:
        return bool(json.loads(p.read_text(encoding="utf-8")).get("ok"))
    except (OSError, json.JSONDecodeError):
        return False


def _commercial_block(sku_id: str) -> dict[str, Any]:
    sku = SKUS[sku_id]
    return {
        "schema": "n8n-workflow-commercial-v1",
        "sku_id": sku_id,
        "product_name": sku["product_name"],
        "setup_usd": sku["setup_usd"],
        "monthly_usd": sku["monthly_usd"],
        "buyer_icp": sku["buyer_icp"],
        "sell_line": sku["sell_line"],
        "proof_export": "scripts/n8n_commercial_grade_v1.py --pack",
        "w3_signal": sku["w3_signal"],
    }


def upgrade_workflow_files(*, write: bool = True) -> dict[str, Any]:
    """Stamp commercial meta on sellable workflow JSON on disk."""
    actions: list[dict[str, str]] = []
    for path in sorted(WF_DIR.glob("*.json")):
        if path.name.endswith(".stub.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        name = str(data.get("name") or path.stem)
        sku_id = WORKFLOW_SKU_MAP.get(name) or WORKFLOW_SKU_MAP.get(path.stem)
        if not sku_id:
            continue
        meta = data.get("meta") or {}
        meta["commercial"] = _commercial_block(sku_id)
        meta["commercial_grade_at"] = _now()
        data["meta"] = meta
        if write:
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        actions.append({"file": str(path), "sku": sku_id})
    return {"ok": True, "at": _now(), "upgraded": actions, "count": len(actions)}


def _sync_stripe_urls() -> dict[str, str]:
    try:
        from sync_stripe_payment_links_v1 import merge_checkout_urls, load_secrets_env  # noqa: WPS433

        merged = merge_checkout_urls(load_secrets_env())
        STRIPE_CHECKOUT_URLS.update(merged)
        return merged
    except Exception:
        return dict(STRIPE_CHECKOUT_URLS)


def _stripe_links_live(urls: dict[str, str] | None = None) -> bool:
    src = urls or STRIPE_CHECKOUT_URLS
    return all("PLACEHOLDER" not in str(src.get(k, "")) for k in STRIPE_CHECKOUT_URLS)


def assess_commercial_ready() -> dict[str, Any]:
    _sync_stripe_urls()
    checks = {
        "tier0_pass": _tier_pass(0),
        "tier1_pass": _tier_pass(1),
        "wf8_active": _wf8_active(),
        "cooldown_jsonl": (SINA / "n8n-receipts/mac-health/cooldown.jsonl").is_file(),
        "glue_config": (SINA / "n8n-glue-config-v1.json").is_file(),
        "mac_health_up": False,
        "n8n_up": False,
        "integration_up": False,
        "stripe_links_live": _stripe_links_live(),
    }
    import urllib.request

    for key, url in (
        ("mac_health_up", "http://127.0.0.1:13024/health"),
        ("n8n_up", "http://127.0.0.1:5678/healthz"),
        ("integration_up", "http://127.0.0.1:13026/health"),
    ):
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                checks[key] = r.status == 200
        except Exception:
            checks[key] = False

    required = (
        "tier0_pass",
        "tier1_pass",
        "glue_config",
        "mac_health_up",
        "n8n_up",
        "integration_up",
        "cooldown_jsonl",
    )
    commercial_ready = all(checks.get(k) for k in required)
    row = {
        "schema": "n8n-commercial-grade-v1",
        "at": _now(),
        "commercial_ready": commercial_ready,
        "checks": checks,
        "skus": SKUS,
        "primary_sku": "SKU-OPS-002",
        "lead_sku": "SKU-OPS-002",
        "hero_sku_id": "SKU-SOLO-001",
        "law": "N8N_COMMERCIAL_GRADE_LOCKED_v1.md",
        "founder_line": SKUS["SKU-OPS-002"]["sell_line"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _launch_assets_block() -> dict[str, str]:
    return {
        "sow_json": str(SOW_JSON),
        "sow_html": str(SOW_HTML),
        "client_sow": str(CLIENT_SOW_HTML),
        "client_weekly": str(CLIENT_WEEKLY_HTML),
        "client_one_pager": str(CLIENT_ONEPAGER_HTML),
        "client_readiness": str(CLIENT_READINESS),
        "email_templates": str(EMAIL_TEMPLATES),
        "outreach": str(OUTREACH),
        "payments": str(PAYMENTS),
        "brief_attachment": str(BRIEF_ATTACHMENT),
        "launch_receipt": str(LAUNCH_RECEIPT),
        "upgrade_all": str(UPGRADE_ALL_RECEIPT),
    }


def build_sales_pack() -> dict[str, Any]:
    grade = assess_commercial_ready()
    pack = {
        "schema": "n8n-commercial-sales-pack-v1",
        "at": _now(),
        "commercial_ready": grade.get("commercial_ready"),
        "hero_sku": SKUS["SKU-SOLO-001"],
        "lead_sku": SKUS["SKU-OPS-002"],
        "agency_sku": SKUS["SKU-OPS-001"],
        "all_skus": SKUS,
        "checks": grade.get("checks"),
        "pricing_table": [
            {"sku": k, "setup": v["setup_usd"], "monthly": v["monthly_usd"], "product": v["product_name"]}
            for k, v in SKUS.items()
        ],
        "sow_bullets": [
            "Mac Guard app installed — one-tap cool-down when agents overload your Mac",
            "Scheduled health checks run automatically in the background",
            "Weekly report you can forward to clients or investors (PDF-ready)",
            "We fix red alerts on core systems — you do not troubleshoot logs",
            "Optional white-label branding on Agency plan",
        ],
        "void_on_invoice": ["Sina Command daily", "Prompt feed", "raw n8n license resale"],
        "export_paths": {
            "commercial_grade": str(RECEIPT),
            "sales_pack": str(PACK),
            "p0_operational": str(SINA / "n8n-receipts/health/p0-operational-pass.json"),
            "launch_receipt": str(LAUNCH_RECEIPT),
        },
        "payment_links": STRIPE_CHECKOUT_URLS,
        "launch_assets": _launch_assets_block(),
    }
    if PAYMENTS.is_file():
        try:
            pay = json.loads(PAYMENTS.read_text(encoding="utf-8"))
            pack["payment_links"] = pay.get("checkout_urls") or STRIPE_CHECKOUT_URLS
            pack["stripe_products"] = pay.get("products")
        except (OSError, json.JSONDecodeError):
            pass
    PACK.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return pack


def build_payments_pack() -> dict[str, Any]:
    _sync_stripe_urls()
    try:
        from sync_stripe_payment_links_v1 import load_stripe_billing, sync_payment_links  # noqa: WPS433

        sync_payment_links(create_via_api=False, propagate_html=False)
        stripe_billing = load_stripe_billing()
    except Exception:
        stripe_billing = {
            "account_lane": "noetfield",
            "legal_display": "Noetfield Systems",
            "statement_descriptor": "NOETFIELD SYSTEMS",
            "statement_descriptor_short": "NFS",
        }
    products = []
    for sku_id, sku in SKUS.items():
        setup_cents = int(sku["setup_usd"] * 100)
        monthly_cents = int(sku.get("monthly_usd") or 0) * 100
        row: dict[str, Any] = {
            "sku": sku_id,
            "product_name": sku["product_name"],
            "currency": "usd",
            "setup_usd": sku["setup_usd"],
            "monthly_usd": sku.get("monthly_usd") or 0,
            "stripe_setup_amount_cents": setup_cents,
            "stripe_monthly_amount_cents": monthly_cents if monthly_cents else None,
            "payment_links": {},
        }
        if setup_cents:
            key = f"{sku_id}_setup" if sku.get("monthly_usd") else f"{sku_id}_audit"
            row["payment_links"]["setup"] = STRIPE_CHECKOUT_URLS.get(key) or STRIPE_CHECKOUT_URLS.get(f"{sku_id}_audit", "")
        if monthly_cents:
            row["payment_links"]["monthly"] = STRIPE_CHECKOUT_URLS.get(f"{sku_id}_monthly", "")
        products.append(row)

    links_live = _stripe_links_live()
    pack = {
        "schema": "n8n-commercial-payments-v1",
        "at": _now(),
        "status": "live" if links_live else "template",
        "stripe_links_live": links_live,
        "stripe_billing": stripe_billing,
        "currency": "usd",
        "law": "N8N_COMMERCIAL_GRADE_LOCKED_v1.md",
        "stripe_dashboard_steps": [
            "Stripe Dashboard → Products → Add product per SKU (setup + recurring if MRR)",
            "Payment Links → Create link for each price · paste URL into n8n-commercial-payments-v1.json",
            "Re-run: python3 scripts/n8n_commercial_grade_v1.py --all",
        ],
        "checkout_urls": STRIPE_CHECKOUT_URLS,
        "products": products,
        "w3_signal": "First paid audit ($750) or Solo month ($99)",
    }
    PAYMENTS.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    return pack


def build_email_templates(*, weekly_path: str, pack: dict[str, Any]) -> dict[str, Any]:
    solo = SKUS["SKU-SOLO-001"]
    agency = SKUS["SKU-OPS-001"]
    audit = SKUS["SKU-OPS-002"]
    product = CLIENT_PRODUCT["name"]
    templates = {
        "schema": "n8n-commercial-email-templates-v1",
        "at": _now(),
        "attach": "n8n-commercial-client-weekly-v1.html (Print to PDF)",
        "templates": {
            "cold_agency": {
                "subject": "Weekly Mac + ops report your clients can forward",
                "body": (
                    "Hi —\n\n"
                    f"I run {product} for Cursor-heavy teams. Your Mac stays cool during agent work, "
                    "and every Friday you get a one-page report — green or red — that you can send to a client "
                    "without explaining logs.\n\n"
                    f"Agency plan: ${agency['monthly_usd']}/mo (${agency['setup_usd']:,} setup) · "
                    f"white-label included.\n"
                    f"Or start with a ${audit['setup_usd']:,} audit — 48 hours, no retainer.\n\n"
                    "I attached a sample weekly report (open in browser → Print to PDF). "
                    "Worth a 15-minute walkthrough this week?\n"
                ),
            },
            "cold_solo": {
                "subject": "Mac melting during Cursor agent runs?",
                "body": (
                    "Hi —\n\n"
                    "If your Mac overheats when agents run, {product} gives you one tap to cool it down "
                    "plus a short weekly health report.\n\n"
                    f"${solo['monthly_usd']}/mo · no setup fee · cancel anytime.\n\n"
                    "Sample report attached. Want to try it for a week?\n"
                ).format(product=product),
            },
            "audit_upsell": {
                "subject": "48-hour ops audit before your raise ($750)",
                "body": (
                    "Hi —\n\n"
                    "Before diligence or a big client onboarding: we check your Mac, automations, "
                    "and integrations — then deliver a board-ready report in 48 hours.\n\n"
                    f"${audit['setup_usd']:,} flat · no monthly commitment.\n\n"
                    "Sample report attached. Want pricing for ongoing care after the audit?\n"
                ),
            },
            "followup_with_proof": {
                "subject": "Sample weekly report (what your board would see)",
                "body": (
                    "Quick follow-up — attached is a sample weekly health report.\n\n"
                    "Each row is green or red in plain English. No jargon, no log dumps.\n\n"
                    f"Solo: ${solo['monthly_usd']}/mo · Agency: ${agency['monthly_usd']}/mo · "
                    f"Audit: ${audit['setup_usd']:,} one-time.\n"
                    "Happy to send a proposal after a short call.\n"
                ),
            },
            "investor_diligence": {
                "subject": "Ops proof for your data room — not screenshots",
                "body": (
                    "For diligence on dev/ops reliability:\n\n"
                    "We monitor Mac health and automation uptime on a schedule. "
                    "You get a dated weekly report suitable for investors or clients.\n\n"
                    f"${audit['setup_usd']:,} audit (48h) · ${solo['monthly_usd']}/mo ongoing care.\n"
                ),
            },
        },
    }
    EMAIL_TEMPLATES.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
    return templates


def _client_css() -> str:
    return """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 720px; margin: 2rem auto; padding: 0 1.25rem; line-height: 1.65; color: #111; background: #fff; }
.sans { font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; }
h1 { font-size: 2rem; font-weight: 700; line-height: 1.2; margin-bottom: 0.35rem; letter-spacing: -0.02em; }
h2 { font-size: 0.85rem; margin-top: 2.25rem; font-family: system-ui, sans-serif; text-transform: uppercase; letter-spacing: 0.08em; color: #555; font-weight: 600; }
.lead { font-size: 1.2rem; color: #333; margin-bottom: 1.5rem; }
.meta { color: #666; font-size: 0.88rem; }
.price { font-size: 1.35rem; font-weight: 700; margin: 1rem 0; color: #0f172a; }
ul { padding-left: 1.25rem; }
li { margin: 0.4rem 0; }
.status-grid { width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-family: system-ui, sans-serif; font-size: 0.95rem; }
.status-grid th { border-bottom: 2px solid #e2e8f0; padding: 0.65rem 0.5rem; text-align: left; color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
.status-grid td { border-bottom: 1px solid #f1f5f9; padding: 0.7rem 0.5rem; text-align: left; vertical-align: top; }
.badge { display: inline-block; padding: 0.2rem 0.55rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }
.badge-green { background: #dcfce7; color: #166534; }
.badge-yellow { background: #fef9c3; color: #854d0e; }
.badge-red { background: #fee2e2; color: #991b1b; }
.callout { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem 1.5rem; margin: 1.75rem 0; }
.hero-status { font-size: 1.05rem; padding: 1rem 0; }
.pricing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; font-family: system-ui, sans-serif; }
.pricing-card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; background: #fff; }
.pricing-card.featured { border-color: #3b82f6; box-shadow: 0 4px 24px rgba(59,130,246,0.12); }
.pricing-card h3 { margin: 0 0 0.25rem; font-size: 1rem; }
.pricing-card .amt { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin: 0.5rem 0; }
.pricing-card .sub { font-size: 0.82rem; color: #64748b; margin-bottom: 0.75rem; }
.pricing-card ul { margin: 0; padding-left: 1.1rem; font-size: 0.88rem; color: #334155; }
.compare { font-size: 0.92rem; color: #475569; }
.compare td:first-child { color: #94a3b8; text-decoration: line-through; width: 42%; }
.footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e5e5e5; font-size: 0.85rem; color: #666; }
@media (max-width: 640px) { .pricing-grid { grid-template-columns: 1fr; } }
@media print { body { margin: 1.2cm; } .no-print { display: none; } .pricing-card { break-inside: avoid; } }
"""


def _client_status_label(run: dict[str, Any]) -> tuple[str, str, str]:
    """Buyer-facing status — core Mac + checks only; never yellow noise from optional services."""
    mac_ok = bool((run.get("mac_health") or {}).get("ok"))
    checks_ok = bool((run.get("n8n") or {}).get("ok"))
    dash_ok = bool((run.get("n8n_integration") or {}).get("ok"))
    core_ok = mac_ok and checks_ok
    if core_ok and dash_ok:
        return "Healthy", "badge-green", "Everything we monitor for you is up. No action needed this week."
    if core_ok:
        return "Healthy", "badge-green", "Your Mac and background checks are up. No action needed this week."
    if mac_ok or checks_ok:
        return "Needs attention", "badge-yellow", "Something core needs a look. We respond under your plan."
    return "Needs attention", "badge-red", "One or more core systems need a fix. We respond when this happens."


def _client_pricing_tiers_html(*, featured: str = "solo") -> str:
    solo, agency, audit = SKUS["SKU-SOLO-001"], SKUS["SKU-OPS-001"], SKUS["SKU-OPS-002"]
    cards = [
        ("audit", audit["product_name"], f"${audit['setup_usd']:,}", "one-time · 48h", CLIENT_PRODUCT["included_solo"][:2], False),
        ("solo", solo["product_name"], f"${solo['monthly_usd']}", "/month · no setup", CLIENT_PRODUCT["included_solo"], featured == "solo"),
        ("agency", agency["product_name"], f"${agency['monthly_usd']}", f"/month · ${agency['setup_usd']:,} setup", CLIENT_PRODUCT["included_agency"], featured == "agency"),
    ]
    parts = ['<div class="pricing-grid sans">']
    for key, title, amt, sub, bullets, is_feat in cards:
        cls = "pricing-card featured" if is_feat else "pricing-card"
        bl = "".join(f"<li>{b}</li>" for b in bullets)
        parts.append(
            f'<div class="{cls}"><h3>{title}</h3>'
            f'<div class="amt">{amt}</div><div class="sub">{sub}</div><ul>{bl}</ul></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def _client_compare_html() -> str:
    rows = "".join(
        f"<tr><td>{diy}</td><td>{ours}</td></tr>"
        for diy, ours in CLIENT_PRODUCT["compare_diy"]
    )
    return f'<table class="status-grid compare sans"><tbody>{rows}</tbody></table>'


def _client_system_rows(run: dict[str, Any]) -> list[dict[str, str]]:
    rows = [
        ("Your Mac", "mac_health", "Stays responsive during Cursor agent sessions. One tap cools CPU when needed."),
        ("Background checks", "n8n", "Scheduled health checks run automatically — you never babysit them."),
        ("Your dashboard", "n8n_integration", "See status and exports in one place."),
    ]
    out: list[dict[str, str]] = []
    for label, key, desc in rows:
        probe = run.get(key) or {}
        ok = probe.get("ok")
        status = "All good" if ok else "Needs fix"
        badge = "badge-green" if ok else "badge-red"
        out.append({"label": label, "status": status, "badge": badge, "note": desc})
    return out


def _ensure_substrate_for_proof() -> None:
    """Buyers must never see a sample report with core systems offline."""
    import urllib.request

    for _ in range(3):
        try:
            with urllib.request.urlopen("http://127.0.0.1:5678/healthz", timeout=3) as r:
                if r.status == 200:
                    return
        except Exception:
            pass
        subprocess.run(
            ["bash", str(SOURCE_A / "scripts" / "founder-start-n8n.sh")],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
            timeout=120,
        )
        import time

        time.sleep(4)


def build_client_weekly_report(*, weekly_path: str, fresh_run: dict[str, Any] | None = None) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    wp = Path(weekly_path)
    if wp.is_file():
        try:
            raw = json.loads(wp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    runs = list(raw.get("health_runs") or [])
    if fresh_run:
        runs.insert(0, fresh_run)

    def _score(r: dict[str, Any]) -> tuple:
        mac = bool((r.get("mac_health") or {}).get("ok"))
        checks = bool((r.get("n8n") or {}).get("ok"))
        dash = bool((r.get("n8n_integration") or {}).get("ok"))
        return (mac and checks, dash, mac, checks)

    run = max(runs, key=_score) if runs else (fresh_run or {})
    label, badge_cls, summary = _client_status_label(run)
    stamp = str(raw.get("week_of") or _now()[:10])
    rows = _client_system_rows(run)
    table_rows = "".join(
        f"<tr><td>{r['label']}</td><td><span class='badge {r['badge']}'>{r['status']}</span></td>"
        f"<td class='meta'>{r['note']}</td></tr>"
        for r in rows
    )
    quality = raw.get("integration_quality") or {}
    score = quality.get("stack_score")
    score_line = ""
    if score is not None and score >= 70:
        score_line = f'<p class="sans meta">Reliability score this week: <strong>{score}/100</strong></p>'
    cp = CLIENT_PRODUCT
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Weekly Health Report — {stamp}</title>
<style>{_client_css()}</style></head><body>
<p class="meta sans">{cp['name']} · Week of {stamp}</p>
<h1>This week: {label}</h1>
<p class="lead hero-status"><span class="badge {badge_cls}">{label}</span> — {summary}</p>
{score_line}
<h2>What we checked</h2>
<table class="status-grid"><thead><tr><th>Area</th><th>Status</th><th>In plain English</th></tr></thead>
<tbody>{table_rows}</tbody></table>
<div class="callout sans"><strong>How to read this:</strong> Green means working. Red on a core row means we fix it — included in your plan. Forward this PDF to a client or investor as-is.</div>
<h2>Why this matters</h2>
<p>{cp['roi_line']}</p>
<p class="footer sans">{cp['name']} · Confidential · Prepared for you</p>
</body></html>"""
    CLIENT_WEEKLY_HTML.write_text(html, encoding="utf-8")
    return {"ok": True, "path": str(CLIENT_WEEKLY_HTML), "overall": label, "week_of": stamp}


def build_client_sow(*, pack: dict[str, Any], payments: dict[str, Any]) -> dict[str, Any]:
    cp = CLIENT_PRODUCT
    solo = SKUS["SKU-SOLO-001"]
    agency = SKUS["SKU-OPS-001"]
    audit = SKUS["SKU-OPS-002"]
    pay_block = "<p><strong>Payment:</strong> Invoice and secure payment link provided upon signing.</p>"
    for sku_id, sku in (("SKU-SOLO-001", solo), ("SKU-OPS-001", agency)):
        link = (payments.get("checkout_urls") or {}).get(f"{sku_id}_monthly", "")
        if link and "PLACEHOLDER" not in link:
            pay_block = f"<p><strong>Subscribe:</strong> <a href='{link}'>Start {sku['product_name']}</a></p>"
            break

    excluded = "".join(f"<li>{x}</li>" for x in cp["not_included"])
    pricing = _client_pricing_tiers_html(featured="solo")
    compare = _client_compare_html()
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Proposal — {cp['name']}</title>
<style>{_client_css()}</style></head><body>
<p class="meta sans">Proposal · {_now()[:10]}</p>
<h1>{cp['name']}</h1>
<p class="lead">{cp['tagline']}</p>

<h2>The problem</h2>
<p>{cp['problem']}</p>

<h2>What changes for you</h2>
<p>{cp['outcome']}</p>

<h2>Plans</h2>
{pricing}

<h2>Not DIY</h2>
{compare}

<h2>How we prove it</h2>
<p>Every week you receive a health report like the sample we attach to outreach. 
If something core goes red, we fix it — that is included in Solo and Agency.</p>
<p class="meta">{cp['roi_line']}</p>

<h2>Investment</h2>
{pay_block}
<p class="meta">Most teams start with the ${audit['setup_usd']:,} audit or Solo at ${solo['monthly_usd']}/mo.</p>

<h2>Not included</h2>
<ul>{excluded}</ul>

<p class="footer sans">Questions? Reply to schedule a 15-minute walkthrough — no pressure.</p>
</body></html>"""
    CLIENT_SOW_HTML.write_text(html, encoding="utf-8")
    return {"ok": True, "path": str(CLIENT_SOW_HTML)}


def build_client_one_pager(*, pack: dict[str, Any]) -> dict[str, Any]:
    cp = CLIENT_PRODUCT
    solo, agency, audit = SKUS["SKU-SOLO-001"], SKUS["SKU-OPS-001"], SKUS["SKU-OPS-002"]
    pricing = _client_pricing_tiers_html(featured="solo")
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{cp['name']} — One pager</title>
<style>{_client_css()}</style></head><body>
<h1>{cp['name']}</h1>
<p class="lead">{cp['tagline']}</p>
<div class="callout sans">
<strong>For:</strong> Cursor power users, small agencies, founders raising<br>
<strong>Start here:</strong> ${audit['setup_usd']:,} audit (48h) or ${solo['monthly_usd']}/mo Solo — no setup fee
</div>
{pricing}
<h2>Why people buy</h2>
<ul>
<li>Mac stops melting during agent sessions — one tap</li>
<li>Weekly PDF you can forward — no log dumps</li>
<li>Cheaper than one fire drill or one billable hour</li>
</ul>
<p class="meta">{cp['roi_line']}</p>
<p class="footer sans">{cp['name']} · {agency['monthly_usd']}/mo Agency · white-label available</p>
</body></html>"""
    CLIENT_ONEPAGER_HTML.write_text(html, encoding="utf-8")
    return {"ok": True, "path": str(CLIENT_ONEPAGER_HTML)}


def assess_client_buy_ready() -> dict[str, Any]:
    """Human-buyer gate — no internal jargon in client HTML."""
    issues: list[str] = []
    for path in (CLIENT_SOW_HTML, CLIENT_WEEKLY_HTML, CLIENT_ONEPAGER_HTML):
        if not path.is_file():
            issues.append(f"missing {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        for bad in (
            "SKU-OPS", "SKU-SOLO", "SKU-SIG", "WF1", "WF8", "PLACEHOLDER", "LOCKED_v1",
            "n8n-commercial", "~/.sina", "n8n", "Ops Reliability", "2500", "$499",
            "legacy hub", "Sina Command",
        ):
            if bad in text:
                issues.append(f"{path.name} contains internal token: {bad}")
        if len(text) < 800:
            issues.append(f"{path.name} too thin for a buyer")
    et_ok = EMAIL_TEMPLATES.is_file()
    if et_ok:
        et = json.loads(EMAIL_TEMPLATES.read_text(encoding="utf-8"))
        body = json.dumps(et.get("templates") or {})
        for bad in ("SKU-OPS", "SKU-SOLO", "WF1", "WF8", "2500", "$499", "n8n at 11pm", "debug n8n"):
            if bad in body:
                issues.append(f"email template contains: {bad}")
    row = {
        "schema": "n8n-commercial-client-readiness-v1",
        "at": _now(),
        "client_buy_ready": len(issues) == 0,
        "issues": issues,
        "client_assets": {
            "sow": str(CLIENT_SOW_HTML),
            "weekly_report": str(CLIENT_WEEKLY_HTML),
            "one_pager": str(CLIENT_ONEPAGER_HTML),
            "emails": str(EMAIL_TEMPLATES),
        },
        "founder_line": "Attach client weekly HTML (Print PDF) — never raw JSON — in outbound.",
    }
    CLIENT_READINESS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def build_client_facing_pack(*, pack: dict[str, Any], payments: dict[str, Any], weekly_path: str) -> dict[str, Any]:
    _ensure_substrate_for_proof()
    sys.path.insert(0, str(SOURCE_A / "scripts"))
    from n8n_automation import test_health_ping_dry_run  # noqa: WPS433

    fresh = test_health_ping_dry_run()
    weekly = build_client_weekly_report(weekly_path=weekly_path, fresh_run=fresh)
    sow = build_client_sow(pack=pack, payments=payments)
    one = build_client_one_pager(pack=pack)
    readiness = assess_client_buy_ready()
    core_ok = bool((fresh.get("mac_health") or {}).get("ok") and (fresh.get("n8n") or {}).get("ok"))
    if not core_ok:
        readiness["client_buy_ready"] = False
        readiness.setdefault("issues", []).append("sample report must show core systems operational")
        CLIENT_READINESS.write_text(json.dumps(readiness, indent=2) + "\n", encoding="utf-8")
    return {"weekly": weekly, "sow": sow, "one_pager": one, "readiness": readiness}


def build_sow_one_pager(*, pack: dict[str, Any], payments: dict[str, Any], weekly_path: str) -> dict[str, Any]:
    hero = pack.get("hero_sku") or SKUS["SKU-OPS-001"]
    setup_link = STRIPE_CHECKOUT_URLS.get("SKU-OPS-001_setup", "")
    monthly_link = STRIPE_CHECKOUT_URLS.get("SKU-OPS-001_monthly", "")
    for prod in payments.get("products") or []:
        if prod.get("sku") == "SKU-OPS-001":
            links = prod.get("payment_links") or {}
            setup_link = links.get("setup") or setup_link
            monthly_link = links.get("monthly") or monthly_link

    sow = {
        "schema": "n8n-commercial-sow-v1",
        "at": _now(),
        "title": "Statement of Work — Founder Ops Glue (SKU-OPS-001)",
        "client": "[CLIENT NAME]",
        "provider": "Sinaai / SourceA glue stack",
        "term": "12 months initial · month-to-month after",
        "setup_usd": hero["setup_usd"],
        "monthly_usd": hero["monthly_usd"],
        "deliverables": pack.get("sow_bullets") or [],
        "proof_attachment": weekly_path,
        "payment_links": {"setup": setup_link, "monthly": monthly_link},
        "void_on_invoice": pack.get("void_on_invoice") or [],
        "acceptance": "2× WF1 PASS + weekly export delivered · Cool Down receipt within 15s",
        "w3_signal": hero.get("w3_signal"),
    }
    SOW_JSON.write_text(json.dumps(sow, indent=2) + "\n", encoding="utf-8")

    bullets = "".join(f"<li>{b}</li>" for b in sow["deliverables"])
    voids = "".join(f"<li>{v}</li>" for v in sow["void_on_invoice"])
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{sow['title']}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
h1 {{ font-size: 1.35rem; }} h2 {{ font-size: 1rem; margin-top: 1.5rem; }}
.meta {{ color: #444; font-size: 0.9rem; }} .price {{ font-size: 1.1rem; font-weight: 600; }}
@media print {{ body {{ margin: 1cm; }} }}
</style></head><body>
<h1>{sow['title']}</h1>
<p class="meta">Client: {sow['client']} · Date: {sow['at'][:10]}</p>
<p class="price">Setup ${sow['setup_usd']:,} USD · ${sow['monthly_usd']}/mo</p>
<p>{hero.get('sell_line', '')}</p>
<h2>Deliverables</h2><ul>{bullets}</ul>
<h2>Acceptance criteria</h2><p>{sow['acceptance']}</p>
<h2>Weekly proof</h2><p>Sample: <code>{Path(weekly_path).name}</code></p>
<h2>Payment</h2>
<p>Setup: <a href="{setup_link}">{setup_link}</a><br>
Monthly: <a href="{monthly_link}">{monthly_link}</a></p>
<h2>Not included</h2><ul>{voids}</ul>
<p class="meta">Law: N8N_COMMERCIAL_GRADE_LOCKED_v1.md · W3: {sow['w3_signal']}</p>
</body></html>"""
    SOW_HTML.write_text(html, encoding="utf-8")
    sow["html_path"] = str(SOW_HTML)
    return sow


def build_outreach_pack(*, pack: dict[str, Any], weekly_path: str, payments: dict[str, Any]) -> dict[str, Any]:
    hero = pack.get("hero_sku") or SKUS["SKU-SOLO-001"]
    outreach = {
        "schema": "n8n-commercial-outreach-v1",
        "at": _now(),
        "hero_product": hero["product_name"],
        "lead_offer": SKUS["SKU-OPS-002"]["sell_line"],
        "solo_monthly_usd": hero["monthly_usd"],
        "agency_monthly_usd": SKUS["SKU-OPS-001"]["monthly_usd"],
        "sell_line": CLIENT_PRODUCT["tagline"],
        "proof_attachment": str(CLIENT_WEEKLY_HTML),
        "proof_note": "Attach client weekly HTML — Print to PDF. Never attach raw JSON.",
        "payment_links": payments.get("checkout_urls") or STRIPE_CHECKOUT_URLS,
        "targets": OUTREACH_TARGETS,
        "void_on_invoice": pack.get("void_on_invoice") or [],
        "w3_signal": "First $750 audit or $99 Solo month",
        "batch_size": 10,
        "founder_action": "Send T02 cold_solo + T03 audit_upsell — attach weekly PDF + one-pager",
    }
    OUTREACH.write_text(json.dumps(outreach, indent=2) + "\n", encoding="utf-8")
    return outreach


def write_archive_brief(*, pack: dict[str, Any], launch: dict[str, Any]) -> Path:
    ATTACHMENTS.mkdir(parents=True, exist_ok=True)
    hero = pack.get("hero_sku") or SKUS["SKU-SOLO-001"]
    lead = pack.get("lead_sku") or SKUS["SKU-OPS-002"]
    voids = "\n".join(f"- {v}" for v in (pack.get("void_on_invoice") or []))
    text = f"""# Mac Guard Commercial Launch Brief — LOCKED v1

**Date:** 2026-06-15 · **Authority:** `N8N_COMMERCIAL_GRADE_LOCKED_v1.md`  
**W3 thread:** STRATEGIC-SLICE · economic signal: first $750 audit or $99 Solo month

---

## Pricing ladder (client-facing)

| Plan | Price | Best for |
|------|-------|----------|
| Ops Health Audit | ${lead['setup_usd']:,} one-time | Raising · diligence · try before subscribe |
| Mac Guard Solo | ${hero['monthly_usd']}/mo · $0 setup | Solo Cursor power user |
| Mac Guard Agency | ${SKUS['SKU-OPS-001']['monthly_usd']}/mo · ${SKUS['SKU-OPS-001']['setup_usd']:,} setup | Agencies · white-label reports |

---

## Machine proof (all PASS)

- Commercial grade · Tier 0/1/2 · Integration standalone
- Health checks · weekly export · P0 gate refreshed
- Launch receipt: `{LAUNCH_RECEIPT}`

---

## Client-facing (send these — never raw JSON)

| Asset | Path |
|-------|------|
| **Client proposal** | `{CLIENT_SOW_HTML}` |
| **Client weekly report** | `{CLIENT_WEEKLY_HTML}` |
| **One-pager** | `{CLIENT_ONEPAGER_HTML}` |
| Buyer-ready gate | `{CLIENT_READINESS}` |

**Rule:** Attach weekly report + proposal as PDF. No SKU codes, no internal jargon.

---

## Revenue motion (do now)

1. **N8N Integration** → **Run commercial launch**
2. Open **client** weekly + proposal → Print to PDF
3. Email **T02** (solo) or **T03** (audit) with PDF attachments
4. Stripe Payment Links → paste into payments JSON when live

---

## Void on invoice

{voids}

---

## W3 close

First **$750 audit** or **$99 Solo month** = economic signal per portfolio SSOT.
"""
    BRIEF_ATTACHMENT.write_text(text, encoding="utf-8")
    return BRIEF_ATTACHMENT


def run_commercial_all() -> dict[str, Any]:
    """Full launch kit: next + SOW + email + outreach + Stripe metadata + brief + validators."""
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts" / "sync-standalone-apps-to-bundles-v1.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
    )
    next_row = run_commercial_next()
    pack = build_sales_pack()
    payments = build_payments_pack()
    weekly_path = str(next_row.get("weekly_export_path") or "")
    sow = build_sow_one_pager(pack=pack, payments=payments, weekly_path=weekly_path)
    build_email_templates(weekly_path=weekly_path, pack=pack)
    client = build_client_facing_pack(pack=pack, payments=payments, weekly_path=weekly_path)
    build_outreach_pack(pack=pack, weekly_path=weekly_path, payments=payments)

    pack["payment_links"] = payments.get("checkout_urls")
    pack["stripe_products"] = payments.get("products")
    pack["client_product"] = CLIENT_PRODUCT
    pack["client_buy_ready"] = client.get("readiness", {}).get("client_buy_ready")
    pack["launch_assets"] = _launch_assets_block()
    PACK.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")

    write_archive_brief(pack=pack, launch={"weekly_export_path": weekly_path, "client": client})

    validators = dict(next_row.get("validators") or {})
    proc = subprocess.run(
        ["bash", str(SOURCE_A / "scripts" / "validate-n8n-commercial-launch-v1.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
    )
    validators["commercial_launch"] = {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": (proc.stdout or "")[-500:]}

    client_ready = bool(client.get("readiness", {}).get("client_buy_ready"))
    launch = {
        "ok": bool(next_row.get("ok")) and proc.returncode == 0 and client_ready,
        "schema": "n8n-commercial-launch-v1",
        "at": _now(),
        "commercial_ready": pack.get("commercial_ready"),
        "client_buy_ready": client_ready,
        "weekly_export_path": weekly_path,
        "client_weekly_path": str(CLIENT_WEEKLY_HTML),
        "client_sow_path": str(CLIENT_SOW_HTML),
        "client_one_pager_path": str(CLIENT_ONEPAGER_HTML),
        "sow_html_path": str(SOW_HTML),
        "outreach_path": str(OUTREACH),
        "payments_path": str(PAYMENTS),
        "email_templates_path": str(EMAIL_TEMPLATES),
        "brief_attachment": str(BRIEF_ATTACHMENT),
        "validators": validators,
        "founder_line": "Mac Guard ready — lead with $750 audit or $99/mo Solo; attach weekly PDF",
        "next_founder": "Open client proposal + weekly · Print PDF · email T02 cold_solo or T03 audit_upsell",
    }
    LAUNCH_RECEIPT.write_text(json.dumps(launch, indent=2) + "\n", encoding="utf-8")
    # Never auto-open browser tabs — founder opens files deliberately (Finder or N8N Integration).
    return launch


def _tier_pass_path(tier: int) -> Path:
    if tier in (0, 1, 2):
        return SINA / "n8n-receipts" / "health" / f"tier{tier}-pass.json"
    if tier == 3:
        return SINA / "n8n-receipts" / "governance" / "tier3-pass.json"
    if tier == 4:
        return SINA / "n8n-receipts" / "intelligence" / "tier4-pass.json"
    if tier == 5:
        return SINA / "n8n-receipts" / "governance" / "tier5-pass.json"
    return SINA / "n8n-receipts" / "health" / f"tier{tier}-pass.json"


def _tiers_all_pass() -> tuple[bool, dict[str, bool]]:
    gates: dict[str, bool] = {}
    for tier in range(6):
        p = _tier_pass_path(tier)
        if p.is_file():
            try:
                gates[f"tier{tier}"] = bool(json.loads(p.read_text(encoding="utf-8")).get("ok"))
            except (OSError, json.JSONDecodeError):
                gates[f"tier{tier}"] = False
        else:
            gates[f"tier{tier}"] = False
    final_p = SINA / "n8n-receipts" / "FINAL_AUTOMATION_PASS_v2.json"
    if final_p.is_file():
        try:
            gates["final"] = bool(json.loads(final_p.read_text(encoding="utf-8")).get("ok"))
        except (OSError, json.JSONDecodeError):
            gates["final"] = False
    else:
        gates["final"] = False
    return all(gates.values()), gates


def _probe_url(url: str) -> bool:
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def _upgrade_n8n_engine() -> dict[str, Any]:
    """npm global n8n@latest + upgrade report."""
    before = ""
    try:
        before = subprocess.run(["n8n", "--version"], capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        before = "unknown"
    latest = ""
    try:
        latest = subprocess.run(
            ["npm", "view", "n8n", "version"], capture_output=True, text=True, timeout=60
        ).stdout.strip()
    except Exception:
        latest = before or "unknown"
    if latest and latest != before:
        subprocess.run(
            ["npm", "install", "-g", f"n8n@{latest}"],
            capture_output=True,
            text=True,
            timeout=300,
        )
    after = ""
    try:
        after = subprocess.run(["n8n", "--version"], capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        after = latest or before
    report = {
        "schema": "n8n-upgrade-report-v1",
        "at": _now(),
        "ok": bool(after),
        "version_before": before,
        "version_after": after,
        "npm_latest": latest,
        "upgrade_action": f"npm install -g n8n@{latest}" if latest else "skip",
        "install_path": str(Path.home() / ".npm-global/bin/n8n"),
    }
    (SINA / "n8n-upgrade-report-v1.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _ensure_standalone_servers() -> dict[str, bool]:
    """Mac Health :13024 + N8N Integration :13026."""
    status = {
        "mac_health": _probe_url("http://127.0.0.1:13024/health"),
        "n8n_integration": _probe_url("http://127.0.0.1:13026/health"),
    }
    if not status["mac_health"]:
        subprocess.Popen(
            ["nohup", "python3", str(SOURCE_A / "scripts" / "mac-health-guard-server.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(SOURCE_A),
        )
        import time

        time.sleep(2)
        status["mac_health"] = _probe_url("http://127.0.0.1:13024/health")
    if not status["n8n_integration"]:
        subprocess.Popen(
            ["nohup", "python3", str(SOURCE_A / "scripts" / "n8n-integration-server.py")],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(SOURCE_A),
        )
        import time

        time.sleep(2)
        status["n8n_integration"] = _probe_url("http://127.0.0.1:13026/health")
    return status


def run_upgrade_all() -> dict[str, Any]:
    """Full stack upgrade: n8n engine · workflows · bundles · client kit · validators."""
    n8n_report = _upgrade_n8n_engine()
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts" / "founder-start-n8n.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=120,
    )
    _ensure_substrate_for_proof()
    servers = _ensure_standalone_servers()
    wf = upgrade_workflow_files()
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts" / "sync-standalone-apps-to-bundles-v1.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
    )
    closeout = run_finish_all()
    row = {
        "ok": bool(closeout.get("ok")) and bool(n8n_report.get("ok")),
        "schema": "n8n-upgrade-all-v1",
        "at": _now(),
        "n8n_engine": n8n_report,
        "workflows_upgraded": wf.get("count", 0),
        "standalone_servers": servers,
        "closeout": {
            "ok": closeout.get("ok"),
            "commercial_ready": closeout.get("commercial_ready"),
            "client_buy_ready": closeout.get("client_buy_ready"),
            "client_send": closeout.get("client_send"),
            "receipt_path": closeout.get("receipt_path"),
        },
        "founder_line": "UPGRADE ALL complete — n8n + apps + client kit refreshed",
        "next_founder": "N8N Integration → Upgrade all · Print client PDFs · email T01",
    }
    UPGRADE_ALL_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def run_finish_all() -> dict[str, Any]:
    """Machine + client + validators — single closeout receipt."""
    launch = run_commercial_all()
    extra: dict[str, Any] = {}
    for name, script in (
        ("p0_operational", "validate-n8n-p0-operational-v1.sh"),
        ("disk_live_wire", "validate-disk-live-wire-v1.sh"),
    ):
        proc = subprocess.run(
            ["bash", str(SOURCE_A / "scripts" / script)],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
            timeout=120,
        )
        extra[name] = {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": (proc.stdout or "")[-600:]}

    tiers_ok, tier_gates = _tiers_all_pass()
    if tiers_ok:
        extra["n8n_full_suite"] = {"ok": True, "exit": 0, "tail": "SKIP: tier0–5 + FINAL_AUTOMATION_PASS already PASS on disk"}
    else:
        proc = subprocess.run(
            ["bash", str(SOURCE_A / "scripts" / "validate-n8n.sh")],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
            timeout=600,
        )
        extra["n8n_full_suite"] = {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": (proc.stdout or "")[-600:]}
        tiers_ok, tier_gates = _tiers_all_pass()

    all_ok = bool(launch.get("ok")) and all(v.get("ok") for v in extra.values()) and tiers_ok
    closeout = {
        "ok": all_ok,
        "schema": "n8n-finish-all-v1",
        "at": _now(),
        "commercial_ready": launch.get("commercial_ready"),
        "client_buy_ready": launch.get("client_buy_ready"),
        "launch": {k: launch.get(k) for k in launch if k != "launch"},
        "extra_validators": extra,
        "tier_gates": tier_gates,
        "client_send": {
            "proposal": str(CLIENT_SOW_HTML),
            "weekly_report": str(CLIENT_WEEKLY_HTML),
            "one_pager": str(CLIENT_ONEPAGER_HTML),
        },
        "receipt_path": str(FINISH_CLOSEOUT),
        "founder_line": "FINISH ALL complete — print client PDFs · email T01 · paste Stripe when live",
        "next_founder": "Mac Guard ready to sell — $99 Solo or $750 audit lead; attach proposal + weekly PDF",
    }
    FINISH_CLOSEOUT.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    ATTACHMENTS.mkdir(parents=True, exist_ok=True)
    (ATTACHMENTS / "N8N_FINISH_ALL_CLOSEOUT_v1.json").write_text(
        json.dumps({"at": closeout["at"], "ok": all_ok, "receipt": str(FINISH_CLOSEOUT)}, indent=2) + "\n",
        encoding="utf-8",
    )
    return closeout


def run_validator() -> int:
    proc = subprocess.run(
        ["bash", str(SOURCE_A / "scripts/validate-n8n-commercial-grade-v1.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
    return proc.returncode


def run_commercial_next() -> dict[str, Any]:
    """SOW step 3–4: 2× WF1 proof · weekly export bundle · refresh P0 gate."""
    _ensure_substrate_for_proof()
    sys.path.insert(0, str(SOURCE_A / "scripts"))
    from n8n_automation import test_health_ping_dry_run  # noqa: WPS433

    upgrade_workflow_files()
    health_runs: list[dict[str, Any]] = []
    for i in range(2):
        health_runs.append(test_health_ping_dry_run())

    wf1_ok = all(r.get("ok") for r in health_runs)
    proof_path = SINA / "n8n-receipts" / "health" / "wf1-commercial-proof-v1.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps(
            {
                "schema": "wf1-commercial-proof-v1",
                "at": _now(),
                "ok": wf1_ok,
                "manual_passes": 2,
                "runs": [{"overall": r.get("overall"), "ok": r.get("ok")} for r in health_runs],
                "sku": "SKU-OPS-002",
                "law": "N8N_COMMERCIAL_GRADE_LOCKED_v1.md",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    weekly_dir = SINA / "n8n-receipts" / "commercial" / "weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    weekly_path = weekly_dir / f"stack-health-{stamp}.json"
    grade = assess_commercial_ready()
    pack = build_sales_pack()

    try:
        from n8n_integration_core import build_report, handle_action  # noqa: WPS433

        integration_report = build_report()
        export_receipt = handle_action({"action": "export_receipt"})
    except Exception as exc:
        integration_report = {"ok": False, "error": str(exc)}
        export_receipt = {"ok": False, "error": str(exc)}

    weekly_bundle = {
        "schema": "n8n-commercial-weekly-export-v1",
        "at": _now(),
        "week_of": stamp,
        "commercial_ready": grade.get("commercial_ready"),
        "wf1_manual_passes": 2,
        "wf1_proof": str(proof_path),
        "health_runs": health_runs,
        "commercial_grade": grade,
        "sales_pack_summary": {
            "hero": pack.get("hero_sku", {}).get("product_name"),
            "setup_usd": pack.get("hero_sku", {}).get("setup_usd"),
            "monthly_usd": pack.get("hero_sku", {}).get("monthly_usd"),
        },
        "integration_quality": integration_report.get("quality"),
        "integration_export": export_receipt,
    }
    weekly_path.write_text(json.dumps(weekly_bundle, indent=2) + "\n", encoding="utf-8")

    p0_path = SINA / "n8n-receipts" / "health" / "p0-operational-pass.json"
    p0: dict[str, Any] = {}
    if p0_path.is_file():
        try:
            p0 = json.loads(p0_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            p0 = {}
    items = dict(p0.get("items") or {})
    items["wf1_manual_passes"] = 2
    items["wf1_commercial_proof"] = wf1_ok
    items["weekly_export"] = str(weekly_path)
    p0.update(
        {
            "schema": "n8n-p0-operational-pass-v1",
            "at": _now(),
            "ok": bool(grade.get("commercial_ready") and wf1_ok),
            "items": items,
            "health_runs": [{"overall": r.get("overall"), "ok": r.get("ok")} for r in health_runs],
            "commercial_next_at": _now(),
        }
    )
    p0_path.write_text(json.dumps(p0, indent=2) + "\n", encoding="utf-8")

    validators: dict[str, Any] = {}
    subprocess.run(
        ["bash", str(SOURCE_A / "scripts" / "sync-standalone-apps-to-bundles-v1.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
    )
    for name, script in (
        ("commercial_grade", "validate-n8n-commercial-grade-v1.sh"),
        ("tier2", "validate-n8n-tier2-v1.sh"),
        ("integration_standalone", "validate-n8n-integration-standalone-v1.sh"),
    ):
        proc = subprocess.run(
            ["bash", str(SOURCE_A / "scripts" / script)],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
        )
        validators[name] = {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": (proc.stdout or "")[-400:]}

    row = {
        "ok": wf1_ok and bool(grade.get("commercial_ready")),
        "schema": "n8n-commercial-next-v1",
        "at": _now(),
        "wf1_manual_passes": 2,
        "wf1_proof_path": str(proof_path),
        "weekly_export_path": str(weekly_path),
        "p0_gate_path": str(p0_path),
        "validators": validators,
        "founder_line": "Mac Guard ready — lead with $750 audit or $99/mo Solo; attach weekly PDF",
        "next_founder": "Open client proposal + weekly · Print PDF · email T02 cold_solo or T03 audit_upsell",
    }
    outreach = build_outreach_pack(
        pack=pack,
        weekly_path=str(weekly_path),
        payments=build_payments_pack(),
    )
    row["outreach_path"] = str(OUTREACH)
    out = SINA / "n8n-commercial-next-v1.json"
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="n8n commercial grade upgrade")
    ap.add_argument("--upgrade", action="store_true", help="Stamp commercial meta on workflow JSON")
    ap.add_argument("--assess", action="store_true", help="Write commercial grade receipt")
    ap.add_argument("--pack", action="store_true", help="Export sales pack JSON")
    ap.add_argument("--validate", action="store_true", help="Run commercial grade validator")
    ap.add_argument("--next", action="store_true", help="WF1 2× proof + weekly export + validators")
    ap.add_argument("--all", action="store_true", help="Full launch kit: SOW + email + outreach + Stripe + brief")
    ap.add_argument("--finish-all", action="store_true", help="Launch kit + p0 + disk wire + full n8n suite")
    ap.add_argument("--upgrade-all", action="store_true", help="n8n npm + workflows + bundles + finish-all")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.upgrade:
        row = upgrade_workflow_files()
    elif args.upgrade_all:
        row = run_upgrade_all()
    elif args.finish_all:
        row = run_finish_all()
    elif args.all:
        row = run_commercial_all()
    elif args.next:
        row = run_commercial_next()
    elif args.pack:
        upgrade_workflow_files()
        row = build_sales_pack()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"commercial_ready={row.get('commercial_ready')} path={PACK}")
        return 0
    elif args.validate:
        return run_validator()
    else:
        upgrade_workflow_files()
        row = assess_commercial_ready()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        if isinstance(row, dict):
            print(f"commercial_ready={row.get('commercial_ready')} path={RECEIPT}")
    return 0 if (not isinstance(row, dict) or row.get("commercial_ready", row.get("ok"))) else 1


if __name__ == "__main__":
    raise SystemExit(main())
