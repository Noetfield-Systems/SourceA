#!/usr/bin/env python3
"""Unified research root — register artifacts, rebuild INDEX + filtered core digests."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path.home() / ".sina" / "research-root"
REGISTRY = ROOT / "registry.jsonl"
INDEX = ROOT / "INDEX.yaml"
FILTERED = ROOT / "filtered"

VAULT_GLOBS = [
    Path.home() / ".sina/agent-workspaces/research-acquisitor/briefs",
    Path.home() / ".sina/agent-workspaces/research-acquisitor/lane-imports",
    Path.home() / ".sina/agent-workspaces/trustfield/commercial-goal",
    Path.home() / ".sina/agent-workspaces/noetfield_local/legal-goal",
    Path.home() / "Desktop/Cursor OS Pro/docs/research",
]

# Machine truth JSON (lane research — register as artifacts, not duplicated)
LANE_JSON_ARTIFACTS = [
    Path.home() / "Desktop/Cursor OS Pro/scripts/investor-data-200.json",
    Path.home() / "Desktop/Cursor OS Pro/scripts/canada-voice-100.json",
]

COMMERCIAL_KEYS = ("roi", "pricing", "gtm", "revenue", "vertical", "offer", "channel", "iap", "arr")
GOVERNANCE_KEYS = ("constraint", "legal", "risk", "compliance", "block", "msa", "dpa", "rpaa", "liability")
RESEARCH_KEYS = ("gap", "sector", "competitor", "landscape", "source", "confidence", "bucket")
ROUTING_DIGEST_FILES = frozenset({"execution_core.digest.yaml", "commercial.signal.yaml"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ensure() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    FILTERED.mkdir(parents=True, exist_ok=True)


def _append_registry(row: dict[str, Any]) -> None:
    _ensure()
    with REGISTRY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_registry() -> list[dict[str, Any]]:
    if not REGISTRY.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _canonical_registry_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """One INDEX row per artifact_path — prefer cursor_os_pro, then latest at (CIR-COSPRO dedup)."""
    by_path: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        path = str(row.get("artifact_path") or "").strip()
        if path:
            by_path.setdefault(path, []).append(row)
    canonical: list[dict[str, Any]] = []
    superseded: list[str] = []
    for path, group in by_path.items():
        cospro = [r for r in group if r.get("producer") == "cursor_os_pro"]
        pick_from = cospro if cospro else group
        winner = max(pick_from, key=lambda r: str(r.get("at") or ""))
        canonical.append(winner)
        for r in group:
            rid = str(r.get("id") or "")
            if rid and rid != winner.get("id"):
                superseded.append(rid)
    return canonical, superseded


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"raw": data}
    except Exception:
        return {}


def _text_blob(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, default=str).lower()


def _stub_ratio(items: list[str]) -> float:
    if not items:
        return 1.0
    stubs = sum(
        1
        for item in items
        if ": registered" in item.lower()
        or item.lower().startswith("total_artifacts")
        or item.lower().startswith("synced_at:")
    )
    return stubs / len(items)


def _digest_has_w123(items: list[str]) -> bool:
    blob = " ".join(items).upper()
    return "W1" in blob and "W2" in blob and "W3" in blob


def _extract_execution_routing(data: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("open_gaps", "gaps"):
        val = data.get(key)
        if isinstance(val, list):
            for item in val[:6]:
                if isinstance(item, str) and item.strip():
                    out.append(item.strip()[:280])
    findings = data.get("findings")
    if isinstance(findings, list):
        for item in findings[:4]:
            if isinstance(item, dict):
                fact = item.get("fact") or item.get("id")
                if fact:
                    out.append(str(fact)[:280])
    for block in ("w1_buyer", "w3_proof"):
        val = data.get(block)
        if isinstance(val, dict):
            for k, v in val.items():
                if v:
                    out.append(f"{block}.{k}: {v}"[:280])
    apex = data.get("apex")
    if apex:
        out.append(str(apex)[:280])
    return out


def _extract_commercial_routing(data: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("channel", "offer", "vertical", "gtm", "revenue"):
        val = data.get(key)
        if val:
            out.append(f"{key}: {v}"[:280] if (v := val) else "")
    for gap in data.get("open_gaps") or []:
        if isinstance(gap, str) and any(tag in gap.upper() for tag in ("W1", "W2", "W3")):
            out.append(gap.strip()[:280])
    return [line for line in out if line]


def _extract_lines(data: dict[str, Any], keys: tuple[str, ...], limit: int = 5) -> list[str]:
    out: list[str] = []
    blob = _text_blob(data)
    for key in ("advocacy", "constraints", "findings", "comparisons", "gaps", "proposals", "open_gaps"):
        val = data.get(key)
        if isinstance(val, list):
            for item in val[:limit]:
                if isinstance(item, str):
                    out.append(item[:240])
                elif isinstance(item, dict):
                    out.append(json.dumps(item, ensure_ascii=False, default=str)[:240])
    if len(out) < limit:
        for k, v in data.items():
            if any(x in str(k).lower() for x in keys) and v:
                out.append(f"{k}: {str(v)[:200]}")
            if len(out) >= limit:
                break
    return out[:limit]


def cmd_register(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        print(f"FAIL: not a file: {path}")
        return 1
    row = {
        "id": f"rr-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
        "at": _now(),
        "producer": args.producer,
        "lane": args.lane,
        "bucket": args.bucket,
        "artifact_path": str(path),
        "title": args.title or path.name,
        "confidence": args.confidence,
        "critic_class": args.critic_class,
        "status": "brief",
        "cores_target": [c.strip() for c in args.cores.split(",") if c.strip()],
    }
    _append_registry(row)
    print(f"OK: registered {row['id']} -> {path}")
    return 0


def _discover_artifacts() -> list[Path]:
    found: list[Path] = []
    for base in VAULT_GLOBS:
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.yaml")):
            found.append(p.resolve())
        for p in sorted(base.rglob("*.yml")):
            found.append(p.resolve())
    for p in LANE_JSON_ARTIFACTS:
        if p.is_file():
            found.append(p.resolve())
    return found


def cmd_sync(_args: argparse.Namespace) -> int:
    _ensure()
    rows = _load_registry()
    discovered = _discover_artifacts()
    known = {r.get("artifact_path") for r in rows}
    for p in discovered:
        if str(p) not in known:
            _append_registry(
                {
                    "id": f"rr-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
                    "at": _now(),
                    "producer": "auto_discover",
                    "lane": "sourcea",
                    "bucket": "market",
                    "artifact_path": str(p),
                    "title": p.name,
                    "confidence": "medium",
                    "critic_class": None,
                    "status": "brief",
                    "cores_target": ["research", "execution_core"],
                }
            )
            rows = _load_registry()

    commercial: list[str] = []
    governance: list[str] = []
    research: list[str] = []
    execution: list[str] = []

    canonical_rows, superseded_ids = _canonical_registry_rows(rows)
    dedup_note = ROOT / "CIR-COSPRO-REGISTRY-DEDUP-v1.yaml"
    if superseded_ids:
        dedup_note.write_text(
            yaml.safe_dump(
                {
                    "incident": "CIR-COSPRO-RESEARCH-SAVE-2026-06-07",
                    "updated": _now(),
                    "superseded_rr_count": len(superseded_ids),
                    "superseded_rr_ids": superseded_ids[:200],
                    "policy": "append-only registry.jsonl unchanged; INDEX uses one row per artifact_path",
                },
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

    def _row_priority(row: dict[str, Any]) -> tuple[int, str]:
        title = str(row.get("title") or "").lower()
        path = str(row.get("artifact_path") or "").lower()
        if "100m" in title or "w1/w2/w3" in title or "100m-signal" in path:
            return (0, str(row.get("at") or ""))
        if row.get("producer") == "research_acquisitor":
            return (1, str(row.get("at") or ""))
        return (2, str(row.get("at") or ""))

    artifacts_meta: list[dict[str, Any]] = []
    for row in sorted(canonical_rows, key=_row_priority):
        path = Path(row.get("artifact_path", ""))
        entry = {**row, "exists": path.is_file()}
        artifacts_meta.append(entry)
        if not path.is_file():
            continue
        data = _load_yaml(path)
        exec_routing = _extract_execution_routing(data)
        if exec_routing:
            execution.extend(exec_routing)
        else:
            execution.append(f"{row.get('producer')}/{path.name}: registered")

        comm_routing = _extract_commercial_routing(data)
        if comm_routing:
            commercial.extend(comm_routing)
        else:
            commercial.extend(_extract_lines(data, COMMERCIAL_KEYS, 2))

        governance.extend(_extract_lines(data, GOVERNANCE_KEYS, 3))
        research.extend(_extract_lines(data, RESEARCH_KEYS, 3))

    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            key = item.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(key)
        return out

    def _write_filtered(name: str, items: list[str], cap: int) -> str:
        path = FILTERED / name
        existing_items: list[str] = []
        if path.is_file():
            existing_items = list((_load_yaml(path).get("items") or []))

        items = _dedupe(items)
        action = "written"
        if name in ROUTING_DIGEST_FILES:
            new_stub = _stub_ratio(items) >= 0.6
            existing_rich = _digest_has_w123(existing_items) or (
                _stub_ratio(existing_items) < 0.4 and len(existing_items) >= 4
            )
            if new_stub and existing_rich:
                print(f"SKIP: {name} — preserve routing-grade digest ({len(existing_items)} items)")
                return "skipped"
            if existing_rich:
                merged: list[str] = []
                seen: set[str] = set()
                for line in items + existing_items:
                    if not line or line in seen:
                        continue
                    if ": registered" in line.lower():
                        continue
                    if line.lower().startswith("total_artifacts") or line.lower().startswith("synced_at:"):
                        continue
                    seen.add(line)
                    merged.append(line)
                items = merged
                action = "overlay"

        payload = {
            "updated": _now(),
            "source": "research_root_sync.py",
            "items": items[:cap],
            "rule": "digest only — drill artifact_path in registry for depth",
            "routing_grade": _digest_has_w123(items[:cap]),
        }
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return action

    comm_action = _write_filtered("commercial.signal.yaml", commercial, 8)
    _write_filtered("governance.constraints.yaml", governance, 5)
    _write_filtered("research.backlog.yaml", research, 10)
    exec_action = _write_filtered(
        "execution_core.digest.yaml",
        execution,
        12,
    )

    index = {
        "updated": _now(),
        "registry_path": str(REGISTRY),
        "filtered_dir": str(FILTERED),
        "artifact_count": len(artifacts_meta),
        "artifacts": artifacts_meta,
        "policy": "UNIFIED_RESEARCH_ROOT_LOCKED_v1.md",
    }
    INDEX.write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(
        f"OK: sync — {len(artifacts_meta)} artifacts · "
        f"execution={exec_action} commercial={comm_action} · INDEX.yaml written"
    )
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    rows = _load_registry()
    print(f"registry: {REGISTRY} ({len(rows)} rows)")
    print(f"index: {INDEX} ({'yes' if INDEX.is_file() else 'no'})")
    for name in (
        "commercial.signal.yaml",
        "governance.constraints.yaml",
        "research.backlog.yaml",
        "execution_core.digest.yaml",
    ):
        p = FILTERED / name
        print(f"  {name}: {'yes' if p.is_file() else 'no'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified research root sync")
    sub = parser.add_subparsers(dest="cmd", required=True)

    reg = sub.add_parser("register", help="Register one research artifact")
    reg.add_argument("--path", required=True)
    reg.add_argument("--producer", required=True)
    reg.add_argument("--lane", default="sourcea")
    reg.add_argument("--bucket", default="market")
    reg.add_argument("--title", default="")
    reg.add_argument("--confidence", default="medium", choices=["low", "medium", "high"])
    reg.add_argument("--critic-class", default=None, dest="critic_class")
    reg.add_argument("--cores", default="research,execution_core")
    reg.set_defaults(func=cmd_register)

    syn = sub.add_parser("sync", help="Rebuild INDEX + filtered digests")
    syn.set_defaults(func=cmd_sync)

    st = sub.add_parser("status", help="Show research root status")
    st.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
