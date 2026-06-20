#!/usr/bin/env python3
"""Agent rule live wire — registry orchestrator for nerves → surfaces → loops.

Law: data/agent-rule-live-wire-registry-v1.json
Receipt: ~/.sina/agent-rule-live-wire-receipt-v1.json

Every new rule: R1–R10 then --wire-sync upgrades DISK + MACHINES (H2) + nerves.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "agent-rule-live-wire-registry-v1.json"
RECEIPT = SINA / "agent-rule-live-wire-receipt-v1.json"
CHECKCART = SINA / "agent-law-wire-checkcart-v1.json"
H2_REGISTRY = SINA / "h2-pending-registry-v1.json"
DISK_WIRE_RECEIPT = SINA / "disk-live-wire-receipt-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
CURSOR_RULES_DIR = ROOT / ".cursor" / "rules"
CURSOR_RULES_INDEX = SINA / "cursor-rules-index-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _expand(path: str) -> Path:
    p = path.replace("~", str(Path.home()))
    return Path(p)


def load_registry() -> dict:
    return _read(SSOT)


def _import_script(script_rel: str):
    path = ROOT / script_rel
    if not path.is_file():
        raise FileNotFoundError(script_rel)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {script_rel}")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SCRIPTS))
    spec.loader.exec_module(mod)
    return mod


def pulse_rule(rule: dict, *, write: bool = True) -> dict:
    script = str(rule.get("script") or "")
    pulse_fn = str(rule.get("pulse_fn") or "assess")
    mod = _import_script(script)
    fn = getattr(mod, pulse_fn, None)
    if fn is None:
        return {"ok": False, "error": f"missing {pulse_fn} in {script}"}
    try:
        row = fn(write=write)
    except TypeError:
        row = fn()
    if not isinstance(row, dict):
        return {"ok": False, "error": f"{pulse_fn} returned non-dict"}
    row.setdefault("ok", True)
    return row


def _surfaces_patch(rule: dict, pulse_row: dict, surfaces: dict) -> None:
    line_key = str(rule.get("surfaces_line_key") or "")
    block_key = str(rule.get("surfaces_block_key") or "")
    if line_key:
        line = pulse_row.get(line_key) or pulse_row.get(f"{rule['id']}_line")
        if line:
            surfaces[line_key] = line
    if block_key:
        block: dict = {
            "id": rule.get("id"),
            "ok": bool(pulse_row.get("ok", True)),
            "receipt": str(_expand(str(rule.get("receipt") or ""))),
            "ssot": rule.get("ssot"),
            "at": pulse_row.get("at") or _now(),
        }
        for extra in (
            "defer_active",
            "cloud_factories_online",
            "workers_online",
            "sites_online",
            "founder_lift",
            "passed",
            "total",
            "sina_pending",
            "registry_count",
            "wef_gln_total",
            "one_law",
        ):
            if extra in pulse_row:
                block[extra] = pulse_row[extra]
        if rule.get("id") == "email_send_defer" and "defer_active" in pulse_row:
            block["ok"] = not bool(pulse_row.get("defer_active"))
        surfaces[block_key] = block


def pulse_registry_to_surfaces(surfaces: dict, *, write: bool = True) -> dict:
    registry = load_registry()
    rules_out: list[dict] = []
    live_n = 0
    pass_n = 0
    for rule in registry.get("rules") or []:
        if str(rule.get("status") or "") != "live":
            continue
        live_n += 1
        rid = str(rule.get("id") or "")
        try:
            row = pulse_rule(rule, write=write)
            wire = validate_rule(rule)
            ok = bool(wire.get("ok"))
            pulse_ok = bool(row.get("ok", True))
            _surfaces_patch(rule, row, surfaces)
            rules_out.append(
                {
                    "id": rid,
                    "ok": ok,
                    "pulse_ok": pulse_ok,
                    "label": rule.get("label"),
                }
            )
            if ok:
                pass_n += 1
        except Exception as exc:
            rules_out.append({"id": rid, "ok": False, "error": str(exc)[:120]})
    line = f"rule-wire · {pass_n}/{live_n} wired · registry={live_n}"
    surfaces["rule_live_wire_line"] = line
    surfaces["rule_live_wire"] = {
        "ok": pass_n == live_n and live_n > 0,
        "live_count": live_n,
        "pass_count": pass_n,
        "rules": rules_out,
        "receipt": str(RECEIPT),
        "ssot": str(SSOT.relative_to(ROOT)),
        "procedure": "python3 scripts/agent_rule_live_wire_v1.py --wire-sync",
    }
    return {"ok": pass_n == live_n, "line": line, "rules": rules_out}


def validate_rule(rule: dict) -> dict:
    rid = str(rule.get("id") or "")
    issues: list[str] = []
    ssot_path = ROOT / str(rule.get("ssot") or "")
    script_path = ROOT / str(rule.get("script") or "")
    receipt_path = _expand(str(rule.get("receipt") or ""))
    validator = str(rule.get("validator") or "")

    if not ssot_path.is_file():
        issues.append(f"missing ssot:{rule.get('ssot')}")
    if not script_path.is_file():
        issues.append(f"missing script:{rule.get('script')}")
    pulse_fn = str(rule.get("pulse_fn") or "assess")
    try:
        mod = _import_script(str(rule.get("script") or ""))
        if not callable(getattr(mod, pulse_fn, None)):
            issues.append(f"missing pulse_fn:{pulse_fn}")
    except Exception as exc:
        issues.append(f"script_load:{exc}")

    validate_fn = str(rule.get("validate_fn") or "")
    if validate_fn:
        try:
            mod = _import_script(str(rule.get("script") or ""))
            if not callable(getattr(mod, validate_fn, None)):
                issues.append(f"missing validate_fn:{validate_fn}")
        except Exception:
            pass

    if validator:
        vpath = ROOT / validator
        if not vpath.is_file():
            issues.append(f"missing validator:{validator}")

    line_key = str(rule.get("surfaces_line_key") or "")
    surfaces = _read(SURFACES)
    if line_key and not surfaces.get(line_key):
        try:
            row = pulse_rule(rule, write=True)
            pulse_registry_to_surfaces(surfaces, write=False)
            if not surfaces.get(line_key) and not row.get(line_key):
                issues.append(f"surfaces missing {line_key}")
        except Exception as exc:
            issues.append(f"pulse:{exc}")

    nerve_keys = rule.get("nerve_keys") or []
    if nerve_keys:
        nerve = _read(SINA / "agent-nerve-system-receipt-v1.json")
        ship = nerve.get("ship_gates") or {}
        missing = [k for k in nerve_keys if k not in ship and k not in nerve]
        if missing and rid == "founder_execution_model":
            if surfaces.get("founder_execution_model_line"):
                missing = [k for k in missing if k != "founder_execution_model"]
        if missing:
            try:
                _run([PY, str(SCRIPTS / "agent_nerve_system_v1.py"), "--json"], timeout=25)
                nerve = _read(SINA / "agent-nerve-system-receipt-v1.json")
                ship = nerve.get("ship_gates") or {}
                missing = [k for k in nerve_keys if k not in ship and k not in nerve]
            except Exception:
                pass
            issues.extend(f"nerve missing key:{k}" for k in missing)

    anti_chk = str(rule.get("anti_theater_check") or "")
    if anti_chk:
        at_ssot = _read(ROOT / "data" / "anti-theater-validator-loop-v1.json")
        order = (at_ssot.get("loop_chain") or {}).get("order") or []
        if anti_chk not in order:
            issues.append(f"anti_theater loop_chain missing:{anti_chk}")

    for target in rule.get("runs_on") or []:
        t = str(target)
        if t.startswith("POST "):
            continue
        if not (ROOT / t).is_file() and not t.endswith(".py"):
            issues.append(f"runs_on target missing:{t}")

    return {
        "id": rid,
        "label": rule.get("label"),
        "ok": not issues,
        "issues": issues,
        "status": rule.get("status"),
    }


def validate_all() -> dict:
    registry = load_registry()
    rows = [validate_rule(r) for r in registry.get("rules") or [] if r.get("status") == "live"]
    passed = sum(1 for r in rows if r.get("ok"))
    total = len(rows)
    return {
        "ok": passed == total and total > 0,
        "passed": passed,
        "total": total,
        "rules": rows,
        "procedure": registry.get("procedure"),
    }


def _run_json_step(cmd: list[str], *, timeout: float = 85.0) -> dict:
    code, out = _run(cmd, timeout=timeout)
    row: dict = {"ok": code == 0, "exit": code}
    if "{" in out:
        try:
            row["detail"] = json.loads(out[out.find("{") :])
        except json.JSONDecodeError:
            row["detail_preview"] = out[:200]
    return row


def sync_cursor_rules_index(*, write: bool = True) -> dict:
    """Index .cursor/rules/*.mdc — detect founder new-rule ships."""
    rules: list[dict] = []
    if CURSOR_RULES_DIR.is_dir():
        for path in sorted(CURSOR_RULES_DIR.glob("*.mdc")):
            try:
                stat = path.stat()
                head = path.read_text(encoding="utf-8", errors="replace")[:800]
            except OSError as exc:
                rules.append({"path": str(path.relative_to(ROOT)), "ok": False, "error": str(exc)[:80]})
                continue
            rules.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "name": path.name,
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "always_apply": "alwaysApply: true" in head,
                    "has_globs": "globs:" in head,
                }
            )
    digest = hash(tuple((r.get("path"), r.get("mtime")) for r in rules if r.get("path")))
    row = {
        "schema": "cursor-rules-index-v1",
        "at": _now(),
        "ok": True,
        "count": len(rules),
        "digest": digest,
        "rules": rules,
        "upgrade_command": "python3 scripts/agent_rule_live_wire_v1.py --on-new-rule --json",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        CURSOR_RULES_INDEX.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def _patch_h2_cursor_rules(*, cursor_index: dict, wire_ok: bool) -> None:
    reg = _read(H2_REGISTRY)
    if not reg:
        return
    reg["cursor_rules_index"] = {
        "at": _now(),
        "ok": wire_ok,
        "count": cursor_index.get("count", 0),
        "digest": cursor_index.get("digest"),
        "path": str(CURSOR_RULES_INDEX),
        "execution_model": "cloud_factories_only · mac_control_panel_only",
    }
    reg["updated_at"] = _now()
    reg["updated_by"] = "machine:agent_rule_live_wire:on-new-rule"
    H2_REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")


def upgrade_disk(*, role: str = "worker") -> dict:
    """Disk chain — anti-staleness (includes live wire) · factory-now · queue."""
    steps: list[dict] = []
    core_cmds = (
        ("anti_staleness_auto_wire", [PY, str(SCRIPTS / "anti_staleness_auto_wire_v1.py"), "--tier", "session", "--json"], 120),
        ("factory_now", [PY, str(SCRIPTS / "factory_control_v1.py"), "now", "--json"], 30),
        ("queue_ssot_unify", [PY, str(SCRIPTS / "queue_ssot_unify_v1.py"), "--json"], 30),
    )
    optional_cmds = (
        ("active_now_sync", [PY, str(SCRIPTS / "active_now_sync_from_factory_now_v1.py"), "--json"], 20),
    )
    for name, cmd, timeout in core_cmds:
        row = _run_json_step(cmd, timeout=timeout)
        row["step"] = name
        steps.append(row)
        if name == "anti_staleness_auto_wire" and not row.get("ok"):
            fallback = _run_json_step(
                [PY, str(SCRIPTS / "disk_live_wire_sync_v1.py"), "--role", role, "--json"],
                timeout=90,
            )
            fallback["step"] = "disk_live_wire_sync_fallback"
            steps.append(fallback)
    for name, cmd, timeout in optional_cmds:
        row = _run_json_step(cmd, timeout=timeout)
        row["step"] = name
        row["warn_only"] = True
        steps.append(row)
    disk = _read(DISK_WIRE_RECEIPT)
    surfaces = _read(SURFACES)
    core_ok = all(s.get("ok") for s in steps if not s.get("warn_only"))
    return {
        "ok": core_ok or bool(disk.get("ok")),
        "steps": steps,
        "disk_live_wire_ok": bool(disk.get("ok")),
        "factory_now_line": surfaces.get("factory_now_line") or disk.get("factory_now_line"),
        "queue_sa": disk.get("queue_sa") or surfaces.get("queue_sa"),
    }


def sync_rules_to_h2_registry(*, write: bool = True) -> dict:
    """Push every live registry rule into H2 /machines/ maintainer_ship bucket."""
    registry = load_registry()
    reg = _read(H2_REGISTRY)
    if not reg:
        reg = {
            "schema": "h2-pending-registry-v1",
            "version": "1.1",
            "next_phase": [],
            "deferred": [],
            "ops_blocker": [],
            "maintainer_ship": [],
        }
    bucket = [r for r in (reg.get("maintainer_ship") or []) if isinstance(r, dict) and not str(r.get("id") or "").startswith("RULE-WIRE-")]
    synced: list[str] = []
    for rule in registry.get("rules") or []:
        if str(rule.get("status") or "") != "live":
            continue
        rid = f"RULE-WIRE-{rule.get('id')}"
        bucket.append(
            {
                "id": rid,
                "title": f"Rule live wire · {rule.get('label')}",
                "win": f"{rule.get('surfaces_line_key')} on surfaces · nerves · disk receipt",
                "cadence": "on_rule_ship",
                "owner": "executor",
                "source": "agent_rule_live_wire_v1.py",
                "ssot": rule.get("ssot"),
                "script": rule.get("script"),
                "validator": rule.get("validator"),
                "rule_id": rule.get("id"),
                "layer": rule.get("layer"),
                "h2_url": "http://127.0.0.1:13020/machines/",
            }
        )
        synced.append(rid)
    reg["maintainer_ship"] = bucket
    reg["rule_live_wire"] = {"synced_at": _now(), "rule_ids": synced, "count": len(synced)}
    reg["updated_at"] = _now()
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        H2_REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "synced": synced, "count": len(synced), "path": str(H2_REGISTRY)}


def upgrade_machines() -> dict:
    """H2 machines registry + reconcile + hub cache bust."""
    steps: list[dict] = []
    h2 = sync_rules_to_h2_registry(write=True)
    steps.append({"step": "h2_rule_registry", **h2})

    for name, script in (
        ("h2_registry_sync", "h2_pending_registry_sync_v1.py"),
        ("h2_registry_reconcile", "h2_pending_registry_reconcile_v1.py"),
        ("machine_refinement_h2", "machine_refinement_h2_sync_v1.py"),
    ):
        row = _run_json_step([PY, str(SCRIPTS / script), "--json"], timeout=45)
        row["step"] = name
        steps.append(row)

    try:
        sys.path.insert(0, str(SCRIPTS))
        from machine_hub_v1 import invalidate_machine_hub_cache  # noqa: WPS433

        invalidate_machine_hub_cache()
        steps.append({"step": "machine_hub_cache_bust", "ok": True})
    except Exception as exc:
        steps.append({"step": "machine_hub_cache_bust", "ok": False, "error": str(exc)[:80]})

    reg = _read(H2_REGISTRY)
    ok = all(s.get("ok", True) for s in steps)
    return {"ok": ok, "steps": steps, "h2_rule_count": (reg.get("rule_live_wire") or {}).get("count", 0)}


def register_rule(rule_id: str, *, full_wire: bool = True) -> dict:
    registry = load_registry()
    for rule in registry.get("rules") or []:
        if str(rule.get("id")) == rule_id:
            val = validate_rule(rule)
            if full_wire:
                wire = wire_sync()
                val["wire_sync"] = {"ok": wire.get("ok"), "elapsed_sec": wire.get("elapsed_sec")}
            return val
    return {"ok": False, "error": f"rule not in registry:{rule_id}"}


def _run(cmd: list[str], *, timeout: float = 85.0) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=timeout, cwd=str(ROOT))
        return 0, out
    except subprocess.CalledProcessError as exc:
        return int(exc.returncode or 1), (exc.output or str(exc))[:500]
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def on_new_rule_upgrade(*, skip_heavy: bool = False, role: str = "worker") -> dict:
    """Founder ships new .mdc or registry row — mandatory disk + machines refresh."""
    t0 = time.monotonic()
    steps: list[dict] = []

    cursor_idx = sync_cursor_rules_index(write=True)
    steps.append({"step": "cursor_rules_index", "ok": bool(cursor_idx.get("ok")), "count": cursor_idx.get("count")})

    try:
        sys.path.insert(0, str(SCRIPTS))
        from agent_memory_mirror_v1 import sync_mirror  # noqa: WPS433

        mirror = sync_mirror()
        mirror_ok = bool((mirror.get("validation") or {}).get("ok", True))
        steps.append({"step": "memory_mirror_sync", "ok": mirror_ok, "hash8": mirror.get("mirror_hash8")})
    except Exception as exc:
        steps.append({"step": "memory_mirror_sync", "ok": False, "error": str(exc)[:120]})

    wire = wire_sync(skip_heavy=skip_heavy, role=role)
    steps.extend(wire.get("steps") or [])
    _patch_h2_cursor_rules(cursor_index=cursor_idx, wire_ok=bool(wire.get("ok")))

    try:
        sys.path.insert(0, str(SCRIPTS))
        from rule_zero_latency_hook_v1 import run_hook  # noqa: WPS433

        hook = run_hook(reason="on-new-rule", tier="fast", sync_cursor_index=False, sync_mirror=False)
        steps.append(
            {
                "step": "rule_zero_latency_hook",
                "ok": bool(hook.get("ok")),
                "line": hook.get("rule_wire_line"),
                "fanout_ok": (hook.get("fanout") or {}).get("ok"),
            }
        )
    except Exception as exc:
        steps.append({"step": "rule_zero_latency_hook", "ok": False, "error": str(exc)[:120]})

    elapsed = round(time.monotonic() - t0, 2)
    wire_ok = bool(wire.get("ok"))
    mirror_step = next((s for s in steps if s.get("step") == "memory_mirror_sync"), {})
    hook_step = next((s for s in steps if s.get("step") == "rule_zero_latency_hook"), {})
    ok = bool(cursor_idx.get("ok")) and wire_ok and mirror_step.get("ok", True) and hook_step.get("ok", True)
    row = {
        **wire,
        "schema": "agent-rule-live-wire-on-new-rule-v1",
        "at": _now(),
        "ok": ok,
        "elapsed_sec": elapsed,
        "steps": steps,
        "cursor_rules_count": cursor_idx.get("count"),
        "cursor_rules_index": str(CURSOR_RULES_INDEX),
        "command": "python3 scripts/agent_rule_live_wire_v1.py --on-new-rule --json",
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def wire_sync(*, skip_heavy: bool = False, role: str = "worker") -> dict:
    """Full chain — disk upgrade → registry → nerves → machines (H2) → validate."""
    t0 = time.monotonic()
    registry = load_registry()
    chain = (registry.get("procedure") or {}).get("chain_order") or []
    steps: list[dict] = []

    code, _out = _run(
        [PY, str(SCRIPTS / "founder_execution_model_v1.py"), "--wire-sync", "--skip-chain", "--json"],
        timeout=45,
    )
    steps.append({"step": "founder_execution_model_wire_sync", "ok": code == 0, "exit": code})

    code, _out = _run(
        [PY, str(SCRIPTS / "mac_law_mandatory_v1.py"), "--sync-receipt", "--json"],
        timeout=30,
    )
    steps.append({"step": "mac_law_mandatory_sync", "ok": code == 0, "exit": code})

    code, _out = _run(
        [PY, str(SCRIPTS / "mac_law_universal_wire_v1.py"), "--sync-receipt", "--json"],
        timeout=20,
    )
    steps.append({"step": "mac_law_universal_wire_sync", "ok": code == 0, "exit": code})

    code, _out = _run(
        [PY, str(SCRIPTS / "mac_law_agent_execution_plane_lock_v1.py"), "--sync-receipt", "--json"],
        timeout=20,
    )
    steps.append({"step": "mac_law_agent_execution_plane_lock_sync", "ok": code == 0, "exit": code})

    disk_row = upgrade_disk(role=role)
    steps.append({"step": "upgrade_disk", "ok": disk_row.get("ok"), "factory_now_line": (disk_row.get("factory_now_line") or "")[:72]})

    cursor_idx = sync_cursor_rules_index(write=True)
    steps.append({"step": "cursor_rules_index", "ok": bool(cursor_idx.get("ok")), "count": cursor_idx.get("count")})

    surfaces = _read(SURFACES)
    pulse_row = pulse_registry_to_surfaces(surfaces, write=True)
    SINA.mkdir(parents=True, exist_ok=True)
    SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "registry_pulse", "ok": pulse_row.get("ok"), "detail": pulse_row.get("line")})

    if not skip_heavy:
        code, _out = _run([PY, str(SCRIPTS / "better_loop_pulse_v1.py"), "--json"], timeout=45)
        steps.append({"step": "better_loop_pulse", "ok": code == 0, "exit": code, "warn_only": code != 0})

        code, _out = _run(
            [PY, str(SCRIPTS / "agent_nerve_system_v1.py"), "--patch-surfaces", "--json"],
            timeout=30,
        )
        steps.append({"step": "agent_nerve_pulse", "ok": code == 0, "exit": code, "warn_only": code != 0})

    machines_row = upgrade_machines()
    steps.append({"step": "upgrade_machines", "ok": machines_row.get("ok"), "h2_rules": machines_row.get("h2_rule_count")})

    val = validate_all()
    steps.append({"step": "validate_registry", "ok": val.get("ok"), "passed": val.get("passed"), "total": val.get("total")})
    _patch_h2_cursor_rules(cursor_index=cursor_idx, wire_ok=bool(val.get("ok")))

    elapsed = round(time.monotonic() - t0, 2)
    core_ok = bool(disk_row.get("ok")) and bool(machines_row.get("ok")) and bool(pulse_row.get("ok"))
    ok = core_ok and bool(val.get("ok"))
    row = {
        "schema": "agent-rule-live-wire-receipt-v1",
        "at": _now(),
        "ok": ok,
        "one_law": registry.get("one_law"),
        "rule_live_wire_line": pulse_row.get("line"),
        "disk_upgrade_ok": disk_row.get("ok"),
        "machines_upgrade_ok": machines_row.get("ok"),
        "h2_rule_count": machines_row.get("h2_rule_count"),
        "elapsed_sec": elapsed,
        "chain_order": chain,
        "steps": steps,
        "validation": val,
        "surfaces_path": str(SURFACES),
        "h2_registry_path": str(H2_REGISTRY),
        "procedure_command": "python3 scripts/agent_rule_live_wire_v1.py --wire-sync --json",
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    _sync_checkcart_w12(ok=ok)
    return row


def _sync_checkcart_w12(*, ok: bool) -> None:
    cart = _read(CHECKCART)
    if not cart:
        return
    mandatory = list(cart.get("mandatory_after_every_lock") or [])
    w12 = {
        "id": "W12",
        "step": "Rule live wire — disk + machines + nerves",
        "command": "python3 scripts/agent_rule_live_wire_v1.py --on-new-rule --json",
        "pass": "disk_live_wire ok · H2 RULE-WIRE-* rows · rule_live_wire_line · all live rules PASS",
    }
    if not any(str(x.get("id")) == "W12" for x in mandatory):
        mandatory.append(w12)
        cart["mandatory_after_every_lock"] = mandatory
        cart["at"] = _now()
        CHECKCART.write_text(json.dumps(cart, indent=2) + "\n", encoding="utf-8")


def scaffold(rule_id: str) -> dict:
    registry = load_registry()
    proc = registry.get("procedure") or {}
    return {
        "rule_id": rule_id,
        "one_law": registry.get("one_law"),
        "steps": proc.get("steps"),
        "template_row": {
            "id": rule_id,
            "label": "Human label",
            "status": "live",
            "layer": "commercial|governance|factory",
            "ssot": f"data/{rule_id.replace('_', '-')}-v1.json",
            "script": f"scripts/{rule_id}_v1.py",
            "pulse_fn": "assess",
            "validator": f"scripts/validate-{rule_id.replace('_', '-')}-v1.sh",
            "receipt": f"~/.sina/{rule_id.replace('_', '-')}-receipt-v1.json",
            "surfaces_line_key": f"{rule_id}_line",
            "surfaces_block_key": rule_id,
            "nerve_keys": [],
            "anti_theater_check": "",
            "runs_on": ["scripts/disk_live_wire_sync_v1.py", "scripts/agent_nerve_system_v1.py"],
        },
        "finish": "python3 scripts/agent_rule_live_wire_v1.py --on-new-rule --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent rule live wire registry orchestrator")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--register", metavar="RULE_ID")
    ap.add_argument("--pulse", action="store_true", help="Pulse all live rules to surfaces only")
    ap.add_argument("--wire-sync", action="store_true", help="Disk + machines + nerves full chain")
    ap.add_argument(
        "--on-new-rule",
        action="store_true",
        help="Mandatory after new .mdc — index rules · mirror · disk · H2 machines",
    )
    ap.add_argument("--upgrade-disk-machines", action="store_true", help="Alias for --on-new-rule")
    ap.add_argument("--upgrade-disk", action="store_true", help="Anti-staleness · disk live wire · factory-now")
    ap.add_argument("--upgrade-machines", action="store_true", help="H2 /machines/ registry sync for live rules")
    ap.add_argument("--scaffold", metavar="RULE_ID")
    ap.add_argument("--skip-heavy", action="store_true")
    args = ap.parse_args()

    if args.list:
        reg = load_registry()
        row = {"rules": [{"id": r.get("id"), "status": r.get("status"), "label": r.get("label")} for r in reg.get("rules") or []]}
    elif args.scaffold:
        row = scaffold(args.scaffold)
    elif args.register:
        row = register_rule(args.register)
    elif args.validate:
        row = validate_all()
    elif args.upgrade_disk:
        row = upgrade_disk()
    elif args.upgrade_machines:
        row = upgrade_machines()
    elif args.wire_sync:
        row = wire_sync(skip_heavy=args.skip_heavy)
    elif args.on_new_rule or args.upgrade_disk_machines:
        row = on_new_rule_upgrade(skip_heavy=args.skip_heavy)
    elif args.pulse:
        surfaces = _read(SURFACES)
        row = pulse_registry_to_surfaces(surfaces, write=True)
        SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    else:
        row = validate_all()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("rule_live_wire_line") or row.get("line") or row)
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
