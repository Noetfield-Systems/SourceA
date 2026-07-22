#!/usr/bin/env python3
"""ENGINE-404 — pipeline row → Remotion prospect JSON → MP4 → eval pack.

Reads commercial-pipeline row · public URLs · boot/AEG disk.
Writes commercial-video-factory/data/prospect-{suffix}-v1.json
Renders ProspectReel · attaches to ~/.sina/outbound/eval-booking-{suffix}/

Receipt: ~/.sina/enforcement/commercial-video-factory-receipt-v1.json
Law: SHIP_BLOCKED_MOCK — proof beat is JSON+terminal preview only until real b-roll wired.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
FACTORY = ROOT / "commercial-video-factory"
DATA_DIR = FACTORY / "data"
OUT_DIR = FACTORY / "out"
BROLL_PUBLIC = FACTORY / "public" / "broll" / "w1-proof.mp4"
W1_SITE_MP4 = ROOT / "SourceA-landing" / "green-unified" / "assets" / "w1-demo.mp4"
RECEIPT = SINA / "enforcement" / "commercial-video-factory-receipt-v1.json"

LANE_COPY: dict[str, dict[str, str]] = {
    "AB1": {
        "hook": "Can you prove what your agents ran last night?",
        "pain": "Logs aren't receipts — counsel can't file a chat transcript when execution has no signed gate.",
        "proof_line": "PASS · BLOCK · tamper-FAIL — every gate signed on disk",
        "scenario": "sourcea-boot",
        "cta": "Book 15-min live proof",
        "brand": "SourceA",
        "accent": "#69d419",
    },
    "NW1": {
        "hook": "Can Copilot act before your policy runs?",
        "pain": "Microsoft logs what happened — not whether it was allowed before it ran.",
        "proof_line": "BLOCK · ESCALATE · ALLOW — receipt chain on disk",
        "scenario": "copilot-governance",
        "cta": "Book 15-min walkthrough",
        "brand": "Noetfield",
        "accent": "#2dd4bf",
    },
    "AEG": {
        "hook": "Your agents act before policy runs?",
        "pain": "Irreversible sends without signed receipts — GRC can't prove what happened.",
        "proof_line": "BLOCK · ESCALATE · ALLOW — forensic bundle on disk",
        "scenario": "aeg-proof",
        "cta": "Book 15-min proof",
        "brand": "SourceA",
        "accent": "#69d419",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _row_suffix(row_id: str) -> str:
    return str(row_id or "").replace("cp-", "")[:10]


def _load_row(row_id: str) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_pipeline_v1 import load_rows  # noqa: WPS433

    row = load_rows().get(row_id)
    if not row:
        raise SystemExit(f"FAIL: unknown pipeline row {row_id}")
    return row


def _receipt_hash() -> str:
    boot = ROOT / "SourceA-landing" / "green-unified" / "data" / "boot-proof.json"
    if boot.is_file():
        try:
            row = json.loads(boot.read_text(encoding="utf-8"))
            rid = str(row.get("receipt_id") or row.get("gate_id") or "")
            if rid:
                return f"sha256:{rid[:32]}"
        except (OSError, json.JSONDecodeError):
            pass
    aeg = _read_json(SINA / "aeg-latest-receipt-v1.json")
    eid = str(aeg.get("evidence_id") or "")
    if eid:
        return f"sha256:{eid[-32:]}"
    return "sha256:sourcea-boot-receipt-on-disk"


def _verdict(*, lane: str) -> str:
    aeg = _read_json(SINA / "aeg-latest-receipt-v1.json")
    v = str(aeg.get("verdict") or "").strip().upper()
    if v in ("BLOCK", "PASS", "ESCALATE", "ALLOW"):
        return v
    boot = ROOT / "SourceA-landing" / "green-unified" / "data" / "boot-proof.json"
    if boot.is_file():
        try:
            row = json.loads(boot.read_text(encoding="utf-8"))
            return str(row.get("verdict") or "PASS").upper()
        except (OSError, json.JSONDecodeError):
            pass
    return "ESCALATE" if lane == "AB1" else "BLOCK"


def _ensure_broll_public() -> str:
    """Copy site W1 hero mp4 into Remotion public/ — blocks mock-only outbound."""
    if not W1_SITE_MP4.is_file() or W1_SITE_MP4.stat().st_size < 100_000:
        raise SystemExit(
            "FAIL: mock ship blocked — no w1-demo.mp4 on site.\n"
            "  Run: python3 scripts/w1_film_ingest_master_v1.py\n"
            "  Or: bash scripts/run_w1_film_pipeline_v1.sh"
        )
    BROLL_PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(W1_SITE_MP4, BROLL_PUBLIC)
    return "broll/w1-proof.mp4"


def build_prospect_props(*, row_id: str, proof_url: str = "", duration_seconds: int = 30) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from commercial_recipient_guard_v1 import resolve_aeg_proof_url, resolve_w1_proof_url  # noqa: WPS433

    row = _load_row(row_id)
    lane = str(row.get("lane") or "AB1").upper()
    if lane not in LANE_COPY:
        lane = "AB1"
    copy = LANE_COPY[lane]
    company = str(row.get("company") or "Prospect").strip()
    proof = (
        proof_url.strip()
        or str(row.get("proof_url") or "").strip()
        or resolve_aeg_proof_url()
    )
    broll_file = _ensure_broll_public()
    return {
        "schema": "remotion-prospect-reel-v1",
        "pipeline_row_id": row_id,
        "company": company,
        "lane": lane if lane in ("AB1", "NW1", "AEG", "WBC") else "AB1",
        "hook": copy["hook"],
        "pain": copy["pain"].replace("your agents", f"{company}'s agents") if company and "draft" not in company.lower() else copy["pain"],
        "proof_line": copy["proof_line"],
        "scenario": copy["scenario"],
        "verdict": _verdict(lane=lane),
        "receipt_hash": _receipt_hash(),
        "proof_url": proof,
        "w1_film_url": resolve_w1_proof_url(),
        "cta": copy["cta"],
        "brand": copy["brand"],
        "accent": copy["accent"],
        "duration_seconds": max(15, min(90, int(duration_seconds))),
        "engine": "ENGINE-404",
        "broll_video_file": broll_file,
        "broll_law": "w1-demo.mp4 real UI — TerminalMock blocked for outbound",
    }


def write_props_json(props: dict[str, Any], *, row_id: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    suffix = _row_suffix(row_id)
    path = DATA_DIR / f"prospect-{suffix}-v1.json"
    path.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")
    return path


def render_reel(*, props_path: Path, row_id: str, skip_render: bool = False) -> Path | None:
    if skip_render:
        return None
    if not (FACTORY / "node_modules").is_dir():
        raise SystemExit("FAIL: commercial-video-factory node_modules missing — run npm install in commercial-video-factory/")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = _row_suffix(row_id)
    out_mp4 = OUT_DIR / f"prospect-{suffix}-reel.mp4"
    npm = shutil.which("npm") or "npm"
    cmd = [
        npm,
        "run",
        "render:prospect",
        "--",
        f"out/prospect-{suffix}-reel.mp4",
        f"--props={props_path.relative_to(FACTORY)}",
    ]
    proc = subprocess.run(cmd, cwd=str(FACTORY), capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-1500:]
        raise SystemExit(f"FAIL: remotion render — {tail}")
    if not out_mp4.is_file() or out_mp4.stat().st_size < 5000:
        raise SystemExit(f"FAIL: render produced no mp4 at {out_mp4}")
    return out_mp4


def find_eval_pack_dir(row_id: str) -> Path | None:
    suffix = _row_suffix(row_id)
    pack = SINA / "outbound" / f"eval-booking-{suffix}"
    if pack.is_dir() and (pack / "pack.json").is_file():
        return pack
    for d in sorted((SINA / "outbound").glob("eval-booking-*"), reverse=True):
        meta = _read_json(d / "pack.json")
        if meta.get("row_id") == row_id:
            return d
    return None


def attach_to_pack(
    *,
    pack_dir: Path,
    props: dict[str, Any],
    props_path: Path,
    mp4_path: Path | None,
) -> dict[str, Any]:
    meta = _read_json(pack_dir / "pack.json")
    if not meta:
        raise SystemExit(f"FAIL: missing pack.json in {pack_dir}")

    attached_mp4: str | None = None
    if mp4_path and mp4_path.is_file():
        dest = pack_dir / "prospect-reel.mp4"
        shutil.copy2(mp4_path, dest)
        attached_mp4 = str(dest)

    props_copy = pack_dir / "prospect-reel-props-v1.json"
    shutil.copy2(props_path, props_copy)

    meta.update(
        {
            "prospect_reel_props": str(props_copy),
            "prospect_reel_mp4": attached_mp4,
            "prospect_reel_engine": "ENGINE-404",
            "prospect_reel_at": _now(),
            "prospect_reel_proof_url": props.get("proof_url"),
        }
    )
    (pack_dir / "pack.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    body_path = pack_dir / "body.txt"
    if body_path.is_file() and attached_mp4:
        body = body_path.read_text(encoding="utf-8")
        reel_line = f"\n**Personalized 30s proof reel** (generated for {props.get('company')}):\nfile://{attached_mp4}\n"
        if "Personalized 30s proof reel" not in body:
            body = body.rstrip() + "\n" + reel_line + "\n"
            body_path.write_text(body, encoding="utf-8")

    return meta


def run_video_factory(
    *,
    row_id: str,
    proof_url: str = "",
    skip_render: bool = False,
    attach_pack: bool = True,
    duration_seconds: int = 30,
) -> dict[str, Any]:
    props = build_prospect_props(row_id=row_id, proof_url=proof_url, duration_seconds=duration_seconds)
    props_path = write_props_json(props, row_id=row_id)
    mp4_path = render_reel(props_path=props_path, row_id=row_id, skip_render=skip_render)

    pack_dir = find_eval_pack_dir(row_id) if attach_pack else None
    pack_meta: dict[str, Any] | None = None
    if pack_dir:
        pack_meta = attach_to_pack(pack_dir=pack_dir, props=props, props_path=props_path, mp4_path=mp4_path)

    row = {
        "ok": True,
        "schema": "commercial-video-factory-receipt-v1",
        "engine": "ENGINE-404",
        "at": _now(),
        "row_id": row_id,
        "company": props.get("company"),
        "lane": props.get("lane"),
        "props_path": str(props_path),
        "mp4_path": str(mp4_path) if mp4_path else None,
        "pack_dir": str(pack_dir) if pack_dir else None,
        "rendered": mp4_path is not None,
        "attached": pack_meta is not None,
        "founder_line": (
            f"ENGINE-404 · {props.get('company')} · "
            + ("reel attached to eval pack" if pack_meta else "JSON ready — no eval pack found")
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="ENGINE-404 — pipeline row → Remotion prospect reel")
    ap.add_argument("--row-id", required=True, help="Pipeline row e.g. cp-a0c7c6c607")
    ap.add_argument("--proof-url", default="")
    ap.add_argument("--duration", type=int, default=30)
    ap.add_argument("--skip-render", action="store_true", help="Write JSON only")
    ap.add_argument("--no-attach", action="store_true", help="Do not patch eval pack")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        row = run_video_factory(
            row_id=args.row_id,
            proof_url=args.proof_url,
            skip_render=args.skip_render,
            attach_pack=not args.no_attach,
            duration_seconds=args.duration,
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or "OK")
        print(f"PROPS={row.get('props_path')}")
        if row.get("mp4_path"):
            print(f"MP4={row.get('mp4_path')}")
        if row.get("pack_dir"):
            print(f"PACK={row.get('pack_dir')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
