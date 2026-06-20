#!/usr/bin/env python3
"""G7 — unified governance self-heal: scan → classify → remediate via G3/G4/S10/monitor/graph."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PANEL = ROOT / "agent-control-panel"
RECEIPT_PATH = SINA / "governance-self-heal-receipt-v1.json"
MONITOR_STATE_PATH = SINA / "governance-self-heal-monitor-v1.json"
DEFAULT_MONITOR_HEAL_INTERVAL_SEC = 1800
MONITOR_LIGHT_HEAL_SKIP = frozenset(
    {"g3_align_hub", "g3_drain", "s10_daily", "inbox_truth", "monitor_sync"}
)

sys.path.insert(0, str(SCRIPTS))

GRAPH_PATH = SINA / "governance-reference-graph-v1.json"
SPINE_PATH = SINA / "governance-event-spine-v1.jsonl"
CANONICAL_HUB = PANEL / "command-data-canonical.json"
MONITOR_PATH = SINA / "monitor-live-v1.json"
GATE_PATH = SINA / "governance-projection-gate-v1.json"
QUEUE_PATH = SINA / "governance-projection-queue-v1.jsonl"
S10_RECEIPT = SINA / "s10-eternal-receipt-v1.json"
TRUTH_PATH = SINA / "run-inbox-disk-truth-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _age_sec(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        return datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
    except OSError:
        return None


def _finding(
    *,
    check_id: str,
    status: str,
    detail: str,
    heal: str = "",
    healed: bool = False,
) -> dict:
    return {
        "id": check_id,
        "status": status,
        "detail": detail,
        "heal_action": heal,
        "healed": healed,
    }


def scan_governance_health() -> list[dict]:
    findings: list[dict] = []

    if not SPINE_PATH.is_file():
        findings.append(_finding(check_id="spine_ledger", status="FAIL", detail="missing spine ledger"))
    else:
        findings.append(_finding(check_id="spine_ledger", status="PASS", detail="spine ledger present"))

    reg = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
    try:
        reg_data = json.loads(reg.read_text(encoding="utf-8")) if reg.is_file() else {}
        if len(reg_data.get("plans") or []) != 1000:
            findings.append(
                _finding(
                    check_id="registry_json",
                    status="FAIL",
                    detail=f"REGISTRY plans={len(reg_data.get('plans') or [])}",
                    heal="repair_registry",
                )
            )
        else:
            findings.append(_finding(check_id="registry_json", status="PASS", detail="REGISTRY 1000 plans"))
    except (OSError, json.JSONDecodeError):
        findings.append(
            _finding(
                check_id="registry_json",
                status="FAIL",
                detail="REGISTRY.json corrupt",
                heal="repair_registry",
            )
        )

    if not GRAPH_PATH.is_file():
        findings.append(
            _finding(check_id="reference_graph", status="FAIL", detail="missing graph", heal="build_graph")
        )
    else:
        graph = _read(GRAPH_PATH)
        age = _age_sec(GRAPH_PATH)
        nc = int(graph.get("node_count") or 0)
        if nc < 50:
            findings.append(
                _finding(
                    check_id="reference_graph",
                    status="WARN",
                    detail=f"low node_count={nc}",
                    heal="build_graph",
                )
            )
        elif age is not None and age > 86400:
            findings.append(
                _finding(
                    check_id="reference_graph",
                    status="WARN",
                    detail=f"graph stale {int(age)}s",
                    heal="build_graph",
                )
            )
        else:
            findings.append(_finding(check_id="reference_graph", status="PASS", detail=f"nodes={nc}"))

    age = _age_sec(CANONICAL_HUB)
    if age is None:
        findings.append(
            _finding(
                check_id="canonical_hub",
                status="WARN",
                detail="command-data-canonical.json missing",
                heal="g3_align_hub",
            )
        )
    elif age > 900:
        findings.append(
            _finding(
                check_id="canonical_hub",
                status="WARN",
                detail=f"canonical hub stale {int(age)}s",
                heal="g3_align_hub",
            )
        )
    else:
        findings.append(_finding(check_id="canonical_hub", status="PASS", detail=f"age {int(age)}s"))

    gate = _read(GATE_PATH)
    if not gate:
        findings.append(
            _finding(check_id="projection_gate", status="WARN", detail="gate missing", heal="g3_authorize")
        )
    else:
        try:
            until = datetime.fromisoformat(str(gate.get("until") or "").replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > until:
                findings.append(
                    _finding(
                        check_id="projection_gate",
                        status="WARN",
                        detail="gate expired",
                        heal="g3_authorize",
                    )
                )
            else:
                findings.append(_finding(check_id="projection_gate", status="PASS", detail="gate valid"))
        except ValueError:
            findings.append(
                _finding(check_id="projection_gate", status="WARN", detail="gate bad until", heal="g3_authorize")
            )

    pending = 0
    if QUEUE_PATH.is_file():
        for line in QUEUE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                if json.loads(line).get("status") == "pending":
                    pending += 1
            except json.JSONDecodeError:
                continue
    if pending:
        findings.append(
            _finding(
                check_id="projection_queue",
                status="WARN",
                detail=f"pending_jobs={pending}",
                heal="g3_drain",
            )
        )
    else:
        findings.append(_finding(check_id="projection_queue", status="PASS", detail="queue clear"))

    mage = _age_sec(MONITOR_PATH)
    if mage is None:
        findings.append(
            _finding(check_id="monitor_mirror", status="WARN", detail="monitor-live missing", heal="monitor_sync")
        )
    elif mage > 300:
        findings.append(
            _finding(
                check_id="monitor_mirror",
                status="WARN",
                detail=f"monitor stale {int(mage)}s",
                heal="monitor_sync",
            )
        )
    else:
        findings.append(_finding(check_id="monitor_mirror", status="PASS", detail=f"age {int(mage)}s"))

    s10 = _read(S10_RECEIPT)
    if s10.get("day") != _today_utc():
        findings.append(
            _finding(
                check_id="s10_daily",
                status="WARN",
                detail=f"last s10 day={s10.get('day') or 'none'}",
                heal="s10_daily",
            )
        )
    else:
        findings.append(_finding(check_id="s10_daily", status="PASS", detail="receipt today"))

    truth = _read(TRUTH_PATH)
    inbox_match = (truth.get("inbox") or {}).get("truth_match")
    if inbox_match is False:
        findings.append(
            _finding(check_id="inbox_truth", status="WARN", detail="truth_match=false", heal="inbox_truth")
        )
    else:
        findings.append(_finding(check_id="inbox_truth", status="PASS", detail="truth ok"))

    return findings


def _apply_heal(action: str, *, dry_run: bool) -> dict:
    if dry_run:
        return {"ok": True, "action": action, "dry_run": True}
    if action == "build_graph":
        from governance_reference_graph_v1 import build_graph  # noqa: WPS433

        return {"ok": True, "action": action, "result": build_graph()}
    if action == "g3_authorize":
        from governance_projection_g3_v1 import authorize_projection_write  # noqa: WPS433

        return {
            "ok": True,
            "action": action,
            "result": authorize_projection_write(
                ["hub", "monitor", "catalog", "truth_bundle"],
                reason="g7_self_heal",
            ),
        }
    if action == "g3_align_hub":
        from governance_projection_g3_v1 import authorize_projection_write  # noqa: WPS433
        from align_command_data_ui_v1 import align_command_data_ui  # noqa: WPS433

        authorize_projection_write(["hub", "monitor", "truth_bundle"], reason="g7_self_heal")
        align_command_data_ui()
        return {"ok": True, "action": action}
    if action == "g3_drain":
        from governance_projection_g3_v1 import drain_projection_queue  # noqa: WPS433

        return {"ok": True, "action": action, "result": drain_projection_queue()}
    if action == "monitor_sync":
        from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

        return {"ok": True, "action": action, "result": sync_disk(force=True, reason="g7_self_heal")}
    if action == "s10_daily":
        from s10_eternal_audit_loop_v1 import run_loop, _day_pack  # noqa: WPS433

        return {"ok": True, "action": action, "result": run_loop(full=False, pack=_day_pack())}
    if action == "inbox_truth":
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        return {"ok": True, "action": action, "result": write_truth(sync=False)}
    if action == "repair_registry":
        from repair_sourcea_registry_v1 import repair_registry  # noqa: WPS433

        return {"ok": True, "action": action, "result": repair_registry()}
    return {"ok": False, "action": action, "error": "unknown heal action"}


def heal_findings(
    findings: list[dict],
    *,
    dry_run: bool = False,
    skip_actions: frozenset[str] | None = None,
) -> list[dict]:
    heals: list[dict] = []
    seen: set[str] = set()
    skip = skip_actions or frozenset()
    for f in findings:
        if f.get("status") not in ("WARN", "FAIL"):
            continue
        action = str(f.get("heal_action") or "")
        if not action or action in seen or action in skip:
            continue
        seen.add(action)
        try:
            res = _apply_heal(action, dry_run=dry_run)
        except Exception as exc:
            res = {"ok": False, "action": action, "error": str(exc)}
        heals.append(res)
        f["healed"] = res.get("ok", False) and not dry_run
    return heals


def run_cycle(
    *,
    heal: bool = False,
    dry_run: bool = False,
    monitor_light: bool = False,
) -> dict:
    findings = scan_governance_health()
    heal_steps: list[dict] = []
    if heal:
        skip = MONITOR_LIGHT_HEAL_SKIP if monitor_light else frozenset()
        heal_steps = heal_findings(findings, dry_run=dry_run, skip_actions=skip)

    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for f in findings:
        st = f.get("status", "WARN")
        counts[st] = counts.get(st, 0) + 1

    ok = counts.get("FAIL", 0) == 0
    receipt = {
        "schema": "governance-self-heal-receipt-v1",
        "at": _now(),
        "ok": ok,
        "heal_mode": heal,
        "dry_run": dry_run,
        "law": "brain-os/law/GOVERNANCE_SELF_HEAL_G7_LOCKED_v1.md",
        "counts": counts,
        "findings": findings,
        "heal_steps": heal_steps,
        "delegates": {
            "s10": "s10_eternal_audit_loop_v1.py",
            "conscious_recovery": "@sina-conscious-recovery",
            "g3": "governance_projection_g3_v1.py",
            "g4": "governance_replay_worker_v1.py",
        },
    }

    if heal and not dry_run and heal_steps:
        try:
            from governance_event_spine_v1 import append_event  # noqa: WPS433

            append_event(
                event_type="RECOVERY_FOUND",
                object_id="governance_self_heal_g7",
                object_kind="system",
                agent_id="maintainer",
                law_id="GOV_EVENT_SPINE",
                skill_id="governance-self-heal-g7",
                validator_set=["validate-governance-self-heal-g7-v1.sh"],
                affected_objects=["projection:hub", "projection:monitor", "projection:catalog"],
                payload={
                    "heal_count": len(heal_steps),
                    "warn": counts.get("WARN", 0),
                    "fail": counts.get("FAIL", 0),
                },
                projection_targets=["hub", "monitor", "catalog", "truth_bundle"],
                gate="governance_self_heal_daemon_v1",
                proof=str(RECEIPT_PATH),
                status="committed",
            )
        except Exception:
            pass

    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def _parse_ts(iso: str) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def maybe_run_heal_from_monitor(*, min_interval_sec: int = DEFAULT_MONITOR_HEAL_INTERVAL_SEC) -> dict | None:
    """Monitor hook — at most once per interval; heal only when WARN/FAIL with heal_action."""
    state = _read(MONITOR_STATE_PATH)
    last_at = _parse_ts(str(state.get("last_heal_at") or ""))
    now = datetime.now(timezone.utc)
    if last_at and (now - last_at).total_seconds() < min_interval_sec:
        return None

    findings = scan_governance_health()
    actionable = [
        f
        for f in findings
        if f.get("status") in ("WARN", "FAIL") and f.get("heal_action")
    ]
    if not actionable:
        return None

    try:
        receipt = run_cycle(heal=True, dry_run=False, monitor_light=True)
    except Exception as exc:
        return {"ran": True, "ok": False, "error": str(exc), "actionable": len(actionable)}
    state = {
        "schema": "governance-self-heal-monitor-v1",
        "last_heal_at": _now(),
        "last_ok": receipt.get("ok"),
        "actionable": len(actionable),
        "source": "monitor_live_sync",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    MONITOR_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return {
        "ran": True,
        "ok": receipt.get("ok"),
        "counts": receipt.get("counts"),
        "heal_steps": len(receipt.get("heal_steps") or []),
        "actionable": len(actionable),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="G7 governance self-heal daemon")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--heal", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.scan and not args.heal:
        args.scan = True

    receipt = run_cycle(heal=args.heal, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        c = receipt.get("counts") or {}
        print(
            f"G7-SELF-HEAL: ok={receipt.get('ok')} PASS={c.get('PASS')} "
            f"WARN={c.get('WARN')} FAIL={c.get('FAIL')} heal={args.heal}"
        )
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
