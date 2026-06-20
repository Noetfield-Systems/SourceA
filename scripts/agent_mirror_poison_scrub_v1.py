#!/usr/bin/env python3
"""Permanent poison scrub — mirror inject, ~/.sina receipts, checkcart, locked law pointers.

Law: data/agent-memory-mirror-poison-law-v1.json · INCIDENT-034 · INCIDENT-039 · INCIDENT-040
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
POISON_LAW = ROOT / "data/agent-memory-mirror-poison-law-v1.json"
CHECKCART_DUTY = ROOT / "data/agent-law-wire-checkcart-duty-v1.json"
RECEIPT = SINA / "agent-mirror-poison-scrub-receipt-v1.json"

# Substrings that must not appear in agent-facing inject / alwaysApply rules (founder chat body)
POISON_SUBSTRINGS: list[tuple[str, str]] = [
    ("run check cart W1", "039"),
    ("run W4–W10 if state moved", "039"),
    ("run W4-W10 if state moved", "039"),
    ("W1–W10 before saying done", "039"),
    ("W1-W10 before saying done", "039"),
    ("wire to ALL surfaces before saying done", "039"),
    ("Seven surfaces → validate", "039"),
    ("Seven surfaces validate then sync mirror then reply", "039"),
    ("validate-law-supersession-surfaces-v1.sh before", "039"),
    ("validate-law-supersession.*reply", "039"),
    ("run all validators to confirm", "039"),
    ("sync mirror → reply", "034"),
]

POISON_REGEX: list[tuple[str, str, str]] = [
    ("R1", r"W1[-–]W10.*before.*(?:reply|done|ship|chat)", "039"),
    ("R2", r"Seven\s+surfaces.*validate-law-supersession", "039"),
    ("R3", r"validate-law-supersession.*(?:→|->).*reply", "039"),
    ("R4", r"(?:run|Run)\s+all\s+validators", "039"),
]

REPLACEMENTS: list[tuple[str, str]] = [
    (
        "run check cart W1–W10 before saying done",
        "wire W1–W10 on ship window / cloud CI only — never Mac founder chat pre-reply (INCIDENT-039)",
    ),
    (
        "run check cart W1-W10 before saying done",
        "wire W1–W10 on ship window / cloud CI only — never Mac founder chat pre-reply (INCIDENT-039)",
    ),
    (
        "W1–W10 wire cart before done",
        "W1–W10 on ship window / cloud CI only — not Mac pre-reply marathon (INCIDENT-039)",
    ),
    (
        "wire to ALL surfaces before saying done",
        "wire W1–W10 on ship window / cloud CI only — not Mac pre-reply marathon (INCIDENT-039)",
    ),
    (
        "If touching law: check cart W1–W10",
        "If law touched: W1–W10 ship window / cloud CI only (INCIDENT-039)",
    ),
    (
        "This card + W1–W10 + disk proof",
        "This card + Read receipts + disk proof — W1–W10 ship window only",
    ),
    (
        "7. Law ships also run agent-law-wire-checkcart W1–W10",
        "7. Law ships: W1–W10 on ship window / cloud CI only (INCIDENT-039)",
    ),
    (
        "Read ~/.sina/agent-law-wire-checkcart-v1.json — run W4–W10 if state moved",
        "Read ~/.sina/agent-law-wire-checkcart-v1.json — ship window / cloud CI only (INCIDENT-039: not Mac pre-reply validator marathon)",
    ),
    (
        "Read ~/.sina/agent-law-wire-checkcart-v1.json \u2014 run W4\u2013W10 if state moved",
        "Read ~/.sina/agent-law-wire-checkcart-v1.json — ship window / cloud CI only (INCIDENT-039: not Mac pre-reply validator marathon)",
    ),
    (
        "This card + W1–W10 + build logged",
        "This card + Read receipts + disk proof — W1–W10 ship window only",
    ),
    (
        "D01: After ANY *_LOCKED_v1.md change or ASF order: run check cart W1\u2013W10 before saying done",
        "D01: After law change: wire W1–W10 on ship window / cloud CI only — never Mac founder chat pre-reply marathon (INCIDENT-039 · INCIDENT-040)",
    ),
    (
        "validators · receipt",
        "read receipts · no bash validate marathon before reply",
    ),
]

SKIP_PATH_PARTS = (
    "archive/",
    "graphify-out/",
    "node_modules/",
    "brain-os/incidents/",
    "validate-agent-memory-mirror",
    "agent_mirror_poison_scrub",
    "agent-memory-mirror-poison-law",
    "agent-law-poison-registry",
    "mac-validator-stuck-red-flag",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _scrub_text(text: str) -> tuple[str, int]:
    n = 0
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            n += 1
    return text, n


def _scrub_json_value(obj, *, changes: list[str]) -> object:
    if isinstance(obj, str):
        new, n = _scrub_text(obj)
        if n:
            changes.append(f"str:{obj[:48]}...")
        return new
    if isinstance(obj, list):
        return [_scrub_json_value(x, changes=changes) for x in obj]
    if isinstance(obj, dict):
        return {k: _scrub_json_value(v, changes=changes) for k, v in obj.items()}
    return obj


def scrub_sina_json_files() -> list[str]:
    touched: list[str] = []
    targets = [
        SINA / "agent-executor-daily-duty-card-v1.json",
        SINA / "agent-law-wire-checkcart-v1.json",
        SINA / "agent-cart-task-inbox-v1.json",
        SINA / "agent_session_gate_receipt_v1.json",
        SINA / "last-truth-bundle-v1.json",
        SINA / "agent-memory-mirror-v1.json",
    ]
    targets.extend(SINA.glob("cart-tasks/agents/*.json"))
    for path in targets:
        if not path.is_file():
            continue
        raw = path.read_text(encoding="utf-8")
        changes: list[str] = []
        if path.name == "agent-law-wire-checkcart-v1.json":
            duty_row = _read_json(CHECKCART_DUTY)
            if isinstance(duty_row, dict) and duty_row.get("duty"):
                try:
                    data = json.loads(raw)
                    if isinstance(data, dict) and data.get("duty") != duty_row["duty"]:
                        data["duty"] = duty_row["duty"]
                        data["session_read"] = duty_row.get("session_read")
                        data["proof_mac_founder_session"] = duty_row.get("proof_mac_founder_session")
                        data["poison_law_version"] = duty_row.get("version")
                        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                        touched.append(str(path))
                        continue
                except json.JSONDecodeError:
                    pass
        new_raw, n = _scrub_text(raw)
        if n:
            path.write_text(new_raw, encoding="utf-8")
            touched.append(str(path))
    return touched


SKIP_RULE_FILES = frozenset(
    {
        "034-mac-no-validator-stuck-red-flag.mdc",
        "agent-memory-mirror.mdc",
        "000-dead-law-stubs.mdc",
    }
)

def scan_poison_in_text(text: str, *, rel: str) -> list[dict]:
    hits: list[dict] = []
    for line in text.splitlines():
        if any(
            s in line
            for s in (
                "ship window",
                "cloud CI only",
                "not Mac",
                "INCIDENT-039",
                "forbidden forever",
                "- **No**",
                "FORBIDDEN",
                "Poison (",
                "Paradox poison",
                "never orders",
                "must not inject",
                "do not bash",
                "forbidden_phrase",
                "paradox_poison",
                "poison_patterns",
                "mirror_must_not",
            )
        ):
            continue
        low = line.lower()
        for sub, inc in POISON_SUBSTRINGS:
            if sub.lower() in low:
                hits.append({"path": rel, "kind": "substring", "match": sub, "incident": inc, "line": line[:120]})
        for rid, pat, inc in POISON_REGEX:
            if re.search(pat, line, re.I):
                hits.append({"path": rel, "kind": "regex", "id": rid, "incident": inc, "line": line[:120]})
    return hits


def scan_repo_rules_and_inject() -> list[dict]:
    hits: list[dict] = []
    scan_dirs = [
        ROOT / ".cursor/rules",
        ROOT / "brain-os/law/enforcement",
        ROOT / "data",
    ]
    for base in scan_dirs:
        if not base.is_dir():
            continue
        glob = "*.mdc" if base.name == "rules" else ("*.json" if base.name == "data" else "*.md")
        for path in base.glob(glob):
            if path.name in SKIP_RULE_FILES:
                continue
            rel = str(path.relative_to(ROOT))
            if any(s in rel for s in SKIP_PATH_PARTS):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for h in scan_poison_in_text(text, rel=rel):
                hits.append(h)
    mirror = SINA / "agent-memory-mirror-v1.json"
    if mirror.is_file():
        inj = (_read_json(mirror) or {}).get("inject") or {}
        blob = json.dumps(inj, ensure_ascii=False)
        hits.extend(scan_poison_in_text(blob, rel="~/.sina/agent-memory-mirror-v1.json inject"))
    duty = SINA / "agent-executor-daily-duty-card-v1.json"
    if duty.is_file():
        blob = json.dumps(_read_json(duty) or {}, ensure_ascii=False)
        hits.extend(scan_poison_in_text(blob, rel="~/.sina/agent-executor-daily-duty-card-v1.json"))
    return hits


def sync_mirror() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from agent_memory_mirror_v1 import sync_mirror as _sync  # noqa: WPS433

    return _sync()


def sync_truth_bundle() -> dict:
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "agent_truth_bundle_v1.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    i = out.find("{")
    if i >= 0:
        try:
            return json.loads(out[i:])
        except json.JSONDecodeError:
            pass
    return {"ok": proc.returncode == 0, "raw": out[:400]}


def run(*, scrub: bool, sync: bool, validate_only: bool) -> dict:
    report: dict = {
        "schema": "agent-mirror-poison-scrub-v1",
        "at": _now(),
        "scrubbed_files": [],
        "mirror_sync": None,
        "truth_bundle": None,
        "poison_hits": [],
        "ok": True,
    }
    if scrub and not validate_only:
        report["scrubbed_files"] = scrub_sina_json_files()
    if sync and not validate_only:
        report["mirror_sync"] = {"ok": True, "hash8": sync_mirror().get("mirror_hash8")}
        report["truth_bundle"] = sync_truth_bundle()
    report["poison_hits"] = scan_repo_rules_and_inject()
    report["ok"] = len(report["poison_hits"]) == 0
    try:
        RECEIPT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError:
        fallback = ROOT / "data" / "agent-mirror-poison-scrub-receipt-v1.json"
        fallback.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["receipt_fallback"] = str(fallback)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrub mirror poison permanently")
    ap.add_argument("--scrub", action="store_true", help="Rewrite ~/.sina stale inject strings")
    ap.add_argument("--sync", action="store_true", help="Re-sync mirror + truth bundle after scrub")
    ap.add_argument("--validate", action="store_true", help="Scan only — fail if poison remains")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="--scrub --sync --validate")
    args = ap.parse_args()
    if args.all:
        args.scrub = args.sync = args.validate = True
    if not (args.scrub or args.sync or args.validate):
        args.scrub = args.sync = args.validate = True
    report = run(scrub=args.scrub, sync=args.sync, validate_only=args.validate and not args.scrub)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"POISON_SCRUB ok={report['ok']} hits={len(report['poison_hits'])} scrubbed={len(report['scrubbed_files'])}")
        for h in report["poison_hits"][:20]:
            print(f"  HIT {h.get('path')} · {h.get('match') or h.get('id')}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
