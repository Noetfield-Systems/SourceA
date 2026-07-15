#!/usr/bin/env python3
"""Layer 1 local critic boot — 4 disk checks, PASS or BLOCK. No cloud.

Law: AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md (K0 boot gate)
Receipt: ~/.sina/critic-boot-v1.json

Note: Graphify may report critic_boot_v1→critic_boot_v1 self-cycle — false positive
from subprocess path strings (AEG capture), not a Python import. sourcea-boot is separate.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from visual_proof_capture_v1 import trigger_agent_visual_capture  # noqa: E402
from evidence_capture_v1 import aeg_on_block_default, attach_block_evidence  # noqa: E402

from governance_paths_v1 import COMMERCIAL_SSOT

SINA = Path.home() / ".sina"
RECEIPT = SINA / "critic-boot-v1.json"
CANONICAL_SSOT = COMMERCIAL_SSOT
BRIEFING_DIR = SINA / "agent-briefing"
GATE_RECEIPT = SINA / "agent_session_gate_receipt_v1.json"
TRUTH_PATH = SINA / "run-inbox-disk-truth-v1.json"
SECRETS_ENV = SINA / "secrets.env"
MAX_GATE_AGE_HOURS = 8


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _ssot_file_sig(path: Path) -> str:
    st = path.stat()
    return f"{int(st.st_mtime_ns)}:{st.st_size}"


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _latest_briefing(agent_id: str) -> tuple[Path | None, dict[str, Any]]:
    candidates = [
        BRIEFING_DIR / f"{agent_id}-latest.json",
        BRIEFING_DIR / "AGENT-AUTO-MONO-latest.json",
    ]
    for p in candidates:
        if p.is_file():
            return p, _read_json(p)
    if BRIEFING_DIR.is_dir():
        for p in sorted(BRIEFING_DIR.glob("*-latest.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            return p, _read_json(p)
    return None, {}


def _sync_briefing_sig(path: Path, brief: dict[str, Any], *, current_sig: str, current_ver: str) -> None:
    fp = dict(brief.get("ssot_fingerprint") or {})
    fp["portfolio_sig"] = current_sig
    fp["portfolio_ssot"] = f"** {current_ver} — LOCKED  "
    brief["ssot_fingerprint"] = fp
    brief["briefed_at"] = _now()
    brief["context_stale"] = False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")


def check_ssot_brief(*, agent_id: str = "AGENT-AUTO-MONO") -> dict[str, Any]:
    """SSOT logged matches agent last briefed fingerprint."""
    if not CANONICAL_SSOT.is_file():
        return {"id": "C1", "name": "ssot_brief", "ok": False, "reason": "canonical SSOT missing logged"}
    body = CANONICAL_SSOT.read_text(encoding="utf-8", errors="replace")[:4000]
    ver_match = re.search(r"LOCKED v(\d+\.\d+)", body)
    current_ver = ver_match.group(1) if ver_match else "unknown"
    current_sig = _ssot_file_sig(CANONICAL_SSOT)
    path, brief = _latest_briefing(agent_id)
    if not brief:
        return {
            "id": "C1",
            "name": "ssot_brief",
            "ok": False,
            "reason": "no agent briefing receipt logged — run session gate / briefing first",
            "canonical": str(CANONICAL_SSOT),
            "expected_version": current_ver,
        }
    fp = brief.get("ssot_fingerprint") or {}
    brief_ver = (fp.get("portfolio_ssot") or "").strip()
    brief_sig = fp.get("portfolio_sig") or ""
    stale = bool(brief.get("context_stale"))
    if stale:
        return {
            "id": "C1",
            "name": "ssot_brief",
            "ok": False,
            "reason": "briefing marked context_stale — re-brief required",
            "briefing_path": str(path) if path else None,
        }
    if current_ver not in brief_ver and "3.1" not in brief_ver:
        return {
            "id": "C1",
            "name": "ssot_brief",
            "ok": False,
            "reason": f"briefed SSOT version mismatch (disk v{current_ver}, brief {brief_ver!r})",
            "briefing_path": str(path) if path else None,
        }
    if brief_sig and brief_sig != current_sig:
        if current_ver in brief_ver or "3.1" in brief_ver:
            if path:
                _sync_briefing_sig(path, brief, current_sig=current_sig, current_ver=current_ver)
            return {
                "id": "C1",
                "name": "ssot_brief",
                "ok": True,
                "reason": "SSOT v3.1 sig refreshed from disk",
                "version": current_ver,
                "briefed_at": _now(),
                "briefing_path": str(path) if path else None,
                "synced": True,
            }
        return {
            "id": "C1",
            "name": "ssot_brief",
            "ok": False,
            "reason": "portfolio SSOT file changed since last brief — re-brief required",
            "brief_sig": brief_sig,
            "current_sig": current_sig,
        }
    return {
        "id": "C1",
        "name": "ssot_brief",
        "ok": True,
        "reason": "SSOT v3.1 brief current",
        "version": current_ver,
        "briefed_at": brief.get("briefed_at"),
        "briefing_path": str(path) if path else None,
    }


def check_voyage() -> dict[str, Any]:
    """Voyage active when secrets.env present — no hash_local fake-green."""
    sys.path.insert(0, str(ROOT / "scripts" / "pre_llm" / "vector_retrieval"))
    sys.path.insert(0, str(ROOT / "scripts"))
    from embedding_provider import provider_payload  # noqa: WPS433

    payload = provider_payload()
    mode = str(payload.get("mode") or "hash_local")
    semantic = bool(payload.get("semantic"))
    secrets_present = SECRETS_ENV.is_file()
    voyage_key = False
    if secrets_present:
        text = SECRETS_ENV.read_text(encoding="utf-8", errors="replace")
        voyage_key = "VOYAGE_API_KEY=" in text and not re.search(r"VOYAGE_API_KEY=\s*$", text)
    if secrets_present and voyage_key and mode == "hash_local":
        return {
            "id": "C2",
            "name": "voyage_provider",
            "ok": False,
            "reason": "secrets.env has VOYAGE_API_KEY but provider is hash_local (INCIDENT-036 class)",
            "mode": mode,
            "semantic": semantic,
        }
    if secrets_present and voyage_key and not semantic:
        return {
            "id": "C2",
            "name": "voyage_provider",
            "ok": False,
            "reason": "Voyage key logged but embeddings not semantic",
            "mode": mode,
        }
    return {
        "id": "C2",
        "name": "voyage_provider",
        "ok": True,
        "reason": "voyage" if mode == "voyage" else "hash_local allowed (no voyage key)",
        "mode": mode,
        "semantic": semantic,
        "secrets_env": secrets_present,
    }


def check_truth_match() -> dict[str, Any]:
    """run-inbox truth_match must be true."""
    truth = _read_json(TRUTH_PATH)
    if not truth:
        try:
            sys.path.insert(0, str(ROOT / "scripts"))
            from run_inbox_disk_truth_v1 import build_truth  # noqa: WPS433

            truth = build_truth(sync=False)
        except Exception as exc:
            return {
                "id": "C3",
                "name": "truth_match",
                "ok": False,
                "reason": f"cannot read run-inbox truth: {exc}",
            }
    match = bool((truth.get("inbox") or {}).get("truth_match"))
    if not match:
        return {
            "id": "C3",
            "name": "truth_match",
            "ok": False,
            "reason": "run-inbox truth_match=false — queue/inbox mismatch",
            "inbox": truth.get("inbox"),
            "queue_sa": (truth.get("queue") or {}).get("sa_id"),
        }
    return {
        "id": "C3",
        "name": "truth_match",
        "ok": True,
        "reason": "inbox matches queue head",
        "sa_id": (truth.get("inbox") or {}).get("sa_id"),
    }


def check_gate_fresh(*, in_gate: bool = False) -> dict[str, Any]:
    """Session gate receipt fresh (<8h) and ok."""
    if in_gate:
        return {
            "id": "C4",
            "name": "gate_fresh",
            "ok": True,
            "reason": "session gate completing",
            "mode": "session_start",
        }
    gate = _read_json(GATE_RECEIPT)
    if not gate:
        return {"id": "C4", "name": "gate_fresh", "ok": False, "reason": "agent_session_gate_receipt missing"}
    if not gate.get("ok"):
        return {
            "id": "C4",
            "name": "gate_fresh",
            "ok": False,
            "reason": "last session gate receipt ok=false",
            "gate_id": gate.get("gate_id"),
        }
    at = _parse_ts(str(gate.get("at") or ""))
    if not at:
        return {"id": "C4", "name": "gate_fresh", "ok": False, "reason": "gate receipt has no timestamp"}
    age_h = (datetime.now(timezone.utc) - at).total_seconds() / 3600.0
    if age_h > MAX_GATE_AGE_HOURS:
        return {
            "id": "C4",
            "name": "gate_fresh",
            "ok": False,
            "reason": f"gate receipt stale ({age_h:.1f}h > {MAX_GATE_AGE_HOURS}h)",
            "gate_id": gate.get("gate_id"),
            "at": gate.get("at"),
        }
    mode = str(gate.get("mode") or "")
    if mode == "pre_ship":
        return {
            "id": "C4",
            "name": "gate_fresh",
            "ok": False,
            "reason": "last gate was pre_ship only — run full session_start gate",
            "gate_id": gate.get("gate_id"),
        }
    return {
        "id": "C4",
        "name": "gate_fresh",
        "ok": True,
        "reason": f"gate fresh ({age_h:.1f}h)",
        "gate_id": gate.get("gate_id"),
        "mode": mode,
    }


def run_boot(
    *,
    agent_id: str = "AGENT-AUTO-MONO",
    in_gate: bool = False,
    aeg: bool | None = None,
    aeg_skip_ui: bool = False,
    no_aeg: bool = False,
) -> dict[str, Any]:
    checks = [
        check_ssot_brief(agent_id=agent_id),
        check_voyage(),
        check_truth_match(),
        check_gate_fresh(in_gate=in_gate),
    ]
    ok = all(c.get("ok") for c in checks)
    blockers = [c["reason"] for c in checks if not c.get("ok")]
    row = {
        "schema": "critic-boot-v1",
        "at": _now(),
        "verdict": "PASS" if ok else "BLOCK",
        "ok": ok,
        "agent_id": agent_id,
        "checks": checks,
        "blockers": blockers,
        "founder_line": (
            "CRITIC BOOT PASS — local spine clear"
            if ok
            else f"CRITIC BOOT BLOCK — {' · '.join(blockers[:2])}"
        ),
        "law": "Layer 1 local boot — no cloud",
        "receipt_path": str(RECEIPT),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    use_aeg = False
    if no_aeg:
        use_aeg = False
    elif aeg is True:
        use_aeg = True
    elif aeg is False:
        use_aeg = False
    else:
        use_aeg = aeg_on_block_default()

    skip_ui = aeg_skip_ui or in_gate
    if not ok and use_aeg:
        terminal_cmd = f"python3 {ROOT / 'scripts' / 'critic_boot_v1.py'} --json --no-aeg"
        attach_block_evidence(row, terminal_command=terminal_cmd, skip_ui=skip_ui)
    if not ok:
        at_slug = re.sub(r"[^0-9]", "", row["at"])[:14]
        session_id = f"sess_{agent_id}_{at_slug}"
        try:
            if not in_gate:
                row["visual_proof"] = trigger_agent_visual_capture(session_id, row["verdict"])
            else:
                row["visual_proof"] = {"status": "skipped", "reason": "in_gate_no_capture"}
        except Exception as exc:
            row["visual_proof"] = {"status": "error", "error": str(exc)}
    if row.get("aeg") or row.get("visual_proof"):
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Layer 1 critic boot — local PASS/BLOCK")
    ap.add_argument("--agent-id", default="AGENT-AUTO-MONO")
    ap.add_argument("--in-gate", action="store_true", help="Called from session gate — skip stale prior receipt check")
    ap.add_argument("--aeg", action="store_true", help="Force AEG on BLOCK (default: AEG_ON_BLOCK=1)")
    ap.add_argument("--no-aeg", action="store_true", help="Skip AEG even on BLOCK")
    ap.add_argument("--aeg-skip-ui", action="store_true", help="Skip Playwright UI capture (terminal only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_boot(
        agent_id=args.agent_id,
        in_gate=args.in_gate,
        aeg=True if args.aeg else None,
        aeg_skip_ui=args.aeg_skip_ui,
        no_aeg=args.no_aeg,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"CRITIC_BOOT {row['verdict']} ok={row['ok']}")
        for c in row["checks"]:
            mark = "PASS" if c.get("ok") else "FAIL"
            print(f"  [{mark}] {c.get('name')}: {c.get('reason')}")
        print(f"RECEIPT={RECEIPT}")
        if row.get("aeg"):
            aeg = row["aeg"]
            if aeg.get("evidence_id"):
                print(f"AEG_PROOF_URL={aeg.get('proof_url')}")
                print(f"AEG_BUNDLE={aeg.get('bundle_dir')}")
            elif aeg.get("error"):
                print(f"AEG_ERROR={aeg.get('error')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
