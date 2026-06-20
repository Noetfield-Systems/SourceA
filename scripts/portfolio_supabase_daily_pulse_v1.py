#!/usr/bin/env python3
"""Portfolio websites + Supabase daily pulse — light stay-up check (≤90s).

Law: data/portfolio-websites-supabase-daily-v1.json
Receipt: ~/.sina/portfolio-supabase-daily-pulse-v1.json
Mac: read-only curl — no validator marathon.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "portfolio-websites-supabase-daily-v1.json"
ACCOUNT_SSOT = ROOT / "data" / "portfolio-account-structure-v1.json"
RECEIPT = SINA / "portfolio-supabase-daily-pulse-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
SECRETS_DIR = Path.home() / ".sourcea-secrets"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _http_probe(url: str, *, timeout: float = 12.0) -> dict:
    t0 = datetime.now(timezone.utc).timestamp()
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "SourceA-daily-pulse/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = int(getattr(resp, "status", 200) or 200)
            resp.read(4096)
        elapsed = datetime.now(timezone.utc).timestamp() - t0
        return {"ok": status < 400, "status": status, "elapsed_sec": round(elapsed, 2)}
    except urllib.error.HTTPError as exc:
        elapsed = datetime.now(timezone.utc).timestamp() - t0
        return {"ok": exc.code < 400, "status": exc.code, "elapsed_sec": round(elapsed, 2), "error": str(exc)[:120]}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        elapsed = datetime.now(timezone.utc).timestamp() - t0
        return {"ok": False, "status": 0, "elapsed_sec": round(elapsed, 2), "error": str(exc)[:120]}


def _probe_website(site: dict) -> dict:
    base = str(site.get("url") or "").rstrip("/")
    paths = site.get("health_paths") or ["/"]
    checks = []
    all_ok = True
    for path in paths:
        path = path if path.startswith("/") else f"/{path}"
        url = f"{base}{path}"
        row = _http_probe(url)
        row["url"] = url
        checks.append(row)
        if site.get("required", True) and not row.get("ok"):
            all_ok = False
    return {
        "id": site.get("id"),
        "label": site.get("label"),
        "module": site.get("module"),
        "supabase_tier": site.get("supabase_tier"),
        "ok": all_ok if site.get("required", True) else any(c.get("ok") for c in checks),
        "required": bool(site.get("required", True)),
        "checks": checks,
    }


def _probe_supabase(project: dict) -> dict:
    secrets_name = str(project.get("secrets_file") or "")
    env_path = SECRETS_DIR / secrets_name
    env = _load_env_file(env_path)
    url_key = str(project.get("env_url") or "SUPABASE_URL")
    anon_key = str(project.get("env_anon") or "SUPABASE_ANON_KEY")
    base = (env.get(url_key) or "").rstrip("/")
    if not base or "YOUR_" in base:
        return {
            "id": project.get("id"),
            "ok": True,
            "required": bool(project.get("required", True)),
            "skipped": True,
            "secrets_missing": True,
            "reason": f"missing or placeholder secrets: {env_path}",
        }
    health_url = f"{base}/auth/v1/health"
    row = _http_probe(health_url, timeout=15.0)
    rest_ok = None
    anon = env.get(anon_key) or ""
    if anon and not anon.startswith("YOUR_"):
        rest_url = f"{base}/rest/v1/"
        rest = _http_probe(rest_url, timeout=12.0)
        rest_ok = rest.get("ok")
    ok = bool(row.get("ok"))
    if project.get("required", True) and rest_ok is False:
        ok = False
    return {
        "id": project.get("id"),
        "tier": project.get("tier"),
        "modules": project.get("modules"),
        "ok": ok,
        "required": bool(project.get("required", True)),
        "health_url": health_url,
        "health": row,
        "rest_ok": rest_ok,
        "secrets_loaded_from": str(env_path),
    }


def _compose_line(*, websites: list[dict], supabase: list[dict]) -> str:
    web_red = [w["id"] for w in websites if w.get("required") and not w.get("ok")]
    sb_red = [s["id"] for s in supabase if s.get("required") and not s.get("ok") and not s.get("skipped")]
    sb_skip = [s["id"] for s in supabase if s.get("skipped")]
    web_n = sum(1 for w in websites if w.get("required") and w.get("ok"))
    web_t = sum(1 for w in websites if w.get("required"))
    sb_n = sum(1 for s in supabase if s.get("required") and s.get("ok") and not s.get("skipped"))
    sb_t = sum(1 for s in supabase if s.get("required"))
    if not web_red and not sb_red:
        skip = f" · sb-secrets-missing:{','.join(sb_skip)}" if sb_skip else ""
        return f"portfolio-daily · UP · sites {web_n}/{web_t} · supabase {sb_n}/{sb_t}{skip}"
    parts = []
    if web_red:
        parts.append("sites:" + ",".join(web_red[:3]))
    if sb_red:
        parts.append("sb:" + ",".join(sb_red))
    if sb_skip:
        parts.append("sb-secrets:" + ",".join(sb_skip))
    return f"portfolio-daily · RED · {' · '.join(parts)}"


def _account_structure_block() -> dict:
    """Always attach portfolio Gmail/account map to daily reports."""
    try:
        import portfolio_account_structure_v1 as pas

        return pas.build_report()
    except Exception as exc:  # noqa: BLE001 — report must not break site pulse
        return {
            "ok": False,
            "portfolio_account_structure_line": f"accounts · WARN · sync-failed:{type(exc).__name__}",
            "error": str(exc)[:160],
        }


def run_pulse(*, wire: bool = False) -> dict:
    ssot = _read(SSOT)
    websites = [_probe_website(s) for s in ssot.get("websites") or []]
    supabase = [_probe_supabase(p) for p in ssot.get("supabase_projects") or []]
    account = _account_structure_block()
    line = _compose_line(websites=websites, supabase=supabase)
    req_web_ok = all(w.get("ok") for w in websites if w.get("required"))
    req_sb_ok = all(s.get("ok") for s in supabase if s.get("required"))
    secrets_missing = any(s.get("secrets_missing") for s in supabase)
    overall = req_web_ok and req_sb_ok
    row = {
        "schema": "portfolio-supabase-daily-pulse-v1",
        "at": _now(),
        "ok": overall,
        "portfolio_supabase_daily_line": line,
        "websites": websites,
        "supabase": supabase,
        "ssot": str(SSOT.relative_to(ROOT)),
        "next_if_red": "Lane agent fixes that module — DNS/Vercel deploy or Supabase unpause",
        "secrets_missing": secrets_missing,
        "secrets_hint": "~/.sourcea-secrets/portfolio-spine.env and labs-sandbox.env" if secrets_missing else None,
        "account_structure": account,
        "account_structure_ssot": str(ACCOUNT_SSOT.relative_to(ROOT)),
        "portfolio_account_structure_line": account.get("portfolio_account_structure_line"),
    }
    if wire:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        surfaces = _read(SURFACES)
        surfaces["portfolio_supabase_daily_line"] = line
        surfaces["portfolio_supabase_daily"] = {
            "ok": overall,
            "at": row["at"],
            "receipt": str(RECEIPT),
        }
        acct_line = str(account.get("portfolio_account_structure_line") or "")
        if acct_line:
            surfaces["portfolio_account_structure_line"] = acct_line
            surfaces["portfolio_account_structure"] = {
                "ok": bool(account.get("ok")),
                "at": row["at"],
                "receipt": str(SINA / "portfolio-account-structure-v1.json"),
                "ssot": str(ACCOUNT_SSOT),
            }
            try:
                import portfolio_account_structure_v1 as pas

                pas.wire()
            except Exception:
                pass
        SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--wire", action="store_true", help="Write receipt + surfaces line")
    args = ap.parse_args()
    row = run_pulse(wire=args.wire)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("portfolio_supabase_daily_line") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
