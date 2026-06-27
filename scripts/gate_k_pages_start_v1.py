#!/usr/bin/env python3
"""Gate K — optional Cloudflare Pages durable publish (CF free tier — $0, not paid).

Default Gate K: gate_k_vercel_start_v1.py (Vercel Hobby — no Cloudflare).

ASF: pages → run-recipe · stage · wrangler pages deploy · verify · refresh outbound.

Receipt: ~/.sina/gate-k-pages-receipt-v1.json
Law: SMART-392 — trycloudflare does not satisfy Gate K.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "gate-k-pages-receipt-v1.json"

DEFAULT_PROJECT = "sourcea-com"
CUSTOM_DOMAINS_BY_PROJECT: dict[str, tuple[str, ...]] = {
    "sourcea-com": ("sourcea.app", "www.sourcea.app"),
    "sourcea-landing": ("sourcea.com", "www.sourcea.com"),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _import_publish():
    sys.path.insert(0, str(ROOT / "scripts"))
    import publish_sourcea_landing_v1 as pub  # noqa: WPS433

    return pub


def gate_k_start(
    *,
    project: str = DEFAULT_PROJECT,
    skip_recipe: bool = False,
    custom_domain: bool = False,
) -> dict:
    pub = _import_publish()

    check_proc = __import__("subprocess").run(
        [sys.executable, str(ROOT / "scripts" / "cf_pages_token_check_v1.py"), "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    token_check: dict = {}
    try:
        token_check = json.loads(check_proc.stdout) if check_proc.stdout.strip().startswith("{") else {}
    except json.JSONDecodeError:
        pass

    token_ok = bool(token_check.get("gate_k_ready"))
    steps: list[dict] = [
        {"step": "cf_token_check", "ok": bool(token_check.get("gate_k_ready")), "lane": "sourcea_only", **token_check},
    ]
    if not token_check.get("gate_k_ready"):
        row = {
            "ok": False,
            "schema": "gate-k-pages-v1",
            "at": _now(),
            "gate": "SMART-392",
            "lane": "sourcea_only",
            "gate_k_pass": False,
            "error": "sourcea_cf_token_missing",
            "founder_line": token_check.get("founder_line")
            or "Gate K blocked — SourceA needs its own Cloudflare token (not TrustField)",
            "fix_steps": token_check.get("fix_steps") or [],
            "fix_url": token_check.get("fix_url"),
            "steps": steps,
            "next": "Create Pages token → save cf-pages-token-v1.json → re-run gate_k_pages_start_v1.py",
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    publish_row = pub.publish(backend="pages", project=project, skip_recipe=skip_recipe)
    steps.append({"step": "publish", **{k: publish_row.get(k) for k in ("ok", "base_url", "backend", "boot_verdict")}})

    domain_rows: list[dict] = []
    if custom_domain and publish_row.get("ok"):
        domain_rows_result = pub.add_pages_custom_domains(
            project=project,
            domains=CUSTOM_DOMAINS_BY_PROJECT.get(project, ()),
        )
        domain_rows = domain_rows_result.get("domains") or []
        steps.append({"step": "custom_domains", **domain_rows_result})

    ok = bool(publish_row.get("ok")) and not publish_row.get("ephemeral")
    base_url = str(publish_row.get("base_url") or "")
    gate_k_pass = ok and "trycloudflare.com" not in base_url

    row = {
        "ok": gate_k_pass,
        "schema": "gate-k-pages-v1",
        "at": _now(),
        "gate": "SMART-392",
        "gate_k_pass": gate_k_pass,
        "project": project,
        "base_url": base_url,
        "ephemeral": publish_row.get("ephemeral", True),
        "boot_verdict": publish_row.get("boot_verdict"),
        "public_urls_path": str(pub.PUBLIC_URLS),
        "publish_receipt": str(pub.RECEIPT),
        "steps": steps,
        "founder_line": (
            f"Gate K {'PASS' if gate_k_pass else 'PARTIAL'} · {base_url}/sourcea/ · boot={publish_row.get('boot_verdict') or '?'}"
            + (" · add sourcea.com in CF dashboard if DNS pending" if custom_domain else "")
        ),
        "next": (
            "Custom domain: Cloudflare dashboard → Pages → sourcea-landing → Custom domains → sourcea.com"
            if gate_k_pass and not custom_domain
            else "Republish: python3 scripts/gate_k_pages_start_v1.py --json"
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate K — Cloudflare Pages durable publish")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--skip-recipe", action="store_true")
    ap.add_argument("--custom-domain", action="store_true", help="Add Pages custom domains for this project")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = gate_k_start(
        project=args.project,
        skip_recipe=args.skip_recipe,
        custom_domain=args.custom_domain,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("error") or "FAIL")
        if row.get("next"):
            print(f"  Next: {row['next']}")
    return 0 if row.get("gate_k_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
