#!/usr/bin/env python3
"""Chat Unify — unified run kernel (state SSOT between sequential stages).

Receipt: ~/.sina/chat-unify-kernels/<run_id>.json
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
KERNEL_DIR = SINA / "chat-unify-kernels"
KERNEL_VERSION = "1.1.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id(prefix: str = "cu") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def kernel_path(run_id: str) -> Path:
    safe = "".join(c for c in run_id if c.isalnum() or c in "-_")
    return KERNEL_DIR / f"{safe}.json"


def empty_kernel(
    *,
    loop: str,
    raw_input: str,
    founder_message: str = "",
    run_id: str | None = None,
    ord_run_id: str | None = None,
    parent_run_id: str | None = None,
) -> dict:
    rid = run_id or new_run_id("cu" if loop == "founder" else "ord")
    now = _now()
    return {
        "schema": "chat-unify-kernel-v1",
        "version": KERNEL_VERSION,
        "run_id": rid,
        "loop": loop,
        "parent_run_id": parent_run_id,
        "ord_run_id": ord_run_id,
        "created_at": now,
        "updated_at": now,
        "raw_input": raw_input,
        "founder_message": founder_message,
        "stages": {},
        "trace": {
            "execution_plane": "mac_hub",
            "model_used": [],
            "worker_id": None,
            "prompt_id": None,
            "provider": None,
        },
        "atoms": [],
        "graph": {"nodes": [], "edges": []},
        "disk_bindings": [],
        "stage_log": [],
        "truth_score": None,
        "decision": None,
    }


def load_kernel(run_id: str) -> dict | None:
    path = kernel_path(run_id)
    if not path.is_file():
        return None
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if row.get("schema") != "chat-unify-kernel-v1":
        return None
    return row


def save_kernel(kernel: dict) -> Path:
    KERNEL_DIR.mkdir(parents=True, exist_ok=True)
    kernel["updated_at"] = _now()
    path = kernel_path(kernel["run_id"])
    path.write_text(json.dumps(kernel, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def append_stage_log(
    kernel: dict,
    *,
    stage: str,
    depends_on: str | None,
    ok: bool,
    method: str | None = None,
    extra: dict | None = None,
) -> None:
    entry: dict[str, Any] = {
        "at": _now(),
        "stage": stage,
        "depends_on": depends_on,
        "ok": ok,
        "method": method,
    }
    if extra:
        entry.update(extra)
    kernel.setdefault("stage_log", []).append(entry)


def record_model(kernel: dict, *, provider: str, method: str | None = None) -> None:
    trace = kernel.setdefault("trace", {})
    models = trace.setdefault("model_used", [])
    tag = method or provider
    if tag and tag not in models:
        models.append(tag)
    trace["provider"] = provider


def merge_stage_output(kernel: dict, stages: dict) -> None:
    kernel["stages"] = dict(stages)


def bind_disk_snapshots(kernel: dict, disk: dict) -> None:
    if not disk:
        return
    bindings = kernel.setdefault("disk_bindings", [])
    for path in disk.get("paths_checked") or []:
        row = {"path": path, "bound_at": _now()}
        if row not in bindings:
            bindings.append(row)


def set_decision(kernel: dict, decision: dict) -> None:
    kernel["decision"] = decision
    if decision.get("truth_score") is not None:
        kernel["truth_score"] = decision.get("truth_score")


def ensure_kernel(
    *,
    loop: str,
    draft: str,
    founder_message: str = "",
    run_id: str | None = None,
    ord_run_id: str | None = None,
    kernel: dict | None = None,
) -> dict:
    if run_id:
        loaded = load_kernel(run_id)
        if loaded:
            if ord_run_id and not loaded.get("ord_run_id"):
                loaded["ord_run_id"] = ord_run_id
            return loaded
    if kernel and kernel.get("schema") == "chat-unify-kernel-v1" and kernel.get("run_id"):
        return kernel
    return empty_kernel(
        loop=loop,
        raw_input=draft,
        founder_message=founder_message,
        run_id=run_id,
        ord_run_id=ord_run_id,
    )


def set_atoms(kernel: dict, atoms: list) -> None:
    kernel["atoms"] = list(atoms or [])


def set_graph(kernel: dict, graph: dict) -> None:
    kernel["graph"] = graph or {"nodes": [], "edges": []}


def kernel_summary(kernel: dict) -> dict:
    stats = {}
    try:
        from chat_ord_atoms_v1 import atom_stats  # noqa: WPS433

        stats = atom_stats(kernel.get("atoms") or [], kernel.get("graph") or {})
    except ImportError:
        stats = {"atom_count": len(kernel.get("atoms") or [])}
    return {
        "run_id": kernel.get("run_id"),
        "loop": kernel.get("loop"),
        "ord_run_id": kernel.get("ord_run_id"),
        "stage_count": len(kernel.get("stage_log") or []),
        "truth_score": kernel.get("truth_score"),
        "decision_action": (kernel.get("decision") or {}).get("action"),
        "atom_count": stats.get("atom_count", 0),
        "verified": stats.get("verified", 0),
        "disk_mismatch": stats.get("disk_mismatch", 0),
        "contradictions": stats.get("contradictions", 0),
        "kernel_path": str(kernel_path(kernel["run_id"])) if kernel.get("run_id") else None,
    }
