#!/usr/bin/env python3
"""Generate W1 proof film — real UI B-roll + AI narration → w1-demo.mp4.

Law: >=70% real product UI (AEG capture or fresh Playwright webm).
Voice: shared ElevenLabs key in ~/.sina/elevenlabs-v1.env · else macOS say.
Output: SourceA-landing/green-unified/assets/w1-demo.mp4 · w1-film receipt.

No outbound email — video artifact only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from film_elevenlabs_wire_v1 import has_elevenlabs, set_vo_lane, synthesize_narration  # noqa: E402

SINA = Path.home() / ".sina"
BEATS_JSON = ROOT / "data" / "w1-film-beats-v1.json"
DEFAULT_LANDING_URLS = [
    "http://127.0.0.1:5180/sourcea/",
    "http://127.0.0.1:5180/sourcea/proof/live.html",
    "http://127.0.0.1:5180/sourcea/proof.html#w1-demo-film",
    "http://127.0.0.1:5180/sourcea/platform.html",
    "http://127.0.0.1:5180/sourcea/scenario.html#proof-quiz",
]
DEFAULT_UI_URL = os.environ.get("AEG_UI_URL", "http://127.0.0.1:13023/")
AEG_LATEST = SINA / "aeg-latest-receipt-v1.json"
WORK = SINA / "w1-film-work-v1"
RECEIPT = SINA / "enforcement" / "w1-film-receipt-v1.json"
SECRETS = SINA / "secrets.env"
OUT_SOURCEA = ROOT / "SourceA-landing" / "green-unified" / "assets" / "w1-demo.mp4"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg  # noqa: WPS433

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        from shutil import which

        exe = which("ffmpeg")
        if not exe:
            raise SystemExit("FAIL: ffmpeg missing — pip install imageio-ffmpeg")
        return exe


def _run(cmd: list[str], *, timeout: int = 300) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "ffmpeg failed").strip())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _secret(key: str) -> str:
    if not SECRETS.is_file():
        return ""
    for line in SECRETS.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _capture_broll_playwright(
    out_webm: Path,
    *,
    urls: list[str] | None = None,
    seconds_per_url: int = 6,
) -> Path:
    """Record real product UI from landing pages (no generative T2V)."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: WPS433
    except ImportError as exc:
        raise SystemExit(f"FAIL: playwright required for B-roll capture — {exc}") from exc

    targets = urls or DEFAULT_LANDING_URLS
    out_webm.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_webm.parent / "capture-videos"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=str(tmp_dir),
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        page = context.new_page()
        for url in targets:
            try:
                page.goto(url, wait_until="networkidle", timeout=25000)
            except Exception:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(max(1, seconds_per_url) * 1000)
            page.evaluate("window.scrollTo(0, Math.min(480, document.body.scrollHeight * 0.35))")
            page.wait_for_timeout(800)
        page.close()
        context.close()
        browser.close()

    videos = sorted(tmp_dir.glob("*.webm"), key=lambda p: p.stat().st_size, reverse=True)
    if not videos or videos[0].stat().st_size < 1000:
        raise SystemExit("FAIL: Playwright capture produced no webm")
    shutil.move(str(videos[0]), str(out_webm))
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return out_webm


def _resolve_broll(explicit: Path | None, *, capture_landing: bool = False) -> Path:
    if explicit and explicit.is_file():
        return explicit
    if capture_landing:
        captured = WORK / "landing-broll.webm"
        return _capture_broll_playwright(captured)
    if AEG_LATEST.is_file():
        manifest = _read_json(AEG_LATEST)
        ui = manifest.get("ui") or {}
        webm = ui.get("webm")
        if webm and Path(webm).is_file():
            return Path(webm)
        bundle = manifest.get("bundle_dir")
        if bundle:
            candidate = Path(bundle) / "ui.webm"
            if candidate.is_file():
                return candidate
    for bundle in sorted((SINA / "aeg").glob("aeg-*"), reverse=True):
        candidate = bundle / "ui.webm"
        if candidate.is_file():
            return candidate
    raise SystemExit(
        "FAIL: no ui.webm B-roll — run with --capture-landing (SourceA :5180) "
        "or critic_boot --aeg with Chat Unify :13023 up"
    )


def _say_tts(text: str, out_aiff: Path) -> None:
    out_aiff.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["say", "-o", str(out_aiff), text], check=True, timeout=120)


def _narration_audio(text: str, work: Path, stem: str) -> tuple[Path, str]:
    mp3 = work / f"{stem}.mp3"
    m4a = work / f"{stem}.m4a"
    aiff = work / f"{stem}.aiff"
    ok, _, _ = synthesize_narration(text, mp3, lane="sourcea")
    if ok:
        return mp3, "elevenlabs"
    _say_tts(text, aiff)
    _run([_ffmpeg(), "-y", "-i", str(aiff), "-c:a", "aac", "-b:a", "128k", str(m4a)])
    return m4a, "macos_say"


def _title_card_png(title: str, subtitle: str, out: Path, *, beat_id: str) -> None:
    from PIL import Image, ImageDraw, ImageFont  # noqa: WPS433

    w, h = 1280, 720
    colors = {
        "BLOCK": ("#1a0a0a", "#ef4444"),
        "ALLOW": ("#0a1a12", "#34d399"),
        "tamper-FAIL": ("#1a1208", "#f59e0b"),
        "FREEZE": ("#0a0f1a", "#60a5fa"),
    }
    bg, accent = colors.get(beat_id, ("#0b1220", "#2dd4bf"))
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)
    try:
        font_l = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 52)
        font_s = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
    except OSError:
        font_l = ImageFont.load_default()
        font_s = font_l
    draw.text((64, h // 2 - 60), title, fill=accent, font=font_l)
    draw.text((64, h // 2 + 20), subtitle, fill="#94a3b8", font=font_s)
    draw.rectangle([0, 0, w, 6], fill=accent)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def _png_to_video(png: Path, seconds: float, out: Path) -> None:
    _run(
        [
            _ffmpeg(),
            "-y",
            "-loop",
            "1",
            "-i",
            str(png),
            "-c:v",
            "libx264",
            "-t",
            str(seconds),
            "-pix_fmt",
            "yuv420p",
            "-r",
            "30",
            str(out),
        ]
    )


def _broll_clip(src: Path, seconds: float, out: Path, *, offset: float = 0) -> None:
    _run(
        [
            _ffmpeg(),
            "-y",
            "-stream_loop",
            "-1",
            "-ss",
            str(max(0.0, offset % 6.0)),
            "-i",
            str(src),
            "-t",
            str(seconds),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            "-r",
            "30",
            str(out),
        ]
    )


def _mux_video_audio(video: Path, audio: Path, out: Path, *, pad_video: float | None = None) -> None:
    probe = subprocess.run(
        [_ffmpeg(), "-i", str(audio)],
        capture_output=True,
        text=True,
    )
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
    audio_dur = 5.0
    if m:
        h, mi, s = m.groups()
        audio_dur = int(h) * 3600 + int(mi) * 60 + float(s)
    target = pad_video if pad_video is not None else max(audio_dur, 3.0)
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
            "-t",
            str(target),
            "-shortest",
            str(out),
        ]
    )


def _concat_segments(segments: list[Path], out: Path) -> None:
    list_file = out.parent / "concat.txt"
    list_file.write_text("\n".join(f"file '{s}'" for s in segments) + "\n", encoding="utf-8")
    _run(
        [
            _ffmpeg(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ]
    )


def _publish_proof_embed() -> None:
    """Inject <video> into green-unified proof.html when w1-demo.mp4 exists."""
    proof = ROOT / "SourceA-landing" / "green-unified" / "proof.html"
    if not proof.is_file() or not OUT_SOURCEA.is_file():
        return
    text = proof.read_text(encoding="utf-8")
    if "assets/w1-demo.mp4" in text:
        return
    video_block = """<video class="sa-demo-film-video sa-w1-film-mp4" controls preload="metadata" poster="/sourcea/assets/w1-demo-poster.svg" playsinline>
            <source src="/sourcea/assets/w1-demo.mp4" type="video/mp4" />
          </video>"""
    marker = '<div class="sa-w1-player" id="sa-w1-player"'
    if marker not in text:
        return
    text = text.replace(
        '        <div class="sa-demo-film-media">\n          <div class="sa-w1-player" id="sa-w1-player"',
        f'        <div class="sa-demo-film-media">\n          {video_block}\n          <p class="sa-metric-note">W1 proof film · real UI capture · AI narration</p>\n          <div class="sa-w1-player" id="sa-w1-player"',
    )
    proof.write_text(text, encoding="utf-8")


def generate_film(
    *,
    broll: Path | None = None,
    beats_path: Path = BEATS_JSON,
    skip_publish: bool = False,
    capture_landing: bool = False,
) -> dict[str, Any]:
    set_vo_lane("sourcea")
    spec = _read_json(beats_path)
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    broll_path = broll if broll and broll.is_file() else _resolve_broll(None, capture_landing=capture_landing)

    segments: list[Path] = []
    voice_engine = "macos_say"
    hook_mp3, hook_eng = _narration_audio(spec.get("hook", ""), WORK, "hook")
    if hook_eng == "elevenlabs":
        voice_engine = "elevenlabs"

    hook_card = WORK / "hook.png"
    _title_card_png("SourceA W1", spec.get("hook", ""), hook_card, beat_id="FREEZE")
    hook_vid = WORK / "hook-card.mp4"
    _png_to_video(hook_card, 2.5, hook_vid)
    hook_mux = WORK / "hook-mux.mp4"
    _mux_video_audio(hook_vid, hook_mp3, hook_mux, pad_video=4.0)
    segments.append(hook_mux)

    offset = 0.0
    beat_ids: list[str] = []
    for i, beat in enumerate(spec.get("beats") or []):
        bid = str(beat.get("id") or f"beat{i}")
        beat_ids.append(bid)
        card_png = WORK / f"{bid}-card.png"
        _title_card_png(str(beat.get("title") or bid), str(beat.get("label") or ""), card_png, beat_id=bid)
        card_vid = WORK / f"{bid}-card.mp4"
        _png_to_video(card_png, float(beat.get("card_seconds") or 3), card_vid)

        broll_sec = float(beat.get("broll_seconds") or 10)
        broll_vid = WORK / f"{bid}-broll.mp4"
        _broll_clip(broll_path, broll_sec, broll_vid, offset=offset)
        offset = (offset + broll_sec * 0.35) % max(broll_sec, 1)

        narr_mp3, narr_eng = _narration_audio(str(beat.get("narration") or ""), WORK, f"{bid}-narr")
        if narr_eng == "elevenlabs":
            voice_engine = "elevenlabs"
        card_mux = WORK / f"{bid}-card-mux.mp4"
        _mux_video_audio(card_vid, narr_mp3, card_mux)
        broll_mux = WORK / f"{bid}-broll-mux.mp4"
        _mux_video_audio(broll_vid, narr_mp3, broll_mux, pad_video=broll_sec)
        segments.extend([card_mux, broll_mux])

    cta = spec.get("cta") or {}
    if cta.get("narration"):
        cta_png = WORK / "cta.png"
        _title_card_png("Book 15 minutes", "hello@sourcea.app", cta_png, beat_id="ALLOW")
        cta_vid = WORK / "cta-card.mp4"
        _png_to_video(cta_png, float(cta.get("seconds") or 8), cta_vid)
        cta_mp3, cta_eng = _narration_audio(str(cta["narration"]), WORK, "cta")
        if cta_eng == "elevenlabs":
            voice_engine = "elevenlabs"
        cta_mux = WORK / "cta-mux.mp4"
        _mux_video_audio(cta_vid, cta_mp3, cta_mux)
        segments.append(cta_mux)

    out_tmp = WORK / "w1-demo.mp4"
    _concat_segments(segments, out_tmp)

    published: list[str] = []
    if not skip_publish:
        for dest in (OUT_SOURCEA,):
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(out_tmp, dest)
            published.append(str(dest))
        _publish_proof_embed()

    receipt = {
        "schema": "w1-film-receipt-v1",
        "at": _now(),
        "status": "embed_live" if published else "filmed",
        "beats": beat_ids,
        "voice_engine": voice_engine,
        "broll_source": str(broll_path),
        "output": str(out_tmp),
        "published": published,
        "embed_url": "assets/w1-demo.mp4",
        "duration_target_seconds": sum(
            float(b.get("card_seconds") or 3) + float(b.get("broll_seconds") or 10)
            for b in (spec.get("beats") or [])
        ),
        "law": "AI-generated narration + real UI B-roll — no fake T2V dashboard",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate W1 AI proof film (real UI + AI voice)")
    ap.add_argument("--broll", type=Path, help="ui.webm path (default: latest AEG)")
    ap.add_argument("--beats", type=Path, default=BEATS_JSON)
    ap.add_argument("--capture-landing", action="store_true", help="Capture B-roll from SourceA :5180 via Playwright")
    ap.add_argument("--skip-publish", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        receipt = generate_film(
            broll=args.broll,
            beats_path=args.beats,
            skip_publish=args.skip_publish,
            capture_landing=args.capture_landing,
        )
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: W1 film generated · voice={receipt.get('voice_engine')}")
        print(f"OUTPUT={receipt.get('output')}")
        for p in receipt.get("published") or []:
            print(f"PUBLISHED={p}")
        print(f"RECEIPT={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
