#!/usr/bin/env python3
"""Close backlog tasks when REGISTRY verify PASS — receipt + registry_updater only.

Skips batch-stamp YAML. No REGISTRY inflate without machine pass.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
LOGS = ROOT / "REPO_EXECUTION_LOGS/sourcea"
LOG = Path.home() / ".sina/reconcile-1000-machine-pass-v1.jsonl"

BATCH_SNIPPETS = (
    "pack30 commercial+pre-llm verify-only",
    "wire+dispatch+hub PASS",
    "validators+batch PASS",
    "pack15 spine-loop",
    "pack12 spine-loop",
    "pack18 spine-loop",
    "pack14 spine-loop",
    "pack26 commercial",
    "pack27 commercial",
)

PHASE_ORDER = (
    "phase-s0-ssot-alignment",
    "phase-s1-eval-dispatch",
    "phase-s2-hub-build-ci",
    "phase-s3-scoreboard-fleet",
    "phase-s4-spine-loop",
    "phase-s6-wtm-pre-llm",
    "phase-s5-commercial-lanes",
    "phase-s7-council-governance",
    "phase-s8-hub-ui-ux",
    "phase-s9-research-models",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _yaml_is_batch(sa: str) -> bool:
    for p in LOGS.glob(f"*{sa}*.yaml"):
        if "plan-with-no-asf" not in p.name:
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"reporter: cursor-worker-batch", t):
            return True
        m = re.search(r"output_snippet: (.+)", t)
        if m and any(b in m.group(1) for b in BATCH_SNIPPETS):
            return True
    return False


def _run_verify(cmd: str, *, timeout: int) -> tuple[bool, str]:
    if not cmd.strip():
        return False, "no_verify"
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == 0 and "FAIL" not in out.upper().split("OK:")[0][-200:]
    return ok, out[-400:]


def reconcile(*, limit: int = 25, phase: str = "", dry_run: bool = False, timeout: int = 120) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from worker_receipt_v1 import write_receipt  # noqa: WPS433

    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = reg.get("plans") or []
    honest = set()
    try:
        from registry_honest_lib_v1 import honest_receipt_ids  # noqa: WPS433

        honest = honest_receipt_ids()
    except Exception:
        pass

    order = {ph: i for i, ph in enumerate(PHASE_ORDER)}
    candidates = [
        p
        for p in plans
        if p.get("status") == "backlog"
        and p.get("id", "").startswith("sa-")
        and p.get("id") not in honest
        and p.get("verify")
        and not _yaml_is_batch(p.get("id", ""))
    ]
    if phase:
        candidates = [p for p in candidates if p.get("phase") == phase]
    candidates.sort(key=lambda p: (order.get(p.get("phase") or "", 99), p.get("id") or ""))

    closed: list[str] = []
    skipped: list[dict] = []
    for pl in candidates[: max(1, limit)]:
        sa = pl["id"]
        verify = str(pl.get("verify") or "")
        ok, tail = _run_verify(verify, timeout=timeout)
        if not ok:
            skipped.append({"sa_id": sa, "reason": "verify_fail", "tail": tail[-120:]})
            continue
        evidence = f"reconcile-1000-machine-pass: {verify[:200]} · PASS · {tail[-120:]}"
        if dry_run:
            closed.append(sa)
            continue
        rec = write_receipt(
            sa_id=sa,
            round_type="verify",
            evidence=evidence,
            source="reconcile_1000_machine_pass_v1",
            engine="MACHINE",
        )
        if not rec.get("ok"):
            skipped.append({"sa_id": sa, "reason": "receipt_fail", "error": rec.get("error")})
            continue
        closed.append(sa)
        _log({"sa_id": sa, "verify": verify[:120], "evidence": evidence[:200]})

    if closed and not dry_run:
        import importlib.util

        spec = importlib.util.spec_from_file_location("ru", ROOT / "scripts/registry_updater_v1.py")
        ru = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ru)  # type: ignore[union-attr]
        ru.run(dry_run=False)

    after = {}
    try:
        from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

        after = audit_registry_done()
    except Exception:
        pass

    return {
        "ok": True,
        "dry_run": dry_run,
        "closed": closed,
        "closed_count": len(closed),
        "skipped_count": len(skipped),
        "skipped_sample": skipped[:10],
        "honest_done_after": after.get("honest_done"),
        "limit": limit,
        "phase": phase or "all",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--phase", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    out = reconcile(limit=args.limit, phase=args.phase, dry_run=args.dry_run, timeout=args.timeout)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
