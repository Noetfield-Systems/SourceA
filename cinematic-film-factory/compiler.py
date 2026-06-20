#!/usr/bin/env python3
"""Cinematic film compiler — GPT factory pathway for SourceA.

Truth → beats → script → TTS → captions → cinematic assemble → critic → memory.
Receipt: ~/.sina/enforcement/cinematic-film-factory-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "cinematic-film-factory-v1.json"
RECEIPT = SINA / "enforcement" / "cinematic-film-factory-receipt-v1.json"

sys.path.insert(0, str(ROOT / "cinematic-film-factory"))
sys.path.insert(0, str(ROOT / "scripts"))

from assemble import assemble, _ffmpeg  # noqa: E402
from capture import capture_sourcea_w1, capture_witnessbc  # noqa: E402
from captions import build_srt  # noqa: E402
from film_memory import evolve_rules_from_incident, load_rules, record_incident  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _probe(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False}
    ff = _ffmpeg()
    proc = subprocess.run([ff, "-i", str(path)], capture_output=True, text=True)
    stderr = proc.stderr
    dur_m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", stderr)
    duration = 0.0
    if dur_m:
        h, m, s = dur_m.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)
    video_m = re.search(r"Video:.* (\d+)x(\d+)", stderr)
    width = height = 0
    if video_m:
        width, height = int(video_m.group(1)), int(video_m.group(2))
    return {
        "exists": True,
        "path": str(path),
        "duration_s": round(duration, 2),
        "width": width,
        "height": height,
        "has_audio": "Audio:" in stderr,
        "size_bytes": path.stat().st_size,
    }


def _mp3_to_wav(mp3: Path, wav: Path) -> None:
    ff = _ffmpeg()
    subprocess.run(
        [ff, "-y", "-i", str(mp3), "-ar", "48000", "-ac", "2", str(wav)],
        check=True,
        capture_output=True,
    )


def _edge_tts(text: str, out_mp3: Path) -> bool:
    try:
        import asyncio
        import edge_tts

        async def _run() -> None:
            comm = edge_tts.Communicate(text, "en-US-AndrewMultilingualNeural", rate="-5%")
            await comm.save(str(out_mp3))

        asyncio.run(_run())
        return out_mp3.stat().st_size > 500
    except Exception:
        return False


def _say_tts(text: str, out_wav: Path) -> None:
    aiff = out_wav.with_suffix(".aiff")
    subprocess.run(["say", "-v", "Daniel", "-r", "175", "-o", str(aiff), text], check=True, timeout=180)
    subprocess.run(
        [_ffmpeg(), "-y", "-i", str(aiff), "-ar", "48000", "-ac", "2", str(out_wav)],
        check=True,
        capture_output=True,
    )


def generate_voice(text: str, assets: Path, *, vo_lane: str) -> tuple[Path, str]:
    assets.mkdir(parents=True, exist_ok=True)
    wav = assets / "voice.wav"
    mp3 = assets / "voice.mp3"
    try:
        from film_elevenlabs_wire_v1 import synthesize_narration  # noqa: WPS433

        ok, _, _ = synthesize_narration(text, mp3, lane=vo_lane)
        if ok and mp3.is_file():
            _mp3_to_wav(mp3, wav)
            return wav, "elevenlabs"
    except Exception:
        pass
    if _edge_tts(text, mp3):
        _mp3_to_wav(mp3, wav)
        return wav, "edge_neural"
    _say_tts(text, wav)
    return wav, "mac_say"


def run_capture(
    lane: str,
    lane_cfg: dict[str, Any],
    work_dir: Path,
    *,
    headed: bool,
    hold_block: float,
) -> dict[str, float]:
    assets = work_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    headless = not headed
    rules = load_rules()
    hold = float(rules.get("rules", {}).get("block_event", {}).get("hold_seconds_min", hold_block))

    if lane == "witnessbc":
        raw, beats = capture_witnessbc(
            lane_cfg["capture_base"],
            headless=headless,
            video_dir=assets,
            hold_block_s=hold,
        )
    else:
        raw, beats = capture_sourcea_w1(
            lane_cfg["capture_base"],
            headless=headless,
            video_dir=assets,
        )

    beats_path = work_dir / "beats.json"
    beats_path.write_text(json.dumps(beats, indent=2) + "\n", encoding="utf-8")
    return beats


def run_compiler(
    *,
    lane: str,
    skip_capture: bool = False,
    headed: bool = False,
    publish_desktop: bool = False,
    hold_block: float = 6.0,
) -> dict[str, Any]:
    cfg = _read_json(CONFIG)
    lane_cfg = cfg["lanes"][lane]
    work_dir = SINA / "cinematic-film-factory" / lane
    work_dir.mkdir(parents=True, exist_ok=True)
    assets = work_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    script_path = ROOT / lane_cfg["script"]
    script_text = script_path.read_text(encoding="utf-8").strip()
    (work_dir / "script.txt").write_text(script_text + "\n", encoding="utf-8")

    rules = load_rules()
    receipt: dict[str, Any] = {
        "schema": "cinematic-film-factory-receipt-v1",
        "at": _now(),
        "lane": lane,
        "pathway": "cinematic-film-factory",
        "steps": [],
    }

    if not skip_capture:
        beats = run_capture(lane, lane_cfg, work_dir, headed=headed, hold_block=hold_block)
        receipt["steps"].append({"step": "capture_truth", "ok": True, "beats": beats})
    else:
        beats_path = work_dir / "beats.json"
        if not beats_path.is_file():
            raise SystemExit("FAIL: --skip-capture but beats.json missing")
        beats = _read_json(beats_path)
        receipt["steps"].append({"step": "capture_truth", "skipped": True})

    voice_path, vo_engine = generate_voice(script_text, assets, vo_lane=lane_cfg.get("vo_lane", lane))
    receipt["steps"].append({"step": "tts_voice", "ok": True, "engine": vo_engine, "path": str(voice_path)})

    srt = build_srt(beats, [ln.strip() for ln in script_text.splitlines() if ln.strip()])
    captions_path = assets / "captions.srt"
    captions_path.write_text(srt + "\n", encoding="utf-8")
    receipt["steps"].append({"step": "captions_from_beats", "ok": True, "path": str(captions_path)})

    final = assemble(work_dir, beats=beats, rules=rules)
    probe = _probe(final)
    receipt["steps"].append({"step": "cinematic_assemble", "ok": True, "final": str(final), "probe": probe})

    critic = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "commercial_film_critic_circle_v1.py"), "--json"],
        capture_output=True,
        text=True,
    )
    critic_data: dict[str, Any] = {}
    try:
        critic_data = json.loads(critic.stdout)
    except Exception:
        critic_data = {"ok": False, "parse_error": True, "stderr": critic.stderr[:500]}
    receipt["steps"].append({"step": "critic_circle_judge", "verdict": critic_data.get("verdict", "UNKNOWN")})

    issues = []
    if critic_data.get("verdict") != "PASS":
        for row in critic_data.get("assets", []):
            if row.get("lane") == lane or lane in str(row.get("path", "")):
                issues.extend(row.get("issues", []))
        if not issues:
            issues = ["critic_blocked_public_hero"]

    video_id = f"{lane}-cinematic-factory-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    incident = record_incident(
        lane=lane,
        video_id=video_id,
        beats=beats,
        critic_verdict=str(critic_data.get("verdict", "BLOCK")),
        issues=issues,
        probe=probe,
    )
    evolved = evolve_rules_from_incident(incident)
    receipt["steps"].append(
        {
            "step": "film_memory_incident",
            "ok": True,
            "incident_id": video_id,
            "next_fix": incident.get("next_fix"),
            "rules_evolved": bool(evolved),
        }
    )

    desktop_name = lane_cfg.get("output_desktop", f"{lane}-Cinematic-Factory.mp4")
    desktop_path = Path.home() / "Desktop" / desktop_name
    shutil.copy2(final, desktop_path)
    receipt["desktop_copy"] = str(desktop_path)
    receipt["publish_allowed"] = critic_data.get("verdict") == "PASS"
    receipt["factory_now_line"] = (
        f"cinematic-factory · {lane} · {probe.get('duration_s', 0)}s · critic={critic_data.get('verdict', 'BLOCK')}"
    )

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Cinematic film factory compiler")
    ap.add_argument("--lane", required=True, choices=("witnessbc", "sourcea"))
    ap.add_argument("--skip-capture", action="store_true", help="Reuse beats + raw in work dir")
    ap.add_argument("--headed", action="store_true", help="Headed Playwright (human-smooth)")
    ap.add_argument("--publish-desktop", action="store_true")
    ap.add_argument("--hold-block", type=float, default=6.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--force", action="store_true", help="Override render freeze (founder only)")
    args = ap.parse_args()

    from commercial_film_render_guard_v1 import assert_render_allowed  # noqa: WPS433

    assert_render_allowed(force=args.force)

    receipt = run_compiler(
        lane=args.lane,
        skip_capture=args.skip_capture,
        headed=args.headed,
        publish_desktop=args.publish_desktop,
        hold_block=args.hold_block,
    )
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(receipt.get("factory_now_line", "OK cinematic factory"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
