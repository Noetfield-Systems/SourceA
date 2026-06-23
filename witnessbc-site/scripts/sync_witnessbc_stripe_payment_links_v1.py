#!/usr/bin/env python3
"""Create or pull WitnessBC Stripe Payment Links (witness.bc account) → env → inject → site SSOT.

Env file: ~/.sina/witnessbc-stripe-links-v1.env
  WITNESSBC_STRIPE_PUBLISHABLE_KEY=pk_live_...
  WITNESSBC_STRIPE_SECRET_KEY=sk_live_...   (or rk_live_ restricted · Payment Links Write)
  WITNESSBC_STRIPE_SOURCING_19=https://buy.stripe.com/...

Usage:
  python3 witnessbc-site/scripts/sync_witnessbc_stripe_payment_links_v1.py --pull --json
  python3 witnessbc-site/scripts/sync_witnessbc_stripe_payment_links_v1.py --create --json
  python3 witnessbc-site/scripts/sync_witnessbc_stripe_payment_links_v1.py --create --deploy --json

Receipt: ~/.sina/witnessbc-stripe-sync-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
ENV_FILE = SINA / "witnessbc-stripe-links-v1.env"
RECEIPT = SINA / "witnessbc-stripe-sync-receipt-v1.json"
INJECT = ROOT / "scripts" / "inject_stripe_links_v1.py"
TOOLKITS = ROOT / "data" / "toolkits-v1.json"

ENV_KEYS = {
    "sourcing": "WITNESSBC_STRIPE_SOURCING_19",
    "corrections": "WITNESSBC_STRIPE_CORRECTIONS_9",
    "privacy": "WITNESSBC_STRIPE_PRIVACY_19",
    "publicrec": "WITNESSBC_STRIPE_PUBLICREC_29",
    "storytemp": "WITNESSBC_STRIPE_STORYTEMP_19",
    "actionmap": "WITNESSBC_STRIPE_ACTIONMAP_29",
    "starter": "WITNESSBC_STRIPE_STARTER_39",
    "pro": "WITNESSBC_STRIPE_PRO_99",
    "team": "WITNESSBC_STRIPE_TEAM_149",
    "train_evidence101": "WITNESSBC_STRIPE_TRAIN_EVIDENCE101",
    "train_privacy": "WITNESSBC_STRIPE_TRAIN_PRIVACY",
}

# link_key → (display name, amount_cents CAD)
CATALOG: dict[str, tuple[str, int]] = {
    "sourcing": ("WitnessBC — Sourcing Discipline Pack", 1900),
    "corrections": ("WitnessBC — Corrections & Update Protocol", 900),
    "privacy": ("WitnessBC — Privacy & De-identification Pack", 1900),
    "publicrec": ("WitnessBC — Public Record Checklist", 2900),
    "storytemp": ("WitnessBC — Accountability Story Template", 1900),
    "actionmap": ("WitnessBC — Civic Action Map", 2900),
    "starter": ("WitnessBC — Starter Bundle", 3900),
    "pro": ("WitnessBC — Pro Bundle (All Toolkits)", 9900),
    "team": ("WitnessBC — Team License (5 seats)", 14900),
    "train_evidence101": ("WitnessBC — Evidence Literacy 101", 7900),
    "train_privacy": ("WitnessBC — Privacy-First Publishing", 9900),
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


def save_env(env: dict[str, str]) -> None:
    lines = [
        "# WitnessBC Stripe Payment Links — witness.bc@gmail.com account",
        "# Machine: witnessbc-site/scripts/sync_witnessbc_stripe_payment_links_v1.py",
        "",
    ]
    order = [
        "WITNESSBC_STRIPE_PUBLISHABLE_KEY",
        "WITNESSBC_STRIPE_SECRET_KEY",
        *ENV_KEYS.values(),
    ]
    seen: set[str] = set()
    for key in order:
        if key in env and env[key]:
            lines.append(f"{key}={env[key]}")
            seen.add(key)
    for k, v in sorted(env.items()):
        if k not in seen and v:
            lines.append(f"{k}={v}")
    ENV_FILE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def stripe_request(secret: str, method: str, path: str, data: dict[str, str] | None = None) -> dict:
    body = urllib.parse.urlencode(data or {}).encode() if data else None
    req = urllib.request.Request(
        f"https://api.stripe.com/v1{path}",
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {secret}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode())
        payload["_http_status"] = exc.code
        raise RuntimeError(payload.get("error", {}).get("message") or str(payload)) from exc


def list_payment_links(secret: str) -> list[dict]:
    out: list[dict] = []
    starting_after = ""
    while True:
        q = "?limit=100&active=true"
        if starting_after:
            q += f"&starting_after={starting_after}"
        page = stripe_request(secret, "GET", f"/payment_links{q}")
        out.extend(page.get("data") or [])
        if not page.get("has_more"):
            break
        starting_after = str((page.get("data") or [{}])[-1].get("id") or "")
        if not starting_after:
            break
    return out


def create_payment_link(secret: str, *, link_key: str, name: str, amount_cents: int) -> str:
    product = stripe_request(
        secret,
        "POST",
        "/products",
        {
            "name": name,
            "metadata[witnessbc_key]": link_key,
            "metadata[account]": "witness.bc@gmail.com",
        },
    )
    price = stripe_request(
        secret,
        "POST",
        "/prices",
        {
            "product": product["id"],
            "unit_amount": str(amount_cents),
            "currency": "cad",
            "metadata[witnessbc_key]": link_key,
        },
    )
    link = stripe_request(
        secret,
        "POST",
        "/payment_links",
        {
            "line_items[0][price]": price["id"],
            "line_items[0][quantity]": "1",
            "metadata[witnessbc_key]": link_key,
            "payment_intent_data[statement_descriptor]": "WITNESSBC",
        },
    )
    return str(link.get("url") or "")


def pull_links(secret: str, env: dict[str, str]) -> dict[str, str]:
    matched: dict[str, str] = {}
    for link in list_payment_links(secret):
        url = str(link.get("url") or "")
        if not _is_live(url):
            continue
        meta = link.get("metadata") or {}
        key = str(meta.get("witnessbc_key") or "")
        if key in ENV_KEYS and key not in matched:
            matched[key] = url
    for link_key, env_key in ENV_KEYS.items():
        if link_key in matched:
            env[env_key] = matched[link_key]
    return matched


def create_missing(secret: str, env: dict[str, str]) -> dict[str, str]:
    created: dict[str, str] = {}
    for link_key, env_key in ENV_KEYS.items():
        existing = env.get(env_key, "")
        if _is_live(existing):
            continue
        name, cents = CATALOG[link_key]
        url = create_payment_link(secret, link_key=link_key, name=name, amount_cents=cents)
        if _is_live(url):
            env[env_key] = url
            created[link_key] = url
    return created


def run_inject() -> dict:
    proc = subprocess.run(
        ["python3", str(INJECT), "--json"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "inject failed")
    return json.loads(proc.stdout)


def run_deploy() -> None:
    sync = ROOT.parent / "scripts" / "sync_witnessbc_deploy_repo_v1.sh"
    if sync.is_file():
        subprocess.run(["bash", str(sync)], check=False, cwd=str(ROOT.parent))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--create", action="store_true", help="Create missing Payment Links via API")
    ap.add_argument("--pull", action="store_true", help="Pull existing Payment Links (metadata witnessbc_key)")
    ap.add_argument("--deploy", action="store_true", help="Sync deploy repo after inject")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.create and not args.pull:
        args.pull = True
        args.create = True

    env = load_env()
    secret = env.get("WITNESSBC_STRIPE_SECRET_KEY", "").strip()
    if not secret.startswith(("sk_", "rk_")):
        raise SystemExit(
            f"FAIL: set WITNESSBC_STRIPE_SECRET_KEY in {ENV_FILE} (witness.bc Stripe → Developers → API keys)"
        )

    pulled: dict[str, str] = {}
    created: dict[str, str] = {}
    if args.pull:
        pulled = pull_links(secret, env)
    if args.create:
        created = create_missing(secret, env)

    save_env(env)
    inject = run_inject()
    if args.deploy:
        run_deploy()

    row = {
        "schema": "witnessbc-stripe-sync-receipt-v1",
        "at": _now(),
        "ok": inject.get("live_count", 0) >= 11,
        "pulled": list(pulled.keys()),
        "created": list(created.keys()),
        "live_count": inject.get("live_count"),
        "total_count": inject.get("total_count"),
        "stripe_links_live": inject.get("stripe_links_live"),
        "env_file": str(ENV_FILE),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row['ok']} live={row['live_count']}/{row['total_count']} receipt={RECEIPT}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
