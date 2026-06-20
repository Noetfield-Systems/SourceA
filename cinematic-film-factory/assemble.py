#!/usr/bin/env python3
"""Cinematic factory — FFmpeg cinema engine (grade, zoom on block, VO, SFX, subs)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from film_memory import load_rules

ROOT = Path(__file__).resolve().parents[1]


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


def _probe_duration(path: Path) -> float:
    ff = _ffmpeg()
    proc = subprocess.run([ff, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if not m:
        return 30.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def _transcode_webm_to_mp4(src: Path, dst: Path) -> None:
    ff = _ffmpeg()
    subprocess.run(
        [
            ff,
            "-y",
            "-i",
            str(src),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dst),
        ],
        check=True,
        capture_output=True,
    )


def _ensure_capture_mp4(work_dir: Path) -> Path:
    assets = work_dir / "assets"
    mp4 = assets / "capture.mp4"
    if mp4.is_file():
        return mp4
    webms = sorted(assets.glob("*.webm"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not webms:
        raise SystemExit(f"FAIL: no capture video in {assets}")
    _transcode_webm_to_mp4(webms[0], mp4)
    return mp4


def _synth_sfx(work_dir: Path, rules: dict[str, Any], beats: dict[str, float]) -> Path | None:
    """Minimal sound design — click, error tone, confirmation (sine bursts via ffmpeg)."""
    try:
        ff = _ffmpeg()
        assets = work_dir / "assets"
        sfx_path = assets / "sfx.wav"
        block_t = beats.get("block", beats.get("block_state", 8))
        receipt_t = beats.get("receipt", beats.get("proof_generation", block_t + 6))
        dur = max(_probe_duration(assets / "capture.mp4") if (assets / "capture.mp4").is_file() else 45, 20)

        filters = [
            f"anullsrc=r=48000:cl=stereo:d={dur}[base]",
            f"sine=frequency=880:duration=0.08,volume=0.25[click]",
            f"sine=frequency=220:duration=0.35,volume=0.18[err]",
            f"sine=frequency=660:duration=0.2,volume=0.2[ding]",
        ]
        mix = (
            f"[base][click]amix=inputs=2:duration=first:dropout_transition=0,"
            f"adelay={int(block_t * 1000)}|{int(block_t * 1000)}[m1];"
            f"[m1][err]amix=inputs=2:duration=first:dropout_transition=0,"
            f"adelay={int((block_t + 0.2) * 1000)}|{int((block_t + 0.2) * 1000)}[m2];"
            f"[m2][ding]amix=inputs=2:duration=first:dropout_transition=0,"
            f"adelay={int(receipt_t * 1000)}|{int(receipt_t * 1000)}[out]"
        )
        fc = ";".join(filters) + ";" + mix
        subprocess.run(
            [ff, "-y", "-filter_complex", fc, "-map", "[out]", str(sfx_path)],
            check=True,
            capture_output=True,
        )
        return sfx_path if sfx_path.is_file() else None
    except Exception:
        return None


def assemble(
    work_dir: Path,
    *,
    beats: dict[str, float],
    rules: dict[str, Any] | None = None,
) -> Path:
    rules = rules or load_rules()
    grade = rules.get("ffmpeg_grade", {})
    block_rules = rules.get("rules", {}).get("block_event", {})
    zoom = float(block_rules.get("zoom_factor", 1.12))
    block_t = beats.get("block", beats.get("block_state", 10))
    zoom_dur = float(block_rules.get("zoom_duration_seconds", 6.0))
    block_end = block_t + zoom_dur

    assets = work_dir / "assets"
    out_dir = work_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    video = _ensure_capture_mp4(work_dir)
    voice = assets / "voice.wav"
    subs = assets / "captions.srt"
    final = out_dir / "final.mp4"

    if not voice.is_file():
        raise SystemExit(f"FAIL: missing voice.wav at {voice}")

    subs_esc = str(subs).replace(":", "\\:").replace("'", "\\'")
    contrast = grade.get("contrast", 1.08)
    brightness = grade.get("brightness", -0.02)
    saturation = grade.get("saturation", 1.05)
    crf = str(grade.get("crf", 18))
    preset = grade.get("preset", "slow")

    vf = (
        f"scale=1920:1080,"
        f"zoompan=z='if(between(in_time,{block_t},{block_end}),{zoom},1.0)':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
        f"subtitles='{subs_esc}':force_style='Fontsize=28,Outline=1,Shadow=0,Alignment=2',"
        f"eq=contrast={contrast}:brightness={brightness}:saturation={saturation}"
    )

    sfx = _synth_sfx(work_dir, rules, beats)
    ff = _ffmpeg()
    cmd: list[str] = [ff, "-y", "-i", str(video), "-i", str(voice)]
    if sfx and sfx.is_file():
        cmd.extend(["-i", str(sfx)])
        cmd.extend(
            [
                "-filter_complex",
                f"[0:v]{vf}[v];[1:a][2:a]amix=inputs=2:duration=shortest:dropout_transition=2[a]",
                "-map",
                "[v]",
                "-map",
                "[a]",
            ]
        )
    else:
        cmd.extend(["-vf", vf, "-map", "0:v", "-map", "1:a"])

    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            crf,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(final),
        ]
    )
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return final


def main() -> None:
    ap = argparse.ArgumentParser(description="Cinematic FFmpeg assembly")
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    beats = json.loads((args.work_dir / "beats.json").read_text(encoding="utf-8"))
    final = assemble(args.work_dir, beats=beats)
    payload = {"ok": True, "final": str(final)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"OK final → {final}")


if __name__ == "__main__":
    main()
