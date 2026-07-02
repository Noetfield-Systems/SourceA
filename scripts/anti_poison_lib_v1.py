#!/usr/bin/env python3
"""Anti-poison shared library — registry-driven scan, projection sanitize, positive inject.

Law: data/agent-law-poison-registry-v1.json · data/agent-memory-mirror-poison-law-v1.json
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY_PATH = ROOT / "data/agent-law-poison-registry-v1.json"
POISON_LAW_PATH = ROOT / "data/agent-memory-mirror-poison-law-v1.json"

# Legacy inline patterns (fallback if registry row missing)
_LEGACY_SUBSTRINGS: list[tuple[str, str]] = [
    ("run check cart W1", "039"),
    ("W1–W10 before saying done", "039"),
    ("W1-W10 before saying done", "039"),
    ("Seven surfaces → validate", "039"),
    ("validate-law-supersession-surfaces-v1.sh before", "039"),
    ("run all validators to confirm", "039"),
    ("sync mirror → reply", "034"),
]

_LEGACY_REGEX: list[tuple[str, str, str]] = [
    ("R1", r"W1[-–]W10.*before.*(?:reply|done|ship|chat)", "039"),
    ("R2", r"Seven\s+surfaces.*validate-law-supersession", "039"),
    ("R3", r"validate-law-supersession.*(?:→|->).*reply", "039"),
    ("R4", r"(?:run|Run)\s+all\s+validators", "039"),
]

SKIP_LINE_MARKERS = (
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
    "projection_patterns",
    "anti_poison",
    "RETIRED_FOUNDER_POISON",
)

SKIP_PATH_PARTS = (
    "archive/",
    "graphify-out/",
    "node_modules/",
    "brain-os/incidents/",
    "validate-agent-memory-mirror",
    "agent_mirror_poison_scrub",
    "anti_poison_lib_v1",
    "anti_poison_engine_v2",
    "agent-law-poison-registry",
    "agent-memory-mirror-poison-law",
    "mac-validator-stuck-red-flag",
    "SOURCEA_ANTI_POISON_ENGINE_V2",
    "POISON_AND_REALTIME_BLOCKER_TERMINOLOGY",
    "projection_poison_sanitize",
)

SKIP_RULE_FILES = frozenset(
    {
        "034-mac-no-validator-stuck-red-flag.mdc",
        "agent-memory-mirror.mdc",
        "000-dead-law-stubs.mdc",
        "020-anti-staleness-vocabulary-key.mdc",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry() -> dict:
    if REGISTRY_PATH.is_file():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"schema": "agent-law-poison-registry-v1", "version": "1.0.0"}


def load_poison_law() -> dict:
    if POISON_LAW_PATH.is_file():
        try:
            return json.loads(POISON_LAW_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def registry_patterns(*, projection: bool = False) -> list[dict]:
    reg = load_registry()
    if projection:
        rows = list(reg.get("projection_poison_patterns") or reg.get("projection_patterns") or [])
        if rows:
            return rows
        return []
    rows = list(reg.get("poison_patterns") or [])
    if rows:
        return rows
    out: list[dict] = []
    for sub, inc in _LEGACY_SUBSTRINGS:
        out.append({"id": f"L-{sub[:8]}", "match": sub, "incident": inc, "kind": "substring"})
    for rid, pat, inc in _LEGACY_REGEX:
        out.append({"id": rid, "match": pat, "incident": inc, "kind": "regex"})
    return out


def registry_replacements(*, projection: bool = False) -> list[tuple[str, str]]:
    reg = load_registry()
    key = "projection_replacements" if projection else "text_replacements"
    raw = reg.get(key) or reg.get("replacements") or []
    out: list[tuple[str, str]] = []
    for row in raw:
        if isinstance(row, dict) and row.get("old") and row.get("new"):
            out.append((str(row["old"]), str(row["new"])))
        elif isinstance(row, (list, tuple)) and len(row) == 2:
            out.append((str(row[0]), str(row[1])))
    if projection:
        rt = reg.get("realtime_ssot") or {}
        if rt.get("form_url"):
            out.append(("http://127.0.0.1:13020/form/", str(rt["form_url"])))
        if rt.get("cockpit_url"):
            out.append(("http://127.0.0.1:13020/", str(rt["cockpit_url"])))
    return out


def scan_roots(*, projection: bool = False) -> list[Path]:
    reg = load_registry()
    key = "projection_scan_roots" if projection else "scan_roots"
    default = ["agent-control-panel"] if projection else []
    roots: list[Path] = []
    for rel in reg.get(key) or default:
        roots.append(ROOT / rel)
    return roots


def _line_is_documentation(line: str) -> bool:
    norm = re.sub(r"[*_`]", "", line).lower().strip()
    low = line.lower()
    if any(m.lower() in low for m in SKIP_LINE_MARKERS):
        return True
    if norm.startswith("#"):
        return True
    if "never describe" in norm or "never say" in norm or "never inject" in norm:
        return True
    if re.search(r"\bnever\s+(say|describe|inject|order|use)\b", norm):
        return True
    if re.search(r"\b(must\s+not|do\s+not|forbidden|retired_founder|poison\s*\(|anti.poison)\b", norm):
        return True
    if re.search(r"^\s*\|.*\b(breaks|forbidden|never|retired|wrong|poison)\b", norm):
        return True
    if re.search(r"as the design\s*\|", norm):
        return True
    return False


def scan_text(text: str, *, rel: str, projection: bool = False) -> list[dict]:
    hits: list[dict] = []
    patterns = registry_patterns(projection=projection)
    for line in text.splitlines():
        if _line_is_documentation(line):
            continue
        low = line.lower()
        for row in patterns:
            if row.get("skip_in_headers") and line.strip().startswith("#"):
                continue
            match = str(row.get("match") or "")
            kind = str(row.get("kind") or "substring")
            inc = str(row.get("incident") or "")
            pid = str(row.get("id") or "")
            if not match:
                continue
            if kind == "regex":
                if re.search(match, line, re.I):
                    hits.append(
                        {
                            "path": rel,
                            "kind": "regex",
                            "id": pid,
                            "match": match[:80],
                            "incident": inc,
                            "line": line[:120],
                            "projection": projection,
                        }
                    )
            elif match.lower() in low:
                hits.append(
                    {
                        "path": rel,
                        "kind": "substring",
                        "id": pid,
                        "match": match,
                        "incident": inc,
                        "line": line[:120],
                        "projection": projection,
                    }
                )
    return hits


def scan_file(path: Path, *, projection: bool = False) -> list[dict]:
    if not path.is_file():
        return []
    rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    if any(s in rel for s in SKIP_PATH_PARTS):
        return []
    if path.name in SKIP_RULE_FILES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return scan_text(text, rel=rel, projection=projection)


def _iter_scan_files(base: Path) -> list[Path]:
    if base.is_file():
        return [base]
    if not base.is_dir():
        return []
    if base.name == "rules":
        return [p for p in base.glob("*.mdc") if p.is_file()]
    if base.name == "enforcement":
        return [p for p in base.glob("*.md") if p.is_file()]
    if base.name == "agent-control-panel":
        files = list(base.glob("command-data*.json"))
        boot = base / "worker-hub" / "boot.json"
        if boot.is_file():
            files.append(boot)
        return files
    out: list[Path] = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in (".mdc", ".md", ".json", ".py"):
            out.append(path)
    return out


def scan_repo(*, projection: bool = False) -> list[dict]:
    hits: list[dict] = []
    reg = load_registry()
    for base in scan_roots(projection=projection):
        for path in _iter_scan_files(base):
            hits.extend(scan_file(path, projection=projection))
    if not projection:
        for rel in reg.get("scan_files") or []:
            hits.extend(scan_file(ROOT / rel, projection=False))
        mirror = SINA / "agent-memory-mirror-v1.json"
        if mirror.is_file():
            try:
                inj = json.loads(mirror.read_text(encoding="utf-8")).get("inject") or {}
                blob = json.dumps(inj, ensure_ascii=False)
                hits.extend(scan_text(blob, rel="~/.sina/agent-memory-mirror-v1.json inject"))
            except (OSError, json.JSONDecodeError):
                pass
    return hits


def apply_text_replacements(text: str, *, projection: bool = False) -> tuple[str, int]:
    n = 0
    for old, new in registry_replacements(projection=projection):
        if old in text:
            text = text.replace(old, new)
            n += 1
    return text, n


def sanitize_projection_file(path: Path, *, dry_run: bool = False) -> dict:
    if not path.is_file():
        return {"path": str(path), "ok": True, "skipped": "missing", "changes": 0}
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"path": str(path), "ok": False, "error": str(exc)[:120], "changes": 0}
    new_raw, n = apply_text_replacements(raw, projection=True)
    if n and not dry_run:
        path.write_text(new_raw, encoding="utf-8")
    return {"path": str(path), "ok": True, "changes": n, "dry_run": dry_run}


def check_positive_inject(inject: dict) -> dict[str, Any]:
    law = load_poison_law()
    required = list(law.get("mirror_must_inject") or [])
    violations: list[str] = []
    blob = json.dumps(inject or {}, ensure_ascii=False).lower()
    for key in required:
        if key.replace("_", " ") not in blob and key not in blob:
            violations.append(f"missing_positive:{key}")
    forbidden_prefixes = ("never_", "forbidden_", "prohibition_")
    for k in (inject or {}):
        if any(str(k).startswith(p) for p in forbidden_prefixes):
            violations.append(f"forbidden_key:{k}")
    return {"ok": len(violations) == 0, "violations": violations}


def ship_window_active() -> bool:
    return (SINA / "asf-ship-window-v1.flag").is_file()


def mac_founder_session() -> bool:
    return (SINA / "mac-control-plane-v1.flag").is_file()
