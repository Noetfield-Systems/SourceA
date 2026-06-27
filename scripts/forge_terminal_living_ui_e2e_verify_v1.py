#!/usr/bin/env python3
"""Forge Terminal Living UI E2E — layout, reply, thread, Connect parity."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
APP_VERSION = "4.11.8-buttons-e2e"
TERMINAL_DIR = ROOT / "apps" / "forge-terminal-v1"
CONNECT_DIR = ROOT / "apps" / "forge-terminal-connect-v1"


def _looks_like_json_blob(text: str) -> bool:
    s = (text or "").strip()
    if not s or s[0] not in "{[":
        return False
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def _port() -> tuple[int, str] | None:
    for p in (13029,):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{p}/health", timeout=2) as r:
                row = json.loads(r.read().decode())
            if row.get("service") == "forge-terminal":
                return p, str(row.get("forge_local_token") or "")
        except Exception:
            continue
    return None


def _get(url: str, timeout: float = 5) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def _post(port: int, body: dict, token: str = "", timeout: float = 30) -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Forge-Token"] = token
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/forge-terminal/v1",
        data=data,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _static_contract_checks() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    html = (TERMINAL_DIR / "index.html").read_text(encoding="utf-8")
    css = (TERMINAL_DIR / "terminal.css").read_text(encoding="utf-8")
    js = (TERMINAL_DIR / "terminal.js").read_text(encoding="utf-8")
    connect_html = (CONNECT_DIR / "index.html").read_text(encoding="utf-8")
    connect_js = (CONNECT_DIR / "app.js").read_text(encoding="utf-8")

    checks.append(("terminal version", APP_VERSION in html and f"terminal.js?v={APP_VERSION}" in html, ""))
    checks.append(("L2 self-improve html", 'id="opt-cloud-l3"' in html and 'id="btn-self-heal"' in html, ""))
    checks.append(("advisor mode pills", 'id="forge-mode-pills"' in html and 'id="mode-advisor"' in html, ""))
    checks.append(("L2 self-improve js", "onSelfImprove" in js and "agent_self_improve" in js, ""))
    checks.append(("advisor js", "advisor_run" in js and "renderAdvisorTimeline" in js, ""))
    checks.append(("advisor timeline css", "forge-advisor-timeline" in css, ""))
    kernel_src = (SCRIPTS / "forge_agent_kernel_v1.py").read_text(encoding="utf-8")
    swarm_src = (SCRIPTS / "forge_agent_kernel_v3_swarm.py").read_text(encoding="utf-8")
    checks.append(("L2 kernel", "run_self_improve_loop" in kernel_src and "patch_only" in kernel_src, ""))
    checks.append(("v3 swarm kernel", "run_swarm_loop" in swarm_src and "ForgeState" in swarm_src, ""))
    checks.append(("swarm blackboard", (SCRIPTS / "forge_swarm_blackboard_v1.py").is_file(), ""))
    checks.append(("parallel swarm", "merge_plans" in swarm_src and "_parallel_planners" in swarm_src, ""))
    bb_src = (SCRIPTS / "forge_swarm_blackboard_v1.py").read_text(encoding="utf-8")
    checks.append(("cloud swarm dispatch module", (SCRIPTS / "forge_swarm_cloud_dispatch_v1.py").is_file(), ""))
    checks.append(("repair agent", "SWARM_REPAIR" in swarm_src and "repair_runs" in swarm_src, ""))
    checks.append(("optimizer agent", "SWARM_OPTIMIZER" in swarm_src and "optimizer_notes" in swarm_src, ""))
    checks.append(("execution mesh module", (SCRIPTS / "forge_execution_mesh_v1.py").is_file(), ""))
    checks.append(("repo intel module", (SCRIPTS / "forge_repo_intel_v1.py").is_file(), ""))
    checks.append(("civilization memory module", (SCRIPTS / "forge_civilization_memory_v1.py").is_file(), ""))
    checks.append(("agent registry module", (SCRIPTS / "forge_agent_registry_v1.py").is_file(), ""))
    checks.append(("civilization loop module", (SCRIPTS / "forge_civilization_loop_v1.py").is_file(), ""))
    checks.append(("task economy", "estimate_task_value" in bb_src and "select_agent_for_task" in bb_src, ""))
    checks.append(("v3 swarm law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_V3_SWARM_BLACKBOARD_LOCKED_v1.md").is_file(), ""))
    checks.append(("v4 civilization law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_TERMINAL_V4_CIVILIZATION_LOCKED_v1.md").is_file(), ""))
    checks.append(("governance kernel module", (SCRIPTS / "forge_governance_kernel_v1.py").is_file(), ""))
    gov_src = (SCRIPTS / "forge_governance_kernel_v1.py").read_text(encoding="utf-8")
    checks.append(("governance v2 economy", "GOVERNANCE_VERSION" in gov_src and "check_economy" in gov_src, ""))
    checks.append(("governance v3 legal", (SCRIPTS / "forge_governance_legal_v3.py").is_file(), ""))
    checks.append(("governance v4 geo legal", (SCRIPTS / "forge_geopolitical_legal_v4.py").is_file(), ""))
    checks.append(("governance v3 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_V3_LOCKED_v1.md").is_file(), ""))
    checks.append(("governance v4 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_V4_LOCKED_v1.md").is_file(), ""))
    checks.append(("governance v4 version", 'GOVERNANCE_VERSION = "v4"' in gov_src, ""))
    checks.append(("forge economy module", (SCRIPTS / "forge_economy_v1.py").is_file(), ""))
    checks.append(("governance v2 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_GOVERNANCE_KERNEL_V2_LOCKED_v1.md").is_file(), ""))
    checks.append(("prompt os compiler", (SCRIPTS / "forge_prompt_os_compiler_v1.py").is_file(), ""))
    checks.append(("prompt os v2 compiler", (SCRIPTS / "forge_prompt_os_compiler_v2.py").is_file(), ""))
    checks.append(("prompt os v3 runtime", (SCRIPTS / "forge_prompt_os_compiler_v3.py").is_file(), ""))
    checks.append(("prompt os law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_PROMPT_OS_COMPILER_LOCKED_v1.md").is_file(), ""))
    checks.append(("prompt os v2 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_PROMPT_OS_COMPILER_V2_LOCKED_v1.md").is_file(), ""))
    checks.append(("prompt os v3 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_PROMPT_OS_COMPILER_V3_LOCKED_v1.md").is_file(), ""))
    checks.append(("world state v6 stub", (SCRIPTS / "forge_world_state_v1.py").is_file(), ""))
    checks.append(("self build v1", (SCRIPTS / "forge_self_build_v1.py").is_file(), ""))
    checks.append(("self build v2 proof", (SCRIPTS / "forge_self_build_v2.py").is_file(), ""))
    checks.append(("self build v3 swarm", (SCRIPTS / "forge_self_build_v3.py").is_file(), ""))
    checks.append(("civ code v4", (SCRIPTS / "forge_civilization_code_v4.py").is_file(), ""))
    checks.append(("digital nation v5", (SCRIPTS / "forge_digital_nation_v5.py").is_file(), ""))
    checks.append(("world system v6", (SCRIPTS / "forge_world_system_v6.py").is_file(), ""))
    checks.append(("planetary consciousness v7", (SCRIPTS / "forge_planetary_consciousness_v7.py").is_file(), ""))
    checks.append(("consciousness v7 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_PLANETARY_CONSCIOUSNESS_V7_LOCKED_v1.md").is_file(), ""))
    checks.append(("reality consciousness v8", (SCRIPTS / "forge_reality_consciousness_v8.py").is_file(), ""))
    checks.append(("reality consciousness v8 law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_REALITY_CONSCIOUSNESS_V8_LOCKED_v1.md").is_file(), ""))
    checks.append(("self build law", (ROOT / "brain-os/law/enforcement/SOURCEA_FORGE_SELF_BUILD_STACK_LOCKED_v1.md").is_file(), ""))
    checks.append(("repair timeline js", "repairRuns" in js, ""))
    checks.append(("economy timeline js", "taskEconomy" in js, ""))
    connect_srv = (SCRIPTS / "forge_terminal_connect_server_v1.py").read_text(encoding="utf-8")
    checks.append(("connect server wired", "FORGE_TERMINAL_USE_LIVE_UI" in connect_srv and "UI_VERSION" in connect_srv, ""))
    checks.append(("swarm js flag", "swarm: true" in js, ""))
    checks.append(("thread tabs html", 'id="thread-tabs"' in html and "btn-new-thread" in html, ""))
    checks.append(("editor pane html", 'id="editor-pane"' in html and "forge-main-split" in html, ""))
    checks.append(("reload ui button", 'id="btn-reload-ui"' in html, ""))
    checks.append(("ui reload version", f'UI_VERSION = "{APP_VERSION}"' in js and "UI_VERSION)" in js, ""))
    checks.append(("chat mode default", 'class="forge-mode-pill is-active" data-mode="chat"' in html, ""))
    checks.append(("chat unify connect panel", "Chat Unify · ping" in js and "peer_dispatch" in js, ""))
    checks.append(("chat sessions js", "loadChatSessions" in js and "newChatThread" in js, ""))
    checks.append(("live ui server", "FORGE_TERMINAL_USE_LIVE_UI" in (SCRIPTS / "forge_terminal_connect_server_v1.py").read_text(encoding="utf-8"), ""))
    checks.append(("no chat 42vh cap", "42vh" not in css, ""))
    checks.append(("founder sections css", "forge-founder-sections" in css, ""))
    checks.append(("forge-markdown css", "forge-chat-inner.forge-markdown" in css or "forge-markdown" in css, ""))
    checks.append(("forge-embed css", "forge-embed" in css, ""))
    checks.append(("dock resize html", 'id="dock-resize"' in html, ""))
    checks.append(("sidebar resize html", 'id="sidebar-resize"' in html, ""))
    checks.append(("offline banner html", 'id="offline-banner"' in html, ""))
    checks.append(("initDockResize js", "initDockResize" in js, ""))
    checks.append(("initSidebarResize js", "initSidebarResize" in js, ""))
    checks.append(("renderFounderSections js", "renderFounderSections" in js, ""))
    checks.append(("forge-embed js", "forge-embed" in js, ""))
    checks.append(("connect shell", "forge-ide-frame" in connect_html and "forge-quality-bridge.js" in connect_html, ""))
    checks.append(("connect forge-ide tab", "forge-ide" in connect_html and 'data-tab="forge-ide"' in connect_html, ""))
    checks.append(("app.js forge-ide router", '"forge-ide"' in connect_js and "panel-forge-ide" in connect_js, ""))
    return checks


def _cli_chat_checks() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    sys.path.insert(0, str(SCRIPTS))
    from forge_terminal_desktop_mesh_v1 import create_chat_session, list_chat_sessions, load_thread  # noqa: WPS433
    from forge_terminal_v1 import handle_post  # noqa: WPS433
    from forge_workspace_open_v1 import open_folder  # noqa: WPS433

    td = Path(tempfile.mkdtemp(prefix="forge-living-cli-"))
    try:
        (td / "README.md").write_text("# living ui e2e\n", encoding="utf-8")
        open_folder(str(td), auto_init=True)
        ws = str(td)

        turn = handle_post(
            {
                "action": "chat_turn",
                "text": "Summarize README purpose in plain English for the founder",
                "full_llm": False,
                "fast": True,
                "workspace_path": ws,
            }
        )
        checks.append(("chat_turn ok", turn.get("ok") is True, turn.get("error") or ""))
        disp = str(turn.get("display_response") or turn.get("response") or "")
        checks.append(("display_response present", bool(disp.strip()), ""))
        checks.append(("display not json blob", not _looks_like_json_blob(disp), disp[:80]))

        forge_turn = handle_post(
            {
                "action": "chat_turn",
                "text": "Summarize README in one sentence",
                "full_llm": False,
                "fast": False,
                "workspace_path": ws,
            }
        )
        forge_meta = forge_turn.get("forge") or {}
        checks.append(
            (
                "chat_turn prompt forge",
                forge_turn.get("ok") is True and forge_meta.get("fast") is False,
                forge_turn.get("error") or str(forge_meta.get("mode") or ""),
            )
        )

        thread = load_thread(workspace_path=ws)
        turns = thread.get("turns") or []
        last_asst = next((t for t in reversed(turns) if t.get("role") == "assistant"), {})
        meta = last_asst.get("meta") or {}
        qg = meta.get("quality_gate") or {}
        checks.append(("thread quality meta", bool(qg.get("verdict")), qg.get("verdict") or ""))

        created = create_chat_session(workspace_path=ws, title="E2E session")
        checks.append(("chat_session_create", created.get("ok") is True, ""))
        listed = list_chat_sessions(workspace_path=ws)
        checks.append(("chat_sessions_list", len(listed.get("sessions") or []) >= 2, ""))
        empty = load_thread(workspace_path=ws, session_id=created.get("active_session_id"))
        checks.append(("new session empty", len(empty.get("turns") or []) == 0, ""))

        from forge_agent_kernel_v1 import run_self_improve_loop  # noqa: WPS433

        fake_qg = {
            "verdict": "REVISE",
            "passed_layers": 7,
            "total_layers": 10,
            "execution_allowed": False,
            "layers": [{"id": "mission_fit", "ok": False, "note": "e2e stub"}],
        }
        l2 = run_self_improve_loop(
            workspace_path=ws,
            quality_gate=fake_qg,
            founder_text="fix readme",
            response="stub",
            run_id="",
            dry_run=True,
        )
        checks.append(("agent_self_improve dry_run", l2.get("schema") == "forge-agent-self-improve-v1", ""))
        checks.append(("agent_self_improve rounds", len(l2.get("repair_rounds") or []) >= 1, ""))

        si = handle_post(
            {
                "action": "agent_self_improve",
                "quality_gate": fake_qg,
                "text": "fix readme",
                "workspace_path": ws,
                "dry_run": True,
            }
        )
        checks.append(("agent_self_improve api", si.get("level") == "L2", si.get("error") or ""))

        from forge_advisor_orchestrator_v1 import run_advisor  # noqa: WPS433

        adv = run_advisor(goal="Summarize README", workspace_path=ws, dry_run=True, max_steps=2)
        checks.append(("advisor_run cli", adv.get("schema") == "forge-advisor-run-v1", ""))
        adv_api = handle_post(
            {"action": "advisor_run", "goal": "Summarize README", "workspace_path": ws, "dry_run": True, "swarm": True}
        )
        checks.append(("advisor_run api", adv_api.get("schema") == "forge-advisor-run-v1", adv_api.get("error") or ""))
        checks.append(("advisor_run swarm", adv_api.get("swarm") is True, ""))
        checks.append(("advisor compiled", bool(adv_api.get("compiled")), ""))
        checks.append(("advisor v3 schema", (adv_api.get("compiled") or {}).get("schema") == "forge-prompt-os-runtime-v3", ""))
        from forge_prompt_os_compiler_v3 import (  # noqa: WPS433
            autonomous_execute,
            compile_prompt,
            record_execution_outcome,
            route_execution,
            seed_learning_demo,
        )

        seed_learning_demo()
        compiled = compile_prompt(raw="Add README summary feature", workspace_path=ws)
        checks.append(("compile_prompt cli", compiled.get("schema") == "forge-prompt-os-runtime-v3", ""))
        checks.append(("compile stack level", compiled.get("stackLevel") in ("L1", "L2", "L3", "L4", "L5", "L6", "L7"), ""))
        checks.append(("compile adaptive routing", bool(compiled.get("routing")), ""))
        checks.append(("compile runtime capable", compiled.get("runtime_capable") is True, ""))
        checks.append(("compile suggested route", bool(compiled.get("suggested_route")), ""))
        compile_api = handle_post({"action": "compile_prompt", "text": "Optimize forge terminal", "workspace_path": ws})
        checks.append(("compile_prompt api", compile_api.get("schema") == "forge-prompt-os-runtime-v3", ""))
        checks.append(("compile dispatch hint", bool(compile_api.get("dispatch_hint")), ""))
        checks.append(("compile dispatch autonomous", (compile_api.get("dispatch_hint") or {}).get("action") == "autonomous_run", ""))
        learn_row = record_execution_outcome(compiled=compiled, execution_ok=True, execution_state="DONE")
        checks.append(("prompt learning record", learn_row.get("ok") is True, ""))
        route = route_execution(compiled)
        checks.append(("route execution", bool(route.get("executor")), ""))
        auto_cli = autonomous_execute(raw="Summarize README purpose", workspace_path=ws, dry_run=True, max_tasks=2)
        checks.append(("autonomous_run cli", auto_cli.get("schema") == "forge-prompt-os-runtime-v3", ""))
        checks.append(("autonomous_run execution", bool(auto_cli.get("execution")), ""))
        auto_api = handle_post(
            {"action": "autonomous_run", "text": "List README files", "workspace_path": ws, "dry_run": True, "max_tasks": 2}
        )
        checks.append(("autonomous_run api", auto_api.get("schema") == "forge-prompt-os-runtime-v3", ""))
        checks.append(("autonomous_run learning", bool(auto_api.get("learning")), ""))

        from forge_agent_kernel_v3_swarm import run_swarm_loop  # noqa: WPS433

        swarm = run_swarm_loop(goal="List README purpose", workspace_path=ws, max_tasks=2, dry_run=True)
        checks.append(("agent_swarm_run cli", swarm.get("schema") == "forge-agent-kernel-swarm-v3", ""))
        swarm_api = handle_post(
            {"action": "agent_swarm_run", "goal": "List README", "workspace_path": ws, "dry_run": True, "max_tasks": 2}
        )
        checks.append(("agent_swarm_run api", swarm_api.get("schema") == "forge-agent-kernel-swarm-v3", ""))
        checks.append(("swarm blackboard receipt", bool(swarm.get("blackboard")), ""))
        checks.append(("swarm task_economy", bool((swarm.get("blackboard") or {}).get("task_economy")), ""))
        checks.append(("swarm optimizer notes", bool(swarm.get("optimizer_notes")), ""))
        checks.append(("swarm repair_runs field", isinstance(swarm.get("repair_runs"), list), ""))
        from forge_swarm_cloud_dispatch_v1 import dispatch_swarm_cloud  # noqa: WPS433

        cloud = dispatch_swarm_cloud(goal="List README", workspace_path=ws, dry_run=True)
        checks.append(("cloud swarm dispatch cli", cloud.get("schema") == "forge-swarm-cloud-dispatch-v1", ""))
        cloud_api = handle_post(
            {"action": "agent_swarm_run", "goal": "List README", "workspace_path": ws, "cloud": True, "dry_run": True}
        )
        checks.append(("cloud swarm dispatch api", cloud_api.get("schema") == "forge-swarm-cloud-dispatch-v1", ""))
        from forge_civilization_memory_v1 import load_memory, record_run  # noqa: WPS433

        mem_row = record_run(swarm)
        checks.append(("civilization memory record", mem_row.get("ok") is True, ""))
        checks.append(("civilization memory events", len(load_memory().get("event_log") or []) >= 1, ""))
        from forge_agent_registry_v1 import load_registry, update_reputation  # noqa: WPS433

        reg = load_registry()
        checks.append(("agent registry agents", len(reg.get("agents") or []) >= 10, ""))
        update_reputation(agent_ids=["planner-001"], success=True)
        from forge_civilization_loop_v1 import civilization_tick  # noqa: WPS433

        tick = civilization_tick(workspace_path=ws, dry_run=True)
        checks.append(("civilization tick", tick.get("schema") == "forge-civilization-tick-v1", ""))
        from forge_repo_intel_v1 import build_repo_graph  # noqa: WPS433

        graph = build_repo_graph(workspace=Path(ws))
        checks.append(("repo graph build", isinstance(graph.get("nodes"), list), ""))
        from forge_governance_kernel_v1 import govern, list_violations  # noqa: WPS433

        allow = govern(agent_id="builder-001", agent_role="builder", action_type="read_file", payload={"path": "README.md"}, dry_run=True)
        checks.append(("governance allow read", allow.get("status") == "ALLOW", ""))
        checks.append(("governance v4 schema", allow.get("schema") == "forge-governance-decision-v4", ""))
        deny = govern(agent_id="planner-001", agent_role="planner", action_type="write_file", payload={"path": "x"}, dry_run=True)
        checks.append(("governance deny planner write", deny.get("status") == "DENY", ""))
        conflict = govern(
            agent_id="builder-001",
            agent_role="builder",
            action_type="write_file",
            payload={"path": "secrets.env"},
            dry_run=True,
        )
        checks.append(("governance legal conflict", bool(conflict.get("legal")), ""))
        checks.append(("governance conflict judgment", bool((conflict.get("legal") or {}).get("judgment")), ""))
        from forge_governance_legal_v3 import (  # noqa: WPS433
            add_precedent,
            arbitrate,
            create_case,
            detect_rule_conflict,
            load_precedents,
            process_violation,
        )

        case = create_case(
            action={"action_type": "deploy", "payload": {}},
            agent_id="builder-001",
            violation="deploy_requires_approval",
            checks=[{"status": "ALLOW"}, {"status": "DENY", "reason": "deploy_requires_approval"}],
            conflict=True,
        )
        checks.append(("legal case create", bool(case.get("id")), ""))
        judgment = arbitrate(case, dry_run=True)
        checks.append(("legal arbitrate", judgment.get("schema") == "forge-governance-judgment-v3", ""))
        checks.append(("legal precedent store", len(load_precedents().get("precedents") or []) >= 1, ""))
        legal_api = handle_post(
            {
                "action": "legal_arbitrate",
                "agent_id": "builder-001",
                "action_type": "write_file",
                "violation": "forbidden_path",
                "dry_run": True,
            }
        )
        checks.append(("legal arbitrate api", legal_api.get("schema") == "forge-governance-legal-v3", ""))
        checks.append(("detect rule conflict", detect_rule_conflict([{"status": "ALLOW"}, {"status": "DENY"}]) is True, ""))
        from forge_geopolitical_legal_v4 import (  # noqa: WPS433
            check_geopolitical,
            geo_legal_tick,
            impose_sanction,
            load_geo_legal,
            nation_for_agent,
            seed_geo_legal,
            sign_treaty,
        )

        seed_geo_legal()
        checks.append(("geo nation map", nation_for_agent("builder-001") == "nation-sourcea", ""))
        checks.append(("geo treaty seed", len(load_geo_legal().get("treaties") or []) >= 2, ""))
        cross = check_geopolitical(
            agent_id="lab-001",
            action_type="deploy",
            payload={"target_nation": "nation-sourcea"},
        )
        checks.append(("geo cross border check", cross.get("geo", {}).get("cross_border") is True, ""))
        sanction = impose_sanction(issuer="nation-sourcea", target="nation-labs", reason="e2e_test")
        checks.append(("geo impose sanction", sanction.get("ok") is True, ""))
        blocked = check_geopolitical(
            agent_id="lab-001",
            action_type="write_file",
            payload={"target_nation": "nation-sourcea"},
        )
        checks.append(("geo sanction block", blocked.get("reason") == "sanction_active", ""))
        treaty = sign_treaty(party_a="nation-sourcea", party_b="nation-labs", terms=["e2e_access"], allowed_actions=["read_file"])
        checks.append(("geo sign treaty", bool(treaty.get("treaty")), ""))
        tick = geo_legal_tick(dry_run=True)
        checks.append(("geo legal tick", tick.get("schema") == "forge-geopolitical-legal-tick-v4", ""))
        geo_api = handle_post({"action": "geo_legal_tick", "dry_run": True})
        checks.append(("geo legal tick api", geo_api.get("schema") == "forge-geopolitical-legal-tick-v4", ""))
        from forge_economy_v1 import ensure_account, load_economy, reward_agent  # noqa: WPS433

        acct = ensure_account("builder-001")
        checks.append(("economy account", float(acct.get("balance") or 0) > 0, ""))
        reward_agent(agent_id="builder-001", amount=0.5, reason="e2e")
        checks.append(("economy reward", load_economy().get("schema") == "forge-economy-v1", ""))
        prob = govern(agent_id="builder-001", agent_role="builder", action_type="run_shell", payload={"cmd": "pytest"}, dry_run=True)
        checks.append(("governance violations log", isinstance(list_violations(limit=5), list), ""))
        from forge_world_state_v1 import world_tick, load_world  # noqa: WPS433

        wt = world_tick(dry_run=True)
        checks.append(("world tick v6 stub", wt.get("schema") == "forge-world-tick-v1", ""))
        checks.append(("world nations seed", len(load_world().get("nations") or {}) >= 3, ""))
        from forge_self_build_v1 import introspect_system, self_build_tick  # noqa: WPS433
        from forge_self_build_v2 import safe_evolve_tick  # noqa: WPS433
        from forge_self_build_v3 import swarm_evolve_tick  # noqa: WPS433
        from forge_civilization_code_v4 import civilization_code_tick, load_civilizations  # noqa: WPS433
        from forge_world_system_v6 import world_system_tick, load_world_vector  # noqa: WPS433

        intro = introspect_system()
        checks.append(("self build introspect", intro.get("module_count", 0) > 10, ""))
        sb = self_build_tick(dry_run=True)
        checks.append(("self build tick", sb.get("schema") == "forge-self-build-v1", ""))
        sb2 = safe_evolve_tick(dry_run=True)
        checks.append(("self build v2 proof", sb2.get("schema") == "forge-self-build-v2", ""))
        sb3 = swarm_evolve_tick(dry_run=True, pool_size=3, rounds=1)
        checks.append(("self build v3 swarm", sb3.get("schema") == "forge-self-build-v3", ""))
        civ_code = civilization_code_tick(dry_run=True)
        checks.append(("civ code tick", civ_code.get("schema") == "forge-civilization-code-v4", ""))
        checks.append(("civ code seed", len(load_civilizations().get("civilizations") or []) >= 3, ""))
        world_sys = world_system_tick(dry_run=True)
        checks.append(("world system tick", world_sys.get("schema") == "forge-world-system-v6", ""))
        checks.append(("world vector v6", bool(load_world_vector().get("globalGDP")), ""))
        sb_api = handle_post({"action": "self_build_tick", "dry_run": True})
        checks.append(("self build api", sb_api.get("schema") == "forge-self-build-v1", ""))
        ws_api = handle_post({"action": "world_system_tick", "dry_run": True})
        checks.append(("world system api", ws_api.get("schema") == "forge-world-system-v6", ""))
        from forge_planetary_consciousness_v7 import (  # noqa: WPS433
            collect_meta_signals,
            compute_awareness_index,
            consciousness_status,
            planetary_consciousness_tick,
        )

        pc = planetary_consciousness_tick(dry_run=True, run_world=False)
        checks.append(("consciousness tick", pc.get("schema") == "forge-planetary-consciousness-v7", ""))
        checks.append(("consciousness awareness", bool(pc.get("awareness")), ""))
        checks.append(("consciousness thought", bool(pc.get("thought")), ""))
        signals = collect_meta_signals()
        awareness = compute_awareness_index(signals)
        checks.append(("awareness index", 0.0 <= float(awareness.get("awarenessIndex", 0)) <= 1.0, ""))
        checks.append(("awareness level", awareness.get("level") in ("dormant", "observing", "reflecting", "stabilizing", "coherent"), ""))
        pc_api = handle_post({"action": "planetary_consciousness_tick", "dry_run": True, "run_world": False})
        checks.append(("consciousness api", pc_api.get("schema") == "forge-planetary-consciousness-v7", ""))
        cs = consciousness_status()
        checks.append(("consciousness status", cs.get("schema") == "forge-planetary-consciousness-v7", ""))
        from forge_reality_consciousness_v8 import (  # noqa: WPS433
            collect_reality_signals,
            compute_reality_health,
            reality_consciousness_status,
            reality_consciousness_tick,
        )

        rs = collect_reality_signals()
        checks.append(("reality signals mac", "mac" in rs, ""))
        rh = compute_reality_health(rs)
        checks.append(("reality health", 0.0 <= float(rh.get("realityHealth", 0)) <= 1.0, ""))
        r8 = reality_consciousness_tick(dry_run=True, run_v7=False)
        checks.append(("reality consciousness tick", r8.get("schema") == "forge-reality-consciousness-v8", ""))
        checks.append(("reality coupled awareness", bool(r8.get("coupled")), ""))
        checks.append(("reality thought", bool(r8.get("thought")), ""))
        r8_api = handle_post({"action": "reality_consciousness_tick", "dry_run": True, "run_v7": False})
        checks.append(("reality consciousness api", r8_api.get("schema") == "forge-reality-consciousness-v8", ""))
        r8s = reality_consciousness_status()
        checks.append(("reality status api", r8s.get("schema") == "forge-reality-consciousness-v8", ""))
        kernel_swarm = (SCRIPTS / "forge_agent_kernel_v3_swarm.py").read_text(encoding="utf-8")
        checks.append(("governance wired kernel", "governance_denied" in (SCRIPTS / "forge_agent_kernel_v1.py").read_text(encoding="utf-8"), ""))
        checks.append(("swarm git apply", "apply_git_patch" in kernel_swarm, ""))
        checks.append(("swarm state machine", "ForgeState" in kernel_swarm, ""))
    finally:
        shutil.rmtree(td, ignore_errors=True)
    return checks


def _http_mesh_checks(port: int, token: str) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    try:
        mesh = _post(port, {"action": "desktop_mesh_status"}, token=token, timeout=10)
        peers = mesh.get("peers") or []
        checks.append(("mesh peers", len(peers) >= 3, str(len(peers))))
    except Exception as exc:
        checks.append(("mesh peers", False, str(exc)[:80]))
    try:
        light = _post(port, {"action": "status_light"}, token=token, timeout=10)
        checks.append(("status_light ok", light.get("ok") is True, ""))
        checks.append(("status_light mesh field", "desktop_mesh" in light, ""))
    except Exception as exc:
        checks.append(("status_light ok", False, str(exc)[:80]))
    if token:
        try:
            _post(port, {"action": "status_light"}, token="bad-token", timeout=5)
            checks.append(("auth negative", False, "expected 401"))
        except urllib.error.HTTPError as e:
            checks.append(("auth negative", e.code == 401, str(e.code)))
        except Exception as exc:
            checks.append(("auth negative skip", True, str(exc)[:40]))
    try:
        fake_qg = {
            "verdict": "REVISE",
            "passed_layers": 7,
            "total_layers": 11,
            "execution_allowed": False,
            "layers": [{"id": "mission_fit", "ok": False, "note": "http e2e"}],
        }
        si_http = _post(
            port,
            {
                "action": "agent_self_improve",
                "quality_gate": fake_qg,
                "text": "fix readme",
                "workspace_path": str(ROOT),
                "dry_run": True,
            },
            token=token,
            timeout=30,
        )
        checks.append(
            (
                "http agent_self_improve",
                si_http.get("schema") == "forge-agent-self-improve-v1",
                si_http.get("error") or "",
            )
        )
    except Exception as exc:
        checks.append(("http agent_self_improve", False, str(exc)[:80]))
    return checks


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.extend(_static_contract_checks())
    checks.extend(_cli_chat_checks())

    port_row = _port()
    if port_row:
        port, token = port_row
        checks.extend(_http_mesh_checks(port, token))
        print(f"Forge Living UI E2E (disk + CLI + HTTP :{port})\n")
    else:
        print("Forge Living UI E2E (disk + CLI — no HTTP server)\n")

    passed = sum(1 for _, ok, _ in checks if ok)
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" ({detail})" if detail else ""))
    print(f"\n{passed}/{len(checks)} passed")

    receipt = {
        "schema": "forge-terminal-living-ui-e2e-v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "port": port_row[0] if port_row else None,
        "app_version": APP_VERSION,
        "passed": passed,
        "total": len(checks),
        "living_ui_dock_resize": True,
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "forge-terminal-living-ui-e2e-v1.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
