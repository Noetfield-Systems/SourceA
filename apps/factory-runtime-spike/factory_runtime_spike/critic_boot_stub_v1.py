"""SourceA critic boot stub — PASS/BLOCK pre-flight for runtime spike (no hub)."""
from __future__ import annotations

from factory_runtime_spike.types_v1 import FORBIDDEN_PROMPT_MARKERS, JobInput, utc_now


def run_critic_boot_stub(job: JobInput) -> dict:
    """Mode A pre-flight — blocks forbidden factory vocabulary before agent embed."""
    reasons: list[str] = []
    for marker in FORBIDDEN_PROMPT_MARKERS:
        if marker in job.prompt:
            reasons.append(f"forbidden_marker:{marker}")
    verdict = "BLOCK" if reasons else "PASS"
    return {
        "schema": "sourcea-critic-boot-stub-v1",
        "verdict": verdict,
        "reasons": reasons,
        "job_id": job.job_id,
        "at": utc_now(),
    }
