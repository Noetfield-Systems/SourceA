#!/usr/bin/env python3
"""FORM_OFFICIAL E2E wire — unify intake · form mirror · Canvas · hub · receipts.

SSOT index: data/form_official_nerve_map_v1.json
Receipt: ~/.sina/form-official-wire-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
NERVE_MAP = ROOT / "data/form_official_nerve_map_v1.json"
WIRE_RECEIPT = SINA / "form-official-wire-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _expand(path: str) -> Path:
    p = path.replace("~", str(Path.home()))
    if not p.startswith("/"):
        return ROOT / p
    return Path(p)


def _run(label: str, cmd: list[str], *, timeout: int = 300) -> dict:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
    return {
        "step": label,
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-500:],
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def _load_nerve_map() -> dict:
    if not NERVE_MAP.is_file():
        return {}
    return json.loads(NERVE_MAP.read_text(encoding="utf-8"))


def _path_checks(nerve: dict) -> list[dict]:
    checks: list[dict] = []
    targets: list[tuple[str, str]] = [
        ("m1_canvas", nerve.get("canvas", {}).get("m1_canvas", "")),
        ("open_row_spec", nerve.get("canvas", {}).get("open_row_spec", "")),
        ("generated_data", nerve.get("canvas", {}).get("generated_data", "")),
        ("intake", nerve.get("receipts", {}).get("intake", "")),
        ("third_form", nerve.get("receipts", {}).get("third_form", "")),
        ("live_form_machine", nerve.get("live_form", {}).get("machine", "")),
    ]
    for label, raw in targets:
        if not raw:
            continue
        path = _expand(raw)
        checks.append({"id": label, "path": str(path), "ok": path.is_file()})
    for scratch in nerve.get("canvas", {}).get("forbidden_scratch") or []:
        path = _expand(scratch)
        checks.append({"id": f"forbidden:{path.name}", "path": str(path), "ok": not path.is_file()})
    return checks


def _form_snapshot() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from live_founder_decision_form_v1 import payload  # noqa: WPS433

    return payload()


def _form_official_line(form: dict) -> str:
    oq = int(form.get("open_questions_count") or 0)
    edition = form.get("active_form_edition") or form.get("form_edition") or "v2"
    if oq > 0:
        ids = [q.get("id") for q in (form.get("open_questions") or [])[:3]]
        head = " · ".join(i for i in ids if i)
        return f"FORM_OFFICIAL · {edition} · {oq} open PICKs · M1 Canvas · {head}"
    return f"FORM_OFFICIAL · {edition} · filled · M1 Canvas slot D"


def wire(
    *,
    regen: bool = True,
    validate: bool = True,
    sync_surfaces: bool = False,
    sync_hub: bool = False,
) -> dict:
    nerve = _load_nerve_map()
    steps: list[dict] = []

    if regen:
        steps.append(_run("regen_canvas", [sys.executable, str(SCRIPTS / "generate_integrity_canvas_form_data_v1.py")]))

    steps.append(_run("write_receipt", [sys.executable, str(SCRIPTS / "live_founder_decision_form_v1.py"), "--write-receipt"]))

    reconcile_cmd = [sys.executable, str(SCRIPTS / "form_open_questions_reconcile_v1.py"), "--json"]
    if regen:
        reconcile_cmd.append("--regen")
    proc = subprocess.run(reconcile_cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    reconcile: dict = {}
    try:
        reconcile = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        reconcile = {"ok": False, "parse_error": True}
    steps.append(
        {
            "step": "reconcile",
            "ok": proc.returncode == 0 and bool(reconcile.get("ok")),
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-500:],
            "stderr_tail": (proc.stderr or "")[-500:],
        }
    )

    steps.append(_run("form_minder", [sys.executable, str(SCRIPTS / "form_official_minder_v1.py")]))

    if validate:
        steps.append(
            _run(
                "validate_canvas_ssot",
                ["bash", str(SCRIPTS / "validate-integrity-form-canvas-ssot-v1.sh")],
            )
        )
        steps.append(
            _run(
                "validate_e2e",
                ["bash", str(SCRIPTS / "validate-form-official-e2e-v1.sh")],
            )
        )

    if sync_surfaces:
        steps.append(_run("disk_live_wire", [sys.executable, str(SCRIPTS / "disk_live_wire_sync_v1.py")]))

    if sync_hub:
        steps.append(_run("build_hub", [sys.executable, str(SCRIPTS / "build-sina-command-panel.py")], timeout=300))

    form = _form_snapshot()
    path_checks = _path_checks(nerve)
    paths_ok = all(c.get("ok") for c in path_checks)
    core_steps = {"regen_canvas", "write_receipt", "reconcile"}
    if validate:
        core_steps |= {"validate_canvas_ssot", "validate_e2e"}
    core_ok = all(s.get("ok") for s in steps if s.get("step") in core_steps) and bool(reconcile.get("ok"))

    result = {
        "ok": core_ok and paths_ok,
        "schema": "form-official-wire-receipt-v1",
        "wired_at": _now(),
        "nerve_map": str(NERVE_MAP),
        "form_official_line": _form_official_line(form),
        "active_form_edition": form.get("active_form_edition"),
        "open_questions_count": form.get("open_questions_count"),
        "open_question_ids": [q.get("id") for q in (form.get("open_questions") or [])],
        "canvas_open_count": form.get("canvas_open_count"),
        "awaiting_founder_picks": form.get("awaiting_founder_picks"),
        "reconcile": {
            "ok": reconcile.get("ok"),
            "open_count": reconcile.get("open_count"),
            "canvas_open_count": reconcile.get("canvas_open_count"),
            "missing_on_canvas": reconcile.get("missing_on_canvas"),
            "extra_on_canvas": reconcile.get("extra_on_canvas"),
        },
        "path_checks": path_checks,
        "steps": steps,
        "hub_action": nerve.get("hub", {}).get("action_label"),
        "canvas_path": nerve.get("canvas", {}).get("m1_canvas"),
        "find_fast": nerve.get("find_fast", {}),
    }

    WIRE_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    WIRE_RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["receipt_path"] = str(WIRE_RECEIPT)

    nerve["saved_at"] = _now()
    nerve["active"] = {
        "edition": form.get("active_form_edition"),
        "open_count": form.get("open_questions_count"),
        "open_ids": result["open_question_ids"],
        "form_official_line": result["form_official_line"],
        "awaiting_founder_picks": form.get("awaiting_founder_picks"),
    }
    NERVE_MAP.write_text(json.dumps(nerve, indent=2) + "\n", encoding="utf-8")

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="FORM_OFFICIAL E2E wire — unify all nerves")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-regen", action="store_true")
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument("--sync-surfaces", action="store_true")
    ap.add_argument("--sync-hub", action="store_true")
    args = ap.parse_args()
    result = wire(
        regen=not args.no_regen,
        validate=not args.no_validate,
        sync_surfaces=args.sync_surfaces,
        sync_hub=args.sync_hub,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "OK" if result.get("ok") else "FAIL"
        print(
            f"{status}: {result.get('form_official_line')} "
            f"open={result.get('open_questions_count')} canvas={result.get('canvas_open_count')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
