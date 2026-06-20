#!/usr/bin/env python3
"""n8n intelligence layer — stack snapshots, product signals, hub + workflow wiring."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _source_a_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return Path(__file__).resolve().parents[1]


SOURCE_A = _source_a_root()
INTEL_DIR = Path.home() / ".sina" / "n8n-intelligence"
LATEST_PATH = INTEL_DIR / "latest.json"
BRIEF_PATH = INTEL_DIR / "brief-latest.md"
HISTORY_DIR = INTEL_DIR / "snapshots"
HUB_INTEL_URL = "http://127.0.0.1:13020/api/n8n/intelligence"
RUNTIME_ASK = "http://127.0.0.1:8000/api/v1/liaison/ask"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _probe_json(url: str, *, method: str = "GET", body: dict | None = None, timeout: float = 8.0) -> dict:
    try:
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(65536).decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                parsed = {"raw": raw[:2000]}
            return {"ok": resp.status in (200, 201, 204), "status": resp.status, "data": parsed}
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read(4096).decode("utf-8", errors="replace")
            parsed = json.loads(err_body) if err_body.strip().startswith("{") else {"raw": err_body[:500]}
        except Exception:
            parsed = {}
        return {"ok": False, "status": e.code, "data": parsed, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e), "data": {}}


def _layer_a_summary() -> dict:
    try:
        from sina_command_lib import personal_db_detail  # noqa: WPS433

        return personal_db_detail()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _intelligence_circle_summary() -> dict:
    try:
        from intelligence_circle import circle_payload  # noqa: WPS433

        cp = circle_payload()
        feed = cp.get("feed") or []
        roster = cp.get("roster") or []
        return {
            "ok": cp.get("ok", True),
            "feed_count": len(feed),
            "roster_count": len(roster),
            "recent_feed": feed[:5],
            "enabled_agents": [
                r.get("id") for r in roster if r.get("enabled") or r.get("status") == "online"
            ][:8],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _mac_health_light() -> dict:
    try:
        from mac_health_guard import build_report  # noqa: WPS433

        r = build_report(rescan=False)
        return {
            "ok": r.get("ok", True),
            "grade": r.get("grade"),
            "issue_count": len(r.get("issues") or []),
            "top_issues": (r.get("issues") or [])[:3],
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def collect_snapshot(*, include_runtime_ask: bool = False) -> dict:
    from n8n_automation import (  # noqa: WPS433
        n8n_status_payload,
        test_health_ping_dry_run,
        validate_workflow_files,
    )

    health = test_health_ping_dry_run()
    wf = validate_workflow_files()
    staging_count = 0
    try:
        from personal_db_ops import list_staging  # noqa: WPS433

        staging_count = len(list_staging())
    except Exception:
        pass

    snap: dict[str, Any] = {
        "ok": True,
        "captured_at": _now(),
        "schema": "n8n-intelligence-v1",
        "n8n": n8n_status_payload(),
        "stack_health": health,
        "workflows": wf,
        "layer_a": _layer_a_summary(),
        "staging_count": staging_count,
        "intelligence_circle": _intelligence_circle_summary(),
        "mac_health": _mac_health_light(),
    }
    snap["analysis"] = analyze_for_products(snap)
    if include_runtime_ask and health.get("runtime", {}).get("ok"):
        snap["runtime_insights"] = _runtime_product_ask(snap)
    return snap


def analyze_for_products(snapshot: dict) -> dict:
    """Rule-based product + automation signals (no LLM required)."""
    signals: list[dict] = []
    opportunities: list[dict] = []
    score = 100

    n8n = snapshot.get("n8n") or {}
    if not n8n.get("n8n_running"):
        score -= 15
        signals.append(
            {
                "id": "n8n_down",
                "severity": "medium",
                "title": "n8n not running",
                "action": "Start n8n and import intelligence pipeline workflow",
            }
        )
        opportunities.append(
            {
                "id": "sched_capture",
                "theme": "automation",
                "title": "Scheduled intelligence capture",
                "why": "n8n can poll hub/runtime/Layer A on a cadence for product planning",
            }
        )

    health = snapshot.get("stack_health") or {}
    if not health.get("ok"):
        score -= 25
        signals.append(
            {
                "id": "stack_degraded",
                "severity": "high",
                "title": "Hub or runtime health ping failed",
                "action": "Run layer-a-smoke.sh and validate-n8n.sh",
            }
        )

    la = snapshot.get("layer_a") or {}
    ec = int(la.get("entry_count") or 0)
    staging = int(snapshot.get("staging_count") or 0)
    if staging > 0:
        signals.append(
            {
                "id": "staging_pending",
                "severity": "medium",
                "title": f"{staging} file(s) in ingest staging",
                "action": "Run promote-all-staging.sh",
            }
        )
    if ec < 25:
        opportunities.append(
            {
                "id": "layer_a_depth",
                "theme": "knowledge_product",
                "title": "Deepen Layer A knowledge graph",
                "why": f"Only {ec} indexed entries — ingest more Cursor exports for smarter products",
            }
        )
    layers = la.get("layers") or {}
    if layers.get("L2-knowledge", 0) < 5:
        signals.append(
            {
                "id": "l2_thin",
                "severity": "low",
                "title": "L2 knowledge layer is thin",
                "action": "Promote staging → L2 via CLI ingest",
            }
        )

    ic = snapshot.get("intelligence_circle") or {}
    if ic.get("ok") and ic.get("feed_count", 0) == 0:
        opportunities.append(
            {
                "id": "live_agents",
                "theme": "intelligence_product",
                "title": "Wire live-agent feed into n8n",
                "why": "Intelligence circle has no recent feed — connect OpenRouter/maintainer to n8n webhooks",
            }
        )

    wf = snapshot.get("workflows") or {}
    if wf.get("ok"):
        for chk in wf.get("checks") or []:
            if chk.get("ok"):
                opportunities.append(
                    {
                        "id": f"wf_{chk.get('id')}",
                        "theme": "n8n_workflow",
                        "title": f"Activate workflow: {chk.get('name', chk.get('id'))}",
                        "why": "Validated in the repository — import in n8n UI for scheduled runs",
                    }
                )

    opportunities = opportunities[:8]
    signals = signals[:6]
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"

    return {
        "stack_health_score": score,
        "grade": grade,
        "signals": signals,
        "product_opportunities": opportunities,
        "recommended_automations": [
            "Schedule: GET /api/n8n/intelligence?refresh=1 every 6h",
            "Webhook: POST product events to /api/n8n/intelligence action=ingest",
            "Chain: snapshot → liaison/ask → store brief in ~/.sina/n8n-intelligence/",
        ],
    }


def _runtime_product_ask(snapshot: dict) -> dict:
    summary = json.dumps(
        {
            "analysis": snapshot.get("analysis"),
            "layer_a_count": (snapshot.get("layer_a") or {}).get("entry_count"),
            "n8n_running": (snapshot.get("n8n") or {}).get("n8n_running"),
        },
        indent=0,
    )[:3500]
    query = (
        "You are a product strategist for Sina AI. Given this hub automation snapshot, "
        "return exactly 3 bullet product ideas that could be built with n8n + existing stack. "
        "One line each. Snapshot: "
        + summary
    )
    r = _probe_json(RUNTIME_ASK, method="POST", body={"query": query, "chat_id": "n8n-intelligence"})
    if not r.get("ok"):
        return {"ok": False, "error": r.get("error", "liaison ask failed")}
    data = r.get("data") or {}
    reply = data.get("reply") or data.get("summary") or data.get("answer") or str(data)[:2000]
    return {"ok": True, "reply": reply}


def save_snapshot(snapshot: dict) -> dict:
    INTEL_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ts = snapshot.get("captured_at", _now()).replace(":", "-")
    hist_path = HISTORY_DIR / f"{ts}.json"
    hist_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    LATEST_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    brief = format_brief_markdown(snapshot)
    BRIEF_PATH.write_text(brief, encoding="utf-8")
    return {
        "ok": True,
        "latest": str(LATEST_PATH),
        "brief": str(BRIEF_PATH),
        "history": str(hist_path),
    }


def load_latest() -> dict:
    if not LATEST_PATH.is_file():
        return {"ok": False, "error": "no capture yet — run capture_intelligence"}
    return {"ok": True, "snapshot": json.loads(LATEST_PATH.read_text(encoding="utf-8"))}


def format_brief_markdown(snapshot: dict) -> str:
    a = snapshot.get("analysis") or {}
    lines = [
        "# n8n Intelligence Brief",
        "",
        f"**Captured:** {snapshot.get('captured_at', '?')}",
        f"**Stack score:** {a.get('stack_health_score', '?')} ({a.get('grade', '?')})",
        "",
        "## Signals",
    ]
    for s in a.get("signals") or []:
        lines.append(f"- **{s.get('title')}** — {s.get('action', s.get('severity', ''))}")
    lines.append("")
    lines.append("## Product opportunities")
    for o in a.get("product_opportunities") or []:
        lines.append(f"- **{o.get('title')}** ({o.get('theme')}): {o.get('why')}")
    ri = snapshot.get("runtime_insights") or {}
    if ri.get("ok") and ri.get("reply"):
        lines.extend(["", "## Runtime strategist", "", str(ri.get("reply"))])
    lines.extend(
        [
            "",
            "## n8n wiring",
            f"- Hub API: `{HUB_INTEL_URL}`",
            "- Webhook workflow: `sinaai-product-signal-webhook.json`",
            "- Scheduled pipeline: `sinaai-intelligence-pipeline.json`",
            "",
        ]
    )
    return "\n".join(lines)


def capture_and_save(*, include_runtime_ask: bool = True) -> dict:
    snap = collect_snapshot(include_runtime_ask=include_runtime_ask)
    saved = save_snapshot(snap)
    return {
        "ok": True,
        "message": "Intelligence capture saved",
        "snapshot": snap,
        "paths": saved,
        "brief_preview": (BRIEF_PATH.read_text(encoding="utf-8")[:1200] if BRIEF_PATH.is_file() else ""),
    }


def ingest_webhook_payload(body: dict) -> dict:
    """n8n (or external) pushes events — append to intel feed."""
    INTEL_DIR.mkdir(parents=True, exist_ok=True)
    feed_path = INTEL_DIR / "webhook-feed.jsonl"
    row = {"at": _now(), "source": body.get("source", "n8n"), "payload": body}
    with feed_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    latest = load_latest()
    if latest.get("ok"):
        snap = latest["snapshot"]
        snap.setdefault("webhook_events", []).append(row)
        save_snapshot(snap)
    return {"ok": True, "stored": str(feed_path), "event": row}


def intelligence_payload(*, refresh: bool = False) -> dict:
    if refresh:
        return capture_and_save(include_runtime_ask=True)
    latest = load_latest()
    if latest.get("ok"):
        snap = latest["snapshot"]
        return {
            "ok": True,
            "refreshed": False,
            "snapshot": snap,
            "analysis": snap.get("analysis"),
            "paths": {"latest": str(LATEST_PATH), "brief": str(BRIEF_PATH)},
            "webhook_url": HUB_INTEL_URL,
            "webhook_ingest_hint": 'POST {"action":"ingest","source":"n8n","event":"...","data":{}}',
        }
    return capture_and_save(include_runtime_ask=False)


def handle_intelligence_action(body: dict | None = None, *, query: dict | None = None) -> dict:
    body = body or {}
    q = query or {}
    action = (body.get("action") or q.get("action") or "get").strip().lower()
    if action in ("capture", "refresh"):
        return capture_and_save(include_runtime_ask=body.get("runtime_ask", True))
    if action == "ingest":
        return ingest_webhook_payload(body)
    if action == "analyze":
        latest = load_latest()
        if not latest.get("ok"):
            snap = collect_snapshot()
        else:
            snap = latest["snapshot"]
        return {"ok": True, "analysis": analyze_for_products(snap)}
    if q.get("refresh") in ("1", "true", "yes"):
        return capture_and_save(include_runtime_ask=True)
    return intelligence_payload(refresh=False)
