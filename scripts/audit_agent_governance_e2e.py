#!/usr/bin/env python3
"""E2E governance audit — registry, disk, packs, edit lock, readonly rules, copy."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))

from agent_command_reviews import ALLOWED_EDIT_WORKSPACES, _load_lock_manifest  # noqa: E402
from agent_private_workspaces import WORKSPACES_ROOT, ensure_all_workspaces  # noqa: E402
from agent_workspace_registry import AGENT_WORKSPACES, GOVERNANCE_VERSION  # noqa: E402
from loop_pack_registry import PACKS, resolve_noetfield_local_root  # noqa: E402

STALE_PHRASE = "Agent loop tab"
STALE_SCAN_DIRS = (SOURCE_A / "scripts", SOURCE_A)
STALE_ALLOWLIST = {
    "command_audit_backlog.py",
    "audit_agent_governance_e2e.py",
}
STALE_EXCLUDE_GLOBS = ("command-data.json", "index.html", "agent-transcripts")

# Agents whose repo_root is SourceA — no repo-root sina-command-readonly (private rules only)
REPO_ROOT_READONLY_SKIP = frozenset({"semej"})
# Portfolio repos optional on disk — skip repo/pack hard-fail when absent (Wave 0)
OPTIONAL_REPO_AGENTS = frozenset({"semej", "noetfield_local"})


def _stale_hits() -> list[str]:
    hits = []
    for base in STALE_SCAN_DIRS:
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(x in p.name for x in STALE_EXCLUDE_GLOBS):
                continue
            if p.suffix not in (".py", ".md", ".mdc", ".html"):
                continue
            if p.name in STALE_ALLOWLIST:
                continue
            if "agent-control-panel" in p.parts and p.name in ("command-data.json", "index.html"):
                continue
            if "archive" in p.parts:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if STALE_PHRASE in text:
                rel = p.relative_to(SOURCE_A)
                hits.append(str(rel))
    return hits


def main() -> int:
    errors: list[str] = []
    ensure_all_workspaces()

    if len(AGENT_WORKSPACES) != 7:
        errors.append(f"registry count {len(AGENT_WORKSPACES)} != 7")

    if any(w.get("may_edit_source_a") for w in AGENT_WORKSPACES):
        errors.append("no registered agent may_edit_source_a — hub edits: SinaaiDataBase workspace only (SINA_COMMAND_EDIT_LOCK)")

    law_path = SOURCE_A / "SINA_AGENT_PRIVATE_WORKSPACES_LOCKED_v1.md"
    if law_path.is_file():
        law = law_path.read_text(encoding="utf-8")
        for spec in AGENT_WORKSPACES:
            if f"| {spec['id']} |" not in law and f"`{spec['id']}`" not in law:
                if spec["id"] not in law:
                    errors.append(f"law table missing id: {spec['id']}")

    nf_local = resolve_noetfield_local_root()
    nf_cloud = PACKS["noetfield_cloud"]["root"]
    for spec in AGENT_WORKSPACES:
        aid = spec["id"]
        repo = Path(spec["repo_root"])
        priv = WORKSPACES_ROOT / aid

        if not repo.is_dir() and aid not in OPTIONAL_REPO_AGENTS:
            errors.append(f"missing repo_root: {aid} → {repo}")

        for name in ("GOVERNANCE_LOCKED.md", "manifest.json"):
            if not (priv / name).is_file():
                errors.append(f"missing {name}: {aid}")

        mdc = priv / ".cursor" / "rules" / "workspace-governance.mdc"
        if not mdc.is_file():
            errors.append(f"missing private governance mdc: {aid}")

        try:
            manifest = json.loads((priv / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("governance_version") != GOVERNANCE_VERSION:
                errors.append(f"{aid}: manifest governance_version != {GOVERNANCE_VERSION}")
        except (json.JSONDecodeError, OSError):
            errors.append(f"{aid}: invalid manifest.json")

        if aid not in REPO_ROOT_READONLY_SKIP and repo.is_dir():
            marker = repo / ".sina-agent" / "README.md"
            if not marker.is_file():
                errors.append(f"missing .sina-agent/README.md: {aid}")
            if not spec.get("may_edit_source_a"):
                root_rule = repo / ".cursor" / "rules" / "sina-command-readonly.mdc"
                if not root_rule.is_file():
                    errors.append(f"missing repo-root sina-command-readonly.mdc: {aid}")

        if aid == "semej":
            forb = spec.get("forbidden_roots") or []
            if not any("SourceA" in p or "sourceA" in p for p in forb):
                errors.append("semej: forbidden_roots must include SourceA")

        pid = spec.get("pack_id")
        if pid:
            pack_meta = PACKS.get(pid)
            if not pack_meta:
                errors.append(f"unknown pack_id: {pid}")
            else:
                pack_file = Path(pack_meta["root"]) / pack_meta["pack"]
                if not pack_file.is_file() and repo.is_dir():
                    errors.append(f"missing pack file: {aid} → {pack_file}")

    local_spec = next(w for w in AGENT_WORKSPACES if w["id"] == "noetfield_local")
    cloud_spec = next(w for w in AGENT_WORKSPACES if w["id"] == "noetfield_cloud")
    if str(nf_cloud) not in (local_spec.get("forbidden_roots") or []):
        errors.append("noetfield_local must forbid cloud root")
    if str(nf_local) not in (cloud_spec.get("forbidden_roots") or []):
        errors.append("noetfield_cloud must forbid local root")

    lock = _load_lock_manifest()
    allowed = frozenset(lock.get("allowed_edit_workspaces") or [])
    if allowed != ALLOWED_EDIT_WORKSPACES:
        errors.append(f"edit lock allowed workspaces mismatch: {allowed}")

    stale = _stale_hits()
    for rel in stale[:15]:
        errors.append(f"stale phrase '{STALE_PHRASE}' in {rel}")
    if len(stale) > 15:
        errors.append(f"... and {len(stale) - 15} more stale files")

    import subprocess

    priv_audit = SOURCE_A / "scripts" / "audit_private_agent_pages.py"
    if priv_audit.is_file():
        r = subprocess.run([sys.executable, str(priv_audit)], cwd=str(SOURCE_A / "scripts"))
        if r.returncode != 0:
            errors.append("audit_private_agent_pages.py failed")

    if errors:
        print("GOVERNANCE AUDIT FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: governance E2E · {len(AGENT_WORKSPACES)} agents · v{GOVERNANCE_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
