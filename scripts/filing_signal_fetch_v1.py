#!/usr/bin/env python3
"""Minimal filing signal fetch — routes Canadian FPI to 40-F not 10-K Item 1A.

SSOT routes: data/canadian-issuer-filing-routes-v1.json
No Proxycurl · no LinkedIn scrape.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "data" / "canadian-issuer-filing-routes-v1.json"
SEC_UA = "Noetfield Systems research-bot contact@noetfield.com"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_issuer(ticker: str, routes: dict) -> dict | None:
    t = ticker.upper().strip()
    for row in routes.get("issuers") or []:
        if str(row.get("ticker") or "").upper() == t:
            return row
    return None


def _sec_submissions(cik: str) -> dict:
    cik10 = str(cik).lstrip("0").zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    req = urllib.request.Request(url, headers={"User-Agent": SEC_UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def fetch(*, ticker: str, issuer_country: str = "CA") -> dict:
    routes_doc = _read(ROUTES)
    issuer = _find_issuer(ticker, routes_doc)
    if not issuer:
        return {
            "ok": False,
            "ticker": ticker.upper(),
            "error": "issuer not in filing routes SSOT",
            "filing_type": None,
        }

    sec_route = str(issuer.get("sec_route") or "")
    forbidden = str(issuer.get("forbidden_route") or "")
    if forbidden == "sec_10k":
        filing_type = sec_route or "sedar_aif"
    else:
        filing_type = str(issuer.get("primary_route") or "manual_only")

    if filing_type == "sec_10k":
        return {
            "ok": False,
            "ticker": ticker.upper(),
            "filing_type": "sec_10k",
            "error": "10-K-only path forbidden for this issuer",
            "issuer": issuer.get("company_name"),
        }

    result: dict = {
        "ok": True,
        "ticker": ticker.upper(),
        "issuer_country": issuer_country or issuer.get("issuer_country"),
        "issuer": issuer.get("company_name"),
        "filing_type": "40-F" if filing_type == "sec_40f" else filing_type,
        "route": filing_type,
        "risk_excerpt": "",
        "source_url": "",
        "at": _now(),
        "note": issuer.get("note"),
    }

    cik = issuer.get("cik")
    if filing_type == "sec_40f" and cik:
        try:
            sub = _sec_submissions(str(cik))
            recent = sub.get("filings", {}).get("recent") or {}
            forms = recent.get("form") or []
            idx = next((i for i, f in enumerate(forms) if str(f).upper().startswith("40-F")), None)
            if idx is not None:
                accession = (recent.get("accessionNumber") or [""])[idx]
                primary = (recent.get("primaryDocument") or [""])[idx]
                cik_num = str(sub.get("cik") or cik).lstrip("0")
                result["source_url"] = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik_num}/"
                    f"{accession.replace('-', '')}/{primary}"
                )
                result["risk_excerpt"] = (
                    f"Latest SEC filing form {forms[idx]} — use AIF/MD&A narrative; not 10-K Item 1A."
                )
            else:
                result["ok"] = True
                result["manual_sedar_required"] = True
                result["risk_excerpt"] = "No 40-F in recent submissions — prefer SEDAR+ AIF"
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as exc:
            result["ok"] = True
            result["fetch_warning"] = str(exc)
            result["manual_sedar_required"] = True

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Filing signal fetch — 40-F branch for Canadian FPI")
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--issuer-country", default="CA")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = fetch(ticker=args.ticker, issuer_country=args.issuer_country)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("filing_type"), row.get("ok"), row.get("source_url") or row.get("error"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
