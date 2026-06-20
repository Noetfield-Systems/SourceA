#!/usr/bin/env python3
"""Repair SinaPromptOS rejected inbox YAML (missing next_action) and re-ingest — clears B-001."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PROMPTOS = Path("/Users/sinakazemnezhad/Desktop/SinaPromptOS")
REJECTED = PROMPTOS / "outputs" / "inbox" / "rejected"


def _extract_yaml(text: str) -> str | None:
    m = re.search(r"```yaml\s*\n(.*?)```", text, re.DOTALL | re.I)
    if m:
        return m.group(1).strip()
    if "repo:" in text:
        idx = text.index("repo:")
        return text[idx:].strip()
    return None


def _repo_from_yaml(chunk: str) -> str:
    m = re.search(r"^repo:\s*(\S+)", chunk, re.M)
    return m.group(1).strip() if m else ""


def repair_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    chunk = _extract_yaml(raw)
    if not chunk:
        return {"ok": False, "file": str(path), "error": "no_yaml"}
    if "next_action:" not in chunk:
        chunk = chunk.rstrip() + "\nnext_action: \"\"\n"
    repo = _repo_from_yaml(chunk)
    if not repo:
        return {"ok": False, "file": str(path), "error": "no_repo"}
    sys.path.insert(0, str(PROMPTOS))
    from core.yaml_ingest import ingest_cursor_reply  # noqa: WPS433

    reply = raw.split("```yaml")[0] + "```yaml\n" + chunk + "\n```"
    result = ingest_cursor_reply(repo, reply, mark_done_after=True, refresh_cycle=False)
    ok = bool(result.get("ok"))
    if ok:
        path.unlink(missing_ok=True)
    return {"ok": ok, "file": path.name, "repo": repo, "result": result}


def main() -> int:
    if not REJECTED.is_dir():
        print("OK: no rejected dir")
        return 0
    rows = []
    ok_all = True
    for path in sorted(REJECTED.glob("*.txt")):
        row = repair_file(path)
        rows.append(row)
        ok_all = ok_all and row.get("ok")
        print(f"{'OK' if row.get('ok') else 'FAIL'}: {path.name} repo={row.get('repo')} err={row.get('error','')}")
    repaired = sum(1 for r in rows if r.get("ok"))
    print(f"SUMMARY: repaired={repaired}/{len(rows)} ok_all={ok_all}")
    return 0 if ok_all or not rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
