#!/usr/bin/env python3
"""AI advisory — OpenRouter analyzes live Sina Command snapshot → golden links + upgrades."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
BOWL = SOURCE_A / "sina-bowl"
ADVISORY_JSON = BOWL / "AI_ADVISORY.json"
ADVISORY_MD = BOWL / "AI_ADVISORY_LATEST.md"
PROMPTOS = Path.home() / "Desktop/SinaPromptOS"


def _load_vault_key() -> str:
    for vault in (Path.home() / ".sina/secrets.env", PROMPTOS / "secrets.env"):
        if not vault.is_file():
            continue
        for line in vault.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return (sys.environ.get("OPENROUTER_API_KEY") or "").strip()


def _chat(system: str, user: str) -> tuple[bool, str]:
    sys.path.insert(0, str(PROMPTOS))
    try:
        from core.openrouter_client import chat_completion  # noqa: WPS433

        return chat_completion(system=system, user=user, temperature=0.25, timeout=90)
    except Exception as e:
        return False, str(e)


def build_snapshot(payload: dict) -> dict:
    """Compact, no secrets — safe to send to LLM."""
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    kpi = payload.get("mergepack_kpi") or {}
    kd = kpi.get("data") or {}
    return {
        "built_at": payload.get("built_at"),
        "p0": founder.get("p0"),
        "ops_blockers": payload.get("ops_blockers") or [],
        "parallel_plans": [
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "thread": p.get("thread"),
                "status": p.get("status"),
                "next_action": p.get("next_action"),
                "progress_pct": p.get("progress_pct"),
            }
            for p in (payload.get("bowl") or {}).get("parallel_plans") or []
        ],
        "threads": [
            {"id": t.get("id"), "label": t.get("label"), "plans": t.get("plan_ids"), "products": t.get("product_ids")}
            for t in (payload.get("thread_index") or [])[:8]
        ],
        "live_products": [
            {"id": p.get("id"), "title": p.get("title"), "live": p.get("live")}
            for p in (payload.get("live_products") or [])
        ],
        "repos_blocked": [
            {"name": r.get("name"), "blocked": r.get("blocked"), "next": (r.get("next_tasks") or [{}])[0]}
            for r in (cc.get("repos") or [])
            if r.get("blocked") or r.get("global_blocker")
        ],
        "agents_active_24h": (cc.get("summary") or {}).get("active_agents_24h"),
        "kpi_trio_complete": kd.get("kpi_trio_complete"),
        "kpi_keys": {k: kd.get(k) for k in ("kpi_first_payment", "kpi_first_referral_payment", "kpi_first_organic_user")},
        "open_founder_notes": [
            {"category": n.get("category"), "text": (n.get("text") or "")[:200]}
            for n in (payload.get("founder_notes") or [])
            if n.get("status") != "done"
        ][:5],
        "drift_count": len(payload.get("drift_hints") or []),
    }


SYSTEM = """You are the Sina OS strategic advisor for founder ASF.
You receive a JSON snapshot of the live command center (programs, threads, KPI, blockers, products).
Output ONLY valid JSON (no markdown fences) with this shape:
{
  "golden_connections": [
    {"from": "entity A", "to": "entity B", "why": "one sentence — why linking them creates progress"}
  ],
  "upgrade_suggestions": [
    {"priority": "P0|P1|P2", "title": "short title", "action": "concrete next step", "thread": "THREAD-..."}
  ],
  "risks": ["short risk bullets"],
  "one_focus_today": "single sentence — the highest-leverage move today"
}
Rules:
- Respect threads: MERGEPACK revenue ≠ M8 wire automation.
- Prefer evidence from snapshot; do not invent URLs.
- Max 6 golden_connections, max 8 upgrade_suggestions, max 4 risks.
- upgrade_suggestions must be actionable in Cursor/Source A/MergePack/VIRLUX context."""


def parse_advisory_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None


def run_advisory(*, payload: dict | None = None) -> dict:
    if payload is None:
        sys.path.insert(0, str(SOURCE_A / "scripts"))
        from sina_command_lib import build_payload  # noqa: WPS433

        payload = build_payload(run_refresh_scripts=False)

    if not _load_vault_key():
        return {
            "ok": False,
            "error": "OpenRouter not configured — add OPENROUTER_API_KEY to private vault, restart Prompt OS / Command server",
            "generated_at": None,
        }

    snap = build_snapshot(payload)
    user_msg = json.dumps(snap, indent=2, ensure_ascii=False)[:14000]
    ok, raw = _chat(SYSTEM, user_msg)
    if not ok:
        return {"ok": False, "error": raw, "generated_at": None}

    parsed = parse_advisory_json(raw)
    if not parsed:
        parsed = {
            "golden_connections": [],
            "upgrade_suggestions": [],
            "risks": ["AI response was not valid JSON — retry advisory"],
            "one_focus_today": "Fix advisory parse or switch model via OPENROUTER_MODEL",
            "_raw_excerpt": raw[:1500],
        }

    out = {
        "ok": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": sys.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
        "snapshot_built_at": payload.get("built_at"),
        "advisory": parsed,
        "error": None,
    }
    _write_outputs(out, snap)
    return out


def _write_outputs(report: dict, snap: dict) -> None:
    BOWL.mkdir(parents=True, exist_ok=True)
    ADVISORY_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    adv = report.get("advisory") or {}
    lines = [
        "# AI Advisory (latest)",
        "",
        f"Generated: {report.get('generated_at')}",
        f"Snapshot: {report.get('snapshot_built_at')}",
        "",
        "## One focus today",
        adv.get("one_focus_today") or "—",
        "",
        "## Golden connections",
    ]
    for g in adv.get("golden_connections") or []:
        lines.append(f"- **{g.get('from', '?')}** → **{g.get('to', '?')}**: {g.get('why', '')}")
    lines.extend(["", "## Upgrade suggestions"])
    for u in adv.get("upgrade_suggestions") or []:
        lines.append(
            f"- **[{u.get('priority', 'P1')}]** {u.get('title', '')} — {u.get('action', '')} "
            f"({u.get('thread', '')})"
        )
    lines.extend(["", "## Risks"])
    for r in adv.get("risks") or []:
        lines.append(f"- {r}")
    ADVISORY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_cached_advisory() -> dict:
    if not ADVISORY_JSON.is_file():
        return {"ok": False, "error": "No advisory yet — run AI Advisory from Sina Command", "advisory": None}
    return json.loads(ADVISORY_JSON.read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.path.insert(0, str(SOURCE_A / "scripts"))
    from sina_command_lib import build_payload  # noqa: E402

    result = run_advisory(payload=build_payload(run_refresh_scripts=False))
    print(json.dumps({"ok": result.get("ok"), "error": result.get("error"), "generated_at": result.get("generated_at")}, indent=2))
