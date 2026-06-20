#!/usr/bin/env python3
"""Automated Evidence Generation (AEG) — BLOCK → forensic proof bundle.

Capture: terminal (asciinema .cast or transcript) + UI (Playwright png/webm).
Compile: evidence_report.md + self-contained index.html proof page.
Deliver: ~/.sina/aeg/{id}/ + archive copy · proof_url in receipt.

Law: subordinate to critic_boot_v1.py — evidence on BLOCK only unless --force.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
AEG_ROOT = SINA / "aeg"
AEG_CONFIG = SINA / "aeg-config-v1.json"
AEG_INDEX = SINA / "aeg-index-v1.jsonl"
ARCHIVE = ROOT / "archive" / "attachments" / "evidence" / "aeg"
DEFAULT_UI_URL = os.environ.get("AEG_UI_URL", "http://127.0.0.1:13023/")
DEFAULT_BASE_URL = os.environ.get("AEG_BASE_URL", "")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _evidence_id() -> str:
    return f"aeg-{_slug_ts()}-{uuid.uuid4().hex[:8]}"


def _load_config() -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "ui_url": DEFAULT_UI_URL,
        "base_url": DEFAULT_BASE_URL,
        "ui_capture_seconds": 5,
    }
    if AEG_CONFIG.is_file():
        try:
            cfg.update(json.loads(AEG_CONFIG.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    if os.environ.get("AEG_UI_URL"):
        cfg["ui_url"] = os.environ["AEG_UI_URL"]
    if os.environ.get("AEG_BASE_URL"):
        cfg["base_url"] = os.environ["AEG_BASE_URL"]
    return cfg


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401

        return True
    except ImportError:
        return False


def capture_terminal_receipt(
    bundle: Path,
    boot: dict[str, Any],
    *,
    command: str | None = None,
) -> dict[str, Any]:
    """Honest terminal transcript from boot receipt — no re-exec (avoids AEG recursion)."""
    transcript_path = bundle / "terminal.txt"
    cmd = command or f"python3 {ROOT / 'scripts' / 'critic_boot_v1.py'} --json --no-aeg"
    lines = [
        f"$ {cmd}",
        "",
        f"CRITIC_BOOT {boot.get('verdict')} ok={boot.get('ok')}",
        f"RECEIPT={boot.get('receipt_path', str(SINA / 'critic-boot-v1.json'))}",
        "",
    ]
    for c in boot.get("checks") or []:
        mark = "PASS" if c.get("ok") else "FAIL"
        lines.append(f"  [{mark}] {c.get('name')}: {c.get('reason')}")
    if boot.get("blockers"):
        lines.extend(["", "blockers:"])
        for b in boot["blockers"]:
            lines.append(f"  - {b}")
    lines.append("")
    body = "\n".join(lines)
    transcript_path.write_text(body, encoding="utf-8")
    return {
        "ok": True,
        "mode": "receipt_transcript",
        "path": str(transcript_path),
        "note": "Captured from critic_boot receipt — not a re-run",
    }


def capture_terminal_cast(bundle: Path, *, command: str) -> dict[str, Any]:
    """Record terminal via asciinema, else write plain transcript."""
    cast_path = bundle / "evidence.cast"
    transcript_path = bundle / "terminal.txt"
    if _which("asciinema"):
        try:
            proc = subprocess.run(
                [
                    "asciinema",
                    "rec",
                    "--overwrite",
                    "--stdin",
                    "-c",
                    command,
                    str(cast_path),
                ],
                input=b"\n",
                capture_output=True,
                timeout=120,
                cwd=str(ROOT),
            )
            if proc.returncode == 0 and cast_path.is_file() and cast_path.stat().st_size > 0:
                return {
                    "ok": True,
                    "mode": "asciinema",
                    "path": str(cast_path),
                    "size_bytes": cast_path.stat().st_size,
                }
        except (subprocess.TimeoutExpired, OSError) as exc:
            return {"ok": False, "mode": "asciinema", "error": str(exc)}
    # Fallback: run command and capture stdout/stderr
    try:
        env = {**os.environ, "AEG_CAPTURE": "1", "AEG_ON_BLOCK": "0"}
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=45,
            cwd=str(ROOT),
            env=env,
        )
        body = f"$ {command}\n\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n--- exit ---\n{proc.returncode}\n"
        transcript_path.write_text(body, encoding="utf-8")
        return {
            "ok": True,
            "mode": "transcript",
            "path": str(transcript_path),
            "exit_code": proc.returncode,
            "asciinema_missing": _which("asciinema") is None,
        }
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"ok": False, "mode": "transcript", "error": str(exc)}


def capture_ui(bundle: Path, *, ui_url: str, seconds: int = 5) -> dict[str, Any]:
    """Headless Playwright full-page png + optional short webm."""
    png_path = bundle / "ui.png"
    webm_path = bundle / "ui.webm"
    if not _playwright_available():
        return {"ok": False, "skipped": True, "reason": "playwright not installed"}

    try:
        from playwright.sync_api import sync_playwright  # noqa: WPS433
    except ImportError:
        return {"ok": False, "skipped": True, "reason": "playwright import failed"}

    out: dict[str, Any] = {"ok": False, "ui_url": ui_url}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                record_video_dir=str(bundle),
                record_video_size={"width": 1280, "height": 720},
            )
            page = context.new_page()
            try:
                page.goto(ui_url, wait_until="networkidle", timeout=20000)
            except Exception:
                page.goto(ui_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(min(max(seconds, 1), 15) * 1000)
            page.screenshot(path=str(png_path), full_page=True)
            context.close()
            browser.close()
        out["ok"] = True
        out["png"] = str(png_path) if png_path.is_file() else None
        videos = sorted(bundle.glob("*.webm"))
        if videos:
            videos[-1].rename(webm_path)
            out["webm"] = str(webm_path)
        return out
    except Exception as exc:
        out["error"] = str(exc)
        return out


def _primary_blocker(boot: dict[str, Any]) -> str:
    blockers = boot.get("blockers") or []
    if blockers:
        return str(blockers[0])
    for c in boot.get("checks") or []:
        if not c.get("ok"):
            return str(c.get("reason") or c.get("name") or "BLOCK")
    return "critic_boot BLOCK"


def _checks_table(boot: dict[str, Any]) -> str:
    lines = ["| Check | Status | Reason |", "|---|---|---|"]
    for c in boot.get("checks") or []:
        status = "PASS" if c.get("ok") else "BLOCK"
        lines.append(f"| {c.get('name', '?')} | {status} | {c.get('reason', '')} |")
    return "\n".join(lines)


def compile_report(
    bundle: Path,
    *,
    evidence_id: str,
    boot: dict[str, Any],
    heal_boot: dict[str, Any] | None,
    terminal: dict[str, Any],
    ui: dict[str, Any],
) -> Path:
    ts = boot.get("at") or _now()
    blocker = _primary_blocker(boot)
    md_path = bundle / "evidence_report.md"
    lines = [
        f"# Proof Narrative — System Blocked",
        "",
        f"**Header:** System Blocked: {ts} | Reason: {blocker}",
        "",
        f"**Evidence ID:** `{evidence_id}`",
        "",
        "Forensic bundle — terminal capture, UI state, critic_boot receipt. Buyer-clickable proof link.",
        "",
        "## Critic boot checks",
        "",
        _checks_table(boot),
        "",
        "## Terminal evidence",
        "",
    ]
    if terminal.get("mode") == "asciinema":
        lines.append("- Asciinema cast: `evidence.cast` (embedded in proof page)")
    elif terminal.get("mode") == "receipt_transcript":
        lines.append("- Terminal transcript from boot receipt (honest snapshot, no re-run)")
    elif terminal.get("path"):
        lines.append(f"- Transcript: `{Path(terminal['path']).name}`")
    lines.extend(["", "## UI evidence", ""])
    if ui.get("ok"):
        lines.append(f"- Screenshot: `{Path(ui.get('png', 'ui.png')).name}`")
        if ui.get("webm"):
            lines.append(f"- Recording: `{Path(ui['webm']).name}`")
    else:
        lines.append(f"- UI capture skipped: {ui.get('reason') or ui.get('error') or 'unavailable'}")
    lines.extend(["", "## Verdict (JSON)", "", "```json", json.dumps(boot, indent=2), "```", ""])
    if heal_boot:
        lines.extend(
            [
                "## Heal state (after fix)",
                "",
                f"**Verdict:** {heal_boot.get('verdict')} · {heal_boot.get('founder_line', '')}",
                "",
                _checks_table(heal_boot),
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def compile_proof_page(
    bundle: Path,
    *,
    evidence_id: str,
    boot: dict[str, Any],
    heal_boot: dict[str, Any] | None,
    terminal: dict[str, Any],
    ui: dict[str, Any],
    proof_url: str,
) -> Path:
    html_path = bundle / "index.html"
    blocker = _html_escape(_primary_blocker(boot))
    ts = _html_escape(str(boot.get("at") or _now()))
    cast_embed = ""
    if (bundle / "evidence.cast").is_file():
        cast_embed = """
    <section class="panel">
      <h2>Terminal — critic boot</h2>
      <div id="asciinema-player"></div>
      <script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.6.3/dist/bundle/asciinema-player.min.js"></script>
      <script>
        AsciinemaPlayer.create('evidence.cast', document.getElementById('asciinema-player'), {
          cols: 100, rows: 24, autoPlay: false, preload: true, theme: 'asciinema', fit: 'width'
        });
      </script>
    </section>"""
    elif (bundle / "terminal.txt").is_file():
        txt = _html_escape((bundle / "terminal.txt").read_text(encoding="utf-8", errors="replace"))
        cast_embed = f"""
    <section class="panel">
      <h2>Terminal transcript</h2>
      <pre class="term">{txt}</pre>
    </section>"""

    ui_block = ""
    if (bundle / "ui.png").is_file():
        ui_block = """
    <section class="panel">
      <h2>UI state (Chat Unify :13023)</h2>
      <img src="ui.png" alt="UI capture at BLOCK" class="shot" />"""
        if (bundle / "ui.webm").is_file():
            ui_block += """
      <video src="ui.webm" controls playsinline class="vid"></video>"""
        ui_block += "\n    </section>"

    heal_block = ""
    if heal_boot:
        broken_checks = _html_escape(_checks_table(boot))
        heal_checks = _html_escape(_checks_table(heal_boot))
        heal_block = f"""
    <section class="panel compare">
      <h2>Broken vs Heal</h2>
      <div class="compare-grid">
        <div class="compare-col broken">
          <h3>Blocked state</h3>
          <p><strong>{_html_escape(str(boot.get('verdict')))}</strong> — {blocker}</p>
          <pre class="md">{broken_checks}</pre>
        </div>
        <div class="compare-col heal">
          <h3>Governed state (after fix)</h3>
          <p><strong>{_html_escape(str(heal_boot.get('verdict')))}</strong> — {_html_escape(str(heal_boot.get('founder_line', '')))}</p>
          <pre class="md">{heal_checks}</pre>
        </div>
      </div>
      <details class="json-details">
        <summary>Full heal receipt JSON</summary>
        <pre class="json">{_html_escape(json.dumps(heal_boot, indent=2))}</pre>
      </details>
    </section>"""

    receipt_json = _html_escape(json.dumps(boot, indent=2))
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AEG Proof — {evidence_id}</title>
  <style>
    :root {{ font-family: Inter, system-ui, sans-serif; background: #0b1220; color: #e2e8f0; }}
    body {{ margin: 0; padding: 1.5rem; max-width: 960px; margin-inline: auto; }}
    h1 {{ font-size: 1.35rem; margin: 0 0 0.25rem; }}
    .meta {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem; }}
    .panel {{ background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem; }}
    .panel h2 {{ margin: 0 0 0.75rem; font-size: 1rem; color: #2dd4bf; }}
    pre.term, pre.json {{ overflow-x: auto; font-size: 0.78rem; background: #060a0f; padding: 1rem; border-radius: 8px; }}
    .shot {{ max-width: 100%; border-radius: 8px; border: 1px solid #334155; }}
    .vid {{ width: 100%; margin-top: 0.75rem; border-radius: 8px; }}
    .heal {{ border-color: #065f46; }}
    .compare-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .compare-col {{ padding: 0.75rem; border-radius: 8px; border: 1px solid #334155; }}
    .compare-col.broken {{ border-color: #7f1d1d; background: rgba(127,29,29,0.15); }}
    .compare-col.heal {{ border-color: #065f46; background: rgba(6,95,70,0.12); }}
    .compare-col h3 {{ margin: 0 0 0.5rem; font-size: 0.85rem; }}
    pre.md {{ font-size: 0.72rem; white-space: pre-wrap; background: transparent; padding: 0; }}
    .json-details summary {{ cursor: pointer; color: #94a3b8; font-size: 0.82rem; margin-top: 0.75rem; }}
    @media (max-width: 720px) {{ .compare-grid {{ grid-template-columns: 1fr; }} }}
    footer {{ color: #64748b; font-size: 0.78rem; margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>System Blocked — forensic evidence</h1>
  <p class="meta">{ts} · {blocker} · <code>{evidence_id}</code></p>
  {cast_embed}
  {ui_block}
  <section class="panel">
    <h2>Critic boot receipt</h2>
    <pre class="json">{receipt_json}</pre>
  </section>
  {heal_block}
  <footer>Automated Evidence Generation (AEG) · SourceA critic_boot · proof URL: {_html_escape(proof_url)}</footer>
</body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")
    return html_path


def _proof_url(evidence_id: str, bundle: Path, cfg: dict[str, Any]) -> str:
    base = (cfg.get("base_url") or "").rstrip("/")
    if base:
        return f"{base}/{evidence_id}/"
    return bundle / "index.html"


def publish_bundle(bundle: Path, manifest: dict[str, Any]) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    archive_bundle = ARCHIVE / bundle.name
    if archive_bundle.exists():
        shutil.rmtree(archive_bundle)
    shutil.copytree(bundle, archive_bundle)
    AEG_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with AEG_INDEX.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "at": manifest.get("at"),
                    "evidence_id": manifest.get("evidence_id"),
                    "verdict": manifest.get("verdict"),
                    "proof_url": manifest.get("proof_url"),
                    "bundle": str(bundle),
                }
            )
            + "\n"
        )


def emit_block_evidence(
    boot: dict[str, Any],
    *,
    heal_boot: dict[str, Any] | None = None,
    terminal_command: str | None = None,
    skip_ui: bool = False,
) -> dict[str, Any]:
    """Build full AEG bundle from a critic_boot BLOCK row."""
    cfg = _load_config()
    evidence_id = _evidence_id()
    bundle = AEG_ROOT / evidence_id
    bundle.mkdir(parents=True, exist_ok=True)

    (bundle / "critic_boot_receipt.json").write_text(json.dumps(boot, indent=2) + "\n", encoding="utf-8")
    if heal_boot:
        (bundle / "heal_boot_receipt.json").write_text(json.dumps(heal_boot, indent=2) + "\n", encoding="utf-8")

    cmd = terminal_command or f"python3 {ROOT / 'scripts' / 'critic_boot_v1.py'} --json --no-aeg"
    if os.environ.get("AEG_ASCIINEMA_RERUN") == "1" and _which("asciinema"):
        terminal = capture_terminal_cast(bundle, command=cmd)
        if not terminal.get("ok"):
            terminal = capture_terminal_receipt(bundle, boot, command=cmd)
    else:
        terminal = capture_terminal_receipt(bundle, boot, command=cmd)
    ui: dict[str, Any] = {"ok": False, "skipped": True}
    if not skip_ui:
        ui = capture_ui(bundle, ui_url=str(cfg.get("ui_url", DEFAULT_UI_URL)), seconds=int(cfg.get("ui_capture_seconds", 5)))

    compile_report(
        bundle,
        evidence_id=evidence_id,
        boot=boot,
        heal_boot=heal_boot,
        terminal=terminal,
        ui=ui,
    )
    proof_url = str(_proof_url(evidence_id, bundle, cfg))
    compile_proof_page(
        bundle,
        evidence_id=evidence_id,
        boot=boot,
        heal_boot=heal_boot,
        terminal=terminal,
        ui=ui,
        proof_url=proof_url,
    )

    manifest = {
        "schema": "aeg-evidence-bundle-v1",
        "evidence_id": evidence_id,
        "at": boot.get("at") or _now(),
        "verdict": boot.get("verdict"),
        "blockers": boot.get("blockers"),
        "proof_url": proof_url,
        "bundle_dir": str(bundle),
        "archive_dir": str(ARCHIVE / evidence_id),
        "terminal": terminal,
        "ui": ui,
        "heal_verdict": (heal_boot or {}).get("verdict"),
    }
    publish_bundle(bundle, manifest)
    receipt = SINA / "aeg-latest-receipt-v1.json"
    receipt.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description="AEG — Automated Evidence Generation")
    ap.add_argument("--from-boot-receipt", type=Path, help="Path to critic-boot-v1.json")
    ap.add_argument("--heal-receipt", type=Path, help="Optional heal PASS receipt JSON")
    ap.add_argument("--skip-ui", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    boot_path = args.from_boot_receipt or (SINA / "critic-boot-v1.json")
    if not boot_path.is_file():
        print(f"FAIL: boot receipt missing: {boot_path}", file=sys.stderr)
        return 1
    boot = json.loads(boot_path.read_text(encoding="utf-8"))
    if boot.get("verdict") != "BLOCK" and boot.get("ok"):
        print("SKIP: boot verdict is PASS — AEG runs on BLOCK only (use critic_boot --aeg after BLOCK)", file=sys.stderr)
        return 0

    heal_boot = None
    if args.heal_receipt and args.heal_receipt.is_file():
        heal_boot = json.loads(args.heal_receipt.read_text(encoding="utf-8"))

    manifest = emit_block_evidence(boot, heal_boot=heal_boot, skip_ui=args.skip_ui)
    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"AEG OK evidence_id={manifest['evidence_id']}")
        print(f"PROOF_URL={manifest['proof_url']}")
        print(f"BUNDLE={manifest['bundle_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
