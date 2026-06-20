#!/usr/bin/env python3
"""Fail-closed enforcer — no Proxycurl / self-score theater in runtime tree.

Law: data/anti-theater-validator-loop-v1.json · data/outbound-factory-salvage-spec-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "anti-theater-validator-loop-v1.json"
SALVAGE = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"
RECEIPTS = ROOT / "receipts"

DEFAULT_FORBIDDEN: list[tuple[str, re.Pattern[str]]] = [
    ("proxycurl", re.compile(r"proxycurl", re.I)),
    ("nubela", re.compile(r"nubela", re.I)),
    ("insight_quality", re.compile(r"insight_quality\s*[:=]", re.I)),
    ("auto_send_on_model_score", re.compile(r"auto_send_on_model_score", re.I)),
    ("fetch_executive_dna", re.compile(r"fetch_executive_dna", re.I)),
    ("pg_net_webhook", re.compile(r"pg_net\s*webhook|supabase.*webhook.*compile", re.I)),
    ("self_healing", re.compile(r"self[_-]?healing.*llm|self_healing_llm", re.I)),
    ("pydantic_scorecard", re.compile(r"pydantic.*scorecard|scorecard.*pydantic", re.I)),
    ("supabase_targets", re.compile(r"supabase.*targets|targets.*webhook.*async", re.I)),
    ("auto_send_outbox", re.compile(r"auto[_-]?send.*outbox|outbox_queue.*auto", re.I)),
    ("model_pass_ship", re.compile(r"if.*score.*>=.*92.*send|model.*pass.*auto.?send", re.I)),
]

DEFAULT_ALLOWLIST = {
    "data/outbound-factory-salvage-spec-v1.json",
    "data/outbound-factory-100-upgrade-plan-v1.json",
    "data/outbound-factory-worker-queue-v1.json",
    "data/anti-theater-validator-loop-v1.json",
    "docs/SOURCEA_OUTBOUND_FACTORY_SALVAGE_SPEC_LOCKED_v1.md",
    "scripts/validate_outbound_forbidden_sources_v1.py",
    "scripts/anti_theater_validator_loop_v1.py",
    "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json",
}

DEFAULT_DOC_ALLOW = re.compile(
    r"REJECT|DEFER|rejected_theater|No Proxycurl|document forbidden|theater|dead API|Manual LinkedIn|salvage rejected",
    re.I,
)

# Defensive references — blocklists, deferred absence checks, not runtime theater wiring.
SAFE_FORBIDDEN_LINE = re.compile(
    r"SCRAPE_PASTE_SOURCES|frozenset\s*\(|"
    r"deferred\s*=\s*True|len\(\w+\)\s*==\s*0|"
    r"check_u09[0-9]_deferred|forbidden_patterns|validate_outbound_forbidden|"
    r"rejected_theater|No Proxycurl|document forbidden|anti-theater|"
    r"glob\([\"'].*targets\*|check_u091",
    re.I,
)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot_config() -> tuple[list[tuple[str, re.Pattern[str]]], set[str], re.Pattern[str]]:
    ssot = _read_json(SSOT)
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for row in ssot.get("forbidden_patterns") or []:
        flags = re.I if str(row.get("flags", "i")).lower() == "i" else 0
        patterns.append((str(row.get("id") or "pat"), re.compile(str(row.get("regex") or ""), flags)))
    if not patterns:
        patterns = list(DEFAULT_FORBIDDEN)
    allow = set(ssot.get("allowlist_paths") or []) or set(DEFAULT_ALLOWLIST)
    doc_pat = ssot.get("doc_line_allow_regex")
    doc_re = re.compile(str(doc_pat), re.I) if doc_pat else DEFAULT_DOC_ALLOW
    return patterns, allow, doc_re


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _is_allowlisted(rel: str, allowlist: set[str]) -> bool:
    if rel in allowlist:
        return True
    for prefix in allowlist:
        if prefix.endswith("/") and rel.startswith(prefix):
            return True
        if rel.startswith(prefix + "/"):
            return True
    return False


def scan_forbidden_text(
    paths: list[Path],
    *,
    patterns: list[tuple[str, re.Pattern[str]]] | None = None,
    allowlist: set[str] | None = None,
    doc_allow: re.Pattern[str] | None = None,
    exclude_subpaths: tuple[str, ...] = ("fixtures/anti-theater-negative-v1",),
) -> dict:
    if patterns is None:
        pats, allow, doc_re = load_ssot_config()
    else:
        pats = patterns
        allow = allowlist or set()
        doc_re = doc_allow or DEFAULT_DOC_ALLOW

    violations: list[dict] = []
    scanned = 0
    suffixes = {".py", ".json", ".md", ".yaml", ".yml", ".txt", ".sh"}

    for base in paths:
        if not base.exists():
            continue
        files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file() and p.suffix in suffixes]
        for fp in files:
            rel = _rel(fp)
            if _is_allowlisted(rel, allow):
                continue
            if "graphify-out" in rel or "__pycache__" in rel:
                continue
            if exclude_subpaths and any(x in rel for x in exclude_subpaths):
                continue
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            scanned += 1
            for line_no, line in enumerate(text.splitlines(), 1):
                if doc_re.search(line):
                    continue
                if SAFE_FORBIDDEN_LINE.search(line):
                    continue
                for name, pat in pats:
                    if pat.search(line):
                        violations.append(
                            {
                                "file": rel,
                                "line": line_no,
                                "pattern": name,
                                "snippet": line.strip()[:120],
                            }
                        )
                        break
    return {
        "ok": len(violations) == 0,
        "scanned_files": scanned,
        "violation_count": len(violations),
        "violations": violations[:30],
    }


def scan_ship_authority_packs(outbound_root: Path | None = None) -> dict:
    """FAIL if pack claims ready_for_founder_send without sina_read >= 90."""
    root = outbound_root or (SINA / "outbound")
    violations: list[dict] = []
    scanned = 0
    if not root.is_dir():
        return {"ok": True, "scanned_packs": 0, "violations": [], "violation_count": 0}
    for pack_path in sorted(root.glob("**/pack.json")):
        scanned += 1
        try:
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        status = str(pack.get("status") or "")
        sina = pack.get("sina_read_score_pct")
        if sina is None:
            sina = pack.get("founder_score_pct")
        if status == "ready_for_founder_send" and (sina is None or int(sina) < 90):
            violations.append(
                {
                    "pack": str(pack_path.relative_to(root.parent) if pack_path.is_relative_to(root.parent) else pack_path),
                    "account_id": pack.get("account_id"),
                    "status": status,
                    "sina_read_score_pct": sina,
                    "issue": "ready_for_founder_send_without_sina_read_90",
                }
            )
    return {
        "ok": len(violations) == 0,
        "scanned_packs": scanned,
        "violation_count": len(violations),
        "violations": violations,
    }


def scan_paths(paths: list[Path] | None = None) -> dict:
    targets = paths or [
        ROOT / "scripts",
        ROOT / "data",
        SINA / "outbound",
        ROOT / "data" / "icp-compile",
        RECEIPTS,
    ]
    forbidden = scan_forbidden_text(targets)
    packs = scan_ship_authority_packs()
    ok = forbidden.get("ok") and packs.get("ok")
    # #region agent log
    try:
        import time

        with open(ROOT / ".cursor" / "debug-baabac.log", "a", encoding="utf-8") as _df:
            _df.write(
                json.dumps(
                    {
                        "sessionId": "baabac",
                        "runId": "full-e2e-v3",
                        "hypothesisId": "H3",
                        "location": "validate_outbound_forbidden_sources_v1.py:scan_paths",
                        "message": "forbidden_scan_complete",
                        "data": {
                            "ok": ok,
                            "violation_count": int(forbidden.get("violation_count") or 0),
                            "violations": [v.get("file") for v in (forbidden.get("violations") or [])[:5]],
                        },
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except OSError:
        pass
    # #endregion
    return {
        "ok": ok,
        "forbidden_scan": forbidden,
        "ship_authority_packs": packs,
        "scanned_files": forbidden.get("scanned_files"),
        "violation_count": int(forbidden.get("violation_count") or 0) + int(packs.get("violation_count") or 0),
        "violations": (forbidden.get("violations") or []) + (packs.get("violations") or []),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound forbidden sources enforcer")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--packs-only", action="store_true")
    args = ap.parse_args()
    if args.packs_only:
        row = scan_ship_authority_packs()
    else:
        row = scan_paths()
    row["ssot"] = str(SSOT.relative_to(ROOT))
    row["salvage"] = str(SALVAGE.relative_to(ROOT))
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row['ok']} violations={row.get('violation_count', 0)}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
