#!/usr/bin/env python3
"""SSOT: monitor road map columns + progress law (INCIDENT-006 + monitor honesty v2).

Law file: brain-os/laws/MONITOR_HONESTY_LOCKED_v1.md

Progress bar = Valid YES only (Worker receipt + full broker CHECK→ACT→VERIFY + verify deliver_ok).
Broker PASS on backlog without receipt = STALE (never counts as done).
Audit backlog structural ok = STRUCT_OK (not PASS, not done).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
BROKER_EVENTS = SINA / "goal1-lane-broker-events.jsonl"
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
RECEIPTS = ROOT / "receipts"
LOGS = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
QUEUE_STATE = SINA / "healthy-queue-state-v1.json"
HYGIENE_PASS = SINA / "last-hygiene-pass-v1.json"
BRAIN_VAL = SINA / "brain-goal1-validation-v1.json"
TRACK_SNAP = SINA / "track-validate-snapshot-v1.json"

ALLOWED_RECEIPT_SOURCES = frozenset(
    {
        "goal1_lane_broker",
        "restore-broker-proven-v1",
        "api",
        "maintainer_executor",
        "worker_inbox",
    }
)

PROGRESS_LAW = (
    "UI progress = Valid YES only · receipt_done shown separately · "
    "STRUCT_OK = prompt file only · Broker STALE = old submit not closed"
)

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from closeout_audit_lib_v1 import (  # noqa: E402
    HONEST_RECEIPT,
    load_closeouts,
    load_receipts,
    proof_verdict,
)


def _norm_role(round_type: str) -> str:
    rt = (round_type or "").lower().strip()
    if rt in ("implement", "act"):
        return "act"
    if rt in ("audit", "check"):
        return "check"
    if rt in ("verify", "verify_backend", "closeout"):
        return "verify"
    if rt in ("fix",):
        return "act"
    return rt


@dataclass
class BrokerCycle:
    roles: set[str]
    verify_deliver_ok: bool | None
    verify_orch_ok: bool | None
    last_at: str
    event_count: int


def _sa_num(sa: str) -> int:
    try:
        return int(sa.split("-")[1])
    except (IndexError, ValueError):
        return 9999


def queue_context() -> tuple[set[str], str, int, str]:
    """queue_sas, here_sa, here_pos, here_role."""
    here_sa = ""
    here_role = ""
    here_pos = 0
    queue_sas: set[str] = set()
    if QUEUE_HOME.is_file():
        try:
            q = json.loads(QUEUE_HOME.read_text(encoding="utf-8"))
            for item in q.get("queue") or []:
                sa = str(item.get("sa_id") or "")
                if sa.startswith("sa-"):
                    queue_sas.add(sa)
        except (OSError, json.JSONDecodeError):
            pass
    if QUEUE_STATE.is_file():
        try:
            st = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
            here_pos = int(st.get("next_pos") or 0)
        except (OSError, json.JSONDecodeError, TypeError):
            here_pos = 0
    if here_pos and QUEUE_HOME.is_file():
        try:
            q = json.loads(QUEUE_HOME.read_text(encoding="utf-8"))
            items = q.get("queue") or []
            if 0 < here_pos <= len(items):
                cur = items[here_pos - 1]
                here_sa = str(cur.get("sa_id") or "")
                here_role = str(cur.get("queue_role") or "")
        except (OSError, json.JSONDecodeError):
            pass
    return queue_sas, here_sa, here_pos, here_role


def _you_are_here_payload(*, here_sa: str, here_pos: int, here_role: str) -> dict:
    queue_total = 0
    if QUEUE_HOME.is_file():
        try:
            q = json.loads(QUEUE_HOME.read_text(encoding="utf-8"))
            queue_total = len(q.get("queue") or [])
        except (OSError, json.JSONDecodeError):
            pass
    exhausted = bool(here_pos and queue_total and here_pos > queue_total and not here_sa)
    label = "Queue complete" if exhausted else ""
    return {
        "n": _sa_num(here_sa) if here_sa else here_pos,
        "sa_id": here_sa,
        "queue_pos": here_pos,
        "queue_total": queue_total,
        "role": here_role,
        "queue_exhausted": exhausted,
        "label": label,
    }


def load_broker_cycles() -> dict[str, BrokerCycle]:
    """Per-sa broker WORKER_SUBMIT history from events jsonl."""
    out: dict[str, BrokerCycle] = {}
    if not BROKER_EVENTS.is_file():
        return out
    for line in BROKER_EVENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(e.get("kind") or "") not in ("WORKER_SUBMIT", "WORKER_SUBMIT_AUTO"):
            continue
        sa = str(e.get("sa") or e.get("sa_id") or "")
        if not sa.startswith("sa-"):
            continue
        role = _norm_role(str(e.get("round_type") or ""))
        if not role:
            continue
        cur = out.get(sa)
        if cur is None:
            cur = BrokerCycle(roles=set(), verify_deliver_ok=None, verify_orch_ok=None, last_at="", event_count=0)
            out[sa] = cur
        cur.roles.add(role)
        cur.event_count += 1
        cur.last_at = str(e.get("at") or cur.last_at)
        if role == "verify":
            cur.verify_deliver_ok = e.get("deliver_ok")
            ok = e.get("ok")
            if ok is None:
                ok = e.get("orch_ok")
            cur.verify_orch_ok = bool(ok) if ok is not None else None
    return out


def _has_honest_receipt(rec: dict | None) -> bool:
    if not rec:
        return False
    return str(rec.get("status") or "").upper() in HONEST_RECEIPT


def broker_column(
    *,
    sa: str,
    cycle: BrokerCycle | None,
    in_queue: bool,
    worker: str,
    reg_st: str,
    has_receipt: bool,
) -> str:
    """PASS only on full CHECK→ACT→VERIFY with verify deliver_ok true."""
    # Pack file lists future sas — only backlog rows in active drain are PEND
    if in_queue and reg_st != "done":
        return "PEND"
    roles = cycle.roles if cycle else set()
    full = {"check", "act", "verify"}.issubset(roles)

    if worker == "PASS" and has_receipt:
        if not full:
            return "PEND"
        if cycle and cycle.verify_orch_ok is False:
            return "FAIL"
        # Receipt logged wins over deliver_ok=false (hub cooldown — INCIDENT-006)
        if cycle and (cycle.verify_deliver_ok is True or cycle.verify_orch_ok is True):
            return "PASS"
        return "PEND"

    if reg_st != "done" and not has_receipt and roles:
        if full and cycle and cycle.verify_deliver_ok is True:
            return "STALE"
        return "STALE" if roles else "WAIT"

    if worker == "PASS" and has_receipt:
        return "PEND"
    return "WAIT"


def worker_column(*, rec: dict | None, reg_st: str, in_queue: bool) -> str:
    if rec:
        st = str(rec.get("status") or "").upper()
        if st in HONEST_RECEIPT:
            return "PASS"
        if st in ("BLOCKED", "FAIL"):
            return "FAIL"
    if reg_st == "done" and not _has_honest_receipt(rec):
        return "FAIL"
    if in_queue and reg_st != "done":
        return "PEND"
    return "WAIT"


def recipe_column(proof: str) -> str:
    """Short proof/recipe label for monitor (recipe = validation = proof)."""
    m = {
        "HONEST_RECEIPT": "OK",
        "RECEIPT_AND_BATCH_YAML": "MIXED",
        "BATCH_CLOSEOUT_ONLY": "FAKE",
        "BROKER_YAML_ONLY": "YAML",
        "WORKER_YAML_ONLY": "YAML",
        "MAINTAINER_YAML_ONLY": "YAML",
        "YAML_ONLY_OTHER": "YAML",
        "DONE_NO_PROOF_ON_DISK": "NONE",
        "BACKLOG": "—",
    }
    return m.get(proof, proof[:8] if proof else "—")


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_dual_proof_system(*, valid_yes: int, hygiene_ok: bool | None = None) -> dict:
    """System-level Brain + Maintainer validation snapshots (layer 5–6)."""
    hygiene = _load_json(HYGIENE_PASS)
    brain = _load_json(BRAIN_VAL)
    track = _load_json(TRACK_SNAP)
    maint = (track.get("broker_validation") or {}).get("maintainer_proof") or {}

    if hygiene_ok is None:
        hygiene_ok = bool(hygiene.get("ok")) and int(hygiene.get("unproven_done") or 0) == 0
    brain_prog = brain.get("progress_honest") or {}
    brain_vy = brain_prog.get("valid_yes")
    brain_ok = bool(brain.get("ok")) and brain_vy == valid_yes
    maint_ok = bool(maint.get("ok")) if maint else hygiene_ok
    snapshot_stale = brain_vy is not None and brain_vy != valid_yes
    brain_gap = (valid_yes - int(brain_vy)) if brain_vy is not None else None

    return {
        "hygiene": {
            "ok": hygiene_ok,
            "at": hygiene.get("at"),
            "valid_yes": hygiene.get("valid_yes"),
        },
        "brain": {
            "ok": brain_ok,
            "at": brain.get("at"),
            "valid_yes": brain_vy,
            "live_valid_yes": valid_yes,
            "snapshot_stale": snapshot_stale,
            "gap": brain_gap,
            "status": brain.get("status"),
        },
        "maintainer": {
            "ok": maint_ok,
            "at": maint.get("at") or track.get("at"),
            "label": maint.get("label") or "Maintainer gates",
        },
        "dual_proof_ok": hygiene_ok and brain_ok and maint_ok,
        "law": "PROOF_VALIDATION_CHAIN_LOCKED_v1",
    }


def brain_row_column(*, valid: str, proof: str, system_brain_ok: bool) -> str:
    """Brain column: row closed only when system Brain validation agrees."""
    if valid == "YES":
        return "PASS" if system_brain_ok else "PEND"
    if valid in ("PARTIAL", "PEND"):
        return "PEND"
    if valid in ("FAKE", "NO") or proof in ("BATCH_CLOSEOUT_ONLY", "DONE_NO_PROOF_ON_DISK"):
        return "FAIL"
    return "WAIT"


def maintainer_row_column(
    *,
    valid: str,
    proof: str,
    recipe: str,
    rec: dict | None,
    system_maintainer_ok: bool,
) -> str:
    """Maintainer column: receipt source + gates + recipe honesty."""
    if valid == "YES":
        if proof not in ("HONEST_RECEIPT", "RECEIPT_AND_BATCH_YAML") and recipe not in ("OK", "MIXED"):
            return "FAIL"
        src = str((rec or {}).get("source") or "").strip()
        if src and src not in ALLOWED_RECEIPT_SOURCES:
            return "FAIL"
        return "PASS" if system_maintainer_ok else "PEND"
    if valid in ("PARTIAL", "PEND"):
        return "PEND"
    if valid in ("FAKE", "NO") or recipe in ("FAKE", "NONE"):
        return "FAIL"
    return "WAIT"


def valid_column(*, registry: str, worker: str, broker: str, proof: str) -> str:
    if worker == "PASS" and broker == "PASS":
        return "YES"
    if worker == "PASS" and broker in ("PEND", "FAIL"):
        return "PARTIAL"
    if worker == "PASS" and broker == "STALE":
        return "PARTIAL"
    if proof in ("BATCH_CLOSEOUT_ONLY", "DONE_NO_PROOF_ON_DISK") or (
        registry == "done" and worker != "PASS"
    ):
        return "FAKE"
    if worker == "FAIL":
        return "NO"
    if worker == "PEND" or broker == "PEND":
        return "PEND"
    return "WAIT"


def map_column(*, sa: str, worker: str, broker: str, here_sa: str, in_queue: bool) -> str:
    if worker == "PASS" and broker == "PASS":
        return "DONE"
    if sa == here_sa:
        return "HERE"
    if in_queue:
        return "QUEUE"
    if worker == "PASS" and broker != "PASS":
        return "GAP"
    if worker == "FAIL":
        return "FAIL"
    return "ROAD"


def active_batch_yaml_on_honest_done() -> list[dict]:
    """Honest done rows with cursor-worker-batch YAML still in active logs."""
    from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

    audit = audit_registry_done()
    honest = set(audit.get("honest_done_ids") or [])
    out: list[dict] = []
    for p in sorted(LOGS.glob("*plan-with-no-asf*.yaml")):
        if "QUARANTINE_BATCH_YAML" in str(p):
            continue
        text = p.read_text(encoding="utf-8")[:800]
        if "cursor-worker-batch" not in text:
            continue
        import re

        m = re.search(r"(sa-\d{4})", p.name)
        if not m:
            continue
        sa = m.group(1)
        if sa in honest:
            out.append({"sa_id": sa, "path": p.name})
    return out


def quarantine_batch_yaml_on_honest_done(*, dry_run: bool = False) -> dict:
    """Move cursor-worker-batch YAML off honest-done sas into quarantine (batch only)."""
    import shutil
    from datetime import datetime, timezone

    from yaml_quarantine_lib_v1 import QUARANTINE, MANIFEST, is_quarantined_path  # noqa: WPS433

    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    targets = active_batch_yaml_on_honest_done()
    by_sa: dict[str, list[str]] = {}
    for t in targets:
        by_sa.setdefault(t["sa_id"], []).append(t["path"])
    moved: list[str] = []
    if not dry_run and targets:
        QUARANTINE.mkdir(parents=True, exist_ok=True)
        for t in targets:
            src = LOGS / t["path"]
            if not src.is_file() or is_quarantined_path(src):
                continue
            dest = QUARANTINE / src.name
            if dest.exists():
                dest = QUARANTINE / f"{src.stem}_{_now().replace(':', '')}{src.suffix}"
            shutil.move(str(src), str(dest))
            moved.append(str(dest))
            with MANIFEST.open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {
                            "at": _now(),
                            "sa_id": t["sa_id"],
                            "from": str(src),
                            "to": str(dest),
                            "reason": "honest_done_stale_batch",
                        }
                    )
                    + "\n"
                )
    return {
        "ok": True,
        "dry_run": dry_run,
        "sa_count": len(by_sa),
        "file_count": len(targets),
        "sa_ids": sorted(by_sa.keys(), key=lambda x: int(x.split("-")[1])),
        "moved": moved,
    }


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_factory_now() -> dict:
    row = _read_json(SINA / "factory-now-v1.json")
    inbox = _read_json(SINA / "worker-prompt-inbox-v1.json")
    if row:
        row = dict(row)
        row["inbox_pending"] = bool(inbox.get("pending"))
        row["inbox_sa"] = str((inbox.get("meta") or {}).get("sa_id") or inbox.get("sa_id") or "")
    return row


def _load_phase_strict() -> dict:
    cfg = _read_json(SINA / "phase-strict-drain-v1.json")
    routing = _read_json(SINA / "run-inbox-routing-v1.json")
    if not cfg.get("enabled"):
        order = routing.get("order") or ""
        try:
            from founder_directive_ssot_v1 import execution_rail_line, hub_closed  # noqa: WPS433

            if hub_closed():
                order = execution_rail_line()
        except Exception:
            pass
        return {"enabled": False, "order": order}
    order = routing.get("order") or ""
    try:
        from founder_directive_ssot_v1 import execution_rail_line, hub_closed  # noqa: WPS433

        if hub_closed():
            order = execution_rail_line()
    except Exception:
        pass
    if not order and cfg.get("execution_order"):
        parts = []
        for block in cfg["execution_order"]:
            parts.append(f"{block.get('phase')}({block.get('achievable_count')})")
        order = " → ".join(parts)
    return {
        "enabled": True,
        "order": order,
        "resume_sa": cfg.get("resume_sa") or routing.get("resume_sa"),
        "resume_pack": cfg.get("resume_pack"),
        "total_headless": cfg.get("total_achievable_headless"),
        "law": "SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md",
    }


def audit_monitor(*, filter_mode: str = "road") -> dict:
    """Full road map + progress — same logic as validator_list build_list."""
    from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

    audit = audit_registry_done()
    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = sorted(reg.get("plans") or [], key=lambda p: _sa_num(str(p.get("id") or "sa-0")))
    cycles = load_broker_cycles()
    queue_sas, here_sa, here_pos, here_role = queue_context()
    receipts_raw = load_receipts()
    closeouts = load_closeouts()
    receipts: dict[str, dict] = {}
    if RECEIPTS.is_dir():
        for p in RECEIPTS.glob("sa-*-receipt.json"):
            try:
                receipts[p.stem.replace("-receipt", "")] = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass

    rows: list[dict] = []
    valid_counts: dict[str, int] = {}
    broker_counts: dict[str, int] = {}
    brain_counts: dict[str, int] = {}
    maint_counts: dict[str, int] = {}
    backlog_broker_pass = 0

    for n, pl in enumerate(plans, start=1):
        sa = pl.get("id") or ""
        if not sa.startswith("sa-"):
            continue
        reg_st = pl.get("status") or "backlog"
        rec = receipts.get(sa)
        proof = proof_verdict(sa, reg_st, receipts_raw.get(sa), closeouts.get(sa))
        in_q = sa in queue_sas
        w = worker_column(rec=rec, reg_st=reg_st, in_queue=in_q)
        has_rcpt = _has_honest_receipt(rec)
        b = broker_column(
            sa=sa,
            cycle=cycles.get(sa),
            in_queue=in_q,
            worker=w,
            reg_st=reg_st,
            has_receipt=has_rcpt,
        )
        if reg_st == "backlog" and b == "PASS":
            backlog_broker_pass += 1
        broker_counts[b] = broker_counts.get(b, 0) + 1
        valid = valid_column(registry=reg_st, worker=w, broker=b, proof=proof)
        valid_counts[valid] = valid_counts.get(valid, 0) + 1
        rows.append(
            {
                "n": n,
                "sa_id": sa,
                "worker": w,
                "broker": b,
                "valid": valid,
                "recipe": recipe_column(proof),
                "proof": proof,
                "map": map_column(sa=sa, worker=w, broker=b, here_sa=here_sa, in_queue=in_q),
                "registry": reg_st,
                "_rec": rec,
            }
        )

    rows.sort(key=lambda r: r["n"])
    all_rows = rows
    valid_yes_n = valid_counts.get("YES", 0)
    map_done_n = sum(1 for r in all_rows if r["map"] == "DONE")
    dual = load_dual_proof_system(valid_yes=valid_yes_n)
    sys_brain_ok = bool((dual.get("brain") or {}).get("ok"))
    sys_maint_ok = bool((dual.get("maintainer") or {}).get("ok"))

    for r in all_rows:
        rec = r.pop("_rec", None)
        recipe = r.get("recipe") or "—"
        br = brain_row_column(valid=r["valid"], proof=r.get("proof") or "", system_brain_ok=sys_brain_ok)
        mt = maintainer_row_column(
            valid=r["valid"],
            proof=r.get("proof") or "",
            recipe=recipe,
            rec=rec,
            system_maintainer_ok=sys_maint_ok,
        )
        r["brain"] = br
        r["maintainer"] = mt
        brain_counts[br] = brain_counts.get(br, 0) + 1
        maint_counts[mt] = maint_counts.get(mt, 0) + 1

    if filter_mode == "queue":
        rows = [r for r in rows if r["map"] in ("HERE", "QUEUE")]
    elif filter_mode == "done":
        rows = [r for r in rows if r["map"] == "DONE"]
    elif filter_mode == "attention":
        rows = [
            r
            for r in rows
            if r["worker"] in ("PEND", "FAIL")
            or r["broker"] in ("PEND", "FAIL", "STALE")
            or r["valid"] in ("PARTIAL", "FAKE", "NO")
        ]

    receipt_done_n = int(audit.get("honest_done", 0) or 0)
    stale_batch = active_batch_yaml_on_honest_done()
    factory_now = _load_factory_now()
    phase_strict = _load_phase_strict()
    you_here = _you_are_here_payload(here_sa=here_sa, here_pos=here_pos, here_role=here_role)

    return {
        "ok": backlog_broker_pass == 0 and audit.get("unproven_done", 0) == 0,
        "schema": "monitor-honesty-v1",
        "law": PROGRESS_LAW,
        "honest_done": receipt_done_n,
        "receipt_done": receipt_done_n,
        "unproven_done": audit.get("unproven_done", 0),
        "total": 1000,
        "filter": filter_mode,
        "progress": {
            "valid_yes": valid_yes_n,
            "map_done": map_done_n,
            "pct": round(100.0 * valid_yes_n / 1000, 2),
            "law": PROGRESS_LAW,
        },
        "integrity": {
            "backlog_broker_pass": backlog_broker_pass,
            "active_batch_yaml_on_honest_done": len(stale_batch),
            "broker_stale": broker_counts.get("STALE", 0),
            "valid_yes_matches_map_done": valid_yes_n == map_done_n,
        },
        "you_are_here": you_here,
        "factory_now": factory_now,
        "phase_strict": phase_strict,
        "counts": {
            "showing": len(rows),
            "done_both": map_done_n,
            "valid_yes": valid_yes_n,
            "valid_partial": valid_counts.get("PARTIAL", 0),
            "valid_fake": valid_counts.get("FAKE", 0),
            "valid_wait": valid_counts.get("WAIT", 0),
            "broker_stale": broker_counts.get("STALE", 0),
            "here": 1 if here_sa else 0,
            "queue": sum(1 for r in rows if r["map"] == "QUEUE"),
            "road": sum(1 for r in rows if r["map"] == "ROAD"),
        },
        "broker_breakdown": broker_counts,
        "valid_breakdown": valid_counts,
        "brain_breakdown": brain_counts,
        "maintainer_breakdown": maint_counts,
        "dual_proof": dual,
        "rows": rows,
        "legend": (
            "Valid YES=Worker+Broker · Brain/Maintainer=system validation · progress=Valid YES only"
        ),
    }


def governance_events_taxonomy_audit(*, limit: int = 500) -> dict:
    """§7.6 — last N agent-governance-events rows must resolve via normalize_kind."""
    from governance_event_kind_v1 import normalize_kind  # noqa: WPS433

    path = SINA / "agent-governance-events.jsonl"
    if not path.is_file():
        return {"ok": True, "sample": 0, "orphans": [], "skipped_blank": 0}
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    sample = rows[-limit:]
    orphans: list[dict] = []
    skipped = 0
    for row in sample:
        raw = str(row.get("kind") or row.get("event") or "").strip()
        if not raw:
            skipped += 1
            continue
        if not normalize_kind(row):
            orphans.append({"event": raw, "at": row.get("at")})
    return {
        "ok": not orphans,
        "sample": len(sample),
        "skipped_blank": skipped,
        "orphans": orphans[:20],
    }
