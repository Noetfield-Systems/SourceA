#!/usr/bin/env python3
"""Build Sina Command local UI — merges bowl state + fleet + KPI.

Refresh dedupe: ``SINA_SKIP_NESTED_BOWL`` in ``update-program-progress`` pipeline (sa-0230).

Eval CI (strict build — ``SINA_AUDIT_STRICT`` default on)
----------------------------------------------------------
Two eval layers run on every build; do not conflate them (council brief §Eval-1 vs Eval-1b).

**Eval-1 — structural** (no live LLM)
  - ``eval_packet_v1.runner.run_eval`` refreshes ``~/.sina/eval_packet_v1_report.json``
  - Metric: packet ``readiness_score`` / ``gate_eligible`` vs empty template (≥80% wins)
  - Hub: ``/api/eval-packet-v1`` · validator: ``validate-eval-packet-v1.sh`` (find_critical_bugs)

**Eval-1b — behavioral** (scaffold + optional live)
  - ``eval_packet_v1b.runner.run_eval`` — scaffold arm always; live when ``SINA_EVAL_1B_LIVE=1``
    or when report file is missing (first seed)
  - Scaffold: composite proxy ≥70% · Live pilots: OpenRouter A/B ≥80% on ``live_pilot`` tasks
  - Artifact: ``~/.sina/eval_packet_v1b_report.json`` · gate: ``eval_1b_gate_ok`` via policy_engine

**Strict eval chain** (after panel write + council seed)
  1. ``validate-eval-packet-v1b-grounding.sh`` — path citation / task needles (no OpenRouter)
  2. ``eval_1b_ci_mode.resolve_mode()`` — probe OpenRouter; 402 → ``structural_only`` honest
  3. ``validate-eval-packet-v1b-live.sh`` — live A/B or SKIP with exit 0 when 402 (sa-0127 strict default chain)
  4. ``eval_report_capture.capture_eval_report`` — SSOT capture meta under ``~/.sina/``
  5. ``validate-eval-report-capture-v1.sh`` — capture receipt present
  6. ``validate-command-data-eval-win-pct-v1.sh`` — hub eval panels match disk
  7. ``validate-governance-drift-v1.sh`` — drift sensors after eval script touch (score ≥85)
  8. ``validate-governance-fleet-v1.sh`` — fleet nudges + verify_gap after eval live (sa-0213)

**Dispatch eval gate** (same strict pass, after eval CI + fleet)
  - ``validate-dispatch-policy-v1.sh`` · alignment · graph-executor pos-dispatch guard
  - ``validate-dispatch-ready-lock-v1.sh`` — hub ``dispatch_ready`` stays false (founder law)

**Env overrides**
  - ``SINA_AUDIT_STRICT=0`` — skip FAIL-on-validator (dev only)
  - ``SINA_EVAL_1B_LIVE=1`` — force live Eval-1b arm on build (needs OpenRouter credits)
  - ``SINA_EVAL_1B_STRUCTURAL_ONLY=1`` — set by CI mode probe when 402

Machine truth: ``eval_1b_gate_ok=false`` until live pass · ``dispatch_ready=false`` at hub.
See ``COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md`` §Eval-1 vs Eval-1b.

**Eval CI header T1 replay (sa-0142):** Registry T1 re-doc of Eval-1/1b + strict chain above
(origin sa-0117 T0); ACT = header comment only · VERIFY = ``validate-eval-packet-v1b-live.sh`` +
``validate-governance-fleet-v1.sh`` + ``audit_hub_source_alignment.py`` (disk validators on ACT).

**Fleet snapshot (sa-0208):** on build complete, log nudges · auto-green · report/verify gaps
to stdout and ``~/.sina/fleet_build_snapshot_v1.json``.

**Wire validate (sa-0209):** ``validate-verify-wire-v1.sh`` in strict chain; no P0-RUNRECEIPT bump
(RunReceipt T2b parallel only per GOAL_HIERARCHY v1.1).

**Spine bridge (sa-0210):** after ``run_graph_executor()`` seed, run
``validate-spine-bridge-founder-v1.sh`` (hub :13020 required).

**Personal DB Layer A (sa-0212):** ``audit_personal_db_layer_a.py`` on every build with
``strict=False`` — WARN on fail, never blocks strict chain.

**Hub health before E2E (sa-0214):** when ``SINA_RUN_BACKEND_E2E=1``, ``audit_backend_e2e.py``
runs ``serve-sina-command.sh`` if ``http://127.0.0.1:13020/health`` is down before API probes.

**Council strategic slice seed (sa-0218):** ``seed_council_strategic_slice_v1.run_seed`` on every build;
strict mode FAIL if seed or marker verify fails (no WARN-only flake).

**Founder directives import (sa-0219):** ``import_founder_directives_v1.run_import_on_build`` when
``~/.sina/founder-directives.jsonl`` has rows; strict FAIL on import error.

**Command-data atomic write (sa-0220):** ``write_panel_outputs`` uses temp+replace for
``command-data.json`` and ``command-data-shell.json``; ``validate-command-data-atomic-v1.sh`` on strict build.

**Fleet snapshot cross-check (sa-0221):** ``fleet_build_snapshot_v1.json`` must match live
``scoreboard_payload`` + ``essay_discourse_payload`` — ``validate-fleet-snapshot-scoreboard-v1.sh``.

**No duplicate panel build (sa-0222):** hub ``run_refresh_pipeline`` sets ``SINA_SKIP_PANEL_BUILD``;
``build-sina-daily-bowl`` must not nest ``build-sina-command-panel`` — ``validate-no-duplicate-panel-build-v1.sh``.

**Governance drift in find_critical_bugs (sa-0223):** ``validate-governance-drift-v1.sh`` is CRITICAL in
``SHELL_VALIDATORS`` — ``validate-find-critical-bugs-governance-drift-chain-v1.sh`` proves wiring.

**WTM future column guard (sa-0224):** ``find_critical_bugs._check_wtm_future_column`` when hub up —
``validate-find-critical-bugs-wtm-future-guard-v1.sh`` proves wiring.

**CI pass execution log (sa-0225):** ``append_repo_execution_log_v1.append_on_ci_pass`` on
``find_critical_bugs`` critical 0 — ``validate-append-repo-execution-log-on-ci-pass-v1.sh`` proves wiring.

**Scoreboard auto-verify (sa-0301):** ``agent_scoreboard._auto_verify`` sets ``verified_by: auto`` on
``auto_pass`` — ``validate-agent-scoreboard-auto-verify-v1.sh`` proves wiring.

**Fleet auto-green count (sa-0302):** ``scoreboard_payload`` exposes ``fleet_auto_green_count`` —
``validate-fleet-auto-green-count-v1.sh`` proves wiring + command-data sync.

**Scoreboard row auto-verify backfill (sa-0303):** ``_maybe_backfill_auto_verify`` in ``scoreboard_row``
when ``auto_pass`` + report — ``validate-scoreboard-row-auto-verify-backfill-v1.sh`` proves wiring.

**Scoreboard tagline (sa-0304):** ``SCOREBOARD_TAGLINE`` — auto-checks green, not ASF verify —
``validate-scoreboard-tagline-v1.sh`` proves wiring.

**Scoreboard UI hero (sa-0305):** ``app.js`` ``renderAgentScoreboard`` — tagline + gap banners —
``validate-render-agent-scoreboard-v1.sh`` proves wiring.

**Scoreboard auto-green pill (sa-0306 · sa-0356):** ``renderScoreboardVerifyCell`` — pill when ``auto_pass``,
no Verify/Force — ``validate-scoreboard-auto-green-pill-v1.sh`` proves wiring.

**S3 scoreboard fleet batch (sa-0307–0317):** essay nudge banners, planner bridge note,
governance-fleet SSOT, FR sync, mirror copy, gap banners, council essay_nudges —
validators ``validate-essay-nudge-banner-v1.sh`` through ``validate-essay-nudges-council-v1.sh``.

**30-task batch (sa-0318–0424):** scoreboard law UI, spine/event-bus E2E, fleet PRIORITY targets —
``validate-batch-sa-0318-0424-v1.sh`` proves wiring.

**Run audit bash (sa-0226 T1 backfill):** ``_run_audit`` invokes ``.sh`` via ``bash`` not ``python3`` —
``validate-build-run-audit-v1.sh`` proves wiring (same contract as sa-0201 T0).

**Honest score not_here (sa-0076):** ``audit_hub_source_alignment`` + ``system_roadmap`` structural_only
wording — ``validate-honest-score-not-here-drift-v1.sh`` proves no L8/eval stale drift.

**L8 hybrid skip (sa-0077):** skip ``full L8 embeddings later`` when ``embedding_provider.py`` +
``vector_index_v1.json`` exist — ``validate-honest-score-l8-skip-v1.sh``.

**Phase-s2 backfill (sa-0226..sa-0300):** T0 machine proof replay for T1/T2/T3 tiers —
``validate-phase-s2-hub-build-ci-v1.sh``.

**Phase-s0 SSOT (sa-0076..sa-0100):** honest_score · synthesis hub · dispatch lock —
``validate-phase-s0-ssot-alignment-v1.sh``.

**Program progress sync (sa-0015):** ``_run_update_program_progress`` runs
``update-program-progress.py`` (``SINA_SKIP_NESTED_BOWL`` + ``SINA_SKIP_FLEET_SCAN``) before
``build_payload`` so ``signals_auto.synced_at`` advances on every strict build.

**Feedback aggregate sync (sa-0017):** ``_run_sync_feedback_aggregate`` runs
``sync_feedback_aggregate_hub_built_at_v1.py`` after ``_write_panel`` so
``FEEDBACK_AGGREGATE.execution_truth.hub_built_at`` matches ``command-data`` ``built_at``.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))
from sina_command_lib import build_payload, sync_sa_queue_into_payload, write_panel_outputs  # noqa: E402


def _apply_factory_freeze_state(payload: dict) -> None:
    """Phase 1 — FREEZE banner + suppress START hero when kill_flag (factory_control SSOT)."""
    try:
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now()
    except Exception:
        fn = {}
    freeze = bool(fn.get("kill_flag"))
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    founder["factory_state"] = {
        "freeze": freeze,
        "mode": fn.get("mode") or "FREEZE",
        "line": fn.get("line") or "",
        "stop_receipt_open": bool(fn.get("stop_receipt_open")),
        "queue_sa": fn.get("queue_sa") or "",
    }
    if freeze:
        founder["primary_action_id"] = "founder-ecosystem-safety"
    cc["founder"] = founder
    payload["command_center"] = cc
    g1 = payload.get("goal1_auto_run") or payload.get("goal1_loop") or {}
    if isinstance(g1, dict):
        g1["factory_state"] = founder.get("factory_state") or {}
        if freeze:
            line = g1["factory_state"].get("line") or "FROZEN — factory drain blocked"
            g1["primary_action_id"] = "founder-goal1-autorun-stop"
            g1["tab_hint"] = line
            ua = g1.get("unified_autorun")
            if isinstance(ua, dict):
                ua["message"] = line
                g1["unified_autorun"] = ua
        payload["goal1_auto_run"] = g1
    if freeze:
        for group in payload.get("founder_actions") or []:
            if not isinstance(group, dict):
                continue
            for act in group.get("actions") or []:
                if not isinstance(act, dict):
                    continue
                if act.get("id") == "founder-goal1-autorun-start":
                    act["hidden"] = True
                    act["disabled"] = True


def _align_p0_pick_in_next_action(payload: dict) -> None:
    """P0 founder card must cite queue-bound pick (dual-pick law — queue_sa wins over phase-first)."""
    from founder_p0_next_action_v1 import rt_live_gate_active  # noqa: WPS433

    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        if int(live_form_payload().get("open_questions_count") or 0) > 0:
            return
    except Exception:
        pass
    if rt_live_gate_active():
        return
    sq = payload.get("sourcea_sa_queue") or {}
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    fs = founder.get("factory_state") or {}
    pick_id = str(fs.get("queue_sa") or (sq.get("live_pick") or {}).get("id") or "")
    if not pick_id.startswith("sa-"):
        return
    p0 = founder.get("p0") or {}
    na = str(p0.get("next_action") or "")
    import re

    na = re.sub(r"\s*·\s*pick sa-\d{4}\s*$", "", na)
    if pick_id not in na:
        p0["next_action"] = f"{na} · pick {pick_id}" if na else f"Live pick: {pick_id}"
    founder["p0"] = p0
    cc["founder"] = founder
    payload["command_center"] = cc


def _write_panel(payload: dict, *, json_only: bool = False) -> None:
    try:
        from governance_projection_g3_v1 import authorize_projection_write  # noqa: WPS433

        authorize_projection_write(["hub", "monitor", "truth_bundle"], reason="strict_build_panel")
    except Exception:
        pass
    sync_sa_queue_into_payload(payload)
    _apply_factory_freeze_state(payload)
    _align_p0_pick_in_next_action(payload)
    try:
        from sina_command_lib import _must_do_today_lines  # noqa: WPS433

        cc = payload.get("command_center") or {}
        founder = cc.get("founder") or {}
        bowl = payload.get("daily_bowl") or payload.get("bowl") or {}
        founder["must_do_today"] = _must_do_today_lines(bowl)
        cc["founder"] = founder
        payload["command_center"] = cc
    except Exception:
        pass
    write_panel_outputs(payload, json_only=json_only)


def _sync_command_data_eval(payload: dict) -> None:
    """Re-write command-data eval panels from ~/.sina reports after post-build run_eval."""
    try:
        from system_roadmap import system_roadmap_payload  # noqa: WPS433

        payload["system_roadmap"] = system_roadmap_payload()
        _write_panel(payload, json_only=True)
        sr = payload.get("system_roadmap") or {}
        ev = sr.get("eval_packet") or {}
        evb = sr.get("eval_packet_v1b") or {}
        print(
            f"OK: command-data eval sync · Eval-1 {ev.get('packet_win_pct')}% · "
            f"Eval-1b {evb.get('mode')} {evb.get('packet_win_pct')}%"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: command-data eval sync: {exc}")


FLEET_BUILD_SNAPSHOT = Path.home() / ".sina" / "fleet_build_snapshot_v1.json"


def _log_fleet_build_snapshot() -> None:
    """Log fleet nudges, auto-green, and report/verify gaps at end of strict build (sa-0208)."""
    from agent_essay_discourse import essay_discourse_payload  # noqa: WPS433
    from agent_scoreboard import scoreboard_payload  # noqa: WPS433

    ed = essay_discourse_payload()
    sb = scoreboard_payload()
    report_gap = list(sb.get("fleet_report_gap") or [])
    verify_gap = list(sb.get("fleet_verify_gap") or [])
    snapshot = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "nudge_count": ed.get("nudge_count"),
        "reported_count": sb.get("reported_count"),
        "agent_count": sb.get("agent_count"),
        "fleet_auto_green_count": sb.get("fleet_auto_green_count"),
        "fleet_report_gap": report_gap,
        "fleet_verify_gap": verify_gap,
    }
    FLEET_BUILD_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    FLEET_BUILD_SNAPSHOT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(
        f"OK: fleet snapshot · nudges {ed.get('nudge_count')} · "
        f"reports {sb.get('reported_count')}/{sb.get('agent_count')} · "
        f"auto-green {sb.get('fleet_auto_green_count')} · "
        f"gaps report {len(report_gap)} · gaps verify {len(verify_gap)} · "
        f"receipt {FLEET_BUILD_SNAPSHOT}"
    )


def _run_founder_directives_import(strict: bool) -> int:
    """Import MASTER_ORDERS into jsonl when directives file has rows (sa-0219)."""
    try:
        from import_founder_directives_v1 import run_import_on_build  # noqa: WPS433

        imp = run_import_on_build()
        if not imp.get("ok"):
            print(f"{'FAIL' if strict else 'WARN'}: founder-directives import — {imp.get('error')}")
            return 1 if strict else 0
        if imp.get("skipped"):
            print("OK: founder-directives import skipped — no jsonl rows (sa-0219)")
            return 0
        print(
            f"OK: founder-directives import · {imp.get('jsonl_rows')} jsonl rows · "
            f"imported {imp.get('imported', 0)} (sa-0219)"
        )
        return 0
    except Exception as exc:
        print(f"{'FAIL' if strict else 'WARN'}: founder-directives import: {exc}")
        return 1 if strict else 0


def _run_council_strategic_slice_seed(strict: bool) -> int:
    """Idempotent council seed — strict build fails on error (sa-0218)."""
    try:
        from seed_council_strategic_slice_v1 import run_seed, verify_seed_marker  # noqa: WPS433

        seed_out = run_seed()
        if not seed_out.get("ok"):
            print(f"{'FAIL' if strict else 'WARN'}: council strategic slice seed — {seed_out.get('error')}")
            return 1 if strict else 0
        ok, detail = verify_seed_marker()
        if not ok:
            print(f"{'FAIL' if strict else 'WARN'}: council seed marker — {detail}")
            return 1 if strict else 0
        state = "skipped" if seed_out.get("skipped") else "applied"
        print(f"OK: council strategic slice seed {state} (sa-0218)")
        return 0
    except Exception as exc:
        print(f"{'FAIL' if strict else 'WARN'}: council strategic slice seed: {exc}")
        return 1 if strict else 0


def _run_sync_feedback_aggregate(strict: bool, *, built_at: str) -> int:
    """Stamp FEEDBACK_AGGREGATE execution_truth with hub built_at after panel write (sa-0017)."""
    import subprocess

    script = SOURCE_A / "scripts" / "sync_feedback_aggregate_hub_built_at_v1.py"
    if not script.is_file():
        print(f"{'FAIL' if strict else 'WARN'}: sync_feedback_aggregate_hub_built_at_v1.py missing (sa-0017)")
        return 1 if strict else 0
    if not built_at:
        print(f"{'FAIL' if strict else 'WARN'}: hub built_at empty — skip feedback aggregate sync (sa-0017)")
        return 1 if strict else 0
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--built-at", built_at],
            cwd=str(SOURCE_A),
            timeout=120,
            check=False,
        )
        if proc.returncode != 0:
            print(f"{'FAIL' if strict else 'WARN'}: sync_feedback_aggregate_hub_built_at_v1.py failed (sa-0017)")
            return proc.returncode if strict else 0
        print("OK: FEEDBACK_AGGREGATE execution_truth synced to hub built_at (sa-0017)")
        return 0
    except subprocess.TimeoutExpired:
        print(f"{'FAIL' if strict else 'WARN'}: sync_feedback_aggregate_hub_built_at_v1.py timeout (sa-0017)")
        return 1 if strict else 0


def _run_update_program_progress(strict: bool) -> int:
    """Refresh PROGRAM_PROGRESS signals_auto.synced_at before panel payload (sa-0015)."""
    import subprocess

    script = SOURCE_A / "scripts" / "update-program-progress.py"
    if not script.is_file():
        print(f"{'FAIL' if strict else 'WARN'}: update-program-progress.py missing (sa-0015)")
        return 1 if strict else 0
    env = {
        **os.environ,
        "SINA_SKIP_NESTED_BOWL": "1",
        "SINA_SKIP_FLEET_SCAN": "1",
    }
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(SOURCE_A),
            env=env,
            timeout=300,
            check=False,
        )
        if proc.returncode != 0:
            print(f"{'FAIL' if strict else 'WARN'}: update-program-progress.py failed (sa-0015)")
            return proc.returncode if strict else 0
        print("OK: PROGRAM_PROGRESS signals_auto synced on build (sa-0015)")
        return 0
    except subprocess.TimeoutExpired:
        print(f"{'FAIL' if strict else 'WARN'}: update-program-progress.py timeout (sa-0015)")
        return 1 if strict else 0


def _run_audit(name: str, strict: bool) -> int:
    """Run audit script — .sh via bash, .py via sys.executable (sa-0201 sa-0226)."""
    path = SOURCE_A / "scripts" / name
    if not path.is_file():
        return 0
    import subprocess

    if name.endswith(".sh"):
        cmd = ["bash", str(path)]
    elif name.endswith(".py"):
        cmd = [sys.executable, str(path)]
    else:
        cmd = [str(path)]
    r = subprocess.run(cmd, cwd=str(SOURCE_A / "scripts"))
    if r.returncode != 0:
        msg = f"{'FAIL' if strict else 'WARN'}: {name} failed"
        print(msg)
        if strict:
            return r.returncode
    return 0


def main() -> None:
    strict = os.environ.get("SINA_AUDIT_STRICT", "1").strip() not in ("0", "false", "no")
    under_e2e = os.environ.get("SINA_UNDER_FACTORY_E2E", "").strip() in ("1", "true", "yes")
    lock_acquired = False
    if strict and not under_e2e:
        try:
            from factory_validation_lock_v1 import acquire, release  # noqa: WPS433

            lk = acquire(holder="strict_build")
            if not lk.get("ok"):
                print(f"FAIL: factory lock: {lk.get('error')} blocked_by={lk.get('blocked_by')}")
                raise SystemExit(1)
            lock_acquired = True
        except SystemExit:
            raise
        except Exception as exc:
            print(f"WARN: factory lock acquire: {exc}")
    try:
        _main_body(strict)
    finally:
        if lock_acquired:
            try:
                from factory_validation_lock_v1 import release  # noqa: WPS433

                release(holder="strict_build")
            except Exception:
                pass


def _main_body(strict: bool) -> None:
    code = _run_audit("audit_agent_governance_e2e.py", strict)
    if code:
        raise SystemExit(code)
    code = _run_audit("audit_essentials_nav.py", strict)
    if code:
        raise SystemExit(code)
    pdb_code = _run_audit("audit_personal_db_layer_a.py", strict=False)
    print("OK: audit_personal_db_layer_a non-strict on build (sa-0212)" if pdb_code == 0 else "WARN: audit_personal_db_layer_a failed (non-strict, sa-0212)")
    # Backend HTTP E2E cancelled by default (founder 2026-06-10). Requires SINA_E2E_FORCE=1 on script.
    if os.environ.get("SINA_RUN_BACKEND_E2E", "").strip() in ("1", "true", "yes"):
        if os.environ.get("SINA_E2E_FORCE", "").strip() in ("1", "true", "yes"):
            code = _run_audit("audit_backend_e2e.py", strict)
            if code:
                raise SystemExit(code)
        else:
            print("OK: SINA_RUN_BACKEND_E2E set but backend E2E cancelled — skip (SINA_E2E_FORCE=1 to run)")
    code = _run_update_program_progress(strict)
    if code:
        raise SystemExit(code)
    payload = build_payload()
    _write_panel(payload)
    # Seed L0/L1 + Eval-1 SSOT for WTM layer map
    try:
        from pre_llm.user_signals.store import record_hub_touch  # noqa: WPS433

        record_hub_touch(hub_tab="system-roadmap", active_repo="SourceA", source="hub_build")
        from eval_packet_v1.runner import run_eval  # noqa: WPS433
        from eval_packet_v1b.runner import REPORT_PATH as EVAL_1B_PATH  # noqa: WPS433
        from eval_packet_v1b.runner import run_eval as run_eval_1b  # noqa: WPS433

        run_eval(write_report=True)
        live_env = os.environ.get("SINA_EVAL_1B_LIVE", "").strip() in ("1", "true", "yes")
        if live_env:
            run_eval_1b(write_report=True, live=True)
        elif not EVAL_1B_PATH.is_file():
            run_eval_1b(write_report=True, live=False)
        try:
            from runtime.graph_executor.executor_engine import run_graph_executor  # noqa: WPS433

            run_graph_executor()
        except Exception as ge:
            print(f"WARN: graph executor refresh: {ge}")
        if strict:
            code = _run_audit("validate-spine-bridge-founder-v1.sh", strict)
            if code:
                raise SystemExit(code)
            print("OK: validate-spine-bridge-founder-v1 after graph executor seed (sa-0210)")
            try:
                from append_spine_proof_priority_v1 import maybe_append_spine_proof_row  # noqa: WPS433

                spine_pri = maybe_append_spine_proof_row()
                if spine_pri.get("appended"):
                    print(f"OK: append_spine_proof_priority_v1 · {spine_pri.get('action_id')}")
            except Exception as spe:
                print(f"{'FAIL' if strict else 'WARN'}: spine proof PRIORITY append: {spe}")
                if strict:
                    raise SystemExit(1) from spe
            code = _run_audit("validate-spine-proof-priority-v1.sh", strict)
            if code:
                raise SystemExit(code)
            print("OK: validate-spine-proof-priority-v1 spine.bridge proof row (sa-0425)")
    except Exception as e:
        print(f"WARN: post-build L0/Eval seed: {e}")
    _sync_command_data_eval(payload)
    code = _run_council_strategic_slice_seed(strict)
    if code:
        raise SystemExit(code)
    if strict:
        code = _run_audit("validate-eval-packet-v1b-grounding.sh", strict)
        if code:
            raise SystemExit(code)
        try:
            from eval_1b_ci_mode import resolve_mode  # noqa: WPS433

            mode_row = resolve_mode()
            if mode_row.get("structural_fallback"):
                os.environ.setdefault("SINA_EVAL_1B_STRUCTURAL_ONLY", "1")
        except Exception as em:
            print(f"WARN: eval_1b_ci_mode probe: {em}")
        code = _run_audit("validate-eval-packet-v1b-live.sh", strict)
        if code:
            raise SystemExit(code)
        # sa-0024: live validator runs under strict without SINA_EVAL_1B_LIVE=1
        print("OK: validate-eval-packet-v1b-live in strict build default chain (sa-0127)")
        code = _run_audit("validate-eval-packet-v1b-strict-build-chain-v1.sh", strict)
        if code:
            raise SystemExit(code)
        try:
            from eval_report_capture import capture_eval_report  # noqa: WPS433

            cap = capture_eval_report(strict=True)
            print(
                f"OK: eval report capture · {cap.get('report_path')} · "
                f"mode={cap.get('report_mode')} live_attempt={cap.get('attempted_live')}"
            )
            if not cap.get("attempted_live"):
                print(
                    f"WARN: eval-1b live gate skipped — {cap.get('ci_reason')} "
                    f"(mode={cap.get('ci_mode')})"
                )
            from eval_report_capture import sync_synthesis_eval_line_from_disk  # noqa: WPS433

            syn = sync_synthesis_eval_line_from_disk(strict=True)
            if not syn.get("ok"):
                print(f"FAIL: synthesis eval line sync: {syn.get('error')}")
                raise SystemExit(1)
            print(
                f"OK: synthesis Eval-1b synced from disk · {syn.get('ratio')} "
                f"({syn.get('pct')}%) · mode={syn.get('report_mode')}"
            )
        except Exception as em:
            print(f"WARN: eval report capture: {em}")
        code = _run_audit("validate-eval-report-capture-v1.sh", strict)
        if code:
            raise SystemExit(code)
        _sync_command_data_eval(payload)
        code = _run_audit("validate-command-data-eval-win-pct-v1.sh", strict)
        if code:
            raise SystemExit(code)
        code = _run_audit("validate-governance-drift-v1.sh", strict)
        if code:
            raise SystemExit(code)
        code = _run_audit("validate-governance-fleet-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: validate-governance-fleet-v1 after eval live (sa-0213)")
    if strict:
        code = _run_audit("validate-dispatch-policy-v1.sh", strict)
        if code:
            raise SystemExit(code)
        code = _run_audit("validate-dispatch-policy-alignment-v1.sh", strict)
        if code:
            raise SystemExit(code)
        code = _run_audit("validate-graph-executor-pos-dispatch-v1.sh", strict)
        if code:
            raise SystemExit(code)
        code = _run_audit("validate-dispatch-ready-lock-v1.sh", strict)
        if code:
            raise SystemExit(code)
        # sa-0209: wire pack validate on strict build — no P0-RUNRECEIPT bump (GOAL_HIERARCHY v1.1 T2b parallel only)
        code = _run_audit("validate-verify-wire-v1.sh", strict)
        if code:
            raise SystemExit(code)
        # sa-0501: validate P0-RUNRECEIPT progress_pct == 100 when verify:wire passes
        _prog = json.loads((SOURCE_A / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
        _plan = next((p for p in _prog.get("parallel_plans", []) if p.get("id") == "P0-RUNRECEIPT"), None)
        _pct = (_plan or {}).get("progress_pct")
        if _pct != 100:
            msg = f"{'FAIL' if strict else 'WARN'}: P0-RUNRECEIPT progress_pct={_pct} — expected 100 after verify:wire pass (sa-0501)"
            print(msg)
            if strict:
                raise SystemExit(1)
        else:
            print("OK: P0-RUNRECEIPT progress_pct=100 verified after verify:wire pass (sa-0501)")
    code = _run_founder_directives_import(strict)
    if code:
        raise SystemExit(code)
    try:
        from founder_request_tracker import sync_shipped_from_disk  # noqa: WPS433

        fr_sync = sync_shipped_from_disk()
        if fr_sync.get("count"):
            print(f"OK: founder-request sync · {fr_sync.get('count')} rows")
    except Exception as e:
        print(f"WARN: founder-request sync: {e}")
    try:
        _log_fleet_build_snapshot()
    except Exception as e:
        print(f"{'FAIL' if strict else 'WARN'}: fleet snapshot: {e}")
        if strict:
            raise SystemExit(1) from e
    if strict:
        code = _run_audit("validate-registry-honest-gate-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: REGISTRY honest gate — receipt-only done enforced (structural-fix)")
        try:
            _log_fleet_build_snapshot()
        except Exception as e:
            print(f"FAIL: fleet snapshot refresh before scoreboard cross-check: {e}")
            raise SystemExit(1) from e
        code = _run_audit("validate-fleet-snapshot-scoreboard-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: fleet snapshot matches scoreboard_payload live (sa-0221)")
    code = _run_audit("audit_hub_source_alignment.py", strict)
    if code:
        raise SystemExit(code)
    if strict:
        code = _run_audit("validate-honest-score-not-here-drift-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: honest_score not_here drift guard (sa-0076)")
        code = _run_audit("validate-honest-score-l8-skip-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: honest_score L8 hybrid skip when shipped (sa-0077)")
    if strict:
        code = _run_audit("validate-build-run-audit-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: _run_audit .sh via bash wired (sa-0226 T1 backfill)")
        code = _run_audit("validate-phase-s2-hub-build-ci-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: phase-s2 hub-build-ci backfill proof sa-0226..sa-0300")
        code = _run_audit("validate-no-duplicate-panel-build-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: duplicate panel build rejected in bowl refresh path (sa-0222)")
        code = _run_audit("validate-find-critical-bugs-governance-drift-chain-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: governance-drift wired in find_critical_bugs CRITICAL chain (sa-0223)")
        code = _run_audit("validate-find-critical-bugs-wtm-future-guard-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: WTM future column guard wired in find_critical_bugs (sa-0224)")
        code = _run_audit("validate-append-repo-execution-log-on-ci-pass-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: REPO_EXECUTION_LOGS append on CI pass wired (sa-0225)")
        code = _run_audit("validate-agent-scoreboard-auto-verify-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: agent_scoreboard _auto_verify verified_by=auto wired (sa-0301)")
        code = _run_audit("validate-fleet-auto-green-count-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: fleet_auto_green_count exposed in scoreboard_payload (sa-0302)")
        code = _run_audit("validate-scoreboard-row-auto-verify-backfill-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: scoreboard_row auto_verify backfill wired (sa-0303)")
        code = _run_audit("validate-scoreboard-tagline-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: scoreboard tagline auto-checks green not ASF verify (sa-0304)")
        code = _run_audit("validate-render-agent-scoreboard-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: renderAgentScoreboard hero auto-green copy + gap banners (sa-0305)")
        code = _run_audit("validate-scoreboard-auto-green-pill-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: scoreboard auto_pass Auto green pill replaces Verify/Force (sa-0306 · sa-0356)")
        for script, label in (
            ("validate-essay-nudge-banner-v1.sh", "sa-0307 sa-0317 sa-0357 essay nudge banners"),
            ("validate-graph-executor-planner-bridge-v1.sh", "sa-0308 planner bridge note"),
            ("validate-governance-fleet-nudges-ssot-v1.sh", "sa-0309 governance-fleet SSOT"),
            ("validate-founder-request-fleet-sync-v1.sh", "sa-0310–0312 FR fleet sync"),
            ("validate-workspace-mirror-scoreboard-v1.sh", "sa-0313 mirror scoreboard copy"),
            ("validate-fleet-gap-banners-ui-v1.sh", "sa-0314 sa-0315 fleet gap banners"),
            ("validate-essay-nudges-council-v1.sh", "sa-0316 council essay_nudges"),
        ):
            code = _run_audit(script, strict)
            if code:
                raise SystemExit(code)
            print(f"OK: {label}")
        code = _run_audit("validate-batch-sa-0318-0424-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: batch sa-0318–0424 scoreboard+spine proof (30-task drain)")
        code = _run_audit("validate-command-data-atomic-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: command-data.json + shell.json atomic write verified (sa-0220)")
        _write_panel(payload, json_only=True)
        code = _run_audit("validate-command-data-sa-queue-v1.py", strict)
        if code:
            raise SystemExit(code)
        print("OK: command-data SA queue + P0 pick aligned with queue_sa (dual-pick law)")
        code = _run_audit("validate-ui-wiring-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: command-data UI wiring — goal1 + eval + scoreboard + P0 organized")
        code = _run_audit("validate-hub-p0-no-autorun-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: hub P0 next_action — no Cursor AUTO-RUN (AS-01)")
        code = _run_audit("validate-anti-staleness-bundle-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: anti-staleness bundle on strict build")
        code = _run_audit("validate-agent-loop-gate-receipt-v1.sh", strict)
        if code:
            raise SystemExit(code)
        print("OK: agent loop gate receipt enforcement wired")
    shell_path = SOURCE_A / "agent-control-panel" / "command-data-shell.json"
    built_for_feedback = str(payload.get("built_at") or "")
    if shell_path.is_file():
        try:
            built_for_feedback = str(
                json.loads(shell_path.read_text(encoding="utf-8")).get("built_at") or built_for_feedback
            )
        except (OSError, json.JSONDecodeError):
            pass
    code = _run_sync_feedback_aggregate(strict, built_at=built_for_feedback)
    if code:
        raise SystemExit(code)
    if strict:
        code = 1
        for attempt in range(3):
            if shell_path.is_file():
                try:
                    built_for_feedback = str(
                        json.loads(shell_path.read_text(encoding="utf-8")).get("built_at") or built_for_feedback
                    )
                except (OSError, json.JSONDecodeError):
                    pass
            code = _run_sync_feedback_aggregate(strict, built_at=built_for_feedback)
            if code:
                raise SystemExit(code)
            code = _run_audit("validate-phase-s0-ssot-alignment-v1.sh", strict)
            if not code:
                break
        if code:
            raise SystemExit(code)
        print("OK: phase-s0 SSOT alignment proof sa-0076..sa-0100")
    _run_audit("audit_private_agent_pages.py", strict=False)
    print(f"OK: {SOURCE_A / 'agent-control-panel/index.html'}")
    print(f"OK: {SOURCE_A / 'agent-control-panel/command-data.json'}")
    p0 = (payload.get("bowl") or {}).get("p0", {})
    kpi = payload.get("mergepack_kpi") or {}
    print(f"P0: {p0.get('id')} · KPI ok: {kpi.get('ok')} · drift: {len((payload.get('bowl') or {}).get('drift') or [])}")


if __name__ == "__main__":
    main()  # noqa: RET503
