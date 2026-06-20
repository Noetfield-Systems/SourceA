#!/usr/bin/env python3
"""Sync Noetfield Systems Stripe Payment Link URLs from ~/.sina/secrets.env into commercial pack.

Billing SSOT: data/platform-neutral-world-model-v1.json · stripe_billing
Statement descriptor: NOETFIELD SYSTEMS · short: NFS

Optional: STRIPE_SECRET_KEY + --create-via-api creates Payment Links when placeholders remain.

Env keys (paste live buy.stripe.com URLs from Stripe Dashboard):
  STRIPE_PUBLISHABLE_KEY
  STRIPE_STATEMENT_DESCRIPTOR=NOETFIELD SYSTEMS
  STRIPE_STATEMENT_DESCRIPTOR_SHORT=NFS
  STRIPE_PAYMENT_LINK_SOLO_99
  STRIPE_PAYMENT_LINK_AGENCY_500
  STRIPE_PAYMENT_LINK_AGENCY_299
  STRIPE_PAYMENT_LINK_AUDIT_750
  STRIPE_PAYMENT_LINK_SIG_299
  STRIPE_PAYMENT_LINK_SIG_79
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
SECRETS = SINA / "secrets.env"
PAYMENTS = SINA / "n8n-commercial-payments-v1.json"
ROOT = Path(__file__).resolve().parents[1]
WTM_SSOT = ROOT / "data" / "platform-neutral-world-model-v1.json"

ENV_TO_CHECKOUT: dict[str, str] = {
    "STRIPE_PAYMENT_LINK_SOLO_99": "SKU-SOLO-001_monthly",
    "STRIPE_PAYMENT_LINK_AGENCY_500": "SKU-OPS-001_setup",
    "STRIPE_PAYMENT_LINK_AGENCY_299": "SKU-OPS-001_monthly",
    "STRIPE_PAYMENT_LINK_AUDIT_750": "SKU-OPS-002_audit",
    "STRIPE_PAYMENT_LINK_SIG_299": "SKU-SIG-001_setup",
    "STRIPE_PAYMENT_LINK_SIG_79": "SKU-SIG-001_monthly",
}

DEFAULT_PLACEHOLDERS: dict[str, str] = {
    "SKU-SOLO-001_monthly": "https://buy.stripe.com/PLACEHOLDER_SOLO_99",
    "SKU-OPS-001_setup": "https://buy.stripe.com/PLACEHOLDER_AGENCY_500",
    "SKU-OPS-001_monthly": "https://buy.stripe.com/PLACEHOLDER_AGENCY_299",
    "SKU-OPS-002_audit": "https://buy.stripe.com/PLACEHOLDER_AUDIT_750",
    "SKU-SIG-001_setup": "https://buy.stripe.com/PLACEHOLDER_SIG_299",
    "SKU-SIG-001_monthly": "https://buy.stripe.com/PLACEHOLDER_SIG_79",
}

STRIPE_PRODUCTS: list[dict[str, Any]] = [
    {"checkout_key": "SKU-SOLO-001_monthly", "name": "Mac Guard Solo", "amount_cents": 9900, "recurring": True},
    {"checkout_key": "SKU-OPS-001_setup", "name": "Mac Guard Agency Setup", "amount_cents": 50000, "recurring": False},
    {"checkout_key": "SKU-OPS-001_monthly", "name": "Mac Guard Agency Monthly", "amount_cents": 29900, "recurring": True},
    {"checkout_key": "SKU-OPS-002_audit", "name": "Ops Health Audit", "amount_cents": 75000, "recurring": False},
    {"checkout_key": "SKU-SIG-001_setup", "name": "Signal Lane Setup", "amount_cents": 29900, "recurring": False},
    {"checkout_key": "SKU-SIG-001_monthly", "name": "Signal Lane Monthly", "amount_cents": 7900, "recurring": True},
]

HTML_GLOB = [
    "n8n-commercial-client-sow-v1.html",
    "n8n-commercial-client-weekly-v1.html",
    "n8n-commercial-client-one-pager-v1.html",
    "n8n-commercial-sow-v1.html",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_stripe_billing() -> dict[str, str]:
    """Load statement descriptor SSOT — defaults to Noetfield Systems / NFS."""
    defaults = {
        "account_lane": "noetfield",
        "legal_display": "Noetfield Systems",
        "statement_descriptor": "NOETFIELD SYSTEMS",
        "statement_descriptor_short": "NFS",
    }
    if not WTM_SSOT.is_file():
        return dict(defaults)
    try:
        ssot = json.loads(WTM_SSOT.read_text(encoding="utf-8"))
        billing = (ssot.get("platform_neutral_policy") or {}).get("stripe_billing") or {}
        return {
            "account_lane": str(billing.get("account_lane") or defaults["account_lane"]),
            "legal_display": str(billing.get("legal_display") or defaults["legal_display"]),
            "statement_descriptor": str(
                billing.get("statement_descriptor") or defaults["statement_descriptor"]
            ),
            "statement_descriptor_short": str(
                billing.get("statement_descriptor_short") or defaults["statement_descriptor_short"]
            ),
        }
    except (OSError, json.JSONDecodeError):
        return dict(defaults)


def load_secrets_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not SECRETS.is_file():
        return out
    for line in SECRETS.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _is_live_url(url: str) -> bool:
    return bool(url) and "PLACEHOLDER" not in url and url.startswith("https://buy.stripe.com/")


def merge_checkout_urls(secrets: dict[str, str], existing: dict[str, str] | None = None) -> dict[str, str]:
    urls = dict(DEFAULT_PLACEHOLDERS)
    if existing:
        urls.update(existing)
    for env_key, checkout_key in ENV_TO_CHECKOUT.items():
        val = secrets.get(env_key, "").strip()
        if _is_live_url(val):
            urls[checkout_key] = val
    if PAYMENTS.is_file():
        try:
            pay = json.loads(PAYMENTS.read_text(encoding="utf-8"))
            for k, v in (pay.get("checkout_urls") or {}).items():
                if _is_live_url(str(v)):
                    urls[k] = str(v)
        except (OSError, json.JSONDecodeError):
            pass
    return urls


def stripe_request(*, secret: str, method: str, path: str, data: dict[str, str] | None = None) -> dict[str, Any]:
    body = urllib.parse.urlencode(data or {}).encode() if data else None
    req = urllib.request.Request(
        f"https://api.stripe.com/v1{path}",
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {secret}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def create_payment_link(secret: str, *, name: str, amount_cents: int, recurring: bool) -> str:
    product = stripe_request(secret=secret, method="POST", path="/products", data={"name": name})
    price_data: dict[str, str] = {
        "product": product["id"],
        "unit_amount": str(amount_cents),
        "currency": "usd",
    }
    if recurring:
        price_data["recurring[interval]"] = "month"
    price = stripe_request(secret=secret, method="POST", path="/prices", data=price_data)
    link = stripe_request(
        secret=secret,
        method="POST",
        path="/payment_links",
        data={"line_items[0][price]": price["id"], "line_items[0][quantity]": "1"},
    )
    return str(link.get("url") or "")


def create_missing_via_api(urls: dict[str, str], secret: str) -> dict[str, str]:
    out = dict(urls)
    for spec in STRIPE_PRODUCTS:
        key = spec["checkout_key"]
        if _is_live_url(out.get(key, "")):
            continue
        try:
            live = create_payment_link(
                secret,
                name=str(spec["name"]),
                amount_cents=int(spec["amount_cents"]),
                recurring=bool(spec["recurring"]),
            )
            if _is_live_url(live):
                out[key] = live
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError) as exc:
            out[f"_error_{key}"] = str(exc)
    return out


def propagate_html_urls(old_to_new: dict[str, str]) -> list[str]:
    touched: list[str] = []
    for name in HTML_GLOB:
        path = SINA / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for old, new in old_to_new.items():
            if old and new and old != new and old in text:
                text = text.replace(old, new)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            touched.append(str(path))
    return touched


def write_payments_json(urls: dict[str, str]) -> dict[str, Any]:
    live = all(_is_live_url(urls.get(k, "")) for k in DEFAULT_PLACEHOLDERS)
    existing: dict[str, Any] = {}
    if PAYMENTS.is_file():
        try:
            existing = json.loads(PAYMENTS.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}

    products = existing.get("products") or []
    for prod in products:
        sku = prod.get("sku", "")
        links = prod.get("payment_links") or {}
        if sku == "SKU-SOLO-001":
            if urls.get("SKU-SOLO-001_monthly"):
                links["monthly"] = urls["SKU-SOLO-001_monthly"]
        elif sku == "SKU-OPS-001":
            if urls.get("SKU-OPS-001_setup"):
                links["setup"] = urls["SKU-OPS-001_setup"]
            if urls.get("SKU-OPS-001_monthly"):
                links["monthly"] = urls["SKU-OPS-001_monthly"]
        elif sku == "SKU-OPS-002":
            if urls.get("SKU-OPS-002_audit"):
                links["setup"] = urls["SKU-OPS-002_audit"]
        elif sku == "SKU-SIG-001":
            if urls.get("SKU-SIG-001_setup"):
                links["setup"] = urls["SKU-SIG-001_setup"]
            if urls.get("SKU-SIG-001_monthly"):
                links["monthly"] = urls["SKU-SIG-001_monthly"]
        prod["payment_links"] = links

    row = {
        "schema": "n8n-commercial-payments-v1",
        "at": _now(),
        "status": "live" if live else "template",
        "stripe_links_live": live,
        "stripe_billing": load_stripe_billing(),
        "currency": "usd",
        "law": "brain-os/law/N8N_COMMERCIAL_GRADE_LOCKED_v1.md",
        "checkout_urls": {k: urls[k] for k in DEFAULT_PLACEHOLDERS},
        "products": products,
        "w3_signal": "First paid audit ($750) or Solo month ($99)",
        "founder_line": (
            "Stripe links live — close with audit checkout"
            if live
            else "Paste Payment Links into secrets.env STRIPE_PAYMENT_LINK_* or run --create-via-api"
        ),
    }
    PAYMENTS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def sync_payment_links(*, create_via_api: bool = False, propagate_html: bool = True) -> dict[str, Any]:
    secrets = load_secrets_env()
    urls = merge_checkout_urls(secrets)
    old_urls = dict(urls)

    if create_via_api:
        sk = secrets.get("STRIPE_SECRET_KEY", "").strip()
        if sk.startswith("sk_"):
            urls = create_missing_via_api(urls, sk)
        else:
            urls["_stripe_api_skipped"] = "STRIPE_SECRET_KEY missing in secrets.env"

    replacements = {
        old: urls[k]
        for k in DEFAULT_PLACEHOLDERS
        for old in [DEFAULT_PLACEHOLDERS[k], old_urls.get(k, "")]
        if k in urls and _is_live_url(urls[k]) and old and old != urls[k]
    }
    html_touched: list[str] = []
    if propagate_html and replacements:
        html_touched = propagate_html_urls(replacements)

    pay = write_payments_json(urls)
    live_count = sum(1 for k in DEFAULT_PLACEHOLDERS if _is_live_url(urls.get(k, "")))
    return {
        "ok": True,
        "at": _now(),
        "stripe_links_live": pay.get("stripe_links_live"),
        "live_link_count": live_count,
        "total_links": len(DEFAULT_PLACEHOLDERS),
        "checkout_urls": pay.get("checkout_urls"),
        "html_touched": html_touched,
        "payments_path": str(PAYMENTS),
        "founder_line": pay.get("founder_line"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--create-via-api", action="store_true", help="Create missing links via Stripe API")
    ap.add_argument("--no-html", action="store_true", help="Skip HTML propagation")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sync_payment_links(create_via_api=args.create_via_api, propagate_html=not args.no_html)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"stripe_links_live={row.get('stripe_links_live')} live={row.get('live_link_count')}/{row.get('total_links')}")
        print(row.get("founder_line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
