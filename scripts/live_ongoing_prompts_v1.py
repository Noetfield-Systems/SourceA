#!/usr/bin/env python3
"""Live next-10 ongoing prompts — disk truth mirror for Next steps + machine order.

Law: SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md
Rows = 10 consecutive queue turns from cursor (not deduped by sa_id).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "live-ongoing-prompts-next-10-v1.json"
OVERRIDES = SINA / "live-prompt-overrides-v1.json"
VALIDATOR_RECEIPT = SINA / "live-pack-validator-receipt-v1.json"
SCHEMA = "live-ongoing-prompts-next-10-v1"
LIMIT = 10
PREVIEW_CHARS = 400

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _honest_progress() -> dict:
    try:
        from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

        audit = audit_registry_done()
        honest = int(audit.get("honest_done") or 0)
        total = int(audit.get("total") or 1000)
        return {
            "honest_done": honest,
            "total": total,
            "label": f"{honest}/{total}",
            "pct": round(100.0 * honest / max(total, 1), 1),
        }
    except Exception:
        return {"honest_done": 0, "total": 1000, "label": "0/1000", "pct": 0.0}


def _factory_snapshot() -> dict:
    try:
        from factory_control_v1 import rebuild_factory_now  # noqa: WPS433

        row = rebuild_factory_now(caller="live_ongoing_prompts", force=False)
        return {
            "mode": row.get("mode") or "UNKNOWN",
            "kill_flag": bool(row.get("kill_flag")),
            "freeze": bool(row.get("kill_flag")),
        }
    except Exception:
        return {"mode": "UNKNOWN", "kill_flag": False, "freeze": False}


def load_overrides() -> dict:
    data = _read_json(OVERRIDES)
    if not data:
        return {
            "schema": "live-prompt-overrides-v1",
            "edits": {},
            "quarantine": [],
            "excluded": [],
            "founder_confirmed_at": None,
        }
    return data


def _clean_title(item: dict) -> str:
    title = str(item.get("sa_title") or item.get("title") or "")
    title = re.sub(r"^\[(CHECK|ACT|VERIFY)\]\s*", "", title, flags=re.I)
    sa = str(item.get("sa_id") or "")
    if sa:
        title = re.sub(rf"^{re.escape(sa)}\s*[—–-]\s*", "", title).strip()
    return title[:120] if title else "Audit task"


def _apply_overrides(*, item: dict, pos: int, overrides: dict) -> dict | None:
    if pos in overrides.get("excluded") or str(pos) in overrides.get("excluded", []):
        return None
    quarantine = set(overrides.get("quarantine") or [])
    if pos in quarantine or str(pos) in quarantine:
        return None
    edits = overrides.get("edits") or {}
    edit = edits.get(str(pos)) or edits.get(pos)
    if edit and isinstance(edit, dict):
        if edit.get("instruction"):
            item = {**item, "instruction": edit["instruction"]}
        if edit.get("title"):
            item = {**item, "sa_title": edit["title"]}
    return item


def _cloud_forge_glance() -> dict:
    """Read-only Railway queue — Mac FREEZE routes factory body to cloud."""
    try:
        from fbe.lib.hub_cloud_proxy_v1 import cloud_worker_url, execution_mode  # noqa: WPS433

        if execution_mode() != "CLOUD_ONLY":
            return {}
        base = cloud_worker_url()
        if not base:
            return {}
        import urllib.request

        with urllib.request.urlopen(f"{base.rstrip('/')}/api/cloud-forge-run/queue/v1", timeout=12) as resp:
            row = json.loads(resp.read().decode("utf-8"))
        head = str(row.get("cloud_forge_run_head") or "")
        return {
            "ok": bool(head),
            "head": head,
            "batch_id": row.get("batch_id"),
            "drain_status": row.get("drain_status"),
            "queue_batch_complete": row.get("queue_batch_complete"),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:120]}


def _execution_surface() -> str:
    try:
        from fbe.lib.hub_cloud_proxy_v1 import execution_mode  # noqa: WPS433

        return "cloud_forge" if execution_mode() == "CLOUD_ONLY" else "inbox_only"
    except Exception:
        return "inbox_only"


def _inline_validator_receipt(*, cursor_pos: int, items: list[dict]) -> dict:
    head = items[cursor_pos - 1] if 0 < cursor_pos <= len(items) else {}
    inbox_path = SINA / "worker-prompt-inbox-v1.json"
    inbox = _read_json(inbox_path) if inbox_path.is_file() else {}
    sa = str(head.get("sa_id") or "")
    ib_sa = str((inbox.get("meta") or {}).get("sa_id") or inbox.get("sa_id") or "")
    bind_ok = bool(sa and ib_sa == sa)
    cloud = _cloud_forge_glance()
    cloud_active = bool(cloud.get("ok") and cloud.get("head"))
    surface = _execution_surface()
    if surface == "cloud_forge" and cloud_active and not bool(inbox.get("pending")):
        bind_ok = True
    bind_detail = (
        f"queue={sa} cloud_head={cloud.get('head')} batch={cloud.get('batch_id')} surface={surface}"
        if cloud_active and surface == "cloud_forge"
        else f"queue={sa} inbox={ib_sa} bind={ib_sa if bind_ok else 'mismatch'}"
    )
    row = {
        "ok": bind_ok,
        "schema": "live-pack-validator-receipt-v1",
        "at": _now(),
        "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        "checks": [
            {
                "id": "run_inbox_truth",
                "ok": bool(sa) or cloud_active,
                "detail": sa or str(cloud.get("head") or ""),
                "inbox_pending": bool(inbox.get("pending")),
            },
            {
                "id": "healthy_pack_bind",
                "ok": bind_ok,
                "detail": bind_detail,
            },
            {
                "id": "cloud_forge_glance",
                "ok": cloud_active if surface == "cloud_forge" else True,
                "detail": cloud.get("head") or cloud.get("error") or "skipped_not_cloud_only",
            },
        ],
        "failed": [],
    }
    row["failed"] = [c["id"] for c in row["checks"] if not c.get("ok")]
    row["ok"] = not row["failed"]
    VALIDATOR_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def rebuild(*, write: bool = True, preview: bool = True) -> dict:
    from healthy_queue_ssot_lib import healthy_queue_path, healthy_queue_state_path  # noqa: WPS433
    from prompt_feasibility_gate import check_text  # noqa: WPS433

    queue_path = healthy_queue_path()
    if not queue_path.is_file():
        return {"ok": False, "error": "queue_missing", "path": str(queue_path)}

    queue = _read_json(queue_path)
    items = queue.get("queue") or []
    exhausted = bool(queue.get("queue_exhausted") or queue.get("phase_strict_complete"))
    if not items:
        if not exhausted:
            return {"ok": False, "error": "empty_queue"}
        hp = _honest_progress()
        factory = _factory_snapshot()
        row = {
            "ok": True,
            "schema": SCHEMA,
            "built_at": _now(),
            "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
            "cursor_pos": 0,
            "queue_total": 0,
            "queue_exhausted": True,
            "queue_path": str(queue_path),
            "valid_yes": hp["label"],
            "honest_done": hp["honest_done"],
            "honest_total": hp["total"],
            "factory_mode": factory.get("mode"),
            "freeze": factory.get("freeze"),
            "founder_confirmed_at": load_overrides().get("founder_confirmed_at"),
            "validator_receipt": {"ok": True, "detail": "queue_exhausted_idle"},
            "turns": [],
            "count": 0,
            "limit": LIMIT,
            "note": "Goal 1 complete · queue idle — advisory only until ASF names next pack",
        }
        if write:
            SINA.mkdir(parents=True, exist_ok=True)
            OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
            _write_worker_drain_compat(row)
        return row

    state = _read_json(healthy_queue_state_path())
    cursor_pos = int(state.get("next_pos") or 1)
    if cursor_pos < 1:
        cursor_pos = 1
    exhausted = bool(queue.get("queue_exhausted") or queue.get("phase_strict_complete"))
    if cursor_pos > len(items):
        if exhausted:
            hp = _honest_progress()
            factory = _factory_snapshot()
            cloud = _cloud_forge_glance()
            surface = _execution_surface()
            cloud_ok = bool(cloud.get("ok")) if surface == "cloud_forge" else False
            validator_receipt = {
                "ok": cloud_ok,
                "schema": "live-pack-validator-receipt-v1",
                "at": _now(),
                "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
                "checks": [
                    {
                        "id": "queue_exhausted",
                        "ok": True,
                        "detail": f"cursor={cursor_pos} items={len(items)}",
                    },
                    {
                        "id": "healthy_pack_bind",
                        "ok": cloud_ok,
                        "detail": f"cloud_head={cloud.get('head')} batch={cloud.get('batch_id')} surface={surface}",
                    },
                    {
                        "id": "cloud_forge_glance",
                        "ok": cloud_ok,
                        "detail": cloud.get("head") or cloud.get("error") or "missing",
                    },
                ],
                "failed": [] if cloud_ok else ["healthy_pack_bind", "cloud_forge_glance"],
            }
            row = {
                "ok": cloud_ok,
                "schema": SCHEMA,
                "built_at": _now(),
                "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
                "cursor_pos": cursor_pos,
                "queue_total": len(items),
                "queue_exhausted": True,
                "queue_path": str(queue_path),
                "valid_yes": hp["label"],
                "honest_done": hp["honest_done"],
                "honest_total": hp["total"],
                "factory_mode": factory.get("mode"),
                "freeze": factory.get("freeze"),
                "founder_confirmed_at": load_overrides().get("founder_confirmed_at"),
                "validator_receipt": validator_receipt,
                "turns": [],
                "count": 0,
                "limit": LIMIT,
                "execution_surface": surface,
                "cloud_forge_glance": cloud,
                "note": (
                    f"Healthy queue complete · cloud body at {cloud.get('head')} · "
                    "Mac observes only — CF cron */10"
                ),
            }
            if write:
                SINA.mkdir(parents=True, exist_ok=True)
                OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
                VALIDATOR_RECEIPT.write_text(json.dumps(validator_receipt, indent=2) + "\n", encoding="utf-8")
                _write_worker_drain_compat(row)
            return row
        cursor_pos = len(items)

    if cursor_pos > len(items):
        cursor_pos = len(items)

    overrides = load_overrides()
    hp = _honest_progress()
    factory = _factory_snapshot()
    validator_receipt = _inline_validator_receipt(cursor_pos=cursor_pos, items=items)

    surface = _execution_surface()
    cloud = _cloud_forge_glance()
    turns: list[dict] = []
    order = 0
    for pos in range(cursor_pos, min(len(items), cursor_pos + LIMIT - 1) + 1):
        raw_item = items[pos - 1]
        item = _apply_overrides(item=dict(raw_item), pos=pos, overrides=overrides)
        if item is None:
            continue
        role = (item.get("queue_role") or item.get("step_type") or "check").lower()
        sa_id = str(item.get("sa_id") or "")
        instr = str(item.get("instruction") or "")
        if role == "check" or re.search(r"\bNO\s+OpenRouter\b", instr, re.I):
            blob = instr
        else:
            blob = " ".join(str(item.get(k) or "") for k in ("instruction", "verify", "queue_role", "sa_title"))
        feas = check_text(blob)
        preview_text = ""
        if preview:
            try:
                from healthy_prompt_turn_v1 import build_turn_prompt  # noqa: WPS433

                full = build_turn_prompt(item=item, pos=pos, total=len(items), engine="WORKER")
                preview_text = full[:PREVIEW_CHARS]
            except Exception as exc:
                preview_text = f"(preview error: {exc})"[:PREVIEW_CHARS]
        order += 1
        turns.append(
            {
                "order": order,
                "queue_pos": pos,
                "sa_id": sa_id,
                "queue_role": role,
                "title": _clean_title(item),
                "preview": preview_text,
                "feasible": bool(feas.get("ok")),
                "feasibility_reasons": feas.get("reasons") or [],
                "quarantined": False,
                "founder_edit": (overrides.get("edits") or {}).get(str(pos)),
                "is_current": pos == cursor_pos,
                "execution_bind": "bound" if pos == cursor_pos else "preview_not_bound",
                "execution_surface": surface if pos == cursor_pos else "not_bound",
                "cloud_forge_head": cloud.get("head") if pos == cursor_pos else None,
                "label": (
                    "CLOUD FORGE — CF cron auto-tick"
                    if pos == cursor_pos and surface == "cloud_forge"
                    else ("RUN INBOX — current turn" if pos == cursor_pos else "not bound — preview only")
                ),
            }
        )

    row = {
        "ok": True,
        "schema": SCHEMA,
        "built_at": _now(),
        "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        "cursor_pos": cursor_pos,
        "queue_total": len(items),
        "queue_path": str(queue_path),
        "valid_yes": hp["label"],
        "honest_done": hp["honest_done"],
        "honest_total": hp["total"],
        "factory_mode": factory.get("mode"),
        "freeze": factory.get("freeze"),
        "founder_confirmed_at": overrides.get("founder_confirmed_at"),
        "validator_receipt": validator_receipt if validator_receipt else {"ok": None},
        "turns": turns,
        "count": len(turns),
        "limit": LIMIT,
        "execution_surface": surface,
        "cloud_forge_glance": cloud if surface == "cloud_forge" else None,
        "note": (
            f"Live machine order: queue turns {cursor_pos}..{cursor_pos + len(turns) - 1}"
            if turns
            else "No turns at cursor — check queue/overrides"
        ),
    }

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        _write_worker_drain_compat(row)

    return row


def _write_worker_drain_compat(live: dict) -> None:
    """Backward compat for home card worker-drain-next-10-v1.json."""
    drain_path = SINA / "worker-drain-next-10-v1.json"
    turns = live.get("turns") or []
    seen: set[str] = set()
    drain: list[dict] = []
    for t in turns:
        sa = t.get("sa_id")
        if not sa or sa in seen:
            continue
        seen.add(sa)
        drain.append(
            {
                "order": len(drain) + 1,
                "queue_pos": t.get("queue_pos"),
                "sa_id": sa,
                "title": t.get("title"),
                "roles": ["check", "act", "verify"],
                "rail": "goal1_healthy_drain",
            }
        )
    compat = {
        "ok": True,
        "schema": "worker-drain-next-10-v1",
        "built_at": live.get("built_at"),
        "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        "queue_path": live.get("queue_path"),
        "next_pos": live.get("cursor_pos"),
        "queue_total": live.get("queue_total"),
        "valid_yes_label": live.get("valid_yes"),
        "count": len(drain),
        "limit": 10,
        "note": "Compat slice from live-ongoing-prompts (unique sa for home card)",
        "drain": drain,
        "live_ongoing_path": str(OUT),
    }
    drain_path.write_text(json.dumps(compat, indent=2) + "\n", encoding="utf-8")


def payload(*, rebuild_if_missing: bool = True) -> dict:
    if OUT.is_file():
        data = _read_json(OUT)
        if data.get("schema") == SCHEMA:
            return data
    if rebuild_if_missing:
        return rebuild(write=True)
    return {"ok": False, "error": "live_ongoing_missing"}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Live ongoing prompts next-10")
    p.add_argument("--rebuild", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-preview", action="store_true")
    args = p.parse_args()

    if args.rebuild:
        out = rebuild(write=True, preview=not args.no_preview)
    else:
        out = payload()

    if args.json or args.rebuild:
        print(json.dumps(out, indent=2))
    else:
        print("OK" if out.get("ok") else f"FAIL: {out.get('error')}")

    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
