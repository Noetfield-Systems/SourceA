#!/usr/bin/env python3
"""WitnessBC Proof Lab publish — sandbox-class interactive + STYLE-B1 film tier split.

Learns from: P0-01 sandbox · P0-13 noetfield bay · trust_center_publish pattern.

Unblocks: Proof Lab site deploy + interactive demo publish
Honest block: STYLE-B1 hero ship gate until Screen Studio master ingest

Law: data/witnessbc-proof-lab-v1.json
Receipt: ~/.sina/witnessbc-proof-lab-publish-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "witnessbc-proof-lab-v1.json"
RECEIPT = SINA / "witnessbc-proof-lab-publish-receipt-v1.json"
SITE_ROOT = ROOT / "witnessbc-site"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _run(cmd: list[str], *, timeout: int = 600) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": (proc.stdout or proc.stderr)[-500:]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def run_publish(*, skip_recipe: bool = False, write: bool = True) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    steps: list[dict] = []
    ssot = _read(SSOT)

    bay_mod = __import__("fbe.witnessbc_proof_lab_bay_v1", fromlist=["run_bay"])
    bay = bay_mod.run_bay(work_order_id="witnessbc-proof-lab-publish")
    steps.append({"step": "proof_lab_bay", "ok": bay.get("ok"), "checks": len(bay.get("checks") or [])})

    recipe = {"skipped": True}
    if not skip_recipe:
        recipe = _run(["bash", str(SITE_ROOT / "scripts" / "run-recipe.sh")], timeout=900)
        steps.append({"step": "site_run_recipe", **recipe})
    else:
        steps.append({"step": "site_run_recipe", "skipped": True})

    ship_proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "commercial_film_ship_gate_v1.py"),
            "--lane",
            "witnessbc",
            "--skip-ingest",
            "--json",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    ship_json: dict = {}
    if ship_proc.stdout.strip():
        try:
            ship_json = json.loads(ship_proc.stdout)
        except json.JSONDecodeError:
            ship_json = {}
    publish_allowed_hero = bool(ship_json.get("publish_allowed"))
    steps.append(
        {
            "step": "style_b1_ship_gate",
            "ok": publish_allowed_hero,
            "publish_allowed": publish_allowed_hero,
            "critic_only": True,
            "exit": ship_proc.returncode,
        }
    )

    interactive_ok = bool(bay.get("ok")) and (recipe.get("ok") or recipe.get("skipped"))
    proof_deploy = SITE_ROOT / "dist" / "deploy" / "proof.html"
    scenarios = SITE_ROOT / "data" / "proof-scenarios-v1.json"

    row = {
        "schema": "witnessbc-proof-lab-publish-receipt-v1",
        "saved_at": _now(),
        "ok": interactive_ok,
        "lane": "witnessbc",
        "upgrade_ids": ["P0-03", "P0-08"],
        "publish": {
            "interactive_proof_lab": interactive_ok,
            "style_b1_hero_film": publish_allowed_hero,
        },
        "proof_lab_line": (
            f"Proof Lab · interactive={'YES' if interactive_ok else 'NO'} · "
            f"STYLE-B1 publish={'YES' if publish_allowed_hero else 'BLOCKED — Screen Studio master'}"
        ),
        "urls": {
            "canonical_proof": "https://witnessbc.com/proof",
            "local_proof": "http://127.0.0.1:8090/proof.html",
            "deploy_proof": str(proof_deploy.relative_to(ROOT)) if proof_deploy.is_file() else None,
        },
        "assets": {
            "w1_demo_mp4": str((SITE_ROOT / "assets" / "w1-demo.mp4").relative_to(ROOT)),
            "scenarios": str(scenarios.relative_to(ROOT)),
            "bay_verify": "receipts/bays/witnessbc-proof-lab-bay/verify.json",
        },
        "next_founder_tap": (
            "Proof Lab interactive is deploy-ready — run publish_witnessbc_landing or serve :8090"
            if interactive_ok and not publish_allowed_hero
            else "STYLE-B1 hero ready — bash witnessbc-commercial-film-ship.sh"
            if publish_allowed_hero
            else "Fix bay checks · run witnessbc-site run-recipe"
        ),
        "pattern_learned": {
            "sandbox": "mock_only · demo_seconds · validate-only bay",
            "noetfield": "freemium bay verify + catalog + spec",
            "trust_center": "publish script + receipt + validator",
        },
        "steps": steps,
        "ssot": str(SSOT.relative_to(ROOT)),
    }

    if write:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        pub_urls = _read(SINA / "witnessbc-public-urls-v1.json")
        pub_urls.update(
            {
                "at": _now(),
                "proof_lab_publish_ok": interactive_ok,
                "style_b1_publish_allowed": publish_allowed_hero,
                "proof_lab_receipt": str(RECEIPT),
            }
        )
        (SINA / "witnessbc-public-urls-v1.json").write_text(json.dumps(pub_urls, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="WitnessBC Proof Lab publish")
    ap.add_argument("--skip-recipe", action="store_true", help="Bay + ship gate only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_publish(skip_recipe=args.skip_recipe)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("proof_lab_line"))
        print(f"NEXT: {row.get('next_founder_tap')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
