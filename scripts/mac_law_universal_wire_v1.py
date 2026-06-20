#!/usr/bin/env python3
"""Mac Law universal wire — all agents · nodes · pipelines · anti-drift · anti-staleness · anti-fragmentation.

SSOT: data/mac-law-universal-wire-v1.json
Receipt: ~/.sina/mac-law-universal-wire-receipt-v1.json
Law: Mac Law boss order — Mac control panel · cloud executes
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "mac-law-universal-wire-v1.json"
RECEIPT = SINA / "mac-law-universal-wire-receipt-v1.json"


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


def _grep_file(path: Path, needle: str) -> bool:
    if not path.is_file():
        return False
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _wire_nodes(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    rows: dict = {}
    wires = {
        "session_gate": ("scripts/agent_session_gate_run_v1.py", "mac_law_universal_wire"),
        "conduct_gate": ("scripts/agentic_conduct_gate_v1.py", "mac_law_machine"),
        "pre_write_guard": ("scripts/pre_write_guard_v1.py", "mac_law_universal"),
        "memory_mirror": ("scripts/agent_memory_mirror_v1.py", "mac_law_universal"),
    }
    for node in ssot.get("agent_nodes") or []:
        nid = str(node.get("id") or "")
        rows[nid] = {"ok": True, "required": node.get("required", True)}
        if nid in wires:
            rel, needle = wires[nid]
            ok = _grep_file(ROOT / rel, needle)
            rows[nid]["wired"] = ok
            if node.get("required") and not ok:
                issues.append(f"node_unwired:{nid}")
                rows[nid]["ok"] = False
    return issues, rows


def _triple_sync(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    chain: dict = {}

    asw = _read(_expand("~/.sina/anti-staleness-auto-wire-v1.json"))
    as_ok = bool(asw.get("ok", True)) if asw else True
    chain["anti_staleness"] = {"ok": as_ok, "queue_sa": asw.get("queue_sa")}
    if asw and not as_ok:
        issues.append("anti_staleness:RED")

    vocab_path = SCRIPTS / "validate-anti-staleness-vocabulary-gate-v1.sh"
    chain["vocabulary"] = {"validator_exists": vocab_path.is_file()}
    if not vocab_path.is_file():
        issues.append("vocabulary:validator_missing")

    drift = _read(_expand("~/.sina/governance_drift_report_v1.json"))
    min_score = int((ssot.get("triple_sync") or {}).get("zero_drift", {}).get("min_drift_score") or 85)
    drift_score = drift.get("drift_score")
    drift_items = drift.get("drift_items")
    if isinstance(drift_items, list):
        drift_count = len(drift_items)
    elif isinstance(drift_items, dict):
        drift_count = len(drift_items)
    else:
        drift_count = drift.get("cross_layer", {}).get("drift_items", 0) if isinstance(drift.get("cross_layer"), dict) else 0
    drift_ok = True
    if drift_score is not None and int(drift_score) < min_score:
        drift_ok = False
        issues.append(f"zero_drift:score_below_{min_score}")
    if drift_count and int(drift_count) > 0:
        drift_ok = False
        issues.append("zero_drift:items_nonzero")
    chain["zero_drift"] = {"ok": drift_ok, "drift_score": drift_score, "drift_items": drift_count}

    frag_ok = True
    queue_values: list[str] = []
    for rel in (ssot.get("triple_sync") or {}).get("anti_fragmentation", {}).get("receipts") or []:
        row = _read(_expand(str(rel)))
        sa = str(row.get("queue_sa") or row.get("meta", {}).get("sa_id") or "")
        if sa:
            queue_values.append(sa)
    unique = set(queue_values)
    if len(unique) > 1:
        frag_ok = False
        issues.append("anti_fragmentation:queue_sa_mismatch")
    chain["anti_fragmentation"] = {"ok": frag_ok, "queue_sa_values": list(unique), "sources": len(queue_values)}

    return issues, chain


def _mac_law_stack(ssot: dict) -> tuple[list[str], dict]:
    issues: list[str] = []
    stack: dict = {}
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    try:
        from mac_law_mandatory_v1 import assess as mandatory_assess  # noqa: WPS433

        m = mandatory_assess()
        stack["mandatory"] = {"ok": m.get("ok"), "line": m.get("line")}
        if not m.get("ok"):
            issues.extend(f"mandatory:{x}" for x in (m.get("issues") or [])[:5])
    except Exception as exc:
        issues.append(f"mandatory_load:{exc}")
        stack["mandatory"] = {"ok": False, "error": str(exc)[:80]}

    try:
        from mac_law_machine_enforce_v1 import assess as machine_assess  # noqa: WPS433

        ml = machine_assess()
        stack["machine"] = {"ok": ml.get("ok"), "line": ml.get("line")}
        if not ml.get("ok"):
            issues.extend(f"machine:{x}" for x in (ml.get("issues") or [])[:5])
    except Exception as exc:
        issues.append(f"machine_load:{exc}")
        stack["machine"] = {"ok": False, "error": str(exc)[:80]}

    fem = _read(ROOT / "data/founder-execution-model-v1.json")
    mer = _read(ROOT / "data/machine-execution-plane-registry-v1.json")
    mac_role_f = (fem.get("mac_role") or {}).get("canonical") if isinstance(fem.get("mac_role"), dict) else fem.get("mac_role")
    mac_role_m = mer.get("mac_role")
    role_ok = mac_role_f == mac_role_m == "control_plane_only"
    stack["execution_plane"] = {"mac_role_fem": mac_role_f, "mac_role_mer": mac_role_m, "ok": role_ok}
    if not role_ok:
        issues.append("execution_plane:mac_role_drift")

    return issues, stack


def scan_text(text: str) -> dict:
    ssot = load_ssot()
    hits: list[dict] = []
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    try:
        from mac_law_machine_enforce_v1 import scan_agent_text  # noqa: WPS433

        ml = scan_agent_text(text)
        hits.extend(ml.get("hits") or [])
    except Exception:
        pass
    for pat in ssot.get("forbidden_mac_execution_patterns") or []:
        if pat and re.search(str(pat), text or "", re.I):
            hits.append({"id": f"forbidden_pattern:{pat[:24]}", "because": "Mac Law universal — cloud executes"})
    return {"ok": not hits, "hits": hits}


def check_pre_write(*, path: str) -> dict:
    low = (path or "").lower()
    blockers: list[str] = []
    if "autorun-worker" in low and "archive" not in low:
        blockers.append("MAC_LAW_FORBIDDEN_AUTORUN_PATH")
    if re.search(r"com\.sourcea\.autorun", low):
        blockers.append("MAC_LAW_FORBIDDEN_AUTORUN_LAUNCH")
    cp = _expand("~/.sina/mac-control-plane-v1.flag")
    if not cp.is_file():
        blockers.append("MAC_CONTROL_PLANE_FLAG_MISSING")
    return {"ok": not blockers, "blockers": blockers, "path": path}


def assess(*, sync_children: bool = False) -> dict:
    ssot = load_ssot()
    issues: list[str] = []
    if not ssot:
        issues.append("missing_ssot")

    node_issues, nodes = _wire_nodes(ssot) if ssot else ([], {})
    issues.extend(node_issues)
    sync_issues, triple = _triple_sync(ssot) if ssot else ([], {})
    issues.extend(sync_issues)
    stack_issues, mac_stack = _mac_law_stack(ssot) if ssot else ([], {})
    issues.extend(stack_issues)

    if sync_children:
        for cmd in (
            [sys.executable, str(SCRIPTS / "mac_law_machine_enforce_v1.py"), "--sync-receipt", "--json"],
            [sys.executable, str(SCRIPTS / "mac_law_mandatory_v1.py"), "--sync-receipt", "--json"],
            [sys.executable, str(SCRIPTS / "mac_law_agent_execution_plane_lock_v1.py"), "--sync-receipt", "--json"],
        ):
            subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=30)

    ok = not issues
    line = (
        f"mac-law-universal · nodes={'PASS' if not node_issues else 'RED'} · "
        f"triple={'PASS' if not sync_issues else 'RED'} · stack={'PASS' if not stack_issues else 'RED'} · "
        f"ok={'PASS' if ok else 'RED'}"
    )
    return {
        "ok": ok,
        "issues": issues,
        "line": line,
        "one_law": ssot.get("one_law"),
        "nodes": nodes,
        "triple_sync": triple,
        "mac_law_stack": mac_stack,
    }


def inject_slice() -> dict:
    row = _read(RECEIPT) or assess()
    ssot = load_ssot()
    return {
        "one_law": ssot.get("one_law"),
        "line": row.get("line"),
        "boss_order": ssot.get("boss_order"),
        "mac_role": "control_plane_only",
        "cloud_executes": True,
        "triple_sync_law": "anti_staleness + vocabulary paired · zero_drift session · queue_sa anti-fragmentation",
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def _patch_surfaces(row: dict) -> None:
    surf_path = SINA / "agent-live-surfaces-v1.json"
    patch = {
        "mac_law_universal_line": row.get("line"),
        "mac_law_universal_wire": {"ok": row.get("ok"), "ssot": "data/mac-law-universal-wire-v1.json"},
    }
    base = _read(surf_path) if surf_path.is_file() else {}
    if not isinstance(base, dict):
        base = {}
    base.update({k: v for k, v in patch.items() if v is not None})
    SINA.mkdir(parents=True, exist_ok=True)
    tmp = surf_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(base, indent=2) + "\n", encoding="utf-8")
    tmp.replace(surf_path)


def sync_receipt(*, enforce: bool = False, full_stack_sync: bool = False) -> dict:
    row = assess(sync_children=full_stack_sync)
    receipt = {"schema": "mac-law-universal-wire-receipt-v1", "saved_at": _now(), **row}
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _patch_surfaces(row)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Mac Law universal wire v1")
    ap.add_argument("--assess", action="store_true")
    ap.add_argument("--sync-receipt", action="store_true")
    ap.add_argument("--enforce", action="store_true", help="Legacy alias — no nested child sync (use --full-stack-sync for CI)")
    ap.add_argument(
        "--full-stack-sync",
        action="store_true",
        help="Cloud CI / ship window only — sync child Mac Law receipts (forbidden Mac founder session)",
    )
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--scan-text", default="")
    ap.add_argument("--check-pre-write", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.inject:
        row = inject_slice()
    elif args.scan_text:
        row = scan_text(args.scan_text)
    elif args.check_pre_write:
        row = check_pre_write(path=args.check_pre_write)
    elif args.sync_receipt:
        row = sync_receipt(enforce=args.enforce, full_stack_sync=args.full_stack_sync)
    else:
        row = assess()

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("line") or row.get("one_law") or json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
