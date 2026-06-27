#!/usr/bin/env python3
"""Forge Terminal Quality execution block matrix — deterministic CLI + optional HTTP."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-terminal-quality-matrix-v1.json"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _good_doc(run_id: str, ws: str, *, response: str = "Clear README summary for the founder.") -> dict:
    card = {
        "goal": "Summarize README",
        "risk": "low",
        "cursor_prompt": "Summarize README in plain English.",
        "summary": response,
        "decision": "pending",
        "cost_usd": 0.01,
    }
    return {
        "schema": "forge-terminal-run-v1",
        "run_id": run_id,
        "at": "2026-06-25T00:00:00Z",
        "founder_input": "Summarize README purpose",
        "response": response,
        "llm": {"ok": True, "provider": "gemini_direct", "model": "gemini-3.1-flash-lite"},
        "forge": {"workspace": ws},
        "decision_card": card,
    }


def _write_run(run_id: str, doc: dict) -> None:
    from forge_terminal_v1 import _run_path, _write_json  # noqa: WPS433

    _write_json(_run_path(run_id), doc)


def run_matrix() -> list[tuple[str, bool, str, str]]:
    from forge_quality_gate_v1 import apply_gate_to_decision_card, evaluate_quality_gate, write_quality_receipt  # noqa: WPS433
    from forge_terminal_v1 import (  # noqa: WPS433
        decide,
        execute,
        quality_rerun,
        send_to_cloud,
        send_to_cursor,
    )

    td = Path(tempfile.mkdtemp(prefix="forge-qm-"))
    ws = str(td)
    (td / "README.md").write_text("# matrix\n", encoding="utf-8")
    results: list[tuple[str, bool, str, str]] = []

    # REJECT path
    rid_reject = "ft-qm0000000001"
    bad = _good_doc(rid_reject, ws, response='{"goal":"x"}')
    q_bad = evaluate_quality_gate(run_id=rid_reject, doc=bad, workspace_path=ws, full_llm=True)
    bad["quality_gate"] = q_bad
    bad["decision_card"] = apply_gate_to_decision_card(bad["decision_card"], q_bad)
    _write_run(rid_reject, bad)
    write_quality_receipt(q_bad)

    c1 = send_to_cloud(run_id=rid_reject, dry_run=True, workspace_path=ws)
    results.append(("reject blocks cloud", c1.get("error") == "quality_gate_blocked", c1.get("error") or "", "cli"))
    c2 = send_to_cursor(run_id=rid_reject)
    results.append(
        (
            "reject blocks cursor",
            c2.get("error") == "quality_gate_blocked" or c2.get("cursor_blocked"),
            c2.get("error") or "",
            "cli",
        )
    )
    c3 = execute(run_id=rid_reject)
    results.append(("reject blocks execute", c3.get("error") == "quality_gate_blocked", c3.get("error") or "", "cli"))

    # REVISE path
    rid_rev = "ft-qm0000000002"
    rev_doc = _good_doc(rid_rev, ws, response="x")
    q_rev = evaluate_quality_gate(run_id=rid_rev, doc=rev_doc, workspace_path=ws, full_llm=False)
    rev_doc["quality_gate"] = q_rev
    rev_doc["decision_card"] = apply_gate_to_decision_card(rev_doc["decision_card"], q_rev)
    _write_run(rid_rev, rev_doc)
    ex_rev = execute(run_id=rid_rev)
    results.append(
        (
            "revise blocks execute",
            ex_rev.get("error") in ("decision_revise", "quality_gate_blocked", "decision_not_approved"),
            ex_rev.get("error") or "",
            "cli",
        )
    )

    # quality_rerun improves
    rr = quality_rerun(
        run_id=rid_rev,
        founder_text="Summarize README purpose with clear bullet points for the founder.",
        workspace_path=ws,
        full_llm=False,
    )
    results.append(("quality_rerun ok", rr.get("ok") is True, str((rr.get("quality_gate") or {}).get("verdict")), "cli"))

    # PASS path
    rid_pass = "ft-qm0000000003"
    good = _good_doc(rid_pass, ws)
    q_pass = evaluate_quality_gate(run_id=rid_pass, doc=good, workspace_path=ws, full_llm=True)
    good["quality_gate"] = q_pass
    good["decision_card"] = apply_gate_to_decision_card(good["decision_card"], q_pass)
    _write_run(rid_pass, good)
    write_quality_receipt(q_pass)
    decide(run_id=rid_pass, decision="approved", workspace_path=ws)
    cloud_ok = send_to_cloud(run_id=rid_pass, dry_run=True, workspace_path=ws)
    results.append(("pass cloud dry", cloud_ok.get("ok") is True, cloud_ok.get("error") or "", "cli"))

    # missing gate
    rid_miss = "ft-qm0000000004"
    miss = _good_doc(rid_miss, ws)
    miss.pop("quality_gate", None)
    _write_run(rid_miss, miss)
    miss_ex = execute(run_id=rid_miss)
    results.append(
        ("missing gate", miss_ex.get("error") == "quality_gate_missing", miss_ex.get("error") or "", "cli")
    )

    return results


def main() -> int:
    print("Forge quality matrix E2E\n")
    results = run_matrix()
    failed = 0
    out_rows = []
    for name, ok, detail, lane in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"  {status}  [{lane}] {name} ({detail})")
        out_rows.append({"name": name, "ok": ok, "detail": detail, "lane": lane})
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": "forge-terminal-quality-matrix-v1",
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "failed": failed,
                "results": out_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\n{len(results) - failed}/{len(results)} passed")
    print(f"Receipt: {RECEIPT}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
