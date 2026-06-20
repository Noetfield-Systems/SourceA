#!/usr/bin/env python3
"""Cinematic factory — Playwright truth engine (event graph + beats.json)."""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class _Timing:
    def __init__(self) -> None:
        self._t0 = time.time()
        self._beats: dict[str, float] = {}

    def record(self, key: str) -> float:
        t = round(time.time() - self._t0, 3)
        self._beats[key] = t
        return t

    def snapshot(self) -> dict[str, float]:
        return dict(self._beats)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _click_scenario(page, slug: str) -> bool:
    for sel in (
        f'.proof-scenario-card[data-scenario="{slug}"]',
        f'.proof-pill[data-scenario="{slug}"]',
        f'.roster li[data-scenario="{slug}"]',
    ):
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                el.scroll_into_view_if_needed(timeout=4000)
                el.click(timeout=5000)
                page.wait_for_timeout(600)
                return True
        except Exception:
            continue
    return False


def _wait_block(page, timing: _Timing) -> None:
    timing.record("policy_evaluation")
    for sel in (
        "#proofVerdictLive",
        ".proof-evidence-verdict.verdict-fail",
        "#proofTerminal .line.fail",
    ):
        try:
            page.locator(sel).first.wait_for(state="visible", timeout=15000)
            break
        except Exception:
            continue
    timing.record("enforcement_trigger")
    page.wait_for_timeout(1200)
    timing.record("block_state")


def _wait_receipt(page, timing: _Timing, *, dwell_ms: int = 5000) -> None:
    timing.record("proof_generation")
    for sel in ("[data-evidence-hash]", "#proofReceiptJson", "#proofEvidencePanel"):
        try:
            if page.locator(sel).first.count() > 0:
                page.locator(sel).first.scroll_into_view_if_needed(timeout=4000)
                break
        except Exception:
            continue
    page.wait_for_timeout(dwell_ms)
    timing.record("audit_commit")


def capture_witnessbc(
    base_url: str,
    *,
    headless: bool = True,
    video_dir: Path,
    hold_block_s: float = 6.0,
) -> tuple[Path, dict[str, float]]:
    from playwright.sync_api import sync_playwright

    timing = _Timing()
    timing.record("intent_start")

    video_dir.mkdir(parents=True, exist_ok=True)
    proof_url = f"{base_url.rstrip('/')}/proof.html#scenario=tool"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        page.goto(proof_url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("#proofScenarioCards .proof-scenario-card", timeout=25000)
        timing.record("action_hover")

        _click_scenario(page, "outbound")
        page.wait_for_timeout(2200)
        timing.record("action_execute")

        _click_scenario(page, "tool")
        page.wait_for_timeout(1800)
        _wait_block(page, timing)
        page.wait_for_timeout(int(hold_block_s * 1000))

        tamper_url = f"{base_url.rstrip('/')}/proof.html#scenario=tamper"
        page.goto(tamper_url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(1200)
        _click_scenario(page, "tamper")
        page.wait_for_timeout(2000)

        clicked = False
        for sel in ("#proofTamperBtn", ".proof-tamper-btn", "[data-action='tamper']"):
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.scroll_into_view_if_needed(timeout=3000)
                    el.hover(timeout=3000)
                    timing.record("action_hover")
                    page.wait_for_timeout(1500)
                    el.click(timeout=4000)
                    clicked = True
                    break
            except Exception:
                continue

        if clicked:
            _wait_block(page, timing)
            page.wait_for_timeout(int(hold_block_s * 1000))
            _wait_receipt(page, timing, dwell_ms=3500)
        else:
            _wait_receipt(page, timing, dwell_ms=4000)

        timing.record("end")
        page.wait_for_timeout(1500)

        video_path = Path(page.video.path()) if page.video else None
        context.close()
        browser.close()

    if not video_path or not video_path.is_file():
        raise SystemExit("FAIL: Playwright did not produce capture video")

    beats = timing.snapshot()
    beats["attempt"] = beats.get("action_execute", beats.get("intent_start", 0))
    beats["block"] = beats.get("block_state", beats.get("enforcement_trigger", 0))
    beats["receipt"] = beats.get("proof_generation", beats.get("audit_commit", 0))
    return video_path, beats


def capture_sourcea_w1(
    url: str,
    *,
    headless: bool = True,
    video_dir: Path,
) -> tuple[Path, dict[str, float]]:
    from playwright.sync_api import sync_playwright

    timing = _Timing()
    timing.record("intent_start")
    video_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(2000)
        timing.record("w1_allow")
        page.wait_for_timeout(4000)
        timing.record("w1_block")
        page.wait_for_timeout(6000)
        timing.record("w1_tamper")
        page.wait_for_timeout(5000)
        timing.record("audit_commit")
        timing.record("end")
        page.wait_for_timeout(1000)

        video_path = Path(page.video.path()) if page.video else None
        context.close()
        browser.close()

    if not video_path or not video_path.is_file():
        raise SystemExit("FAIL: Playwright did not produce capture video")

    beats = timing.snapshot()
    beats["attempt"] = beats.get("w1_allow", 0)
    beats["block"] = beats.get("w1_block", 0)
    beats["receipt"] = beats.get("w1_tamper", 0)
    return video_path, beats


def main() -> None:
    ap = argparse.ArgumentParser(description="Cinematic factory truth capture")
    ap.add_argument("--lane", required=True, choices=("witnessbc", "sourcea"))
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--headless", action="store_true", default=True)
    ap.add_argument("--headed", action="store_true", help="Human-smooth headed capture")
    ap.add_argument("--hold-block", type=float, default=6.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = _read_json(ROOT / "data" / "cinematic-film-factory-v1.json")
    lane = cfg["lanes"][args.lane]
    assets = args.work_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    headless = not args.headed
    if args.lane == "witnessbc":
        raw_webm, beats = capture_witnessbc(
            lane["capture_base"],
            headless=headless,
            video_dir=assets,
            hold_block_s=args.hold_block,
        )
    else:
        raw_webm, beats = capture_sourcea_w1(
            lane["capture_base"],
            headless=headless,
            video_dir=assets,
        )

    beats_path = args.work_dir / "beats.json"
    beats_path.write_text(json.dumps(beats, indent=2) + "\n", encoding="utf-8")

    out = {
        "ok": True,
        "lane": args.lane,
        "beats": beats,
        "raw_video": str(raw_webm),
        "beats_path": str(beats_path),
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"OK capture lane={args.lane} beats={beats_path}")


if __name__ == "__main__":
    main()
