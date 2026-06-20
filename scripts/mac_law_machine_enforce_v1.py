#!/usr/bin/env python3
"""Mac Law machine enforce — locked MacLaw docs → agent + shell gates.

Law: data/mac-law-machine-enforceable-v1.json
Docs: ~/Desktop/MacLaw/MAC_LAW_SSOT_LOCKED.md + mandates + cursor + pressure
Receipt: ~/.sina/mac-law-machine-enforce-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/mac-law-machine-enforceable-v1.json"
RECEIPT = SINA / "mac-law-machine-enforce-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _expand(raw: str) -> Path:
    return Path(str(raw or "").replace("~", str(Path.home()))).expanduser()


def load_ssot() -> dict:
    return _read(SSOT)


def _flags_ok(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    row: dict = {"present": {}, "absent": {}}
    for rel in ssot.get("mandatory_flags_present") or []:
        path = _expand(str(rel))
        ok = path.is_file()
        row["present"][rel] = ok
        if not ok:
            issues.append(f"flag_missing:{Path(rel).name}")
    for rel in ssot.get("mandatory_flags_absent") or []:
        path = _expand(str(rel))
        ok = not path.is_file()
        row["absent"][rel] = ok
        if not ok:
            issues.append(f"flag_must_be_absent:{Path(rel).name}")
    cfg = ssot.get("config_must") or {}
    vp = _expand(str(cfg.get("path") or ""))
    if vp.is_file() and cfg.get("visual_proof_enabled") is False:
        try:
            data = json.loads(vp.read_text(encoding="utf-8"))
            if data.get("enabled") is True:
                issues.append("visual_proof_enabled_must_be_false")
        except (OSError, json.JSONDecodeError):
            pass
    return issues, row


def _law_docs_ok(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    docs: dict = {}
    for key, rel in (ssot.get("law_docs") or {}).items():
        path = _expand(str(rel))
        ok = path.is_file()
        docs[key] = {"path": str(path), "ok": ok}
        if not ok:
            issues.append(f"missing_mac_law_doc:{key}")
    return issues, docs


def scan_shell_command(command: str) -> dict:
    """Block forbidden Mac-body shell before run."""
    ssot = load_ssot()
    hits: list[dict] = []
    cmd = command or ""
    for row in ssot.get("forbidden_shell_patterns") or []:
        pat = str(row.get("pattern") or "")
        if pat and re.search(pat, cmd, re.I):
            hits.append(
                {
                    "id": row.get("id"),
                    "because": row.get("because"),
                    "pattern": pat,
                }
            )
    return {"ok": not hits, "hits": hits}


def scan_agent_text(text: str) -> dict:
    """Block agents suggesting or running Mac-body forbidden work."""
    hits: list[dict] = []
    combined = scan_shell_command(text)
    hits.extend(combined.get("hits") or [])

    ssot = load_ssot()
    low = (text or "").lower()
    parrot_mac_fix = (
        "fix_disk" in low
        and "disk_live_wire_sync" in low
        and "for_founder" not in low
    )
    if parrot_mac_fix:
        hits.append(
            {
                "id": "mac_sync_parrot_to_founder",
                "because": "Do not tell founder to run Mac sync chains — use cloud bay / Hub",
            }
        )
    if re.search(r"validate-[a-z0-9-]*e2e", text, re.I):
        if "cloud ci" not in low and "ship window" not in low:
            hits.append(
                {
                    "id": "suggest_e2e_on_mac",
                    "because": "E2E validators run on cloud CI — not Mac during founder session",
                }
            )
    if "comprehension_pipeline_loop" in low and "/api/comprehension-loop" not in low:
        hits.append(
            {
                "id": "local_comprehension_primary",
                "because": "Comprehension runs on cloud via POST /api/comprehension-loop/v1",
            }
        )
    return {"ok": not hits, "hits": hits}


def assess(*, include_cursor: bool = False) -> dict:
    ssot = load_ssot()
    issues: list[str] = []
    if not ssot:
        issues.append("missing_ssot")

    doc_issues, law_docs = _law_docs_ok(ssot) if ssot else ([], {})
    issues.extend(doc_issues)
    flag_issues, flags = _flags_ok(ssot) if ssot else ([], {})
    issues.extend(flag_issues)

    cursor_probe: dict = {}
    if include_cursor and str(SCRIPTS) not in __import__("sys").path:
        __import__("sys").path.insert(0, str(SCRIPTS))
    if include_cursor:
        try:
            from cursor_agent_law_v1 import probe_caps  # noqa: WPS433

            cursor_probe = probe_caps()
            if not cursor_probe.get("ok"):
                for v in cursor_probe.get("violations") or []:
                    if v.get("id") != "cursor_process_warn":
                        issues.append(f"cursor_law:{v.get('id')}")
        except Exception as exc:
            issues.append(f"cursor_law_load:{exc}")

    ok = not issues
    line = (
        f"mac-law-enforce · cloud_body={'YES' if flags.get('present', {}).get('~/.sina/mac-cloud-body-only-v1.flag') else 'NO'} · "
        f"light_validators={'YES' if flags.get('present', {}).get('~/.sina/mac-light-validators-only-v1.flag') else 'NO'} · "
        f"ok={'PASS' if ok else 'RED'}"
    )
    return {
        "ok": ok,
        "issues": issues,
        "line": line,
        "one_law": ssot.get("one_law"),
        "agent_must": ssot.get("agent_must") or [],
        "cloud_only_routes": ssot.get("cloud_only_routes") or {},
        "law_docs": law_docs,
        "flags": flags,
        "cursor_probe": cursor_probe if include_cursor else None,
    }


def inject_slice() -> dict:
    ssot = load_ssot()
    row = _read(RECEIPT)
    return {
        "one_law": ssot.get("one_law"),
        "agent_must": ssot.get("agent_must") or [],
        "forbidden_on_mac_body": ssot.get("forbidden_on_mac_body") or [],
        "cloud_only_routes": ssot.get("cloud_only_routes") or {},
        "comprehension_hub": (ssot.get("cloud_only_routes") or {}).get("comprehension"),
        "line": row.get("line") or assess().get("line"),
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def sync_receipt(*, include_cursor: bool = False, enforce: bool = False) -> dict:
    if enforce:
        try:
            import sys

            if str(SCRIPTS) not in sys.path:
                sys.path.insert(0, str(SCRIPTS))
            from cursor_agent_law_v1 import enforce_flags  # noqa: WPS433

            enforce_flags()
        except Exception:
            pass
        ssot = load_ssot()
        SINA.mkdir(parents=True, exist_ok=True)
        ts = _now()
        for rel in ssot.get("mandatory_flags_present") or []:
            path = _expand(str(rel))
            if not path.is_file():
                path.write_text(f"mac-law-machine-enforce · {ts}\n", encoding="utf-8")
    row = assess(include_cursor=include_cursor)
    receipt = {"schema": "mac-law-machine-enforce-receipt-v1", "saved_at": _now(), **row}
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    surf_path = SINA / "agent-live-surfaces-v1.json"
    if surf_path.is_file():
        surf = _read(surf_path)
        surf["mac_law_machine_line"] = row.get("line")
        surf["mac_law_machine_enforce"] = {
            "ok": row.get("ok"),
            "ssot": "data/mac-law-machine-enforceable-v1.json",
        }
        surf_path.write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac Law machine enforce v1")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--sync-receipt", action="store_true")
    ap.add_argument("--include-cursor", action="store_true")
    ap.add_argument("--scan-shell", default="")
    ap.add_argument("--scan-text", default="")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--enforce", action="store_true", help="Create missing Mac Law flags")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.inject:
        row = inject_slice()
    elif args.scan_shell:
        row = scan_shell_command(args.scan_shell)
    elif args.scan_text:
        row = scan_agent_text(args.scan_text)
    elif args.sync_receipt:
        row = sync_receipt(include_cursor=args.include_cursor, enforce=args.enforce)
    else:
        row = assess(include_cursor=args.include_cursor)

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("line") or row.get("one_law") or json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
