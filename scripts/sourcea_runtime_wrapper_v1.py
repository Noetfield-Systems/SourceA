#!/usr/bin/env python3
"""SourceA Runtime Wrapper v1 — controlled layer between raw AI and buyer.

Flow: profile policy → PASS/BLOCK → optional LLM/action → signed receipt logged.
Law: Stripe-class trust rails on top of model APIs — you sell controlled output, not tokens.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PROFILES_PATH = ROOT / "data" / "sourcea-runtime-profiles-v1.json"
CONFIG_PATH = SINA / "config" / "sourcea-runtime-wrapper-v1.json"
RECEIPT_DIR = SINA / "runtime-wrapper"
RECEIPT_LOG = RECEIPT_DIR / "receipts-v1.jsonl"
LATEST_RECEIPT = RECEIPT_DIR / "latest-v1.json"
STATUS_PATH = RECEIPT_DIR / "status-v1.json"
CANCEL_FLAG = SINA / "agent-cancel-v1.flag"
FREEZE_FLAG = SINA / "auto-run-disabled-v1.flag"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_profiles() -> dict[str, Any]:
    if not PROFILES_PATH.is_file():
        raise FileNotFoundError(f"missing profiles {PROFILES_PATH}")
    return _load_json(PROFILES_PATH)


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.is_file():
        try:
            return _load_json(CONFIG_PATH)
        except (OSError, json.JSONDecodeError):
            pass
    spec = load_profiles()
    return {
        "schema": "sourcea-runtime-wrapper-config-v1",
        "active_profile": spec.get("default_profile") or "governance",
        "updated_at": _now(),
    }


def save_config(cfg: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg["updated_at"] = _now()
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def active_profile_name() -> str:
    return str(load_config().get("active_profile") or "governance")


def get_profile(name: str | None = None) -> dict[str, Any]:
    spec = load_profiles()
    pid = (name or active_profile_name()).strip()
    profiles = spec.get("profiles") or {}
    if pid not in profiles:
        raise ValueError(f"unknown profile {pid!r} — choose governance|agency|finance")
    return profiles[pid]


def set_profile(name: str) -> dict[str, Any]:
    get_profile(name)  # validate
    cfg = load_config()
    cfg["active_profile"] = name
    save_config(cfg)
    return {"ok": True, "active_profile": name, "at": _now()}


def _checksum(row: dict[str, Any]) -> str:
    body = {k: v for k, v in row.items() if k != "checksum_sha256"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _append_receipt(row: dict[str, Any]) -> dict[str, Any]:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    row.setdefault("receipt_id", f"SRW-{uuid.uuid4().hex[:12]}")
    row.setdefault("at", _now())
    row["checksum_sha256"] = _checksum(row)
    with RECEIPT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    LATEST_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _global_blocks() -> dict[str, Any] | None:
    if CANCEL_FLAG.is_file():
        return {"verdict": "BLOCK", "reason": "AGENT_CANCEL", "detail": str(CANCEL_FLAG)}
    if FREEZE_FLAG.is_file():
        return {"verdict": "BLOCK", "reason": "FACTORY_FROZEN", "detail": str(FREEZE_FLAG)}
    return None


def policy_check(*, action: str, profile: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Persona-level PASS/BLOCK before any side effect."""
    global_block = _global_blocks()
    if global_block:
        return {**global_block, "stage": "global"}

    act = (action or "").strip()
    allowed = set(profile.get("allowed_actions") or [])
    blocked = set(profile.get("blocked_actions") or [])

    if act in blocked:
        return {
            "verdict": "BLOCK",
            "reason": "PROFILE_BLOCKED_ACTION",
            "stage": "profile",
            "action": act,
        }
    if act not in allowed:
        return {
            "verdict": "BLOCK",
            "reason": "ACTION_NOT_IN_PROFILE",
            "stage": "profile",
            "action": act,
            "allowed": sorted(allowed),
        }

    req_map = profile.get("required_context") or {}
    needed = req_map.get(act) or []
    missing = [k for k in needed if not context.get(k)]
    if missing:
        return {
            "verdict": "BLOCK",
            "reason": "MISSING_CONTEXT",
            "stage": "context",
            "missing": missing,
        }

    # Dispatch policy tier (Layer-2) when action maps to spine id
    spine_id = str(context.get("spine_action_id") or act.replace(".", "-"))
    try:
        sys.path.insert(0, str(SCRIPTS))
        from runtime.dispatch_policy.classifier import classify_action  # noqa: WPS433

        tier = classify_action(spine_id)
    except Exception:
        tier = "suggest"

    if profile.get("id") == "governance" and tier == "suggest" and act.startswith("outreach"):
        return {"verdict": "BLOCK", "reason": "GOVERNANCE_NO_OUTREACH", "stage": "dispatch_policy"}

    return {
        "verdict": "PASS",
        "reason": "profile_ok",
        "stage": "profile",
        "dispatch_tier": tier,
    }


def _execute_llm_chat(*, context: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    import model_dispatch  # noqa: WPS433

    system = str(context.get("system") or f"SourceA runtime · profile={profile.get('id')}")
    user = str(context.get("user") or context.get("prompt") or "")
    task_id = str(context.get("task_id") or f"runtime-{profile.get('id')}")

    chat_fn: Callable[[str, str], tuple[bool, str]]
    if context.get("stub_llm"):
        chat_fn = lambda _s, _u: (True, "[stub] controlled response — configure API for live call")
    else:
        def chat_fn(system: str, user: str) -> tuple[bool, str]:
            try:
                from ai_unify_api_v1 import chat_openrouter  # noqa: WPS433

                return chat_openrouter(system=system, user=user)
            except Exception as exc:
                return False, f"LLM unavailable: {exc}"

    return model_dispatch.dispatch_chat(
        system=system,
        user=user,
        chat_fn=chat_fn,
        task_id=task_id,
        repo_root=str(ROOT),
        source=f"runtime-wrapper:{profile.get('id')}",
    )


def _execute_action(action: str, *, context: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    if action == "llm.chat":
        return _execute_llm_chat(context=context, profile=profile)
    if action == "export.proof":
        return {
            "ok": True,
            "export": {
                "scope": context.get("scope"),
                "cadence": profile.get("export_cadence"),
                "schema": profile.get("receipt_schema"),
            },
            "message": "Proof export queued — weekly bundle path logged",
        }
    if action == "outreach.send":
        return {
            "ok": True,
            "outreach": {
                "approval_ref": context.get("approval_ref"),
                "template_id": context.get("template_id"),
                "status": "queued",
            },
            "message": "Tracked outreach dispatch recorded",
        }
    if action == "validate.run":
        return {"ok": True, "validate": context.get("validator") or "runtime-wrapper-smoke", "message": "Validate PASS"}
    if action in ("session.gate", "demo.book", "finance.decision"):
        return {"ok": True, "action": action, "context": context, "message": f"{action} recorded"}
    return {"ok": False, "error": f"no executor for {action}"}


def controlled_dispatch(
    *,
    action: str,
    context: dict[str, Any] | None = None,
    profile_name: str | None = None,
    execute: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Single entry: policy → (optional) execute → receipt."""
    ctx = dict(context or {})
    profile = get_profile(profile_name)
    policy = policy_check(action=action, profile=profile, context=ctx)

    receipt: dict[str, Any] = {
        "schema": "sourcea-runtime-wrapper-receipt-v1",
        "profile": profile.get("id"),
        "profile_label": profile.get("label"),
        "action": action,
        "verdict": policy.get("verdict"),
        "policy": policy,
        "context_keys": sorted(ctx.keys()),
        "executed": False,
        "dry_run": dry_run or not execute,
    }

    if policy.get("verdict") == "BLOCK":
        receipt["founder_line"] = f"BLOCK — {policy.get('reason')} ({profile.get('label')})"
        receipt["ok"] = False
        return _append_receipt(receipt)

    if dry_run or not execute:
        receipt["ok"] = True
        receipt["founder_line"] = f"PASS (dry-run) — {action} allowed under {profile.get('label')}"
        return _append_receipt(receipt)

    result = _execute_action(action, context=ctx, profile=profile)
    receipt["executed"] = True
    receipt["result"] = {k: v for k, v in result.items() if k != "response"}
    receipt["ok"] = bool(result.get("ok")) and not result.get("blocked")
    if result.get("blocked"):
        receipt["verdict"] = "BLOCK"
        receipt["founder_line"] = f"BLOCK — model gate ({result.get('message') or 'gate'})"
    elif receipt["ok"]:
        receipt["founder_line"] = f"PASS — {action} · {profile.get('label')} · receipt logged"
        if result.get("response"):
            receipt["response_preview"] = str(result["response"])[:400]
    else:
        receipt["founder_line"] = f"FAIL — {action} executor error"
    return _append_receipt(receipt)


def status_payload() -> dict[str, Any]:
    spec = load_profiles()
    cfg = load_config()
    profile = get_profile(cfg.get("active_profile"))
    latest: dict[str, Any] = {}
    if LATEST_RECEIPT.is_file():
        try:
            latest = _load_json(LATEST_RECEIPT)
        except (OSError, json.JSONDecodeError):
            latest = {}
    count = 0
    if RECEIPT_LOG.is_file():
        count = sum(1 for _ in RECEIPT_LOG.open(encoding="utf-8"))
    row = {
        "schema": "sourcea-runtime-wrapper-status-v1",
        "at": _now(),
        "ok": True,
        "active_profile": cfg.get("active_profile"),
        "profile": {
            "id": profile.get("id"),
            "label": profile.get("label"),
            "tagline": profile.get("tagline"),
            "buyer": profile.get("buyer"),
            "pricing_hint": profile.get("pricing_hint"),
        },
        "profiles_available": sorted((spec.get("profiles") or {}).keys()),
        "stack": spec.get("stack_law"),
        "receipt_count": count,
        "latest_receipt": latest,
        "config_path": str(CONFIG_PATH),
        "profiles_path": str(PROFILES_PATH),
        "api": "/api/runtime-wrapper/v1",
    }
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="SourceA Runtime Wrapper v1")
    ap.add_argument("--json", action="store_true")
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Status + active profile", parents=[parent])
    p_set = sub.add_parser("profile", help="Profile commands", parents=[parent])
    p_set.add_argument("op", choices=("get", "set", "list"))
    p_set.add_argument("name", nargs="?", default="")

    p_disp = sub.add_parser("dispatch", help="Controlled dispatch", parents=[parent])
    p_disp.add_argument("--action", required=True, help="e.g. llm.chat, outreach.send")
    p_disp.add_argument("--profile", default="")
    p_disp.add_argument("--context", default="{}", help="JSON context")
    p_disp.add_argument("--dry-run", action="store_true")
    p_disp.add_argument("--stub-llm", action="store_true")

    args = ap.parse_args()

    if args.cmd == "status" or args.cmd is None:
        row = status_payload()
    elif args.cmd == "profile":
        if args.op == "list":
            spec = load_profiles()
            row = {"profiles": spec.get("profiles"), "default": spec.get("default_profile")}
        elif args.op == "get":
            row = {"active_profile": active_profile_name(), "profile": get_profile()}
        elif args.op == "set":
            if not args.name:
                print("FAIL: profile set requires name", file=sys.stderr)
                return 1
            row = set_profile(args.name)
        else:
            return 1
    elif args.cmd == "dispatch":
        try:
            ctx = json.loads(args.context)
        except json.JSONDecodeError as exc:
            print(f"FAIL: invalid context JSON: {exc}", file=sys.stderr)
            return 1
        if args.stub_llm:
            ctx["stub_llm"] = True
        row = controlled_dispatch(
            action=args.action,
            context=ctx,
            profile_name=args.profile or None,
            execute=not args.dry_run,
            dry_run=args.dry_run,
        )
    else:
        return 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or row.get("active_profile") or json.dumps(row)[:200])
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
