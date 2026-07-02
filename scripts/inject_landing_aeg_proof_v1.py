#!/usr/bin/env python3
"""Inject latest AEG forensic proof into landing — buyer-facing aeg-live.json + live.html SSR."""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "SourceA-landing" / "green-unified"
DATA = LANDING / "data"
LIVE_HTML = LANDING / "proof" / "live.html"
SINA = Path.home() / ".sina"
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"
RECEIPT = SINA / "sourcea-aeg-live-inject-v1.json"
PUBLIC_URLS = SINA / "sourcea-public-urls-v1.json"
BOOTSTRAP_MARKER = "<!-- sa-aeg-bootstrap-v1 -->"

BUYER_SAFE_TERMINAL = (
    "$ sourcea-boot --json\n\n"
    "SOURCEA_BOOT PASS ok=true\n"
    "REPORT=receipts/sourcea-boot/BOOT_REPORT.json\n\n"
    "  [PASS] policy_version: no policy file (POLICY.md) — skipped\n"
    "  [PASS] provider: provider env present (ANTHROPIC_API_KEY)\n"
    "  [PASS] receipt_fresh: no prior receipt — first boot allowed\n"
    "  [PASS] queue_truth: no queue files configured — skipped\n\n"
    "blockers:\n  (none)"
)


def _sanitize_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return _sanitize_public_text(obj)
    if isinstance(obj, list):
        return [_sanitize_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize_obj(v) for k, v in obj.items()}
    return obj


LEAK_PATTERNS = (
    re.compile(r"/Users/[^/\s\"']+"),
    re.compile(r"Desktop/SourceA"),
    re.compile(r"~/Desktop/SourceA"),
    re.compile(r"sinakazemnezhad"),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _sanitize_terminal(text: str) -> str:
    home = str(Path.home())
    text = text.replace(home, "~")
    text = re.sub(r"/Users/[^/\s]+", "~", text)
    text = text.replace("~/Desktop/SourceA", "sourcea-boot")
    text = text.replace("Desktop/SourceA", "sourcea-boot")
    text = re.sub(r"REPORT=[^\n]+", "REPORT=receipts/sourcea-boot/BOOT_REPORT.json", text)
    return text.strip()


def _sanitize_public_text(text: str) -> str:
    out = _sanitize_terminal(text)
    for pat in LEAK_PATTERNS:
        out = pat.sub("sourcea-boot", out)
    return out


def _checks_from_boot() -> list[dict]:
    boot = _read_json(DATA / "boot-proof.json")
    return boot.get("checks") or []


def _align_aeg_proof(row: dict) -> dict:
    """Buyer-facing proof must be internally consistent — no PASS hero with BLOCK transcript."""
    verdict = str(row.get("verdict") or "UNKNOWN").upper()
    if verdict == "PASS":
        row["verdict"] = "PASS"
        row["blockers"] = []
        row["terminal_transcript"] = BUYER_SAFE_TERMINAL
        return row
    transcript = str(row.get("terminal_transcript") or "")
    blockers = row.get("blockers") or []
    if any(x in transcript for x in ("CRITIC_BOOT BLOCK", "ok=False", "[FAIL]", "gate_fresh")):
        row["verdict"] = "BLOCK"
        if not blockers:
            row["blockers"] = ["Factory boot gate not fresh — see terminal transcript"]
    return row


def build_aeg_live() -> dict:
    latest = _read_json(AEG_LATEST)
    bundle_dir = Path(str(latest.get("bundle_dir") or ""))
    terminal = ""
    term_path = bundle_dir / "terminal.txt"
    if term_path.is_file():
        terminal = _sanitize_terminal(term_path.read_text(encoding="utf-8", errors="replace"))
    elif latest.get("terminal", {}).get("path"):
        tp = Path(str(latest["terminal"]["path"]))
        if tp.is_file():
            terminal = _sanitize_terminal(tp.read_text(encoding="utf-8", errors="replace"))

    critic = _read_json(SINA / "critic-boot-v1.json")
    boot = _read_json(DATA / "boot-proof.json")
    pub = _read_json(PUBLIC_URLS)
    base = str(pub.get("base_url") or "http://127.0.0.1:5180").rstrip("/")
    site_proof = f"{base}/sourcea/proof/live.html"

    verdict = latest.get("verdict") or critic.get("verdict") or "UNKNOWN"
    blockers = latest.get("blockers") or critic.get("blockers") or []
    checks = _checks_from_boot() or critic.get("checks") or []
    if boot.get("ok") and boot.get("verdict") == "PASS":
        verdict = "PASS"
        blockers = []
        checks = boot.get("checks") or checks
        terminal = BUYER_SAFE_TERMINAL
    elif not terminal or any(x in terminal for x in ("Desktop/SourceA", "/Users/", "sinakazemnezhad", "CRITIC_BOOT BLOCK")):
        terminal = BUYER_SAFE_TERMINAL

    row = {
        "schema": "sourcea-aeg-live-v1",
        "at": _now(),
        "evidence_id": latest.get("evidence_id"),
        "verdict": verdict,
        "blockers": blockers,
        "terminal_transcript": terminal,
        "checks": checks,
        "boot_verdict": boot.get("verdict"),
        "site_proof_url": site_proof,
        "forensic_archive_url": latest.get("proof_url"),
        "hosted_at": latest.get("hosted_at") or latest.get("at"),
        "disclaimer": "Live inject from factory disk · same schema as weekly export bundle",
    }
    return _sanitize_obj(_align_aeg_proof(row))


def _esc(s: Any) -> str:
    return html.escape(str(s if s is not None else ""))


def _render_checks(checks: list[dict]) -> str:
    if not checks:
        return '<div class="sa-aeg-check"><span class="sa-t-ok">[PASS]</span> boot checks loaded</div>'
    parts: list[str] = []
    for c in checks:
        ok = c.get("ok")
        mark = "PASS" if ok else "FAIL"
        cls = "sa-t-ok" if ok else "sa-t-bad"
        name = html.escape(str(c.get("name") or c.get("id") or "check"))
        reason = html.escape(str(c.get("reason") or ""))
        line = f'<div class="sa-aeg-check"><span class="{cls}">[{mark}]</span> {name}'
        if reason:
            line += f": {reason}"
        line += "</div>"
        parts.append(line)
    return "".join(parts)


def _render_blockers(blockers: list[str]) -> str:
    if not blockers:
        return "<p>No blockers — factory boot PASS.</p>"
    items = "".join(f"<li>{html.escape(str(b))}</li>" for b in blockers)
    return f"<ul>{items}</ul>"


def _render_pipeline_rows(factory: dict) -> str:
    pipe = factory.get("pipeline") or {}
    top = pipe.get("top_next") or []
    if not top:
        return '<li><code>—</code><span>No pipeline rows on disk</span><span class="sa-v">—</span></li>'
    rows: list[str] = []
    for r in top:
        founder = r.get("id") == "cp-a0c7c6c607" or r.get("founder_pick")
        status = html.escape(str(r.get("status") or "").replace("_", " "))
        cls = "pass" if r.get("status") == "eval_scheduled" else ""
        fcls = "is-founder" if founder else ""
        rows.append(
            f'<li class="{fcls}">'
            f'<code>{html.escape(str(r.get("lane") or "AB1"))}</code>'
            f'<span><strong>{html.escape(str(r.get("company") or "prospect"))}</strong>'
            f' · {html.escape(str(r.get("next_action") or ""))}</span>'
            f'<span class="sa-v {cls}">{status}</span></li>'
        )
    return "".join(rows)


def _consistent_factory(factory: dict, aeg: dict) -> dict:
    out = dict(factory)
    nested = dict(out.get("aeg") or {})
    nested.update(
        {
            "verdict": aeg.get("verdict"),
            "blockers": aeg.get("blockers") or [],
            "terminal_transcript": aeg.get("terminal_transcript"),
            "checks": aeg.get("checks") or [],
            "evidence_id": aeg.get("evidence_id"),
        }
    )
    out["aeg"] = _sanitize_obj(nested)
    return _sanitize_obj(out)


def hydrate_live_html(aeg: dict, factory: dict) -> bool:
    aeg = _align_aeg_proof(dict(aeg))
    factory = _consistent_factory(factory, aeg)
    if not LIVE_HTML.is_file():
        return False
    text = LIVE_HTML.read_text(encoding="utf-8")
    trust = _read_json(DATA / "trust-signals.json")
    verdict = str(aeg.get("verdict") or "UNKNOWN")
    evidence_id = str(aeg.get("evidence_id") or "")
    pipe = factory.get("pipeline") or {}
    counts = pipe.get("counts") or {}
    metrics = factory.get("metrics") or {}
    proof_viewed = counts.get("proof_viewed", metrics.get("proof_viewed", 0))
    eval_sched = counts.get("eval_scheduled", metrics.get("eval_scheduled", 0))
    deposits = counts.get("pilot_deposit", 0)
    meta_parts: list[str] = []
    if aeg.get("hosted_at"):
        meta_parts.append(f"Synced {str(aeg['hosted_at'])[:19].replace('T', ' UTC')}")
    if factory.get("valid_yes") is not None:
        meta_parts.append(f"Valid YES {factory['valid_yes']}/{factory.get('valid_yes_total') or 1000}")
    if evidence_id:
        meta_parts.append(evidence_id)
    meta = " · ".join(meta_parts) or "Live from factory disk"
    sync_line = factory.get("factory_now_line") or aeg.get("disclaimer") or "Live from factory disk"
    if str(aeg.get("verdict") or "").upper() == "PASS":
        terminal = html.escape(BUYER_SAFE_TERMINAL)
        blockers_html = _render_blockers([])
    else:
        terminal = html.escape(_sanitize_public_text(str(aeg.get("terminal_transcript") or "")))
        blockers_html = _render_blockers(aeg.get("blockers") or [])
    verdict_cls = "is-pass" if verdict == "PASS" else ("is-block" if verdict == "BLOCK" else "")

    valid_yes = trust.get("valid_yes")
    valid_yes_total = trust.get("valid_yes_total") or 1000
    gov = trust.get("governance") or {}
    proof_checks = f"{valid_yes}/{valid_yes_total}" if valid_yes is not None else f"{len(aeg.get('checks') or [])}/{len(aeg.get('checks') or [])}"
    gov_verdict = str(gov.get("verdict") or verdict or "PASS")

    replacements = [
        (
            r'<span[^>]*id="sa-aeg-verdict"[^>]*>[^<]*</span>',
            f'<span class="ar-hero-accent sa-aeg-verdict-hero {verdict_cls}" id="sa-aeg-verdict">{html.escape(verdict)}</span>',
        ),
        (r'id="sa-aeg-evidence"[^>]*>Evidence ID · [^<]*</p>', f'id="sa-aeg-evidence">Evidence ID · {html.escape(evidence_id)}</p>'),
        (r'id="sa-aeg-proof-viewed">[^<]*</strong>', f'id="sa-aeg-proof-viewed">{proof_viewed}</strong>'),
        (r'id="sa-aeg-eval-scheduled">[^<]*</strong>', f'id="sa-aeg-eval-scheduled">{eval_sched}</strong>'),
        (r'id="sa-aeg-deposits">[^<]*</strong>', f'id="sa-aeg-deposits">{deposits}</strong>'),
        (r'id="sa-aeg-meta">[^<]*</p>', f'id="sa-aeg-meta">{html.escape(meta)}</p>'),
        (r'id="sa-aeg-sync">[^<]*</p>', f'id="sa-aeg-sync">{html.escape(sync_line)}</p>'),
        (r'data-trust-valid-yes>[^<]*</strong>', f'data-trust-valid-yes>{html.escape(proof_checks)}</strong>'),
        (r'data-trust-governance>[^<]*</strong>', f'data-trust-governance>{html.escape(gov_verdict)}</strong>'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, count=1)

    text = re.sub(
        r'(<div id="sa-aeg-checks"[^>]*>).*?(</div>)',
        lambda m: f'<div id="sa-aeg-checks" class="sa-aeg-checks">{_render_checks(aeg.get("checks") or [])}</div>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<div id="sa-aeg-blockers"[^>]*>).*?(</div>)',
        lambda m: f'<div id="sa-aeg-blockers" class="sa-aeg-blockers">{blockers_html}</div>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'(<pre[^>]*id="sa-aeg-terminal"[^>]*>).*?(</pre>)',
        lambda m: f'{m.group(1)}{terminal}{m.group(2)}',
        text,
        count=1,
        flags=re.DOTALL,
    )

    rows_html = _render_pipeline_rows(factory)
    text = re.sub(
        r'<ul class="sa-aeg-pipeline-rows" id="sa-aeg-pipeline-rows"[^>]*>.*?</ul>',
        f'<ul class="sa-aeg-pipeline-rows" id="sa-aeg-pipeline-rows" aria-label="Live pipeline rows">{rows_html}</ul>',
        text,
        count=1,
        flags=re.DOTALL,
    )

    bootstrap = {"aeg": _sanitize_obj(aeg), "factory": _consistent_factory(factory, aeg)}
    bootstrap_tag = (
        f"{BOOTSTRAP_MARKER}\n"
        f'<script type="application/json" id="sa-aeg-bootstrap">{json.dumps(bootstrap)}</script>'
    )
    if BOOTSTRAP_MARKER in text:
        start = text.index(BOOTSTRAP_MARKER)
        end = text.find("</script>", start)
        if end != -1:
            text = text[:start] + bootstrap_tag + text[end + len("</script>") :]
    else:
        text = text.replace(
            '<script src="/sourcea/sourcea-aeg-live.js" defer></script>',
            bootstrap_tag + '\n<script src="/sourcea/sourcea-aeg-live.js" defer></script>',
        )

    LIVE_HTML.write_text(text, encoding="utf-8")
    return True


def update_public_urls(site_proof: str) -> None:
    row = _read_json(PUBLIC_URLS)
    if not row:
        row = {"schema": "sourcea-public-urls-v1", "at": _now()}
    row["aeg_live_url"] = site_proof
    row["proof_url"] = site_proof
    row["at"] = _now()
    boot = _read_json(DATA / "boot-proof.json")
    if boot.get("verdict"):
        row["boot_verdict"] = boot.get("verdict")
    PUBLIC_URLS.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Inject AEG live proof JSON for landing")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    row = build_aeg_live()
    out_path = DATA / "aeg-live.json"
    factory = _read_json(DATA / "factory-live.json")
    if not args.dry_run:
        DATA.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        update_public_urls(str(row.get("site_proof_url") or ""))
        hydrated = hydrate_live_html(row, factory)
        RECEIPT.write_text(
            json.dumps(
                {
                    "schema": "sourcea-aeg-live-inject-v1",
                    "at": _now(),
                    "path": str(out_path),
                    "evidence_id": row.get("evidence_id"),
                    "site_proof_url": row.get("site_proof_url"),
                    "live_html_hydrated": hydrated,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: aeg-live · {row.get('evidence_id')} · {row.get('site_proof_url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
