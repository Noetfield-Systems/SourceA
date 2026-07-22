#!/usr/bin/env python3
"""Sync founder-picks-locked-v2 YAML from live_founder_decision_form_v1.py --json."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    Path.home() / ".sina/agent-workspaces/trustfield/commercial-goal/terminology/picks-locked.yaml",
    ROOT / "archive/attachments/founder-language/picks-locked.yaml",
    ROOT / "archive/attachments/founder-language/FOUNDER_LANGUAGE_CORPUS_v3/picks-locked.yaml",
]

BATCH_FORMAL_BLOCK = """\
ASF: FIVE-STEP — PICK: Q-PLAN-300 LOCKED
11.01 SHIP — TF+NF outreach this week (PLAN-001,002,103,273)
11.02 SHIP — Film W1 ALLOW/TAMPER/BLOCK <6min (PLAN-041–044)
11.03 SHIP — K1 receipt on read + export + bypass=0 (PLAN-026,038,141,145,157)
11.04 SHIP — Procurement pack SOW+SOC2+security (PLAN-006,064,065,140,217)
11.05 SHIP — TF+NF instrument + 10-min scaffold (PLAN-076,077,201,217)
3.07 NO — no pending GOV_UNIFY batch · Phase 3 index-only
5.08 APPROVE — sa-0798 check turn · factory background
6.07 B — Council stays Phase 1 until W3 signal
6.10 NO — no agent roster change
7.05 DEFER — conflict #1 logged · continue_work
7.07 NEVER — no new paradox→policy doc this sprint
8.08 YES — weekly incident certify on
8.09 B — keep existing severity rubric
9.07 A — 30-day order: ENFORCEMENT W1 film + NOETFIELD-W3 batch 1
9.08 C — defer Paid.ai pilot post-W3
10.07 B — integrity playbook monthly SCAN cadence"""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_form() -> dict:
    raw = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts/live_founder_decision_form_v1.py"), "--json"],
        text=True,
    )
    return json.loads(raw)


def _yaml_quote(s: str) -> str:
    if not s or any(c in s for c in ':"\\\'\n'):
        return json.dumps(s, ensure_ascii=False)
    return s


def _yaml_list(items: list[str], indent: int = 0) -> str:
    pad = " " * indent
    return "\n".join(f'{pad}- {_yaml_quote(x)}' for x in items)


def _yaml_pick_rows(rows: list[dict], indent: int = 2) -> str:
    pad = " " * indent
    lines: list[str] = []
    for row in rows:
        lines.append(f"{pad}- id: {_yaml_quote(str(row['id']))}")
        lines.append(f"{pad}  pick: {_yaml_quote(str(row['pick']))}")
    return "\n".join(lines)


def build_yaml(form: dict) -> str:
    shipped = sorted(form.get("canvas_shipped") or [])
    session = form.get("canvas_session_picks") or []
    open_rows = form.get("open_questions") or []
    open_ids = [str(q["id"]) for q in open_rows]
    v2 = form.get("v2_answers", {}).get("rows") or []

    shipped_set = set(shipped)
    sync_pending = sorted(shipped_set & set(open_ids))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "schema: founder-picks-locked-v2",
        f'updated: "{today}"',
        f"synced_at: {_yaml_quote(_now())}",
        "sync_source: live_founder_decision_form_v1.py --json",
        "",
        "form_v2:",
        _yaml_pick_rows([{"id": r["id"], "pick": r["pick"]} for r in v2], indent=2),
        "",
        "canvas_shipped:",
        _yaml_list(shipped, indent=2),
        "",
        "batch_confirmed:",
        f'  date: "{today}"',
        "  status: confirmed_asf",
        "  ship_status: shipped_maintainer_2026-06-12",
        '  effect: "RT LIVE met · resume Phases 3–10 · parallel W1+W3 · batch on disk"',
        "  threads: [THREAD-INTEGRITY-100, THREAD-ECOSYSTEM, THREAD-MAINTAINER, THREAD-ENFORCEMENT, THREAD-NOETFIELD-W3]",
        "  formal_block: |",
    ]
    for block_line in BATCH_FORMAL_BLOCK.splitlines():
        lines.append(f"    {block_line}")
    lines.extend(
        [
            "  picks:",
            _yaml_pick_rows([{"id": p["id"], "pick": p["pick"]} for p in session], indent=4),
            "",
            "canvas_pending_ship: []",
            "",
            "form_v2_sync_pending:",
            _yaml_list(sync_pending, indent=2) if sync_pending else "  []",
            "",
            "form_official:",
            f"  open_count: {len(open_ids)}",
            f"  awaiting_founder_picks: {str(bool(form.get('awaiting_founder_picks'))).lower()}",
            f"  needs_asf_fill: {str(bool(form.get('needs_asf_fill'))).lower()}",
            "  canvas_ssot: sourcea-system-integrity-100.canvas.tsx",
            "  canvas_view: my-chat-lane",
            "  chat_lane_default: anchor",
            "",
            "open_question_ids:",
            _yaml_list(open_ids, indent=2),
            "",
            "chat_lane_open_counts:",
            "  anchor: 4",
            "  maintainer_2: 7",
            "  commercial: 21",
            "  gov: 3",
            "  aect: 3",
            "  maintainer_1: 3",
            "  research: 2",
            "  brain: 0",
            "",
            "maintainer_p0:",
            f'  - "FORM_OFFICIAL: {len(open_ids)} open rows — M1 Canvas My chat lane"',
            '  - "Apply confirms: founder Hub Submit only — agents never canvas_form_apply_picks_v1.py --apply (INCIDENT-037)"',
            '  - "validate-integrity-form-canvas-ssot-v1.sh PASS on form/canvas touch"',
            '  - "sync_picks_locked_v1.py after form/canvas touch"',
            '  - "FR-003 EXTERNAL_CRITIC wiring"',
            '  - "Phase 1.10 seal (Q-1.10-SEAL)"',
            f'  - "form_v2_sync_pending: {", ".join(sync_pending) or "none"}"',
            '  - "W1 film + W3 batch 1 (9.07 A locked)"',
            "",
            "parallel_execution_p0:",
            "  - thread: THREAD-ENFORCEMENT",
            '    action: "Film W1 demo · write-path validator"',
            "  - thread: THREAD-NOETFIELD-W3",
            '    action: "W3 outreach batch 1"',
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Exit 1 if any target differs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    form = _load_form()
    body = build_yaml(form)
    stale: list[str] = []

    for path in TARGETS:
        if not path.parent.is_dir():
            print(f"WARN: skip missing dir {path.parent}", file=sys.stderr)
            continue
        if path.is_file() and path.read_text(encoding="utf-8") == body:
            print(f"OK: {path} · already synced")
            continue
        if args.check:
            stale.append(str(path))
            continue
        if args.dry_run:
            print(f"DRY: would write {path}")
            continue
        path.write_text(body, encoding="utf-8")
        print(f"OK: synced {path}")

    if args.check and stale:
        print("FAIL: stale picks-locked.yaml:", ", ".join(stale), file=sys.stderr)
        return 1
    if not args.check and not args.dry_run:
        print(
            f"OK: sync_picks_locked_v1 · open={form.get('open_questions_count')} · "
            f"shipped={len(form.get('canvas_shipped') or [])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
