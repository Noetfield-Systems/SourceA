#!/usr/bin/env python3
"""Avatar pipeline v1 — Master image + ElevenLabs VO + optional HeyGen mux.

Routed layer (NOT WitnessBC tier A hero):
  LinkedIn · TrustField social · Noetfield social · Fitness

Flow:
  1. Resolve master image (founder headshot)
  2. ElevenLabs narration from avatar-scripts-v1.json
  3. Optional HeyGen API if HEYGEN_API_KEY wired
  4. Or manual pack (script + voice + image + HeyGen/D-ID steps)
  5. Optional --avatar-video mux with ffmpeg

Usage:
  python3 scripts/avatar_pipeline_v1.py --lane linkedin --json
  python3 scripts/avatar_pipeline_v1.py --lane linkedin --avatar-video ~/Downloads/heygen-out.mp4 --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "avatar-pipeline-config-v1.json"
SCRIPTS_PATH = ROOT / "data" / "avatar-scripts-v1.json"
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _read_env_key(env_path: Path, key: str) -> str:
    if not env_path.is_file():
        return os.environ.get(key, "").strip()
    for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return os.environ.get(key, "").strip()


def _find_master_image(cfg: dict[str, Any]) -> Path | None:
    for raw in cfg.get("master_image_candidates") or []:
        p = _expand(str(raw))
        if p.is_file() and p.stat().st_size > 1000:
            return p
    return None


def _words_to_srt(words: list[dict[str, Any]], out: Path) -> None:
    from film_elevenlabs_wire_v1 import words_to_phrase_srt_entries  # noqa: WPS433

    entries = words_to_phrase_srt_entries(words)
    lines: list[str] = []
    for i, (start, end, text) in enumerate(entries, 1):

        def fmt(t: float) -> str:
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int(round((t - int(t)) * 1000))
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        lines.extend([str(i), f"{fmt(start)} --> {fmt(end)}", text, ""])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mux_video_audio(video: Path, audio: Path, out: Path) -> None:
    ff = _ffmpeg()
    subprocess.run(
        [
            ff,
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(out),
        ],
        check=True,
        capture_output=True,
    )


def _heygen_try_generate(
    api_key: str,
    *,
    image_path: Path,
    audio_path: Path,
    out_mp4: Path,
    cache_dir: Path,
    quality: dict[str, Any],
    lane: str,
) -> tuple[bool, str]:
    """HeyGen v3 photo avatar — upload assets, lipsync ElevenLabs mp3, poll, download."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from heygen_avatar_wire_v1 import generate_talking_photo  # noqa: WPS433

    return generate_talking_photo(
        api_key=api_key,
        image_path=image_path,
        audio_path=audio_path,
        out_mp4=out_mp4,
        cache_dir=cache_dir,
        quality=quality,
        title=f"SourceA {lane} avatar",
    )


def _write_manual_pack(
    work: Path,
    *,
    lane: str,
    script_text: str,
    image: Path,
    voice: Path,
    words: list[dict[str, Any]],
) -> Path:
    manifest = {
        "schema": "avatar-pipeline-manual-v1",
        "at": _now(),
        "lane": lane,
        "steps": [
            "1. Open HeyGen or D-ID studio",
            f"2. Upload master image: {image}",
            f"3. Upload voice track: {voice}",
            "4. Export talking-head MP4 (1080p, neutral background)",
            f"5. Run: python3 scripts/avatar_pipeline_v1.py --lane {lane} --avatar-video <export.mp4> --json",
        ],
        "files": {
            "master_image": str(image),
            "voice_mp3": str(voice),
            "script_txt": str(work / "script.txt"),
            "captions_srt": str(work / "captions.srt") if words else None,
        },
        "blocked_for": ["witnessbc tier A hero", "witnessbc.com homepage hero"],
        "allowed_for": ["LinkedIn profile", "Canada funding intro", "tier C social tests"],
    }
    path = work / "manual-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    readme = work / "HEYGEN-MANUAL-STEPS.md"
    readme.write_text(
        "\n".join(
            [
                "# Avatar pipeline — manual HeyGen / D-ID",
                "",
                f"- **Image:** `{image}`",
                f"- **Voice:** `{voice}`",
                f"- **Script:** `{work / 'script.txt'}`",
                "",
                "Export MP4 from HeyGen, then:",
                "",
                f"```bash",
                f"python3 scripts/avatar_pipeline_v1.py --lane {lane} --avatar-video ~/Downloads/heygen-export.mp4 --json",
                f"```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def run_pipeline(
    *,
    lane: str,
    avatar_video: Path | None = None,
    vo_lane: str = "sourcea",
    skip_voice: bool = False,
    skip_heygen: bool = False,
) -> dict[str, Any]:
    cfg = _read_json(CONFIG_PATH)
    scripts_doc = _read_json(SCRIPTS_PATH)
    lane_cfg = (cfg.get("lanes") or {}).get(lane)
    if not lane_cfg:
        raise SystemExit(f"FAIL: unknown lane {lane!r} — see {CONFIG_PATH}")

    if lane in (cfg.get("blocked_lanes") or []):
        raise SystemExit(f"FAIL: lane {lane!r} blocked for avatar pipeline")

    script_id = str(lane_cfg.get("script_id") or "")
    script_entry = (scripts_doc.get("scripts") or {}).get(script_id)
    if not script_entry:
        raise SystemExit(f"FAIL: script_id {script_id!r} missing in {SCRIPTS_PATH}")

    script_text = str(script_entry.get("full_text") or "").strip()
    if not script_text:
        raise SystemExit(f"FAIL: empty script for {script_id}")

    work_root = _expand(str(cfg.get("work_root") or "~/.sina/avatar-pipeline-v1"))
    work = work_root / lane
    work.mkdir(parents=True, exist_ok=True)

    master = _find_master_image(cfg)
    master_dest: Path | None = None
    if master is None:
        if skip_heygen and not skip_voice:
            pass  # voice-only prep — no headshot required
        else:
            raise SystemExit(
                "FAIL: no master image found.\n"
                "  Drop founder headshot at:\n"
                "    ~/.sina/avatar-pipeline-v1/master-image.jpg\n"
                "  or ~/Desktop/founder-headshot.jpg\n"
                "  Voice-only (no HeyGen): add --skip-heygen"
            )
    else:
        master_dest = work / f"master-image{master.suffix.lower()}"
        if master.resolve() != master_dest.resolve():
            shutil.copy2(master, master_dest)

    script_path = work / "script.txt"
    script_path.write_text(script_text + "\n", encoding="utf-8")

    voice_path = work / "voice.mp3"
    words: list[dict[str, Any]] = []
    voice_engine = "none"
    alignment_engine = "none"

    if not skip_voice:
        sys.path.insert(0, str(ROOT / "scripts"))
        from film_elevenlabs_wire_v1 import set_vo_lane, synthesize_narration  # noqa: WPS433

        set_vo_lane(vo_lane)
        ok, align_eng, words = synthesize_narration(script_text, voice_path, lane=vo_lane)
        if not ok or not voice_path.is_file():
            raise SystemExit("FAIL: ElevenLabs voice synthesis failed — check ~/.sina/elevenlabs-v1.env")
        voice_engine = "elevenlabs"
        alignment_engine = align_eng
        if words:
            words_path = work / "words.json"
            from film_elevenlabs_wire_v1 import write_words_json  # noqa: WPS433

            write_words_json(words, words_path)
            _words_to_srt(words, work / "captions.srt")

    heygen_key = _read_env_key(
        _expand(str((cfg.get("secrets") or {}).get("heygen_env") or "~/.sina/heygen-v1.env")),
        str((cfg.get("secrets") or {}).get("heygen_key") or "HEYGEN_API_KEY"),
    )

    quality_cfg = dict(cfg.get("quality") or {})
    lane_quality = dict((lane_cfg.get("heygen") or {}))
    merged_quality = {**quality_cfg, **lane_quality}

    heygen_ok, heygen_note = False, "skipped"
    if skip_heygen:
        heygen_note = "skipped_by_flag"
    elif not heygen_key:
        heygen_note = "missing HEYGEN_API_KEY — see ~/.sina/heygen-v1.env.example"
        sys.path.insert(0, str(ROOT / "scripts"))
        from heygen_avatar_wire_v1 import write_env_example  # noqa: WPS433

        write_env_example()
    elif avatar_video is None and not skip_voice and master_dest is not None:
        heygen_out = work / "heygen-auto.mp4"
        heygen_ok, heygen_note = _heygen_try_generate(
            heygen_key,
            image_path=master_dest,
            audio_path=voice_path,
            out_mp4=heygen_out,
            cache_dir=work_root / "heygen-cache",
            quality=merged_quality,
            lane=lane,
        )

    final_name = str(lane_cfg.get("output_desktop") or f"{lane}-anchor.mp4")
    final_work = work / final_name.replace(" ", "-").lower()
    if not final_work.suffix:
        final_work = work / "anchor.mp4"

    desktop_out = Path.home() / "Desktop" / final_name
    status = "voice_ready"

    if avatar_video is not None:
        if not avatar_video.is_file():
            raise SystemExit(f"FAIL: avatar video not found: {avatar_video}")
        _mux_video_audio(avatar_video, voice_path, final_work)
        shutil.copy2(final_work, desktop_out)
        status = "muxed"
    elif heygen_ok and (work / "heygen-auto.mp4").is_file():
        shutil.copy2(work / "heygen-auto.mp4", final_work)
        shutil.copy2(final_work, desktop_out)
        status = "heygen_auto"
    else:
        if master_dest is None:
            status = "voice_only"
        else:
            _write_manual_pack(
                work, lane=lane, script_text=script_text, image=master_dest, voice=voice_path, words=words
            )
            status = "manual_pack"

    receipt = {
        "schema": "avatar-pipeline-receipt-v1",
        "at": _now(),
        "status": status,
        "lane": lane,
        "tier": lane_cfg.get("tier"),
        "script_id": script_id,
        "voice_engine": voice_engine,
        "alignment_engine": alignment_engine,
        "heygen_configured": bool(heygen_key),
        "heygen_quality": merged_quality if heygen_key else None,
        "heygen_note": heygen_note,
        "master_image": str(master_dest) if master_dest else None,
        "master_image_missing": master_dest is None,
        "voice_mp3": str(voice_path),
        "work_dir": str(work),
        "output": str(final_work) if final_work.is_file() else None,
        "published_desktop": str(desktop_out) if desktop_out.is_file() else None,
        "routing_ref": "data/commercial-film-routing-v1.json",
        "blocked_for_witnessbc_hero": True,
    }
    receipt_path = SINA / "enforcement" / f"avatar-pipeline-{lane}-receipt-v1.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lane", default="linkedin", help="linkedin | trustfield_social | noetfield_social | fitness_social")
    ap.add_argument("--avatar-video", type=Path, help="HeyGen/D-ID export to mux with voice")
    ap.add_argument("--vo-lane", default="sourcea", choices=["sourcea", "witnessbc"])
    ap.add_argument("--skip-voice", action="store_true")
    ap.add_argument("--skip-heygen", action="store_true", help="ElevenLabs voice only — skip HeyGen API")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    receipt = run_pipeline(
        lane=args.lane,
        avatar_video=args.avatar_video,
        vo_lane=args.vo_lane,
        skip_voice=args.skip_voice,
        skip_heygen=args.skip_heygen,
    )
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: avatar pipeline {receipt['status']} → {receipt.get('work_dir')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
