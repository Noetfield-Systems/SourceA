#!/usr/bin/env python3
"""Inject live sourcea-boot --json output into green-unified terminal blocks."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "sourcea-boot-terminal-inject-v1.json"
BOOT_PKG = ROOT / "packages" / "sourcea-boot" / "src"
PUBLIC_REPORT = "receipts/sourcea-boot/BOOT_REPORT.json"

MARKER_START = "<!-- sa-boot-terminal:v1 -->"
MARKER_END = "<!-- /sa-boot-terminal:v1 -->"

TARGETS = [
    LANDING / "index.html",
    LANDING / "proof.html",
    LANDING / "eval.html",
    LANDING / "attach" / "agency-onepager.html",
    LANDING / "attach" / "procurement-pack.html",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_boot_json() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{BOOT_PKG}:{env.get('PYTHONPATH', '')}"
    proc = subprocess.run(
        [sys.executable, "-m", "sourcea_boot.cli", "--json", "--no-write"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    if not proc.stdout.strip():
        raise RuntimeError(proc.stderr or "sourcea-boot produced no output")
    return json.loads(proc.stdout)


def _public_report_path(report_file: str | None) -> str:
    raw = str(report_file or "").strip()
    if not raw or "/Users/" in raw or "Desktop/SourceA" in raw or "sinakazemnezhad" in raw:
        return PUBLIC_REPORT
    if raw.startswith("receipts/"):
        return raw
    name = Path(raw).name or "BOOT_REPORT.json"
    if name == "BOOT_REPORT.json":
        return PUBLIC_REPORT
    return f"receipts/sourcea-boot/{name}"


def _check_class(c: dict) -> str:
    if c.get("skipped"):
        return "sa-t-warn"
    return "sa-t-ok" if c.get("ok") else "sa-t-bad"


def _check_mark(c: dict) -> str:
    if c.get("skipped"):
        return "SKIP"
    return "PASS" if c.get("ok") else "FAIL"


def format_html_pre(row: dict) -> str:
    ok = bool(row.get("ok"))
    verdict = str(row.get("verdict") or ("PASS" if ok else "BLOCK"))
    verdict_cls = "sa-t-ok" if verdict == "PASS" else "sa-t-bad"
    lines = [
        f'<span class="sa-t-prompt">$</span> sourcea-boot --json',
        f'<span class="{verdict_cls}">SOURCEA_BOOT {escape(verdict)}</span> '
        f'<span class="sa-t-dim">ok={str(ok).lower()}</span>',
    ]
    for c in row.get("checks") or []:
        mark = _check_mark(c)
        name = escape(str(c.get("name") or c.get("id") or "check"))
        reason = escape(str(c.get("reason") or "").replace("— skipped", "(not configured)"))
        lines.append(
            f'  <span class="{_check_class(c)}">[{mark}]</span> {name}: {reason}'
        )
    report = escape(_public_report_path(str(row.get("report_file") or "")))
    lines.append(f'<span class="sa-t-dim">REPORT={report}</span><span class="sa-t-cursor">▋</span>')
    return "\n".join(lines)


def format_plain(row: dict) -> str:
    ok = bool(row.get("ok"))
    verdict = str(row.get("verdict") or ("PASS" if ok else "BLOCK"))
    lines = [
        "$ sourcea-boot --json",
        f"SOURCEA_BOOT {verdict} ok={str(ok).lower()}",
    ]
    for c in row.get("checks") or []:
        mark = _check_mark(c)
        name = str(c.get("name") or c.get("id") or "check")
        reason = str(c.get("reason") or "")
        lines.append(f"  [{mark}] {name}: {reason}")
    lines.append(f"REPORT={_public_report_path(str(row.get('report_file') or ''))}")
    return "\n".join(lines)


def format_label(row: dict) -> str:
    at = str(row.get("at") or _now())[:19].replace("T", " ")
    verdict = str(row.get("verdict") or "BLOCK")
    return f"Last factory boot · {at} UTC · {verdict}"


def inject_file(path: Path, *, html_pre: str, plain: str, label: str) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text

    if MARKER_START in text and MARKER_END in text:
        pattern = re.compile(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            re.DOTALL,
        )
        if 'class="proof"' in text or path.name == "agency-onepager.html":
            block = (
                f'{MARKER_START}\n'
                f'  <p class="sa-boot-terminal-label">{escape(label)}</p>\n'
                f'  <div class="proof">{plain}</div>\n'
                f'{MARKER_END}'
            )
        else:
            block = (
                f'{MARKER_START}\n'
                f'        <p class="sa-boot-terminal-label">{escape(label)}</p>\n'
                f'        <pre class="sa-terminal-body" id="sa-terminal-replay">{html_pre}</pre>\n'
                f'{MARKER_END}'
            )
        text = pattern.sub(block, text, count=1)
    elif 'class="sa-terminal-body"' in text:
        text = re.sub(
            r'(<pre class="sa-terminal-body"[^>]*>)(.*?)(</pre>)',
            lambda m: f'{m.group(1)}{html_pre}{m.group(3)}',
            text,
            count=1,
            flags=re.DOTALL,
        )
        if "sa-boot-terminal-label" not in text:
            text = text.replace(
                '<span>replay · sourcea-boot</span></div>',
                f'<span>replay · sourcea-boot</span></div>\n'
                f'        <p class="sa-boot-terminal-label">{escape(label)}</p>',
                1,
            )
        else:
            text = re.sub(
                r'(<p class="sa-boot-terminal-label">)(.*?)(</p>)',
                lambda m: f"{m.group(1)}{escape(label)}{m.group(3)}",
                text,
                count=1,
                flags=re.DOTALL,
            )
    elif 'class="proof"' in text:
        text = re.sub(
            r'(<div class="proof">)(.*?)(</div>)',
            lambda m: f'{m.group(1)}{plain}{m.group(3)}',
            text,
            count=1,
            flags=re.DOTALL,
        )

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def build_factory_live(boot_row: dict) -> dict:
    """Disk truth for live command center — SourceA account only."""
    live: dict = {
        "schema": "sourcea-factory-live-v1",
        "at": _now(),
        "account": "sourcea",
        "console_url": "command.sourcea.com/team",
    }
    surf_path = SINA / "agent-live-surfaces-v1.json"
    if surf_path.is_file():
        try:
            surf = json.loads(surf_path.read_text(encoding="utf-8"))
            live["factory_now_line"] = str(surf.get("factory_now_line") or "")
            live["queue_sa"] = str(surf.get("queue_sa") or "")
            live["mode"] = str(surf.get("mode") or "")
        except (OSError, json.JSONDecodeError):
            pass
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "commercial_pipeline_v1.py"), "--glance", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.stdout.strip().startswith("{"):
            live["pipeline"] = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        live["pipeline"] = {}
    checks = boot_row.get("checks") or []
    live["boot"] = {
        "verdict": boot_row.get("verdict"),
        "ok": boot_row.get("ok"),
        "checks": checks,
        "pass_count": sum(1 for c in checks if c.get("ok")),
        "block_count": sum(1 for c in checks if not c.get("ok")),
    }
    counts = (live.get("pipeline") or {}).get("counts") or {}
    live["metrics"] = {
        "active": int((live.get("pipeline") or {}).get("active_conversations") or 0),
        "proof_viewed": int(counts.get("proof_viewed") or 0),
        "eval_scheduled": int(counts.get("eval_scheduled") or 0),
        "sent": int(counts.get("personalized_sent") or 0),
    }
    aeg_path = LANDING / "data" / "aeg-live.json"
    if aeg_path.is_file():
        try:
            live["aeg"] = json.loads(aeg_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            live["aeg"] = {}
    trust_path = LANDING / "data" / "trust-signals.json"
    if trust_path.is_file():
        try:
            trust = json.loads(trust_path.read_text(encoding="utf-8"))
            live["valid_yes"] = trust.get("valid_yes")
            live["valid_yes_total"] = trust.get("valid_yes_total") or 1000
        except (OSError, json.JSONDecodeError):
            pass
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from commercial_recipient_guard_v1 import resolve_aeg_proof_url  # noqa: WPS433

        aeg_url = resolve_aeg_proof_url()
        live["aeg_live_url"] = aeg_url
        pipe = live.get("pipeline") or {}
        for row in pipe.get("top_next") or []:
            if row.get("id") == "cp-a0c7c6c607" or row.get("founder_pick"):
                row["proof_url"] = aeg_url
                row["proof_label"] = "Live forensic proof"
        live["pipeline"] = pipe
    except (ImportError, SystemExit, OSError):
        pass
    return live


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject live sourcea-boot terminal into landing HTML")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    row = run_boot_json()
    row["injected_at"] = _now()
    html_pre = format_html_pre(row)
    plain = format_plain(row)
    label = format_label(row)

    changed: list[str] = []
    for path in TARGETS:
        if not path.is_file():
            continue
        if args.dry_run:
            changed.append(str(path.relative_to(ROOT)))
            continue
        if inject_file(path, html_pre=html_pre, plain=plain, label=label):
            changed.append(str(path.relative_to(ROOT)))

    receipt = {
        "schema": "sourcea-boot-terminal-inject-v1",
        "at": _now(),
        "verdict": row.get("verdict"),
        "ok": row.get("ok"),
        "checks": [c.get("name") for c in (row.get("checks") or [])],
        "label": label,
        "files": changed,
    }
    if not args.dry_run:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        data_dir = LANDING / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        proof = {
            "schema": "sourcea-boot-proof-v1",
            "at": row.get("injected_at"),
            "verdict": row.get("verdict"),
            "ok": row.get("ok"),
            "checks": row.get("checks") or [],
            "founder_line": f"Factory boot {row.get('verdict')} — four checks on disk",
        }
        (data_dir / "boot-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
        factory_live = build_factory_live(row)
        (data_dir / "factory-live.json").write_text(json.dumps(factory_live, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: inject_sourcea_boot_terminal_v1 · {row.get('verdict')} · {len(changed)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
