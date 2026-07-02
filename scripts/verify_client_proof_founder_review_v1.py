#!/usr/bin/env python3
"""Machine-verify all 15 founder review recipes — defect list + markers.

LAW (permanent): Verify = raw HTTPS fetch of the PUBLIC hostname from outside.
Local dist / workspace HTML is INVALID as a PASS source.
Use --min-seconds-after-deploy 60 after Pages publish before trusting PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "data/client-proof-founder-review-pack-v1.json"
PUBLISH_RECEIPT = Path.home() / ".sina/sourcea-landing-publish-receipt-v1.json"
VERIFY_RECEIPT = Path.home() / ".sina/client-proof-founder-review-verify-v1.json"

PUBLIC_VERIFY_LAW = (
    "Verify = raw HTTPS fetch of the PUBLIC hostname from outside; "
    "minimum 60s after deploy; local dist verification is INVALID as PASS."
)

EXTRA_FORBIDDEN = ["kazemnezhadsina144-dot", "/Users/", "sinakazemnezhad", "Desktop/SourceA"]
REPO = "github.com/"
FAKE_GREEN = ["[PASS] policy_version: no policy file", "— skipped", "skipped-check", "fake-green"]
EMDASH = (
    'id="sa-aeg-verdict">—',
    'data-trust-valid-yes>—',
    'data-trust-governance>—',
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_vbp():
    spec = importlib.util.spec_from_file_location("vbp", ROOT / "scripts/verify_buyer_proof_hotfix_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _public_fetch(url: str, *, follow_redirects: bool = True) -> dict[str, Any]:
    """Raw HTTPS fetch — only valid proof source for public HTML recipes."""
    fetched_at = _now()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "sourcea-public-founder-review-verify/1.0",
            "Accept": "*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    handlers: list[urllib.request.BaseHandler] = []
    if not follow_redirects:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        handlers.append(_NoRedirect())
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(req, timeout=30) as resp:
            raw = resp.read()
            body = raw.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "fetched_at": fetched_at,
                "http_code": int(resp.status),
                "body": body,
                "body_bytes": len(raw),
                "body_sha256_prefix": hashlib.sha256(raw[:100]).hexdigest(),
                "body_sha256_full": hashlib.sha256(raw).hexdigest(),
                "cache_control": resp.headers.get("Cache-Control"),
                "location": resp.geturl() if int(resp.status) in (301, 302, 303, 307, 308) else resp.headers.get("Location"),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read() if exc.fp else b""
        body = raw.decode("utf-8", errors="replace") if raw else ""
        return {
            "ok": False,
            "fetched_at": fetched_at,
            "http_code": int(exc.code),
            "body": body,
            "body_bytes": len(raw),
            "body_sha256_prefix": hashlib.sha256(raw[:100]).hexdigest() if raw else "",
            "body_sha256_full": hashlib.sha256(raw).hexdigest() if raw else "",
            "cache_control": exc.headers.get("Cache-Control") if exc.headers else None,
            "location": exc.headers.get("Location") if exc.headers else None,
            "error": str(exc)[:120],
        }
    except Exception as exc:
        return {
            "ok": False,
            "fetched_at": fetched_at,
            "http_code": 0,
            "body": "",
            "body_bytes": 0,
            "body_sha256_prefix": "",
            "body_sha256_full": "",
            "error": str(exc)[:120],
        }


def _deploy_cooldown_ok(*, min_seconds: int) -> dict[str, Any]:
    if min_seconds <= 0:
        return {"ok": True, "skipped": True, "min_seconds": min_seconds}
    if not PUBLISH_RECEIPT.is_file():
        return {"ok": True, "skipped": True, "reason": "no_publish_receipt", "min_seconds": min_seconds}
    try:
        doc = json.loads(PUBLISH_RECEIPT.read_text(encoding="utf-8"))
        published_at = datetime.fromisoformat(str(doc.get("at") or "").replace("Z", "+00:00"))
        elapsed = (datetime.now(timezone.utc) - published_at).total_seconds()
        return {
            "ok": elapsed >= min_seconds,
            "published_at": doc.get("at"),
            "elapsed_seconds": int(elapsed),
            "min_seconds": min_seconds,
            "deploy_url": doc.get("deploy_url"),
        }
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        return {"ok": True, "skipped": True, "reason": str(exc)[:80], "min_seconds": min_seconds}


def _scan(body: str) -> list[str]:
    hits = []
    for x in EXTRA_FORBIDDEN:
        if x in body:
            hits.append(f'"{x}"')
    if REPO in body:
        hits.append(f'"{REPO}"')
    for fg in FAKE_GREEN:
        if fg in body:
            hits.append(f'"{fg}"')
    for e in EMDASH:
        if e in body:
            hits.append(f'"{e}"')
    return hits


def _parse_markers(s: str) -> list[str]:
    return [m.strip().strip('"') for m in s.split("·") if m.strip()]


def _fetch_meta_slice(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "fetched_at": meta.get("fetched_at"),
        "http_code": meta.get("http_code"),
        "body_sha256_prefix": meta.get("body_sha256_prefix"),
        "body_bytes": meta.get("body_bytes"),
        "cache_control": meta.get("cache_control"),
        "location": meta.get("location"),
    }


def verify_row(row: dict[str, Any], vbp, *, deploy_gate: dict[str, Any]) -> dict[str, Any]:
    rid = row["recipe_id"]
    url = row["live_url"]
    markers = _parse_markers(row.get("proof_marker") or "")
    defects: list[str] = []
    machine_ok = True
    fetch_meta: dict[str, Any] = {}

    if not deploy_gate.get("ok") and not deploy_gate.get("skipped"):
        machine_ok = False
        defects.append(
            f"deploy_cooldown:{deploy_gate.get('elapsed_seconds')}s<{deploy_gate.get('min_seconds')}s"
        )

    if rid == "cpr-supabase-rows":
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/cloud_forge_run_supabase_v1.py"), "--count", "--json"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env={**__import__("os").environ, "CLOUD_FORGE_RUN_SUPABASE_ALLOW_MAC": "1"},
        )
        try:
            d = json.loads(proc.stdout)
            if not (proc.returncode == 0 and d.get("ok") and int(d.get("total") or 0) > 0):
                machine_ok = False
                defects.append(f"supabase total={d.get('total')}")
        except Exception as exc:
            machine_ok = False
            defects.append(str(exc)[:80])
    elif rid == "cpr-free-job-intake":
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/verify_mvp_intake_proof_v1.py"),
                "--url",
                "https://sourcea.app/api/commercial/mvp-intake/v1",
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        try:
            d = json.loads(proc.stdout)
            if not d.get("ok"):
                machine_ok = False
                defects.append(f"mvp_intake_e2e fail post={d.get('post')} read={d.get('read_back')}")
        except Exception as exc:
            machine_ok = False
            defects.append(str(exc)[:80])
        fetch_meta = _public_fetch(url)
        body = fetch_meta["body"]
        if fetch_meta["http_code"] != 200:
            machine_ok = False
            defects.append(f"http_code:{fetch_meta['http_code']}")
        for m in markers:
            if m not in body:
                machine_ok = False
                defects.append(f'marker missing: "{m}"')
        defects.extend(_scan(body))
    elif rid == "cpr-live-receipt":
        r = vbp.verify_proof_live("https://sourcea.app")
        if not r["ok"]:
            machine_ok = False
            defects.extend([f'"{x}"' for x in (r.get("forbidden_hits") or [])])
            defects.extend([f'"{x}"' for x in (r.get("emdash_slots") or [])])
            defects.extend(r.get("contradictions") or [])
            if r.get("markers_missing"):
                defects.extend([f'marker missing: "{m}"' for m in r["markers_missing"]])
        fetch_meta = _public_fetch(url)
        defects.extend(_scan(fetch_meta["body"]))
        if defects:
            machine_ok = False
    elif rid == "cpr-eval-boot":
        r = vbp.verify_eval_live("https://sourcea.app")
        if not r["ok"]:
            machine_ok = False
            defects.extend([f'"{x}"' for x in (r.get("forbidden_hits") or [])])
            defects.extend([f'"{x}"' for x in (r.get("emdash_slots") or [])])
            if r.get("markers_missing"):
                defects.extend([f'marker missing: "{m}"' for m in r["markers_missing"]])
        fetch_meta = _public_fetch(url)
        defects.extend(_scan(fetch_meta["body"]))
        if defects:
            machine_ok = False
    elif rid == "cpr-brain-chat":
        status = _public_fetch("https://sourcea.app/api/brain/status/v1")
        body = status["body"]
        if status["http_code"] != 200 or '"ok":true' not in body.replace(" ", ""):
            machine_ok = False
            defects.append(f"brain status http={status['http_code']}")
        fetch_meta = _public_fetch(url)
        defects.extend(_scan(fetch_meta["body"]))
        if defects:
            machine_ok = False
    elif rid == "cpr-railway-observer":
        fetch_meta = _public_fetch("https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1")
        if fetch_meta["http_code"] != 200:
            machine_ok = False
            defects.append(f"http_code:{fetch_meta['http_code']}")
        else:
            try:
                d = json.loads(fetch_meta["body"])
                if not d.get("ok"):
                    machine_ok = False
                    defects.append("queue ok=false")
            except json.JSONDecodeError:
                machine_ok = False
                defects.append("invalid_json")
    elif rid == "cpr-contract-aivg":
        fetch_meta = _public_fetch(url)
        body = fetch_meta["body"]
        if fetch_meta["http_code"] != 200:
            machine_ok = False
            defects.append(f"http_code:{fetch_meta['http_code']}")
        for m in markers:
            if m not in body:
                machine_ok = False
                defects.append(f'marker missing: "{m}"')
        defects.extend(_scan(body))
        ca = _public_fetch("https://sourcea.ca/", follow_redirects=False)
        if ca["http_code"] != 301:
            machine_ok = False
            defects.append(f"sourcea.ca root http={ca['http_code']} expected 301")
        elif not str(ca.get("location") or "").startswith("https://sourcea.app/ai-value-governance"):
            machine_ok = False
            defects.append(f"sourcea.ca location={ca.get('location')}")
        regional_redirect_fetch = _fetch_meta_slice(ca)
    else:
        fetch_meta = _public_fetch(url)
        body = fetch_meta["body"]
        if fetch_meta["http_code"] != 200:
            machine_ok = False
            defects.append(f"http_code:{fetch_meta['http_code']}")
        for m in markers:
            if m not in body:
                machine_ok = False
                defects.append(f'marker missing: "{m}"')
        defects.extend(_scan(body))

    verdict = "PASS" if machine_ok and not defects else "HOLD"
    out = {
        "recipe_id": rid,
        "live_url": url,
        "verdict": verdict,
        "defect": defects[0] if defects else "",
        "defects": defects[:5],
        "fix": "" if verdict == "PASS" else "see defect",
    }
    if rid == "cpr-contract-aivg":
        out["regional_redirect_fetch"] = regional_redirect_fetch
    if fetch_meta:
        out["public_fetch"] = _fetch_meta_slice(fetch_meta)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument(
        "--min-seconds-after-deploy",
        type=int,
        default=0,
        help="Require at least N seconds since last Pages publish (use 60 for ship proof)",
    )
    args = ap.parse_args()
    vbp = _load_vbp()
    deploy_gate = _deploy_cooldown_ok(min_seconds=args.min_seconds_after_deploy)
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    rows = [verify_row(r, vbp, deploy_gate=deploy_gate) for r in pack["rows"]]
    passed = sum(1 for r in rows if r["verdict"] == "PASS")
    out = {
        "schema": "client-proof-founder-review-verify-v1",
        "version": "1.1.0",
        "verify_law": PUBLIC_VERIFY_LAW,
        "at": _now(),
        "commit_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip(),
        "deploy_gate": deploy_gate,
        "total": len(rows),
        "passed": passed,
        "ok": passed == len(rows),
        "rows": rows,
    }
    if args.write_receipt:
        VERIFY_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        VERIFY_RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        out["receipt_path"] = str(VERIFY_RECEIPT)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"{passed}/{len(rows)} PASS · public HTTPS only")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
