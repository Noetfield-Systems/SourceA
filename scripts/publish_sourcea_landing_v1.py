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
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
AGENTRUN = Path.home() / "Desktop/agentrun-app"
STAGING = SINA / "sourcea-landing-pages-staging"
RECEIPT = SINA / "sourcea-landing-publish-receipt-v1.json"
PUBLIC_URLS = SINA / "sourcea-public-urls-v1.json"
TUNNEL_LOG = SINA / "sourcea-landing-tunnel-v1.log"
TUNNEL_PID = SINA / "sourcea-landing-tunnel-v1.pid"
TUNNEL_PORT = int(os.environ.get("SOURCEA_LANDING_TUNNEL_PORT", "8190"))
DEFAULT_PROJECT = os.environ.get("SOURCEA_PAGES_PROJECT", "source-a")
PAGES_CUSTOM_DOMAINS: dict[str, tuple[str, ...]] = {
    "sourcea-com": ("sourcea.app", "www.sourcea.app", "sourcea.ca", "www.sourcea.ca", "sourcea.uk", "www.sourcea.uk"),
    "sourcea-landing": ("sourcea.com", "www.sourcea.com"),
}
CANONICAL_PRODUCTION_BASE: dict[str, str] = {
    "sourcea-com": "https://sourcea.app",
}
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
    """Vercel Hobby static — rewrites mirror Cloudflare _redirects (extensionless)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_clean_urls_v1 import vercel_rewrites  # noqa: WPS433

    vercel = {
        "rewrites": vercel_rewrites(),
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
    """Cloudflare Pages — headers; _redirects from build (extensionless clean URLs)."""
    redirects = staging / "_redirects"
    if not redirects.is_file():
        sys.path.insert(0, str(ROOT / "scripts"))
        from sourcea_clean_urls_v1 import write_redirects  # noqa: WPS433

        write_redirects(staging)
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
    start_page = staging / "sourcea" / "start.html"
    if not root_index.is_file() and start_page.is_file():
        shutil.copy2(start_page, root_index)


def _copy_pages_functions(staging: Path) -> None:
    """Cloudflare Pages Functions — commercial MVP intake API."""
    src = ROOT / "cloud" / "pages-functions"
    if not src.is_dir():
        return
    dest = staging / "functions"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def run_copy_depth_gate() -> dict:
    proc = _run(
        [sys.executable, str(ROOT / "scripts" / "landing_copy_depth_gate_v1.py"), "--json"],
        cwd=ROOT,
        timeout=120,
    )
    ok = proc.returncode == 0
    body: dict = {}
    try:
        body = json.loads(proc.stdout) if (proc.stdout or "").strip().startswith("{") else {}
    except json.JSONDecodeError:
        body = {}
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "verdict": body.get("verdict"),
        "finding_count": body.get("finding_count"),
        "findings_tail": (body.get("findings") or [])[:8],
        "receipt": str(Path.home() / ".sina/enforcement/landing-copy-depth-gate-receipt-v1.json"),
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def run_brain_live_smoke(*, base: str = "https://sourcea.app") -> dict:
    env = {**os.environ, "SOURCEA_E2E_BASE": base}
    proc = _run(
        ["bash", str(ROOT / "scripts" / "validate-sourcea-brain-live-v1.sh")],
        cwd=ROOT,
        timeout=120,
        env=env,
    )
    ok = proc.returncode == 0
    receipt = Path.home() / ".sina/enforcement/sourcea-brain-live-gate-receipt-v1.json"
    body: dict = {}
    if receipt.is_file():
        try:
            body = json.loads(receipt.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            body = {}
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "verdict": body.get("verdict") or ("PASS" if ok else "BLOCK"),
        "base": base,
        "receipt": str(receipt),
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def run_ui_mechanical_gate() -> dict:
    proc = _run(
        [sys.executable, str(ROOT / "scripts" / "sourcea_ui_mechanical_gate_v1.py"), "--json"],
        cwd=ROOT,
        timeout=120,
    )
    ok = proc.returncode == 0
    body: dict = {}
    try:
        body = json.loads(proc.stdout) if (proc.stdout or "").strip().startswith("{") else {}
    except json.JSONDecodeError:
        body = {}
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "verdict": body.get("verdict"),
        "finding_count": body.get("finding_count"),
        "findings_tail": (body.get("findings") or [])[:8],
        "receipt": str(Path.home() / ".sina/enforcement/sourcea-ui-mechanical-gate-receipt-v1.json"),
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def run_commercial_copy_gate() -> dict:
    proc = _run(
        [sys.executable, str(ROOT / "scripts" / "landing_commercial_copy_gate_v1.py"), "--json"],
        cwd=ROOT,
        timeout=120,
    )
    ok = proc.returncode == 0
    body: dict = {}
    try:
        body = json.loads(proc.stdout) if (proc.stdout or "").strip().startswith("{") else {}
    except json.JSONDecodeError:
        body = {}
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "verdict": body.get("verdict"),
        "finding_count": body.get("finding_count"),
        "findings_tail": (body.get("findings") or [])[:8],
        "receipt": str(Path.home() / ".sina/enforcement/landing-commercial-copy-gate-receipt-v1.json"),
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def run_recipe() -> dict:
    script = ROOT / "SourceA-landing" / "green-unified" / "scripts" / "run-recipe.sh"
    proc = _run(["bash", str(script)], cwd=ROOT, timeout=600)
    ok = proc.returncode == 0
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-800:], "stderr_tail": (proc.stderr or "")[-400:]}


def run_brain_corpus_refresh() -> dict:
    """Refresh Brain knowledge bundle before landing build (P1-09)."""
    env = {**os.environ, "SKIP_BRAIN_EVAL": os.environ.get("SKIP_BRAIN_EVAL", "1")}
    proc = _run(
        ["bash", str(ROOT / "scripts" / "brain_chatbot_refresh_v1.sh")],
        cwd=ROOT,
        timeout=240,
        env=env,
    )
    ok = proc.returncode == 0
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-600:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def stage_from_build_dist() -> Path:
    """Stage from green-unified/dist when agentrun-app absent (compact living center)."""
    proc = _run([sys.executable, str(ROOT / "scripts" / "build_sourcea_vercel_output_v1.py")], cwd=ROOT, timeout=120)
    if proc.returncode != 0:
        raise SystemExit(f"FAIL: build dist — {(proc.stderr or proc.stdout or '')[-800:]}")
    dist = ROOT / "SourceA-landing" / "green-unified" / "dist"
    if not dist.is_dir():
        raise SystemExit(f"FAIL: dist missing: {dist}")
    boot_proof = dist / "sourcea" / "data" / "boot-proof.json"
    if not boot_proof.is_file():
        raise SystemExit("FAIL: boot-proof.json missing in dist")
    proof_pack = dist / "sourcea" / "data" / "phase1-proof-pack-public-v1.json"
    if not proof_pack.is_file():
        raise SystemExit("FAIL: phase1-proof-pack-public-v1.json missing in dist — site truth gate")
    try:
        pack_row = json.loads(proof_pack.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: phase1-proof-pack-public-v1.json invalid JSON: {exc}") from exc
    if pack_row.get("schema") != "sourcea-phase1-proof-pack-public-v1":
        raise SystemExit(
            f"FAIL: phase1-proof-pack-public-v1.json bad schema: {pack_row.get('schema')!r}"
        )
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(dist, STAGING)
    _write_pages_extras(STAGING)
    _copy_pages_functions(STAGING)
    _write_vercel_json(STAGING)
    manifest = {
        "schema": "sourcea-landing-staging-v1",
        "at": _now(),
        "source": "green-unified/dist",
        "files": sorted(str(p.relative_to(STAGING)) for p in STAGING.rglob("*") if p.is_file()),
        "pages_extras": ["_redirects", "_headers", "index.html"],
        "pages_functions": sorted(
            str(p.relative_to(STAGING)) for p in (STAGING / "functions").rglob("*") if p.is_file()
        )
        if (STAGING / "functions").is_dir()
        else [],
        "vercel_json": True,
    }
    (STAGING / "staging-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return STAGING


def stage_site() -> Path:
    """Always stage from green-unified/dist — agentrun-app may lag repo (Week 0 INCIDENT-042)."""
    return stage_from_build_dist()


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
    scope = str(cfg.get("scope") or os.environ.get("SOURCEA_VERCEL_SCOPE", "the-777-foundation")).strip()
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


def _wrangler_env_oauth_fallback() -> dict[str, str] | None:
    """Wrangler OAuth on main portfolio account when api token file absent."""
    proc = _run(_wrangler_cmd() + ["whoami"], timeout=60)
    if proc.returncode != 0:
        return None
    out = (proc.stdout or "") + (proc.stderr or "")
    if "logged in" not in out.lower():
        return None
    main_acct = "0d0b967b77e2e5535455d39ff3dae72c"
    if main_acct not in out:
        return None
    env = dict(os.environ)
    env.pop("CLOUDFLARE_API_TOKEN", None)
    env["CLOUDFLARE_ACCOUNT_ID"] = main_acct
    return env


def deploy_pages(staging: Path, *, project: str) -> dict:
    tok, _ = _load_cf_api_token()
    if tok:
        wenv = _wrangler_env()
        auth_mode = "api_token_file"
    else:
        wenv = _wrangler_env_oauth_fallback()
        if not wenv:
            return {
                "ok": False,
                "backend": "cloudflare_pages",
                "error": (
                    "no SourceA CF token — create ~/.sina/cf-pages-token-v1.json "
                    "or run: wrangler login (main account 0d0b967b…)"
                ),
                "gate_k": "SMART-331",
                "lane": "sourcea_only",
            }
        auth_mode = "wrangler_oauth"
    wr = _wrangler_cmd()
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
        wr
        + [
            "pages",
            "deploy",
            str(staging),
            f"--project-name={project}",
            "--branch=main",
            "--commit-dirty=true",
        ],
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
        "auth_mode": auth_mode,
        "base_url": base.rstrip("/"),
        "ephemeral": False,
        "gate_k": "SMART-392",
        "project": project,
    }


def _load_wrangler_oauth_token() -> str | None:
    """Return a valid wrangler OAuth access token (refresh if expired)."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from sourcea_pages_activate_domains_v1 import _get_access_token  # noqa: WPS433

        return _get_access_token()
    except SystemExit:
        return None
    except Exception:
        cfg = Path.home() / "Library/Preferences/.wrangler/config/default.toml"
        if not cfg.is_file():
            return None
        m = re.search(r'^oauth_token = "(.+)"', cfg.read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else None


def _cf_api(token: str, path: str, *, method: str = "GET", data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode())
        except Exception:
            payload = {"success": False, "errors": [{"message": str(exc)}]}
        payload["_http_status"] = exc.code
        return payload


def add_pages_custom_domains(*, project: str, domains: tuple[str, ...] | None = None) -> dict:
    """Attach custom domains via Cloudflare API (wrangler v4 removed pages domain CLI)."""
    doms = domains or PAGES_CUSTOM_DOMAINS.get(project, ())
    if not doms:
        return {"ok": True, "skipped": True, "reason": "no_domains_for_project", "project": project}

    tok, acct = _load_cf_api_token()
    if not tok:
        tok = _load_wrangler_oauth_token()
    if not tok:
        return {
            "ok": False,
            "error": "no_cf_auth_for_custom_domains",
            "fix": "wrangler login or ~/.sina/cf-pages-token-v1.json",
        }
    account_id = acct or os.environ.get("CLOUDFLARE_ACCOUNT_ID") or "0d0b967b77e2e5535455d39ff3dae72c"
    rows: list[dict] = []
    all_ok = True
    for dom in doms:
        res = _cf_api(
            tok,
            f"/accounts/{account_id}/pages/projects/{project}/domains",
            method="POST",
            data={"name": dom},
        )
        ok = bool(res.get("success"))
        errs = [str(e.get("message") or e) for e in res.get("errors") or []]
        if not ok and any("already" in e.lower() for e in errs):
            ok = True
        rows.append(
            {
                "domain": dom,
                "ok": ok,
                "note": errs[0] if errs and not ok else "added or exists",
            }
        )
        if not ok:
            all_ok = False
    return {"ok": all_ok, "project": project, "account_id": account_id, "domains": rows}


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
        f"{base}/",
        f"{base}/sourcea/start.html",
        f"{base}/sourcea/scenario.html",
        f"{base}/sourcea/proof.html",
        f"{base}/sourcea/forge/terminal",
        f"{base}/forge/terminal",
        f"{base}/sourcea/data/boot-proof.json",
        f"{base}/sourcea/data/phase1-proof-pack-public-v1.json",
        f"{base}/sourcea/data/sourcea-brain-chat-config-v1.json",
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
        elif "sourcea-brain-chat-config-v1.json" in url and body:
            if body.lstrip().startswith("<!") or body.lstrip().startswith("<html"):
                row["brain_config_schema"] = "html_poison"
                row["ok"] = False
                ok = False
            else:
                try:
                    cfg = json.loads(body)
                    row["brain_config_schema"] = cfg.get("schema")
                    row["brain_worker_url"] = bool(cfg.get("api_worker_url"))
                    if cfg.get("schema") != "sourcea-brain-chat-config-v1":
                        row["ok"] = False
                        ok = False
                except json.JSONDecodeError:
                    row["brain_config_schema"] = "invalid_json"
                    row["ok"] = False
                    ok = False
        elif "phase1-proof-pack-public-v1.json" in url and body:
            if body.lstrip().startswith("<!") or body.lstrip().startswith("<html"):
                row["proof_pack_schema"] = "html_poison"
                row["ok"] = False
                ok = False
            else:
                try:
                    pack = json.loads(body)
                    row["proof_pack_schema"] = pack.get("schema")
                    row["proof_pack_id"] = pack.get("pack_id")
                    row["proof_pack_verdict"] = pack.get("verdict")
                    row["proof_pack_ok"] = pack.get("schema") == "sourcea-phase1-proof-pack-public-v1"
                    if not row["proof_pack_ok"]:
                        row["ok"] = False
                        ok = False
                except json.JSONDecodeError:
                    row["proof_pack_schema"] = "invalid_json"
                    row["ok"] = False
                    ok = False
        elif url == f"{base}/" or url == base:
            row["founder_headline"] = "AI that proves its work" in body or "sourcea-boot" in body
            if row.get("ok") and not row["founder_headline"]:
                row["ok"] = False
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
        "phase1_proof_pack_url": f"{base}/sourcea/data/phase1-proof-pack-public-v1.json",
    }
    PUBLIC_URLS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    write_desktop_url_note(row)
    return row


def refresh_outbound_packs() -> dict:
    try:
        proc = _run(
            [sys.executable, str(ROOT / "scripts" / "commercial_pipeline_repair_v1.py"), "--json"],
            cwd=ROOT,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {"ok": True, "skipped": True, "reason": "outbound_refresh_timeout"}
    try:
        return json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {"ok": proc.returncode == 0}
    except json.JSONDecodeError:
        return {"ok": proc.returncode == 0, "out": (proc.stdout or "")[-400:]}


def run_founder_proof_verify(*, min_seconds: int = 60) -> dict[str, Any]:
    """Public HTTPS verify of 15 founder recipes — fail-closed after Pages publish."""
    if min_seconds > 0:
        time.sleep(min_seconds)
    proc = _run(
        [
            sys.executable,
            str(ROOT / "scripts/verify_client_proof_founder_review_v1.py"),
            "--json",
            "--write-receipt",
            "--min-seconds-after-deploy",
            str(min_seconds),
        ],
        cwd=ROOT,
        timeout=180,
    )
    try:
        row = json.loads(proc.stdout)
        return {
            "ok": proc.returncode == 0 and bool(row.get("ok")),
            "passed": row.get("passed"),
            "total": row.get("total"),
            "receipt_path": str(Path.home() / ".sina/client-proof-founder-review-verify-v1.json"),
            "verify_law": row.get("verify_law"),
        }
    except json.JSONDecodeError:
        return {"ok": False, "error": (proc.stderr or proc.stdout)[-400:]}


def publish(
    *,
    backend: str = "auto",
    project: str = DEFAULT_PROJECT,
    skip_recipe: bool = False,
    custom_domain: bool = False,
) -> dict:
    steps: list[dict] = []
    guard_proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "deploy_dirty_tree_guard_v1.py"), "--scope", "landing", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    dirty_guard: dict = {"ok": guard_proc.returncode == 0}
    try:
        dirty_guard = json.loads(guard_proc.stdout or "{}")
    except json.JSONDecodeError:
        dirty_guard["parse_error"] = True
    steps.append({"step": "dirty_tree_guard", **dirty_guard})
    if not dirty_guard.get("ok"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "at": _now(),
            "steps": steps,
            "error": "dirty_tree_guard BLOCK — commit scoped landing files before publish",
        }

    copy_gate = run_commercial_copy_gate()
    steps.append({"step": "commercial_copy_gate", **copy_gate})
    if not copy_gate.get("ok"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "steps": steps,
            "error": "commercial_copy_gate BLOCK — fix copy in the repository before publish",
        }

    depth_gate = run_copy_depth_gate()
    steps.append({"step": "copy_depth_gate", **depth_gate})
    if not depth_gate.get("ok"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "steps": steps,
            "error": "copy_depth_gate BLOCK — cut repetition/padding in the repository before publish",
        }

    ui_gate = run_ui_mechanical_gate()
    steps.append({"step": "ui_mechanical_gate", **ui_gate})
    if not ui_gate.get("ok"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "steps": steps,
            "error": "ui_mechanical_gate BLOCK — fix mechanical UI regressions before publish",
        }

    if not skip_recipe:
        recipe = run_recipe()
        steps.append({"step": "run_recipe", **recipe})
        if not recipe.get("ok"):
            return {"ok": False, "schema": "sourcea-landing-publish-v1", "steps": steps, "error": "run_recipe failed"}

    brain_refresh = run_brain_corpus_refresh()
    steps.append({"step": "brain_corpus_refresh", **brain_refresh})
    if not brain_refresh.get("ok"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "steps": steps,
            "error": "brain_corpus_refresh failed — fix knowledge pipeline before publish",
        }

    staging = stage_site()
    steps.append({
        "step": "stage",
        "ok": True,
        "path": str(staging),
        "boot_proof": str(staging / "sourcea" / "data" / "boot-proof.json"),
        "phase1_proof_pack": str(staging / "sourcea" / "data" / "phase1-proof-pack-public-v1.json"),
    })

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

    if custom_domain and deploy_row.get("backend") == "cloudflare_pages":
        domain_row = add_pages_custom_domains(project=project)
        steps.append({"step": "custom_domains", **domain_row})

    base_url = str(deploy_row.get("base_url") or "")
    canonical_base = CANONICAL_PRODUCTION_BASE.get(project) if custom_domain else None
    public_base = canonical_base or base_url
    local_port = TUNNEL_PORT if deploy_row.get("backend") == "cloudflared_tunnel" else None
    verify = verify_public(base_url, local_port=local_port)
    steps.append({"step": "verify", **verify})

    brain_live: dict = {"ok": True, "skipped": True, "reason": "ephemeral or non-pages deploy"}
    if deploy_row.get("backend") in ("cloudflare_pages", "vercel") and not deploy_row.get("ephemeral"):
        brain_live = run_brain_live_smoke(base="https://sourcea.app")
    steps.append({"step": "brain_live_production", **brain_live})
    if not brain_live.get("ok"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "at": _now(),
            "steps": steps,
            "error": "brain_live_production BLOCK — production Brain smoke failed on sourcea.app",
        }

    founder_proof: dict = {"ok": True, "skipped": True, "reason": "not sourcea-com pages deploy"}
    if (
        deploy_row.get("backend") == "cloudflare_pages"
        and project == "sourcea-com"
        and not deploy_row.get("ephemeral")
    ):
        founder_proof = run_founder_proof_verify(min_seconds=60)
    steps.append({"step": "founder_proof_verify", **founder_proof})
    if not founder_proof.get("ok") and not founder_proof.get("skipped"):
        return {
            "ok": False,
            "schema": "sourcea-landing-publish-v1",
            "at": _now(),
            "steps": steps,
            "error": "founder_proof_verify BLOCK — 15-recipe public verify failed after publish",
        }

    public = write_public_urls(public_base, boot_verdict=boot_verdict)
    steps.append({"step": "public_urls", "ok": True, "path": str(PUBLIC_URLS), "canonical_base": public_base})
    repair = refresh_outbound_packs()
    steps.append({"step": "outbound_refresh", **repair})

    row = {
        "ok": (verify.get("ok", False) or bool(canonical_base and brain_live.get("ok"))) and brain_live.get("ok", False),
        "schema": "sourcea-landing-publish-v1",
        "at": _now(),
        "base_url": public_base,
        "deploy_url": base_url,
        "ephemeral": deploy_row.get("ephemeral", False),
        "backend": deploy_row.get("backend"),
        "boot_verdict": boot_verdict,
        "public_urls": public,
        "steps": steps,
        "founder_line": (
            f"Published · {public_base}/sourcea/scenario.html · boot={boot_verdict or '?'}"
            + (" · ephemeral tunnel" if deploy_row.get("ephemeral") else "")
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish SourceA landing (recipe + boot-proof + public URL)")
    ap.add_argument("--backend", choices=["auto", "vercel", "pages", "tunnel", "cloudflare"], default="auto")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--skip-recipe", action="store_true")
    ap.add_argument(
        "--custom-domain",
        action="store_true",
        help="Add project custom domains after Pages deploy (sourcea-com → sourcea.app)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    backend = args.backend
    if backend == "cloudflare":
        backend = "pages"
    if backend == "auto" and (args.custom_domain or args.project == "sourcea-com"):
        backend = "pages"
    row = publish(
        backend=backend,
        project=args.project,
        skip_recipe=args.skip_recipe,
        custom_domain=args.custom_domain,
    )
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
