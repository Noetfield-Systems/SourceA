#!/usr/bin/env python3
"""Cloud factories online only — Mac is control panel, never factory body.

Law: data/cloud-factories-online-only-v1.json
Receipt: ~/.sina/cloud-factories-online-only-receipt-v1.json
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
SSOT = ROOT / "data" / "cloud-factories-online-only-v1.json"
RECEIPT = SINA / "cloud-factories-online-only-receipt-v1.json"
FEM = ROOT / "data" / "founder-execution-model-v1.json"
MACHINE_REG = ROOT / "data" / "machine-execution-plane-registry-v1.json"
FBE_CFG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
SECRETS = SINA / "secrets.env"

LOCAL_PREFIXES = ("http://127.", "http://localhost", "http://0.0.0.0")


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


def _is_local_url(url: str) -> bool:
    u = str(url or "").lower()
    return any(u.startswith(p) for p in LOCAL_PREFIXES)


def _fbe_health_ok(url: str) -> bool:
    if not url:
        return False
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=8) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        return bool(row.get("ok")) and str(row.get("service", "")).startswith("fbe")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return False


def _fbe_public_url() -> tuple[str, str]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from fbe.lib.public_worker_url_v1 import resolve_public_fbe_url  # noqa: WPS433

    return resolve_public_fbe_url(require_health=True)


def assess(*, write: bool = True) -> dict:
    ssot = _read(SSOT)
    fem = _read(FEM)
    reg = _read(MACHINE_REG)
    issues: list[str] = []
    checks: dict[str, bool] = {}

    mac = (fem.get("mac_role") or {}).get("canonical")
    cloud = (fem.get("cloud_role") or {}).get("canonical")
    checks["mac_control_plane_only"] = mac == "control_plane_only"
    checks["cloud_execution_plane"] = cloud == "execution_plane_headless"
    if not checks["mac_control_plane_only"]:
        issues.append(f"mac_role={mac}")
    if not checks["cloud_execution_plane"]:
        issues.append(f"cloud_role={cloud}")

    cloud_rows = reg.get("cloud_factories") or []
    mac_in_cloud = [
        str(r.get("id"))
        for r in cloud_rows
        if str(r.get("execution_plane") or "").startswith("mac")
    ]
    checks["no_mac_in_cloud_factories"] = not mac_in_cloud
    if mac_in_cloud:
        issues.append(f"mac_in_cloud_factories:{','.join(mac_in_cloud)}")

    control = reg.get("control_plane_only") or []
    checks["control_plane_registered"] = len(control) >= 3
    if not checks["control_plane_registered"]:
        issues.append("control_plane_registry_thin")

    fbe_url, fbe_src = _fbe_public_url()
    checks["fbe_public_https"] = bool(fbe_url)
    if not fbe_url:
        raw = _secret("FBE_CLOUD_WORKER_URL") or str(_read(FBE_CFG).get("worker_url") or "")
        if _is_local_url(raw):
            issues.append("fbe_still_local_not_cloud")
        else:
            issues.append("fbe_no_public_https")

    wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    checks["local_worker_deprecated"] = bool(wo.get("local_worker_deprecated")) or wo.get("execution_mode") != "local_worker"
    if not checks["local_worker_deprecated"]:
        issues.append("local_worker_still_factory_path")

    grad = _read(SINA / "brain-cloud-graduate-receipt-v1.json")
    checks["cloud_graduate_receipt"] = bool(grad.get("ok"))
    if not checks["cloud_graduate_receipt"]:
        issues.append("cloud_graduate_receipt_missing")

    fed = _read(SINA / "fbe-federated-receipt-v1.json")
    fed_cloud = (
        fed.get("remote_status") == "cloud_api_worker"
        or (fed.get("mode") == "federated_headless" and bool(fed.get("ok")))
        or "cloud_api_worker" in json.dumps(fed)
    )
    checks["federated_cloud_api"] = fed_cloud
    if not fed_cloud:
        issues.append(f"federated_not_cloud:{fed.get('remote_status') or fed.get('mode')}")

    defer = {}
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from commercial_email_send_defer_v1 import assess as defer_assess  # noqa: WPS433

        defer = defer_assess(write=False)
        mac_only_probes = []
        for row in defer.get("main_cloud_factories") or []:
            kind = str(row.get("kind") or "")
            if kind in ("script", "file") and row.get("required"):
                mac_only_probes.append(str(row.get("id")))
        checks["defer_no_mac_disk_required_probes"] = not mac_only_probes
        if mac_only_probes:
            issues.append(f"defer_mac_disk_probes:{','.join(mac_only_probes)}")
    except Exception as exc:
        checks["defer_no_mac_disk_required_probes"] = False
        issues.append(f"defer_assess_error:{exc}")

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    ok = passed == total and not issues
    line = (
        f"cloud-factories · {'PASS' if ok else 'RED'} · {passed}/{total} · "
        f"Mac=control-panel · factories=cloud+API · "
        f"anti-staleness+zero-drift+zero-fragmentation"
    )

    row = {
        "schema": "cloud-factories-online-only-receipt-v1",
        "at": _now(),
        "ok": ok,
        "one_law": ssot.get("one_law"),
        "cloud_factories_online_line": line,
        "passed": passed,
        "total": total,
        "checks": checks,
        "issues": issues,
        "fbe_public_url": fbe_url or None,
        "fbe_url_source": fbe_src,
        "main_cloud_factory_count": len(cloud_rows),
        "defer_main_online": defer.get("main_factories_online"),
        "ssot": str(SSOT.relative_to(ROOT)),
    }

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        surf = _read(SINA / "agent-live-surfaces-v1.json")
        if surf:
            surf["cloud_factories_online_line"] = line
            surf["cloud_factories_online_only"] = {
                "ok": ok,
                "issues": issues[:6],
                "ssot": "data/cloud-factories-online-only-v1.json",
            }
            (SINA / "agent-live-surfaces-v1.json").write_text(json.dumps(surf, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloud factories online only — anti Mac-factory theater")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = assess(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("cloud_factories_online_line") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
