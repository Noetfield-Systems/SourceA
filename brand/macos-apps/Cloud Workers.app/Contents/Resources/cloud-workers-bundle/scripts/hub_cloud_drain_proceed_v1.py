#!/usr/bin/env python3
"""Hub cloud drain proceed — one tap on Worker Hub · cloud executes · no Mac motor.

SSOT: data/hub-cloud-drain-proceed-v1.json
Receipt: ~/.sina/hub-cloud-drain-proceed-receipt-v1.json

Mac: POST /api/cloud-drain/proceed/v1 → proxy Railway → full FORGE motor · OpenRouter/Gemini on cloud.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/hub-cloud-drain-proceed-v1.json"
RECEIPT = SINA / "hub-cloud-drain-proceed-receipt-v1.json"
DRAIN = ROOT / "data/secondary-cloud-drain-next-100-v1.json"

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ssot() -> dict:
    return _read(SSOT)


def _resolve_next(*, plan_id: str = "", maps_registry: str = "") -> dict[str, Any]:
    if plan_id or maps_registry:
        drain = _read(DRAIN)
        if plan_id:
            row = next((p for p in (drain.get("plans") or []) if p.get("id") == plan_id), {})
        else:
            row = next(
                (p for p in (drain.get("plans") or []) if p.get("maps_registry") == maps_registry),
                {},
            )
        if row:
            return {
                "task_id": row.get("id"),
                "maps_registry": row.get("maps_registry"),
                "title": row.get("cloud_action"),
                "tier": row.get("tier"),
                "cost_tier": row.get("cost_tier"),
            }
    try:
        sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))
        from cloud_drain_queue_v1 import _plan_by_id, read_head  # noqa: WPS433

        head_row = read_head()
        head_id = str(head_row.get("cloud_drain_head") or "")
        plan = _plan_by_id(head_id)
        if head_id and plan:
            return {
                "task_id": head_id,
                "maps_registry": plan.get("maps_registry"),
                "title": plan.get("cloud_action"),
                "tier": plan.get("tier"),
                "cost_tier": plan.get("cost_tier"),
                "queue_source": "cloud_drain_queue_v1",
            }
    except Exception:
        pass
    from task_plan_priority_v1 import sequential_next  # noqa: WPS433

    seq = sequential_next() or {}
    return {
        "task_id": seq.get("task_id"),
        "maps_registry": seq.get("maps_registry") or seq.get("paired_registry"),
        "title": seq.get("title"),
        "tier": seq.get("tier"),
        "cost_tier": seq.get("cost_tier"),
        "unified_priority": seq.get("unified_priority"),
        "output_type": seq.get("output_type"),
    }


def _apply_llm_provider(provider: str) -> None:
    p = (provider or "openrouter").strip().lower()
    os.environ["SOURCEA_CLOUD_LLM_PROVIDER"] = p
    if p == "gemini":
        os.environ.setdefault("SOURCEA_PREFER_GEMINI", "1")


def proceed_on_cloud(body: dict[str, Any]) -> dict[str, Any]:
    """Runs on Railway FBE HTTP worker."""
    plan_id = str(body.get("plan_id") or "").strip()
    registry = str(body.get("maps_registry") or body.get("plan_registry") or "").strip()
    resolved = _resolve_next(plan_id=plan_id, maps_registry=registry)
    plan_id = plan_id or str(resolved.get("task_id") or "")
    registry = registry or str(resolved.get("maps_registry") or "")
    llm = str(body.get("llm_provider") or body.get("llm") or "openrouter").lower()
    full_motor = bool(body.get("full_motor", True))
    dry_run = bool(body.get("dry_run"))

    if not plan_id and not registry:
        return {"ok": False, "error": "plan_id_or_registry_required", "schema": "hub-cloud-drain-proceed-v1"}

    _apply_llm_provider(llm)

    row: dict[str, Any] = {
        "schema": "hub-cloud-drain-proceed-v1",
        "at": _now(),
        "execution_plane": "headless_cloud",
        "plan_id": plan_id,
        "maps_registry": registry,
        "llm_provider": llm,
        "full_motor": full_motor,
        "dry_run": dry_run,
        "resolved": resolved,
    }

    if full_motor and registry:
        from portfolio__forge_dispatch_v1 import (  # noqa: WPS433
            dispatch_pick,
            enrich_pick,
            load_registry,
            resolve_stack,
        )

        stack_key = resolve_stack(str(body.get("stack") or "sourcea"))
        reg = load_registry(stack_key)
        raw = next((pl for pl in reg.get("plans") or [] if pl.get("id") == registry), None)
        if not raw:
            row.update({"ok": False, "error": "registry_plan_not_found", "maps_registry": registry})
            return row
        pick = enrich_pick(stack_key, raw, reg)
        dispatch = dispatch_pick(pick, dry_run=dry_run, mode="railway_fbe", full_motor=True)
        run_result = dispatch.get("run_result") or {}
        lines = run_result.get("lines") or {}
        motor_ok = bool((lines.get("motor") or {}).get("ok"))
        row.update(
            {
                "ok": bool(dispatch.get("ok")) and (dry_run or motor_ok),
                "dispatch_lane": "full_forge_motor",
                "forge_dispatch": dispatch,
                "motor_ok": motor_ok,
                "federated_ok": run_result.get("federated_ok"),
                "tier_target": run_result.get("tier_target"),
            }
        )
        if not row.get("ok") and not run_result and dispatch.get("skeleton", {}).get("dockerfile") is False:
            row["failure_class"] = "skeleton_blocked"
            row["for_founder"] = {
                "show_this": (
                    f"{plan_id} · {registry} · FAIL · skeleton blocked on cloud "
                    "(dockerfile missing in image — redeploy FBE runner)"
                ),
                "failure_class": "skeleton_blocked",
            }
    else:
        from cloud_worker_dispatch_v1 import dispatch  # noqa: WPS433

        cloud = dispatch(plan_id=plan_id or registry, dry_run=dry_run)
        row.update({"ok": bool(cloud.get("ok")), "dispatch_lane": "evidence_slice", "cloud_dispatch": cloud})

    row["for_founder"] = row.get("for_founder") or {
        "show_this": (
            f"{'DRY-RUN · ' if dry_run else ''}{plan_id} · {registry} · "
            f"{'PASS' if row.get('ok') else 'FAIL'} · {llm} on cloud"
        )
    }

    if row.get("ok") and not dry_run and plan_id:
        try:
            sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))
            from cloud_drain_queue_v1 import advance_on_pass  # noqa: WPS433

            adv = advance_on_pass(plan_id=plan_id)
            row["queue_advance"] = adv
        except Exception as exc:
            row["queue_advance"] = {"ok": False, "error": str(exc)[:120]}

    return row


def _next_brain_pair_id() -> str:
    plan = _read(ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json")
    for u in plan.get("upgrades") or []:
        if str(u.get("status") or "") in ("planned", "pending", "open") and not u.get("cloud_proof"):
            return str(u.get("id") or "")
    return ""


def _mac_post_process(*, plan_id: str, registry: str, cloud_row: dict[str, Any]) -> dict[str, Any]:
    """Receipt · observed head · brain pair · nerves — Mac control plane only."""
    out: dict[str, Any] = {"steps": []}
    if not cloud_row.get("ok"):
        return out

    now = _now()
    if plan_id.startswith("CLOUD-SEC-"):
        n = plan_id.split("-")[-1].zfill(3)
        receipt_path = ROOT / "receipts" / f"cloud-sec-{n}-receipt-v1.json"
    else:
        receipt_path = ROOT / "receipts" / f"{plan_id.lower().replace('_', '-')}-receipt-v1.json"

    summary = {
        "schema": "cloud-sec-receipt-v1",
        "id": plan_id,
        "maps_registry": registry,
        "ok": True,
        "dry_run": False,
        "full_motor": True,
        "hub_proceed": True,
        "forge_dispatch": cloud_row.get("forge_dispatch") or cloud_row.get("cloud_dispatch"),
        "at": now,
        "evidence": cloud_row.get("for_founder", {}).get("show_this", ""),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    out["steps"].append({"step": "receipt", "ok": True, "path": str(receipt_path)})

    drain = _read(DRAIN)
    ids = [
        str(p.get("id") or "")
        for p in (drain.get("plans") or [])
        if str(p.get("id", "")).startswith("CLOUD-SEC-")
    ]
    if plan_id in ids and not cloud_row.get("dry_run"):
        idx = ids.index(plan_id)
        nxt = ids[idx + 1] if idx + 1 < len(ids) else plan_id
        obs_path = SINA / "phase-observed-v1.json"
        obs = _read(obs_path)
        obs.update(
            {
                "cloud_drain_head": nxt,
                "cloud_drain_last_completed": plan_id,
                "rebuilt_at": now,
                "rebuilt_by": "hub_cloud_drain_proceed_v1",
            }
        )
        obs_path.write_text(json.dumps(obs, indent=2) + "\n", encoding="utf-8")
        out["steps"].append({"step": "observed_head", "ok": True, "head": nxt, "completed": plan_id})

    brain_id = _next_brain_pair_id()
    if brain_id:
        try:
            from mark_brain_reasoning_done_v1 import mark_done  # noqa: WPS433

            br = mark_done(
                brain_id,
                evidence=f"hub proceed {plan_id} · {registry} · cloud PASS",
            )
            out["steps"].append({"step": "brain_pair", "ok": bool(br.get("ok")), "upgrade_id": brain_id})
        except Exception as exc:
            out["steps"].append({"step": "brain_pair", "ok": False, "error": str(exc)[:120]})

    try:
        from brain_cloud_reasoning_plan_pulse_v1 import run_pulse  # noqa: WPS433

        out["steps"].append({"step": "brain_pulse", **run_pulse(write=True)})
    except Exception as exc:
        out["steps"].append({"step": "brain_pulse", "ok": False, "error": str(exc)[:120]})

    try:
        from task_plan_priority_v1 import refresh as tp_refresh  # noqa: WPS433

        out["steps"].append({"step": "task_plan_priority", **tp_refresh(write=True)})
    except Exception as exc:
        out["steps"].append({"step": "task_plan_priority", "ok": False, "error": str(exc)[:120]})

    try:
        from agent_nerve_system_v1 import run_nerve_pulse  # noqa: WPS433

        out["steps"].append({"step": "nerve_system", **run_nerve_pulse(write=True)})
    except Exception as exc:
        out["steps"].append({"step": "nerve_system", "ok": False, "error": str(exc)[:120]})

    out["ok"] = all(s.get("ok", True) for s in out["steps"] if "ok" in s)
    return out


def proceed_from_hub(body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Mac Hub handler — proxy to cloud then post-process receipts on Mac."""
    body = body or {}
    resolved = _resolve_next(
        plan_id=str(body.get("plan_id") or ""),
        maps_registry=str(body.get("maps_registry") or body.get("plan_registry") or ""),
    )
    plan_id = str(body.get("plan_id") or resolved.get("task_id") or "")
    registry = str(body.get("maps_registry") or body.get("plan_registry") or resolved.get("maps_registry") or "")
    llm = str(body.get("llm_provider") or body.get("llm") or load_ssot().get("default_llm") or "openrouter")

    payload = {
        "plan_id": plan_id,
        "maps_registry": registry,
        "full_motor": bool(body.get("full_motor", True)),
        "dry_run": bool(body.get("dry_run")),
        "llm_provider": llm,
        "founder_proceed": True,
        "stack": body.get("stack") or "sourcea",
    }

    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    cloud_row = proxy_to_cloud(path="/api/cloud-drain/proceed/v1", body=payload, timeout_s=300)
    dry_run = bool(payload.get("dry_run"))
    post = (
        _mac_post_process(plan_id=plan_id, registry=registry, cloud_row=cloud_row)
        if cloud_row.get("ok") and not dry_run
        else {}
    )

    founder_hint: dict[str, Any] = {}
    if not cloud_row.get("ok"):
        try:
            from cloud_workers_hub_v1 import _cloud_error_founder_hint  # noqa: WPS433

            inner = cloud_row.get("details") if isinstance(cloud_row.get("details"), dict) else cloud_row
            founder_hint = _cloud_error_founder_hint(inner if inner.get("forge_dispatch") else cloud_row)
        except Exception:
            founder_hint = {"show_this": cloud_row.get("message") or cloud_row.get("error") or "Cloud proceed failed"}

    row = {
        "schema": "hub-cloud-drain-proceed-receipt-v1",
        "at": _now(),
        "ok": bool(cloud_row.get("ok")),
        "execution_plane": "mac_hub_proxy",
        "plan_id": plan_id,
        "maps_registry": registry,
        "llm_provider": llm,
        "cloud": cloud_row,
        "mac_post": post,
        "hub_proceed_line": (
            f"hub-proceed · {plan_id} · {registry} · "
            f"{'PASS' if cloud_row.get('ok') else 'FAIL'} · {llm} · cloud_only"
        ),
        "for_founder": cloud_row.get("for_founder")
        or founder_hint
        or {"show_this": f"Hub proceed · {plan_id} · use Worker Hub Proceed button"},
        "failure_class": (founder_hint or {}).get("failure_class"),
        "pipe_live": (founder_hint or {}).get("pipe_live", cloud_row.get("proxied")),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if not row["failure_class"]:
        try:
            from cloud_workers_hub_v1 import classify_cloud_result  # noqa: WPS433

            row["failure_class"] = classify_cloud_result(cloud_row).get("failure_class")
        except Exception:
            pass
    try:
        from cloud_workers_hub_v1 import append_event, classify_cloud_result  # noqa: WPS433

        classified = classify_cloud_result(cloud_row)
        append_event(
            "proceed",
            {
                "ok": bool(cloud_row.get("ok")),
                "plan_id": plan_id,
                "maps_registry": registry,
                "llm_provider": llm,
                "line": row["hub_proceed_line"],
                "failure_class": classified.get("failure_class"),
                "show_this": (row.get("for_founder") or {}).get("show_this"),
            },
        )
    except Exception:
        pass
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    ssot = load_ssot()
    resolved = _resolve_next()
    last = _read(RECEIPT)
    return {
        "schema": "worker-hub-cloud-drain-proceed-v1",
        "ok": True,
        "one_law": ssot.get("one_law"),
        "hub_api": ssot.get("hub_api"),
        "default_llm": ssot.get("default_llm"),
        "llm_providers": ssot.get("llm_providers"),
        "next": resolved,
        "last_line": last.get("hub_proceed_line"),
        "last_ok": last.get("ok"),
    }


def inject_for_agents() -> dict:
    ssot = load_ssot()
    sl = hub_slice()
    return {
        "one_law": ssot.get("one_law"),
        "hub_api": "POST http://127.0.0.1:13020/api/cloud-drain/proceed/v1",
        "hub_button": "Worker Hub · Cloud proceed · Proceed next cloud task",
        "forbidden": ssot.get("forbidden"),
        "next": sl.get("next"),
        "body_example": {"llm_provider": "openrouter", "full_motor": True},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Hub cloud drain proceed v1")
    ap.add_argument("--hub", action="store_true", help="Mac hub proxy + post-process")
    ap.add_argument("--cloud", action="store_true", help="Cloud worker body (Railway)")
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--registry", default="")
    ap.add_argument("--llm", default="openrouter", choices=("openrouter", "gemini"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--inject", action="store_true")
    ap.add_argument("--slice", action="store_true", help="Hub payload slice only (no dispatch)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    body = {
        "plan_id": args.plan_id,
        "maps_registry": args.registry,
        "llm_provider": args.llm,
        "dry_run": args.dry_run,
    }
    if args.inject:
        row = inject_for_agents()
    elif args.slice:
        row = hub_slice()
    elif args.cloud:
        row = proceed_on_cloud(body)
    else:
        row = proceed_from_hub(body)

    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(row.get("hub_proceed_line") or row.get("for_founder", {}).get("show_this") or json.dumps(row))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
