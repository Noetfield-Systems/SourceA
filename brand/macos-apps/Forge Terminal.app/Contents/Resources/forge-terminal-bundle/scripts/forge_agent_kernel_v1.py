#!/usr/bin/env python3
"""Forge Self-Dev Kernel v1 — plan → tool act → verify loop (Level 1 + L2 self-improve).

Law: Mac control plane may dispatch; kernel runs bounded tools inside open workspace only.
Receipt: ~/.sina/forge-agent-kernel-latest-v1.json
L2 receipt: ~/.sina/forge-agent-self-improve-latest-v1.json
"""
from __future__ import annotations

import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from difflib import unified_diff
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-agent-kernel-latest-v1.json"
SELF_IMPROVE_RECEIPT = SINA / "forge-agent-self-improve-latest-v1.json"
MAX_STEPS = 8
MAX_REPAIR_ROUNDS = 2
MAX_FILE_BYTES = 512_000
MAX_SHELL_SEC = 90

FORBIDDEN_PATH = re.compile(
    r"(^|/)(\.env|secrets\.env|\.git/|node_modules/|\.sina/)|"
    r"(rm\s+-rf|sudo\s+|curl\s+.*\|.*sh|chmod\s+777)",
    re.I,
)

SHELL_ALLOW = re.compile(
    r"^(pytest|python3\s+-m\s+pytest|npm\s+(test|run\s+build)|"
    r"bash\s+scripts/[\w./\-]+\.sh|"
    r"python3\s+scripts/forge_terminal_living_ui_e2e_verify_v1\.py|"
    r"python3\s+scripts/forge_terminal_reply_contract_v1\.py|"
    r"python3\s+[\w./\-]+\.py)(\s|$)",
    re.I,
)

PLANNER_SYSTEM = """You are a software engineer agent inside Forge Terminal.
You have tools (respond with ONE JSON object only, no markdown fences):
{
  "done": false,
  "summary": "one line progress",
  "action": {
    "tool": "read_file|write_file|patch_file|list_files|search_code|run_shell",
    "args": {}
  }
}

Tool args:
- read_file: {"path": "relative/path"}
- write_file: {"path": "rel/path", "content": "full file"}
- patch_file: {"path": "rel/path", "search": "exact snippet", "replace": "new snippet"}
- list_files: {"prefix": "optional/dir", "limit": 40}
- search_code: {"query": "string", "limit": 20}
- run_shell: {"cmd": "pytest or npm test only"}

Rules:
- Work ONLY inside the open workspace.
- Do NOT explain prose — take actions until done=true.
- After each write/patch, prefer run_shell to verify.
- Set done=true only when goal is satisfied and verify passed.
- Never delete whole repo; use patch_file for edits when possible."""

SELF_IMPROVE_PLANNER = """You are a self-healing engineer inside Forge Terminal (Level 2).
Quality gate FAILED — fix the repo with minimal patches.

Respond ONE JSON object only:
{"done": false, "summary": "...", "action": {"tool": "...", "args": {...}}}

PRIORITY:
1. patch_file (preferred) — small targeted fixes
2. read_file + search_code to locate issues
3. run_shell to verify (pytest / npm test)
4. write_file ONLY for brand-new small files explicitly required

Do NOT rewrite large files whole. Do NOT explain — act until done=true and tests pass."""

VERIFIER_SYSTEM = """You are a verifier agent for Forge Terminal.
Given goal + last action result, reply JSON only:
{"pass": true|false, "note": "short reason"}
Pass only if change matches goal and no obvious breakage."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_receipt(row: dict[str, Any]) -> None:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _safe_rel(root: Path, rel: str) -> Path | None:
    rel = (rel or "").strip().lstrip("/")
    if not rel or ".." in rel.split("/"):
        return None
    if FORBIDDEN_PATH.search(rel):
        return None
    fp = (root / rel).resolve()
    try:
        fp.relative_to(root.resolve())
    except ValueError:
        return None
    return fp


class ForgeAgentTools:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def read_file(self, path: str) -> dict[str, Any]:
        fp = _safe_rel(self.root, path)
        if not fp or not fp.is_file():
            return {"ok": False, "error": "read_denied_or_missing", "path": path}
        if fp.stat().st_size > MAX_FILE_BYTES:
            return {"ok": False, "error": "file_too_large", "path": path}
        return {"ok": True, "path": path, "content": fp.read_text(encoding="utf-8", errors="replace")}

    def write_file(self, path: str, content: str, *, dry_run: bool = False) -> dict[str, Any]:
        fp = _safe_rel(self.root, path)
        if not fp:
            return {"ok": False, "error": "write_denied", "path": path}
        if FORBIDDEN_PATH.search(str(content)[:500]):
            return {"ok": False, "error": "content_forbidden"}
        if dry_run:
            return {"ok": True, "dry_run": True, "path": path, "bytes": len(content)}
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return {"ok": True, "path": path, "bytes": len(content)}

    def patch_file(self, path: str, search: str, replace: str, *, dry_run: bool = False) -> dict[str, Any]:
        read = self.read_file(path)
        if not read.get("ok"):
            return read
        old = read["content"]
        if search not in old:
            return {"ok": False, "error": "search_not_found", "path": path}
        new = old.replace(search, replace, 1)
        diff = "\n".join(
            unified_diff(old.splitlines(), new.splitlines(), fromfile=path, tofile=path, lineterm="")
        )
        if dry_run:
            return {"ok": True, "dry_run": True, "path": path, "diff": diff[:4000]}
        return {**self.write_file(path, new), "diff": diff[:4000]}

    def list_files(self, prefix: str = "", limit: int = 40) -> dict[str, Any]:
        base = _safe_rel(self.root, prefix or ".") or self.root
        if not base.is_dir():
            base = self.root
        out: list[str] = []
        for p in sorted(base.rglob("*")):
            if len(out) >= min(limit, 80):
                break
            if any(part.startswith(".") and part not in (".sourcea",) for part in p.parts):
                continue
            if "node_modules" in p.parts:
                continue
            try:
                rel = p.relative_to(self.root).as_posix()
            except ValueError:
                continue
            if p.is_file():
                out.append(rel)
        return {"ok": True, "files": out, "count": len(out)}

    def search_code(self, query: str, limit: int = 20) -> dict[str, Any]:
        q = (query or "").strip().lower()
        if not q:
            return {"ok": False, "error": "empty_query"}
        hits: list[dict[str, str]] = []
        for p in self.root.rglob("*"):
            if len(hits) >= min(limit, 40):
                break
            if not p.is_file() or p.stat().st_size > MAX_FILE_BYTES:
                continue
            if p.suffix not in (".py", ".js", ".ts", ".tsx", ".md", ".json", ".html", ".css", ".yaml", ".yml"):
                continue
            if "node_modules" in p.parts:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if q in text.lower():
                rel = p.relative_to(self.root).as_posix()
                line_no = next((i + 1 for i, ln in enumerate(text.splitlines()) if q in ln.lower()), 0)
                hits.append({"path": rel, "line": str(line_no)})
        return {"ok": True, "hits": hits, "count": len(hits)}

    def run_shell(self, cmd: str) -> dict[str, Any]:
        c = (cmd or "").strip()
        if not c or not SHELL_ALLOW.match(c):
            return {"ok": False, "error": "shell_not_allowed", "cmd": c}
        if FORBIDDEN_PATH.search(c):
            return {"ok": False, "error": "shell_forbidden"}
        try:
            proc = subprocess.run(
                c,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=MAX_SHELL_SEC,
            )
            return {
                "ok": proc.returncode == 0,
                "cmd": c,
                "exit_code": proc.returncode,
                "stdout": (proc.stdout or "")[-8000:],
                "stderr": (proc.stderr or "")[-4000:],
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout", "cmd": c}
        except OSError as exc:
            return {"ok": False, "error": str(exc), "cmd": c}

    def execute(
        self,
        action: dict[str, Any],
        *,
        dry_run: bool = False,
        patch_only: bool = False,
        agent_id: str = "builder-001",
        agent_role: str = "builder",
        task_id: str = "",
        governance_level: str = "",
    ) -> dict[str, Any]:
        tool = str(action.get("tool") or "").strip()
        args = action.get("args") or {}
        try:
            from forge_governance_kernel_v1 import govern  # noqa: WPS433

            decision = govern(
                agent_id=agent_id,
                agent_role=agent_role,
                action_type=tool,
                payload=args if isinstance(args, dict) else {"raw": args},
                task_id=task_id,
                level=governance_level,
                dry_run=dry_run,
                charge_on_allow=not dry_run,
            )
            if decision.get("status") == "DENY":
                return {"ok": False, "error": "governance_denied", "governance": decision, "tool": tool}
        except Exception:
            pass
        if patch_only and tool == "write_file":
            return {
                "ok": False,
                "error": "write_file_blocked_l2_patch_only",
                "hint": "Use patch_file for self-improve repairs",
            }
        if tool == "read_file":
            return self.read_file(str(args.get("path") or ""))
        if tool == "write_file":
            return self.write_file(
                str(args.get("path") or ""), str(args.get("content") or ""), dry_run=dry_run
            )
        if tool == "patch_file":
            return self.patch_file(
                str(args.get("path") or ""),
                str(args.get("search") or ""),
                str(args.get("replace") or ""),
                dry_run=dry_run,
            )
        if tool == "list_files":
            return self.list_files(str(args.get("prefix") or ""), int(args.get("limit") or 40))
        if tool == "search_code":
            return self.search_code(str(args.get("query") or ""), int(args.get("limit") or 20))
        if tool == "run_shell":
            return self.run_shell(str(args.get("cmd") or ""))
        return {"ok": False, "error": "unknown_tool", "tool": tool}


def _parse_agent_json(raw: str) -> dict[str, Any] | None:
    s = (raw or "").strip()
    if not s:
        return None
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    try:
        row = json.loads(s)
        return row if isinstance(row, dict) else None
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", s)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None


def _llm_json(*, system: str, user: str, model: str, source: str) -> dict[str, Any]:
    from ai_unify_api_v1 import dispatch_raw  # noqa: WPS433

    row = dispatch_raw(
        system=system,
        user=user[:14000],
        model=model or None,
        source=source,
        light_gate=True,
        explicit_model=bool(model),
    )
    if not row.get("ok"):
        return {"ok": False, "error": row.get("message") or row.get("error"), "raw": row}
    parsed = _parse_agent_json(str(row.get("response") or ""))
    if not parsed:
        return {"ok": False, "error": "json_parse_failed", "response": row.get("response")}
    return {"ok": True, "parsed": parsed, "model": row.get("model"), "provider": row.get("provider")}


def build_repair_goal(
    *,
    quality_gate: dict[str, Any],
    founder_text: str = "",
    response: str = "",
    run_id: str = "",
) -> str:
    failed = [ly for ly in (quality_gate.get("layers") or []) if not ly.get("ok")]
    notes = "; ".join(
        f"{ly.get('id') or '?'}: {ly.get('note') or 'fail'}" for ly in failed[:10]
    )
    return (
        f"Self-improve run {run_id} — quality {quality_gate.get('verdict')} "
        f"({quality_gate.get('passed_layers')}/{quality_gate.get('total_layers')}).\n"
        f"Mission: {(founder_text or '')[:600]}\n"
        f"Failed layers: {notes or 'see verdict'}\n"
        f"Prior output excerpt: {(response or '')[:900]}\n"
        "Fix root causes with patch_file; run tests; stop when quality would PASS."
    )


def run_verify_harness_static(*, workspace_path: str = "") -> dict[str, Any]:
    """Light static contract checks — no HTTP, Mac-safe ≤2s."""
    root = Path(__file__).resolve().parents[1]
    checks: list[tuple[str, bool]] = []
    terminal = root / "apps" / "forge-terminal-v1"
    if terminal.is_dir():
        html = (terminal / "index.html").read_text(encoding="utf-8")
        js = (terminal / "terminal.js").read_text(encoding="utf-8")
        checks.append(("mode_pills", 'id="forge-mode-pills"' in html))
        checks.append(("advisor_timeline", "renderAdvisorTimeline" in js))
        checks.append(("advisor_run", "advisor_run" in js))
    else:
        checks.append(("terminal_dir", False))
    passed = sum(1 for _, ok in checks if ok)
    return {
        "ok": passed == len(checks) and bool(checks),
        "schema": "forge-verify-harness-static-v1",
        "passed": passed,
        "total": len(checks),
        "checks": [{"name": n, "ok": ok} for n, ok in checks],
        "workspace_path": workspace_path,
    }


def run_agent_dev_loop(
    *,
    goal: str,
    workspace_path: str,
    model: str = "",
    verifier_model: str = "",
    max_steps: int = MAX_STEPS,
    dry_run: bool = False,
    patch_only: bool = False,
    planner_system: str = "",
    tools_class: type | None = None,
) -> dict[str, Any]:
    """Level 1 closed loop: plan → act → verify until done or max_steps."""
    from model_dispatch import pick_roi_model  # noqa: WPS433

    root = Path(workspace_path).expanduser().resolve()
    if not root.is_dir():
        return {"ok": False, "error": "invalid_workspace", "path": workspace_path}

    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "empty_goal"}

    run_id = f"agk-{uuid.uuid4().hex[:10]}"
    planner_model = model or pick_roi_model("build")
    check_model = verifier_model or pick_roi_model("check")
    tools = (tools_class or ForgeAgentTools)(root)
    system = planner_system or (SELF_IMPROVE_PLANNER if patch_only else PLANNER_SYSTEM)

    steps: list[dict[str, Any]] = []
    repo_hint = tools.list_files(prefix="", limit=25)
    state = f"Goal: {goal}\nWorkspace: {root}\nFiles sample: {json.dumps(repo_hint.get('files') or [])}"
    fail_streak = 0
    reason_escalated = False

    for step in range(1, max_steps + 1):
        step_planner = planner_model
        if fail_streak >= 2 and not reason_escalated:
            from model_dispatch import pick_roi_model as _pick  # noqa: WPS433

            step_planner = _pick("reason")
            reason_escalated = True
        plan_row = _llm_json(
            system=system,
            user=f"{state}\n\nStep {step}/{max_steps}. Previous steps: {json.dumps(steps[-3:])}",
            model=step_planner,
            source="forge-agent-kernel-self-improve" if patch_only else "forge-agent-kernel-planner",
        )
        if not plan_row.get("ok"):
            out = {
                "ok": False,
                "run_id": run_id,
                "error": "planner_failed",
                "step": step,
                "detail": plan_row,
                "steps": steps,
                "patch_only": patch_only,
            }
            _write_receipt(out)
            return out

        parsed = plan_row["parsed"]
        if parsed.get("done"):
            steps.append({"step": step, "done": True, "summary": parsed.get("summary")})
            break

        action = parsed.get("action") or {}
        result = tools.execute(action, dry_run=dry_run, patch_only=patch_only)

        verify_row: dict[str, Any] = {"pass": True, "note": "skipped"}
        if action.get("tool") in ("write_file", "patch_file", "run_shell"):
            v = _llm_json(
                system=VERIFIER_SYSTEM,
                user=f"Goal: {goal}\nAction: {json.dumps(action)}\nResult: {json.dumps(result)[:6000]}",
                model=check_model,
                source="forge-agent-kernel-verifier",
            )
            if v.get("ok"):
                verify_row = v["parsed"]

        step_rec = {
            "step": step,
            "summary": parsed.get("summary"),
            "action": action,
            "result": result,
            "verify": verify_row,
            "planner_model": step_planner,
            "verifier_model": check_model,
            "planner_role": "reason" if reason_escalated and step_planner != planner_model else "build",
            "verifier_role": "check",
        }
        steps.append(step_rec)
        state += f"\nStep {step} result: {json.dumps(result)[:2000]} verify: {json.dumps(verify_row)}"

        if not result.get("ok") and action.get("tool") not in ("search_code", "list_files", "read_file"):
            fail_streak += 1
            break
        if verify_row.get("pass") is False:
            fail_streak += 1
            break
        fail_streak = 0

    done = bool(steps and steps[-1].get("done"))
    out = {
        "ok": done or any(s.get("result", {}).get("ok") for s in steps if s.get("action")),
        "schema": "forge-agent-kernel-run-v1",
        "run_id": run_id,
        "goal": goal,
        "workspace_path": str(root),
        "planner_model": planner_model,
        "verifier_model": check_model,
        "done": done,
        "patch_only": patch_only,
        "steps": steps,
        "at": _now(),
    }
    _write_receipt(out)
    return out


def run_self_improve_loop(
    *,
    workspace_path: str,
    quality_gate: dict[str, Any],
    founder_text: str = "",
    response: str = "",
    run_id: str = "",
    model: str = "",
    verifier_model: str = "",
    max_repair_rounds: int = MAX_REPAIR_ROUNDS,
    dry_run: bool = False,
    cloud_l3: bool = False,
) -> dict[str, Any]:
    """Level 2: quality fail → patch-only agent loop → re-gate until PASS or rounds exhausted."""
    qg = quality_gate or {}
    if qg.get("verdict") == "PASS" and qg.get("execution_allowed"):
        return {
            "ok": True,
            "schema": "forge-agent-self-improve-v1",
            "skipped": True,
            "reason": "already_pass",
            "quality_gate": qg,
        }

    repair_rounds: list[dict[str, Any]] = []
    current_qg = dict(qg)
    final_run_id = run_id
    last_decision_card: dict[str, Any] | None = None

    for rnd in range(1, max_repair_rounds + 1):
        if current_qg.get("verdict") == "PASS" and current_qg.get("execution_allowed"):
            break

        before_verdict = current_qg.get("verdict")
        goal = build_repair_goal(
            quality_gate=current_qg,
            founder_text=founder_text,
            response=response,
            run_id=run_id,
        )
        if dry_run:
            agent_out = {
                "ok": True,
                "run_id": f"agk-dry-{uuid.uuid4().hex[:8]}",
                "done": False,
                "steps": [
                    {
                        "step": 1,
                        "summary": "dry_run stub (no LLM)",
                        "action": {"tool": "read_file", "args": {"path": "README.md"}},
                        "result": {"ok": True, "dry_run": True},
                    }
                ],
            }
        else:
            agent_out = run_agent_dev_loop(
                goal=goal,
                workspace_path=workspace_path,
                model=model,
                verifier_model=verifier_model,
                max_steps=6,
                dry_run=False,
                patch_only=True,
            )
        gate_after = dict(current_qg)
        harness: dict[str, Any] = {"ok": True, "skipped": dry_run}
        if not dry_run:
            harness = run_verify_harness_static(workspace_path=workspace_path)
        if run_id and not dry_run and harness.get("ok"):
            from forge_terminal_v1 import quality_rerun  # noqa: WPS433

            qr = quality_rerun(
                run_id=run_id,
                founder_text=founder_text,
                workspace_path=workspace_path,
                full_llm=False,
            )
            if qr.get("quality_gate"):
                gate_after = qr["quality_gate"]
                current_qg = gate_after
            if qr.get("decision_card"):
                last_decision_card = qr["decision_card"]
                final_run_id = run_id
        elif run_id and not dry_run and not harness.get("ok"):
            gate_after = {**dict(current_qg), "harness_blocked": True}

        repair_rounds.append(
            {
                "round": rnd,
                "agent_run_id": agent_out.get("run_id"),
                "agent_ok": agent_out.get("ok"),
                "agent_done": agent_out.get("done"),
                "agent_steps": len(agent_out.get("steps") or []),
                "quality_before": before_verdict,
                "quality_after": gate_after,
                "verify_harness": harness,
            }
        )
        if gate_after.get("verdict") == "PASS" and gate_after.get("execution_allowed"):
            break

    improved = bool(
        current_qg.get("verdict") == "PASS"
        and current_qg.get("execution_allowed")
    )
    l3_result: dict[str, Any] | None = None
    if cloud_l3 and not improved and run_id:
        from forge_agent_self_improve_l3_v1 import run_self_improve_cloud  # noqa: WPS433
        from forge_l3_auto_runtime_v1 import enqueue_forge_l3_repair  # noqa: WPS433

        l3_result = run_self_improve_cloud(
            run_id=run_id,
            workspace_path=workspace_path,
            quality_gate=current_qg,
            founder_text=founder_text,
            l2_result={"improved": improved, "repair_rounds": repair_rounds},
            dry_run=dry_run,
        )
        enqueue_forge_l3_repair(run_id=run_id, quality_gate=current_qg, l3_result=l3_result)

    out = {
        "ok": improved or bool(repair_rounds),
        "schema": "forge-agent-self-improve-v1",
        "level": "L2",
        "run_id": final_run_id,
        "improved": improved,
        "repair_rounds": repair_rounds,
        "final_quality_gate": current_qg,
        "decision_card": last_decision_card,
        "initial_verdict": qg.get("verdict"),
        "final_verdict": current_qg.get("verdict"),
        "workspace_path": workspace_path,
        "l3": l3_result,
        "at": _now(),
    }
    SELF_IMPROVE_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    SELF_IMPROVE_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def run_self_improve_from_run(
    *,
    run_id: str,
    workspace_path: str,
    model: str = "",
    dry_run: bool = False,
    cloud_l3: bool = False,
) -> dict[str, Any]:
    """Load forge run doc and start L2 self-improve from its quality gate."""
    from forge_terminal_v1 import _read_json, _run_path  # noqa: WPS433

    doc = _read_json(_run_path(run_id))
    if not doc.get("run_id"):
        return {"ok": False, "error": "run_not_found", "run_id": run_id}
    qg = doc.get("quality_gate") or {}
    return run_self_improve_loop(
        workspace_path=workspace_path,
        quality_gate=qg,
        founder_text=str(doc.get("founder_input") or ""),
        response=str(doc.get("display_response") or doc.get("response") or ""),
        run_id=run_id,
        model=model,
        dry_run=dry_run,
        cloud_l3=cloud_l3,
    )
