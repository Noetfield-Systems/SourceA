#!/usr/bin/env python3
"""One-word keyword → live context → PROMPT_CATALOG template → assembled prompt.

Keywords: implement | fix | debug | 10loop | PLAN WITH NO ASF
Lane: --lane or SINA_PROMPT_LANE env (default: sourcea)

Wiring (header only — plan-no-asf-run.sh may call this router):
  python3 scripts/prompt_router.py --keyword "PLAN WITH NO ASF" --lane sourcea
  python3 scripts/prompt_router.py --keyword implement --lane sourcea --dry-run
  python3 scripts/prompt_router.py --keyword implement --lane sourcea --invoke-loop
  python3 scripts/prompt_router.py --l1-cycle --keyword implement --lane sourcea --json

L1 semi-auto cycle (--l1-cycle): read REPO_EXECUTION_LOGS closeout → route next prompt
→ append reducer summary to ~/.sina/llm_context_packet_v1.json tail only (auto-paste OFF).

Loads: ARCHITECT_REPORT.yaml, GLOBAL_BLOCKERS.json, pick-sourcea-no-asf-plan (sourcea lane).
Selects: SinaPromptOS core/prompt_library.py PROMPT_CATALOG.
Optional: --invoke-loop → scripts/agent_loop.py handle_action(start).
Emits: ~/.sina/agent-governance-events.jsonl via agent_governance_events.log_governance_event.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ARCHITECT_REPORT = ROOT / "ARCHITECT_REPORT.yaml"
GLOBAL_BLOCKERS = ROOT / "GLOBAL_BLOCKERS.json"
EXEC_LOGS_DIR = ROOT / "REPO_EXECUTION_LOGS"
LOG_LANE_MAP = {"sourcea": "sourcea", "mono": "sinaai_mono"}

L1_CYCLE_LIMITATIONS = [
    "L1 semi-auto — manual Cursor paste + Submit round required (auto-paste OFF)",
    "Reducer reads last REPO_EXECUTION_LOGS YAML — not live clipboard ingest",
    "Tail-only packet write — D15 latest/builds SSOT untouched",
    "No zero-human claim — Level 3 blockers remain (eval, dispatch, SDK)",
]
PROMPTOS_ROOT = Path.home() / "Desktop" / "SinaPromptOS"

LANE_ROOTS: dict[str, Path] = {
    "sourcea": ROOT,
    "sinaai": Path.home() / "Desktop" / "SinaaiDataBase",
    "mono": Path.home() / "Desktop" / "SinaaiMonoRepo",
    "trustfield": Path.home() / "Desktop" / "TrustField Technologies",
    "virlux": Path.home() / "Desktop" / "VIRLUX",
    "noetfield": Path.home() / "Desktop" / "SinaaiMonoRepo",
    "seven77": Path.home() / "Desktop" / "The 777 Foundation",
    "wire": Path.home() / "Desktop" / "AI Dev Bridge OS",
}

READY_TO_PASTE: dict[str, str] = {
    "trustfield": "ready_to_paste_trustfield.txt",
    "mono": "ready_to_paste_sinaai_mono.txt",
    "virlux": "ready_to_paste_virlux.txt",
    "noetfield": "ready_to_paste_noetfield.txt",
    "seven77": "ready_to_paste_seven77.txt",
    "wire": "ready_to_paste_wire.txt",
}

MONO_PICK = Path.home() / "Desktop" / "SinaaiMonoRepo" / "scripts" / "pick-mono-no-asf-plan.py"
READY_DIR = PROMPTOS_ROOT / "outputs" / "ready_to_paste"

KEYWORD_CATALOG: dict[str, str | None] = {
    "implement": "cursor-one-outcome",
    "fix": "test-gap",
    "debug": "debug-root-cause",
    "10loop": None,
    "plan with no asf": None,
}

REGISTRY_IDLE_TASK_ID = "registry-exhausted-idle"

LOOP_TEMPLATE = """Start a 10-round Sina agent loop.

PRIMARY GOAL (round 1 seed):
{goal}

RULES:
- Execute each [SINA_LOOP N/10] task fully before Submit round.
- Founder uses Private agents → Submit round (never Terminal).
- Executor may POST /api/agent-loop action=response when a round completes.
- Read workspace law + os/plan.json before editing.

LIVE CONTEXT:
{context_block}

OUTPUT each round: 1) Changes 2) VERIFY (raw command output) 3) plan.json or REGISTRY update if applicable"""


def _normalize_keyword(raw: str) -> str:
    return " ".join((raw or "").strip().lower().split())


def _load_prompt_catalog() -> list[dict[str, Any]]:
    if not PROMPTOS_ROOT.is_dir():
        raise SystemExit(f"SinaPromptOS not found: {PROMPTOS_ROOT}")
    if str(PROMPTOS_ROOT) not in sys.path:
        sys.path.insert(0, str(PROMPTOS_ROOT))
    from core.prompt_library import PROMPT_CATALOG  # noqa: WPS433

    return PROMPT_CATALOG


def _catalog_by_id(catalog: list[dict[str, Any]], prompt_id: str) -> dict[str, Any] | None:
    for entry in catalog:
        if entry.get("id") == prompt_id:
            return entry
    return None


def _load_yaml_blockers() -> list[dict[str, Any]]:
    if not ARCHITECT_REPORT.is_file():
        return []
    try:
        import yaml  # noqa: WPS433
    except ImportError:
        text = ARCHITECT_REPORT.read_text(encoding="utf-8")
        blockers: list[dict[str, Any]] = []
        in_blockers = False
        for line in text.splitlines():
            if line.startswith("system_blockers:"):
                in_blockers = True
                continue
            if in_blockers and line and not line.startswith((" ", "-", "#")):
                break
            if in_blockers and line.strip().startswith("- id:"):
                blockers.append({"id": line.split(":", 1)[1].strip()})
        return blockers
    data = yaml.safe_load(ARCHITECT_REPORT.read_text(encoding="utf-8")) or {}
    return list(data.get("system_blockers") or [])


def _load_global_blockers(lane: str) -> list[dict[str, Any]]:
    if not GLOBAL_BLOCKERS.is_file():
        return []
    data = json.loads(GLOBAL_BLOCKERS.read_text(encoding="utf-8"))
    rows = list(data.get("blockers") or [])
    lane_key = lane.lower()
    if lane_key == "sourcea":
        return rows
    return [r for r in rows if (r.get("project_id") or "").lower() == lane_key]


def _pick_mono_plan() -> dict[str, Any] | None:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from mono_progress_pulse_v1 import pick_allowed  # noqa: WPS433

        gate = pick_allowed()
        if gate.get("blocked"):
            return {
                "blocked": True,
                "reason": gate.get("reason") or "commercial_L3_pending",
                "commercial_l3_pct": gate.get("commercial_l3_pct"),
                "agent_prompt": (
                    f"MONO PICK BLOCKED — commercial L3 {gate.get('commercial_l3_pct')}% < 90% · "
                    "complete fundmore/ocree founder send first"
                ),
            }
    except Exception:
        pass
    if not MONO_PICK.is_file():
        return None
    proc = subprocess.run(
        [sys.executable, str(MONO_PICK), "--any-tier", "--limit", "1", "--json"],
        capture_output=True,
        text=True,
        cwd=str(LANE_ROOTS["mono"]),
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        picked = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not picked:
        return None
    row = picked[0]
    if not row.get("agent_prompt"):
        row["agent_prompt"] = f"PLAN WITH NO ASF — {row.get('id')}: {row.get('title', '')}"
    return row


def _load_ready_to_paste(lane: str) -> str | None:
    fname = READY_TO_PASTE.get(lane)
    if not fname:
        return None
    path = READY_DIR / fname
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").strip()


def _pick_for_lane(lane: str) -> dict[str, Any] | None:
    if lane == "sourcea":
        return _pick_sourcea_plan()
    if lane == "mono":
        return _pick_mono_plan()
    return None


def _pick_by_id(lane: str, task_id: str) -> dict[str, Any] | None:
    if lane == "sourcea":
        reg = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
    elif lane == "mono":
        reg = Path.home() / "Desktop" / "SinaaiMonoRepo" / "os" / "plan-library" / "mono-1000" / "REGISTRY.json"
    else:
        return None
    if not reg.is_file():
        return None
    data = json.loads(reg.read_text(encoding="utf-8"))
    for pl in data.get("plans") or []:
        if pl.get("id") == task_id:
            return pl
    return None


def _pick_sourcea_plan() -> dict[str, Any] | None:
    pick_script = SCRIPTS / "pick-sourcea-no-asf-plan.py"
    if not pick_script.is_file():
        return None
    proc = subprocess.run(
        [sys.executable, str(pick_script), "--any-tier", "--limit", "1", "--json"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        picked = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not picked:
        return None
    return picked[0]


def _sourcea_registry_exhausted() -> bool:
    fn = Path.home() / ".sina" / "factory-now-v1.json"
    if fn.is_file():
        try:
            row = json.loads(fn.read_text(encoding="utf-8"))
            if int(row.get("backlog") or 0) == 0 and int(row.get("valid_yes") or 0) >= 1000:
                return True
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return _pick_sourcea_plan() is None


def _registry_idle_pick() -> dict[str, Any]:
    return {
        "id": REGISTRY_IDLE_TASK_ID,
        "title": "Goal 1 registry exhausted — honest 1000/1000 idle",
        "agent_prompt": (
            "REGISTRY EXHAUSTED — Goal 1 honest 1000/1000 complete. "
            "No agent-runnable backlog until founder/ASF names next pack. "
            "Worker Hub → Next steps for commercial P0 glance only."
        ),
        "status": "idle",
    }


def _architect_summary() -> str:
    blockers = _load_yaml_blockers()
    if not blockers:
        return "No system_blockers in ARCHITECT_REPORT.yaml"
    lines = []
    for b in blockers[:5]:
        title = b.get("title") or b.get("id") or "blocker"
        detail = (b.get("detail") or b.get("recommended_action") or "")[:120]
        lines.append(f"- {title}: {detail}".strip(": "))
    return "\n".join(lines)


def _blockers_summary(lane: str) -> str:
    rows = _load_global_blockers(lane)
    if not rows:
        return f"No GLOBAL_BLOCKERS for lane={lane}"
    lines = []
    for r in rows[:6]:
        name = r.get("name") or r.get("project_id") or "?"
        item = r.get("item") or ""
        reason = r.get("reason") or ""
        tail = f" ({reason})" if reason else ""
        lines.append(f"- {name}: {item}{tail}")
    return "\n".join(lines)


def _context_block(*, lane: str, keyword: str, pick: dict[str, Any] | None) -> str:
    parts = [
        f"Lane: {lane}",
        f"Keyword: {keyword}",
        f"Repo root: {LANE_ROOTS.get(lane, ROOT)}",
        "",
        "ARCHITECT_REPORT system_blockers:",
        _architect_summary(),
        "",
        "GLOBAL_BLOCKERS:",
        _blockers_summary(lane),
    ]
    if pick:
        parts.extend(
            [
                "",
                f"Next task: {pick.get('id')} — {pick.get('title', '')[:100]}",
                f"Verify: {pick.get('verify', '')}",
                f"Prompt path: {pick.get('path', '')}",
            ]
        )
    ready = _load_ready_to_paste(lane)
    if ready:
        parts.extend(["", "ready_to_paste (first 400 chars):", ready[:400] + ("…" if len(ready) > 400 else "")])
    return "\n".join(parts)


def _live_variables(
    *,
    lane: str,
    keyword: str,
    pick: dict[str, Any] | None,
    catalog_entry: dict[str, Any] | None,
) -> dict[str, str]:
    repo_path = str(LANE_ROOTS.get(lane, ROOT))
    pick_title = (pick or {}).get("title") or "top next_tasks[0] in os/plan.json"
    pick_verify = (pick or {}).get("verify") or "cd scripts && python3 find_critical_bugs.py"
    agent_prompt = (pick or {}).get("agent_prompt") or pick_title
    ready_snippet = (_load_ready_to_paste(lane) or "")[:800]
    if lane in ("sourcea", "mono") and keyword in ("implement", "plan with no asf"):
        outcome = agent_prompt
    elif ready_snippet:
        outcome = ready_snippet
    else:
        outcome = pick_title

    defaults: dict[str, str] = {
        "repo": repo_path,
        "outcome": outcome,
        "symptom": pick_title if pick else "hub or validator failure",
        "context": _context_block(lane=lane, keyword=keyword, pick=pick),
        "scope": f"{repo_path} — current task + validators",
        "project": lane,
        "goal": agent_prompt if pick else f"ship one verifiable outcome on {lane}",
        "module": pick.get("path", "scripts/") if pick else "scripts/",
        "pain": pick_title,
        "area": pick.get("id", "active lane") if pick else lane,
        "risk": "REGISTRY drift or validator fail without fix",
        "role": "SourceA maintainer agent",
        "alert": pick_title if pick else "validator or hub regression",
        "timeline": "current session",
    }

    if catalog_entry:
        if str(PROMPTOS_ROOT) not in sys.path:
            sys.path.insert(0, str(PROMPTOS_ROOT))
        from core.prompt_library import default_variables  # noqa: WPS433

        base = default_variables(catalog_entry)
        for key, val in defaults.items():
            if val and val != "…":
                base[key] = val
        return base
    return defaults


def _assemble_prompt(
    *,
    keyword: str,
    lane: str,
    catalog: list[dict[str, Any]],
    pick: dict[str, Any] | None,
) -> dict[str, Any]:
    norm = _normalize_keyword(keyword)
    if norm not in KEYWORD_CATALOG:
        known = ", ".join(sorted(KEYWORD_CATALOG))
        raise SystemExit(f"Unknown keyword {keyword!r}. Known: {known}")

    context_block = _context_block(lane=lane, keyword=norm, pick=pick)
    catalog_id = KEYWORD_CATALOG[norm]
    meta: dict[str, Any] = {
        "keyword": norm,
        "lane": lane,
        "catalog_id": catalog_id,
        "pick_id": (pick or {}).get("id"),
    }

    if norm == "plan with no asf":
        if not pick:
            ready = _load_ready_to_paste(lane)
            if ready:
                prompt = f"{ready}\n\n--- LIVE CONTEXT ---\n{context_block}"
                meta["source"] = "ready_to_paste"
                return {"prompt": prompt.strip(), "meta": meta}
            if lane == "sourcea" and _sourcea_registry_exhausted():
                idle = _registry_idle_pick()
                meta["pick_id"] = idle["id"]
                meta["source"] = "registry_exhausted_idle"
                meta["registry_exhausted"] = True
                prompt = f"{idle['agent_prompt']}\n\n--- LIVE CONTEXT ---\n{context_block}"
                return {"prompt": prompt.strip(), "meta": meta}
            raise SystemExit("PLAN WITH NO ASF requires pick or ready_to_paste — no agent-runnable backlog")
        body = (pick.get("agent_prompt") or "").strip()
        if not body:
            body = f"PLAN WITH NO ASF — {pick.get('id')}: {pick.get('title')}"
        prompt = f"{body}\n\n--- LIVE CONTEXT ---\n{context_block}"
        meta["source"] = "pick-sourcea-no-asf-plan"
        return {"prompt": prompt.strip(), "meta": meta}

    if norm == "10loop":
        goal = (pick or {}).get("agent_prompt") or (pick or {}).get("title") or "complete top backlog item with verify"
        prompt = LOOP_TEMPLATE.format(goal=goal, context_block=context_block)
        meta["source"] = "10loop_template"
        return {"prompt": prompt.strip(), "meta": meta}

    entry = _catalog_by_id(catalog, catalog_id or "")
    if not entry:
        raise SystemExit(f"Catalog entry missing: {catalog_id}")

    if str(PROMPTOS_ROOT) not in sys.path:
        sys.path.insert(0, str(PROMPTOS_ROOT))
    from core.prompt_library import fill_template  # noqa: WPS433

    values = _live_variables(lane=lane, keyword=norm, pick=pick, catalog_entry=entry)
    filled = fill_template(entry["template"], values)
    prompt = f"{filled}\n\n--- LIVE CONTEXT ---\n{context_block}"
    meta["source"] = "prompt_catalog"
    meta["catalog_title"] = entry.get("title")
    return {"prompt": prompt.strip(), "meta": meta}


def _log_event(*, keyword: str, lane: str, meta: dict[str, Any], dry_run: bool, invoked_loop: bool) -> None:
    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "prompt_router",
        workspace_id=lane,
        detail=f"keyword={keyword} pick={meta.get('pick_id') or '-'} catalog={meta.get('catalog_id') or '-'}",
        extra={
            "keyword": keyword,
            "lane": lane,
            "dry_run": dry_run,
            "invoke_loop": invoked_loop,
            "pick_id": meta.get("pick_id"),
            "catalog_id": meta.get("catalog_id"),
            "source": meta.get("source"),
        },
    )


def _maybe_invoke_loop(goal: str) -> dict[str, Any]:
    from agent_loop import handle_action  # noqa: WPS433

    return handle_action(
        {
            "action": "start",
            "goal": goal,
            "max_rounds": 10,
            "trigger_source": "prompt_router",
        }
    )


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Minimal YAML for REPO_EXECUTION_LOGS closeout files (no PyYAML required)."""
    try:
        import yaml  # noqa: WPS433

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    out: dict[str, Any] = {}
    nested_key: str | None = None
    nested: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s{2,}\S", line) and nested_key:
            m = re.match(r"^\s+(\w+):\s*(.*)$", line)
            if m:
                val = m.group(2).strip().strip("'\"")
                if val.lower() in ("true", "false"):
                    nested[m.group(1)] = val.lower() == "true"
                else:
                    nested[m.group(1)] = val
            continue
        if nested_key:
            out[nested_key] = nested
            nested_key = None
            nested = {}
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip("'\"")
        if not val:
            nested_key = key
            nested = {}
            continue
        if val.lower() in ("true", "false"):
            out[key] = val.lower() == "true"
        elif re.match(r"^-?\d+(\.\d+)?$", val):
            out[key] = float(val) if "." in val else int(val)
        else:
            out[key] = val
    if nested_key:
        out[nested_key] = nested
    return out


def _read_last_closeout(lane: str) -> dict[str, Any]:
    log_lane = LOG_LANE_MAP.get(lane, lane)
    latest = EXEC_LOGS_DIR / log_lane / "latest.yaml"
    if not latest.is_file():
        return {"ok": False, "error": f"missing {latest}", "path": str(latest)}
    text = latest.read_text(encoding="utf-8")
    parsed = _parse_simple_yaml(text)
    return {
        "ok": True,
        "path": str(latest),
        "raw": parsed,
        "last_task": parsed.get("last_task") or (parsed.get("evidence") or {}).get("task_id") or parsed.get("task"),
        "verify_passed": parsed.get("verify_passed"),
        "next_task": parsed.get("next_task"),
        "status": parsed.get("status"),
        "reported_at": parsed.get("reported_at"),
    }


def _build_reducer_summary(
    *,
    closeout: dict[str, Any],
    pick: dict[str, Any] | None,
    meta: dict[str, Any],
    prompt_preview: str,
) -> dict[str, Any]:
    raw = closeout.get("raw") or {}
    last_task = closeout.get("last_task") or "unknown"
    next_id = (pick or {}).get("id") or meta.get("pick_id") or closeout.get("next_task") or "unknown"
    verify_ok = closeout.get("verify_passed")
    architect = _architect_summary()
    blockers = _blockers_summary(meta.get("lane") or "sourcea")
    summary_lines = [
        f"Closeout ingest: {last_task} status={closeout.get('status')} verify_passed={verify_ok}",
        f"Next route: {next_id} keyword={meta.get('keyword')} lane={meta.get('lane')}",
        f"Architect: {architect.splitlines()[0] if architect else 'n/a'}",
        f"Blockers: {blockers.splitlines()[0] if blockers else 'n/a'}",
        "Founder: copy routed prompt → Cursor manually (auto_paste=OFF).",
    ]
    return {
        "at": datetime.now(timezone.utc).isoformat(),
        "producer": "L1-ingest-reducer",
        "auto_paste": False,
        "summary": "\n".join(summary_lines),
        "closeout_path": closeout.get("path"),
        "last_task": last_task,
        "next_task_id": next_id,
        "verify_passed": verify_ok,
        "routed": {
            "keyword": meta.get("keyword"),
            "lane": meta.get("lane"),
            "pick_id": meta.get("pick_id"),
            "catalog_id": meta.get("catalog_id"),
            "source": meta.get("source"),
        },
        "prompt_preview": prompt_preview[:600],
        "limitations": list(L1_CYCLE_LIMITATIONS),
        "tests_status": (raw.get("tests") or {}).get("status") if isinstance(raw.get("tests"), dict) else None,
    }


def run_l1_cycle(
    *,
    keyword: str,
    lane: str,
    dry_run: bool = False,
    task_id: str = "",
    catalog: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """L1 semi-auto: closeout ingest → route next prompt → tail reducer (no auto-paste)."""
    closeout = _read_last_closeout(lane)
    cat = catalog if catalog is not None else _load_prompt_catalog()

    pick: dict[str, Any] | None = None
    if task_id:
        pick = _pick_by_id(lane, task_id)
        if not pick:
            return {"ok": False, "error": f"task-id not found: {task_id}", "closeout": closeout}
    elif lane in ("sourcea", "mono"):
        pick = _pick_for_lane(lane)

    assembled = _assemble_prompt(keyword=keyword, lane=lane, catalog=cat, pick=pick)
    prompt = assembled["prompt"]
    meta = assembled["meta"]
    reducer = _build_reducer_summary(closeout=closeout, pick=pick, meta=meta, prompt_preview=prompt)

    tail_result: dict[str, Any] | None = None
    if not dry_run:
        sys.path.insert(0, str(SCRIPTS))
        from pre_llm.context_assembly.store import write_tail_section  # noqa: WPS433

        tail_result = write_tail_section(entry=reducer)

    return {
        "ok": True,
        "schema": "l1-semi-auto-cycle-v1",
        "auto_paste": False,
        "limitations": list(L1_CYCLE_LIMITATIONS),
        "closeout": closeout,
        "routed": {"ok": True, "meta": meta, "prompt": prompt},
        "reducer": reducer,
        "tail": tail_result or {"ok": False, "skipped": True, "reason": "dry_run"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Route one-word keyword to assembled agent prompt")
    parser.add_argument("--keyword", default="", help="implement | fix | debug | 10loop | PLAN WITH NO ASF")
    parser.add_argument("keyword_pos", nargs="?", default="", help=argparse.SUPPRESS)
    parser.add_argument("--lane", default=os.environ.get("SINA_PROMPT_LANE", "sourcea"))
    parser.add_argument("--dry-run", action="store_true", help="Print assembled prompt; do not start agent loop")
    parser.add_argument("--invoke-loop", action="store_true", help="Call agent_loop.handle_action(start) with prompt")
    parser.add_argument("--json", action="store_true", help="Emit JSON envelope instead of prompt body only")
    parser.add_argument("--task-id", default="", help="Force REGISTRY task id (scheduler-bound)")
    parser.add_argument(
        "--l1-cycle",
        action="store_true",
        help="L1 semi-auto: ingest closeout YAML → route next prompt → packet tail reducer",
    )
    args = parser.parse_args()

    lane = (args.lane or "sourcea").strip().lower()
    kw_raw = (args.keyword or args.keyword_pos or "implement").strip()
    if not kw_raw:
        raise SystemExit("--keyword required (or positional: implement)")
    keyword = _normalize_keyword(kw_raw)
    catalog = _load_prompt_catalog()

    if args.l1_cycle:
        cycle = run_l1_cycle(
            keyword=keyword,
            lane=lane,
            dry_run=args.dry_run,
            task_id=(args.task_id or "").strip(),
            catalog=catalog,
        )
        _log_event(
            keyword=f"l1-cycle:{keyword}",
            lane=lane,
            meta={
                "pick_id": (cycle.get("routed") or {}).get("meta", {}).get("pick_id"),
                "source": "l1-semi-auto-cycle",
                "closeout_task": (cycle.get("closeout") or {}).get("last_task"),
            },
            dry_run=args.dry_run,
            invoked_loop=False,
        )
        print(json.dumps(cycle, indent=2, ensure_ascii=False))
        if not cycle.get("ok"):
            raise SystemExit(1)
        return

    pick: dict[str, Any] | None = None
    if args.task_id:
        tid = args.task_id.strip()
        if tid == REGISTRY_IDLE_TASK_ID:
            pick = _registry_idle_pick()
        else:
            pick = _pick_by_id(lane, tid)
            if not pick:
                raise SystemExit(f"task-id not found in REGISTRY: {args.task_id}")
    elif lane in ("sourcea", "mono") or keyword in ("implement", "plan with no asf"):
        pick = _pick_for_lane(lane if lane in ("sourcea", "mono") else "sourcea")
        if not pick and lane == "sourcea" and _sourcea_registry_exhausted():
            pick = _registry_idle_pick()

    assembled = _assemble_prompt(keyword=keyword, lane=lane, catalog=catalog, pick=pick)
    prompt = assembled["prompt"]
    meta = assembled["meta"]

    loop_result: dict[str, Any] | None = None
    if args.invoke_loop and not args.dry_run:
        loop_result = _maybe_invoke_loop(prompt)

    _log_event(
        keyword=keyword,
        lane=lane,
        meta=meta,
        dry_run=args.dry_run,
        invoked_loop=bool(args.invoke_loop and not args.dry_run),
    )

    if args.json:
        out = {"ok": True, "meta": meta, "prompt": prompt}
        if loop_result is not None:
            out["loop"] = loop_result
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    if args.dry_run:
        print(f"# prompt_router dry-run keyword={keyword} lane={lane} pick={meta.get('pick_id')}")
        print(prompt)
        return

    print(prompt)
    if loop_result is not None:
        print("\n--- agent_loop start ---")
        print(json.dumps(loop_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
