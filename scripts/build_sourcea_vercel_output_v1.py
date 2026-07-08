#!/usr/bin/env python3
"""Build static output for SourceA Vercel deploy (source-a project).

Assembles green-unified under /sourcea/ plus vendored /assets/ for Gate K.
Law: SourceA-landing/green-unified · vercel-static/assets
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GREEN = ROOT / "SourceA-landing" / "green-unified"
DIST = GREEN / "dist"
VENDORED_ASSETS = ROOT / "SourceA-landing" / "vercel-static" / "assets"
DESKTOP_ASSETS = Path.home() / "Desktop" / "agentrun-app" / "assets"

ALLOW_SUFFIX = {".html", ".css", ".js", ".svg", ".json", ".mp4", ".webp", ".png", ".jpg", ".dmg"}
PROOF_PACK_NAME = "phase1-proof-pack-public-v1.json"
PROOF_PACK_SCHEMA = "sourcea-phase1-proof-pack-public-v1"
BRAIN_CHAT_CONFIG = "sourcea-brain-chat-config-v1.json"
BRAIN_CHAT_CONFIG_SCHEMA = "sourcea-brain-chat-config-v1"


def _copy_tree(src: Path, dest: Path) -> int:
    n = 0
    skip_dirs = {"dist", ".vercel", "__pycache__", "node_modules"}
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        if f.name == "vercel.json":
            continue
        if any(part in skip_dirs for part in f.relative_to(src).parts):
            continue
        if f.suffix.lower() not in ALLOW_SUFFIX and f.name not in ("favicon.svg",):
            continue
        rel = f.relative_to(src)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        n += 1
    return n


def _sync_assets(dest_assets: Path) -> None:
    dest_assets.mkdir(parents=True, exist_ok=True)
    src = VENDORED_ASSETS if VENDORED_ASSETS.is_dir() else DESKTOP_ASSETS
    if not src.is_dir():
        raise SystemExit(f"FAIL: no assets source — need {VENDORED_ASSETS} or {DESKTOP_ASSETS}")
    for name in ("agentrun.css", "agentrun.js", "favicon.svg"):
        f = src / name
        if not f.is_file():
            raise SystemExit(f"FAIL: missing asset {f}")
        shutil.copy2(f, dest_assets / name)


def build(*, clean: bool = True) -> dict:
    if not GREEN.is_dir():
        raise SystemExit(f"FAIL: green-unified missing: {GREEN}")

    sync_auth = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "sync_sourcea_platform_auth_public_v1.py")],
        cwd=ROOT,
        timeout=30,
        capture_output=True,
        text=True,
    )
    if sync_auth.returncode != 0:
        raise SystemExit(f"FAIL: platform auth sync — {(sync_auth.stderr or sync_auth.stdout or '')[-400:]}")

    if clean and DIST.is_dir():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    sourcea_dir = DIST / "sourcea"
    page_count = _copy_tree(GREEN, sourcea_dir)
    _sync_assets(DIST / "assets")

    downloads_src = GREEN / "downloads"
    if downloads_src.is_dir():
        dl_dest = DIST / "downloads"
        dl_dest.mkdir(parents=True, exist_ok=True)
        for f in downloads_src.iterdir():
            if f.is_file():
                shutil.copy2(f, dl_dest / f.name)

    for web_app in ("unify", "unify-demo"):
        src = GREEN / web_app
        if src.is_dir():
            dest = DIST / web_app
            if dest.is_dir():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)

    start_src = sourcea_dir / "start.html"
    founder_src = GREEN / "founder-home.html"
    eval_src = GREEN / "eval.html"
    platform_src = GREEN / "platform-portal.html"
    root_index = DIST / "index.html"
    if founder_src.is_file():
        shutil.copy2(founder_src, root_index)
    elif start_src.is_file():
        shutil.copy2(start_src, root_index)
    else:
        raise SystemExit(f"FAIL: root founder-home missing: {founder_src}")
    if platform_src.is_file():
        shutil.copy2(platform_src, DIST / "platform.html")
    auth_src = GREEN / "auth"
    if auth_src.is_dir():
        auth_dest = DIST / "auth"
        auth_dest.mkdir(parents=True, exist_ok=True)
        for f in auth_src.glob("*.html"):
            shutil.copy2(f, auth_dest / f.name)
    if eval_src.is_file():
        shutil.copy2(eval_src, DIST / "eval.html")

    sys.path.insert(0, str(ROOT / "scripts"))
    from sourcea_clean_urls_v1 import write_redirects  # noqa: WPS433

    redirect_lines = write_redirects(DIST)

    headers_src = GREEN / "_headers"
    if headers_src.is_file():
        shutil.copy2(headers_src, DIST / "_headers")

    pulse_snippet = '<script src="/sourcea/sourcea-site-pulse-v1.js" defer></script>\n'
    interact_snippet = '<script src="/sourcea/sourcea-site-interact-v1.js" defer></script>\n'
    segment_snippet = '<script src="/sourcea/sourcea-segment-router-v1.js" defer></script>\n'
    auth_nav_snippet = '<script src="/sourcea/sourcea-auth-nav-wire-v1.js" defer></script>\n'
    shell_snippet = pulse_snippet + interact_snippet + segment_snippet + auth_nav_snippet

    def inject_shell(text: str) -> str:
        if "sourcea-site-interact-v1.js" in text and "sourcea-segment-router-v1.js" in text:
            return text
        if "sourcea-site-interact-v1.js" in text and "sourcea-segment-router-v1.js" not in text:
            text = text.replace(
                '<script src="/sourcea/sourcea-site-interact-v1.js" defer></script>\n',
                '<script src="/sourcea/sourcea-site-interact-v1.js" defer></script>\n'
                + segment_snippet,
                1,
            )
            return text
        anchor = '<script src="/sourcea/sourcea-chatbot.js"'
        if anchor in text:
            return text.replace(anchor, shell_snippet + anchor, 1)
        if "</body>" in text:
            return text.replace("</body>", shell_snippet + "</body>", 1)
        return text

    pulse_injected = 0
    for html_path in sourcea_dir.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        new_text = inject_shell(text)
        if new_text != text:
            html_path.write_text(new_text, encoding="utf-8")
            pulse_injected += 1
    if (DIST / "index.html").is_file():
        text = (DIST / "index.html").read_text(encoding="utf-8")
        new_text = inject_shell(text)
        if new_text != text:
            (DIST / "index.html").write_text(new_text, encoding="utf-8")

    proof_pack = sourcea_dir / "data" / PROOF_PACK_NAME
    if not proof_pack.is_file():
        raise SystemExit(f"FAIL: site truth gate — {PROOF_PACK_NAME} missing in dist")
    try:
        proof_row = json.loads(proof_pack.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: site truth gate — {PROOF_PACK_NAME} invalid JSON: {exc}") from exc
    if proof_row.get("schema") != PROOF_PACK_SCHEMA:
        raise SystemExit(
            f"FAIL: site truth gate — {PROOF_PACK_NAME} schema "
            f"{proof_row.get('schema')!r} != {PROOF_PACK_SCHEMA!r}"
        )

    brain_cfg = sourcea_dir / "data" / BRAIN_CHAT_CONFIG
    if not brain_cfg.is_file():
        raise SystemExit(f"FAIL: brain chat gate — {BRAIN_CHAT_CONFIG} missing in dist")
    try:
        brain_row = json.loads(brain_cfg.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: brain chat gate — {BRAIN_CHAT_CONFIG} invalid JSON: {exc}") from exc
    if brain_row.get("schema") != BRAIN_CHAT_CONFIG_SCHEMA:
        raise SystemExit(
            f"FAIL: brain chat gate — {BRAIN_CHAT_CONFIG} schema "
            f"{brain_row.get('schema')!r} != {BRAIN_CHAT_CONFIG_SCHEMA!r}"
        )
    if not brain_row.get("api_worker_url"):
        raise SystemExit(f"FAIL: brain chat gate — {BRAIN_CHAT_CONFIG} missing api_worker_url")

    return {
        "ok": True,
        "dist": str(DIST.relative_to(ROOT)),
        "page_count": page_count,
        "clean_url_rules": len(redirect_lines),
        "truth_gate": {
            "proof_pack": str(proof_pack.relative_to(ROOT)),
            "pack_id": proof_row.get("pack_id"),
            "verdict": proof_row.get("verdict"),
            "truth_gate_score": proof_row.get("truth_gate_score"),
        },
        "urls": {
            "root": "/",
            "founder_home": "/",
            "mvp_canonical": "/start",
            "mvp_hub_preserved": "/sourcea/48h-mvp",
            "mvp_retired_redirect": "/mvp → 301 /start",
            "kernel": "/sourcea/",
            "full_site": "/sourcea/",
            "trust": "/sourcea/trust/",
            "proof_bundle_sample": "/sourcea/attach/proof-bundle-sample",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Build SourceA Vercel static dist")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = build()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: {row['dist']} pages={row['page_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
