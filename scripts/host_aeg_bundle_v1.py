#!/usr/bin/env python3
"""Host AEG forensic bundles — Cloudflare Pages (preferred) or quick tunnel fallback.

Stages ~/.sina/aeg/{id}/ → public proof_url · updates aeg-config + latest receipt.
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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
AEG_ROOT = SINA / "aeg"
STAGING = SINA / "aeg-pages-staging"
AEG_CONFIG = SINA / "aeg-config-v1.json"
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"
HOST_RECEIPT = SINA / "aeg-host-receipt-v1.json"
DEFAULT_PROJECT = os.environ.get("AEG_PAGES_PROJECT", "sourcea-aeg-proof")
TUNNEL_PORT = int(os.environ.get("AEG_HOST_PORT", "8093"))
TUNNEL_LOG = SINA / "aeg-tunnel-v1.log"
TUNNEL_PID = SINA / "aeg-tunnel-v1.pid"
CLOUDFLARED = SINA / "bin" / "cloudflared"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _which(name: str) -> str | None:
    from shutil import which

    return which(name)


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _wrangler_cmd() -> list[str]:
    if _which("wrangler"):
        return ["wrangler"]
    return ["npx", "--yes", "wrangler"]


def _ensure_cloudflared() -> Path | None:
    if _which("cloudflared"):
        return Path(_which("cloudflared") or "")
    if CLOUDFLARED.is_file() and os.access(CLOUDFLARED, os.X_OK):
        return CLOUDFLARED
    CLOUDFLARED.parent.mkdir(parents=True, exist_ok=True)
    arch = "arm64" if os.uname().machine == "arm64" else "amd64"
    url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-{arch}.tgz"
    tmp = SINA / "tmp-cloudflared.tgz"
    try:
        urllib.request.urlretrieve(url, tmp)
        _run(["tar", "-xzf", str(tmp), "-C", str(CLOUDFLARED.parent)])
        bin_path = CLOUDFLARED.parent / "cloudflared"
        if bin_path.is_file():
            bin_path.chmod(0o755)
            return bin_path
    except Exception:
        return None
    return None


def _list_bundles(evidence_id: str | None = None) -> list[Path]:
    if evidence_id:
        p = AEG_ROOT / evidence_id
        if not p.is_dir():
            raise SystemExit(f"FAIL: bundle not found: {p}")
        return [p]
    if not AEG_ROOT.is_dir():
        return []
    return sorted([p for p in AEG_ROOT.iterdir() if p.is_dir() and p.name.startswith("aeg-")])


def _write_staging_index(staging: Path, bundles: list[str]) -> None:
    rows = "\n".join(
        f'    <li><a href="{bid}/">{bid}</a> — BLOCK forensic bundle</li>'
        for bid in reversed(bundles)
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>SourceA AEG Proof Index</title>
  <style>
    body {{ font-family: Inter, system-ui, sans-serif; background: #0b1220; color: #e2e8f0; padding: 2rem; max-width: 720px; margin: auto; }}
    h1 {{ font-size: 1.25rem; }}
    a {{ color: #2dd4bf; }}
    ul {{ line-height: 1.8; }}
  </style>
</head>
<body>
  <h1>SourceA · Automated Evidence Generation</h1>
  <p>Forensic BLOCK bundles — terminal + UI capture + JSON receipt.</p>
  <ul>
{rows}
  </ul>
</body>
</html>
"""
    (staging / "index.html").write_text(html, encoding="utf-8")


def stage_bundles(*, evidence_id: str | None = None) -> tuple[Path, list[str]]:
    bundles = _list_bundles(evidence_id)
    if not bundles:
        raise SystemExit("FAIL: no AEG bundles on disk")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    ids: list[str] = []
    for src in bundles:
        dst = STAGING / src.name
        shutil.copytree(src, dst)
        ids.append(src.name)
    _write_staging_index(STAGING, ids)
    _write_json(
        STAGING / "host-manifest.json",
        {"schema": "aeg-host-staging-v1", "at": _now(), "bundles": ids},
    )
    return STAGING, ids


def _parse_pages_url(output: str) -> str | None:
    for pat in (
        r"https://[a-z0-9-]+\.pages\.dev",
        r"Deployment complete! Take a peek over at (https://[^\s]+)",
        r"(https://[a-z0-9-]+\.pages\.dev[^\s]*)",
    ):
        m = re.search(pat, output, re.I)
        if m:
            return m.group(1).rstrip(").")
    return None


def deploy_pages(staging: Path, *, project: str) -> dict[str, Any]:
    wr = _wrangler_cmd()
    listed = _run(wr + ["pages", "project", "list"])
    if project not in listed.stdout:
        created = _run(wr + ["pages", "project", "create", project, "--production-branch=main"])
        if created.returncode != 0 and "8000007" not in created.stderr and "already exists" not in created.stderr.lower():
            return {
                "ok": False,
                "backend": "cloudflare_pages",
                "error": (created.stderr or created.stdout or "project create failed").strip(),
            }
    deploy = _run(wr + ["pages", "deploy", str(staging), f"--project-name={project}", "--commit-dirty=true"], timeout=300)
    out = deploy.stdout + deploy.stderr
    if deploy.returncode != 0:
        return {"ok": False, "backend": "cloudflare_pages", "error": out.strip()}
    base = _parse_pages_url(out) or f"https://{project}.pages.dev"
    return {"ok": True, "backend": "cloudflare_pages", "base_url": base.rstrip("/"), "raw": out.strip()}


def _stop_tunnel() -> None:
    if TUNNEL_PID.is_file():
        try:
            pid = int(TUNNEL_PID.read_text().strip())
            os.kill(pid, 15)
        except (OSError, ValueError):
            pass
        TUNNEL_PID.unlink(missing_ok=True)


def deploy_tunnel(staging: Path) -> dict[str, Any]:
    cf = _ensure_cloudflared()
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
    _write_json(
        SINA / "aeg-tunnel-server-v1.json",
        {"port": TUNNEL_PORT, "server_pid": server.pid, "tunnel_pid": tunnel.pid, "at": _now()},
    )

    base_url = None
    for _ in range(30):
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
            "error": f"tunnel URL not found in {TUNNEL_LOG}",
            "log_tail": TUNNEL_LOG.read_text(encoding="utf-8", errors="replace")[-800:] if TUNNEL_LOG.is_file() else "",
        }

    return {
        "ok": True,
        "backend": "cloudflared_tunnel",
        "base_url": base_url.rstrip("/"),
        "ephemeral": True,
        "note": "Quick tunnel — URL changes on restart; use Pages for durable hosting",
    }


def _update_proof_urls(*, base_url: str, evidence_ids: list[str], primary_id: str | None) -> dict[str, str]:
    base = base_url.rstrip("/")
    urls: dict[str, str] = {}
    for eid in evidence_ids:
        url = f"{base}/{eid}/"
        urls[eid] = url
        manifest_path = AEG_ROOT / eid / "manifest.json"
        if manifest_path.is_file():
            manifest = _read_json(manifest_path)
            manifest["proof_url"] = url
            manifest["hosted_at"] = _now()
            manifest["host_base_url"] = base
            _write_json(manifest_path, manifest)
        archive = ROOT / "archive" / "attachments" / "evidence" / "aeg" / eid / "manifest.json"
        if archive.is_file():
            manifest = _read_json(archive)
            manifest["proof_url"] = url
            manifest["hosted_at"] = _now()
            manifest["host_base_url"] = base
            _write_json(archive, manifest)

    cfg = _read_json(AEG_CONFIG)
    cfg["base_url"] = base
    cfg["hosted_at"] = _now()
    _write_json(AEG_CONFIG, cfg)

    target = primary_id or (evidence_ids[-1] if evidence_ids else "")
    if target and AEG_LATEST.is_file():
        latest = _read_json(AEG_LATEST)
        if latest.get("evidence_id") == target or not primary_id:
            latest["proof_url"] = urls.get(target, f"{base}/{target}/")
            latest["host_base_url"] = base
            latest["hosted_at"] = _now()
            _write_json(AEG_LATEST, latest)

    return urls


def host_bundle(
    *,
    evidence_id: str | None = None,
    backend: str = "auto",
    project: str = DEFAULT_PROJECT,
) -> dict[str, Any]:
    staging, ids = stage_bundles(evidence_id=evidence_id)
    primary = evidence_id or ids[-1]

    deploy_result: dict[str, Any] | None = None
    if backend in ("auto", "pages"):
        deploy_result = deploy_pages(staging, project=project)
        if not deploy_result.get("ok") and backend == "pages":
            return {"ok": False, "stage": "deploy", **deploy_result}

    if not deploy_result or not deploy_result.get("ok"):
        if backend in ("auto", "tunnel"):
            deploy_result = deploy_tunnel(staging)
        if not deploy_result or not deploy_result.get("ok"):
            return {
                "ok": False,
                "error": "all hosting backends failed",
                "pages_error": deploy_result.get("error") if deploy_result else None,
                "staging": str(staging),
                "bundles": ids,
            }

    base_url = str(deploy_result["base_url"])
    urls = _update_proof_urls(base_url=base_url, evidence_ids=ids, primary_id=primary)
    proof_url = urls.get(primary, f"{base_url}/{primary}/")

    receipt = {
        "schema": "aeg-host-receipt-v1",
        "at": _now(),
        "ok": True,
        "backend": deploy_result.get("backend"),
        "base_url": base_url,
        "proof_url": proof_url,
        "evidence_id": primary,
        "bundles_hosted": ids,
        "staging": str(staging),
        "ephemeral": bool(deploy_result.get("ephemeral")),
    }
    _write_json(HOST_RECEIPT, receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Host AEG bundles — Pages or cloudflared tunnel")
    ap.add_argument("--evidence-id", help="Single bundle id (default: all bundles staged, latest primary)")
    ap.add_argument("--backend", choices=["auto", "pages", "tunnel"], default="auto")
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    receipt = host_bundle(
        evidence_id=args.evidence_id,
        backend=args.backend,
        project=args.project,
    )
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        if receipt.get("ok"):
            print(f"OK: AEG hosted · backend={receipt.get('backend')}")
            print(f"PROOF_URL={receipt.get('proof_url')}")
            print(f"BASE_URL={receipt.get('base_url')}")
            if receipt.get("ephemeral"):
                print("NOTE: ephemeral tunnel — restart host_aeg_bundle_v1.py after reboot")
        else:
            print(f"FAIL: {receipt.get('error')}", file=sys.stderr)
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
