#!/usr/bin/env python3
"""Forge Execution Mesh v1 — parallel builder job dispatch."""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable


def _default_workers() -> int:
    """Mac control plane: cap at 2; cloud may override via env."""
    try:
        cap = int(os.environ.get("FORGE_MESH_WORKERS", "2"))
    except ValueError:
        cap = 2
    return max(1, min(cap, 8))


def execute_mesh(
    jobs: list[dict[str, Any]],
    *,
    run_fn: Callable[[dict[str, Any]], dict[str, Any]],
    max_workers: int | None = None,
) -> list[dict[str, Any]]:
    """Run builder jobs in parallel; preserve input order in results."""
    if not jobs:
        return []
    workers = max_workers or _default_workers()
    if workers <= 1 or len(jobs) == 1:
        return [run_fn(j) for j in jobs]

    indexed: dict[int, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(workers, len(jobs))) as pool:
        futs = {pool.submit(run_fn, job): i for i, job in enumerate(jobs)}
        for fut in as_completed(futs):
            idx = futs[fut]
            try:
                indexed[idx] = fut.result()
            except Exception as exc:
                indexed[idx] = {"ok": False, "error": str(exc)[:120], "job_index": idx}
    return [indexed[i] for i in range(len(jobs))]
