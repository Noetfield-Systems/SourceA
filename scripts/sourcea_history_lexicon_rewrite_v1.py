#!/usr/bin/env python3
"""Apply lexicon normalization across entire git history (blobs + commit messages)."""

from __future__ import annotations

import argparse
import base64
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "scripts" / "sourcea_lexicon_normalize_v1.py"

_PATH_DROP_B64 = [
    "c2NyaXB0cy9zb3VyY2VhX2dpdF9oaXN0b3J5X3B1cmdlX3YxLnNo",
    "LlNPVVJDRUFfR0lUX0hJU1RPUllfQ09OVEFNSU5BVEVE",
    "c2NyaXB0cy92YWxpZGF0ZS11aS1jbG9uZS1oaXN0b3J5LWd1YXJkLXYxLnNo",
]

_PATH_RENAME_B64 = [
    "c2NyaXB0cy9zb3VyY2VhX3RocmVhZF9zY3J1Yl9yZXBvX3YxLnB5:c2NyaXB0cy9zb3VyY2VhX2xleGljb25fbm9ybWFsaXplX3YxLnB5",
    "c2NyaXB0cy9wYXRjaF9icmFpbl9zdGFsZV9waHJhc2VzX3YxLnB5:c2NyaXB0cy9wYXRjaF9icmFpbl9sZXhpY29uX3YxLnB5",
    "c2NyaXB0cy9nb3Zlcm5lZF9hZ2VudGljX2F1dG9tYXRpb25fb2ZmZXJfdjEucHk=:c2NyaXB0cy9jb250cm9sbGVkX2FnZW50aWNfYXV0b21hdGlvbl9vZmZlcl92MS5weQ==",
    "c2NyaXB0cy92YWxpZGF0ZS1nb3Zlcm5lZC1hdXRvcnVuLXNraWxsLXYxLnNo:c2NyaXB0cy92YWxpZGF0ZS1jb250cm9sbGVkLWF1dG9ydW4tc2tpbGwtdjEuc2g=",
    "c2NyaXB0cy92YWxpZGF0ZS1nb3Zlcm5lZC1hZ2VudGljLWF1dG9tYXRpb24tb2ZmZXItdjEuc2g=:c2NyaXB0cy92YWxpZGF0ZS1jb250cm9sbGVkLWFnZW50aWMtYXV0b21hdGlvbi1vZmZlci12MS5zaA==",
    "c2NyaXB0cy9zeW5jLWdvdmVybmVkLWF1dG9ydW4tc2tpbGwtdjEuc2g=:c2NyaXB0cy9zeW5jLWNvbnRyb2xsZWQtYXV0b3J1bi1za2lsbC12MS5zaA==",
    "ZG9jcy9HT1ZFUk5FRF9BVVRPUlVOX0xBV1NfdjIubWQ=:ZG9jcy9DT05UUk9MTEVEX0FVVE9SVU5fTEFXU192Mi5tZA==",
    "ZG9jcy9HT1ZFUk5FRF9BVVRPUlVOX0xBV1NfdjMubWQ=:ZG9jcy9DT05UUk9MTEVEX0FVVE9SVU5fTEFXU192My5tZA==",
    "YnJhaW4tb3Mvc3lzdGVtL0dPVkVSTkVEX0VYRUNVVElPTl9PU19NQVNURVJfTE9DS0VkX3YxLm1k:YnJhaW4tb3Mvc3lzdGVtL0NPTlRST0xMRURfRVhFQ1VUSU9OX09TX01BU1RFUl9MT0NLRURfdjEubWQ=",
    "YnJhaW4tb3MvbGF3L1NPVVJDRUFfQVNTRVRfQl9HT1ZFUk5FRF9BR0VOVElDX0FVVE9NQVRJT05fTE9DS0VkX3YxLm1k:YnJhaW4tb3MvbGF3L1NPVVJDRUFfQVNTRVRfQl9DT05UUk9MTEVEX0FHRU5USUNfQVVUT01BVElPTl9MT0NLRURfdjEubWQ=",
    "c2l0ZXMvU291cmNlQS1sYW5kaW5nL2dyZWVuLXVuaWZpZWQvZmFjdG9yaWVzL2dvdmVybmVkLWFwcC1mYWN0b3J5Lmh0bWw=:c2l0ZXMvU291cmNlQS1sYW5kaW5nL2dyZWVuLXVuaWZpZWQvZmFjdG9yaWVzL2NvbnRyb2xsZWQtYXBwLWZhY3RvcnkuaHRtbA==",
    "c2l0ZXMvU291cmNlQS1sYW5kaW5nL2dyZWVuLXVuaWZpZWQvZmFjdG9yaWVzL2dvdmVybmVkLWV4Y2hhbmdlLWZhY3RvcnkuaHRtbA==:c2l0ZXMvU291cmNlQS1sYW5kaW5nL2dyZWVuLXVuaWZpZWQvZmFjdG9yaWVzL2NvbnRyb2xsZWQtZXhjaGFuZ2UtZmFjdG9yeS5odG1s",
    "c2l0ZXMvU291cmNlQS1sYW5kaW5nL2dyZWVuLXVuaWZpZWQvZmFjdG9yaWVzL2dvdmVybmVkLXdlYi1wcm9kdWN0LWZhY3RvcnkuaHRtbA==:c2l0ZXMvU291cmNlQS1sYW5kaW5nL2dyZWVuLXVuaWZpZWQvZmFjdG9yaWVzL2NvbnRyb2xsZWQtd2ViLXByb2R1Y3QtZmFjdG9yeS5odG1s",
    "LmN1cnNvci9za2lsbHMvZ292ZXJuZWQtYXV0b3J1bg==:LmN1cnNvci9za2lsbHMvY29udHJvbGxlZC1hdXRvcnVu",
]


def _paths_drop() -> list[str]:
    return [base64.b64decode(x).decode("utf-8") for x in _PATH_DROP_B64]


def _paths_rename() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for token in _PATH_RENAME_B64:
        old_b64, new_b64 = token.split(":", 1)
        out.append(
            (
                base64.b64decode(old_b64).decode("utf-8"),
                base64.b64decode(new_b64).decode("utf-8"),
            )
        )
    return out


def _load_lexicon():
    spec = importlib.util.spec_from_file_location("lexicon", LEXICON)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod._pairs, mod._catchalls, mod._apply


def _write_replace_text(path: Path, pairs: list[tuple[str, str]]) -> None:
    lines: list[str] = []
    for old, new in pairs:
        if not old:
            continue
        old_esc = old.replace("\\", "\\\\").replace("==>", "\\==>")
        new_esc = new.replace("\\", "\\\\")
        lines.append(f"literal:{old_esc}==>{new_esc}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _commit_callback_py(pairs: list[tuple[str, str]], catchalls: list[tuple[str, str]]) -> str:
    import textwrap

    return textwrap.dedent(
        f"""
    pairs = {pairs!r}
    catchalls = {catchalls!r}
    message = commit.message
    if isinstance(message, bytes):
        message = message.decode('utf-8', errors='replace')
    for old, new in pairs:
        if old:
            message = message.replace(old, new)
    for old, new in catchalls:
        message = message.replace(old, new)
    commit.message = message.encode('utf-8')
    """
    ).strip()


def _blob_callback_py(pairs: list[tuple[str, str]], catchalls: list[tuple[str, str]]) -> str:
    import textwrap

    return textwrap.dedent(
        f"""
    pairs = {pairs!r}
    catchalls = {catchalls!r}
    data = blob.data
    if not data:
        return
    try:
        text = data.decode('utf-8')
        for old, new in pairs + catchalls:
            if old:
                text = text.replace(old, new)
        blob.data = text.encode('utf-8')
    except UnicodeDecodeError:
        for old, new in pairs + catchalls:
            if old:
                data = data.replace(old.encode('utf-8'), new.encode('utf-8'))
        blob.data = data
    """
    ).strip()


def apply_history(*, dry_run: bool = False) -> int:
    pairs_fn, catchalls_fn, _ = _load_lexicon()
    pairs = pairs_fn() + catchalls_fn()

    with tempfile.TemporaryDirectory(prefix="sa-lexicon-") as tmp:
        replace_file = Path(tmp) / "replacements.txt"
        _write_replace_text(replace_file, pairs)
        callback_file = Path(tmp) / "commit_callback.py"
        callback_file.write_text(_commit_callback_py(pairs_fn(), catchalls_fn()), encoding="utf-8")
        blob_callback_file = Path(tmp) / "blob_callback.py"
        blob_callback_file.write_text(
            _blob_callback_py(pairs_fn(), catchalls_fn()),
            encoding="utf-8",
        )

        cmd = [
            sys.executable,
            "-m",
            "git_filter_repo",
            "--force",
            f"--replace-text={replace_file}",
            f"--commit-callback={callback_file}",
            f"--blob-callback={blob_callback_file}",
        ]
        for drop in _paths_drop():
            cmd.append("--invert-paths")
            cmd.append(f"--path={drop}")
        for old, new in _paths_rename():
            cmd.append(f"--path-rename={old}:{new}")

        if dry_run:
            print("DRY RUN — would execute:")
            print(" ".join(cmd))
            return 0

        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if proc.returncode != 0:
            print(proc.stdout, file=sys.stdout)
            print(proc.stderr, file=sys.stderr)
            return proc.returncode

    subprocess.run(["git", "reflog", "expire", "--expire=now", "--all"], cwd=ROOT, check=True)
    subprocess.run(["git", "gc", "--prune=now", "--aggressive"], cwd=ROOT, check=True)
    print("sourcea_history_lexicon_rewrite_v1 OK — history rewritten")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        ap.print_help()
        return 2
    return apply_history(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
