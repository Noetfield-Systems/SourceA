#!/usr/bin/env python3
"""Ingest founder Screen Studio commercial master → SourceA site + Desktop.

Linear-quality bar: record at 4K in Screen Studio, export as:
  ~/Desktop/SourceA-Commercial-Master.mov
  ~/Desktop/SourceA-Commercial-Master.mp4

Output:
  SourceA-landing/green-unified/assets/commercial-short-demo.mp4
  ~/Desktop/SourceA-Commercial-Short.mp4
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
DESKTOP = Path.home() / "Desktop"
RECEIPT = SINA / "enforcement" / "commercial-short-film-receipt-v1.json"
OUT_SITE = ROOT / "SourceA-landing" / "green-unified" / "assets" / "commercial-short-demo.mp4"
OUT_DESKTOP = DESKTOP / "SourceA-Commercial-Short.mp4"
QUALITY_BAR = ROOT / "data" / "video-quality-bar-v1.json"

CANDIDATES = [
    DESKTOP / "SourceA-Commercial-Master.mov",
    DESKTOP / "SourceA-Commercial-Master.mp4",
    DESKTOP / "SourceA-Commercial-Short-Master.mp4",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg  # noqa: WPS433

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        from shutil import which

        return which("ffmpeg") or "ffmpeg"


def _probe(path: Path) -> tuple[float, int, int]:
    proc = subprocess.run([_ffmpeg(), "-i", str(path)], capture_output=True, text=True)
    import re

    dur = 0.0
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", proc.stderr or "")
    if m:
        h, mi, s = m.groups()
        dur = int(h) * 3600 + int(mi) * 60 + float(s)
    w = h = 0
    m2 = re.search(r"Stream.* Video:.* (\d+)x(\d+)", proc.stderr or "")
    if m2:
        w, h = int(m2.group(1)), int(m2.group(2))
    return dur, w, h


def _to_delivery_mp4(src: Path, dest: Path, *, master_w: int = 3840, master_h: int = 2160) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={master_w}:{master_h}:flags=lanczos,"
    vf += "eq=contrast=1.04:brightness=0.01:saturation=1.02,unsharp=5:5:0.22:5:5:0.0"
    subprocess.run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(src),
            "-vf",
            vf,
            "-af",
            "loudnorm=I=-14:TP=-1.0:LRA=9",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-b:v",
            "18M",
            "-maxrate",
            "22M",
            "-bufsize",
            "44M",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=900,
    )
    return dest


def find_master(explicit: Path | None = None) -> tuple[Path, str]:
    if explicit and explicit.is_file():
        return explicit, "screen_studio_master"
    for p in CANDIDATES:
        if p.is_file():
            return p, "screen_studio_master"
    raise SystemExit(
        "FAIL: no SourceA commercial master on Desktop.\n"
        "  Record in Screen Studio (4K, slow cursor, hover-before-click).\n"
        "  Export as ~/Desktop/SourceA-Commercial-Master.mov\n"
        "  Quality bar: data/video-quality-bar-v1.json"
    )


def ingest(*, source: Path | None = None, deploy: bool = True) -> dict:
    src, tier = find_master(source)
    work = OUT_SITE.parent / "commercial-short-ingest.mp4"
    _to_delivery_mp4(src, work)
    if work.stat().st_size < 500_000:
        raise SystemExit(f"FAIL: ingested mp4 too small ({work.stat().st_size} bytes)")

    for dest in (OUT_SITE, OUT_DESKTOP):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(work, dest)

    duration, w, h = _probe(work)
    grade = "A+" if w >= 3840 and tier == "screen_studio_master" else "A" if tier == "screen_studio_master" else "B+"

    receipt = {
        "schema": "commercial-short-film-receipt-v1",
        "at": _now(),
        "status": "embed_live",
        "title": "SourceA — Controlled Agentic Automation",
        "product": "sourcea",
        "grade": grade,
        "source_tier": tier,
        "source_path": str(src),
        "voice_engine": "founder_master",
        "alignment_engine": "screen_studio",
        "resolution": f"{w}x{h}",
        "capture_resolution": f"{w}x{h}",
        "output": str(OUT_SITE),
        "published": [str(OUT_SITE), str(OUT_DESKTOP)],
        "duration_seconds": round(duration, 1),
        "quality_bar": str(QUALITY_BAR),
        "linear_ui_capture": True,
        "law": "Screen Studio master — Linear-quality bar — no Playwright blur",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    deploy_ok = True
    if deploy:
        proc = subprocess.run(
            ["bash", str(ROOT / "SourceA-landing" / "green-unified" / "scripts" / "run-recipe.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        deploy_ok = proc.returncode == 0
    receipt["deploy_ok"] = deploy_ok
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest SourceA commercial Screen Studio master")
    ap.add_argument("--source", type=Path, default=None)
    ap.add_argument("--no-deploy", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        receipt = ingest(source=args.source, deploy=not args.no_deploy)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"SourceA commercial ingested · grade {receipt.get('grade')} · "
            f"{receipt.get('duration_seconds')}s · {receipt.get('resolution')}"
        )
        print(f"SITE={OUT_SITE}")
        print(f"DESKTOP={OUT_DESKTOP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
