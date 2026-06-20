#!/usr/bin/env python3
"""Gate K — Vercel Hobby durable publish (free, no Cloudflare).

ASF: vercel go → run-recipe · stage · vercel deploy --prod · verify · refresh outbound.

Receipt: ~/.sina/gate-k-vercel-receipt-v1.json
Law: SMART-332 · FOUNDER_NO_CREDIT_CARD_INFRA — $0 · no paid Cloudflare.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "gate-k-vercel-receipt-v1.json"

DEFAULT_PROJECT = "sourcea-landing"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _import_publish():
    sys.path.insert(0, str(ROOT / "scripts"))
    import publish_sourcea_landing_v1 as pub  # noqa: WPS433

    return pub


def gate_k_start(*, project: str = DEFAULT_PROJECT, skip_recipe: bool = False) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_vercel_token_v1 import load_sourcea_vercel_config  # noqa: WPS433

    token_check = load_sourcea_vercel_config()
    steps: list[dict] = [
        {"step": "vercel_token_check", "ok": bool(token_check.get("ok")), "lane": "sourcea_only", **token_check},
    ]
    if not token_check.get("ok"):
        row = {
            "ok": False,
            "schema": "gate-k-vercel-v1",
            "at": _now(),
            "gate": "SMART-332",
            "lane": "sourcea_only",
            "gate_k_pass": False,
            "cost": "free_hobby",
            "error": "sourcea_vercel_token_missing",
            "founder_line": token_check.get("founder_line")
            or "Gate K blocked — add SourceA Vercel Hobby token (free, no Cloudflare)",
            "fix_steps": token_check.get("fix_steps") or [],
            "fix_url": token_check.get("fix_url"),
            "steps": steps,
            "next": "Create Vercel token → save sourcea-vercel-token-v1.json → re-run gate_k_vercel_start_v1.py",
            "alt": "Cloudflare Pages is also free ($0) if you prefer CF: gate_k_pages_start_v1.py",
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    pub = _import_publish()
    publish_row = pub.publish(backend="vercel", project=project, skip_recipe=skip_recipe)
    steps.append({"step": "publish", **{k: publish_row.get(k) for k in ("ok", "base_url", "backend", "boot_verdict")}})

    ok = bool(publish_row.get("ok")) and not publish_row.get("ephemeral")
    base_url = str(publish_row.get("base_url") or "")
    gate_k_pass = ok and "trycloudflare.com" not in base_url and ".vercel.app" in base_url

    row = {
        "ok": gate_k_pass,
        "schema": "gate-k-vercel-v1",
        "at": _now(),
        "gate": "SMART-332",
        "gate_k_pass": gate_k_pass,
        "project": project,
        "base_url": base_url,
        "ephemeral": publish_row.get("ephemeral", True),
        "boot_verdict": publish_row.get("boot_verdict"),
        "cost": "free_hobby",
        "public_urls_path": str(pub.PUBLIC_URLS),
        "publish_receipt": str(pub.RECEIPT),
        "steps": steps,
        "founder_line": (
            f"Gate K {'PASS' if gate_k_pass else 'PARTIAL'} · {base_url}/sourcea/ · boot={publish_row.get('boot_verdict') or '?'}"
            + " · Vercel Hobby · $0"
        ),
        "next": (
            f"Proof URL: {base_url}/sourcea/proof.html#w1-demo-film"
            if gate_k_pass
            else "Fix deploy error → re-run gate_k_vercel_start_v1.py --json"
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate K — Vercel Hobby durable publish (free)")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--skip-recipe", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = gate_k_start(project=args.project, skip_recipe=args.skip_recipe)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("error") or "FAIL")
        if row.get("next"):
            print(f"  Next: {row['next']}")
    return 0 if row.get("gate_k_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
