#!/usr/bin/env python3
"""Chat Unify — lightweight live HTTP verify (one URL per call, short timeout).

Mac may call outbound HEAD/GET for ORD truth binding — not a validator storm.
Receipt cache: ~/.sina/chat-unify-live-http-cache-v1.json
"""
from __future__ import annotations

import json
import re
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VERIFY_VERSION = "1.0.0"
CACHE_PATH = Path.home() / ".sina" / "chat-unify-live-http-cache-v1.json"
DEFAULT_TIMEOUT = 8
_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
_PATH_RE = re.compile(r"(/[\w./_-]+(?:\.md|\.json)?)", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_cache() -> dict:
    if CACHE_PATH.is_file():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"entries": {}}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2) + "\n", encoding="utf-8")


def normalize_url(raw: str, *, base: str = "https://www.noetfield.com") -> str | None:
    t = (raw or "").strip()
    if _URL_RE.match(t):
        return t.split()[0].rstrip(".,;:")
    m = _PATH_RE.search(t)
    if m:
        path = m.group(1)
        return f"{base.rstrip('/')}{path}"
    return None


def verify_url(url: str, *, timeout: int = DEFAULT_TIMEOUT, use_cache: bool = True) -> dict:
    """HEAD then GET fallback — returns status code."""
    cache = _load_cache()
    key = url.strip()
    if use_cache and key in (cache.get("entries") or {}):
        row = dict(cache["entries"][key])
        row["cached"] = True
        return row

    status: int | None = None
    err: str | None = None
    method = "HEAD"
    ctx = ssl.create_default_context()
    for meth in ("HEAD", "GET"):
        try:
            req = Request(key, method=meth, headers={"User-Agent": "SourceA-ChatUnify-ORD/1.0"})
            with urlopen(req, timeout=timeout, context=ctx) as resp:
                status = int(resp.status)
                method = meth
                break
        except HTTPError as e:
            status = int(e.code)
            method = meth
            break
        except URLError as e:
            err = str(e.reason)[:200]
        except Exception as e:
            err = str(e)[:200]

    row = {
        "schema": "chat-unify-live-http-verify-v1",
        "version": VERIFY_VERSION,
        "url": key,
        "status": status,
        "ok": status is not None,
        "method": method,
        "error": err,
        "at": _now(),
        "cached": False,
    }
    cache.setdefault("entries", {})[key] = {k: v for k, v in row.items() if k != "cached"}
    _save_cache(cache)
    return row


def verify_atoms_live_http(
    atoms: list[dict],
    *,
    base_url: str = "https://www.noetfield.com",
    max_requests: int = 3,
) -> dict[str, dict]:
    """Verify up to max_requests LIVE_HTTP atoms — returns url -> result."""
    out: dict[str, dict] = {}
    live = [a for a in atoms if a.get("claim_type") == "LIVE_HTTP"]
    for a in live[:max_requests]:
        url = normalize_url(a.get("text") or "", base=base_url)
        if not url or url in out:
            continue
        out[url] = verify_url(url)
    return out


def apply_live_http_results(atoms: list[dict], results: dict[str, dict], *, base_url: str = "https://www.noetfield.com") -> list[dict]:
    """Update LIVE_HTTP atoms with curl results when claims mention status codes."""
    out: list[dict] = []
    for a in atoms:
        row = dict(a)
        if row.get("claim_type") != "LIVE_HTTP":
            out.append(row)
            continue
        text = row.get("text") or ""
        url = normalize_url(text, base=base_url)
        if not url or url not in results:
            out.append(row)
            continue
        res = results[url]
        status = res.get("status")
        if status is None:
            row["verify_reason"] = f"live HTTP failed — {res.get('error') or 'no response'}"
            out.append(row)
            continue
        tl = text.lower()
        claims_200 = bool(re.search(r"\b200\b", tl))
        claims_404 = bool(re.search(r"\b404\b", tl))
        claims_blocked = bool(re.search(r"\b(block|404|fixed)\b", tl))
        if claims_200 and status == 200:
            row["disk_status"] = "verified"
            row["disk_ref"] = url
            row["verify_reason"] = f"live HTTP {status} matches claim"
        elif claims_404 and status == 404:
            row["disk_status"] = "verified"
            row["disk_ref"] = url
            row["verify_reason"] = f"live HTTP {status} matches claim"
        elif claims_200 and status != 200:
            row["disk_status"] = "mismatch"
            row["disk_ref"] = url
            row["verify_reason"] = f"agent claims 200 — live returned {status}"
        elif claims_blocked and status == 404:
            row["disk_status"] = "verified"
            row["disk_ref"] = url
            row["verify_reason"] = f"path blocked live ({status})"
        else:
            row["disk_status"] = "unverified"
            row["disk_ref"] = url
            row["verify_reason"] = f"live HTTP {status} — claim wording unclear"
        out.append(row)
    return out


if __name__ == "__main__":
    import sys

    u = sys.argv[1] if len(sys.argv) > 1 else "https://www.noetfield.com/"
    print(json.dumps(verify_url(u), indent=2))
