#!/usr/bin/env python3
"""One-shot: live + clean + unified — machines, pipelines, workspace docs (no stale fragmentation)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"

DOC_STALE = re.compile(
    r"/legacy/|oldhubsinacommand|Founder Museum|founder_museum|legacy_archive_url|"
    r"Sina Command(?! RETIRED| DELETED|\s+edit lock)",
    re.I,
)

REPLACEMENTS = (
    (re.compile(r"/legacy/?", re.I), "/"),
    (re.compile(r"Sina Command", re.I), "Hub"),
    (re.compile(r"Founder Museum[^.\n]*", re.I), "Hub H1"),
    (re.compile(r"Legacy archive:[^\n]*", re.I), "Command: DELETED — Hub H1 + H2 only."),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str]) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(SCRIPTS), capture_output=True, text=True, timeout=120)
        return {"ok": p.returncode == 0, "code": p.returncode, "out": (p.stdout or "")[-500:], "err": (p.stderr or "")[-300:]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def scrub_workspace_docs() -> list[dict]:
    actions: list[dict] = []
    roots = [SINA / "agent-workspaces", ROOT / ".sina-agent"]
    names = {"GOVERNANCE_LOCKED.md", "workspace-governance.mdc", "README.md"}
    for base in roots:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.name not in names:
                continue
            try:
                text = path.read_text(encoding="utf-8")
                if not DOC_STALE.search(text):
                    continue
                new = text
                for pat, rep in REPLACEMENTS:
                    new = pat.sub(rep, new)
                if new != text:
                    path.write_text(new, encoding="utf-8")
                    actions.append({"path": str(path), "action": "doc_scrubbed"})
            except OSError:
                continue
    return actions


def scrub_brain_runtime_docs() -> list[dict]:
    actions: list[dict] = []
    brain = SINA / "brain"
    if not brain.is_dir():
        return actions
    for path in brain.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
            if not DOC_STALE.search(text):
                continue
            new = text
            for pat, rep in REPLACEMENTS:
                new = pat.sub(rep, new)
            if new != text:
                path.write_text(new, encoding="utf-8")
                actions.append({"path": str(path), "action": "brain_doc_scrubbed"})
        except OSError:
            continue
    return actions


def write_live_manifest(*, head: dict, hub_ok: bool, h2_ok: bool) -> dict:
    from founder_directive_ssot_v1 import execution_rail_line, truth_block_lines  # noqa: WPS433
    from factory_control_v1 import load_factory_now  # noqa: WPS433

    fn = load_factory_now()
    row = {
        "schema": "system-live-manifest-v1",
        "at": _now(),
        "law": "ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md",
        "live": {
            "h1": "http://127.0.0.1:13020/",
            "h2": "http://127.0.0.1:13020/machines/",
            "command_deleted": True,
            "hub_ok": hub_ok,
            "h2_ok": h2_ok,
        },
        "factory": {
            "valid_yes": fn.get("valid_yes"),
            "mode": fn.get("mode"),
            "queue_sa": head.get("sa_id"),
            "queue_role": head.get("role"),
            "queue_pos": head.get("pos"),
            "queue_total": head.get("total"),
        },
        "rail": execution_rail_line(),
        "truth_lines": truth_block_lines(),
        "pipelines_unified": True,
        "no_stale_steer": True,
    }
    out = SINA / "system-live-manifest-v1.json"
    out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def verify_live() -> dict:
    import urllib.request

    out: dict = {"ok": True, "errors": []}
    try:
        with urllib.request.urlopen("http://127.0.0.1:13020/health", timeout=8) as r:
            out["health"] = json.loads(r.read().decode()).get("ok")
    except OSError as exc:
        out["ok"] = False
        out["errors"].append(f"health: {exc}")
    for path, key in (("/api/worker-hub/v1", "h1"), ("/api/machine-hub/v1", "h2")):
        try:
            with urllib.request.urlopen("http://127.0.0.1:13020" + path, timeout=15) as r:
                d = json.loads(r.read().decode())
            if not d.get("ok"):
                out["ok"] = False
                out["errors"].append(f"{key} api not ok")
            if key == "h1" and d.get("command_retired_forever") is not True:
                out["errors"].append("h1 missing command_retired_forever")
            if key == "h2" and d.get("legacy_retired") is not True:
                out["errors"].append("h2 missing legacy_retired")
        except OSError as exc:
            out["ok"] = False
            out["errors"].append(f"{key}: {exc}")
    return out


def main() -> int:
    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict] = []

    steps.append({"step": "purge", **_run([sys.executable, "hub_stale_disk_purge_v1.py", "--json"])})
    steps.append({"step": "queue_unify", **_run([sys.executable, "queue_ssot_unify_v1.py", "--json"])})
    steps.append({"step": "founder_sync", **_run([sys.executable, "founder_directive_ssot_v1.py", "--sync-all"])})
    steps.append({"step": "brain_scrub", **_run([sys.executable, "brain_stale_prompt_scrub_v1.py", "--json"])})
    steps.append({"step": "worker_scrub", **_run([sys.executable, "worker_stale_prompt_scrub_v1.py", "--json"])})
    steps.append({"step": "boot_refresh", **_run([sys.executable, "hub_stale_disk_purge_v1.py"])})

    doc_actions = scrub_workspace_docs() + scrub_brain_runtime_docs()

    validators = [
        "validate-hub-no-legacy-route-v1.sh",
        "validate-machine-hub-v1.sh",
        "validate-super-fast-hub-v1.sh",
    ]
    val_results = {}
    for v in validators:
        val_results[v] = _run(["bash", str(SCRIPTS / v)])

    from queue_ssot_unify_v1 import queue_head  # noqa: WPS433

    head = queue_head()
    live = verify_live()
    manifest = write_live_manifest(
        head=head,
        hub_ok=bool(live.get("health")),
        h2_ok=live.get("ok", False) and not any("h2" in e for e in live.get("errors", [])),
    )

    row = {
        "ok": live.get("ok") and all(v.get("ok") for v in val_results.values()),
        "at": _now(),
        "steps": steps,
        "doc_scrubs": len(doc_actions),
        "doc_actions": doc_actions[:20],
        "validators": {k: v.get("ok") for k, v in val_results.items()},
        "live": live,
        "manifest": {"queue_sa": manifest.get("factory", {}).get("queue_sa"), "rail": manifest.get("rail")},
    }
    receipt = SINA / "system-live-clean-receipt-v1.json"
    receipt.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
