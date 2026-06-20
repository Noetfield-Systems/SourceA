#!/usr/bin/env python3
"""Rule zero-latency hook — new rule/SSOT → fanout → surfaces → receipt.

Law: data/rule-propagation-zero-latency-v1.json
Receipt: ~/.sina/rule-zero-latency-hook-receipt-v1.json

Triggers: pre_write_guard (rule paths) · agent_rule_live_wire --on-new-rule · CLI
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "rule-propagation-zero-latency-v1.json"
RECEIPT = SINA / "rule-zero-latency-hook-receipt-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"

RULE_PATH_MARKERS = (
    ".cursor/rules/",
    "brain-os/law/",
    "brain-os/incidents/",
    "data/agent-rule-live-wire-registry-v1.json",
    "data/agent-law-poison-registry-v1.json",
    "data/rule-propagation-zero-latency-v1.json",
    "data/governance",
    "data/mac-law",
    "data/cursor-bootstrap-ledger-v1.json",
)

RULE_DATA_SUFFIXES = (
    "-registry-v1.json",
    "-live-wire-v1.json",
    "incident-",
    "agent-behavior-settings-v1.json",
    "founder-execution-model-v1.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _resolve(path: str) -> Path:
    p = Path(path.replace("~/", str(Path.home()) + "/"))
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    return p.resolve()


def hook_disabled() -> bool:
    return os.environ.get("SINA_RULE_ZERO_LATENCY_HOOK", "1").strip().lower() in ("0", "false", "no", "off")


def is_rule_governance_path(path: str) -> bool:
    """True when a write should fan out through zero-latency governance."""
    try:
        p = _resolve(path)
    except (OSError, ValueError):
        return False
    rel = ""
    try:
        rel = p.relative_to(ROOT).as_posix()
    except ValueError:
        rel = p.as_posix()
    if rel.endswith(".mdc"):
        return True
    if any(m in rel for m in RULE_PATH_MARKERS):
        return True
    if rel.startswith("data/") and rel.endswith("-v1.json"):
        name = p.name
        if any(x in name for x in RULE_DATA_SUFFIXES):
            return True
        if "rule" in name or "governance" in name or "incident" in name or "mac-law" in name:
            return True
    if "/incidents/" in rel and rel.endswith(".md"):
        return True
    if rel.startswith("brain-os/law/") and rel.endswith(".md"):
        return True
    return False


def _patch_rule_wire_line(*, ok: bool, reason: str, tier: str) -> str:
    line = f"rule-wire · {'PASS' if ok else 'FAIL'} · tier={tier} · {reason}"
    surfaces = _read(SURFACES)
    if surfaces:
        surfaces["rule_wire_line"] = line
        surfaces["rule_zero_latency_hook"] = {
            "ok": ok,
            "at": _now(),
            "reason": reason,
            "tier": tier,
            "receipt": str(RECEIPT),
            "law": str(SSOT.relative_to(ROOT)),
        }
        SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    return line


def run_hook(
    *,
    path: str = "",
    reason: str = "manual",
    tier: str = "fast",
    sync_cursor_index: bool = True,
    sync_mirror: bool = False,
) -> dict:
    if hook_disabled():
        return {"ok": True, "skipped": True, "reason": "SINA_RULE_ZERO_LATENCY_HOOK=0"}

    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict] = []
    resolved = _resolve(path) if path else None

    if sync_cursor_index and (not path or (resolved and resolved.suffix == ".mdc")):
        try:
            from agent_rule_live_wire_v1 import sync_cursor_rules_index  # noqa: WPS433

            idx = sync_cursor_rules_index(write=True)
            steps.append({"step": "cursor_rules_index", "ok": bool(idx.get("ok")), "count": idx.get("count")})
        except Exception as exc:
            steps.append({"step": "cursor_rules_index", "ok": False, "error": str(exc)[:120]})

    if sync_mirror and tier == "full":
        try:
            from agent_memory_mirror_v1 import sync_mirror  # noqa: WPS433

            mirror = sync_mirror()
            steps.append(
                {
                    "step": "memory_mirror_sync",
                    "ok": bool((mirror.get("validation") or {}).get("ok", True)),
                }
            )
        except Exception as exc:
            steps.append({"step": "memory_mirror_sync", "ok": False, "error": str(exc)[:120]})

    from rule_propagation_fanout_v1 import fanout  # noqa: WPS433

    fan = fanout(reason=reason, tier=tier, trigger_path=path or "")
    steps.append({"step": "rule_propagation_fanout", "ok": bool(fan.get("ok")), "tier": tier})

    if not fan.get("ok") and tier == "fast":
        fan_retry = fanout(reason=f"{reason}:heal-retry", tier="fast", trigger_path=path or "")
        steps.append({"step": "rule_propagation_fanout_retry", "ok": bool(fan_retry.get("ok")), "tier": tier})
        if fan_retry.get("ok"):
            fan = fan_retry

    try:
        from agent_nerve_system_v1 import patch_surfaces  # noqa: WPS433

        nerve_rec = _read(SINA / "agent-nerve-system-receipt-v1.json")
        if nerve_rec.get("nerve_system_line"):
            nerve = patch_surfaces(row=nerve_rec)
        else:
            nerve = {"ok": True, "skipped": True, "reason": "no_cached_nerve_receipt"}
        steps.append({"step": "nerve_patch_surfaces", "ok": bool(nerve.get("ok", True))})
    except Exception as exc:
        steps.append({"step": "nerve_patch_surfaces", "ok": False, "error": str(exc)[:80], "warn_only": True})

    if tier == "full":
        try:
            from agent_rule_live_wire_v1 import pulse_registry_to_surfaces  # noqa: WPS433

            surfaces = _read(SURFACES)
            pulse = pulse_registry_to_surfaces(surfaces, write=True)
            if pulse.get("line"):
                surfaces["rule_live_wire_line"] = pulse.get("line")
            SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
            steps.append({"step": "registry_pulse", "ok": bool(pulse.get("ok"))})
        except Exception as exc:
            steps.append({"step": "registry_pulse", "ok": False, "error": str(exc)[:120]})

    fan_ok = bool(fan.get("ok"))
    core_ok = all(s.get("ok", True) for s in steps if s.get("step") != "rule_propagation_fanout")
    ok = fan_ok and core_ok
    line = _patch_rule_wire_line(ok=ok, reason=reason, tier=tier)
    row = {
        "schema": "rule-zero-latency-hook-receipt-v1",
        "ok": ok,
        "at": _now(),
        "reason": reason,
        "tier": tier,
        "trigger_path": path or None,
        "law": str(SSOT.relative_to(ROOT)),
        "steps": steps,
        "fanout": {"ok": fan_ok, "line": fan.get("line"), "receipt": str(SINA / "rule-propagation-fanout-receipt-v1.json")},
        "rule_wire_line": line,
        "command": "python3 scripts/rule_zero_latency_hook_v1.py --path <target> --json",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def maybe_hook_after_pre_write(*, path: str, agent: str = "cursor") -> dict:
    """Called from pre_write_guard when write is allowed on a governance path."""
    if hook_disabled() or not is_rule_governance_path(path):
        return {"ok": True, "skipped": True, "reason": "not_rule_governance_path"}
    p = _resolve(path)
    reason = f"pre_write:{agent}:{p.name}"
    sync_index = p.suffix == ".mdc" and p.is_file()
    row = run_hook(path=path, reason=reason, tier="fast", sync_cursor_index=sync_index, sync_mirror=False)
    if not p.is_file() and p.suffix == ".mdc":
        row["after_write_required"] = True
        row["after_write_command"] = (
            f"python3 scripts/pre_write_guard_v1.py post-write --agent {agent} --path {path} --json"
        )
    return row


def assess(*, write: bool = True) -> dict:
    """Registry pulse — read hook + fanout receipts (no full chain)."""
    hook = _read(RECEIPT)
    fan = _read(SINA / "rule-propagation-fanout-receipt-v1.json")
    ok = bool(hook.get("ok")) and bool(fan.get("ok"))
    line = str(hook.get("rule_wire_line") or fan.get("line") or "")
    if not line:
        line = f"rule-wire · {'PASS' if ok else 'FAIL'} · assess"
    row = {
        "ok": ok,
        "schema": "rule-zero-latency-assess-v1",
        "at": _now(),
        "rule_wire_line": line,
        "hook_receipt": str(RECEIPT),
        "fanout_receipt": str(SINA / "rule-propagation-fanout-receipt-v1.json"),
        "hook_ok": bool(hook.get("ok")),
        "fanout_ok": bool(fan.get("ok")),
    }
    if write and SURFACES.is_file():
        _patch_rule_wire_line(ok=ok, reason="assess", tier=str(hook.get("tier") or "fast"))
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Rule zero-latency governance hook")
    ap.add_argument("--path", default="", help="Trigger path (rule .mdc or governance SSOT)")
    ap.add_argument("--reason", default="cli")
    ap.add_argument("--tier", choices=("fast", "full"), default="fast")
    ap.add_argument("--full", action="store_true", help="Alias for --tier full")
    ap.add_argument("--check-path", action="store_true", help="Print is_rule_governance_path only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    tier = "full" if args.full else args.tier
    if args.check_path:
        row = {"path": args.path, "is_rule_governance_path": is_rule_governance_path(args.path)}
    else:
        row = run_hook(
            path=args.path,
            reason=args.reason,
            tier=tier,
            sync_cursor_index=True,
            sync_mirror=tier == "full",
        )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("rule_wire_line") or row.get("line") or row)
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
