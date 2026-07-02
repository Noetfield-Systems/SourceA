#!/usr/bin/env python3
"""Machine-verify all 15 founder review recipes — defect list + markers."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "data/client-proof-founder-review-pack-v1.json"

EXTRA_FORBIDDEN = ["kazemnezhadsina144-dot", "/Users/", "sinakazemnezhad", "Desktop/SourceA"]
REPO = "github.com/"
FAKE_GREEN = ["[PASS] policy_version: no policy file", "— skipped", "skipped-check", "fake-green"]
EMDASH = (
    'id="sa-aeg-verdict">—',
    'data-trust-valid-yes>—',
    'data-trust-governance>—',
)


def _load_vbp():
    spec = importlib.util.spec_from_file_location("vbp", ROOT / "scripts/verify_buyer_proof_hotfix_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "founder-review-verify/1.0", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return int(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", errors="replace") if exc.fp else ""


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


def verify_row(row: dict[str, Any], vbp) -> dict[str, Any]:
    rid = row["recipe_id"]
    url = row["live_url"]
    markers = _parse_markers(row.get("proof_marker") or "")
    defects: list[str] = []
    machine_ok = True

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
        code, body = _fetch(url)
        if code != 200:
            machine_ok = False
            defects.append(f"http_code:{code}")
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
        code, body = _fetch(url)
        defects.extend(_scan(body))
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
        code, body = _fetch(url)
        defects.extend(_scan(body))
        if defects:
            machine_ok = False
    elif rid == "cpr-brain-chat":
        code, body = _fetch("https://sourcea.app/api/brain/status/v1")
        if code != 200 or '"ok":true' not in body.replace(" ", ""):
            machine_ok = False
            defects.append(f"brain status http={code}")
        code2, body2 = _fetch(url)
        defects.extend(_scan(body2))
        if defects:
            machine_ok = False
    elif rid == "cpr-railway-observer":
        qurl = "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1"
        code, body = _fetch(qurl)
        if code != 200:
            machine_ok = False
            defects.append(f"http_code:{code}")
        else:
            try:
                d = json.loads(body)
                if not d.get("ok"):
                    machine_ok = False
                    defects.append("queue ok=false")
            except json.JSONDecodeError:
                machine_ok = False
                defects.append("invalid_json")
    else:
        code, body = _fetch(url)
        if code != 200:
            machine_ok = False
            defects.append(f"http_code:{code}")
        for m in markers:
            if m not in body:
                machine_ok = False
                defects.append(f'marker missing: "{m}"')
        defects.extend(_scan(body))

    verdict = "PASS" if machine_ok and not defects else "HOLD"
    return {
        "recipe_id": rid,
        "live_url": url,
        "verdict": verdict,
        "defect": defects[0] if defects else "",
        "defects": defects[:5],
        "fix": "" if verdict == "PASS" else "see defect",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    vbp = _load_vbp()
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    rows = [verify_row(r, vbp) for r in pack["rows"]]
    passed = sum(1 for r in rows if r["verdict"] == "PASS")
    out = {
        "schema": "client-proof-founder-review-verify-v1",
        "at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip(),
        "total": len(rows),
        "passed": passed,
        "ok": passed == len(rows),
        "rows": rows,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"{passed}/{len(rows)} PASS")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
