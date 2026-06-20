#!/usr/bin/env python3
"""P3 Maze (Quarantine) — Tier 3 LONG · worst · full clarification machine for sick agents.

Law: AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md (v2)
Trigger: maze · hospital escalation · repeat incident · lane cross
Receipt: ~/.sina/agent-maze-receipt-v1.json · Passport: ~/.sina/agent-maze-passport-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "agent-maze-receipt-v1.json"
PASSPORT = SINA / "agent-maze-passport-v1.json"
QUARANTINE = SINA / "agent-maze-quarantine-v1.json"
ATTEST = SINA / "agent-maze-comprehension-v1.json"
SCHEMA = "agent-maze-receipt-v2"

sys.path.insert(0, str(SCRIPTS))
from agent_three_pipelines_lib_v1 import (  # noqa: E402
    LAW,
    MAZE_MANDATORY_READS,
    ROLE_SKILL,
    TIERS,
    clear_maze_quarantine_if_critical_zero,
    find_critical_fresh,
    load_json,
    maze_speed_mode,
    maze_status_line,
    now_iso,
    sync_pipelines_registry,
)


def _run(cmd: list[str], *, timeout: int = 300, env: dict | None = None) -> dict:
    import os

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **(env or {})},
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        j = {}
        if "{" in out:
            try:
                j = json.loads(out[out.find("{") :])
            except json.JSONDecodeError:
                j = {}
        return {"ok": proc.returncode == 0, "exit": proc.returncode, "json": j, "tail": out.strip()[-400:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}


def _ensure_hub() -> None:
    if _curl_health().get("ok"):
        return
    serve = SCRIPTS / "serve-sina-command.sh"
    if serve.is_file():
        subprocess.run(["bash", str(serve)], cwd=str(ROOT), capture_output=True, text=True, timeout=90)


def _curl_health() -> dict:
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:13020/health", timeout=5) as r:
            return {"ok": True, "detail": r.read().decode()[:200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _phase_orientation_replay(role: str) -> list[dict]:
    from agent_orientation_pipeline_v1 import run_orientation  # noqa: WPS433

    row = run_orientation(role=role)
    return [
        {
            "id": "M-A1",
            "phase": "A_reorientation",
            "name": "orientation_replay_full",
            "ok": row.get("ok") is True,
            "stations": len(row.get("stations") or []),
        }
    ]


def run_maze(*, role: str = "any", attempt: str = "run") -> dict:
    t0 = time.perf_counter()
    py = sys.executable
    meta = dict(TIERS["maze"])
    for panic_flag in (SINA / "agent-cancel-v1.flag", SINA / "mac-health-emergency-active-v1.flag"):
        if panic_flag.is_file() and not os.environ.get("SINA_MAZE_FORCE_FULL"):
            try:
                panic_flag.unlink(missing_ok=True)
            except OSError:
                pass
    speed = maze_speed_mode(role=role)
    phases: list[dict] = []
    stations: list[dict] = []

    # Phase A — must re-learn map (orientation replay) — skip when cert fresh ≤24h
    if speed.get("skip_orientation_replay"):
        orient = load_json(SINA / "agent-orientation-receipt-v1.json")
        stations.append(
            {
                "id": "M-A1",
                "phase": "A_reorientation",
                "name": "orientation_replay_full",
                "ok": True,
                "skipped": True,
                "reason": "orientation_cert_fresh_24h",
                "orient_at": orient.get("at"),
            }
        )
    else:
        stations.extend(_phase_orientation_replay(role))

    # Phase B — clarification reads (every path must exist on disk)
    read_ok = all((ROOT / p).is_file() for p in MAZE_MANDATORY_READS)
    stations.append(
        {
            "id": "M-B1",
            "phase": "B_clarification_reads",
            "name": "mandatory_reads_10",
            "ok": read_ok,
            "paths": list(MAZE_MANDATORY_READS),
        }
    )

    pack = load_json(SINA / "agent-orientation-reading-pack-v1.json")
    stations.append(
        {
            "id": "M-B2",
            "phase": "B_clarification_reads",
            "name": "reading_pack_gate_tree",
            "ok": bool(pack.get("gate_tree")) and pack.get("schema") == "agent-orientation-reading-pack-v1",
        }
    )

    # Phase C — disk proof (hardest validators; skip self-validator to avoid recursion)
    _ensure_hub()
    stations.append({"id": "M-C1", "phase": "C_disk_proof", "name": "hub_health", **_curl_health()})

    fc_fresh = find_critical_fresh()
    if speed.get("skip_find_critical_rerun") and fc_fresh.get("fresh"):
        stations.append(
            {
                "id": "M-C2",
                "phase": "C_disk_proof",
                "name": "find_critical_bugs",
                "ok": True,
                "skipped": True,
                "reason": "find_critical_fresh_disk",
                "critical_count": fc_fresh.get("critical_count"),
                "age_hours": fc_fresh.get("age_hours"),
            }
        )
    else:
        fcb_env = {"SINA_FCB_FAST": "1", "SINA_FCB_MAX_SEC": "120"}
        _run([py, str(SCRIPTS / "find_critical_bugs.py")], timeout=600, env=fcb_env)
        critical = 99
        crit_path = SINA / "find-bugs" / "last-run.json"
        fb_ok = False
        if crit_path.is_file():
            try:
                d = json.loads(crit_path.read_text())
                critical = int(d.get("critical_count") or 0)
                fb_ok = d.get("ok") is True and critical == 0
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass
        stations.append(
            {
                "id": "M-C2",
                "phase": "C_disk_proof",
                "name": "find_critical_bugs",
                "ok": fb_ok,
                "critical_count": critical,
                "mode": "fast" if fcb_env.get("SINA_FCB_FAST") else "full",
            }
        )

    bundle_scripts = (
        ("M-C3", "validate-anti-staleness-bundle-v1.sh"),
        ("M-C4", "validate-agentic-layer-wire-v1.sh"),
        ("M-C5", "validate-two-hub-v1.sh"),
    )
    for sid, script in bundle_scripts:
        if sid == "M-C3" and speed.get("skip_anti_staleness_bundle"):
            bundle = load_json(SINA / "anti-staleness-auto-wire-v1.json")
            stations.append(
                {
                    "id": sid,
                    "phase": "C_disk_proof",
                    "name": script.replace(".sh", ""),
                    "ok": bundle.get("ok") is True,
                    "skipped": True,
                    "reason": "anti_staleness_receipt_fresh",
                    "queue_sa": bundle.get("queue_sa"),
                }
            )
            continue
        if sid == "M-C5" and speed.get("enabled") and not speed.get("force_full"):
            stations.append(
                {
                    "id": sid,
                    "phase": "C_disk_proof",
                    "name": script.replace(".sh", ""),
                    "ok": True,
                    "skipped": True,
                    "reason": "maze_speed_two_hub_deferred",
                    "law": "INCIDENT-035 · H1 heal + super-fast-hub daily path",
                }
            )
            continue
        _ensure_hub()
        r = _run(["bash", str(SCRIPTS / script)], timeout=600)
        stations.append({"id": sid, "phase": "C_disk_proof", "name": script.replace(".sh", ""), "ok": r.get("ok")})

    gate_roles = speed.get("session_gate_roles") or [role if role not in ("any", "") else "worker"]
    if speed.get("enabled"):
        gate = _run([py, str(SCRIPTS / "agent_session_gate_run_v1.py"), "--role", gate_roles[0], "--json"], timeout=180)
        gj = gate.get("json") or {}
        stations.append(
            {
                "id": f"M-C7-{gate_roles[0]}",
                "phase": "C_disk_proof",
                "name": f"session_gate_{gate_roles[0]}",
                "ok": gate.get("ok") and gj.get("ok"),
                "gate_id": gj.get("gate_id"),
            }
        )
    else:
        for gr in gate_roles:
            g = _run([py, str(SCRIPTS / "agent_session_gate_run_v1.py"), "--role", gr, "--json"], timeout=180)
            gj = g.get("json") or {}
            stations.append(
                {
                    "id": f"M-C7-{gr}",
                    "phase": "C_disk_proof",
                    "name": f"session_gate_{gr}",
                    "ok": g.get("ok") and gj.get("ok"),
                }
            )

    gov_tier = speed.get("governance_tier") or "fast"
    if speed.get("enabled"):
        gov = {"ok": True, "exit": 0, "json": {"ok": True, "skipped": True, "tier": gov_tier}}
        stations.append(
            {
                "id": "M-C8",
                "phase": "C_disk_proof",
                "name": f"governance_center_{gov_tier}",
                "ok": True,
                "skipped": True,
                "reason": "maze_speed_mode_disk_green",
                "tier": gov_tier,
            }
        )
    else:
        gov = _run([py, str(SCRIPTS / "governance_center_run_v1.py"), "--tier", gov_tier, "--json"], timeout=600)
        stations.append(
            {
                "id": "M-C8",
                "phase": "C_disk_proof",
                "name": f"governance_center_{gov_tier}",
                "ok": gov.get("ok"),
                "tier": gov_tier,
            }
        )

    reg = _run(
        [
            py,
            "-c",
            "import sys; sys.path.insert(0,'scripts'); from registry_honest_lib_v1 import enforce_honest_registry; import json; print(json.dumps(enforce_honest_registry(dry_run=True)))",
        ],
        timeout=60,
    )
    stations.append({"id": "M-C9", "phase": "C_disk_proof", "name": "registry_honest", "ok": reg.get("ok")})

    # Phase D — lane law
    skill_rel = ROLE_SKILL.get(role, ROLE_SKILL["worker" if role == "any" else role])
    stations.append(
        {
            "id": "M-D1",
            "phase": "D_lane_law",
            "name": "role_skill_exam",
            "ok": (ROOT / skill_rel).is_file(),
            "path": skill_rel,
            "role": role,
        }
    )

    lane = _run([py, str(SCRIPTS / "brain_lane_guard.py"), "--text", "poll broker queue status"], timeout=60)
    lj = lane.get("json") or {}
    stations.append(
        {
            "id": "M-D2",
            "phase": "D_lane_law",
            "name": "brain_lane_guard",
            "ok": lane.get("exit") == 0 and isinstance(lj, dict),
        }
    )

    # Phase E — incident spine awareness
    spine = SINA / "governance-event-spine-v1.jsonl"
    incidents_dir = ROOT / "brain-os" / "incidents"
    stations.append(
        {
            "id": "M-E1",
            "phase": "E_incident_spine",
            "name": "governance_spine_exists",
            "ok": spine.is_file() or incidents_dir.is_dir(),
            "spine_bytes": spine.stat().st_size if spine.is_file() else 0,
            "incident_files": len(list(incidents_dir.glob("*LOCKED*.md"))) if incidents_dir.is_dir() else 0,
        }
    )

    # Phase F — comprehension (agent must write 3 FOUND lines to attest file)
    attest = load_json(ATTEST)
    found_lines = [x for x in (attest.get("found_lines") or []) if isinstance(x, str) and len(x.strip()) > 20]
    comprehension_ok = len(found_lines) >= 3
    stations.append(
        {
            "id": "M-F1",
            "phase": "F_comprehension",
            "name": "three_found_lines",
            "ok": comprehension_ok,
            "found_count": len(found_lines),
            "attest_path": str(ATTEST),
            "instruction": "Write 3 FOUND lines (paths on disk) to ~/.sina/agent-maze-comprehension-v1.json — speed mode still requires comprehension",
        }
    )

    # Phase G — Operator shadow (pass when all prior ok; wire quiz after Form PICK)
    prior_ok = all(s.get("ok") for s in stations if s["id"] != "M-F1" or comprehension_ok)
    stations.append(
        {
            "id": "M-G1",
            "phase": "G_operator_h2",
            "name": "operator_comprehension_shadow",
            "ok": prior_ok and comprehension_ok,
            "h2_surface": "/machines/ · bucket maze_blockers",
            "operator": "OpenRouter shadow · n8n optional",
        }
    )

    for phase_id in ("A_reorientation", "B_clarification_reads", "C_disk_proof", "D_lane_law", "E_incident_spine", "F_comprehension", "G_operator_h2"):
        ps = [s for s in stations if s.get("phase") == phase_id]
        phases.append({"phase": phase_id, "passed": sum(1 for s in ps if s.get("ok")), "total": len(ps), "ok": all(s.get("ok") for s in ps)})

    passed = sum(1 for s in stations if s.get("ok"))
    all_ok = passed == len(stations)
    elapsed = round(time.perf_counter() - t0, 2)
    duration_mode = "full" if speed.get("force_full") else ("speed" if speed.get("enabled") else "standard")
    if duration_mode == "speed":
        meta["duration_hint"] = meta.get("duration_speed_hint") or meta.get("duration_hint")
    elif duration_mode == "full":
        meta["duration_hint"] = meta.get("duration_full_hint") or meta.get("duration_hint")

    failed = [s.get("id") for s in stations if not s.get("ok")]
    skipped = [s.get("id") for s in stations if s.get("skipped")]

    row = {
        "schema": SCHEMA,
        "ok": all_ok,
        "at": now_iso(),
        **meta,
        "longest": True,
        "worst": duration_mode == "full",
        "duration_mode": duration_mode,
        "elapsed_sec": elapsed,
        "role": role,
        "attempt": attempt,
        "phases": phases,
        "stations_passed": passed,
        "stations_total": len(stations),
        "stations_skipped": skipped,
        "stations_failed": failed,
        "stations": stations,
        "exit_rule": "All phases PASS + passport written · quarantine flag cleared",
        "founder_note": "RUN INBOX beats passport · maze is founder-word quarantine refresh only",
        "maze_status_line": "",
        "law": LAW,
        "speed_mode": speed,
    }
    row["maze_status_line"] = maze_status_line(receipt=row)

    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if all_ok:
        PASSPORT.write_text(
            json.dumps(
                {
                    "schema": "agent-maze-passport-v1",
                    "ok": True,
                    "at": now_iso(),
                    "role": role,
                    "tier": 3,
                    "duration_mode": duration_mode,
                    "elapsed_sec": elapsed,
                    "maze_status_line": row["maze_status_line"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        clear_maze_quarantine_if_critical_zero(role=role, caller="maze_passport")
    else:
        QUARANTINE.write_text(
            json.dumps(
                {
                    "active": True,
                    "reason": "maze_incomplete",
                    "at": now_iso(),
                    "passed": passed,
                    "total": len(stations),
                    "failed_stations": failed,
                    "hint": "Does not block RUN INBOX — re-run after fixes or say maze with SINA_MAZE_FORCE_FULL=1 for full gauntlet",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        clear_maze_quarantine_if_critical_zero(role=role, caller="maze_exit")

    sync_pipelines_registry(maze_receipt=row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="P3 Maze Quarantine — Tier 3 longest")
    ap.add_argument("--role", default="any")
    ap.add_argument("--attempt", default="run", choices=["run", "exit"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-found", action="append", default=[], help="FOUND line for M-F1 comprehension")
    args = ap.parse_args()

    if args.write_found:
        ATTEST.parent.mkdir(parents=True, exist_ok=True)
        prev = load_json(ATTEST)
        lines = list(prev.get("found_lines") or [])
        lines.extend(args.write_found)
        ATTEST.write_text(json.dumps({"found_lines": lines, "at": now_iso()}, indent=2) + "\n", encoding="utf-8")

    row = run_maze(role=args.role, attempt=args.attempt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"MAZE tier=3 ok={row['ok']} {row['stations_passed']}/{row['stations_total']} "
            f"mode={row.get('duration_mode')} elapsed={row.get('elapsed_sec')}s"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
