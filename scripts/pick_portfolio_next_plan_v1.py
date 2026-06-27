#!/usr/bin/env python3
"""Pick next portfolio-next-6000 plan — phase-first backlog drain."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SOURCEA_ROOT = Path(__file__).resolve().parents[1]
PACK_BASE = SOURCEA_ROOT / "brain-os" / "plan-registry" / "portfolio-next-6000"

REPOS = ("sourcea", "witnessbc", "noetfield", "trustfield", "virlux", "mono")
PHASE_ORDER = ("NOW", "NEXT", "LATER", "MOONSHOT")
OPEN_STATUS = frozenset({"open", "backlog"})


def _expand(path: str) -> Path:
    return Path(path.replace("~", str(Path.home())))


def crm_outreach_note() -> str | None:
    for rel in (
        "~/.sina/sourcea-revenue-engine-crm-v1.json",
        "data/sourcea-revenue-engine-crm-pipeline-v1.json",
    ):
        p = _expand(rel) if rel.startswith("~") else SOURCEA_ROOT / rel
        if not p.is_file():
            continue
        try:
            crm = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        contacts = crm.get("contacts") or crm.get("pipeline") or []
        open_outreach = [
            c
            for c in contacts
            if c.get("stage") in {"lead", "outreach_sent", "conversation"}
        ]
        if open_outreach:
            names = ", ".join(c.get("name", c.get("id", "?")) for c in open_outreach[:3])
            return f"Revenue Engine: {len(open_outreach)} open CRM row(s) — {names}"
    return None


def pick_plans(
    plans: list[dict],
    *,
    phases: list[str] | None = None,
    limit: int = 3,
) -> list[dict]:
    phase_list = phases or list(PHASE_ORDER)
    picked: list[dict] = []
    for phase in phase_list:
        candidates = [
            p
            for p in plans
            if p.get("phase") == phase and p.get("status") in OPEN_STATUS
        ]
        candidates.sort(key=lambda p: (p.get("priority_rank", 9999), p.get("id", "")))
        for pl in candidates:
            picked.append(pl)
            if len(picked) >= limit:
                return picked
    return picked


def load_registry(repo: str) -> dict:
    reg_path = PACK_BASE / repo / "REGISTRY.json"
    if not reg_path.is_file():
        raise SystemExit(f"Missing registry: {reg_path}")
    return json.loads(reg_path.read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description="Pick portfolio-next-6000 plan")
    p.add_argument("--repo", default="sourcea", choices=REPOS)
    p.add_argument("--phase", action="append", help="Filter phase (repeatable)")
    p.add_argument("--any-phase", action="store_true", help="All phases phase-first")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt", action="store_true", help="Print prompt body for first pick")
    args = p.parse_args()

    reg = load_registry(args.repo)
    phases = None if args.any_phase or not args.phase else args.phase
    picked = pick_plans(reg["plans"], phases=phases, limit=args.limit)

    note = crm_outreach_note() if args.repo == "sourcea" else None

    if args.json:
        out = {"picks": picked, "repo": args.repo, "revenue_note": note}
        print(json.dumps(out, indent=2))
        return 0 if picked else 1

    if note:
        print(f"# {note}")
        print("")

    if not picked:
        print(f"No open plans in {args.repo} pack")
        return 1

    pack = PACK_BASE / args.repo
    for pl in picked:
        legacy = pl.get("legacy_upgrade_id", "")
        tag = f" ({legacy})" if legacy else ""
        print(f"{pl['id']}\t{pl['path']}\t{pl['title'][:72]}{tag}")

    first = picked[0]
    print("")
    print(f"Verify: cd ~/Desktop/SourceA && python3 scripts/sourcea_revenue_engine_crm_v1.py summary --json")
    if args.prompt:
        prompt_path = pack / first["path"]
        if prompt_path.is_file():
            print("")
            print(prompt_path.read_text(encoding="utf-8"))
        else:
            print(first.get("agent_prompt", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
