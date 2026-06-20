#!/usr/bin/env python3
"""Commercial email send defer — CLOUD factories only; Mac = control panel.

Law: data/commercial-email-send-defer-v1.json
Receipt: ~/.sina/commercial-email-send-defer-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "commercial-email-send-defer-v1.json"
RECEIPT = SINA / "commercial-email-send-defer-receipt-v1.json"
LIFT = SINA / "commercial-email-send-defer-lift-v1.json"
DEFER_FLAG = SINA / "commercial-email-send-deferred-v1.flag"
SECRETS = SINA / "secrets.env"


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
    return Path(path.replace("~", str(Path.home())))


def _secret(key: str) -> str:
    if not SECRETS.is_file():
        return ""
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return ""


def _http_json(url: str, *, timeout: float = 10.0) -> tuple[bool, dict | str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = int(getattr(resp, "status", 200) or 200)
        try:
            row = json.loads(body)
            return True, {"status": status, "body": row}
        except json.JSONDecodeError:
            return True, {"status": status, "body_preview": body[:120]}
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return False, str(exc)[:120]


def _http_status(url: str, *, timeout: float = 10.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", 200) or 200)
        return status < 400, f"HTTP {status}"
    except urllib.error.HTTPError as exc:
        return exc.code < 400, f"HTTP {exc.code}"
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return False, str(exc)[:120]


def _http_body_text(url: str, *, timeout: float = 12.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, TimeoutError) as exc:
        return False, str(exc)[:120]


def _resolve_public_fbe_url(row: dict) -> tuple[str, str]:
    """Cloud factory URL — public HTTPS with fbe health only; no mirror fallback."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from fbe.lib.public_worker_url_v1 import resolve_public_fbe_url  # noqa: WPS433

    return resolve_public_fbe_url(require_health=False)


def _main_factory_ids(ssot: dict) -> list[str]:
    fem = _read(ROOT / "data" / "founder-execution-model-v1.json")
    cloud = fem.get("cloud_role") or ssot.get("execution_model") or {}
    ids = cloud.get("main_cloud_factories") or []
    deferred = {d.get("id") for d in (cloud.get("deferred_lanes") or []) if d.get("id")}
    return [str(x) for x in ids if str(x) not in deferred and str(x) != "commercial_email_cloud"]


def _probe_main_factory(fid: str, probe: dict) -> dict:
    label = str(probe.get("label") or fid)
    required = bool(probe.get("required", True))
    ptype = str(probe.get("type") or "")

    if ptype == "receipt":
        rec = _read(_expand(str(probe.get("receipt") or "")))
        ok = bool(rec.get("ok"))
        return {"id": fid, "label": label, "required": required, "kind": "receipt", "ok": ok, "detail": f"ok={rec.get('ok')}"}

    if ptype == "fbe_public_health":
        row = {"config": probe.get("config"), "secrets_env_key": "FBE_CLOUD_WORKER_URL", "mirror_fallback_key": "mono_mirror_fallback", "health_suffix": "/health", "expect_service_prefix": "fbe", "required": required, "label": label, "id": fid}
        return _probe_cloud_factory(row)

    if ptype == "script":
        path = ROOT / str(probe.get("path") or "")
        ok = False
        return {"id": fid, "label": label, "required": required, "kind": "script", "ok": ok, "detail": "mac_disk_not_cloud_factory"}

    if ptype == "file":
        path = ROOT / str(probe.get("path") or "")
        ok = False
        return {"id": fid, "label": label, "required": required, "kind": "file", "ok": ok, "detail": "mac_disk_not_cloud_factory"}

    if ptype == "cloud_receipt_field":
        rec = _read(_expand(str(probe.get("receipt") or "")))
        field = str(probe.get("field") or "ok")
        expect = str(probe.get("expect") or "")
        val = str(rec.get(field) or "")
        ok = val == expect if expect else bool(rec.get(field))
        return {"id": fid, "label": label, "required": required, "kind": "cloud_receipt_field", "ok": ok, "detail": f"{field}={val or '?'}"}

    if ptype == "cloud_url_secret":
        env = str(probe.get("env") or "")
        url = _secret(env)
        ok = bool(url) and url.startswith("https://")
        return {"id": fid, "label": label, "required": required, "kind": "cloud_url_secret", "ok": ok, "detail": f"{env}={'https' if ok else 'missing_or_local'}"}

    if ptype == "secret":
        env = str(probe.get("env") or "")
        ok = bool(_secret(env))
        return {"id": fid, "label": label, "required": required, "kind": "secret", "ok": ok, "detail": f"{env}={'set' if ok else 'missing'}"}

    if ptype == "fbe_factory_builder_bundle":
        bundle_path = ROOT / str(probe.get("bundle") or "data/fbe_factory_builder_bundle_v1.json")
        bundle = _read(bundle_path)
        schema_ok = bundle.get("schema") == "fbe-factory-builder-bundle-v1"
        two_plane = bundle.get("two_plane") or {}
        exec_plane = two_plane.get("execution") or {}
        cloud_headless = exec_plane.get("location") == "cloud" and bool(exec_plane.get("headless"))
        ok = schema_ok and cloud_headless
        detail = f"schema={bundle.get('schema')} cloud_headless={cloud_headless}"
        if ok:
            fbe_probe = _probe_main_factory(
                "fbe_railway",
                ( _read(SSOT).get("main_factory_probes") or {}).get("fbe_railway") or {"type": "unknown"},
            )
            if fbe_probe.get("required") and not fbe_probe.get("ok"):
                ok = False
                detail += f" · fbe_health=RED ({fbe_probe.get('detail', '')[:80]})"
        return {"id": fid, "label": label, "required": required, "kind": "fbe_factory_builder_bundle", "ok": ok, "detail": detail}

    return {"id": fid, "label": label, "required": required, "kind": "unknown", "ok": False, "detail": "unknown probe type"}


def _probe_cloud_factory(row: dict) -> dict:
    fid = str(row.get("id") or "")
    label = str(row.get("label") or fid)
    required = bool(row.get("required", True))

    receipt_path = str(row.get("receipt") or "")
    if receipt_path:
        rec = _read(_expand(receipt_path))
        ok_key = str(row.get("receipt_ok_key") or "ok")
        ok = bool(rec.get(ok_key))
        return {
            "id": fid,
            "label": label,
            "required": required,
            "kind": "receipt",
            "ok": ok,
            "detail": f"{receipt_path} {ok_key}={rec.get(ok_key)}",
        }

    base, source = _resolve_public_fbe_url(row)
    suffix = str(row.get("health_suffix") or "/health")
    if not base:
        return {
            "id": fid,
            "label": label,
            "required": required,
            "kind": "cloud_http",
            "ok": False,
            "detail": f"no public cloud URL ({source}) — Mac/local proxy does not count",
        }
    url = f"{base}{suffix}"
    ok_raw, payload = _http_json(url)
    ok = ok_raw
    detail = f"{url} via {source}"
    if ok_raw and isinstance(payload, dict):
        body = payload.get("body") or {}
        if isinstance(body, dict):
            prefix = str(row.get("expect_service_prefix") or "")
            if prefix:
                svc = str(body.get("service") or "")
                ok = bool(body.get("ok")) and svc.startswith(prefix)
                detail = f"{url} service={svc or '?'}"
            elif row.get("require_public_https"):
                ok = bool(body.get("ok"))
    elif not ok_raw:
        detail = f"{url} {payload}"
    return {
        "id": fid,
        "label": label,
        "required": required,
        "kind": "cloud_http",
        "ok": ok,
        "detail": detail,
    }


def _probe_mac_panel(row: dict) -> dict:
    url = str(row.get("url") or "")
    ok, detail = _http_json(url) if url else (False, "missing url")
    panel_ok = ok
    if ok and isinstance(detail, dict):
        body = detail.get("body") or {}
        if isinstance(body, dict) and "ok" in body:
            panel_ok = bool(body.get("ok"))
    return {
        "id": str(row.get("id") or "mac_control_panel"),
        "label": str(row.get("label") or "Mac control panel"),
        "ok": panel_ok,
        "gates_email_send": False,
        "detail": f"{url} · {detail if isinstance(detail, str) else 'ok'}",
    }


def _probe_site(row: dict) -> dict:
    sid = str(row.get("id") or "")
    label = str(row.get("label") or sid)
    url = str(row.get("url") or "")
    required = bool(row.get("required", True))
    if not url:
        return {"id": sid, "label": label, "required": required, "ok": False, "detail": "missing url"}
    ok, detail = _http_status(url)
    min_status = int(row.get("min_status") or 200)
    if "HTTP" in detail:
        try:
            code = int(detail.split()[-1])
            ok = code >= min_status and code < 400
        except ValueError:
            pass
    markers = [str(m) for m in (row.get("content_markers") or []) if m]
    stale = [str(m) for m in (row.get("stale_markers") or []) if m]
    if ok and (markers or stale):
        body_ok, body = _http_body_text(url)
        if not body_ok:
            ok = False
            detail = f"body fetch failed · {body}"
        else:
            missing = [m for m in markers if m not in body]
            hit_stale = [m for m in stale if m in body]
            if missing or hit_stale:
                ok = False
                parts = []
                if missing:
                    parts.append(f"missing: {', '.join(missing)}")
                if hit_stale:
                    parts.append(f"stale: {', '.join(hit_stale)}")
                detail = " · ".join(parts)
    return {"id": sid, "label": label, "required": required, "ok": ok, "detail": f"{url} · {detail}"}


def _founder_lift() -> bool:
    return bool(_read(LIFT).get("founder_lift"))


def assess(*, write: bool = True) -> dict:
    ssot = _read(SSOT)
    mac_panel = _probe_mac_panel(ssot.get("mac_control_panel") or {})
    probe_map = ssot.get("main_factory_probes") or {}
    main_ids = _main_factory_ids(ssot)
    main = [_probe_main_factory(fid, probe_map.get(fid) or {"type": "unknown"}) for fid in main_ids if fid in probe_map]
    sites = [_probe_site(s) for s in ssot.get("product_sites") or []]

    req_main = [m for m in main if m.get("required")]
    req_sites = [s for s in sites if s.get("required")]
    main_factories_online = bool(req_main) and all(m.get("ok") for m in req_main)
    sites_online = bool(req_sites) and all(s.get("ok") for s in req_sites)
    founder_lift = _founder_lift()

    hardening_ready = main_factories_online and sites_online
    defer_active = not (hardening_ready and founder_lift)

    main_req_ok = sum(1 for m in req_main if m.get("ok"))
    line = (
        f"email-defer · {'ON' if defer_active else 'LIFTED'} · "
        f"main={main_req_ok}/{len(req_main)} · "
        f"sites={'PASS' if sites_online else 'RED'} · "
        f"email=AFTER_MAIN · "
        f"lift={'YES' if founder_lift else 'NO'}"
    )

    row = {
        "schema": "commercial-email-send-defer-receipt-v1",
        "at": _now(),
        "ok": True,
        "one_law": ssot.get("one_law"),
        "execution_model": ssot.get("execution_model"),
        "defer_active": defer_active,
        "main_factories_online": main_factories_online,
        "cloud_factories_online": main_factories_online,
        "sites_online": sites_online,
        "workers_online": main_factories_online,
        "hardening_ready": hardening_ready,
        "founder_lift": founder_lift,
        "email_send_defer_line": line,
        "deferred_lane": ssot.get("deferred_lane") or {},
        "mac_control_panel": mac_panel,
        "main_cloud_factories": main,
        "cloud_factories": main,
        "product_sites": sites,
        "ssot": str(SSOT.relative_to(ROOT)),
        "lift_command": (ssot.get("lift_policy") or {}).get("lift_command"),
    }

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        if defer_active:
            DEFER_FLAG.write_text(f"defer_active_at={row['at']}\n", encoding="utf-8")
        elif DEFER_FLAG.is_file():
            DEFER_FLAG.unlink(missing_ok=True)

    return row


def is_defer_active() -> bool:
    cached = _read(RECEIPT)
    if cached.get("defer_active") is not None:
        return bool(cached.get("defer_active"))
    return assess(write=False).get("defer_active", True)


def assert_send_allowed(*, action: str = "send") -> None:
    row = assess(write=False)
    if row.get("defer_active"):
        missing = []
        if not row.get("main_factories_online"):
            missing.append("main_cloud_factories")
        if not row.get("sites_online"):
            missing.append("product_sites")
        if not row.get("founder_lift"):
            missing.append("founder_lift")
        msg = (
            f"BLOCKED: email send deferred — email runs AFTER main factories · "
            f"need {' + '.join(missing) or 'cloud hardening'}. "
            f"Mac is control panel only. "
            f"Law: data/commercial-email-send-defer-v1.json"
        )
        print(msg, file=sys.stderr)
        raise SystemExit(2)


def lift(*, force: bool = False) -> dict:
    row = assess(write=True)
    if not force and not row.get("hardening_ready"):
        row["lift_error"] = "main cloud factories + product sites must be online before email lane lifts"
        row["ok"] = False
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row
    lift_row = {
        "schema": "commercial-email-send-defer-lift-v1",
        "founder_lift": True,
        "lifted_at": _now(),
        "hardening_ready": row.get("hardening_ready"),
        "cloud_factories_online": row.get("main_factories_online"),
        "sites_online": row.get("sites_online"),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    LIFT.write_text(json.dumps(lift_row, indent=2) + "\n", encoding="utf-8")
    return assess(write=True)


def validate_defer_wire() -> dict:
    ssot_ok = SSOT.is_file()
    row = assess(write=True)
    defer = bool(row.get("defer_active"))
    nerve = _read(SINA / "agent-nerve-system-receipt-v1.json")
    send_ready = bool((nerve.get("ship_gates") or {}).get("w3_send_ready"))
    send_blocked = (not send_ready) if defer else True
    ok = ssot_ok and bool(row.get("email_send_defer_line")) and send_blocked
    return {
        "ok": ok,
        "defer_active": defer,
        "main_factories_online": row.get("main_factories_online"),
        "cloud_factories_online": row.get("main_factories_online"),
        "sites_online": row.get("sites_online"),
        "founder_lift": row.get("founder_lift"),
        "w3_send_ready": send_ready,
        "send_blocked_while_defer": send_blocked,
        "email_send_defer_line": row.get("email_send_defer_line"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Commercial email send defer — cloud factories only")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lift", action="store_true")
    ap.add_argument("--force-lift", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--validate-wire", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    if args.lift or args.force_lift:
        row = lift(force=args.force_lift)
    elif args.validate_wire:
        row = validate_defer_wire()
    else:
        row = assess(write=not args.no_write)

    if args.check and row.get("defer_active"):
        if args.json:
            print(json.dumps(row, indent=2))
        return 2

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("email_send_defer_line") or row)
    return 0 if row.get("ok", True) and not (args.check and row.get("defer_active")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
