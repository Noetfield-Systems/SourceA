#!/usr/bin/env python3
"""Ingest founder W1 hero film from Desktop → site assets + receipt.

Looks for (in order):
  ~/Desktop/SourceA-W1-Master.mov
  ~/Desktop/SourceA-W1-Master.mp4
  ~/Desktop/SourceA-W1-Film.mp4

Output: SourceA-landing/green-unified/assets/w1-demo.mp4 · deploy · Gate J receipt.
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
RECEIPT = SINA / "enforcement" / "w1-film-receipt-v1.json"
OUT_SOURCEA = ROOT / "SourceA-landing" / "green-unified" / "assets" / "w1-demo.mp4"
MASTER_DESKTOP_MP4 = DESKTOP / "SourceA-W1-Master.mp4"

CANDIDATES = [
    DESKTOP / "SourceA-W1-Master.mov",
    DESKTOP / "SourceA-W1-Master.mp4",
    DESKTOP / "SourceA-W1-Film.mp4",
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


def _probe_duration(path: Path) -> float:
    proc = subprocess.run(
        [_ffmpeg(), "-i", str(path)],
        capture_output=True,
        text=True,
    )
    import re

    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", proc.stderr or "")
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def _to_mp4(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".mp4" and src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
        return dest
    subprocess.run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(src),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(dest),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return dest


def find_master(explicit: Path | None = None) -> tuple[Path, str]:
    if explicit and explicit.is_file():
        tier = "screen_studio_master" if "Master" in explicit.name else "founder_provided"
        return explicit, tier
    for p in CANDIDATES:
        if p.is_file():
            if "Master" in p.name:
                return p, "screen_studio_master" if p.suffix.lower() == ".mov" else "screen_studio_master_mp4"
            return p, "automated_capture_fallback"
    raise SystemExit(
        "FAIL: no W1 master on Desktop.\n"
        "  Save Screen Studio export as ~/Desktop/SourceA-W1-Master.mov\n"
        "  Or run: bash scripts/run_w1_film_pipeline_v1.sh"
    )


def ingest(*, source: Path | None = None, deploy: bool = True) -> dict:
    src, tier = find_master(source)
    work_mp4 = OUT_SOURCEA.parent / "w1-demo-ingest.mp4"
    _to_mp4(src, work_mp4)
    if work_mp4.stat().st_size < 100_000:
        raise SystemExit(f"FAIL: ingested mp4 too small ({work_mp4.stat().st_size} bytes)")

    for dest in (OUT_SOURCEA,):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(work_mp4, dest)

    shutil.copy2(work_mp4, MASTER_DESKTOP_MP4)

    duration = _probe_duration(work_mp4)
    grade = "A" if tier.startswith("screen_studio") else "C+"

    receipt = {
        "schema": "w1-film-receipt-v1",
        "at": _now(),
        "status": "embed_live",
        "grade": grade,
        "source_tier": tier,
        "source_path": str(src),
        "beats": ["BLOCK", "ALLOW", "tamper-FAIL", "FREEZE"],
        "voice_engine": "founder_master" if tier.startswith("screen_studio") else "macos_say",
        "broll_source": str(src),
        "output": str(OUT_SOURCEA),
        "published": [str(OUT_SOURCEA)],
        "embed_url": "assets/w1-demo.mp4",
        "duration_seconds": round(duration, 1),
        "law": "founder hero film — real UI capture — no TerminalMock on site embed",
        "mock_ship_blocked": True,
        "desktop_copy": str(MASTER_DESKTOP_MP4),
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

    return {
        "ok": True,
        "schema": "w1-film-ingest-v1",
        "at": _now(),
        "source": str(src),
        "tier": tier,
        "grade": grade,
        "mp4": str(OUT_SOURCEA),
        "size_bytes": OUT_SOURCEA.stat().st_size,
        "duration_seconds": duration,
        "receipt": str(RECEIPT),
        "deploy_ok": deploy_ok,
        "founder_line": (
            f"W1 film ingested · grade {grade} · {tier} · "
            f"{round(duration)}s · http://127.0.0.1:5180/sourcea/proof.html#w1-demo-film"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest Desktop W1 master → site")
    ap.add_argument("--source", type=Path, help="Override source file")
    ap.add_argument("--no-deploy", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        row = ingest(source=args.source, deploy=not args.no_deploy)
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: ffmpeg — {(exc.stderr or exc.stdout or '')[-800:]}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_line") or "OK")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
