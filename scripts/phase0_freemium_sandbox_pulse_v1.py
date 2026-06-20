#!/usr/bin/env python3
"""Phase 0 freemium + sandbox reference pulse — internal policy alignment.

Audits sandboxes, trials, freemium inventory vs reference requirements.
Receipt: ~/.sina/phase0-freemium-sandbox-pulse-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "phase0-freemium-sandbox-reference-v1.json"
PULSE = SINA / "phase0-freemium-sandbox-pulse-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _check_item(item: dict, *, disk: dict) -> dict:
    iid = str(item.get("id") or "")
    ok = False
    note = "pending"
    wired = str(item.get("wired_to") or "")

    if iid == "P0-01":
        cat = disk["fbe_catalog"]
        row = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-sandbox-demo"), None)
        ok = bool(row and row.get("status") == "mock_only" and row.get("demo_seconds"))
        note = "sandbox mock catalog" if ok else "cat-sandbox-demo missing or not mock_only"
    elif iid == "P0-02":
        trust = disk["trust_center"]
        ok = bool(trust.get("public_url") or trust.get("gate_k_url"))
        note = "trust center URL set" if ok else "trust center URL missing"
    elif iid == "P0-03":
        cp = disk["commercial_pipeline"]
        rows = cp.get("rows") or []
        ok = any(r.get("proof_url") or r.get("status") in ("proof_viewed", "eval_scheduled") for r in rows)
        note = f"commercial rows={len(rows)}" if ok else "no proof/eval URLs"
    elif iid == "P0-04":
        tp = disk["tool_pick"]
        p1 = tp.get("phase_1_free") or {}
        p2 = tp.get("phase_2_affordable_ai") or {}
        ok = bool(p1.get("tools")) and p2.get("founder_approval_required") is True
        note = "two-phase pick SSOT" if ok else "tool pick SSOT incomplete"
    elif iid == "P0-05":
        pn = disk["platform_neutral"]
        narr = _read(ROOT / "data/noetfield-tle-reference-narrative-v1.json")
        routes = pn.get("product_routes") or []
        nf_route = next((r for r in routes if r.get("lane") == "noetfield"), None)
        route_kw = {str(k).lower() for k in (nf_route or {}).get("keywords") or []}
        narr_kw = {str(k).lower() for k in (narr.get("lane_keywords") or [])}
        blob = json.dumps(narr).lower()
        forbidden = ("mac only", "only on mac", "mac-only")
        ok = (
            narr.get("schema") == "noetfield-tle-reference-narrative-v1"
            and bool(nf_route)
            and route_kw.issubset(narr_kw)
            and all(t in blob for t in ("tle", "board pack", "copilot", "governance receipt"))
            and not any(f in blob for f in forbidden)
        )
        note = "noetfield TLE reference narrative" if ok else "narrative or lane route incomplete"
    elif iid == "P0-06":
        beats = disk["tf_beats"]
        story = _read(ROOT / "data/trustfield-msb-compliance-sandbox-story-v1.json")
        sandbox = next((b for b in (beats.get("beats") or []) if str(b.get("id") or "").upper() == "SANDBOX"), None)
        text = json.dumps({**beats, **story}).lower()
        ok = (
            story.get("schema") == "trustfield-msb-compliance-sandbox-story-v1"
            and bool(sandbox and sandbox.get("live_sandbox"))
            and "rpaa" in text
            and "pilot" in text
            and "sandbox" in text
        )
        note = "TF MSB sandbox + RPAA pilot" if ok else "TF sandbox story incomplete"
    elif iid == "P0-07":
        cat = disk["fbe_catalog"]
        engines = [x for x in (cat.get("items") or []) if x.get("tier") == "engines"]
        ok = len(engines) >= 2 and all(x.get("demo_seconds") for x in engines[:3])
        note = f"engines={len(engines)}" if ok else "engine demo_seconds missing"
    elif iid == "P0-08":
        cfr = disk["commercial_film"]
        beats = cfr.get("beats_index") or {}
        ok = bool(beats.get("witnessbc_tier_A_hero") or cfr.get("linear_reference_4k"))
        note = "witnessbc beats_index" if ok else "proof routing missing"
    elif iid == "P0-09":
        pn = disk["platform_neutral"]
        policy = pn.get("platform_neutral_policy") or {}
        tpl = policy.get("stripe_buyer_copy_template") or ""
        billing = policy.get("stripe_billing") or {}
        ok = (
            bool(tpl)
            and "mac" not in tpl.lower()
            and billing.get("statement_descriptor") == "NOETFIELD SYSTEMS"
            and billing.get("statement_descriptor_short") == "NFS"
        )
        note = "noetfield stripe billing SSOT" if ok else "buyer copy or NFS descriptor missing"
    elif iid == "P0-10":
        cat = disk["fbe_catalog"]
        tiers = cat.get("tiers") or {}
        sandbox = tiers.get("sandbox") or {}
        demo = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-sandbox-demo"), None)
        blob = json.dumps(sandbox).lower()
        ok = (
            bool(sandbox)
            and "free tier" in blob
            and "microvm" in blob
            and sandbox.get("microvm_cap") == 0
            and bool(demo and demo.get("upgrade_path"))
        )
        note = "catalog sandbox tier caps honest" if ok else "sandbox tier copy or upgrade path missing"
    elif iid == "P0-14":
        nm = _read(ROOT / "data/newmatch-factory-v1.json")
        graph = _read(ROOT / "apps/newmatch/data/graph-v1.json")
        ok = (
            nm.get("schema") == "newmatch-factory-v1"
            and graph.get("schema") == "newmatch-graph-local-v1"
            and bool(graph.get("persons"))
            and (ROOT / "scripts/newmatch_situation_router_t0_v1.py").is_file()
        )
        note = "newmatch T0 router + graph scaffold" if ok else "newmatch scaffold incomplete"
    elif iid == "P0-15":
        tk = _read(ROOT / "witnessbc-site/data/toolkits-v1.json")
        freemium = tk.get("freemium") or {}
        sandbox = tk.get("sandbox") or {}
        quick = tk.get("quickstart") or {}
        ok = (
            tk.get("schema") == "witnessbc-toolkits-v1"
            and bool(freemium.get("active"))
            and bool(sandbox.get("active"))
            and bool(quick.get("active"))
            and (ROOT / "scripts/witnessbc_freemium_sandbox_activate_v1.py").is_file()
        )
        note = "witnessbc toolkits freemium + sandbox" if ok else "toolkits freemium/sandbox SSOT incomplete"
    elif iid == "P0-11":
        ok = (ROOT / "scripts/validate-phase0-freemium-sandbox-v1.sh").is_file()
        note = "validator logged" if ok else "validator missing"
    elif iid == "P0-12":
        plans = [disk["outbound_plan"], disk["full_stack_plan"], disk["brain_plan"]]
        ok = all(
            (p.get("cross_ref") or {}).get("phase0_freemium_sandbox") == "data/phase0-freemium-sandbox-reference-v1.json"
            for p in plans
            if p
        )
        note = "plans cross_ref" if ok else "cross_ref not synced on all plans"
    elif iid == "P0-13":
        verify_path = ROOT / "receipts" / "bays" / "noetfield-freemium-bay" / "verify.json"
        verify = _read(verify_path)
        cat = disk["fbe_catalog"]
        row = next((x for x in (cat.get("items") or []) if x.get("catalog_id") == "cat-noetfield-freemium"), None)
        ok = bool(verify.get("ok")) and bool(row and row.get("status") == "mock_only")
        note = "noetfield freemium bay + catalog" if ok else "bay verify or catalog missing"

    return {
        "id": iid,
        "title": item.get("title"),
        "lane": item.get("lane"),
        "kind": item.get("kind"),
        "ok": ok,
        "note": note,
        "wired_to": wired,
    }


def _load_commercial_rows() -> dict:
    path = SINA / "commercial-pipeline-v1.jsonl"
    rows: list[dict] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return {"rows": rows, "count": len(rows)}


def run_pulse(*, write: bool = True) -> dict:
    ssot = _read(SSOT)
    inventory = ssot.get("inventory") or []
    disk = {
        "fbe_catalog": _read(ROOT / "data/fbe_catalog_v1.json"),
        "trust_center": _read(ROOT / "data/trust-center-v1.json"),
        "commercial_pipeline": _load_commercial_rows(),
        "tool_pick": _read(ROOT / "data/tool-pick-two-phase-v1.json"),
        "platform_neutral": _read(ROOT / "data/platform-neutral-world-model-v1.json"),
        "tf_beats": _read(ROOT / "data/trustfield-commercial-film-beats-v1.json"),
        "commercial_film": _read(ROOT / "data/commercial-film-routing-v1.json"),
        "outbound_plan": _read(ROOT / "data/outbound-factory-100-upgrade-plan-v1.json"),
        "full_stack_plan": _read(ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json"),
        "brain_plan": _read(ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"),
    }

    checks = [_check_item(item, disk=disk) for item in inventory]
    done = sum(1 for c in checks if c.get("ok"))
    total = len(checks)
    pct = round(100 * done / total) if total else 0
    head = next((c for c in checks if not c.get("ok")), checks[0] if checks else {})

    row = {
        "schema": "phase0-freemium-sandbox-pulse-v1",
        "at": _now(),
        "ok": done >= max(1, total // 2),
        "phase0_line": f"Phase0 reference · {done}/{total} ({pct}%) · head={head.get('id', '—')}",
        "one_law": ssot.get("one_law"),
        "progress": {"done": done, "total": total, "pct": pct},
        "checks": checks,
        "head": head,
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read(PULSE)
    if not row:
        row = run_pulse(write=True)
    return {
        "schema": "worker-hub-phase0-reference-v1",
        "ok": bool(row.get("ok")),
        "phase0_line": row.get("phase0_line"),
        "progress": row.get("progress"),
        "head": row.get("head"),
        "one_law": row.get("one_law"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 0 freemium sandbox pulse")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        print(json.dumps(hub_slice(), indent=2))
        return 0
    row = run_pulse(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("phase0_line"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
