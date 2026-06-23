#!/usr/bin/env python3
"""Validator machine — tracked probes + logs for all founder apps (no agent marathon)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "validator-machine-registry-v1.json"
LOG_DIR = SINA / "validator-machine" / "logs"
ACTIVE_TERMINAL = SINA / "validator-machine" / "active-terminal.log"
ACTIVE_STATE = SINA / "validator-machine" / "active-terminal-state.json"
RECEIPT = SINA / "validator-machine-last-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _log_line(log_path: Path, level: str, msg: str, **extra: Any) -> None:
    row = {"at": _now(), "level": level, "msg": msg, **extra}
    line = json.dumps(row, ensure_ascii=False)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    if os.environ.get("VALIDATOR_MACHINE_QUIET") != "1":
        print(line, flush=True)


def _http_probe(url: str, *, timeout: float = 8.0) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SourceA-validator-machine/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            body = json.loads(raw) if raw.strip() else {}
            return {"ok": resp.status == 200 and bool(body.get("ok", True)), "status": resp.status, "body": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "url": url}


def _emit_terminal(line: str, *, lines: list[str] | None = None) -> str:
    ACTIVE_TERMINAL.parent.mkdir(parents=True, exist_ok=True)
    with ACTIVE_TERMINAL.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    if lines is not None:
        lines.append(line)
    return line


def _set_terminal_state(doc: dict[str, Any]) -> None:
    ACTIVE_STATE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_STATE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _read_terminal_state() -> dict[str, Any]:
    if not ACTIVE_STATE.is_file():
        return {"running": False}
    try:
        return json.loads(ACTIVE_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"running": False}


def terminal_tail(*, lines: int = 80) -> dict[str, Any]:
    state = _read_terminal_state()
    tail: list[str] = []
    if ACTIVE_TERMINAL.is_file():
        try:
            tail = ACTIVE_TERMINAL.read_text(encoding="utf-8").strip().splitlines()[-lines:]
        except OSError:
            pass
    return {
        "ok": True,
        "schema": "validator-terminal-tail-v1",
        "at": _now(),
        "running": bool(state.get("running")),
        "tier": state.get("tier"),
        "app_id": state.get("app_id"),
        "terminal_lines": tail,
        "line_count": len(tail),
        "log_path": str(ACTIVE_TERMINAL),
    }


def run_terminal_session(
    *,
    app_id: str = "n8n_integration",
    tier: str = "probe",
    include_chain: bool = True,
    write: bool = True,
) -> dict[str, Any]:
    """Run validators with live terminal lines — probe+fast chain under ~5s."""
    lines: list[str] = []
    ACTIVE_TERMINAL.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_TERMINAL.write_text("", encoding="utf-8")
    _set_terminal_state({"running": True, "at": _now(), "app_id": app_id, "tier": tier})

    _emit_terminal(f"═══ Validator terminal · {app_id} · tier={tier} · {_now()} ═══", lines=lines)
    ok = True

    if include_chain:
        _emit_terminal("→ living system chain (fast parallel probes)…", lines=lines)
        try:
            from living_system_chain_validate_v1 import validate_chains_fast  # noqa: WPS433

            chain = validate_chains_fast(write=write)
            for ch in chain.get("chains") or []:
                mark = "PASS" if ch.get("ok") else "FAIL"
                err = f" — {ch.get('error')}" if ch.get("error") else ""
                _emit_terminal(f"  [{mark}] {ch.get('label') or ch.get('id')}{err}", lines=lines)
            _emit_terminal(chain.get("summary_line") or "chain done", lines=lines)
            if not chain.get("ok"):
                ok = False
        except Exception as exc:
            _emit_terminal(f"  [FAIL] chain exception — {exc}", lines=lines)
            ok = False

    _emit_terminal(f"→ app probe {app_id}…", lines=lines)
    row = run_app(app_id, tier=tier, write=write)
    _emit_terminal(
        f"  [{'PASS' if row.get('ok') else 'FAIL'}] probe {row.get('label') or app_id} · v{row.get('version') or '—'}",
        lines=lines,
    )
    if row.get("log_path"):
        _emit_terminal(f"  log: {row.get('log_path')}", lines=lines)
    for ln in row.get("log_tail") or []:
        _emit_terminal(f"  | {ln}", lines=lines)
    if not row.get("ok"):
        ok = False

    _emit_terminal(f"═══ done · {'PASS' if ok else 'FAIL'} · {_now()} ═══", lines=lines)
    out = {
        "ok": ok,
        "schema": "validator-terminal-run-v1",
        "at": _now(),
        "app_id": app_id,
        "tier": tier,
        "terminal_lines": lines,
        "log_path": str(ACTIVE_TERMINAL),
        "run": row,
    }
    _set_terminal_state({"running": False, "at": _now(), "app_id": app_id, "tier": tier, "ok": ok})
    return out


def start_terminal_session_async(**kwargs: Any) -> dict[str, Any]:
    state = _read_terminal_state()
    if state.get("running"):
        return {"ok": True, "started": False, "running": True, "message": "Validator already running"}
    thread = threading.Thread(target=run_terminal_session, kwargs=kwargs, daemon=True)
    thread.start()
    return {"ok": True, "started": True, "running": True, "message": "Validator terminal started"}


def _run_light_script(app: dict[str, Any], log_path: Path) -> dict[str, Any]:
    rel = str(app.get("light_validator") or "")
    if not rel:
        return {"ok": True, "skipped": True, "reason": "no_light_validator"}
    path = ROOT / rel
    if not path.is_file():
        _log_line(log_path, "WARN", "light_validator_missing", path=str(path))
        return {"ok": False, "error": "light_validator_missing"}
    args = list(app.get("light_args") or [])
    if path.suffix == ".py":
        cmd = [sys.executable, str(path), *args]
    else:
        cmd = ["bash", str(path), *args]
    _log_line(log_path, "INFO", "light_start", cmd=" ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=30)
    tail = (proc.stdout or proc.stderr or "")[-800:]
    _log_line(log_path, "INFO" if proc.returncode == 0 else "ERROR", "light_done", exit=proc.returncode, tail=tail)
    return {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": tail}


def _run_full_script(app: dict[str, Any], log_path: Path) -> dict[str, Any]:
    rel = str(app.get("full_validator") or "")
    if not rel:
        return {"ok": True, "skipped": True, "reason": "no_full_validator"}
    path = ROOT / rel
    if not path.is_file():
        _log_line(log_path, "WARN", "full_validator_missing", path=str(path))
        return {"ok": False, "error": "full_validator_missing"}
    cmd = ["bash", str(path)] if path.suffix == ".sh" else [sys.executable, str(path)]
    _log_line(log_path, "INFO", "full_start", cmd=" ".join(cmd))
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n--- full validator {rel} {_now()} ---\n")
        proc = subprocess.run(cmd, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT, timeout=600)
    _log_line(log_path, "INFO" if proc.returncode == 0 else "ERROR", "full_done", exit=proc.returncode)
    return {"ok": proc.returncode == 0, "exit": proc.returncode, "log": str(log_path)}


def run_app(app_id: str, *, tier: str = "light", write: bool = True) -> dict[str, Any]:
    ssot = _read(SSOT)
    app = next((a for a in ssot.get("apps") or [] if a.get("id") == app_id), None)
    if not app:
        return {"ok": False, "error": f"unknown_app:{app_id}"}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOG_DIR / f"{app_id}-{tier}-{stamp}.log"
    _log_line(log_path, "INFO", "run_start", app_id=app_id, tier=tier, label=app.get("label"))

    probe_url = str(app.get("probe") or app.get("health") or "")
    probe = _http_probe(probe_url) if probe_url else {"ok": False, "error": "no_probe_url"}
    _log_line(log_path, "INFO" if probe.get("ok") else "ERROR", "probe", url=probe_url, ok=probe.get("ok"))

    row: dict[str, Any] = {
        "id": app_id,
        "label": app.get("label"),
        "tier": tier,
        "ok": bool(probe.get("ok")),
        "probe": probe,
        "log_path": str(log_path),
        "version": (probe.get("body") or {}).get("version"),
    }

    if tier in ("light", "full") and probe.get("ok"):
        light = _run_light_script(app, log_path)
        row["light"] = light
        if not light.get("ok") and not light.get("skipped"):
            row["ok"] = False

    if tier == "full" and probe.get("ok"):
        full = _run_full_script(app, log_path)
        row["full"] = full
        if not full.get("ok") and not full.get("skipped"):
            row["ok"] = False

    row["log_tail"] = _tail_log(log_path, lines=12)
    if write:
        _append_receipt(app_id, row, tier=tier)
    return row


def _tail_log(path: Path, *, lines: int = 20) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
        return text.strip().splitlines()[-lines:]
    except OSError:
        return []


def _append_receipt(app_id: str, row: dict[str, Any], *, tier: str) -> None:
    prev = _read(RECEIPT) if RECEIPT.is_file() else {"schema": "validator-machine-last-receipt-v1", "runs": []}
    runs = list(prev.get("runs") or [])
    runs.insert(0, {"at": _now(), "app_id": app_id, "tier": tier, **row})
    prev["runs"] = runs[:40]
    prev["at"] = _now()
    prev["summary_line"] = (
        f"Validator machine · last {app_id} {tier} {'PASS' if row.get('ok') else 'FAIL'} · log {row.get('log_path')}"
    )
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(prev, indent=2) + "\n", encoding="utf-8")


def run_all(*, tier: str = "light", write: bool = True) -> dict[str, Any]:
    ssot = _read(SSOT)
    apps = ssot.get("apps") or []
    rows = [run_app(str(a.get("id")), tier=tier, write=False) for a in apps]
    ok = all(r.get("ok") for r in rows)
    out = {
        "schema": "validator-machine-run-v1",
        "at": _now(),
        "tier": tier,
        "ok": ok,
        "apps": rows,
        "summary_line": f"Validator machine {tier} · {sum(1 for r in rows if r.get('ok'))}/{len(rows)} PASS",
        "receipt": str(RECEIPT),
        "log_dir": str(LOG_DIR),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps({**out, "runs": rows}, indent=2) + "\n", encoding="utf-8")
    return out


def hub_slice(*, app_id: str | None = None) -> dict[str, Any]:
    receipt = _read(RECEIPT)
    runs = receipt.get("runs") or receipt.get("apps") or []
    if app_id:
        runs = [r for r in runs if r.get("app_id") == app_id or r.get("id") == app_id]
    latest = runs[0] if runs else {}
    tail: list[str] = []
    log_path = latest.get("log_path")
    if log_path:
        tail = _tail_log(Path(log_path), lines=15)
    return {
        "ok": True,
        "schema": "validator-machine-hub-slice-v1",
        "at": receipt.get("at") or _now(),
        "summary_line": receipt.get("summary_line") or "No validator run yet — tap Validate living chains or run validator_machine_v1.py",
        "log_dir": str(LOG_DIR),
        "receipt": str(RECEIPT),
        "latest": latest,
        "log_tail": tail,
        "ssot": str(SSOT.relative_to(ROOT)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validator machine v1")
    ap.add_argument("--app", help="Single app id")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--tier", choices=["probe", "light", "full"], default="light")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--terminal-run", action="store_true")
    ap.add_argument("--terminal-tail", action="store_true")
    ap.add_argument("--include-chain", action="store_true", default=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.json:
        os.environ["VALIDATOR_MACHINE_QUIET"] = "1"
    if args.terminal_tail:
        out = terminal_tail()
    elif args.terminal_run:
        out = run_terminal_session(
            app_id=args.app or "n8n_integration",
            tier=args.tier,
            include_chain=args.include_chain,
        )
    elif args.hub_slice:
        out = hub_slice(app_id=args.app)
    elif args.all:
        out = run_all(tier=args.tier)
    elif args.app:
        out = run_app(args.app, tier=args.tier)
    else:
        out = run_all(tier="probe")
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(out.get("summary_line") or out)
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
