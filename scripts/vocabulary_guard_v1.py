#!/usr/bin/env python3
"""Vocabulary guard — positive inject + forbidden stale phrases (INCIDENT-034).

Paired with anti-staleness: disk truth is useless if inject vocabulary is stale or prohibitive.
Law: SINA_PROHIBITION_INSTEAD_OF_DISK_WIRE_INCIDENT_034 · crawl-mirror vocab v1.2
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
MIRROR_PATH = SINA / "agent-memory-mirror-v1.json"
SURFACES_PATH = SINA / "agent-live-surfaces-v1.json"

# Inject / founder-facing surfaces — prohibition prose forbidden (INCIDENT-034)
INJECT_FORBIDDEN: list[tuple[str, str]] = [
    (r"never say", "never-say-prohibition"),
    (r"deprecated founder word", "deprecated-founder-word"),
    (r"not Prompt feed", "not-prompt-feed"),
    (r"forbidden_close_lines", "forbidden_close_lines-key"),
    (r"no Prompt feed", "no-prompt-feed"),
    (r"prompt-feed confirm", "prompt-feed-confirm-dead"),
    (r"START AUTO RUN", "auto-run-dead"),
    (r"Sina Command", "legacy-hub-brand"),
]

# Pipeline/tooling — display-layer vocabulary (crawl-mirror v1.2)
TOOLING_FORBIDDEN: list[tuple[str, str]] = [
    (r"\brebrand:disk\b", "rebrand-disk-script"),
    (r"\brebrand:assets\b", "rebrand-assets-script"),
    (r"\brebrand-disk\b", "rebrand-disk-name"),
    (r"\brebrand-assets\b", "rebrand-assets-name"),
]

POSITIVE_REQUIRED_IN_SURFACES: list[tuple[str, str]] = [
    (r"work-order|brain-outbound|Auto Runtime|factory.now|factory-now", "execution-path"),
    (r"factory.now|factory-now", "factory-now-line"),
]

POSITIVE_CANONICAL: dict[str, str] = {
    "founder_daily_ops": "Auto Runtime · Brain work-order · Hub glance",
    "execution_path": "brain work-order dispatch",
    "local_brand": "brand:disk / brand:assets / local-brand",
    "stranger_gate": "sascip",
}


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def check_mirror_inject() -> dict[str, Any]:
    mirror = _read_json(MIRROR_PATH)
    inj_text = json.dumps(mirror.get("inject") or {})
    if not inj_text or inj_text == "{}":
        try:
            import sys

            sys.path.insert(0, str(ROOT / "scripts"))
            from agent_memory_mirror_v1 import INJECT_LAW  # noqa: WPS433

            inj_text = json.dumps(INJECT_LAW)
        except Exception:
            inj_text = "{}"
    violations: list[str] = []
    for pat, label in INJECT_FORBIDDEN:
        if re.search(pat, inj_text, re.I):
            violations.append(f"inject:{label}")
    if re.search(r"prompt-feed|Prompt feed", inj_text, re.I) and not re.search(
        r"Next steps", inj_text, re.I
    ):
        violations.append("inject:prompt-feed-without-next-steps")
    return {"ok": len(violations) == 0, "violations": violations, "surface": "mirror_inject"}


def check_live_surfaces() -> dict[str, Any]:
    surf = _read_json(SURFACES_PATH)
    blob = json.dumps(surf)
    violations: list[str] = []
    warnings: list[str] = []
    for pat, label in INJECT_FORBIDDEN:
        if re.search(pat, blob, re.I):
            violations.append(f"surfaces:{label}")
    for pat, label in POSITIVE_REQUIRED_IN_SURFACES:
        if not re.search(pat, blob, re.I):
            warnings.append(f"missing_positive:{label}")
    fn = surf.get("factory_now_line") or ""
    if not fn.strip():
        violations.append("surfaces:empty_factory_now_line")
    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "factory_now_line": fn[:80],
        "surface": "agent_live_surfaces",
    }


def check_mirror_disk_forbidden() -> dict[str, Any]:
    """Delegate to agent_memory_mirror --validate."""
    try:
        import subprocess
        import sys

        out = subprocess.check_output(
            [sys.executable, str(ROOT / "scripts" / "agent_memory_mirror_v1.py"), "--validate", "--json"],
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(ROOT),
            timeout=60,
        )
        i = out.find("{")
        row = json.loads(out[i:]) if i >= 0 else {}
        return {
            "ok": bool(row.get("ok")),
            "violations": [f"{v.get('file')}:{v.get('label')}" for v in (row.get("violations") or [])],
            "surface": "mirror_disk_scan",
        }
    except Exception as exc:
        return {"ok": False, "violations": [f"mirror_validate_error:{exc}"], "surface": "mirror_disk_scan"}


def check_tooling_vocabulary(*, paths: list[Path] | None = None) -> dict[str, Any]:
    scan = paths or [
        ROOT / "scripts",
        ROOT / ".cursor" / "rules",
    ]
    violations: list[str] = []
    for base in scan:
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.suffix not in (".py", ".sh", ".mdc", ".mjs", ".json", ".md"):
                continue
            if "node_modules" in p.parts or "commercial-video-factory" in p.parts:
                continue
            if p.name.startswith("validate-") and "rebrand" in p.name:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat, label in TOOLING_FORBIDDEN:
                if re.search(pat, text, re.I):
                    violations.append(f"{p.relative_to(ROOT)}:{label}")
    return {"ok": len(violations) == 0, "violations": violations[:50], "surface": "tooling_vocab"}


def check_disclosure_ladder() -> dict[str, Any]:
    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from disclosure_ladder_v1 import check_disclosure_surfaces  # noqa: WPS433

        return check_disclosure_surfaces()
    except Exception as exc:
        return {"ok": False, "violations": [f"disclosure_check_error:{exc}"], "surface": "disclosure_ladder"}


def check_mcp_stack() -> dict[str, Any]:
    """Fail if live surfaces expose MCP vendor names as T0 lead (DL-U2 + MCP policy)."""
    violations: list[str] = []
    try:
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        from mcp_stack_free_tier_v1 import load_ssot  # noqa: WPS433

        ssot = load_ssot()
        for _name, row in (ssot.get("servers") or {}).items():
            if row.get("public_mention") is True:
                violations.append(f"mcp_server_public_mention_true:{_name}")
        disc = ssot.get("disclosure_audit") if isinstance(ssot.get("disclosure_audit"), dict) else {}
    except Exception as exc:
        return {"ok": False, "violations": [f"mcp_stack_check_error:{exc}"], "surface": "mcp_stack"}
    surfaces_path = Path.home() / ".sina" / "agent-live-surfaces-v1.json"
    if surfaces_path.is_file():
        try:
            surfaces = json.loads(surfaces_path.read_text(encoding="utf-8"))
            line = str(surfaces.get("factory_now_line") or "").lower()
            for vendor in ("datadog mcp", "github mcp hero", "mcp stack first"):
                if vendor in line:
                    violations.append(f"factory_now_mcp_vendor_lead:{vendor}")
        except (OSError, json.JSONDecodeError):
            pass
    return {"ok": not violations, "violations": violations, "surface": "mcp_stack"}


def check_platform_neutral() -> dict[str, Any]:
    """Live surfaces must not use Mac-only platform gates."""
    try:
        from world_model_plan_check_v1 import run_check  # noqa: WPS433

        row = run_check(write=False)
        violations = row.get("violations") or []
        return {
            "ok": bool(row.get("ok")),
            "violations": [f"{v.get('file')}:{v.get('phrase')}" for v in violations[:8]],
            "surface": "platform_neutral",
            "advisory_count": row.get("advisory_count"),
        }
    except Exception as exc:
        return {"ok": False, "violations": [f"platform_neutral_error:{exc}"], "surface": "platform_neutral"}


def run_vocabulary_gate(*, include_tooling: bool = False, strict_disk: bool = False) -> dict[str, Any]:
    checks = [
        check_mirror_inject(),
        check_live_surfaces(),
        check_disclosure_ladder(),
        check_mcp_stack(),
        check_platform_neutral(),
    ]
    if strict_disk:
        checks.append(check_mirror_disk_forbidden())
    if include_tooling:
        checks.append(check_tooling_vocabulary())
    violations: list[str] = []
    warnings: list[str] = []
    for c in checks:
        violations.extend(c.get("violations") or [])
        warnings.extend(c.get("warnings") or [])
    ok = all(c.get("ok") for c in checks)
    return {
        "schema": "vocabulary-guard-v1",
        "ok": ok,
        "checks": checks,
        "violations": violations,
        "warnings": warnings,
        "positive_canonical": POSITIVE_CANONICAL,
        "law": "INCIDENT-034 + crawl-mirror vocab v1.2",
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Vocabulary guard — anti-staleness companion")
    ap.add_argument("--tooling", action="store_true", help="Also scan scripts/docs for rebrand:*")
    ap.add_argument("--strict-disk", action="store_true", help="Full mirror disk forbidden scan")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_vocabulary_gate(include_tooling=args.tooling, strict_disk=args.strict_disk)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(f"VOCABULARY_GUARD ok={row['ok']} violations={len(row['violations'])}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
