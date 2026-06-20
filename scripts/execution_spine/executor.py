"""Subprocess execution runner."""
from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from execution_spine.types import TaskSpec

SOURCE_A = Path(__file__).resolve().parents[2]
PROMPTOS_ROOT = Path.home() / "Desktop" / "SinaPromptOS"


@dataclass
class RawResult:
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    input_command: str


def run_task(task: TaskSpec) -> RawResult:
    kind = task.kind
    payload = task.payload
    t0 = time.perf_counter()

    if kind == "one_click":
        root = Path(payload.get("promptos_root", PROMPTOS_ROOT))
        script = root / "scripts/one-click.sh"
        action = payload["action"]
        cmd = ["bash", str(script), action]
        proc = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=int(payload.get("timeout", 300)),
        )
        input_command = " ".join(shlex.quote(c) for c in cmd)

    elif kind == "shell":
        cwd = Path(payload["cwd"]).expanduser()
        argv = payload["argv"]
        proc = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=int(payload.get("timeout", 120)),
        )
        input_command = " ".join(shlex.quote(str(a)) for a in argv)

    elif kind == "brief":
        script = SOURCE_A / "scripts/sina-morning-brief.sh"
        lang = payload.get("lang", "en")
        cmd = ["bash", str(script), lang]
        proc = subprocess.run(
            cmd,
            cwd=SOURCE_A,
            capture_output=True,
            text=True,
            timeout=int(payload.get("timeout", 120)),
        )
        input_command = " ".join(shlex.quote(c) for c in cmd)

    elif kind == "ingest_clipboard":
        root = Path(payload.get("promptos_root", PROMPTOS_ROOT))
        repo = payload["repo"]
        script = root / "scripts/ingest-clipboard.sh"
        cmd = ["bash", str(script), repo]
        proc = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=int(payload.get("timeout", 120)),
        )
        input_command = " ".join(shlex.quote(c) for c in cmd)

    else:
        raise ValueError(f"unsupported execution kind: {kind}")

    elapsed = int((time.perf_counter() - t0) * 1000)
    return RawResult(
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        exit_code=proc.returncode,
        execution_time_ms=elapsed,
        input_command=input_command,
    )
