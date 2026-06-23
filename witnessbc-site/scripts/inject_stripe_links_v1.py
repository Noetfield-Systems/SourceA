#!/usr/bin/env python3
"""Inject WitnessBC Stripe payment links from env into site SSOT + assemble tokens."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
ENV_FILE = SINA / "witnessbc-stripe-links-v1.env"
STRIPE_JSON = ROOT / "data" / "stripe-links-v1.json"
RECEIPT = SINA / "witnessbc-stripe-inject-receipt-v1.json"

ENV_KEYS = {
    "WITNESSBC_STRIPE_SOURCING_19": "sourcing",
    "WITNESSBC_STRIPE_CORRECTIONS_9": "corrections",
    "WITNESSBC_STRIPE_PRIVACY_19": "privacy",
    "WITNESSBC_STRIPE_PUBLICREC_29": "publicrec",
    "WITNESSBC_STRIPE_STORYTEMP_19": "storytemp",
    "WITNESSBC_STRIPE_ACTIONMAP_29": "actionmap",
    "WITNESSBC_STRIPE_STARTER_39": "starter",
    "WITNESSBC_STRIPE_PRO_99": "pro",
    "WITNESSBC_STRIPE_TEAM_149": "team",
    "WITNESSBC_STRIPE_TRAIN_EVIDENCE101": "train_evidence101",
    "WITNESSBC_STRIPE_TRAIN_PRIVACY": "train_privacy",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_live(url: str) -> bool:
    return bool(url) and url.startswith("https://buy.stripe.com/") and "REPLACE_" not in url and "PLACEHOLDER" not in url


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV_FILE.is_file():
        return out
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def merge_links() -> dict:
    data = json.loads(STRIPE_JSON.read_text(encoding="utf-8"))
    links = dict(data.get("links") or {})
    env = load_env()
    for env_key, link_key in ENV_KEYS.items():
        val = env.get(env_key, "").strip()
        if _is_live(val):
            links[link_key] = val
    data["links"] = links
    data["saved_at"] = _now()
    live = sum(1 for u in links.values() if _is_live(u))
    data["stripe_links_live"] = live == len(ENV_KEYS)
    data["live_count"] = live
    data["total_count"] = len(links)
    STRIPE_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


STRIPE_LINK_TOKEN_MAP: dict[str, str] = {
    "sourcing": "STRIPE_SOURCING_19_URL",
    "corrections": "STRIPE_CORRECTIONS_9_URL",
    "privacy": "STRIPE_PRIVACY_19_URL",
    "publicrec": "STRIPE_PUBLICREC_29_URL",
    "storytemp": "STRIPE_STORYTEMP_19_URL",
    "actionmap": "STRIPE_ACTIONMAP_29_URL",
    "starter": "STRIPE_STARTER_39_URL",
    "pro": "STRIPE_PRO_99_URL",
    "team": "STRIPE_TEAM_149_URL",
    "train_evidence101": "STRIPE_TRAIN_EVIDENCE101_URL",
    "train_privacy": "STRIPE_TRAIN_PRIVACY_URL",
}


def assemble_tokens(data: dict) -> dict[str, str]:
    links = data.get("links") or {}
    billing = data.get("billing") or {}
    toolkits = "toolkits.html"

    def eff(key: str, fallback: str = toolkits) -> str:
        url = str(links.get(key) or "")
        return url if _is_live(url) else fallback

    out = {token: eff(link_key) for link_key, token in STRIPE_LINK_TOKEN_MAP.items()}
    out["STRIPE_TOOLKITS_HUB_URL"] = toolkits
    out["STRIPE_LINKS_LIVE"] = "true" if data.get("stripe_links_live") else "false"
    out["STRIPE_CURRENCY"] = str(billing.get("currency") or "cad").lower()
    out["STRIPE_DESCRIPTOR"] = str(billing.get("statement_descriptor") or "WITNESSBC")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = merge_links()
    tokens = assemble_tokens(data)
    receipt = {
        "schema": "witnessbc-stripe-inject-receipt-v1",
        "ok": True,
        "at": _now(),
        "stripe_links_live": data.get("stripe_links_live"),
        "live_count": data.get("live_count"),
        "total_count": data.get("total_count"),
        "env_file": str(ENV_FILE),
        "tokens": tokens,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"OK: stripe inject · live={data.get('live_count')}/{data.get('total_count')} "
            f"· stripe_links_live={data.get('stripe_links_live')}"
        )
        if not data.get("stripe_links_live"):
            print(f"HINT: paste live URLs into {ENV_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
