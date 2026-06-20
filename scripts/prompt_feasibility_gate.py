#!/usr/bin/env python3
"""Mandatory prompt feasibility gate — block inject/act on impossible commercial deps.

Law: SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md
Used by: cursor_entry_gate.py · brain-session-start.sh · healthy-drain autoloop
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Titles / instructions requiring founder commercial stack — not agent-runnable today
BLOCK_PATTERNS = (
    r"eval_1b_gate_ok\s*true",
    r"run eval live",
    r"runner\.py live",
    r"after live pass",
    r"openrouter",
    r"real embeddings",
    r"validate-eval-packet-v1b-live",
)

FOUNDER_ONLY_SNIPPETS = (
    "openrouter credits",
    "founder-only:",
    "founder:",
)


def _text_blob(*parts: str) -> str:
    return " ".join(p for p in parts if p).lower()


def _negated_match(t: str, pat: str) -> bool:
    """Match blocker pattern unless immediately negated (NO OpenRouter, FORBIDDEN, etc.)."""
    for m in re.finditer(pat, t, re.I):
        prefix = t[max(0, m.start() - 32) : m.start()]
        if re.search(r"\b(no|not|without|forbidden|skip|never)\s+[\w-]*\s*$", prefix, re.I):
            continue
        if re.search(r"\bforbidden\b", t[max(0, m.start() - 80) : m.start() + 20], re.I):
            continue
        return True
    return False


def blocked_reasons(text: str) -> list[str]:
    t = _text_blob(text)
    reasons: list[str] = []
    for pat in BLOCK_PATTERNS:
        if _negated_match(t, pat):
            reasons.append(pat)
    for snip in FOUNDER_ONLY_SNIPPETS:
        if snip in t:
            reasons.append(f"founder_only:{snip}")
    return reasons


def check_text(text: str, *, live_eval_ok: bool | None = None) -> dict:
    reasons = blocked_reasons(text)
    if live_eval_ok is None:
        try:
            from healthy_queue_blocker_lib import live_eval_available  # noqa: WPS433

            live_eval_ok, _ = live_eval_available()
        except Exception:
            live_eval_ok = False
    if live_eval_ok:
        live_ok_patterns = {"validate-eval-packet-v1b-live", "eval_1b_gate_ok\\s*true"}
        reasons = [r for r in reasons if r not in live_ok_patterns]
    return {
        "ok": len(reasons) == 0,
        "blocked": bool(reasons),
        "reasons": reasons,
        "law": "prompt_feasibility_gate — no OpenRouter/live-eval in inject or ACT",
    }


def pointer_row() -> dict | None:
    """Machine SSOT — follows healthy queue when pointer source says so."""
    path = Path.home() / ".sina" / "next-execution-pointer-v1.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        sa_id = str(data.get("next_sa") or "")
        if not sa_id.startswith("sa-"):
            return None
        return {
            "id": sa_id,
            "path": str(data.get("prompt_path") or ""),
            "title": str(data.get("title") or ""),
            "source": str(data.get("source") or ""),
        }
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def live_pick_row() -> dict | None:
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts/plan-no-asf-run.sh"), "pick", "1"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    for line in proc.stdout.splitlines():
        if line.startswith("sa-"):
            parts = line.split("\t")
            return {
                "id": parts[0].strip(),
                "path": parts[1].strip() if len(parts) > 1 else "",
                "title": parts[2].strip() if len(parts) > 2 else "",
            }
    return None


def healthy_queue_item() -> dict | None:
    for path in (
        Path.home() / ".sina/healthy-queue-30-active.json",
        ROOT / "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json",
    ):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data.get("queue") or []
            state = Path.home() / ".sina/healthy-queue-state-v1.json"
            pos = 1
            if state.is_file():
                pos = int(json.loads(state.read_text()).get("next_pos") or 1)
            if 1 <= pos <= len(items):
                return {"queue_path": str(path), "pos": pos, "item": items[pos - 1]}
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            continue
    return None


def check_session(*, role: str = "worker") -> dict:
    hq = healthy_queue_item()
    ptr = pointer_row()
    # Goal 1 healthy drain: pointer (synced from queue) beats REGISTRY live_pick for mismatch checks.
    if hq and ptr and "healthy-queue" in str(ptr.get("source") or ""):
        pick = ptr
        pick_target = "execution_pointer"
    else:
        pick = live_pick_row()
        pick_target = "live_pick_1"
    checks: list[dict] = []

    if pick:
        blob = f"{pick.get('id')} {pick.get('title')}"
        c = check_text(blob, live_eval_ok=None)
        c["target"] = pick_target
        c["sa_id"] = pick.get("id")
        checks.append(c)

    if hq:
        item = hq["item"]
        # Inject feasibility = instruction for CHECK; instruction + verify for ACT/VERIFY
        # unless instruction explicitly forbids OpenRouter/live (verify footer may still mention path).
        role_q = str(item.get("queue_role") or "").lower()
        instr = str(item.get("instruction") or "")
        if role_q == "check" or re.search(r"\bNO\s+OpenRouter\b", instr, re.I):
            blob = instr
        else:
            blob = " ".join(str(item.get(k) or "") for k in ("instruction", "verify", "queue_role"))
        c = check_text(blob, live_eval_ok=None)
        c["target"] = "healthy_queue_current"
        c["queue_pos"] = hq["pos"]
        c["sa_id"] = item.get("sa_id")
        c["queue_role"] = item.get("queue_role")
        checks.append(c)

    blocked = [c for c in checks if c.get("blocked")]
    queue_c = next((c for c in checks if c.get("target") == "healthy_queue_current"), None)
    pick_c = next(
        (c for c in checks if c.get("target") in ("live_pick_1", "execution_pointer")),
        None,
    )

    # STOP only when current queue item is impossible (the prompt we inject).
    queue_blocked = bool(queue_c and queue_c.get("blocked"))
    pick_blocked = bool(pick_c and pick_c.get("blocked"))
    pick_mismatch = (
        queue_c
        and pick_c
        and queue_c.get("sa_id")
        and pick_c.get("sa_id")
        and queue_c.get("sa_id") != pick_c.get("sa_id")
    )

    if queue_blocked:
        action = "STOP_INJECT"
    elif pick_blocked and not queue_c:
        action = "STOP_INJECT"
    elif pick_blocked and pick_mismatch:
        action = "WARN_PICK_MISMATCH"
    elif pick_blocked:
        action = "WARN_LIVE_PICK_BLOCKED"
    elif blocked:
        action = "WARN"
    else:
        action = "PROCEED"

    return {
        "ok": not queue_blocked,
        "role": role,
        "feasible": not queue_blocked,
        "blocked_count": len(blocked),
        "checks": checks,
        "pick_mismatch": pick_mismatch,
        "action": action,
        "remediation": (
            "Rebuild achievable pack: python3 ~/.sina/build-achievable-healthy-queue.py "
            "· skip OpenRouter/live-eval sa · never ACT on impossible pick"
        ),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Prompt feasibility gate")
    p.add_argument("--role", default="worker")
    p.add_argument("--json", action="store_true")
    p.add_argument("--text", help="Check arbitrary prompt text")
    p.add_argument("--strict", action="store_true", help="Exit 1 if blocked")
    args = p.parse_args()

    if args.text:
        out = check_text(args.text)
    else:
        out = check_session(role=args.role)

    if args.json or not args.text:
        print(json.dumps(out, indent=2))
    else:
        print("OK" if out.get("ok") else f"BLOCKED: {out.get('reasons')}")

    if args.strict and not out.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
