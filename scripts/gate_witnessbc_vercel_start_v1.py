#!/usr/bin/env python3
"""Gate W — WitnessBC commercial Vercel deploy (main team · monorepo witnessbc-site).

Deploys witnessbc-site/dist/deploy to deploy-witnessbc-agentic-governance on the-777-foundation.
Auth: ~/.sina/sourcea-vercel-token-v1.json (scope MUST be the-777-foundation) or Vercel CLI.

Receipt: ~/.sina/gate-w-witnessbc-vercel-receipt-v1.json
Law: data/vercel-portfolio-map-v1.json · docs/PORTFOLIO_VERCEL_CONSOLIDATION_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SITE = ROOT / "witnessbc-site"
DEPLOY = SITE / "dist" / "deploy"
RECEIPT = SINA / "gate-w-witnessbc-vercel-receipt-v1.json"
DEFAULT_PROJECT = "witnessbc-governance-main"
DEFAULT_SCOPE = "the-777-foundation"
CANONICAL_URL = f"https://{DEFAULT_PROJECT}.vercel.app"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 300):
    import subprocess

    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ,
    )


def _vercel_cmd() -> list[str]:
    from shutil import which

    if which("vercel"):
        return ["vercel"]
    return ["npx", "--yes", "vercel"]


def _parse_vercel_url(output: str) -> str | None:
    for pat in (
        r"Production:\s*(https://[^\s]+)",
        r"(https://[a-z0-9][a-z0-9-]*\.vercel\.app)",
    ):
        m = re.search(pat, output, re.I)
        if m:
            return m.group(1).rstrip(").,")
    return None


def _load_auth() -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_vercel_token_v1 import load_sourcea_vercel_config  # noqa: WPS433

    return load_sourcea_vercel_config()


def _deploy_witnessbc(*, project: str, scope: str, token: str | None) -> dict:
    vc = _vercel_cmd()
    cmd = vc + [
        "deploy",
        str(DEPLOY),
        "--prod",
        "--yes",
        f"--scope={scope}",
        f"--name={project}",
    ]
    if token:
        cmd.append(f"--token={token}")
    proc = _run(cmd, timeout=300)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return {"ok": False, "error": out.strip()[-1200:], "scope": scope, "project": project}
    deploy_url = _parse_vercel_url(out) or CANONICAL_URL
    return {
        "ok": True,
        "project": project,
        "scope": scope,
        "deploy_url": deploy_url.rstrip("/"),
        "base_url": CANONICAL_URL.rstrip("/"),
    }


def _probe(url: str) -> int | None:
    import urllib.request

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "witnessbc-gate-w/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp.read(2048)
            return int(resp.status)
    except OSError:
        return None


def gate_w_start(*, project: str = DEFAULT_PROJECT, skip_recipe: bool = False) -> dict:
    scope = str(os.environ.get("WITNESSBC_VERCEL_SCOPE", DEFAULT_SCOPE)).strip()
    steps: list[dict] = []

    recipe: dict = {"ok": True, "skipped": True}
    if not skip_recipe:
        script = SITE / "scripts" / "deploy_witnessbc_v1.sh"
        proc = _run(["bash", str(script), "--skip-recipe"], cwd=ROOT, timeout=300)
        recipe = {"ok": proc.returncode == 0, "returncode": proc.returncode}
        steps.append({"step": "stage_dist_deploy", **recipe})
        if not recipe.get("ok"):
            row = {
                "ok": False,
                "schema": "gate-w-witnessbc-vercel-v1",
                "at": _now(),
                "gate_w_pass": False,
                "error": "witnessbc_deploy_stage_failed",
                "steps": steps,
            }
            RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            return row

    if not (DEPLOY / "index.html").is_file():
        row = {
            "ok": False,
            "schema": "gate-w-witnessbc-vercel-v1",
            "at": _now(),
            "gate_w_pass": False,
            "error": "missing_deploy_artifact",
            "deploy_dir": str(DEPLOY),
            "steps": steps,
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    auth = _load_auth()
    steps.append(
        {
            "step": "vercel_auth",
            "ok": bool(auth.get("ok")),
            "auth_mode": auth.get("auth_mode"),
            "whoami": auth.get("whoami"),
        }
    )

    dashboard_fix = [
        "Vercel the-777-foundation (kazemnezhadsina144@gmail.com) → Add Project → SourceA",
        "Root Directory: witnessbc-site · Framework: Other",
        "Project name: witnessbc-governance-main (trial owns deploy-witnessbc-agentic-governance)",
        "Output Directory: dist/deploy · Deploy production",
        "Or save main-team token: python3 scripts/sourcea_vercel_token_setup_v1.py --token '...'",
        f"Then: WITNESSBC_VERCEL_SCOPE={DEFAULT_SCOPE} python3 scripts/gate_witnessbc_vercel_start_v1.py --json",
    ]

    if not auth.get("ok"):
        row = {
            "ok": False,
            "schema": "gate-w-witnessbc-vercel-v1",
            "at": _now(),
            "gate_w_pass": False,
            "error": "missing_vercel_auth",
            "canonical_url": CANONICAL_URL,
            "dashboard_fix": dashboard_fix,
            "steps": steps,
        }
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    token = auth.get("token")
    deploy_row = _deploy_witnessbc(project=project, scope=scope, token=token)
    steps.append({"step": "vercel_deploy", **deploy_row})

    verify_code = _probe(f"{CANONICAL_URL}/")
    contact_code = _probe(f"{CANONICAL_URL}/contact")
    gate_w_pass = (
        bool(deploy_row.get("ok"))
        and verify_code is not None
        and 200 <= verify_code < 300
        and contact_code is not None
        and 200 <= contact_code < 300
    )

    row = {
        "ok": gate_w_pass,
        "schema": "gate-w-witnessbc-vercel-v1",
        "at": _now(),
        "gate_w_pass": gate_w_pass,
        "project": project,
        "scope": scope,
        "canonical_url": CANONICAL_URL,
        "verify_http": verify_code,
        "contact_http": contact_code,
        "deploy": deploy_row,
        "steps": steps,
        "founder_line": (
            f"Gate W {'PASS' if gate_w_pass else 'FAIL'} · {CANONICAL_URL}/ · http={verify_code or '?'}"
        ),
        "dashboard_fix": None if gate_w_pass else dashboard_fix,
        "next": (
            "bash scripts/validate-vercel-deploy-urls-v1.sh"
            if gate_w_pass
            else "Main Vercel dashboard deploy OR main-team VERCEL token + re-run Gate W"
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate W — WitnessBC Vercel deploy (main team)")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--skip-recipe", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = gate_w_start(project=args.project, skip_recipe=args.skip_recipe)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("error") or "FAIL")
        if row.get("next"):
            print(f"  Next: {row['next']}")
        if row.get("dashboard_fix"):
            print("  Dashboard:")
            for line in row["dashboard_fix"]:
                print(f"    · {line}")
    return 0 if row.get("gate_w_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
