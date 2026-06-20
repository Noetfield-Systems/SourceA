#!/usr/bin/env python3
"""Complex Situation Fork Machine — assess triggers, emit templates, write receipts."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
from governance_paths_v1 import FORK_MACHINE, INTEGRITY_PLAYBOOK

SINA = Path.home() / ".sina"

LAW = FORK_MACHINE
PROMPT = ROOT / "prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md"
PLAYBOOK = INTEGRITY_PLAYBOOK
CANVAS_HINT = (
    "Open Canvas beside chat: "
    "~/.cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/"
    "canvases/sourcea-system-integrity-100.canvas.tsx"
)
RECEIPT_PATH = SINA / "complex-situation-fork-receipt-v1.json"

TRIGGERS = [
    {"id": "T1", "name": "mega_chat", "desc": ">30 turns or multi-topic whole-system ask"},
    {"id": "T2", "name": "high_stakes_role", "desc": "Brain · Maintainer strict · Founder law · Council"},
    {"id": "T3", "name": "multi_fork", "desc": ">=2 founder decisions or conflicts"},
    {"id": "T4", "name": "machine_red", "desc": "find_critical_bugs CRITICAL or ecosystem safety FAIL"},
    {"id": "T5", "name": "playbook", "desc": "SYS-INTEGRITY-100 or governance audit session"},
]

HIGH_STAKES_ROLES = frozenset({"brain", "maintainer", "founder", "council"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_factory_line() -> str:
    fn = _read_json(SINA / "factory-now-v1.json") or {}
    return str(fn.get("line") or "factory-now unavailable")


def assess_session(*, role: str = "", turns: int = 0, forks: int = 0, playbook: bool = False) -> dict[str, Any]:
    role_l = (role or "").strip().lower()
    matched: list[str] = []
    if turns >= 30:
        matched.append("T1")
    if role_l in HIGH_STAKES_ROLES:
        matched.append("T2")
    if forks >= 2:
        matched.append("T3")
    if playbook:
        matched.append("T5")

    critical = False
    try:
        import subprocess

        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "find_critical_bugs.py")],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(ROOT),
        )
        out = r.stdout + r.stderr
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("{") and "critical" in line:
                try:
                    j = json.loads(line)
                    critical = int(j.get("critical") or 0) > 0
                    break
                except json.JSONDecodeError:
                    continue
        if not critical and r.returncode != 0 and "CRITICAL:" in out:
            critical = True
    except (OSError, subprocess.TimeoutExpired):
        pass

    if critical:
        matched.append("T4")

    run_machine = len(matched) > 0
    return {
        "schema": "complex-situation-fork-assess-v1",
        "at": _now(),
        "run_fork_machine": run_machine,
        "triggers_matched": matched,
        "triggers_all": TRIGGERS,
        "role": role_l or None,
        "turns": turns,
        "forks": forks,
        "factory_line": load_factory_line(),
        "law": str(LAW.relative_to(ROOT)),
        "prompt": str(PROMPT.relative_to(ROOT)),
        "canvas": CANVAS_HINT,
        "next_command": "Paste prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md into chat",
    }


def fork_inventory_template() -> str:
    return """## Fork inventory (session)

| id | Subject | Question | Type | Decider | Status |
|----|---------|----------|------|---------|--------|
| F-01 | … | … | choice4 / yesno / text | F | open |

## Options — F-01
| Key | Label | If you pick → Effect logged |
|-----|-------|------------------------------|
| A | … | … |
| B | … | … |
| C | … | … |
| D | … | … |
| **RECOMMENDED** | … | evidence: … |

## Confirmation preview (founder only)
ASF: FORK-MACHINE — execute confirmed:
1. [F-01] A — …
   Effect: …
"""


def write_receipt(row: dict[str, Any]) -> Path:
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return RECEIPT_PATH


def validate_closeout_text(text: str) -> dict[str, Any]:
    required = [
        "Fork inventory",
        "Golden insight",
        "Result table",
    ]
    missing = [r for r in required if r.lower() not in text.lower()]
    ok = len(missing) == 0
    return {"ok": ok, "missing_sections": missing}


def main() -> int:
    p = argparse.ArgumentParser(description="Complex Situation Fork Machine v1")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("assess", help="Assess whether to run fork machine")
    a.add_argument("--role", default="", help="brain|maintainer|founder|council|worker")
    a.add_argument("--turns", type=int, default=0)
    a.add_argument("--forks", type=int, default=0)
    a.add_argument("--playbook", action="store_true")
    a.add_argument("--json", action="store_true")
    a.add_argument("--write-receipt", action="store_true")

    sub.add_parser("template", help="Print fork inventory markdown template")
    sub.add_parser("open-canvas-hint", help="Print canvas path for sidebar")

    v = sub.add_parser("validate-closeout", help="Check closeout has fork sections")
    v.add_argument("--file", required=True, help="Path to closeout markdown")

    args = p.parse_args()

    if args.cmd == "assess":
        row = assess_session(
            role=args.role,
            turns=args.turns,
            forks=args.forks,
            playbook=args.playbook,
        )
        if args.write_receipt:
            write_receipt(row)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"run_fork_machine={row['run_fork_machine']}")
            print(f"triggers={','.join(row['triggers_matched']) or 'none'}")
            print(f"factory: {row['factory_line']}")
            print(row["canvas"])
        return 0

    if args.cmd == "template":
        print(fork_inventory_template())
        return 0

    if args.cmd == "open-canvas-hint":
        print(CANVAS_HINT)
        print(f"law: {LAW}")
        print(f"prompt: {PROMPT}")
        return 0

    if args.cmd == "validate-closeout":
        path = Path(args.file)
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        result = validate_closeout_text(text)
        if args.json if hasattr(args, "json") else False:
            print(json.dumps(result))
        else:
            if result["ok"]:
                print("OK: validate-complex-situation-fork-closeout")
            else:
                print(f"FAIL: missing {result['missing_sections']}", file=sys.stderr)
        return 0 if result["ok"] else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
