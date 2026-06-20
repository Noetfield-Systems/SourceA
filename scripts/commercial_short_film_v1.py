#!/usr/bin/env python3
"""Commercial short film — full-stack real UI capture + AI narration → mp4.

Law: >=70% real product UI (Playwright 1080p). No fake T2V dashboards.
Stack: landing · Hub · Mac Health · governance proof · commercial loops.
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
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from film_elevenlabs_wire_v1 import (  # noqa: E402
    has_elevenlabs,
    lane_secrets_path,
    offset_words,
    set_refresh_voice,
    set_vo_lane,
    synthesize_narration,
    words_to_phrase_srt_entries,
    write_ass,
    write_srt as _write_aligned_srt,
    write_words_json,
)
SINA = Path.home() / ".sina"
BEATS_JSON = ROOT / "data" / "commercial-short-film-beats-v1.json"
WORK = SINA / "commercial-short-film-work-v1"
RECEIPT = SINA / "enforcement" / "commercial-short-film-receipt-v1.json"
SECRETS = SINA / "secrets.env"
OUT_LANDING = ROOT / "SourceA-landing" / "green-unified" / "assets" / "commercial-short-demo.mp4"
OUT_DESKTOP = Path.home() / "Desktop" / "SourceA-Commercial-Short.mp4"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class _CaptureTiming:
    """Perf-counter timing for one Playwright capture chunk (beat / hook / cta)."""

    def __init__(self, manifest: dict[str, Any], beat_key: str) -> None:
        self.manifest = manifest
        self.beat_key = beat_key
        self.t0 = time.perf_counter()

    def elapsed(self) -> float:
        return time.perf_counter() - self.t0

    def mark_range(self, event: str, start: float, end: float) -> None:
        capture = self.manifest.setdefault("capture", {}).setdefault(self.beat_key, {})
        events = capture.setdefault("events", {})
        events[event] = [round(start, 3), round(end, 3)]

    def close(self) -> tuple[float, float]:
        end = self.elapsed()
        capture = self.manifest.setdefault("capture", {}).setdefault(self.beat_key, {})
        capture["duration_s"] = round(end, 3)
        return 0.0, end


def _w1_event_window(manifest: dict[str, Any], beat_id: str, event: str) -> tuple[float, float] | None:
    """Return [start_s, end_s] for a W1 player beat window within a capture chunk."""
    events = (manifest.get("capture") or {}).get(beat_id, {}).get("events") or {}
    cluster = events.get(event)
    if cluster and len(cluster) == 2:
        return float(cluster[0]), float(cluster[1])
    return None


def _w1_sequence_dwell_ms(w1_sequence: list[list] | None) -> int:
    if not w1_sequence:
        return 0
    total = sum(int(float(row[1]) * 1000) for row in w1_sequence if len(row) >= 2)
    return total + 900


def _tamper_cluster_window(manifest: dict[str, Any], beat_id: str) -> tuple[float, float] | None:
    """Return [start_s, end_s] for tamper_cluster within a capture chunk."""
    events = (manifest.get("capture") or {}).get(beat_id, {}).get("events") or {}
    cluster = events.get("tamper_cluster")
    if cluster and len(cluster) == 2:
        return float(cluster[0]), float(cluster[1])
    return None


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


def _run(cmd: list[str], *, timeout: int = 600) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "ffmpeg failed").strip()[:2000])


def _register_render(lane: str, *, work: Path) -> None:
    """Register active render PID for factory guard (one render at a time)."""
    meta_path = SINA / "commercial-film-render-meta-v1.json"
    meta = {
        "schema": "commercial-film-render-meta-v1",
        "at": _now(),
        "pid": os.getpid(),
        "lane": lane,
        "work_dir": str(work),
        "phase": "capture",
    }
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def _write_checkpoint(
    work: Path,
    *,
    beats_path: Path,
    product: str,
    vo_lane: str,
    spec: dict[str, Any],
    raw_out: Path,
    phase: str = "post_concat",
) -> None:
    gc = spec.get("global_capture") or {}
    polish = spec.get("polish") or {}
    ck = {
        "schema": "commercial-film-checkpoint-v1",
        "at": _now(),
        "phase": phase,
        "beats_path": str(beats_path),
        "product": product,
        "vo_lane": vo_lane,
        "raw_mp4": str(raw_out),
        "master_w": int(gc.get("master_width") or gc.get("width") or 1920),
        "master_h": int(gc.get("master_height") or gc.get("height") or 1080),
        "captions_mode": str(spec.get("captions_mode") or "full"),
        "target_bitrate_mbps": float(polish.get("target_bitrate_mbps") or 10.0),
        "commercial_capture": bool(spec.get("commercial_capture")),
        "film_style": str(spec.get("film_style") or "standard"),
        "quality_tier": str(spec.get("quality_tier") or "standard"),
        "cinematic_finish": bool(spec.get("cinematic_finish") or polish.get("cinematic_finish")),
    }
    (work / "checkpoint.json").write_text(json.dumps(ck, indent=2) + "\n", encoding="utf-8")
    try:
        sys.path.insert(0, str(_SCRIPTS))
        from commercial_film_render_guard_v1 import log_render_event  # noqa: WPS433

        log_render_event("checkpoint", lane=vo_lane, product=product, work_dir=str(work), phase=phase)
    except Exception:
        pass


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _secret(key: str) -> str:
    if not SECRETS.is_file():
        return ""
    for line in SECRETS.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _ensure_witnessbc_proof_lab(port: int = 8090) -> None:
    """Fail fast if Proof Lab is not reachable before Playwright capture."""
    base = f"http://127.0.0.1:{port}"
    for path in ("/", "/proof.html"):
        url = f"{base}{path}"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
        except Exception as exc:
            raise RuntimeError(
                f"WitnessBC Proof Lab not ready at {url}: {exc}\n"
                f"  Start: bash witnessbc-commercial-film.sh (auto-starts :{port})\n"
                f"  Or: cd ~/Desktop/SourceA/witnessbc-site/dist/deploy && "
                f"python3 -m http.server {port} --bind 127.0.0.1"
            ) from exc


def _smooth_scroll(page, steps: int = 8, *, step_ms: int = 240) -> None:
    page.evaluate(
        """async ([steps, stepMs]) => {
      const max = Math.max(document.body.scrollHeight - window.innerHeight, 0);
      for (let i = 1; i <= steps; i++) {
        const t = i / steps;
        const ease = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        window.scrollTo({ top: max * ease, behavior: 'instant' });
        await new Promise(r => setTimeout(r, stepMs));
      }
    }""",
        [steps, step_ms],
    )


def _scenario_slug_from_url(url: str) -> str | None:
    m = re.search(r"[#&]scenario=([a-z0-9-]+)", url, re.I)
    return m.group(1).lower() if m else None


def _wait_proof_lab_ready(page) -> None:
    page.wait_for_selector("#proofScenarioCards .proof-scenario-card", timeout=20000)


def _click_scenario(page, slug: str) -> bool:
    for sel in (
        f'.proof-scenario-card[data-scenario="{slug}"]',
        f'.proof-pill[data-scenario="{slug}"]',
        f'.roster li[data-scenario="{slug}"]',
    ):
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                el.scroll_into_view_if_needed(timeout=3000)
                el.click(timeout=4000)
                page.wait_for_timeout(500)
                return True
        except Exception:
            continue
    return False


def _scroll_into_view_safe(page, selector: str, *, timeout: int = 3000) -> bool:
    try:
        el = page.locator(selector).first
        if el.count() > 0:
            el.scroll_into_view_if_needed(timeout=timeout)
            page.wait_for_timeout(350)
            return True
    except Exception:
        pass
    return False


def _hold_tamper_fail_state(
    page,
    *,
    dwell_ms: int = 9500,
    capture_timing: _CaptureTiming | None = None,
    t_hover: float | None = None,
    t_click: float | None = None,
) -> None:
    """Tamper proof cluster — attempt contrast → BLOCK → receipt hash (capture dwell, not edit freeze)."""
    t_verdict_start = capture_timing.elapsed() if capture_timing else None
    for sel in (
        "#proofVerdictLive",
        ".proof-evidence-verdict.verdict-fail",
        "#proofTerminal .line.fail",
    ):
        try:
            page.locator(sel).first.wait_for(state="visible", timeout=12000)
            break
        except Exception:
            continue
    try:
        page.locator("#proofVerdictLive").filter(has_text=re.compile(r"tamper", re.I)).first.wait_for(
            state="visible", timeout=4000
        )
    except Exception:
        pass
    page.wait_for_timeout(5000)
    t_hash_start = capture_timing.elapsed() if capture_timing else None

    _scroll_into_view_safe(page, "#proofTerminal")
    _scroll_into_view_safe(page, "#proofEvidencePanel")
    _scroll_into_view_safe(page, "[data-evidence-hash]")
    _scroll_into_view_safe(page, "#proofReceiptJson")
    page.wait_for_timeout(3500)
    t_hash_end = capture_timing.elapsed() if capture_timing else None

    for sel in ("[data-evidence-hash]", ".proof-evidence-verdict.verdict-fail", "#proofVerdictLive"):
        if _scroll_into_view_safe(page, sel):
            page.wait_for_timeout(max(2500, dwell_ms - 8500))
            break
    else:
        page.wait_for_timeout(max(2500, dwell_ms - 8500))

    if capture_timing:
        if t_hover is not None:
            capture_timing.mark_range("tamper_hover", t_hover, t_hover + 1.8)
        if t_click is not None:
            capture_timing.mark_range("tamper_click", t_click, t_click + 0.15)
        if t_verdict_start is not None:
            capture_timing.mark_range("tamper_verdict", t_verdict_start, t_verdict_start + 5.0)
        if t_hash_start is not None:
            capture_timing.mark_range("tamper_hash", t_hash_start, t_hash_start + 3.5)
        cluster_start = t_hover if t_hover is not None else t_verdict_start
        cluster_end = t_hash_end if t_hash_end is not None else capture_timing.elapsed()
        if cluster_start is not None:
            capture_timing.mark_range("tamper_cluster", cluster_start, cluster_end)


def _interact_proof_lab(
    page,
    url: str,
    *,
    linear_recut: bool = False,
    tamper_dwell_ms: int = 9500,
    capture_timing: _CaptureTiming | None = None,
) -> None:
    """Linear-style — live Proof Lab terminal animation, clicks, tamper demo."""
    if "proof.html" not in url:
        return
    page.wait_for_timeout(1000 if linear_recut else 900)
    try:
        _wait_proof_lab_ready(page)
    except Exception:
        return

    slug = _scenario_slug_from_url(url)
    if not slug and linear_recut:
        slug = "outbound"

    if slug:
        _click_scenario(page, slug)
        dwell = 4500 if linear_recut else 2200
        if slug in ("outbound", "tool", "pii-leak"):
            dwell = 6500 if linear_recut else 2800
        if slug == "tamper":
            dwell = 7500 if linear_recut else 3200
        page.wait_for_timeout(dwell)

    is_tamper = slug == "tamper" or (linear_recut and "scenario=tamper" in url)
    if is_tamper:
        clicked = False
        t_hover: float | None = None
        t_click: float | None = None
        for sel in ("#proofTamperBtn", ".proof-tamper-btn", "[data-action='tamper']"):
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.scroll_into_view_if_needed(timeout=3000)
                    _film_cursor_to(page, sel)
                    el.hover(timeout=3000)
                    t_hover = capture_timing.elapsed() if capture_timing else None
                    page.wait_for_timeout(1800)
                    el.click(timeout=4000)
                    t_click = capture_timing.elapsed() if capture_timing else None
                    clicked = True
                    break
            except Exception:
                continue
        if clicked:
            _hold_tamper_fail_state(
                page,
                dwell_ms=tamper_dwell_ms if linear_recut else min(tamper_dwell_ms, 6500),
                capture_timing=capture_timing,
                t_hover=t_hover,
                t_click=t_click,
            )
        else:
            page.wait_for_timeout(3500 if linear_recut else 1200)

    if linear_recut:
        try:
            term = page.locator("#proofTerminal").first
            if term.count() > 0:
                term.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        try:
            play = page.locator("#proofReplayPlay").first
            if play.count() > 0 and slug and slug not in ("tamper",):
                play.click(timeout=2000)
                page.wait_for_timeout(1200)
        except Exception:
            pass
        page.wait_for_timeout(1500)
    else:
        page.wait_for_timeout(2200)


def _interact_home(page, url: str, *, linear_recut: bool = False) -> None:
    """Linear-style — scroll hero + click control-plane roster on home/platform."""
    page.wait_for_timeout(800)
    if linear_recut:
        for sel in (
            ".roster li[data-scenario='outbound']",
            ".roster li[data-scenario='tool']",
            ".proof-scenario-card[data-scenario='outbound']",
        ):
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.scroll_into_view_if_needed(timeout=3000)
                    page.wait_for_timeout(400)
                    el.hover(timeout=2000)
                    page.wait_for_timeout(600)
                    break
            except Exception:
                continue
    _smooth_scroll(page, steps=6 if linear_recut else 5)
    page.wait_for_timeout(600 if linear_recut else 400)


def _urls_proof_focus(urls: list[str]) -> bool:
    return any("proof.html" in u for u in urls)


def _inject_commercial_capture(page, *, product: str = "sourcea") -> None:
    """Clean theme · hidden chrome · synthetic cursor for pro demo capture."""
    theme_key = "sourcea-theme" if product == "sourcea" else "witness-ai-theme"
    use_light = product == "witnessbc"
    theme = "light" if use_light else "dark"
    witnessbc_hide = """
              .announcement, #mainNav, .site-header, .site-footer, .page-breadcrumb,
              header.site-header, nav.nav, footer.site-footer { display: none !important; }
              body, .proof-lab, main { background: #ffffff !important; color: #0f172a !important; }
              .proof-scenario-card, .proof-panel, #proofEvidencePanel {
                box-shadow: 0 1px 3px rgba(15,23,42,0.08) !important;
              }
            """ if use_light else ""
    try:
        page.add_init_script(
            """
            document.documentElement.setAttribute('data-theme', '__THEME__');
            document.documentElement.setAttribute('data-film-capture', '1');
            localStorage.setItem('__THEME_KEY__', '__THEME__');
            const s = document.createElement('style');
            s.textContent = `
              * { scroll-behavior: auto !important; cursor: none !important; }
              ::-webkit-scrollbar { width: 0 !important; height: 0 !important; }
              body { overflow-x: hidden !important; }
              .proof-terminal, #proofTerminal, #proofEvidencePanel { scroll-margin-top: 80px; }
              #sa-w1-player, #sa-w1-player .sa-w1-screen {
                max-width: 100% !important;
                margin: 0 auto !important;
              }
              header.ar-header, .ar-nav, footer, .sa-scroll-cue { display: none !important; }
              .ar-section-head, .sa-demo-film-copy, .sa-demo-film-media > video,
              .sa-demo-film-media > .sa-metric-note, .ar-kicker { display: none !important; }
              #w1-demo-film ~ section, .ar-features-grid, .ar-feature-card { display: none !important; }
              #sa-w1-player .sa-w1-rail { display: none !important; }
              .sa-w1-player-inner { display: block !important; }
              #w1-demo-film { padding-top: 0 !important; margin-top: 0 !important; }
              #sa-w1-player { margin: 0 auto !important; max-width: 96vw !important; }
              #sa-w1-player .sa-w1-screen { transform: none !important; max-width: 1080px !important; }
              header.ar-header, .ar-nav, footer, .sa-scroll-cue { opacity: 0 !important; }
              __WITNESSBC_HIDE__
              #film-cursor {
                position: fixed; width: 22px; height: 22px; border-radius: 50%;
                border: 2px solid rgba(__CURSOR_RGB__,0.92);
                box-shadow: 0 0 0 1px rgba(0,0,0,0.25), 0 0 18px rgba(45,212,191,0.45);
                pointer-events: none; z-index: 2147483647;
                transform: translate(-50%, -50%);
                transition: left 0.62s cubic-bezier(0.22, 1, 0.36, 1), top 0.62s cubic-bezier(0.22, 1, 0.36, 1), transform 0.18s ease;
              }
              #film-cursor.click { transform: translate(-50%, -50%) scale(0.82); }
            `;
            document.head.appendChild(s);
            const moveCursor = (x, y, click) => {
              let c = document.getElementById('film-cursor');
              if (!c) {
                c = document.createElement('div');
                c.id = 'film-cursor';
                document.body.appendChild(c);
              }
              c.style.left = x + 'px';
              c.style.top = y + 'px';
              if (click) {
                c.classList.add('click');
                setTimeout(() => c.classList.remove('click'), 140);
              }
            };
            document.addEventListener('mousemove', e => moveCursor(e.clientX, e.clientY, false));
            document.addEventListener('mousedown', e => moveCursor(e.clientX, e.clientY, true));
            window.__filmMoveCursor = moveCursor;
            """.replace("__THEME_KEY__", theme_key)
            .replace("__THEME__", theme)
            .replace("__WITNESSBC_HIDE__", witnessbc_hide)
            .replace("__CURSOR_RGB__", "15,23,42" if use_light else "255,255,255")
        )
    except Exception:
        pass
    try:
        page.emulate_media(color_scheme=theme)
    except Exception:
        pass


def _film_cursor_to(page, selector: str, *, dwell_ms: int = 450) -> None:
    try:
        box = page.locator(selector).first.bounding_box(timeout=3000)
        if box:
            page.evaluate(
                "([x,y]) => window.__filmMoveCursor && window.__filmMoveCursor(x, y, false)",
                [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2],
            )
            page.wait_for_timeout(dwell_ms)
    except Exception:
        pass


def _focus_w1_player_page(page, *, commercial_capture: bool = False) -> None:
    """Scroll to W1 player and hide marketing chrome — proof-density frame."""
    try:
        page.evaluate(
            """() => {
              const hide = [
                'header.ar-header', '.ar-nav', 'footer', '.sa-scroll-cue',
                '.ar-section-head', '.sa-demo-film-copy', '.sa-demo-film-media video',
                '.sa-demo-film-media .sa-metric-note', '.ar-kicker',
                '#w1-demo-film ~ section', '.ar-features-grid', '.ar-feature-card',
                '#sa-w1-player .sa-w1-rail'
              ];
              hide.forEach((sel) => {
                document.querySelectorAll(sel).forEach((el) => {
                  el.style.setProperty('display', 'none', 'important');
                });
              });
              const player = document.getElementById('sa-w1-player');
              if (player) {
                player.scrollIntoView({ block: 'center', behavior: 'instant' });
                window.scrollTo({ top: Math.max(player.offsetTop - 48, 0), behavior: 'instant' });
              }
            }"""
        )
        page.wait_for_timeout(900 if commercial_capture else 400)
    except Exception:
        pass


def _show_w1_film_beat(page, beat_id: str) -> bool:
    try:
        return bool(
            page.evaluate(
                """(id) => {
                  if (typeof window.__saW1FilmBeat === 'function') {
                    window.__saW1FilmBeat(id);
                    return true;
                  }
                  const btn = document.querySelector('.sa-w1-beat-btn[data-beat="' + id + '"]');
                  if (btn) { btn.click(); return true; }
                  return false;
                }""",
                beat_id,
            )
        )
    except Exception:
        return False


def _run_w1_player_sequence(
    page,
    *,
    sequence: list[tuple[str, int]] | None = None,
    commercial_capture: bool = False,
    human_smooth: bool = False,
    capture_timing: _CaptureTiming | None = None,
) -> None:
    """Drive #sa-w1-player through ALLOW → BLOCK → tamper — the actual product proof."""
    seq = sequence or [
        ("allow", 1800 if commercial_capture else 1200),
        ("block", 6500 if commercial_capture else 4000),
        ("tamper", 6500 if commercial_capture else 4000),
    ]
    try:
        page.wait_for_selector("#sa-w1-player .sa-w1-terminal", timeout=20000)
    except Exception:
        return
    _focus_w1_player_page(page, commercial_capture=commercial_capture)
    page.wait_for_timeout(900 if human_smooth else 800)
    if human_smooth:
        try:
            page.wait_for_function("() => typeof window.__saW1FilmBeat === 'function'", timeout=15000)
        except Exception:
            human_smooth = False
    for beat_id, dwell in seq:
        beat_start = capture_timing.elapsed() if capture_timing else None
        try:
            if human_smooth:
                _show_w1_film_beat(page, beat_id)
                page.wait_for_timeout(520)
                _film_cursor_to(page, "#sa-w1-terminal", dwell_ms=720)
                page.wait_for_timeout(dwell)
            else:
                btn = page.locator(f'.sa-w1-beat-btn[data-beat="{beat_id}"]').first
                if btn.count() == 0:
                    continue
                btn.scroll_into_view_if_needed(timeout=3000)
                _film_cursor_to(page, f'.sa-w1-beat-btn[data-beat="{beat_id}"]', dwell_ms=500)
                btn.click(timeout=3000)
                page.wait_for_timeout(300)
                page.locator("#sa-w1-terminal").first.scroll_into_view_if_needed(timeout=2000)
                _film_cursor_to(page, "#sa-w1-terminal", dwell_ms=400)
                page.wait_for_timeout(dwell)
            if capture_timing is not None and beat_start is not None:
                capture_timing.mark_range(f"w1_{beat_id}", beat_start, capture_timing.elapsed())
        except Exception:
            continue


def _interact_sourcea(
    page,
    url: str,
    *,
    commercial_capture: bool = False,
    human_smooth: bool = False,
    w1_sequence: list[list] | None = None,
    capture_timing: _CaptureTiming | None = None,
) -> None:
    """SourceA proof-density capture — W1 player + live verdict, NOT marketing scroll."""
    cursor_dwell = 800 if commercial_capture else 450
    scroll_steps = 20 if commercial_capture else 8
    scroll_ms = 280 if commercial_capture else 240
    page.wait_for_timeout(1400 if commercial_capture else 700)

    w1_seq: list[tuple[str, int]] | None = None
    if w1_sequence:
        w1_seq = [(str(row[0]), int(float(row[1]) * 1000)) for row in w1_sequence if len(row) >= 2]

    if "w1-demo-film" in url or "#sa-w1-player" in url or "film_capture" in url:
        _focus_w1_player_page(page, commercial_capture=commercial_capture)
        _run_w1_player_sequence(
            page,
            sequence=w1_seq,
            commercial_capture=commercial_capture,
            human_smooth=human_smooth,
            capture_timing=capture_timing,
        )
        return

    if "proof/live" in url or "proof/live.html" in url:
        for sel in (".ar-hero-accent", "h1", ".sa-aeg-verdict", "main h1", "main"):
            if _scroll_into_view_safe(page, sel):
                _film_cursor_to(page, sel, dwell_ms=cursor_dwell)
                page.wait_for_timeout(3500 if commercial_capture else 2000)
                break
        return

    if "proof.html" in url or "proof/" in url:
        if page.locator("#sa-w1-player").count() > 0:
            _focus_w1_player_page(page, commercial_capture=commercial_capture)
            _run_w1_player_sequence(
                page,
                sequence=w1_seq,
                commercial_capture=commercial_capture,
                human_smooth=human_smooth,
                capture_timing=capture_timing,
            )
            return
        for sel in ("#sa-w1-player", ".sa-w1-terminal", ".sa-demo-film", "main"):
            if _scroll_into_view_safe(page, sel):
                _film_cursor_to(page, sel, dwell_ms=cursor_dwell)
                page.wait_for_timeout(3200 if commercial_capture else 1200)
                break
        return

    if "13020" in url:
        for sel in ("h1", ".worker-hub-card", "[class*='next-step']", "main"):
            if _scroll_into_view_safe(page, sel):
                page.wait_for_timeout(1100)
                _film_cursor_to(page, sel, dwell_ms=cursor_dwell)
                break
        _smooth_scroll(page, steps=scroll_steps, step_ms=scroll_ms)
        page.wait_for_timeout(1200 if commercial_capture else 800)
        return

    if "sa-built-on" in url or url.rstrip("/").endswith("sourcea") or url.endswith("sourcea/") or "#reference" in url:
        for sel in (".sa-built-on", ".sa-built-on-logos", "main h1"):
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.scroll_into_view_if_needed(timeout=3000)
                    _film_cursor_to(page, sel, dwell_ms=cursor_dwell)
                    page.wait_for_timeout(2200 if commercial_capture else 1200)
                    break
            except Exception:
                continue
        return

    if "scenario.html" in url:
        for sel in (".proof-quiz", "[data-scenario]", "main"):
            if _scroll_into_view_safe(page, sel):
                _film_cursor_to(page, sel, dwell_ms=cursor_dwell)
                page.wait_for_timeout(1400 if commercial_capture else 1000)
                break
        return

    if "team.html" in url or "platform.html" in url:
        for sel in (".sa-console-tab", ".sa-tab", "main h1"):
            try:
                loc = page.locator(sel)
                if loc.count() > 0:
                    el = loc.first
                    el.scroll_into_view_if_needed(timeout=3000)
                    _film_cursor_to(page, sel, dwell_ms=cursor_dwell)
                    el.hover(timeout=2500)
                    page.wait_for_timeout(900 if commercial_capture else 700)
                    break
            except Exception:
                continue
    _smooth_scroll(page, steps=min(scroll_steps, 6), step_ms=scroll_ms)
    page.wait_for_timeout(900 if commercial_capture else 400)


def _proof_focus_filter(*, ultra: bool = False, width: int = 1920, height: int = 1080) -> str:
    """Center crop + scale — Proof Lab fills frame like a product demo."""
    if ultra:
        crop_w = min(int(width * 0.875), max(width - 2, 1))
        crop_h = min(int(height * 0.875), max(height - 2, 1))
        if crop_w >= width or crop_h >= height:
            return f"scale={width}:{height}:flags=lanczos,"
        return f"crop={crop_w}:{crop_h}:(iw-{crop_w})/2:(ih-{crop_h})/2,scale={width}:{height}:flags=lanczos,"
    return ""


def _interact_page(
    page,
    url: str,
    *,
    linear_recut: bool = False,
    tamper_dwell_ms: int = 9500,
    capture_timing: _CaptureTiming | None = None,
    commercial_capture: bool = False,
    human_smooth: bool = False,
    product: str = "sourcea",
    w1_sequence: list[list] | None = None,
) -> None:
    if product == "witnessbc" and "proof.html" in url and "8090" in url:
        _interact_proof_lab(
            page,
            url,
            linear_recut=linear_recut,
            tamper_dwell_ms=tamper_dwell_ms,
            capture_timing=capture_timing,
        )
        return
    if commercial_capture and ("5180/sourcea" in url or "13020" in url or "13024" in url):
        _interact_sourcea(
            page,
            url,
            commercial_capture=commercial_capture,
            human_smooth=human_smooth,
            w1_sequence=w1_sequence,
            capture_timing=capture_timing,
        )
        return
    if "proof.html" in url:
        _interact_proof_lab(
            page,
            url,
            linear_recut=linear_recut,
            tamper_dwell_ms=tamper_dwell_ms,
            capture_timing=capture_timing,
        )
        return
    if any(p in url for p in ("8090/",)) and "proof" not in url and product == "witnessbc":
        _interact_home(page, url, linear_recut=linear_recut)
        return
    page.wait_for_timeout(600)
    _smooth_scroll(page, steps=5)


def _overlay_chapter_label(
    video: Path,
    label: str,
    out: Path,
    *,
    hero: bool = False,
    commercial: bool = False,
) -> None:
    """Linear Learn — bottom-left chapter caption on b-roll."""
    safe = label.replace("'", "\\'").replace(":", "\\:")
    if commercial:
        fs, border = 22, 10
    else:
        fs = 30 if hero else 26
        border = 18 if hero else 14
    vf = (
        f"drawtext=text='{safe}':fontsize={fs}:fontcolor=white@0.95:"
        f"x=64:y=h-84:box=1:boxcolor=0x060d18@0.62:boxborderw={border}"
    )
    if hero:
        vf = f"unsharp=5:5:0.4:5:5:0.0,{vf}"
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(video),
            "-vf",
            vf,
            "-c:a",
            "copy",
            "-c:v",
            "libx264",
            "-preset",
            "slow" if hero else "medium",
            "-crf",
            "17" if hero else "20",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ]
    )


def _capture_urls_to_webm(
    urls: list[str],
    out_webm: Path,
    *,
    width: int = 1920,
    height: int = 1080,
    seconds_per_url: float = 4.0,
    zoom: float = 1.0,
    linear_recut: bool = False,
    commercial_capture: bool = False,
    tamper_dwell_ms: int = 9500,
    beat_id: str | None = None,
    timing_manifest: dict[str, Any] | None = None,
    product: str = "sourcea",
    w1_sequence: list[list] | None = None,
    human_smooth: bool = False,
    _allow_fallback: bool = True,
    _attempt: int = 0,
) -> Path:
    try:
        from playwright.sync_api import sync_playwright  # noqa: WPS433
    except ImportError as exc:
        raise SystemExit(f"FAIL: playwright required — {exc}") from exc

    if product == "witnessbc" and any("8090" in u for u in urls):
        _ensure_witnessbc_proof_lab()

    out_webm.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_webm.parent / f"capture-chunks-{_attempt}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    chunk_files: list[Path] = []
    capture_timing: _CaptureTiming | None = None
    capture_errors: list[str] = []
    if timing_manifest is not None and beat_id:
        capture_timing = _CaptureTiming(timing_manifest, beat_id)

    dsf_cap = 3.0 if commercial_capture and width >= 2560 else (
        3.0 if commercial_capture else 2.5
    )
    device_scale = min(max(2.5 if commercial_capture else 2.0 if zoom >= 1.3 else 1.0, 2.0), dsf_cap)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for idx, url in enumerate(urls):
                url_start = capture_timing.elapsed() if capture_timing else 0.0
                context = browser.new_context(
                    record_video_dir=str(tmp_dir),
                    record_video_size={"width": width, "height": height},
                    viewport={"width": width, "height": height},
                    device_scale_factor=device_scale,
                )
                page = context.new_page()
                if commercial_capture:
                    _inject_commercial_capture(page, product=product)
                loaded = False
                for wait_mode in ("domcontentloaded", "load"):
                    try:
                        page.goto(url, wait_until=wait_mode, timeout=45000)
                        loaded = True
                        break
                    except Exception:
                        continue
                if not loaded:
                    msg = f"page.goto failed for {url} (beat={beat_id}, product={product})"
                    capture_errors.append(msg)
                    try:
                        context.close()
                    except Exception:
                        pass
                    if product == "witnessbc" and len(urls) == 1:
                        raise RuntimeError(
                            f"WitnessBC Playwright capture failed: {msg}\n"
                            "  Ensure Proof Lab: curl http://127.0.0.1:8090/proof.html → 200"
                        )
                    continue
                try:
                    _interact_page(
                        page,
                        url,
                        linear_recut=linear_recut,
                        tamper_dwell_ms=tamper_dwell_ms,
                        capture_timing=capture_timing,
                        commercial_capture=commercial_capture,
                        human_smooth=human_smooth,
                        product=product,
                        w1_sequence=w1_sequence,
                    )
                    if w1_sequence and (
                        "w1-demo-film" in url or "#sa-w1-player" in url or "film_capture" in url
                    ):
                        dwell = _w1_sequence_dwell_ms(w1_sequence)
                    else:
                        dwell = int(max(2.0, seconds_per_url) * 1000)
                    if linear_recut and "proof.html" in url:
                        dwell = int(max(dwell, 5500))
                    tamper_slug = _scenario_slug_from_url(url)
                    if tamper_slug == "tamper" or "scenario=tamper" in url:
                        dwell = int(max(dwell, tamper_dwell_ms + 3500 if linear_recut else 6000))
                    page.wait_for_timeout(dwell)
                except Exception:
                    pass
                if capture_timing is not None and timing_manifest is not None:
                    url_end = capture_timing.elapsed()
                    timing_manifest.setdefault("urls", {})[f"{beat_id}_url_{idx:02d}"] = [
                        round(url_start, 3),
                        round(url_end, 3),
                    ]
                video = page.video
                chunk = out_webm.parent / f"{out_webm.stem}-chunk-{idx:02d}.webm"
                try:
                    page.close()
                except Exception:
                    pass
                context.close()
                saved: Path | None = None
                if video is not None:
                    try:
                        video.save_as(str(chunk))
                        if chunk.is_file() and chunk.stat().st_size > 1000:
                            saved = chunk
                    except Exception:
                        for _ in range(120):
                            try:
                                raw = video.path()
                            except Exception:
                                raw = None
                            if raw and Path(raw).is_file() and Path(raw).stat().st_size > 1000:
                                shutil.copy2(str(raw), str(chunk))
                                if chunk.is_file() and chunk.stat().st_size > 1000:
                                    saved = chunk
                                break
                            time.sleep(0.25)
                if saved is not None:
                    if not chunk.is_file() or chunk.stat().st_size <= 1000:
                        msg = (
                            f"chunk {chunk.name} missing or too small after save "
                            f"(url={url}, beat={beat_id})"
                        )
                        capture_errors.append(msg)
                    else:
                        chunk_files.append(chunk)
                else:
                    msg = f"no Playwright video file for {url} (beat={beat_id})"
                    capture_errors.append(msg)
            browser.close()
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        if _attempt < 2:
            time.sleep(1.5)
            return _capture_urls_to_webm(
                urls,
                out_webm,
                width=width,
                height=height,
                seconds_per_url=seconds_per_url,
                zoom=zoom,
                linear_recut=linear_recut,
                commercial_capture=commercial_capture,
                tamper_dwell_ms=tamper_dwell_ms,
                beat_id=beat_id,
                timing_manifest=timing_manifest,
                product=product,
                human_smooth=human_smooth,
                _allow_fallback=_allow_fallback,
                _attempt=_attempt + 1,
            )
        raise RuntimeError(f"Playwright capture failed after retries: {exc}") from exc

    if capture_timing is not None:
        capture_timing.close()

    for c in chunk_files:
        if not c.is_file() or c.stat().st_size <= 1000:
            raise RuntimeError(f"Capture chunk missing or empty before concat: {c}")

    if not chunk_files:
        err_detail = "\n".join(f"  - {e}" for e in capture_errors[:8])
        if product == "witnessbc":
            raise RuntimeError(
                f"WitnessBC Playwright capture produced no chunks for {beat_id or out_webm.stem}\n"
                f"{err_detail}\n"
                "  Ensure Proof Lab: curl http://127.0.0.1:8090/proof.html → 200"
            )
        if _allow_fallback:
            fallback = urls[:2] if urls else [
                "http://127.0.0.1:5180/sourcea/",
                "http://127.0.0.1:5180/sourcea/team.html",
            ]
            return _capture_urls_to_webm(
                fallback,
                out_webm,
                width=width,
                height=height,
                seconds_per_url=seconds_per_url,
                zoom=zoom,
                linear_recut=False,
                beat_id=beat_id,
                timing_manifest=timing_manifest,
                _allow_fallback=False,
            )
        raise SystemExit(
            f"FAIL: Playwright produced no capture chunks for {urls}\n"
            + (
                "  SourceA landing: curl http://127.0.0.1:5180/sourcea/ → 200\n"
                "  Start: bash SourceA-landing/green-unified/scripts/run-recipe.sh --serve"
                if product == "sourcea"
                else "  WitnessBC Proof Lab: curl http://127.0.0.1:8090/ → 200\n"
                "  Start: bash witnessbc-site/scripts/run-recipe.sh --serve"
            )
        )

    if len(chunk_files) == 1:
        shutil.copy2(str(chunk_files[0]), str(out_webm))
    else:
        list_file = tmp_dir / "concat.txt"
        list_file.write_text("\n".join(f"file '{c}'" for c in chunk_files) + "\n", encoding="utf-8")
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
                "-c",
                "copy",
                str(out_webm),
            ]
        )
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return out_webm


def _enc_flags(*, hero: bool = False, ultra: bool = False) -> tuple[str, str, str]:
    """Return (crf, preset, audio_bitrate) for encode passes."""
    if ultra:
        return "14", "slow", "256k"
    if hero:
        return "16", "slow", "192k"
    return "20", "medium", "160k"


def _edge_tts(text: str, out_mp3: Path, *, voice: str = "en-US-AndrewMultilingualNeural", rate: str = "-6%") -> bool:
    """Microsoft Edge neural VO — human-friendly, no API key."""
    try:
        import asyncio  # noqa: WPS433
        import edge_tts  # noqa: WPS433

        async def _run_tts() -> None:
            comm = edge_tts.Communicate(text, voice, rate=rate, pitch="-2Hz")
            await comm.save(str(out_mp3))

        asyncio.run(_run_tts())
        return out_mp3.stat().st_size > 500
    except Exception:
        return False


def _say_tts(text: str, out_aiff: Path, *, voice: str = "Daniel") -> None:
    subprocess.run(
        ["say", "-v", voice, "-r", "175", "-o", str(out_aiff), text],
        check=True,
        timeout=180,
    )


def _narration_audio(
    text: str,
    work: Path,
    stem: str,
    *,
    hero: bool = False,
    ultra: bool = False,
    edge_voice: str = "en-US-AndrewMultilingualNeural",
    vo_lane: str = "sourcea",
) -> tuple[Path, str, list[dict[str, Any]]]:
    mp3 = work / f"{stem}.mp3"
    m4a = work / f"{stem}.m4a"
    aiff = work / f"{stem}.aiff"
    ok, _align_eng, words = synthesize_narration(str(text or ""), mp3, lane=vo_lane)
    if ok:
        return mp3, "elevenlabs", words
    if (hero or ultra) and _edge_tts(str(text or ""), mp3, voice=edge_voice, rate="-6%" if ultra else "-4%"):
        return mp3, "edge_neural", []
    _say_tts(str(text or ""), aiff, voice="Daniel")
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(aiff),
            "-af",
            "highpass=f=80,lowpass=f=12000,compand=attacks=0.1:decays=0.3:points=-80/-80|-20/-15|-10/-8|0/-6",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(m4a),
        ]
    )
    return m4a, "macos_say", []


def _legacy_elevenlabs_tts(text: str, out_mp3: Path, *, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bool:
    """Deprecated — use film_elevenlabs_wire_v1.synthesize_narration."""
    ok, _, _ = synthesize_narration(text, out_mp3)
    return ok


def _logo_cold_open_png(brand_name: str, out: Path, *, width: int = 1920, height: int = 1080) -> None:
    """Linear-style logo cold open — minimal white field + brand mark."""
    from PIL import Image, ImageDraw, ImageFont  # noqa: WPS433

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2
    r = max(28, width // 55)
    draw.ellipse([cx - r, cy - r - height // 18, cx + r, cy + r - height // 18], fill="#0f172a")
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", max(48, width // 42))
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), brand_name, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy + height // 14), brand_name, fill="#0f172a", font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def _title_card_png(
    title: str,
    subtitle: str,
    label: str,
    out: Path,
    *,
    accent: str = "#2dd4bf",
    brand_name: str = "SourceA",
) -> None:
    from PIL import Image, ImageDraw, ImageFont  # noqa: WPS433

    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#060d18")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 8], fill=accent)
    draw.rectangle([0, h - 4, w, h], fill="#1e293b")
    try:
        font_brand = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
        font_l = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 64)
        font_s = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)
        font_tag = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
    except OSError:
        font_brand = font_l = font_s = font_tag = ImageFont.load_default()
    draw.text((80, 72), brand_name, fill="#34d399", font=font_brand)
    draw.text((80, h // 2 - 80), title, fill="#f8fafc", font=font_l)
    draw.text((80, h // 2 + 10), subtitle, fill="#94a3b8", font=font_s)
    draw.text((80, h // 2 + 70), label, fill=accent, font=font_tag)
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
            "-preset",
            "medium",
            "-crf",
            "20",
            "-t",
            str(seconds),
            "-pix_fmt",
            "yuv420p",
            "-r",
            "30",
            str(out),
        ]
    )


def _built_on_wall_png(
    out: Path,
    *,
    width: int = 3840,
    height: int = 2160,
    brand_name: str = "SourceA",
    logos: list[str] | None = None,
) -> None:
    """Linear-style logo wall — one frame, instant credibility."""
    from PIL import Image, ImageDraw, ImageFont  # noqa: WPS433

    logos = logos or ["Temporal", "Anthropic", "OpenAI", "LangGraph", "Cursor", "Cloudflare"]
    img = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", max(42, width // 90))
        font_logo = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", max(36, width // 100))
        font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", max(24, width // 140))
    except OSError:
        font_title = font_logo = font_sub = ImageFont.load_default()
    draw.text((width // 2 - 180, height // 5), "Built on", fill="#9ca3af", font=font_sub)
    draw.text((width // 2 - 320, height // 5 + 50), brand_name, fill="#34d399", font=font_title)
    cols, rows = 3, 2
    cell_w, cell_h = width // cols, height // 3
    start_y = height // 3
    for i, name in enumerate(logos[:6]):
        col, row = i % cols, i // cols
        cx = col * cell_w + cell_w // 2
        cy = start_y + row * cell_h + cell_h // 2
        bbox = draw.textbbox((0, 0), name, font=font_logo)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 28
        draw.rounded_rectangle(
            [cx - tw // 2 - pad, cy - th // 2 - pad, cx + tw // 2 + pad, cy + th // 2 + pad],
            radius=18,
            fill="#1f2937",
            outline="#374151",
            width=2,
        )
        draw.text((cx - tw // 2, cy - th // 2), name, fill="#f3f4f6", font=font_logo)
    draw.text(
        (width // 2 - 420, height - height // 8),
        "Technology dependencies — not co-marketing partnerships",
        fill="#6b7280",
        font=font_sub,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def _cinematic_vf(width: int, height: int, *, beat_id: str | None = None) -> str:
    """Dark-framed product shot — margins, border accent, crisp UI."""
    margin = 0.06 if beat_id == "BLOCK" else 0.08
    inner_w = int(width * (1 - 2 * margin))
    inner_h = int(height * (1 - 2 * margin))
    border_color = "0xef4444@0.45" if beat_id == "BLOCK" else "0x1e293b@0.65"
    border_t = 5 if beat_id == "BLOCK" else 3
    m = margin
    span = 1 - 2 * margin
    return (
        f"scale={inner_w}:{inner_h}:flags=lanczos,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x0A1218,"
        f"drawbox=x=iw*{m}:y=ih*{m}:w=iw*{span}:h=ih*{span}:color={border_color}:t={border_t},"
        f"eq=contrast=1.06:brightness=0.01:saturation=1.04,fps=30"
    )


def _apply_cinematic_frame(
    src: Path,
    out: Path,
    *,
    width: int,
    height: int,
    beat_id: str | None = None,
    ultra: bool = False,
) -> None:
    crf, preset, _ = _enc_flags(hero=True, ultra=ultra)
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(src),
            "-vf",
            _cinematic_vf(width, height, beat_id=beat_id),
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            crf,
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out),
        ]
    )


def _mix_vo_sfx(vo: Path, out: Path, *, duration: float, beat_id: str) -> None:
    """Micro sound design — ambient bed + beat-specific ticks/impacts under ElevenLabs VO."""
    dur = max(duration, 2.5)
    sfx_wav = out.parent / f"{out.stem}-sfx-bed.wav"
    _generate_sfx_wav(sfx_wav, duration=dur, beat_id=beat_id)
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(vo),
            "-i",
            str(sfx_wav),
            "-filter_complex",
            "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0:weights=1 0.4[aout]",
            "-map",
            "[aout]",
            "-c:a",
            "pcm_s16le",
            str(out),
        ]
    )


def _generate_sfx_wav(out: Path, *, duration: float, beat_id: str) -> None:
    """Single lavfi graph — ambient + impacts for one segment."""
    dur = max(duration, 2.5)
    impacts: dict[str, str] = {
        "hook": (
            "anoisesrc=d=0.25:c=pink,lowpass=f=800,volume=0.07,afade=t=out:st=0.1:d=0.15[wh];"
            "[wh]adelay=60|60[whd];"
            "sine=f=900:d=0.08,volume=0.05,afade=t=out:st=0.02:d=0.06[tk];"
            "[tk]adelay=1100|1100[tkd];"
            "[bed][whd][tkd]amix=inputs=3:duration=first:dropout_transition=0:weights=0.35 0.5 0.4[out]"
        ),
        "BLOCK": (
            "anoisesrc=d=0.25:c=pink,lowpass=f=800,volume=0.07,afade=t=out:st=0.1:d=0.15[wh];"
            "[wh]adelay=40|40[whd];"
            "sine=f=68:d=0.5,volume=0.22,afade=t=out:st=0.2:d=0.3[imp];"
            "[imp]adelay=1500|1500[impd];"
            "sine=f=42:d=0.55,volume=0.09,afade=t=out:st=0.2:d=0.35[rum];"
            "[rum]adelay=1650|1650[rumd];"
            "[bed][whd][impd][rumd]amix=inputs=4:duration=first:dropout_transition=0:weights=0.35 0.55 0.75 0.45[out]"
        ),
        "PROOF": (
            "sine=f=1400:d=0.05,volume=0.06,afade=t=out:st=0.01:d=0.04[t1];"
            "[t1]adelay=120|120[t1d];"
            "sine=f=220:d=0.35,volume=0.18,afade=t=out:st=0.1:d=0.25[f1];"
            "[f1]adelay=1400|1400[f1d];"
            "[bed][t1d][f1d]amix=inputs=3:duration=first:dropout_transition=0:weights=0.35 0.4 0.65[out]"
        ),
        "TRUST": (
            "sine=f=180:d=0.9,volume=0.06,afade=t=in:st=0:d=0.35,afade=t=out:st=0.55:d=0.35[sw];"
            "[sw]adelay=250|250[swd];"
            "[bed][swd]amix=inputs=2:duration=first:dropout_transition=0:weights=0.35 0.45[out]"
        ),
        "cta": (
            "anoisesrc=d=0.25:c=pink,lowpass=f=900,volume=0.06,afade=t=out:st=0.1:d=0.15[wh];"
            "[wh]adelay=40|40[whd];"
            "sine=f=320:d=0.45,volume=0.1,afade=t=in:st=0:d=0.08,afade=t=out:st=0.25:d=0.2[res];"
            "[res]adelay=2500|2500[resd];"
            "[bed][whd][resd]amix=inputs=3:duration=first:dropout_transition=0:weights=0.35 0.45 0.5[out]"
        ),
    }
    tail = impacts.get(
        beat_id,
        "anoisesrc=d=0.2:c=pink,volume=0.04,afade=t=out:st=0.08:d=0.12[wh];"
        "[wh]adelay=60|60[whd];"
        "[bed][whd]amix=inputs=2:duration=first:dropout_transition=0:weights=0.35 0.4[out]",
    )
    fc = f"anoisesrc=d={dur}:c=brown:r=48000,lowpass=f=150,volume=0.025[bed];{tail}"
    _run(
        [
            _ffmpeg(),
            "-y",
            "-f",
            "lavfi",
            "-i",
            fc,
            "-t",
            str(dur),
            "-c:a",
            "pcm_s16le",
            str(out),
        ]
    )


def _transcode_capture_hq(
    src: Path,
    out: Path,
    *,
    ultra: bool = False,
    proof_focus: bool = False,
    linear_ui_capture: bool = False,
    src_width: int = 1920,
    src_height: int = 1080,
    out_width: int = 1920,
    out_height: int = 1080,
    width: int | None = None,
    height: int | None = None,
) -> Path:
    """Playwright webm → clean mp4 before polish."""
    if width is not None:
        out_width = width
    if height is not None:
        out_height = height
    crf, preset, _ = _enc_flags(hero=True, ultra=ultra)
    vf = ""
    if proof_focus and not linear_ui_capture:
        vf = _proof_focus_filter(ultra=ultra, width=src_width, height=src_height)
    vf += f"scale={out_width}:{out_height}:flags=lanczos,fps=30"
    if ultra and not linear_ui_capture:
        vf += ",eq=contrast=1.10:brightness=0.02:saturation=1.08,unsharp=5:5:0.45:5:5:0.0"
    elif linear_ui_capture:
        vf += ",eq=contrast=1.04:brightness=0.01:saturation=1.03"
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(src),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            crf,
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out),
        ]
    )
    return out


def _human_smooth_push_vf(seconds: float, width: int, height: int, *, beat_id: str | None) -> str:
    if beat_id not in ("hook", "BLOCK", "PROOF"):
        return ""
    frames = max(int(seconds * 30), 30)
    rate = "0.000055" if beat_id == "BLOCK" else "0.00004"
    zmax = "1.06" if beat_id == "BLOCK" else "1.04"
    return (
        f"zoompan=z='min(1.0+on*{rate},{zmax})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps=30,"
    )


def _broll_clip(
    src: Path,
    seconds: float,
    out: Path,
    *,
    offset: float = 0,
    hero: bool = False,
    ultra: bool = False,
    proof_focus: bool = False,
    commercial_capture: bool = False,
    linear_ui_capture: bool = False,
    cinematic_finish: bool = False,
    human_smooth: bool = False,
    beat_id: str | None = None,
    width: int = 1920,
    height: int = 1080,
) -> None:
    crf, preset, _ = _enc_flags(hero=hero, ultra=ultra)
    vf = ""
    if proof_focus and not linear_ui_capture:
        vf = _proof_focus_filter(ultra=ultra, width=width, height=height)
    if cinematic_finish:
        if human_smooth:
            vf += _human_smooth_push_vf(seconds, width, height, beat_id=beat_id)
        vf += _cinematic_vf(width, height, beat_id=beat_id)
    elif linear_ui_capture:
        vf += f"scale={width}:{height}:flags=lanczos,fps=30"
        if ultra:
            vf += ",eq=contrast=1.04:brightness=0.01:saturation=1.03"
    elif hero or ultra:
        frames = max(int(seconds * 30), 30)
        zoom_rate = "0.00035" if commercial_capture else "0.0008"
        zoom_max = "1.10" if commercial_capture else "1.12"
        y_expr = "ih/3-(ih/zoom/2)" if commercial_capture and proof_focus else "ih/2-(ih/zoom/2)"
        vf += (
            f"zoompan=z='min(zoom+{zoom_rate},{zoom_max})':x='iw/2-(iw/zoom/2)':y='{y_expr}':"
            f"d={frames}:s={width}x{height}:fps=30,"
            "eq=contrast=1.12:brightness=0.025:saturation=1.10,"
            "unsharp=5:5:0.50:5:5:0.0"
        )
    else:
        vf += f"scale={width}:{height}:flags=lanczos,fps=30"
    cmd = [
        _ffmpeg(),
        "-y",
        "-stream_loop",
        "-1",
        "-ss",
        str(max(0.0, offset)),
        "-i",
        str(src),
        "-t",
        str(seconds),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        crf,
        "-pix_fmt",
        "yuv420p",
        "-an",
    ]
    if ultra:
        cmd.extend(["-b:v", "8M", "-maxrate", "12M", "-bufsize", "24M"])
    cmd.append(str(out))
    _run(cmd)


def _audio_duration(audio: Path) -> float:
    probe = subprocess.run([_ffmpeg(), "-i", str(audio)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
    if not m:
        return 5.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def _mux_video_audio(
    video: Path,
    audio: Path,
    out: Path,
    *,
    pad_video: float | None = None,
    hero: bool = False,
    ultra: bool = False,
    beat_id: str | None = None,
    cinematic_sfx: bool = False,
) -> None:
    audio_dur = _audio_duration(audio)
    target = pad_video if pad_video is not None else max(audio_dur, 3.0)
    audio_in = audio
    if cinematic_sfx and beat_id:
        mixed = audio.parent / f"{audio.stem}-sfxmix.wav"
        _mix_vo_sfx(audio, mixed, duration=target, beat_id=beat_id)
        audio_in = mixed
        audio_dur = _audio_duration(audio_in)
    fade_out = 0.45 if ultra else 0.35
    fade_in = 0.3 if ultra else 0.25
    af = (
        f"afade=t=in:st=0:d={fade_in},afade=t=out:st={max(0.0, audio_dur - fade_out)}:d={fade_out}"
    )
    hold_broll = pad_video is not None and target > audio_dur + 0.05
    if hold_broll:
        # VO ends; broll keeps running on silent tail (linear_bar dwell).
        af += f",apad=whole_dur={target:.3f}"
    if hero or ultra:
        af += ",loudnorm=I=-14:TP=-1.0:LRA=9"
    if ultra:
        af += ",acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80"
    crf, preset, abr = _enc_flags(hero=hero, ultra=ultra)
    cmd = [
        _ffmpeg(),
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio_in),
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        crf,
        "-c:a",
        "aac",
        "-b:a",
        abr,
        "-af",
        af,
        "-pix_fmt",
        "yuv420p",
        "-t",
        str(target),
    ]
    if not hold_broll:
        cmd.append("-shortest")
    cmd.append(str(out))
    _run(cmd)


def _segment_duration(path: Path) -> float:
    probe = subprocess.run([_ffmpeg(), "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", probe.stderr)
    if not m:
        return 5.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def _has_audio_stream(path: Path) -> bool:
    probe = subprocess.run([_ffmpeg(), "-i", str(path)], capture_output=True, text=True)
    return "Audio:" in probe.stderr


def _normalize_av_for_concat(
    video: Path,
    out: Path,
    *,
    hero: bool = False,
    ultra: bool = False,
) -> Path:
    """Uniform stereo 48kHz AAC + H264 — concat requires matching stream layouts."""
    crf, preset, abr = _enc_flags(hero=hero, ultra=ultra)
    has_audio = _has_audio_stream(video)
    if has_audio:
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(video),
                "-vf",
                "setpts=PTS-STARTPTS",
                "-af",
                "aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS",
                "-c:v",
                "libx264",
                "-preset",
                preset,
                "-crf",
                crf,
                "-c:a",
                "aac",
                "-b:a",
                abr,
                "-pix_fmt",
                "yuv420p",
                str(out),
            ]
        )
    else:
        dur = max(_segment_duration(video), 0.1)
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(video),
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-vf",
                "setpts=PTS-STARTPTS",
                "-c:v",
                "libx264",
                "-preset",
                preset,
                "-crf",
                crf,
                "-c:a",
                "aac",
                "-b:a",
                abr,
                "-shortest",
                "-t",
                f"{dur:.3f}",
                "-pix_fmt",
                "yuv420p",
                str(out),
            ]
        )
    return out


def _fade_segment(seg: Path, out: Path, *, fade: float = 0.4, ultra: bool = False) -> None:
    """Gentle fade in/out per segment — clean cuts without brittle xfade chains."""
    dur = _segment_duration(seg)
    fade_out = max(0.0, dur - fade)
    crf, preset, abr = _enc_flags(hero=True, ultra=ultra)
    has_audio = _has_audio_stream(seg)
    if has_audio:
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(seg),
                "-vf",
                f"fade=t=in:st=0:d={fade},fade=t=out:st={fade_out}:d={fade}",
                "-af",
                f"afade=t=in:st=0:d={fade},afade=t=out:st={fade_out}:d={fade}",
                "-c:v",
                "libx264",
                "-preset",
                preset,
                "-crf",
                crf,
                "-c:a",
                "aac",
                "-b:a",
                abr,
                "-pix_fmt",
                "yuv420p",
                str(out),
            ]
        )
    else:
        # Video-only segment (logo card) — inject silent stereo so concat keeps audio stream.
        _run(
            [
                _ffmpeg(),
                "-y",
                "-i",
                str(seg),
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-vf",
                f"fade=t=in:st=0:d={fade},fade=t=out:st={fade_out}:d={fade}",
                "-af",
                f"afade=t=in:st=0:d={fade},afade=t=out:st={fade_out}:d={fade}",
                "-c:v",
                "libx264",
                "-preset",
                preset,
                "-crf",
                crf,
                "-c:a",
                "aac",
                "-b:a",
                abr,
                "-shortest",
                "-t",
                f"{dur:.3f}",
                "-pix_fmt",
                "yuv420p",
                str(out),
            ]
        )


def _concat_segments(
    segments: list[Path], out: Path, *, hero: bool = False, ultra: bool = False, fade_sec: float = 0.35
) -> None:
    fade_sec = 0.5 if ultra else fade_sec
    ensured: list[Path] = []
    for i, seg in enumerate(segments):
        norm = out.parent / f"norm-seg-{i:02d}.mp4"
        ensured.append(_normalize_av_for_concat(seg, norm, hero=hero, ultra=ultra))
    to_concat = ensured
    if (hero or ultra) and len(ensured) > 1:
        faded: list[Path] = []
        for i, seg in enumerate(ensured):
            faded_out = out.parent / f"fade-seg-{i:02d}.mp4"
            _fade_segment(seg, faded_out, fade=fade_sec, ultra=ultra)
            faded.append(faded_out)
        to_concat = faded

    crf, preset, abr = _enc_flags(hero=hero, ultra=ultra)
    if len(to_concat) == 1:
        shutil.copy2(to_concat[0], out)
        return
    list_file = out.parent / "concat.txt"
    list_file.write_text("\n".join(f"file '{s}'" for s in to_concat) + "\n", encoding="utf-8")
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
            "-preset",
            preset,
            "-crf",
            crf,
            "-c:a",
            "aac",
            "-b:a",
            abr,
            "-ar",
            "48000",
            "-ac",
            "2",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ],
        timeout=900,
    )


def _master_polish(
    src: Path,
    out: Path,
    *,
    ultra: bool = False,
    pro: bool = False,
    linear_ui_capture: bool = False,
    width: int = 1920,
    height: int = 1080,
    target_bitrate_mbps: float = 10.0,
) -> None:
    """Final master — broadcast loudness + grade; upscale to target resolution."""
    if not (ultra or pro):
        shutil.copy2(src, out)
        return
    crf, preset, abr = _enc_flags(ultra=True)
    probe = subprocess.run([_ffmpeg(), "-i", str(src)], capture_output=True, text=True)
    src_w = src_h = 0
    m = re.search(r"Stream.* Video:.* (\d+)x(\d+)", probe.stderr)
    if m:
        src_w, src_h = int(m.group(1)), int(m.group(2))
    scale_vf = ""
    if src_w and src_h and (src_w != width or src_h != height):
        scale_vf = f"scale={width}:{height}:flags=lanczos,"
    bitrate = f"{int(target_bitrate_mbps)}M"
    maxrate = f"{int(target_bitrate_mbps * 1.2)}M"
    bufsize = f"{int(target_bitrate_mbps * 2.4)}M"
    if linear_ui_capture:
        grade_vf = scale_vf + "eq=contrast=1.04:brightness=0.01:saturation=1.02,unsharp=5:5:0.22:5:5:0.0"
    else:
        grade_vf = (
            scale_vf
            + "unsharp=5:5:0.35:5:5:0.0,eq=contrast=1.06:brightness=0.015:saturation=1.05,"
            "vignette=angle=PI/5:mode=forward"
        )
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(src),
            "-vf",
            grade_vf,
            *(
                ["-af", "loudnorm=I=-14:TP=-1.0:LRA=9"]
                if _has_audio_stream(src)
                else []
            ),
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            crf,
            "-b:v",
            bitrate,
            "-maxrate",
            maxrate,
            "-bufsize",
            bufsize,
            *(
                ["-c:a", "aac", "-b:a", abr]
                if _has_audio_stream(src)
                else []
            ),
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ],
        timeout=3600,
    )


def _write_srt(entries: list[tuple[float, float, str]], path: Path) -> None:
    lines: list[str] = []

    def _ts(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int((sec - int(sec)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    for i, (start, end, text) in enumerate(entries, 1):
        lines.append(str(i))
        lines.append(f"{_ts(start)} --> {_ts(end)}")
        lines.append(text.strip())
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _burn_captions(
    video: Path,
    srt: Path,
    out: Path,
    *,
    hero: bool = False,
    ultra: bool = False,
    ass: Path | None = None,
) -> None:
    sub = ass if ass and ass.is_file() else srt
    escaped = str(sub).replace(":", "\\:").replace("'", "\\'")
    crf, preset, _ = _enc_flags(hero=hero, ultra=ultra)
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(video),
            "-vf",
            f"subtitles='{escaped}'",
            "-c:a",
            "copy",
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            crf,
            str(out),
        ]
    )


def _publish_proof_embed() -> None:
    proof = ROOT / "SourceA-landing" / "green-unified" / "proof.html"
    if not proof.is_file() or not OUT_LANDING.is_file():
        return
    text = proof.read_text(encoding="utf-8")
    marker = "<!-- commercial-short-film:v1 -->"
    block = f"""{marker}
          <video class="sa-demo-film-video sa-commercial-film" controls preload="metadata" playsinline poster="/sourcea/assets/commercial-short-poster.svg">
            <source src="/sourcea/assets/commercial-short-demo.mp4" type="video/mp4" />
          </video>
          <p class="sa-metric-note">90-second commercial short · real UI capture · full stack</p>"""
    if marker in text:
        return
    needle = '<div class="sa-w1-player" id="sa-w1-player"'
    if needle not in text:
        return
    insert_at = text.find('<div class="sa-demo-film-copy">')
    if insert_at < 0:
        return
    text = text[:insert_at] + block + "\n        " + text[insert_at:]
    proof.write_text(text, encoding="utf-8")


def _accent_for(beat_id: str) -> str:
    return {
        "BLOCK": "#ef4444",
        "ALLOW": "#34d399",
        "OPS": "#60a5fa",
        "PROOF": "#f59e0b",
        "FACTORY": "#a78bfa",
        "PLATFORM": "#2dd4bf",
    }.get(beat_id, "#2dd4bf")


def _publish_max_seconds(spec: dict[str, Any], product: str) -> float:
    target = float(spec.get("runtime_target_seconds") or 0)
    if target >= 120:
        return max(target + 120.0, 300.0)
    if product == "witnessbc":
        return 300.0
    return 90.0


def _validate_publish_master(
    path: Path, *, product: str = "sourcea", spec: dict[str, Any] | None = None
) -> None:
    if not path.is_file():
        raise RuntimeError(f"FAIL: publish master missing — {path}")
    if not _has_audio_stream(path):
        raise RuntimeError(f"FAIL: publish master has no audio — {path}")
    max_seconds = _publish_max_seconds(spec or {}, product)
    dur = _segment_duration(path)
    if dur > max_seconds:
        raise RuntimeError(
            f"FAIL: publish master too long ({dur:.1f}s > {max_seconds}s) — wrong asset"
        )
    probe = subprocess.run([_ffmpeg(), "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Stream.* Video:.* (\d+)x(\d+)", probe.stderr)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        if h < 1200 and w >= 3000:
            raise RuntimeError(
                f"FAIL: publish master wrong aspect ({w}x{h}) — likely broken concat"
            )


def _resolve_publish_paths(
    spec: dict[str, Any], *, product: str | None = None
) -> tuple[list[Path], Path, Path]:
    pub = spec.get("publish") or {}
    lane = str(product or spec.get("routing_lane") or spec.get("product") or "sourcea")
    paths: list[Path] = []
    site_rel = pub.get("site_mp4")
    if site_rel:
        paths.append(ROOT / str(site_rel))
    w1_rel = pub.get("w1_mp4")
    if w1_rel:
        paths.append(ROOT / str(w1_rel))
    desktop_name = pub.get("desktop") or (
        "SourceA-Commercial-Short.mp4" if lane == "sourcea" else "Commercial-Short.mp4"
    )
    desktop = Path.home() / "Desktop" / str(desktop_name).replace("~/Desktop/", "")
    if pub.get("desktop"):
        paths.append(desktop)
    # SourceA landing asset only — WitnessBC v5 must never bleed into OUT_LANDING.
    if lane == "sourcea" and not site_rel:
        paths.append(OUT_LANDING)
    if lane == "sourcea" and desktop_name == "SourceA-Commercial-Short.mp4" and not pub.get("desktop"):
        paths.append(OUT_DESKTOP)
    paths = list(dict.fromkeys(paths))
    work_name = pub.get("work_dir") or "commercial-short-film-work-v1"
    work = SINA / str(work_name)
    receipt_name = pub.get("receipt") or "commercial-short-film-receipt-v1.json"
    receipt = SINA / "enforcement" / str(receipt_name)
    return paths, work, receipt


def finish_from_checkpoint(
    *,
    beats_path: Path,
    work: Path,
    skip_publish: bool = False,
) -> dict[str, Any]:
    """Resume polish + publish from commercial-short-raw.mp4 (no re-capture)."""
    spec = _read_json(beats_path)
    ck_path = work / "checkpoint.json"
    ck: dict[str, Any] = {}
    if ck_path.is_file():
        ck = json.loads(ck_path.read_text(encoding="utf-8"))
    product = str(
        ck.get("product") or spec.get("routing_lane") or spec.get("product") or "sourcea"
    )
    vo_lane = str(ck.get("vo_lane") or ("witnessbc" if product == "witnessbc" else "sourcea"))
    set_vo_lane(vo_lane)
    publish_paths, work_resolved, receipt_path = _resolve_publish_paths(spec, product=product)
    if work_resolved != work:
        work = work_resolved

    raw_out = work / "commercial-short-raw.mp4"
    if not raw_out.is_file():
        raise RuntimeError(f"FAIL: missing raw mp4: {raw_out}")

    gc = spec.get("global_capture") or {}
    polish = spec.get("polish") or {}
    master_w = int(ck.get("master_w") or gc.get("master_width") or gc.get("width") or 1920)
    master_h = int(ck.get("master_h") or gc.get("master_height") or gc.get("height") or 1080)
    quality_tier = str(ck.get("quality_tier") or spec.get("quality_tier") or "standard")
    ultra = quality_tier == "ultra"
    hero = ultra or quality_tier == "hero"
    film_style = str(ck.get("film_style") or spec.get("film_style") or "standard")
    commercial_capture = bool(ck.get("commercial_capture") if "commercial_capture" in ck else spec.get("commercial_capture"))
    linear_ui_capture = (
        commercial_capture and product == "witnessbc" and film_style == "linear_bar"
    ) or (commercial_capture and product == "sourcea")
    captions_mode = str(ck.get("captions_mode") or spec.get("captions_mode") or "full")
    target_bitrate_mbps = float(ck.get("target_bitrate_mbps") or polish.get("target_bitrate_mbps") or 10.0)

    srt_path = work / "captions.srt"
    ass_path = work / "captions.ass"
    words_path = work / "narration-words-v1.json"
    final_out = work / "commercial-short-demo.mp4"
    captioned = work / "commercial-short-captioned.mp4"

    if captions_mode == "chapter_only" or not srt_path.is_file():
        shutil.copy2(raw_out, captioned)
    elif ass_path.is_file():
        _burn_captions(raw_out, srt_path, captioned, hero=hero, ultra=ultra, ass=ass_path)
    elif srt_path.is_file():
        _burn_captions(raw_out, srt_path, captioned, hero=hero, ultra=ultra, ass=None)
    else:
        shutil.copy2(raw_out, captioned)

    _master_polish(
        captioned,
        final_out,
        ultra=ultra,
        pro=commercial_capture or has_elevenlabs(vo_lane),
        linear_ui_capture=linear_ui_capture,
        width=master_w,
        height=master_h,
        target_bitrate_mbps=target_bitrate_mbps,
    )

    published: list[str] = []
    if not skip_publish:
        _validate_publish_master(final_out, product=product, spec=spec)
        for dest in publish_paths:
            if product != "sourcea" and dest.resolve() == OUT_LANDING.resolve():
                raise RuntimeError(
                    f"FAIL: cross-lane publish blocked — {product} cannot write {OUT_LANDING}"
                )
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final_out, dest)
            published.append(str(dest))

    receipt = {
        "schema": "commercial-short-film-receipt-v1",
        "at": _now(),
        "status": "embed_live" if published else "filmed",
        "title": spec.get("title"),
        "product": product,
        "output": str(final_out),
        "published": published,
        "resolution": f"{master_w}x{master_h}",
        "recovered_from": "checkpoint",
        "checkpoint": str(ck_path) if ck_path.is_file() else None,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path)
    return receipt


def generate_film(
    *,
    beats_path: Path = BEATS_JSON,
    skip_publish: bool = False,
    vo_lane: str = "sourcea",
    product: str = "sourcea",
) -> dict[str, Any]:
    set_vo_lane(vo_lane)
    if product not in ("sourcea", "witnessbc"):
        raise ValueError(f"product must be sourcea or witnessbc, got {product!r}")
    spec = _read_json(beats_path)
    brand = spec.get("brand") or {}
    brand_name = str(brand.get("name") or "SourceA")
    card_footer = str(brand.get("card_footer") or f"{brand_name} · live product capture")
    publish_paths, work, receipt_path = _resolve_publish_paths(spec, product=product)
    gc = spec.get("global_capture") or {}
    width = int(gc.get("width") or 1920)
    height = int(gc.get("height") or 1080)
    sec_url = float(gc.get("seconds_per_url") or 4)
    zoom = float(gc.get("zoom") or 1.0)
    film_style = str(spec.get("film_style") or "standard")
    linear_style = film_style in ("linear_orientation", "linear_orientation_hero", "linear_bar")
    quality_tier = str(spec.get("quality_tier") or ("hero" if film_style == "linear_orientation_hero" else "standard"))
    ultra = quality_tier == "ultra"
    hero = ultra or quality_tier == "hero" or film_style in ("linear_orientation_hero", "linear_bar")
    linear_recut = bool(spec.get("linear_recut")) or film_style in (
        "linear_orientation_hero",
        "linear_orientation",
        "linear_bar",
    )
    chapter_captions = spec.get("chapter_captions", not linear_recut)
    captions_mode = str(spec.get("captions_mode") or "full")
    commercial_capture = bool(spec.get("commercial_capture"))
    linear_ui_capture = (
        (commercial_capture and product == "sourcea" and linear_style)
        or (commercial_capture and product == "witnessbc" and film_style == "linear_bar")
    )
    polish = spec.get("polish") or {}
    edge_voice = str(polish.get("edge_voice") or "en-US-AndrewMultilingualNeural")
    target_bitrate_mbps = float(polish.get("target_bitrate_mbps") or 10.0)
    cinematic_finish = bool(
        spec.get("cinematic_finish")
        or polish.get("cinematic_finish")
        or (linear_ui_capture and spec.get("proof_density"))
    )
    cinematic_sfx = bool(polish.get("sfx", True)) if cinematic_finish else False
    human_smooth = bool(spec.get("human_smooth")) and commercial_capture and product == "sourcea"
    fade_sec = 0.72 if (cinematic_finish and human_smooth) else (0.42 if cinematic_finish else 0.35)
    master_w = int(gc.get("master_width") or gc.get("width") or 1920)
    master_h = int(gc.get("master_height") or gc.get("height") or 1080)
    if linear_ui_capture:
        zoom = min(zoom, 1.0)
    elif hero or ultra:
        zoom = max(zoom, 1.4 if ultra else 1.35)

    if product == "witnessbc":
        _ensure_witnessbc_proof_lab()

    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    lane_label = "witnessbc" if product == "witnessbc" else "sourcea"
    _register_render(lane_label, work=work)

    film_t0 = time.perf_counter()
    timing_manifest: dict[str, Any] = {
        "schema": "beats-timing-v1",
        "at": _now(),
        "film_t0_perf_counter": film_t0,
        "beats": {},
        "capture": {},
        "urls": {},
    }
    beats_timing_path = work / "beats_timing.json"

    segments: list[Path] = []
    srt_entries: list[tuple[float, float, str]] = []
    all_words: list[dict[str, Any]] = []
    timeline = 0.0
    voice_engine = "macos_say"
    alignment_engine = "none"
    tamper_dwell_ms = 9500
    beat_ids: list[str] = []
    broll_sources: list[str] = []

    def _film_mark(beat_key: str, start: float, end: float) -> None:
        timing_manifest["beats"][beat_key] = [round(start, 3), round(end, 3)]

    logo_cold_open_sec = 1.2 if cinematic_finish else 1.5
    if brand.get("logo_cold_open") or (cinematic_finish and product == "sourcea"):
        logo_png = work / "logo-cold-open.png"
        _logo_cold_open_png(brand_name, logo_png, width=master_w, height=master_h)
        logo_vid = work / "logo-cold-open.mp4"
        _png_to_video(logo_png, logo_cold_open_sec, logo_vid)
        segments.append(logo_vid)
        timeline += logo_cold_open_sec
        _film_mark("logo_cold_open", 0.0, logo_cold_open_sec)

    hook_start = time.perf_counter() - film_t0
    hook_audio, voice_engine, hook_words = _narration_audio(
        spec.get("hook", ""), work, "hook", hero=hero, ultra=ultra, edge_voice=edge_voice, vo_lane=vo_lane
    )
    if hook_words:
        all_words.extend(offset_words(hook_words, timeline))
        alignment_engine = "elevenlabs_timestamps"
    hook_dur = _audio_duration(hook_audio)
    hook_broll_urls = list(brand.get("hook_broll_urls") or [])
    hook_broll_sec = float(
        brand.get("hook_broll_seconds")
        or max(hook_dur + 14.0, sec_url * max(len(hook_broll_urls), 1))
    )
    hook_png = work / "hook.png"
    _title_card_png(
        str(brand.get("hook_title") or "Controlled Agentic Automation"),
        str(brand.get("hook_subtitle") or "Execution Proof Infrastructure"),
        str(brand.get("hook_label") or "Commercial short"),
        hook_png,
        brand_name=brand_name,
    )
    hook_card_sec = float(
        brand.get("hook_card_seconds") if brand.get("hook_card_seconds") is not None else (0.5 if linear_style else 1.5)
    )
    if commercial_capture and ultra and film_style != "linear_bar" and brand.get("hook_card_seconds") is None:
        hook_card_sec = 0.0
    hook_vid = work / "hook-card.mp4"
    hook_proof = _urls_proof_focus(hook_broll_urls) and not linear_ui_capture
    if hook_broll_urls:
        hook_webm = work / "hook-broll.webm"
        _capture_urls_to_webm(
            hook_broll_urls,
            hook_webm,
            width=width,
            height=height,
            seconds_per_url=sec_url,
            zoom=zoom,
            linear_recut=linear_recut,
            commercial_capture=commercial_capture,
            beat_id="hook",
            timing_manifest=timing_manifest,
            product=product,
            w1_sequence=brand.get("hook_w1_sequence"),
            human_smooth=human_smooth,
        )
        hook_hq = work / "hook-broll-hq.mp4"
        if hook_webm.is_file() and hook_webm.stat().st_size > 1000:
            _transcode_capture_hq(
                hook_webm,
                hook_hq,
                ultra=ultra,
                proof_focus=hook_proof,
                linear_ui_capture=linear_ui_capture,
                src_width=width,
                src_height=height,
                out_width=master_w,
                out_height=master_h,
            )
            hook_src = hook_hq
        else:
            hook_src = hook_webm
        _broll_clip(
            hook_src,
            hook_broll_sec,
            hook_vid,
            offset=0,
            hero=hero,
            ultra=ultra,
            proof_focus=hook_proof,
            commercial_capture=commercial_capture,
            linear_ui_capture=linear_ui_capture,
            cinematic_finish=cinematic_finish,
            human_smooth=human_smooth,
            beat_id="hook",
            width=master_w,
            height=master_h,
        )
        if hook_card_sec > 0:
            title_flash = work / "hook-title-flash.mp4"
            _png_to_video(hook_png, min(hook_card_sec, 1.0), title_flash)
            hook_stitched = work / "hook-stitched.mp4"
            _concat_segments([title_flash, hook_vid], hook_stitched, hero=hero, ultra=ultra, fade_sec=0.25)
            hook_vid = hook_stitched
    elif hook_card_sec > 0:
        _png_to_video(hook_png, hook_card_sec, hook_vid)
    else:
        _png_to_video(hook_png, 0.35, hook_vid)
    hook_mux = work / "hook-mux.mp4"
    _mux_video_audio(
        hook_vid,
        hook_audio,
        hook_mux,
        pad_video=hook_broll_sec,
        hero=hero,
        ultra=ultra,
        beat_id="hook",
        cinematic_sfx=cinematic_sfx,
    )
    segments.append(hook_mux)
    srt_entries.append((timeline, timeline + hook_dur, spec.get("hook", "")))
    timeline += hook_broll_sec
    _film_mark("hook", hook_start, time.perf_counter() - film_t0)

    for beat_idx, beat in enumerate(spec.get("beats") or []):
        bid = str(beat.get("id") or f"beat{beat_idx}")
        beat_start = time.perf_counter() - film_t0
        beat_ids.append(bid)
        urls = beat.get("broll_urls") or []
        beat_sec = float(beat.get("seconds_per_url") or sec_url)
        beat_tamper_dwell_ms = int(float(beat.get("tamper_dwell_seconds") or tamper_dwell_ms / 1000.0) * 1000)
        proof_focus = _urls_proof_focus(urls) and not linear_ui_capture

        narr_audio, eng, narr_words = _narration_audio(
            str(beat.get("narration") or ""),
            work,
            f"{bid}-narr",
            hero=hero,
            ultra=ultra,
            edge_voice=edge_voice,
            vo_lane=vo_lane,
        )
        if eng == "elevenlabs":
            voice_engine = "elevenlabs"
        if narr_words:
            all_words.extend(offset_words(narr_words, timeline))
            alignment_engine = "elevenlabs_timestamps"
        narr_dur = _audio_duration(narr_audio)
        card_sec = float(beat.get("card_seconds") or (0.5 if linear_style else 2.5))
        broll_sec = max(float(beat.get("broll_seconds") or 10), narr_dur + (1.0 if linear_style else 0))

        if cinematic_finish and bid == "TRUST":
            wall_png = work / f"{bid}-built-on-wall.png"
            _built_on_wall_png(wall_png, width=master_w, height=master_h, brand_name=brand_name)
            broll_vid = work / f"{bid}-broll.mp4"
            _png_to_video(wall_png, broll_sec, broll_vid)
            broll_mux = work / f"{bid}-broll-mux.mp4"
            _mux_video_audio(
                broll_vid,
                narr_audio,
                broll_mux,
                pad_video=broll_sec,
                hero=hero,
                ultra=ultra,
                beat_id=bid,
                cinematic_sfx=cinematic_sfx,
            )
            segments.append(broll_mux)
            srt_entries.append((timeline, timeline + narr_dur, str(beat.get("narration") or "")))
            timeline += broll_sec
            _film_mark(bid, beat_start, time.perf_counter() - film_t0)
            continue

        if bid == "TAMPER":
            tamper_dwell_ms = beat_tamper_dwell_ms
        broll_webm = work / f"{bid}-broll.webm"
        _capture_urls_to_webm(
            urls,
            broll_webm,
            width=width,
            height=height,
            seconds_per_url=beat_sec,
            zoom=zoom,
            linear_recut=linear_recut,
            commercial_capture=commercial_capture,
            tamper_dwell_ms=beat_tamper_dwell_ms,
            beat_id=bid,
            timing_manifest=timing_manifest,
            product=product,
            w1_sequence=beat.get("w1_sequence"),
            human_smooth=human_smooth,
        )
        broll_sources.append(str(broll_webm))

        broll_hq = work / f"{bid}-broll-hq.mp4"
        if broll_webm.is_file() and broll_webm.stat().st_size > 1000:
            _transcode_capture_hq(
                broll_webm,
                broll_hq,
                ultra=ultra,
                proof_focus=proof_focus,
                linear_ui_capture=linear_ui_capture,
                src_width=width,
                src_height=height,
                out_width=master_w,
                out_height=master_h,
            )
            broll_src = broll_hq
        else:
            broll_src = broll_webm
        broll_vid = work / f"{bid}-broll.mp4"
        cluster = _tamper_cluster_window(timing_manifest, bid)
        capture_events = (timing_manifest.get("capture") or {}).get(bid, {}).get("events") or {}
        verdict_window = capture_events.get("tamper_verdict")
        sync_event = str(beat.get("sync_offset_event") or "")
        broll_offset = cluster[0] if cluster else 0.0
        if sync_event:
            w1_win = _w1_event_window(timing_manifest, bid, sync_event)
            if w1_win:
                broll_offset = w1_win[0]
        elif bid == "TAMPER" and verdict_window and len(verdict_window) == 2 and cluster:
            broll_offset = cluster[0]
            broll_sec = max(broll_sec, float(verdict_window[1]) - cluster[0] + 1.0)
        elif cluster:
            broll_offset = cluster[0]
        _broll_clip(
            broll_src,
            broll_sec,
            broll_vid,
            offset=broll_offset,
            hero=hero,
            ultra=ultra,
            proof_focus=proof_focus,
            commercial_capture=commercial_capture,
            linear_ui_capture=linear_ui_capture,
            cinematic_finish=cinematic_finish,
            beat_id=bid,
            width=master_w,
            height=master_h,
        )
        chapter_label = str(beat.get("label") or beat.get("title") or bid)
        beat_card_sec = float(beat.get("card_seconds") or 0)
        if commercial_capture and ultra and film_style != "linear_bar" and beat.get("card_seconds") is None:
            beat_card_sec = 0.0
        if linear_style and beat_card_sec > 0:
            flash_png = work / f"{bid}-flash.png"
            _title_card_png(
                str(beat.get("title") or bid),
                str(beat.get("label") or ""),
                card_footer,
                flash_png,
                accent=_accent_for(bid),
                brand_name=brand_name,
            )
            flash_vid = work / f"{bid}-flash.mp4"
            _png_to_video(flash_png, min(beat_card_sec, 1.0), flash_vid)
            stitched = work / f"{bid}-stitched.mp4"
            _concat_segments([flash_vid, broll_vid], stitched, hero=hero, ultra=ultra, fade_sec=fade_sec)
            broll_vid = stitched
        if linear_style:
            if chapter_captions:
                labeled = work / f"{bid}-broll-labeled.mp4"
                _overlay_chapter_label(
                    broll_vid, chapter_label, labeled, hero=hero, commercial=commercial_capture and ultra
                )
                broll_vid = labeled
            broll_mux = work / f"{bid}-broll-mux.mp4"
            _mux_video_audio(
                broll_vid,
                narr_audio,
                broll_mux,
                pad_video=broll_sec,
                hero=hero,
                ultra=ultra,
                beat_id=bid,
                cinematic_sfx=cinematic_sfx,
            )
            segments.append(broll_mux)
            srt_entries.append((timeline, timeline + narr_dur, str(beat.get("narration") or "")))
            timeline += broll_sec
            _film_mark(bid, beat_start, time.perf_counter() - film_t0)
            continue

        card_png = work / f"{bid}-card.png"
        _title_card_png(
            str(beat.get("title") or bid),
            str(beat.get("label") or ""),
            card_footer,
            card_png,
            accent=_accent_for(bid),
            brand_name=brand_name,
        )
        card_vid = work / f"{bid}-card.mp4"
        _png_to_video(card_png, card_sec, card_vid)
        card_mux = work / f"{bid}-card-mux.mp4"
        _mux_video_audio(card_vid, narr_audio, card_mux)

        broll_mux = work / f"{bid}-broll-mux.mp4"
        _mux_video_audio(broll_vid, narr_audio, broll_mux, pad_video=broll_sec)

        segments.extend([card_mux, broll_mux])
        srt_entries.append((timeline, timeline + narr_dur, str(beat.get("narration") or "")))
        timeline += card_sec + broll_sec
        _film_mark(bid, beat_start, time.perf_counter() - film_t0)

    cta = spec.get("cta") or {}
    cta_start = time.perf_counter() - film_t0
    if cta.get("narration"):
        cta_audio, cta_eng, cta_words = _narration_audio(
            str(cta["narration"]), work, "cta", hero=hero, ultra=ultra, edge_voice=edge_voice, vo_lane=vo_lane
        )
        if cta_eng == "elevenlabs":
            voice_engine = "elevenlabs"
        if cta_words:
            all_words.extend(offset_words(cta_words, timeline))
            alignment_engine = "elevenlabs_timestamps"
        cta_dur = _audio_duration(cta_audio)
        cta_png = work / "cta.png"
        _title_card_png(
            str(brand.get("cta_title") or "Book 15 minutes"),
            str(brand.get("cta_subtitle") or brand.get("domain") or (
                "sourcea-landing.vercel.app/sourcea" if product == "sourcea" else "witnessbc.com"
            )),
            "Live proof demo",
            cta_png,
            accent="#34d399",
            brand_name=brand_name,
        )
        cta_vid = work / "cta-card.mp4"
        cta_sec = float(cta.get("seconds") or (4 if linear_style else 7))
        if linear_style:
            cta_broll = work / "cta-broll.webm"
            cta_urls = cta.get("broll_urls") or brand.get("cta_broll_urls") or (
                ["http://127.0.0.1:5180/sourcea/proof.html"]
                if product == "sourcea"
                else ["http://127.0.0.1:8090/pricing.html"]
            )
            _capture_urls_to_webm(
                cta_urls,
                cta_broll,
                width=width,
                height=height,
                seconds_per_url=sec_url,
                zoom=zoom,
                linear_recut=linear_recut,
                commercial_capture=commercial_capture,
                beat_id="cta",
                timing_manifest=timing_manifest,
                product=product,
            )
            cta_hq = work / "cta-broll-hq.mp4"
            if cta_broll.is_file() and cta_broll.stat().st_size > 1000:
                _transcode_capture_hq(
                    cta_broll,
                    cta_hq,
                    ultra=ultra,
                    linear_ui_capture=linear_ui_capture,
                    src_width=width,
                    src_height=height,
                    out_width=master_w,
                    out_height=master_h,
                )
                cta_src = cta_hq
            else:
                cta_src = cta_broll
            _broll_clip(
                cta_src,
                cta_sec,
                cta_vid,
                offset=0,
                hero=hero,
                ultra=ultra,
                commercial_capture=commercial_capture,
                linear_ui_capture=linear_ui_capture,
                cinematic_finish=cinematic_finish,
                beat_id="cta",
                width=master_w,
                height=master_h,
            )
        else:
            _png_to_video(cta_png, cta_sec, cta_vid)
        cta_mux = work / "cta-mux.mp4"
        _mux_video_audio(
            cta_vid,
            cta_audio,
            cta_mux,
            pad_video=cta_sec if linear_style else None,
            hero=hero,
            ultra=ultra,
            beat_id="cta",
            cinematic_sfx=cinematic_sfx,
        )
        segments.append(cta_mux)
        srt_entries.append((timeline, timeline + cta_dur, str(cta["narration"])))
        timeline += cta_sec if linear_style else cta_dur
        _film_mark("cta", cta_start, time.perf_counter() - film_t0)

    beats_timing_path.write_text(json.dumps(timing_manifest, indent=2) + "\n", encoding="utf-8")
    raw_out = work / "commercial-short-raw.mp4"
    _concat_segments(segments, raw_out, hero=hero, ultra=ultra, fade_sec=fade_sec)
    _write_checkpoint(
        work,
        beats_path=beats_path,
        product=product,
        vo_lane=vo_lane,
        spec=spec,
        raw_out=raw_out,
        phase="post_concat",
    )
    srt_path = work / "captions.srt"
    ass_path = work / "captions.ass"
    words_path = work / "narration-words-v1.json"
    ass_font_size = 42 if (commercial_capture and ultra) else 54
    if all_words and captions_mode != "chapter_only":
        write_words_json(all_words, words_path)
        aligned_entries = words_to_phrase_srt_entries(all_words)
        _write_aligned_srt(aligned_entries, srt_path)
        write_ass(
            aligned_entries,
            ass_path,
            play_res=(master_w, master_h),
            size=ass_font_size,
        )
    elif all_words:
        write_words_json(all_words, words_path)
        aligned_entries = words_to_phrase_srt_entries(all_words)
        _write_aligned_srt(aligned_entries, srt_path)
        ass_path = None
    else:
        _write_srt(srt_entries, srt_path)
        words_path = None
        ass_path = None
    final_out = work / "commercial-short-demo.mp4"
    captioned = work / "commercial-short-captioned.mp4"
    if captions_mode == "chapter_only":
        shutil.copy2(raw_out, captioned)
    else:
        _burn_captions(
            raw_out,
            srt_path,
            captioned,
            hero=hero,
            ultra=ultra,
            ass=ass_path if ass_path and ass_path.is_file() else None,
        )
    _master_polish(
        captioned,
        final_out,
        ultra=ultra,
        pro=commercial_capture or voice_engine == "elevenlabs",
        linear_ui_capture=linear_ui_capture,
        width=master_w,
        height=master_h,
        target_bitrate_mbps=target_bitrate_mbps,
    )
    if not _has_audio_stream(final_out):
        raise RuntimeError(
            "FAIL: final film has no audio track — check silent logo segment / concat pipeline"
        )

    published: list[str] = []
    if not skip_publish:
        _validate_publish_master(final_out, product=product, spec=spec)
        for dest in publish_paths:
            if product != "sourcea" and dest.resolve() == OUT_LANDING.resolve():
                raise RuntimeError(
                    f"FAIL: cross-lane publish blocked — {product} cannot write {OUT_LANDING}"
                )
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final_out, dest)
            published.append(str(dest))
        if not spec.get("publish"):
            _publish_proof_embed()

    receipt = {
        "schema": "commercial-short-film-receipt-v1",
        "at": _now(),
        "status": "embed_live" if published else "filmed",
        "title": spec.get("title"),
        "product": product,
        "beats": beat_ids,
        "voice_engine": voice_engine,
        "alignment_engine": alignment_engine,
        "vo_lane": vo_lane,
        "elevenlabs_configured": has_elevenlabs(vo_lane),
        "elevenlabs_secrets_path": str(lane_secrets_path(vo_lane)),
        "resolution": f"{master_w}x{master_h}",
        "capture_resolution": f"{width}x{height}",
        "captions_mode": captions_mode,
        "broll_sources": broll_sources,
        "output": str(final_out),
        "published": published,
        "captions": str(srt_path),
        "captions_ass": str(ass_path) if ass_path else None,
        "narration_words": str(words_path) if words_path else None,
        "runtime_target_seconds": spec.get("runtime_target_seconds"),
        "film_style": film_style,
        "quality_tier": quality_tier,
        "linear_recut": linear_recut,
        "chapter_captions": chapter_captions,
        "polish_level": "ultra" if ultra else ("hero" if hero else "standard"),
        "linear_ui_capture": linear_ui_capture,
        "cinematic_finish": cinematic_finish,
        "human_smooth": human_smooth,
        "cinematic_sfx": cinematic_sfx,
        "quality_bar": str(ROOT / "data" / "video-quality-bar-v1.json") if linear_ui_capture else None,
        "grade": (
            "A+" if ultra and voice_engine == "elevenlabs" and alignment_engine == "elevenlabs_timestamps"
            else "A" if ultra and voice_engine in ("elevenlabs", "edge_neural")
            else "A" if hero and voice_engine == "elevenlabs" and alignment_engine == "elevenlabs_timestamps"
            else "A-" if hero and voice_engine in ("elevenlabs", "edge_neural")
            else "B+" if hero
            else "B+" if linear_style
            else "B"
        ),
        "law": ">=70% real UI · tamper FAIL dwell ≥8.5s on camera · burned-in captions",
        "tamper_dwell_ms": tamper_dwell_ms,
        "beats_timing": str(beats_timing_path),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate commercial short film (full stack UI capture)")
    ap.add_argument("--beats", type=Path, default=BEATS_JSON)
    ap.add_argument("--skip-publish", action="store_true")
    ap.add_argument("--refresh-voice", action="store_true", help="Bypass ElevenLabs cache; re-fetch all narration")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--force", action="store_true", help="Override render freeze (founder only)")
    args = ap.parse_args()
    set_refresh_voice(args.refresh_voice)
    from commercial_film_render_guard_v1 import assert_render_allowed  # noqa: WPS433

    assert_render_allowed(force=args.force)
    try:
        receipt = generate_film(beats_path=args.beats, skip_publish=args.skip_publish, product="sourcea")
    except (RuntimeError, SystemExit) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"OK: commercial short film · voice={receipt.get('voice_engine')}")
        print(f"OUTPUT={receipt.get('output')}")
        for p in receipt.get("published") or []:
            print(f"PUBLISHED={p}")
        print(f"RECEIPT={RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
