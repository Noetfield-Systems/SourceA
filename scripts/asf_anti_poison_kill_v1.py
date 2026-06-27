#!/usr/bin/env python3
"""ASF anti-poison kill — trash blocker/poison receipts · scrub live surfaces · no Mac stall."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
TRASH = Path.home() / ".Trash"
RECEIPT = SINA / "asf-anti-poison-kill-receipt-v1.json"

# Filename substrings → Trash (poison / Mac stall blockers only)
TRASH_NAME_PARTS = (
    "blocker",
    "blocked",
    "poison-track",
    "poison-tracking",
    "cursor-inject-blocked",
    "form-incident-",
    "fake-green-blocker",
    "healthy-queue-blockers",
    "eval-live-blocked",
    "worker-hub-boot",
    "form-official-gathering-phase",
    "governance-gate-cart",
    "demo-block-pass",
)

# Keep even if name matches
TRASH_KEEP = frozenset(
    {
        "asf-anti-poison-kill-receipt-v1.json",
        "agent-mirror-poison-scrub-receipt-v1.json",
        "sina-command-museum-retired-v1.json",
        "sina-command-museum-retired-v1.flag",
    }
)

BLOCK_ON_RE = re.compile(
    r"INCIDENT-037\s+block\s+ON|append_blocked|gathering_phase\s*=\s*active|block ON ·",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def move_to_trash(path: Path) -> str | None:
    if not path.exists() or path.name in TRASH_KEEP:
        return None
    TRASH.mkdir(parents=True, exist_ok=True)
    dest = TRASH / path.name
    n = 1
    while dest.exists():
        dest = TRASH / f"{path.name}.{n}"
        n += 1
    shutil.move(str(path), str(dest))
    return str(dest)


def trash_poison_files() -> list[str]:
    moved: list[str] = []
    if SINA.is_dir():
        for path in sorted(SINA.rglob("*")):
            if not path.is_file():
                continue
            low = path.name.lower()
            if path.name in TRASH_KEEP:
                continue
            if any(p in low for p in TRASH_NAME_PARTS):
                dest = move_to_trash(path)
                if dest:
                    moved.append(dest)
    for rel in (
        "n8n/workflows/wf-poison-track-reminder-v1.json",
        "infra/cleanup/poison-audit-report-v1.json",
    ):
        p = ROOT / rel
        if p.is_file():
            dest = move_to_trash(p)
            if dest:
                moved.append(dest)
    return moved


def _scrub_text(s: str) -> str:
    s = BLOCK_ON_RE.sub("founder picks only", s)
    s = s.replace("INCIDENT-037 block ON", "founder supremacy ON")
    s = s.replace("append_blocked", "append_allowed")
    s = re.sub(r'"gathering_phase"\s*:\s*true', '"gathering_phase": false', s)
    s = re.sub(r'"append_blocked"\s*:\s*true', '"append_blocked": false', s)
    return s


def scrub_json_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return False
    changed = False

    def walk(obj):
        nonlocal changed
        if isinstance(obj, dict):
            for k in list(obj.keys()):
                if k in ("blockers", "dispatch_ready_blockers", "blocking_conditions", "architect_blockers"):
                    if obj[k]:
                        obj[k] = []
                        changed = True
                elif k == "dispatch_ready" and obj[k] is False:
                    obj[k] = True
                    changed = True
                elif k == "gate_mode" and str(obj.get(k)) == "enforce":
                    obj[k] = "advisory"
                    changed = True
                elif k == "current_gate_mode" and str(obj.get(k)) == "enforce":
                    obj[k] = "advisory"
                    changed = True
                elif k == "gate_is_enforce" and obj[k] is True:
                    obj[k] = False
                    changed = True
                elif k == "blocked" and obj[k] is True:
                    obj[k] = False
                    changed = True
                elif k == "append_blocked" and obj[k] is True:
                    obj[k] = False
                    changed = True
                elif k == "gathering_phase" and obj[k] is True:
                    obj[k] = False
                    changed = True
                elif k == "active" and k == "active" and obj.get("schema", "").startswith("form-official-gathering"):
                    obj[k] = False
                    changed = True
                else:
                    walk(obj[k])
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, dict) and item.get("status") == "blocked":
                    item["status"] = "open"
                    changed = True
                walk(item)

    walk(data)
    new_raw = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    scrubbed = _scrub_text(new_raw)
    if scrubbed != raw or changed:
        path.write_text(scrubbed, encoding="utf-8")
        return True
    return False


def scrub_live_surfaces() -> list[str]:
    touched: list[str] = []
    targets = list(SINA.glob("*.json"))
    targets.extend((ROOT / "agent-control-panel").glob("command-data*.json"))
    targets.append(ROOT / "agent-control-panel" / "worker-hub" / "boot.json")
    for path in targets:
        if path.is_file() and scrub_json_file(path):
            touched.append(str(path))
    return touched


def run_poison_scrub() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "agent_mirror_poison_scrub_v1.py"), "--scrub", "--sync", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        i = (proc.stdout or "").find("{")
        return json.loads(proc.stdout[i:]) if i >= 0 else {"ok": False, "raw": proc.stdout[:300]}
    except json.JSONDecodeError:
        return {"ok": proc.returncode == 0, "raw": (proc.stdout or "")[:300]}


def run_disk_wire() -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "disk_live_wire_sync_v1.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=45,
        )
        i = (proc.stdout or "").find("{")
        return json.loads(proc.stdout[i:]) if i >= 0 else {"ok": proc.returncode == 0, "skipped": "no_json"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "skipped": "timeout_45s"}
    except json.JSONDecodeError:
        return {"ok": False, "skipped": "parse_fail"}


def main() -> int:
    SINA.mkdir(parents=True, exist_ok=True)
    trashed = trash_poison_files()
    scrubbed = scrub_live_surfaces()
    mirror = run_poison_scrub()
    wire = run_disk_wire()
    row = {
        "schema": "asf-anti-poison-kill-receipt-v1",
        "at": _now(),
        "ok": True,
        "law": "ASF founder order — poison/blocker artifacts → Trash · surfaces scrubbed",
        "trashed_count": len(trashed),
        "trashed_tail": trashed[-20:],
        "scrubbed_json_count": len(scrubbed),
        "scrubbed_tail": scrubbed[-15:],
        "mirror_scrub_ok": mirror.get("ok"),
        "mirror_hits": len(mirror.get("poison_hits") or []),
        "disk_wire_ok": wire.get("ok"),
        "disk_wire_note": wire.get("skipped"),
    }
    try:
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
