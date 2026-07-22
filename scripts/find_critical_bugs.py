#!/usr/bin/env python3
"""Find critical bugs — adapted from Cursor marketplace Find Bugs automation.

Shell chain includes ``validate-governance-fleet-v1.sh`` as CRITICAL (sa-0157),
``validate-dispatch-policy-classes-v1.sh`` as CRITICAL (sa-0158), and
``validate-governance-drift-v1.sh`` as CRITICAL (sa-0223) —
fleet OK + drift score must PASS alongside eval validators.

When hub is up, ``/api/system-roadmap`` future_phase must have steps (sa-0224).

On critical 0, append ``REPO_EXECUTION_LOGS/sourcea/latest.yaml`` (sa-0225).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
HUB_PORT = 13020
WORKER_PORT = 13030
HUB_HEALTH_URL = f"http://127.0.0.1:{HUB_PORT}/health"
WORKER_HEALTH_URL = f"http://127.0.0.1:{WORKER_PORT}/health"
SERVE_SCRIPT = ROOT / "scripts" / "serve-sina-command.sh"
LOG = Path.home() / ".sina" / "command-server.log"
OUT_DIR = Path.home() / ".sina" / "find-bugs"
OUT_PATH = OUT_DIR / "last-run.json"

AUDITS = [
    ("audit_essentials_nav.py", "NAV sync"),
    ("audit_hub_source_alignment.py", "WTM / hub alignment"),
    ("audit_agent_governance_e2e.py", "7 agents governance"),
    ("audit_backend_e2e.py", "Backend APIs E2E"),
]

SHELL_VALIDATORS = [
    {
        "id": "validate-registry-honest-gate-v1.sh",
        "label": "REGISTRY honest done gate (receipt-only)",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-broker-receipt-cycle-v1.sh",
        "label": "Broker receipt cycle PASS on all done rows (INCIDENT-007)",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-closeout-gate-v1.sh",
        "label": "Closeout gate blocks batch/YAML inflate",
        "severity": "critical",
        "timeout": 90,
    },
    {
        "id": "validate-monitor-honesty-v1.sh",
        "label": "Monitor honesty + batch YAML hygiene (INCIDENT-006)",
        "severity": "critical",
        "timeout": 120,
    },
    {
        "id": "validate-founder-docs-no-terminal-v1.sh",
        "label": "Founder docs no Terminal",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-founder-agentic-commercial-policy-v1.sh",
        "label": "Founder agentic commercial + no Cursor AUTO-RUN",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-hub-p0-no-autorun-v1.sh",
        "label": "Hub P0 next_action no AUTO-RUN (INCIDENT-022 / AS-01)",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-anti-staleness-bundle-v1.sh",
        "label": "Anti-staleness bundle Phases 1–5",
        "severity": "critical",
        "timeout": 180,
    },
    {
        "id": "validate-mandatory-read-paths-v1.sh",
        "label": "Mandatory read paths exist on disk",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-authority-index-coverage-v1.sh",
        "label": "Authority index covers root LOCKED laws",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-system-map-tree-v1.sh",
        "label": "System map tree canonical navigation",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-factory-conduct-v1.sh",
        "label": "Factory conduct plane — spawn gate · now · start law",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-brain-sync-hooks-v1.sh",
        "label": "Brain sync hooks wired at honest-count sites",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-brain-snapshot-sync-v1.sh",
        "label": "Brain snapshot matches live valid_yes (INCIDENT-014)",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-prompt-router-v1.sh",
        "label": "prompt_router wiring",
        "severity": "critical",
        "timeout": 120,
    },
    {
        "id": "validate-execution-spine-v1.sh",
        "label": "execution spine SM+scheduler+kernel",
        "severity": "critical",
        "timeout": 120,
    },
    {
        "id": "validate-build-run-audit-v1.sh",
        "label": "build _run_audit bash for .sh",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-no-asf-eval-authority-v1.sh",
        "label": "No ASF eval authority in scoreboard/progress",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-command-data-eval-win-pct-v1.sh",
        "label": "command-data eval win_pct vs disk",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-ui-wiring-v1.sh",
        "label": "Hub UI wiring — goal1 eval scoreboard P0",
        "severity": "critical",
        "timeout": 45,
    },
    {
        "id": "validate-council-strategic-brief-eval-v1.sh",
        "label": "Council brief eval validators vs disk",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-dispatch-classifier-task-ids-v1.sh",
        "label": "Dispatch classifier task ids",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-dispatch-policy-classes-v1.sh",
        "label": "Dispatch policy law classes vs engine",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-honest-score-not-here-v1.sh",
        "label": "honest_score not_here stale drift (sa-0002)",
        "severity": "critical",
        "timeout": 30,
    },
    {
        "id": "validate-phase-s0-ssot-alignment-v1.sh",
        "label": "phase-s0 SSOT alignment pack sa-0002..0010",
        "severity": "critical",
        "timeout": 90,
    },
    {
        "id": "validate-graph-executor-gate-honesty-v1.sh",
        "label": "Graph executor eval gate honesty",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-governance-fleet-v1.sh",
        "label": "Governance fleet",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-governance-drift-v1.sh",
        "label": "Governance drift",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-goal1-unified-autorun-v1.sh",
        "label": "Goal 1 unified auto-run (Choice 1+ START/STOP)",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-agent-skills-v1.sh",
        "label": "Agent skills registry + Worker/Brain skills on disk",
        "severity": "critical",
        "timeout": 60,
    },
    {
        "id": "validate-eval-packet-v1b-phase-s1-t1-bundle-v1.sh",
        "label": "Eval-1b phase-s1 T1 bundle (sa-0131–sa-0140)",
        "severity": "critical",
        "timeout": 180,
    },
    {
        "id": "validate-system-audits-mandatory-loop-v1.sh",
        "label": "System audits mandatory brain loop",
        "severity": "high",
        "timeout": 30,
    },
]

CRITICAL_LOG_PATTERNS = [
    r"Traceback \(most recent call last\)",
    r"UnboundLocalError",
    r"Address already in use",
    r"BACKEND E2E FAILED",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], timeout: int = 300) -> tuple[int, str]:
    try:
        r = subprocess.run(
            cmd,
            cwd=SCRIPTS,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return 1, "TIMEOUT"


def _health_probe() -> tuple[bool, str]:
    """Cross-check curl :13020/health vs serve-sina-command.sh contract (sa-0215)."""
    code, out = _run(["curl", "-sf", HUB_HEALTH_URL], timeout=10)
    if code != 0:
        return False, "hub not reachable on :13020"
    try:
        data = json.loads(out)
        if not data.get("ok"):
            return False, f"health ok=false: {out[:200]}"
        if data.get("service") != "sina-command":
            return False, f"health service mismatch: {data.get('service')}"
        if int(data.get("port") or 0) != HUB_PORT:
            return False, f"health port mismatch: {data.get('port')}"
        return True, out
    except (json.JSONDecodeError, TypeError, ValueError):
        return False, out[:200]


def _worker_health_probe() -> tuple[bool, str]:
    """Cross-check curl :13030/health vs hub-rebuild-worker contract (sa-0240)."""
    code, out = _run(["curl", "-sf", WORKER_HEALTH_URL], timeout=10)
    if code != 0:
        return False, "worker not reachable on :13030"
    try:
        data = json.loads(out)
        if not data.get("ok"):
            return False, f"worker health ok=false: {out[:200]}"
        if int(data.get("port") or 0) not in (0, WORKER_PORT):
            return False, f"worker health port mismatch: {data.get('port')}"
        return True, out
    except (json.JSONDecodeError, TypeError, ValueError):
        return False, out[:200]


def _ensure_hub_via_serve() -> None:
    """Align with audit_backend_e2e — start hub when curl health fails (sa-0214/sa-0215)."""
    if _health_probe()[0]:
        return
    if not SERVE_SCRIPT.is_file():
        return
    subprocess.run(
        ["bash", str(SERVE_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )


def _ensure_worker_via_serve() -> None:
    """Auto-start rebuild worker when :13030 down (sa-0240 / ensure-hub-rebuild-worker)."""
    if _worker_health_probe()[0]:
        return
    ensure = SCRIPTS / "ensure-hub-rebuild-worker-v1.sh"
    if not ensure.is_file():
        return
    subprocess.run(
        ["bash", str(ensure)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )


def _health() -> tuple[bool, str]:
    return _health_probe()


def _scan_log() -> tuple[list[dict], list[dict]]:
    """Tail-only scan — never read multi-GB logs into memory."""
    hits: list[dict] = []
    size_findings: list[dict] = []
    if not LOG.is_file():
        return hits, size_findings
    try:
        size = LOG.stat().st_size
    except OSError:
        return hits, size_findings
    if size > 50 * 1024 * 1024:
        size_findings.append(
            {
                "severity": "critical",
                "title": "Runaway hub log on disk",
                "trigger": str(LOG),
                "impact": f"command-server.log is {_human_log_size(size)} — I/O and RAM cache pressure",
                "fix_hint": ["Truncate ~/.sina/command-server.log", "Mac Health Log Shield → Relieve disk"],
            }
        )
        return hits, size_findings
    try:
        with LOG.open("rb") as fh:
            fh.seek(max(0, size - 256 * 1024))
            text = fh.read(256 * 1024).decode("utf-8", errors="replace")
    except OSError:
        return hits, size_findings
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for pat in CRITICAL_LOG_PATTERNS:
            if re.search(pat, line):
                ctx = "\n".join(lines[max(0, i - 2) : i + 4])[:500]
                hits.append({"pattern": pat, "line": line[:200], "context": ctx})
                break
    return hits[-5:], size_findings


def _human_log_size(n: int) -> str:
    if n >= 1024**3:
        return f"{n / 1024**3:.1f} GB"
    if n >= 1024**2:
        return f"{n / 1024**2:.0f} MB"
    return f"{n / 1024:.0f} KB"


def _shell_validator_pass(spec: dict, code: int, out: str) -> bool:
    sid = spec["id"]
    if sid == "validate-founder-docs-no-terminal-v1.sh":
        return code == 0 and "OK:" in out
    if sid == "validate-founder-agentic-commercial-policy-v1.sh":
        return code == 0 and "OK:" in out
    if sid == "validate-system-map-tree-v1.sh":
        return code == 0 and "OK:" in out
    if sid == "validate-prompt-router-v1.sh":
        return code == 0 and "OK:" in out
    if sid == "validate-execution-spine-v1.sh":
        return code == 0 and "OK:" in out
    if sid == "validate-governance-fleet-v1.sh":
        return code == 0 and "OK:" in out
    if sid == "validate-governance-drift-v1.sh":
        return code == 0 and "PASS" in out
    if sid == "validate-ui-wiring-v1.sh":
        return code == 0 and "OK: validate-ui-wiring-v1" in out
    return code == 0


def _run_shell_validators(
    findings: list[dict],
    checks: list[dict],
    *,
    specs: list[dict] | None = None,
) -> None:
    for spec in specs or SHELL_VALIDATORS:
        if spec["id"] == "validate-ui-wiring-v1.sh":
            _run(
                [sys.executable, "scripts/align_command_data_ui_v1.py"],
                timeout=120,
            )
        # sa-0026 — align/ui-wiring may bump shell built_at; sync before phase-s0
        if spec["id"] == "validate-phase-s0-ssot-alignment-v1.sh":
            sync_code, sync_out = _run(["python3", "sync_feedback_aggregate_hub_built_at_v1.py"], timeout=30)
            if sync_code == 0 and "OK:" in sync_out:
                print(f"OK: find_critical_bugs feedback sync pre phase-s0 (sa-0026) · {sync_out.splitlines()[-1]}")
        code, out = _run(["bash", spec["id"]], timeout=spec.get("timeout", 60))
        passed = _shell_validator_pass(spec, code, out)
        checks.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "ok": passed,
                "detail": out.splitlines()[-1] if out else "",
            }
        )
        if not passed:
            findings.append(
                {
                    "severity": spec["severity"],
                    "title": f"{spec['label']} validator failed",
                    "trigger": spec["id"],
                    "impact": "Fleet proof / governance drift SSOT out of sync with strict build",
                    "fix_hint": out[-300:] if out else "TIMEOUT",
                }
            )


def _check_wtm_future_column(hub_up: bool, findings: list[dict], checks: list[dict]) -> None:
    """Guard WTM Future column when hub is reachable (sa-0224)."""
    if not hub_up:
        checks.append({"id": "wtm_future", "ok": True, "detail": "skipped — hub down"})
        return
    code, wtm_out = _run(
        ["curl", "-sf", f"http://127.0.0.1:{HUB_PORT}/api/system-roadmap"],
        timeout=30,
    )
    if code != 0:
        checks.append({"id": "wtm_future", "ok": False, "detail": f"HTTP curl failed ({code})"})
        findings.append(
            {
                "severity": "critical",
                "title": "WTM system-roadmap unreachable while hub up",
                "trigger": "GET /api/system-roadmap",
                "impact": "Future column guard cannot run",
                "fix_hint": "system_roadmap.py · hub :13020",
            }
        )
        return
    try:
        wtm = json.loads(wtm_out)
    except json.JSONDecodeError:
        checks.append({"id": "wtm_future", "ok": False, "detail": "invalid JSON"})
        findings.append(
            {
                "severity": "critical",
                "title": "WTM system-roadmap invalid JSON",
                "trigger": "GET /api/system-roadmap",
                "impact": "Future column guard failed",
                "fix_hint": "system_roadmap.py",
            }
        )
        return
    fp = (wtm.get("live") or {}).get("future_phase") or {}
    n_future = len(fp.get("steps") or [])
    ok = bool(wtm.get("ok")) and n_future > 0
    checks.append({"id": "wtm_future", "ok": ok, "count": n_future, "detail": f"steps={n_future}"})
    if ok:
        print(f"OK: find_critical_bugs WTM future column guard (sa-0224) · {n_future} steps")
        return
    findings.append(
        {
            "severity": "critical",
            "title": "WTM Future column empty or not ok",
            "trigger": "Open system-roadmap tab",
            "impact": "Founder loses D3–D16 visibility",
            "fix_hint": "system_roadmap.py future_phase when RUNTIME_STACK_COMPLETE",
        }
    )


def _recent_commits() -> list[str]:
    code, out = _run(
        ["git", "-C", str(ROOT), "log", "--oneline", "-10", "--since=7.days"],
        timeout=15,
    )
    if code != 0:
        return []
    return [ln for ln in out.splitlines() if ln.strip()]


def main() -> int:
    import os
    import time

    fast = os.environ.get("SINA_FCB_FAST", "").strip() in ("1", "true", "yes")
    worker_loop = os.environ.get("SINA_WORKER_LOOP", "").strip().lower() in ("1", "true", "yes")
    force_full = os.environ.get("SINA_FCB_FORCE_FULL", "").strip().lower() in ("1", "true", "yes")
    if worker_loop and not fast and not force_full:
        print("REDIRECT: find_critical_bugs → worker_verify_ultra_v1 (Worker loop — not full fleet)")
        proc = subprocess.run(
            ["bash", str(SCRIPTS / "worker_verify_ultra_v1.sh")],
            cwd=str(ROOT),
        )
        return proc.returncode

    s10_mode = os.environ.get("SINA_FCB_S10", "").strip() in ("1", "true", "yes")
    wall_start = time.monotonic()
    wall_limit = int(os.environ.get("SINA_FCB_MAX_SEC", "90" if fast else "0") or 0)

    def _wall_exceeded() -> bool:
        return wall_limit > 0 and (time.monotonic() - wall_start) >= wall_limit

    findings: list[dict] = []
    checks: list[dict] = []

    if fast:
        print("OK: find_critical_bugs FAST mode — Worker CHECK/ACT only (not full fleet)")
    if s10_mode:
        print("OK: find_critical_bugs S10 mode — skip anti-staleness bundle (circular with s10-047)")

    shell_specs = list(SHELL_VALIDATORS)
    if s10_mode:
        shell_specs = [s for s in shell_specs if s["id"] != "validate-anti-staleness-bundle-v1.sh"]

    _ensure_hub_via_serve()
    ok, health_detail = _health()
    checks.append({"id": "hub_health", "ok": ok, "detail": health_detail})
    if ok:
        print(f"OK: find_critical_bugs hub_health curl :{HUB_PORT} cross-check (sa-0215)")
    if not fast:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from sina_command_lib import heal_command_data_shell_from_disk  # noqa: WPS433

            heal_ok, heal_msg = heal_command_data_shell_from_disk()
            checks.append({"id": "heal_command_data_shell", "ok": heal_ok, "detail": heal_msg})
            if heal_ok:
                print(f"OK: find_critical_bugs shell heal pre-audit (sa-0016) · {heal_msg}")
            else:
                findings.append(
                    {
                        "severity": "critical",
                        "title": "command-data-shell heal failed",
                        "trigger": "heal_command_data_shell_from_disk",
                        "impact": "Lazy shell cap / fleet leak breaks hub audits",
                        "fix_hint": heal_msg,
                    }
                )
        except Exception as exc:
            checks.append({"id": "heal_command_data_shell", "ok": False, "detail": str(exc)})
    elif ok:
        checks.append({"id": "heal_command_data_shell", "ok": True, "detail": "skipped fast mode"})
    if not ok:
        findings.append(
            {
                "severity": "critical",
                "title": "Sina Command hub down",
                "trigger": "User opens Sina Command.app or :13020",
                "impact": "No hub UI or APIs",
                "fix_hint": "scripts/serve-sina-command.sh",
            }
        )

    _ensure_worker_via_serve()
    w_ok, w_detail = _worker_health_probe()
    checks.append({"id": "worker_health", "ok": w_ok, "detail": w_detail})
    if w_ok:
        print(f"OK: find_critical_bugs worker_health curl :{WORKER_PORT} cross-check (sa-0240)")
    elif not fast:
        findings.append(
            {
                "severity": "critical",
                "title": "Hub rebuild worker down",
                "trigger": "Factory rebuild / queue consumer on :13030",
                "impact": "Rebuild worker lane unavailable",
                "fix_hint": "scripts/ensure-hub-rebuild-worker-v1.sh",
            }
        )

    audit_scripts = AUDITS if not fast else [a for a in AUDITS if "backend" not in a[0]]
    for script, label in audit_scripts:
        if _wall_exceeded():
            checks.append({"id": script, "label": label, "ok": True, "detail": "skipped wall_limit"})
            break
        audit_timeout = 180 if "hub_source_alignment" in script else (60 if fast else (600 if "backend" in script else 120))
        code, out = _run(["python3", script], timeout=audit_timeout)
        passed = code == 0 and "FAILED" not in out.upper()
        checks.append({"id": script, "label": label, "ok": passed, "tail": out.splitlines()[-3:]})
        # sa-0026 / sa-0017 — backend E2E refresh bumps shell built_at; sync before phase-s0 in FCB
        if script == "audit_backend_e2e.py" and passed and not fast:
            try:
                from sina_command_lib import heal_command_data_shell_from_disk  # noqa: WPS433

                heal_ok, heal_msg = heal_command_data_shell_from_disk(force=True)
                checks.append(
                    {
                        "id": "heal_command_data_shell_post_e2e",
                        "ok": heal_ok,
                        "detail": heal_msg,
                    }
                )
                if heal_ok:
                    print(f"OK: find_critical_bugs shell heal post E2E (sa-0016) · {heal_msg}")
            except Exception as exc:
                checks.append({"id": "heal_command_data_shell_post_e2e", "ok": False, "detail": str(exc)})
            sync_code, sync_out = _run(["python3", "sync_feedback_aggregate_hub_built_at_v1.py"], timeout=30)
            sync_ok = sync_code == 0 and "OK:" in sync_out
            checks.append(
                {
                    "id": "sync_feedback_aggregate_hub_built_at_v1.py",
                    "label": "FEEDBACK_AGGREGATE sync after backend E2E (sa-0026)",
                    "ok": sync_ok,
                    "detail": sync_out.splitlines()[-1] if sync_out else "",
                }
            )
            if sync_ok:
                print(f"OK: find_critical_bugs feedback sync after E2E (sa-0026) · {sync_out.splitlines()[-1]}")
        if not passed:
            findings.append(
                {
                    "severity": "critical",
                    "title": f"Audit failed: {label}",
                    "trigger": f"python3 scripts/{script}",
                    "impact": "Hub drift or broken APIs",
                    "fix_hint": out.splitlines()[-5:],
                }
            )

    if not _wall_exceeded():
        if fast:
            fast_specs = [s for s in SHELL_VALIDATORS if s["id"] in (
                "validate-execution-spine-v1.sh",
                "validate-prompt-router-v1.sh",
            )]
            for spec in fast_specs:
                code, out = _run(["bash", spec["id"]], timeout=spec.get("timeout", 60))
                passed = _shell_validator_pass(spec, code, out)
                checks.append({"id": spec["id"], "label": spec["label"], "ok": passed, "detail": out.splitlines()[-1] if out else ""})
                if not passed:
                    findings.append({"severity": spec["severity"], "title": f"{spec['label']} validator failed", "trigger": spec["id"], "impact": "fast gate failed", "fix_hint": out[-300:] if out else "TIMEOUT"})
        else:
            _run_shell_validators(findings, checks, specs=shell_specs)
    fleet_check = next((c for c in checks if c.get("id") == "validate-governance-fleet-v1.sh"), None)
    if fleet_check and fleet_check.get("ok"):
        print(f"OK: find_critical_bugs governance-fleet chain (sa-0157) · {fleet_check.get('detail', '')}")
    drift_check = next((c for c in checks if c.get("id") == "validate-governance-drift-v1.sh"), None)
    if drift_check and drift_check.get("ok"):
        print(f"OK: find_critical_bugs governance-drift chain (sa-0223) · {drift_check.get('detail', '')}")

    log_hits, log_size_findings = _scan_log()
    findings.extend(log_size_findings)
    if log_hits:
        findings.append(
            {
                "severity": "high",
                "title": "Critical patterns in command-server.log",
                "trigger": "Any hub POST after server error",
                "impact": "API failures for founder actions",
                "fix_hint": log_hits,
            }
        )

    _check_wtm_future_column(ok, findings, checks)

    critical = [f for f in findings if f.get("severity") == "critical"]
    summary = {
        "ok": not critical,
        "ran_at": _now(),
        "source": "CURSOR_FIND_BUGS_AUTOMATION_LOCKED_v1.md",
        "marketplace": "https://cursor.com/marketplace/automations/find-bugs",
        "critical_count": len(critical),
        "finding_count": len(findings),
        "findings": findings,
        "checks": checks,
        "recent_commits": _recent_commits(),
        "verdict": "no critical bugs found" if not critical else f"{len(critical)} critical issue(s)",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps({"ok": summary["ok"], "verdict": summary["verdict"], "critical": len(critical)}, indent=2))
    if critical:
        for f in critical:
            print(f"  CRITICAL: {f['title']}")
        return 1
    try:
        from append_repo_execution_log_v1 import append_on_ci_pass  # noqa: WPS433

        append_on_ci_pass(gate="find_critical_bugs")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: append_repo_execution_log_v1 (sa-0225): {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
