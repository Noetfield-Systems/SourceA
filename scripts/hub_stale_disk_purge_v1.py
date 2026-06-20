#!/usr/bin/env python3
"""Purge + DELETE stale Sina Command / legacy / museum from disk (ASF retire forever)."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "agent-control-panel"
SINA = Path.home() / ".sina"
SUPERSEDED = ROOT / "archive" / "superseded"

STALE_RE = re.compile(
    r"(?:Sina\s+Command(?!\s+RETIRED|\s+DELETED)|/legacy/|Founder\s+Museum|SINA\s+COMMAND|tab=command|"
    r"museum-readonly|\?tab=apps|oldhubsinacommand|legacy_archive_url|legacy_hub_url)",
    re.I,
)

DROP_KEYS = frozenset(
    {
        "founder_museum",
        "legacy_hub_url",
        "legacy_archive_url",
        "museum_url",
        "legacy_url",
        "zone_c_museum",
    }
)

DELETE_SINA_FILES = (
    "founder-museum-read-only-v1.json",
    "sina-command-quarantine-v1.json",
    "worker-hub-boot-v1.json",
    "llm_context_packet_v1.json",
    "context_compression_v1.json",
    "context_ranking_v1.json",
    "vector_index_v1.json",
    "agent-memory-mirror-v1.json",
    "ecosystem-subjects-full.json",
    "vector_index_v1.json",
    "honest-p0-screen.html",
    "command-server-launchd.log",
    "prompt-direction.json",
    "brain-live-context-v1.json",
    "prompt-direction-v1.json",
    "prompt-direction-context-v1.json",
    "hub-projection-stale-v1.json",
    "agent-live-surfaces-v1.json",
)

DELETE_ROOT_FILES = (
    "FOUNDER_MUSEUM_READ_ONLY_RESTORE_LOCKED_v1.md",
)

DELETE_BRAND_APPS = (
    "Sina Command.app",
    "Sina Command Apps.app",
    "Sina Decide.app",
    "Sina Dispatch.app",
    "Sina Execute All.app",
    "Sina Prompt OS.app",
    "Sina Run Now.app",
    "Sina Status.app",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    tmp.replace(path)


def _deep_scrub(obj: Any) -> tuple[Any, bool]:
    changed = False
    if isinstance(obj, dict):
        out: dict = {}
        for k, v in obj.items():
            if k in DROP_KEYS:
                changed = True
                continue
            if k == "hero_actions" and isinstance(v, list):
                nv = [x for x in v if isinstance(x, dict) and x.get("id") != "founder_museum"]
                if len(nv) != len(v):
                    changed = True
                v = nv
            if k == "urls" and isinstance(v, dict):
                v = {kk: vv for kk, vv in v.items() if kk not in ("museum", "alias")}
                changed = True
            fixed, c = _deep_scrub(v)
            changed = changed or c
            if isinstance(fixed, str) and STALE_RE.search(fixed):
                # Preserve intentional retire/deleted wording
                if re.search(r"Command.*DELETED|RETIRED|legacy.*must not", fixed, re.I):
                    out[k] = fixed
                    continue
                fixed = re.sub(r"/legacy/?", "/", fixed, flags=re.I)
                fixed = re.sub(r"Sina\s+Command", "Hub", fixed, flags=re.I)
                fixed = re.sub(r"Founder\s+Museum[^·|]*", "Hub H1", fixed, flags=re.I)
                changed = True
            out[k] = fixed
        return out, changed
    if isinstance(obj, list):
        out_list = []
        for item in obj:
            fixed, c = _deep_scrub(item)
            changed = changed or c
            out_list.append(fixed)
        return out_list, changed
    if isinstance(obj, str) and STALE_RE.search(obj):
        fixed = re.sub(r"/legacy/?", "/", obj, flags=re.I)
        fixed = re.sub(r"Sina\s+Command", "Hub", fixed, flags=re.I)
        return fixed, True
    return obj, False


def _minimal_hub_payload() -> dict:
    from factory_control_v1 import load_factory_now  # noqa: WPS433
    from worker_drain_lib import healthy_queue_status  # noqa: WPS433
    from hub_sync_slim_v1 import bump_shell_generation_id  # noqa: WPS433

    fn = load_factory_now()
    queue = healthy_queue_status()
    sa = str(queue.get("sa_id") or "—")
    role = str(queue.get("queue_role") or "CHECK")
    gid = bump_shell_generation_id()
    built = _now()
    return {
        "schema_version": 5,
        "built_at": built,
        "generation_id": gid,
        "source_a_root": str(ROOT),
        "hub_mode": "worker-only",
        "command_retired_forever": True,
        "law": "ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md",
        "command_center": {
            "founder": {
                "p0": {
                    "id": "HUB-WORKER",
                    "title": "Source A · Hub",
                    "status": "active",
                    "next_action": f"RUN INBOX · Worker chat · {sa} · {role}",
                    "hook": "ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md",
                },
                "must_do_today": [
                    "Hub only — H1 / · H2 /machines/",
                    f"Factory · valid_yes={fn.get('valid_yes')} · mode={fn.get('mode')}",
                ],
                "ops_cards": [],
            }
        },
        "daily_hub": {
            "h1_url": "/",
            "h1_label": "Super Fast Hub (H1)",
            "h2_url": "/machines/",
            "h2_label": "Machine Hub (H2)",
            "legacy_retired": True,
        },
        "sourcea_sa_queue": {
            "sa_id": queue.get("sa_id"),
            "queue_pos": queue.get("queue_pos"),
            "queue_total": queue.get("queue_total"),
            "queue_role": queue.get("queue_role"),
        },
        "factory_now": {
            "valid_yes": fn.get("valid_yes"),
            "mode": fn.get("mode"),
            "brain_vy": fn.get("brain_vy"),
        },
    }


def refresh_worker_hub_boot() -> dict:
    from worker_hub_v1 import worker_hub_payload  # noqa: WPS433
    from worker_hub_daily_rooms_v1 import daily_rooms_payload  # noqa: WPS433

    row = worker_hub_payload(skip_cache=True)
    row["boot"] = True
    row["boot_at"] = _now()
    row.pop("founder_museum", None)
    row.pop("legacy_hub_url", None)
    upgrade = dict(row.get("upgrade") or {})
    upgrade.pop("legacy_archive_url", None)
    row["upgrade"] = upgrade
    row["hero_actions"] = [
        {
            "id": "h2_machines",
            "label": "Machine Hub",
            "path": "/machines/",
            "url": "http://127.0.0.1:13020/machines/",
        }
    ]
    row["command_retired_forever"] = True
    panel_boot = PANEL / "worker-hub" / "boot.json"
    sina_boot = SINA / "worker-hub-boot-v1.json"
    _write_json(panel_boot, row)
    _write_json(sina_boot, row)
    return {"ok": True, "built_at": row.get("built_at"), "hero_count": len(row["hero_actions"])}


def scrub_all_sina_json(*, max_depth: int = 6) -> list[dict]:
    """Deep-scrub ~/.sina JSON/YAML/HTML not under judge counsel / chat exports."""
    actions: list[dict] = []
    skip_dirs = {"judge-center", "chat-unify", "events", "audits"}
    for path in sorted(SINA.rglob("*")):
        if not path.is_file() or path.suffix not in (".json", ".yaml", ".yml", ".html"):
            continue
        rel = path.relative_to(SINA)
        if any(part in skip_dirs for part in rel.parts):
            continue
        if len(rel.parts) > max_depth:
            continue
        if path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            if not STALE_RE.search(text):
                continue
            if path.suffix == ".json":
                data = json.loads(text)
                healed, changed = _deep_scrub(data)
                if changed:
                    healed["stale_purge_at"] = _now()
                    path.write_text(json.dumps(healed, indent=2) + "\n", encoding="utf-8")
                    actions.append({"path": str(path), "action": "deep_scrubbed"})
            else:
                healed_text = STALE_RE.sub("Hub", text)
                healed_text = re.sub(r"/legacy/?", "/", healed_text, flags=re.I)
                if healed_text != text:
                    path.write_text(healed_text, encoding="utf-8")
                    actions.append({"path": str(path), "action": "text_scrubbed"})
        except (OSError, json.JSONDecodeError):
            if path.suffix in (".html", ".yaml", ".yml"):
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                    healed_text = re.sub(r"Sina\s+Command", "Hub", text, flags=re.I)
                    healed_text = re.sub(r"/legacy/?", "/", healed_text, flags=re.I)
                    if healed_text != text:
                        path.write_text(healed_text, encoding="utf-8")
                        actions.append({"path": str(path), "action": "text_scrubbed"})
                except OSError:
                    pass
            continue
    return actions


def purge_stale_files(*, delete_monolith: bool = True) -> list[dict]:
    actions: list[dict] = []

    monolith_archive = ROOT / "archive" / "hub-monolith-legacy-2026-06"
    if delete_monolith and monolith_archive.is_dir():
        shutil.rmtree(monolith_archive)
        actions.append({"path": str(monolith_archive), "action": "deleted_tree"})

    maintainer_ws = SINA / "agent-workspaces" / "sinaai_maintainer"
    if maintainer_ws.is_dir():
        shutil.rmtree(maintainer_ws)
        actions.append({"path": str(maintainer_ws), "action": "deleted_tree"})

    brand_apps = ROOT / "brand" / "macos-apps"
    for name in DELETE_BRAND_APPS:
        app = brand_apps / name
        if app.is_dir():
            shutil.rmtree(app)
            actions.append({"path": str(app), "action": "deleted_app_bundle"})

    for rel in DELETE_SINA_FILES:
        p = SINA / rel
        if p.is_file():
            p.unlink()
            actions.append({"path": str(p), "action": "deleted_file"})

    SUPERSEDED.mkdir(parents=True, exist_ok=True)
    for rel in DELETE_ROOT_FILES:
        src = ROOT / rel
        if src.is_file():
            dst = SUPERSEDED / rel
            if dst.is_file():
                dst.unlink()
            shutil.move(str(src), str(dst))
            actions.append({"path": str(src), "action": "moved_to_superseded"})

    mini_apps = PANEL / "mini-apps"
    if mini_apps.is_dir():
        shutil.rmtree(mini_apps)
        actions.append({"path": str(mini_apps), "action": "deleted_tree"})

    assets = PANEL / "assets"
    if assets.is_dir():
        shutil.rmtree(assets, ignore_errors=True)
        actions.append({"path": str(assets), "action": "deleted_tree_if_any"})

    if (PANEL / "index.html").is_file():
        (PANEL / "index.html").unlink()
        actions.append({"path": str(PANEL / "index.html"), "action": "deleted_file"})

    return actions


def rewrite_command_data() -> dict:
    from sina_command_lib import build_shell_payload, verify_command_data_atomic  # noqa: WPS433
    from hub_projection_canonical_v1 import split_hub_projection  # noqa: WPS433

    payload = _minimal_hub_payload()
    shell = build_shell_payload(payload)
    shell["generation_id"] = payload["generation_id"]
    shell["hub_mode"] = "worker-only"
    shell["command_retired_forever"] = True

    canonical, runtime = split_hub_projection(payload)
    canonical["command_retired_forever"] = True
    runtime["command_retired_forever"] = True
    runtime["recent_subjects"] = []
    runtime["home_v2"] = None

    _write_json(PANEL / "command-data.json", payload)
    _write_json(PANEL / "command-data-shell.json", shell)
    _write_json(PANEL / "command-data-canonical.json", canonical)
    _write_json(PANEL / "command-data-runtime.json", runtime)

    ok, msg = verify_command_data_atomic()
    return {"ok": ok, "verify": msg, "built_at": payload["built_at"]}


def verify_runtime_clean() -> list[str]:
    errors: list[str] = []
    for path in PANEL.glob("command-data*.json"):
        if STALE_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"panel:{path.name}")
    for rel in ("founder-museum-read-only-v1.json", "sina-command-quarantine-v1.json"):
        if (SINA / rel).is_file():
            errors.append(f"~/.sina/{rel}")
    sina_boot = SINA / "worker-hub-boot-v1.json"
    if sina_boot.is_file() and STALE_RE.search(sina_boot.read_text(encoding="utf-8")):
        errors.append("~/.sina/worker-hub-boot-v1.json stale")
    boot = PANEL / "worker-hub" / "boot.json"
    if boot.is_file():
        text = boot.read_text(encoding="utf-8")
        if STALE_RE.search(text) or "founder_museum" in text:
            errors.append("worker-hub/boot.json stale")
    if (PANEL / "index.html").is_file():
        errors.append("agent-control-panel/index.html")
    if (PANEL / "assets" / "app.js").is_file():
        errors.append("agent-control-panel/assets/app.js")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="DELETE stale Command/legacy/museum from disk")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--keep-archive", action="store_true")
    args = ap.parse_args()

    file_actions = purge_stale_files(delete_monolith=not args.keep_archive)
    rewrite = rewrite_command_data()
    boot = refresh_worker_hub_boot()
    scrub_actions = scrub_all_sina_json()

    try:
        from brain_stale_prompt_scrub_v1 import scrub_brain_stale_disk  # noqa: WPS433
        from worker_stale_prompt_scrub_v1 import scrub_worker_stale_disk  # noqa: WPS433
        from founder_directive_ssot_v1 import sync_all_layers  # noqa: WPS433

        brain = scrub_brain_stale_disk()
        worker = scrub_worker_stale_disk()
        sync_all_layers(stairlift=True)
    except Exception as exc:
        brain = {"error": str(exc)}
        worker = {"error": str(exc)}

    errors = verify_runtime_clean()
    row = {
        "ok": rewrite.get("ok") and boot.get("ok") and not errors,
        "at": _now(),
        "file_actions": file_actions,
        "scrub_actions": scrub_actions,
        "rewrite": rewrite,
        "boot": boot,
        "brain_scrub": brain.get("count") if isinstance(brain, dict) else brain,
        "worker_scrub": worker.get("count") if isinstance(worker, dict) else worker,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"HUB_STALE_PURGE ok={row['ok']} deleted={len(file_actions)} "
            f"scrubbed={len(scrub_actions)} errors={len(errors)}"
        )
        for e in errors:
            print(f"  ERR {e}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
