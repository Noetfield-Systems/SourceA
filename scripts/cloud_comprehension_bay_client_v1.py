#!/usr/bin/env python3
"""Cloud comprehension client — POST draft straight to Railway FBE (CLOUD_ONLY).

Mac never runs comprehension validators. Optional Hub URL is legacy fallback only.

Receipt: ~/.sina/cloud-comprehension-bay-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "cloud-comprehension-bay-receipt-v1.json"
HUB_FALLBACK = "http://127.0.0.1:13020"
CLOUD_PATH = "/api/fbe/comprehension-loop/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def light_system_snapshot() -> dict:
    """Hub-side only — tiny read for cloud analyst context. No validator chain."""
    surf = _read(SINA / "agent-live-surfaces-v1.json")
    return {
        "factory_now_line": str(surf.get("factory_now_line") or "")[:200],
        "queue_sa": str(surf.get("queue_sa") or ""),
        "portfolio_line": str(surf.get("portfolio_line") or "")[:200],
        "form_open": int((surf.get("form_official") or {}).get("open_questions_count") or 0)
        if isinstance(surf.get("form_official"), dict)
        else 0,
    }


def _cloud_proxy(
    draft: str,
    founder_message: str,
    *,
    variation_key: str | None = None,
) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

    body = {
        "job_id": str(uuid.uuid4()),
        "factory_id": "comprehension-loop-factory-v1",
        "bay_slug": "comprehension-loop-bay",
        "tenant": "sourcea",
        "execution_mode": "CLOUD_ONLY",
        "draft": draft,
        "founder_message": founder_message,
        "system_snapshot": light_system_snapshot(),
    }
    if variation_key:
        body["variation_key"] = variation_key
    return proxy_to_cloud(path=CLOUD_PATH, body=body, timeout_s=120)


def _hub_fallback(draft: str, founder_message: str, hub_url: str) -> dict:
    import urllib.error
    import urllib.request

    body = {
        "job_id": str(uuid.uuid4()),
        "factory_id": "comprehension-loop-factory-v1",
        "bay_slug": "comprehension-loop-bay",
        "tenant": "sourcea",
        "execution_mode": "CLOUD_ONLY",
        "draft": draft,
        "founder_message": founder_message,
        "system_snapshot": light_system_snapshot(),
    }
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{hub_url.rstrip('/')}/api/comprehension-loop/v1",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            return json.loads(exc.read().decode("utf-8"))
        except Exception:
            return {"ok": False, "error": str(exc)}
    except Exception as exc:
        return {
            "ok": False,
            "error": "hub_unreachable",
            "message": str(exc),
            "for_founder": {"blocked": True, "why": "Cloud comprehension bay unreachable."},
        }


def _local_bay(
    draft: str,
    founder_message: str,
    *,
    variation_key: str | None = None,
    fallback_reason: str = "cloud_unavailable",
) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from fbe_comprehension_bay_v1 import run_comprehension_bay  # noqa: WPS433

    row = run_comprehension_bay(
        draft=draft,
        founder_message=founder_message,
        variation_key=variation_key,
    )
    row["execution_plane"] = "mac_local_fallback"
    row["fallback_reason"] = fallback_reason
    row["proxied"] = False
    return row


def analyze_via_cloud(
    *,
    draft: str,
    founder_message: str = "",
    hub_url: str = HUB_FALLBACK,
    variation_key: str | None = None,
    write_receipt: bool = True,
) -> dict:
    row = _cloud_proxy(draft, founder_message, variation_key=variation_key)
    cloud_errors = (
        "cloud_worker_unreachable",
        "cloud_proxy_fatal",
        "cloud_proxy_http_error",
    )
    if row.get("verdict"):
        pass  # valid bay receipt from cloud (ACCEPT or BLOCKED)
    elif not row.get("ok") and row.get("error") in cloud_errors:
        hub_row = _hub_fallback(draft, founder_message, hub_url)
        if hub_row.get("ok"):
            row = hub_row
        else:
            row = _local_bay(
                draft,
                founder_message,
                variation_key=variation_key,
                fallback_reason=str(hub_row.get("error") or row.get("error") or "cloud_unavailable"),
            )

    out = {
        "schema": "cloud-comprehension-bay-client-receipt-v1",
        "at": _now(),
        "ok": bool(row.get("ok")),
        "proxied": bool(row.get("proxied", row.get("execution_plane") != "mac_local_fallback")),
        "execution_plane": row.get("execution_plane") or "headless_cloud",
        "verdict": row.get("verdict"),
        "config_version": row.get("config_version"),
        "variation_key": row.get("variation_key"),
        "meaning_score": row.get("meaning_score"),
        "escalated": bool(row.get("escalated")),
        "attempts": row.get("attempts") or [],
        "for_founder": row.get("for_founder") or {},
        "for_agent": row.get("for_agent") or {},
        "one_line": row.get("one_line") or "",
        "raw": row,
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Cloud comprehension bay client v1")
    ap.add_argument("--text", default="")
    ap.add_argument("--founder-message", default="")
    ap.add_argument("--file")
    ap.add_argument("--hub", default=HUB_FALLBACK)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8", errors="replace")
    row = analyze_via_cloud(
        draft=body,
        founder_message=args.founder_message,
        hub_url=args.hub,
    )
    if args.json:
        slim = {k: v for k, v in row.items() if k != "raw"}
        print(json.dumps(slim, indent=2, ensure_ascii=False))
    else:
        ff = row.get("for_founder") or {}
        print(row.get("one_line") or "")
        if ff.get("show_this"):
            print(ff["show_this"])
        elif ff.get("why"):
            print("Blocked:", ff["why"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
