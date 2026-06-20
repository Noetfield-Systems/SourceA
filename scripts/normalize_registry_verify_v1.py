#!/usr/bin/env python3
"""Bulk-normalize sa verify lines in REGISTRY + healthy queue + prompt .md → ultra verify."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
QUEUE = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
PROMPTS = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts"


def _normalize(verify: str | None) -> tuple[str, bool]:
    sys.path.insert(0, str(SCRIPTS))
    from worker_verify_normalize_v1 import normalize_worker_verify  # noqa: WPS433

    raw = (verify or "").strip()
    out = normalize_worker_verify(raw, role="verify")
    return out, out != raw


def patch_registry(*, dry_run: bool = False) -> dict:
    data = json.loads(REG.read_text(encoding="utf-8"))
    changed = 0
    for pl in data.get("plans") or []:
        v = pl.get("verify")
        if not v:
            continue
        out, diff = _normalize(str(v))
        if diff:
            pl["verify"] = out
            changed += 1
    if changed and not dry_run:
        REG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"file": str(REG), "changed": changed}


def patch_queue(*, dry_run: bool = False) -> dict:
    if not QUEUE.is_file():
        return {"file": str(QUEUE), "changed": 0, "skipped": True}
    data = json.loads(QUEUE.read_text(encoding="utf-8"))
    changed = 0
    for row in data.get("queue") or []:
        v = row.get("verify")
        if not v:
            continue
        out, diff = _normalize(str(v))
        if diff:
            row["verify"] = out
            changed += 1
    if changed and not dry_run:
        QUEUE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"file": str(QUEUE), "changed": changed}


def patch_prompt_mds(*, dry_run: bool = False) -> dict:
    changed = 0
    for md in PROMPTS.rglob("sa-*.md"):
        text = md.read_text(encoding="utf-8")
        if "find_critical_bugs.py" not in text and "validate-anti-staleness-bundle" not in text:
            continue

        def _repl(m: re.Match[str]) -> str:
            body = m.group(2).strip()
            out = _normalize(body)[0]
            return f"{m.group(1)}{out}\n{m.group(3)}"

        new_text, n = re.subn(
            r"(## Verify\s*\n+```bash\s*\n)(.*?)(```)",
            _repl,
            text,
            count=1,
            flags=re.DOTALL,
        )
        if n and new_text != text:
            changed += 1
            if not dry_run:
                md.write_text(new_text, encoding="utf-8")
    return {"dir": str(PROMPTS), "changed": changed}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Normalize registry verify lines to ultra lane")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    reg = patch_registry(dry_run=args.dry_run)
    que = patch_queue(dry_run=args.dry_run)
    mds = patch_prompt_mds(dry_run=args.dry_run)
    row = {"ok": True, "registry": reg, "queue": que, "prompts": mds}
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"REGISTRY changed={reg['changed']} queue changed={que.get('changed', 0)} "
            f"prompts changed={mds.get('changed', 0)} dry_run={args.dry_run}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
