#!/usr/bin/env python3
"""Remotion artifact factory — pipeline row or JSON in → prospect reel MP4 out.

SSOT input: remotion-prospect-reel-v1 JSON
Pipeline: ~/.sina/commercial-pipeline-v1.jsonl (row-id → props)
Output: ~/.sina/commercial-videos-v1/{slug}.mp4
Receipt: ~/.sina/enforcement/remotion-artifact-factory-receipt-v1.json

Law: programmatic motion + real proof fields from disk — no fake metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FACTORY = ROOT / "commercial-video-factory"
SINA = Path.home() / ".sina"
PIPELINE = SINA / "commercial-pipeline-v1.jsonl"
PROOF_SCENARIOS = ROOT / "witnessbc-site" / "data" / "proof-scenarios-v1.json"
OUT_DIR = SINA / "commercial-videos-v1"
WORK_PROPS = SINA / "remotion-render-input-v1.json"
RECEIPT = SINA / "enforcement" / "remotion-artifact-factory-receipt-v1.json"

LANE_DEFAULTS = {
    "WBC": {
        "brand": "Witness AI",
        "accent": "#2dd4bf",
        "cta": "Book 15-min proof",
        "proof_base": "http://127.0.0.1:8090/proof.html#scenario=",
    },
    "AB1": {
        "brand": "SourceA",
        "accent": "#044441",
        "cta": "See controlled automation proof",
        "proof_base": "http://127.0.0.1:5180/sourcea/proof.html#",
    },
    "NW1": {
        "brand": "Noetfield",
        "accent": "#2563eb",
        "cta": "Book NF-RD pilot",
        "proof_base": "https://www.noetfield.com/copilot/pilot/",
    },
    "AEG": {
        "brand": "Witness AI",
        "accent": "#2dd4bf",
        "cta": "Open live proof",
        "proof_base": "http://127.0.0.1:8090/proof.html#scenario=",
    },
}

SCENARIO_HOOKS = {
    "outbound": "Your outbound agent sends before anyone approves?",
    "tool": "Tool calls exporting PII with zero gate?",
    "publish": "Publishing without proof the policy ran?",
    "pii-leak": "SSN patterns in agent output — blocked at dispatch?",
    "mcp-escalate": "MCP write to prod without human gate?",
    "tamper": "Can you prove receipts weren't hand-edited?",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s[:64] or "prospect"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_pipeline_row(row_id: str) -> dict[str, Any]:
    if not PIPELINE.is_file():
        raise SystemExit(f"FAIL: no pipeline at {PIPELINE}")
    latest: dict[str, dict[str, Any]] = {}
    for line in PIPELINE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = str(row.get("id") or "")
        if rid:
            latest[rid] = row
    row = latest.get(row_id)
    if not row:
        raise SystemExit(f"FAIL: unknown pipeline row {row_id}")
    return row


def _scenario_for_lane(lane: str) -> dict[str, Any]:
    if not PROOF_SCENARIOS.is_file():
        return {}
    data = _read_json(PROOF_SCENARIOS)
    scenarios = data.get("scenarios") or []
    if not scenarios:
        return {}
    lane_u = lane.upper()
    if lane_u in ("WBC", "AEG"):
        for s in scenarios:
            if s.get("slug") == "outbound":
                return s
    return scenarios[0]


def build_props_from_pipeline(row: dict[str, Any], *, scenario_slug: str | None = None) -> dict[str, Any]:
    lane = str(row.get("lane") or "WBC").upper()
    if lane == "AB1":
        lane_key = "AB1"
    elif lane.startswith("NW"):
        lane_key = "NW1"
    else:
        lane_key = "WBC"
    defaults = LANE_DEFAULTS[lane_key]
    scenario = _scenario_for_lane(lane_key)
    slug = scenario_slug or str(scenario.get("slug") or "outbound")
    if PROOF_SCENARIOS.is_file():
        for s in _read_json(PROOF_SCENARIOS).get("scenarios") or []:
            if s.get("slug") == slug:
                scenario = s
                break
    company = str(row.get("company") or "Prospect")
    proof_url = str(row.get("proof_url") or "").strip()
    if not proof_url and "proof_base" in defaults:
        base = defaults["proof_base"]
        proof_url = base + slug if base.endswith("=") else base
    hook = SCENARIO_HOOKS.get(slug) or f"{company}: agent actions without signed proof?"
    pain = str(scenario.get("narrative") or "")[:140]
    if not pain:
        pain = "Irreversible agent steps without policy-at-dispatch and signed receipts."
    return {
        "schema": "remotion-prospect-reel-v1",
        "company": company,
        "lane": lane_key,
        "hook": hook,
        "pain": pain,
        "proof_line": str(scenario.get("verdict_summary") or "Policy at dispatch · signed receipts · tamper-FAIL"),
        "scenario": slug,
        "verdict": str(scenario.get("verdict") or "ESCALATE"),
        "receipt_hash": str(scenario.get("receipt_hash") or "sha256:…"),
        "proof_url": proof_url,
        "cta": defaults["cta"],
        "brand": defaults["brand"],
        "accent": defaults["accent"],
        "duration_seconds": 30,
        "pipeline_row_id": row.get("id"),
    }


def build_props_from_file(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    data.setdefault("schema", "remotion-prospect-reel-v1")
    return data


def ensure_npm() -> None:
    node_modules = FACTORY / "node_modules"
    if node_modules.is_dir():
        return
    print("=== remotion_artifact_factory: npm install ===", file=sys.stderr)
    subprocess.run(
        ["npm", "install", "--no-audit", "--no-fund"],
        cwd=FACTORY,
        check=True,
    )


def render_mp4(props: dict[str, Any], out_path: Path, *, dry_run: bool = False) -> None:
    _write_json(WORK_PROPS, props)
    if dry_run:
        return
    ensure_npm()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "npx",
        "remotion",
        "render",
        "src/index.ts",
        "ProspectReel",
        str(out_path),
        f"--props={WORK_PROPS}",
    ]
    print("=== remotion render ===", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, cwd=FACTORY, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Remotion artifact factory v1")
    ap.add_argument("--row-id", help="commercial-pipeline row id")
    ap.add_argument("--input", type=Path, help="remotion-prospect-reel-v1 JSON")
    ap.add_argument("--scenario", help="proof scenario slug override")
    ap.add_argument("--output", type=Path, help="output mp4 path")
    ap.add_argument("--dry-run", action="store_true", help="build props only, no render")
    ap.add_argument("--sample", action="store_true", help="render bundled sample JSON")
    ap.add_argument("--json", action="store_true", help="stdout receipt JSON")
    args = ap.parse_args()

    if args.sample:
        props = build_props_from_file(FACTORY / "data" / "sample-prospect-reel-v1.json")
        slug = _slugify(props.get("company", "sample"))
    elif args.input:
        props = build_props_from_file(args.input)
        slug = _slugify(str(props.get("company") or "prospect"))
    elif args.row_id:
        row = load_pipeline_row(args.row_id)
        props = build_props_from_pipeline(row, scenario_slug=args.scenario)
        slug = _slugify(str(row.get("company") or args.row_id))
    else:
        ap.error("one of --row-id, --input, or --sample required")

    out = args.output or (OUT_DIR / f"{slug}-reel-v1.mp4")
    t0 = _now()
    try:
        render_mp4(props, out, dry_run=args.dry_run)
        status = "dry_run" if args.dry_run else "rendered"
    except subprocess.CalledProcessError as exc:
        receipt = {
            "schema": "remotion-artifact-factory-receipt-v1",
            "at": _now(),
            "status": "fail",
            "error": str(exc),
            "props_path": str(WORK_PROPS),
        }
        _write_json(RECEIPT, receipt)
        if args.json:
            print(json.dumps(receipt, indent=2))
        return 1

    receipt = {
        "schema": "remotion-artifact-factory-receipt-v1",
        "at": _now(),
        "started_at": t0,
        "status": status,
        "company": props.get("company"),
        "lane": props.get("lane"),
        "scenario": props.get("scenario"),
        "props_path": str(WORK_PROPS),
        "output": str(out) if not args.dry_run else None,
        "proof_url": props.get("proof_url"),
        "pipeline_row_id": props.get("pipeline_row_id"),
        "factory": str(FACTORY),
        "law": "JSON in → Remotion MP4 out · proof fields from disk SSOT",
    }
    _write_json(RECEIPT, receipt)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"PASS: remotion artifact factory — {status} → {out if not args.dry_run else WORK_PROPS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
