#!/usr/bin/env python3
"""Assert W1 player sync markers exist before publishing SourceA commercial film."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SINA = Path.home() / ".sina"
DEFAULT_TIMING = SINA / "commercial-short-film-work-v1" / "beats_timing.json"
DEFAULT_VIDEO = Path.home() / "Desktop" / "SourceA-Commercial-Short.mp4"


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg  # noqa: WPS433

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        from shutil import which

        exe = which("ffmpeg")
        if not exe:
            raise SystemExit("FAIL: ffmpeg missing")
        return exe


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_frame(video: Path, t: float, out: Path) -> bool:
    proc = subprocess.run(
        [_ffmpeg(), "-y", "-ss", str(t), "-i", str(video), "-frames:v", "1", "-q:v", "2", str(out)],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0 and out.is_file() and out.stat().st_size > 1000


def validate(*, timing_path: Path, video_path: Path | None, product: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not timing_path.is_file():
        return {"ok": False, "errors": [f"missing timing: {timing_path}"]}

    timing = _read_json(timing_path)
    capture = timing.get("capture") or {}
    beats = timing.get("beats") or {}

    if product == "sourcea":
        for beat_id, event in (("hook", "w1_block"), ("BLOCK", "w1_block"), ("PROOF", "w1_tamper")):
            events = (capture.get(beat_id) or {}).get("events") or {}
            win = events.get(event)
            if not win or len(win) != 2:
                errors.append(f"{beat_id}: missing capture event {event}")
            elif float(win[1]) - float(win[0]) < 3.0:
                warnings.append(f"{beat_id}: {event} dwell < 3s ({win})")

        beat_windows = beats.get("BLOCK")
        if beat_windows and len(beat_windows) == 2:
            hook_end = (beats.get("hook") or [0, 0])[1]
            block_start = float(beat_windows[0])
            if block_start > 12.0:
                warnings.append(f"BLOCK starts late at {block_start}s — hook may be too long")

    frames: dict[str, str] = {}
    if video_path and video_path.is_file() and product == "sourcea":
        block_win = beats.get("BLOCK")
        proof_win = beats.get("PROOF")
        if block_win and len(block_win) == 2:
            t = float(block_win[0]) + (float(block_win[1]) - float(block_win[0])) * 0.55
            out = Path("/tmp/sourcea-sync-block.jpg")
            if _extract_frame(video_path, t, out):
                frames["BLOCK"] = str(out)
        if proof_win and len(proof_win) == 2:
            t = float(proof_win[0]) + (float(proof_win[1]) - float(proof_win[0])) * 0.55
            out = Path("/tmp/sourcea-sync-proof.jpg")
            if _extract_frame(video_path, t, out):
                frames["PROOF"] = str(out)

    ok = not errors
    return {
        "ok": ok,
        "schema": "validate-commercial-film-sync-v1",
        "product": product,
        "timing_path": str(timing_path),
        "video_path": str(video_path) if video_path else None,
        "errors": errors,
        "warnings": warnings,
        "frames": frames,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", type=Path, default=DEFAULT_TIMING)
    ap.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    ap.add_argument("--product", default="sourcea")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = validate(timing_path=args.timing, video_path=args.video, product=args.product)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"{status}: commercial film sync ({args.product})")
        for err in result.get("errors") or []:
            print(f"  ERROR: {err}")
        for warn in result.get("warnings") or []:
            print(f"  WARN: {warn}")
        for beat, path in (result.get("frames") or {}).items():
            print(f"  frame {beat}: {path}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
