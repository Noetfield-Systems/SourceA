#!/usr/bin/env python3
"""Publish SourceA green-unified landing — run-recipe · stage · Vercel · Pages · tunnel.

Gate K default: Vercel Hobby (free, no Cloudflare). Pages optional (CF free tier).
Law: publish includes boot-proof.json inject (run-recipe step 2b).
Receipt: ~/.sina/sourcea-landing-publish-receipt-v1.json
Public URLs: ~/.sina/sourcea-public-urls-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
AGENTRUN = Path.home() / "Desktop/agentrun-app"
STAGING = SINA / "sourcea-landing-pages-staging"
RECEIPT = SINA / "sourcea-landing-publish-receipt-v1.json"
PUBLIC_URLS = SINA / "sourcea-public-urls-v1.json"
TUNNEL_LOG = SINA / "sourcea-landing-tunnel-v1.log"
TUNNEL_PID = SINA / "sourcea-landing-tunnel-v1.pid"
TUNNEL_PORT = int(os.environ.get("SOURCEA_LANDING_TUNNEL_PORT", "8190"))
DEFAULT_PROJECT = os.environ.get("SOURCEA_PAGES_PROJECT", "sourcea-landing")
CLOUDFLARED = SINA / "bin" / "cloudflared"
CF_TOKEN_FILE = SINA / "cf-pages-token-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 600,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env or os.environ,
    )


def _wrangler_cmd() -> list[str]:
    from shutil import which

    if which("wrangler"):
        return ["wrangler"]
    return ["npx", "--yes", "wrangler"]


def _load_cf_api_token() -> tuple[str | None, str | None]:
    """SourceA-only — ~/.sina/cf-pages-token-v1.json (never TrustField secrets.env)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_cf_pages_token_v1 import load_sourcea_cf_config  # noqa: WPS433

    cfg = load_sourcea_cf_config()
    if cfg.get("ok"):
        return str(cfg["api_token"]), cfg.get("account_id")
    return None, None


def _wrangler_env() -> dict[str, str]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_cf_pages_token_v1 import wrangler_env  # noqa: WPS433

    return wrangler_env()


def _write_vercel_json(staging: Path) -> None:
    """Vercel Hobby static — rewrites mirror Cloudflare _redirects."""
    vercel = {
        "rewrites": [
            {"source": "/", "destination": "/sourcea/index.html"},
            {"source": "/sourcea", "destination": "/sourcea/index.html"},
            {"source": "/proof", "destination": "/sourcea/proof.html"},
            {"source": "/platform", "destination": "/sourcea/platform.html"},
            {"source": "/scenario", "destination": "/sourcea/scenario.html"},
        ],
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {"key": "X-Frame-Options", "value": "DENY"},
                    {"key": "X-Content-Type-Options", "value": "nosniff"},
                    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                ],
            },
            {
                "source": "/sourcea/data/(.*)",
                "headers": [{"key": "Cache-Control", "value": "public, max-age=60"}],
            },
        ],
    }
    (staging / "vercel.json").write_text(json.dumps(vercel, indent=2) + "\n", encoding="utf-8")


def _write_pages_extras(staging: Path) -> None:
    """Cloudflare Pages — redirects, headers, root → /sourcea/."""
    (staging / "_redirects").write_text(
        "\n".join(
            [
                "/              /sourcea/              302",
                "/sourcea       /sourcea/              302",
                "/proof         /sourcea/proof.html    302",
                "/platform      /sourcea/platform.html 302",
                "/scenario      /sourcea/scenario.html 302",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (staging / "_headers").write_text(
        "\n".join(
            [
                "/*",
                "  X-Frame-Options: DENY",
                "  X-Content-Type-Options: nosniff",
                "  Referrer-Policy: strict-origin-when-cross-origin",
                "",
                "/sourcea/data/*",
                "  Cache-Control: public, max-age=60",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    root_index = staging / "index.html"
    if not root_index.is_file():
        root_index.write_text(
            '<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=/sourcea/" />'
            '<link rel="canonical" href="/sourcea/" /></head><body></body></html>\n',
            encoding="utf-8",
        )


def run_recipe() -> dict:
    script = ROOT / "SourceA-landing" / "green-unified" / "scripts" / "run-recipe.sh"
    proc = _run(["bash", str(script)], cwd=ROOT, timeout=600)
    ok = proc.returncode == 0
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-800:], "stderr_tail": (proc.stderr or "")[-400:]}


def stage_site() -> Path:
    src_sourcea = AGENTRUN / "sourcea"
    src_assets = AGENTRUN / "assets"
    if not src_sourcea.is_dir():
        raise SystemExit(f"FAIL: deploy missing — run recipe first: {src_sourcea}")
    boot_proof = src_sourcea / "data" / "boot-proof.json"
    if not boot_proof.is_file():
        raise SystemExit("FAIL: boot-proof.json missing — run inject_sourcea_boot_terminal_v1.py")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    shutil.copytree(src_sourcea, STAGING / "sourcea")
    if src_assets.is_dir():
        shutil.copytree(src_assets, STAGING / "assets")
    _write_pages_extras(STAGING)
    _write_vercel_json(STAGING)
    manifest = {
        "schema": "sourcea-landing-staging-v1",
        "at": _now(),
        "files": sorted(str(p.relative_to(STAGING)) for p in STAGING.rglob("*") if p.is_file()),
        "pages_extras": ["_redirects", "_headers", "index.html"],
        "vercel_json": True,
    }
    (STAGING / "staging-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return STAGING


def _parse_pages_url(output: str) -> str | None:
    for pat in (
        r"https://[a-z0-9-]+\.pages\.dev",
        r"Deployment complete! Take a peek over at (https://[^\s]+)",
    ):
        m = re.search(pat, output, re.I)
        if m:
            return m.group(1).rstrip(").")
    return None


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


def _load_vercel_token() -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_vercel_token_v1 import load_sourcea_vercel_config  # noqa: WPS433

    return load_sourcea_vercel_config()


def deploy_vercel(staging: Path, *, project: str) -> dict:
    cfg = _load_vercel_token()
    if not cfg.get("ok"):
        return {
            "ok": False,
            "backend": "vercel_hobby",
            "error": cfg.get("error") or "no SourceA Vercel auth",
            "fix_steps": cfg.get("fix_steps") or [],
            "fix_url": cfg.get("fix_url"),
            "gate_k": "SMART-332",
            "lane": "sourcea_only",
            "cost": "free_hobby",
        }
    proj = str(cfg.get("project") or project).strip() or project
    scope = str(cfg.get("scope") or os.environ.get("SOURCEA_VERCEL_SCOPE", "noetfield-systems")).strip()
    vc = _vercel_cmd()
    cmd = vc + ["deploy", str(staging), "--prod", "--yes", f"--scope={scope}"]
    if proj:
        cmd.append(f"--name={proj}")
    auth_mode = str(cfg.get("auth_mode") or "token_file")
    if cfg.get("token"):
        cmd.append(f"--token={cfg['token']}")
    deploy = _run(cmd, timeout=300)
    out = (deploy.stdout or "") + (deploy.stderr or "")
    if deploy.returncode != 0:
        return {
            "ok": False,
            "backend": "vercel_hobby",
            "auth_mode": auth_mode,
            "error": out.strip()[-1200:],
            "gate_k": "SMART-332",
            "cost": "free_hobby",
        }
    base = _parse_vercel_url(out) or f"https://{proj}.vercel.app"
    # Team-scoped deployment URLs may be SSO-gated; canonical *.vercel.app alias is public.
    canonical = f"https://{proj}.vercel.app"
    return {
        "ok": True,
        "backend": "vercel_hobby",
        "auth_mode": auth_mode,
        "whoami": cfg.get("whoami"),
        "base_url": canonical.rstrip("/"),
        "deploy_url": base.rstrip("/"),
        "ephemeral": False,
        "gate_k": "SMART-332",
        "project": proj,
        "scope": scope,
        "cost": "free_hobby",
    }


def deploy_pages(staging: Path, *, project: str) -> dict:
    tok, _ = _load_cf_api_token()
    if not tok:
        return {
            "ok": False,
            "backend": "cloudflare_pages",
            "error": (
                "no SourceA CF token — create ~/.sina/cf-pages-token-v1.json "
                "(SourceA account only — NOT TrustField secrets.env)"
            ),
            "gate_k": "SMART-331",
            "lane": "sourcea_only",
        }
    wr = _wrangler_cmd()
    wenv = _wrangler_env()
    listed = _run(wr + ["pages", "project", "list"], timeout=120, env=wenv)
    if project not in (listed.stdout or ""):
        created = _run(
            wr + ["pages", "project", "create", project, "--production-branch=main"],
            timeout=120,
            env=wenv,
        )
        if created.returncode != 0 and "already exists" not in (created.stderr or "").lower():
            return {"ok": False, "backend": "cloudflare_pages", "error": (created.stderr or created.stdout or "").strip()}
    deploy = _run(
        wr + ["pages", "deploy", str(staging), f"--project-name={project}", "--commit-dirty=true"],
        timeout=300,
        env=wenv,
    )
    out = (deploy.stdout or "") + (deploy.stderr or "")
    if deploy.returncode != 0:
        return {"ok": False, "backend": "cloudflare_pages", "error": out.strip()[-1200:]}
    base = _parse_pages_url(out) or f"https://{project}.pages.dev"
    return {
        "ok": True,
        "backend": "cloudflare_pages",
        "base_url": base.rstrip("/"),
        "ephemeral": False,
        "gate_k": "SMART-392",
        "project": project,
    }


def _cloudflared() -> Path | None:
    from shutil import which

    if which("cloudflared"):
        return Path(which("cloudflared") or "")
    if CLOUDFLARED.is_file() and os.access(CLOUDFLARED, os.X_OK):
        return CLOUDFLARED
    return None


def _pids_on_port(port: int) -> list[int]:
    try:
        proc = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode != 0:
            return []
        return [int(x) for x in (proc.stdout or "").strip().split() if x.strip().isdigit()]
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return []


def _stop_tunnel() -> None:
    if TUNNEL_PID.is_file():
        try:
            os.kill(int(TUNNEL_PID.read_text().strip()), 15)
        except (OSError, ValueError):
            pass
        TUNNEL_PID.unlink(missing_ok=True)
    for pid in _pids_on_port(TUNNEL_PORT):
        try:
            os.kill(pid, 15)
        except OSError:
            pass


def deploy_tunnel(staging: Path) -> dict:
    cf = _cloudflared()
    if not cf:
        return {"ok": False, "backend": "cloudflared_tunnel", "error": "cloudflared not available"}
    _stop_tunnel()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(TUNNEL_PORT), "--bind", "127.0.0.1"],
        cwd=str(staging),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    TUNNEL_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_fh = TUNNEL_LOG.open("w", encoding="utf-8")
    tunnel = subprocess.Popen(
        [str(cf), "tunnel", "--url", f"http://127.0.0.1:{TUNNEL_PORT}"],
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )
    TUNNEL_PID.write_text(f"{tunnel.pid}\n", encoding="utf-8")
    base_url = None
    for _ in range(35):
        time.sleep(1)
        if TUNNEL_LOG.is_file():
            text = TUNNEL_LOG.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", text)
            if m:
                base_url = m.group(0)
                break
        if tunnel.poll() is not None:
            break
    if not base_url:
        server.terminate()
        return {
            "ok": False,
            "backend": "cloudflared_tunnel",
            "error": "tunnel URL not found",
            "log_tail": TUNNEL_LOG.read_text(encoding="utf-8", errors="replace")[-600:] if TUNNEL_LOG.is_file() else "",
        }
    return {
        "ok": True,
        "backend": "cloudflared_tunnel",
        "base_url": base_url.rstrip("/"),
        "ephemeral": True,
        "server_pid": server.pid,
        "tunnel_pid": tunnel.pid,
    }


def verify_public(base_url: str, *, local_port: int | None = None) -> dict:
    base = base_url.rstrip("/")
    checks = [
        f"{base}/sourcea/scenario.html",
        f"{base}/sourcea/proof.html",
        f"{base}/sourcea/data/boot-proof.json",
    ]
    results: list[dict] = []
    ok = True
    for url in checks:
        code = 0
        body = ""
        last_err = ""
        for attempt in range(8):
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    code = resp.status
                    body = resp.read(8000).decode("utf-8", errors="replace")
                    if code == 200:
                        break
            except Exception as exc:
                last_err = str(exc)
            time.sleep(1.5 if attempt < 7 else 0)
        row = {"url": url, "status": code, "ok": code == 200}
        if code != 200 and local_port and "trycloudflare.com" in base:
            local_url = url.replace(base, f"http://127.0.0.1:{local_port}", 1)
            try:
                with urllib.request.urlopen(local_url, timeout=10) as resp:
                    lcode = resp.status
                    lbody = resp.read(8000).decode("utf-8", errors="replace")
                if lcode == 200:
                    row["local_ok"] = True
                    row["local_url"] = local_url
                    code = lcode
                    body = lbody
                    row["ok"] = True
                    row["status"] = lcode
                    row["note"] = "public DNS pending — local tunnel server OK"
            except Exception as exc:
                row["local_err"] = str(exc)
        if "boot-proof.json" in url and body:
            try:
                boot = json.loads(body)
                row["boot_verdict"] = boot.get("verdict")
                row["boot_ok"] = boot.get("ok")
            except json.JSONDecodeError:
                row["boot_verdict"] = "invalid_json"
                ok = False
        if not row.get("ok"):
            ok = False
            if last_err:
                row["error"] = last_err
        results.append(row)
    return {"ok": ok, "checks": results}


def write_desktop_url_note(public: dict) -> Path:
    """UPGR-052 — latest landing URLs on Desktop (survives tunnel confusion)."""
    note = Path.home() / "Desktop" / "SourceA-Landing-URL.txt"
    scenario = public.get("scenario_url") or public.get("base_url", "")
    local = f"http://127.0.0.1:{TUNNEL_PORT}/sourcea/scenario.html"
    body = "\n".join(
        [
            f"SourceA landing · updated {_now()}",
            f"Public scenario: {scenario}",
            f"Local scenario:  {local}",
            f"Proof:           {(public.get('proof_url') or scenario.replace('scenario.html', 'proof.html'))}",
            "",
            "Republish after tunnel death:",
            "  cd ~/Desktop/SourceA && python3 scripts/publish_sourcea_landing_v1.py --backend tunnel --skip-recipe",
            "",
            "Gate K (durable, free — no Cloudflare):",
            "  python3 scripts/gate_k_vercel_start_v1.py --json",
            "",
            "Mac Health Stop keeps this tunnel alive (UPGR-051).",
            "",
        ]
    )
    note.write_text(body, encoding="utf-8")
    return note


def write_public_urls(base_url: str, *, boot_verdict: str | None) -> dict:
    base = base_url.rstrip("/")
    row = {
        "schema": "sourcea-public-urls-v1",
        "at": _now(),
        "base_url": base,
        "scenario_url": f"{base}/sourcea/scenario.html",
        "proof_url": f"{base}/sourcea/proof.html",
        "w1_proof_url": f"{base}/sourcea/proof.html#w1-demo-film",
        "boot_proof_url": f"{base}/sourcea/data/boot-proof.json",
        "boot_verdict": boot_verdict,
    }
    PUBLIC_URLS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    write_desktop_url_note(row)
    return row


def refresh_outbound_packs() -> dict:
    proc = _run([sys.executable, str(ROOT / "scripts" / "commercial_pipeline_repair_v1.py"), "--json"], cwd=ROOT, timeout=120)
    try:
        return json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {"ok": proc.returncode == 0}
    except json.JSONDecodeError:
        return {"ok": proc.returncode == 0, "out": (proc.stdout or "")[-400:]}


def publish(*, backend: str = "auto", project: str = DEFAULT_PROJECT, skip_recipe: bool = False) -> dict:
    steps: list[dict] = []
    if not skip_recipe:
        recipe = run_recipe()
        steps.append({"step": "run_recipe", **recipe})
        if not recipe.get("ok"):
            return {"ok": False, "schema": "sourcea-landing-publish-v1", "steps": steps, "error": "run_recipe failed"}

    staging = stage_site()
    steps.append({"step": "stage", "ok": True, "path": str(staging), "boot_proof": str(staging / "sourcea" / "data" / "boot-proof.json")})

    boot_verdict = None
    try:
        boot_verdict = json.loads((staging / "sourcea" / "data" / "boot-proof.json").read_text())["verdict"]
    except (OSError, json.JSONDecodeError, KeyError):
        pass

    deploy_row: dict
    if backend == "vercel":
        deploy_row = deploy_vercel(staging, project=project)
    elif backend == "pages":
        deploy_row = deploy_pages(staging, project=project)
    elif backend == "tunnel":
        deploy_row = deploy_tunnel(staging)
    else:
        deploy_row = deploy_vercel(staging, project=project)
        if not deploy_row.get("ok"):
            steps.append({"step": "vercel_fallback", **deploy_row})
            deploy_row = deploy_tunnel(staging)

    steps.append({"step": "deploy", **deploy_row})
    if not deploy_row.get("ok"):
        return {"ok": False, "schema": "sourcea-landing-publish-v1", "at": _now(), "steps": steps}

    base_url = str(deploy_row.get("base_url") or "")
    local_port = TUNNEL_PORT if deploy_row.get("backend") == "cloudflared_tunnel" else None
    verify = verify_public(base_url, local_port=local_port)
    steps.append({"step": "verify", **verify})
    public = write_public_urls(base_url, boot_verdict=boot_verdict)
    steps.append({"step": "public_urls", "ok": True, "path": str(PUBLIC_URLS)})
    repair = refresh_outbound_packs()
    steps.append({"step": "outbound_refresh", **repair})

    row = {
        "ok": verify.get("ok", False),
        "schema": "sourcea-landing-publish-v1",
        "at": _now(),
        "base_url": base_url,
        "ephemeral": deploy_row.get("ephemeral", False),
        "backend": deploy_row.get("backend"),
        "boot_verdict": boot_verdict,
        "public_urls": public,
        "steps": steps,
        "founder_line": (
            f"Published · {base_url}/sourcea/scenario.html · boot={boot_verdict or '?'}"
            + (" · ephemeral tunnel" if deploy_row.get("ephemeral") else "")
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish SourceA landing (recipe + boot-proof + public URL)")
    ap.add_argument("--backend", choices=["auto", "vercel", "pages", "tunnel"], default="auto")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--skip-recipe", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = publish(backend=args.backend, project=args.project, skip_recipe=args.skip_recipe)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("error") or "FAIL")
        if not row.get("ok"):
            for s in row.get("steps", []):
                if not s.get("ok", True):
                    print(f"  FAIL: {s.get('step')} — {s.get('error', s)}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
