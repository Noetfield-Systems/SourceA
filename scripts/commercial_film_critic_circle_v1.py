#!/usr/bin/env python3
"""Commercial film critic circle — Observe · Analyze · Search · Learn · Improve.

GPT law: judge acceptability BEFORE ship. Blocks weak Playwright heroes from public embed.
Receipt: ~/.sina/enforcement/commercial-film-critic-circle-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
CONFIG = ROOT / "data" / "commercial-film-critic-circle-v1.json"
QUALITY_BAR = ROOT / "data" / "video-quality-bar-v1.json"
RECEIPT = SINA / "enforcement" / "commercial-film-critic-circle-receipt-v1.json"
FREEZE_FLAG = SINA / "commercial-film-render-frozen-v1.flag"
INCIDENTS = SINA / "commercial-film-critic-incidents-v1.jsonl"


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
            raise SystemExit("FAIL: ffmpeg missing")
        return exe


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _probe_video(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "path": str(path)}
    ff = _ffmpeg()
    proc = subprocess.run([ff, "-i", str(path)], capture_output=True, text=True)
    stderr = proc.stderr
    dur_m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", stderr)
    duration = 0.0
    if dur_m:
        h, m, s = dur_m.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)
    bitrate_m = re.search(r"bitrate: (\d+) kb/s", stderr)
    bitrate_kbps = int(bitrate_m.group(1)) if bitrate_m else 0
    video_m = re.search(
        r"Video:.* (\d+)x(\d+).*?(\d+) kb/s", stderr
    ) or re.search(r"Video:.* (\d+)x(\d+)", stderr)
    audio = "Audio:" in stderr
    width = height = 0
    if video_m:
        width, height = int(video_m.group(1)), int(video_m.group(2))
    return {
        "exists": True,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "duration_s": round(duration, 2),
        "width": width,
        "height": height,
        "bitrate_kbps": bitrate_kbps,
        "has_audio": audio,
    }


def _capture_method(receipt: dict[str, Any], probe: dict[str, Any]) -> str:
    law = str(receipt.get("law") or "")
    recovered = str(receipt.get("recovered_from") or "")
    broll = receipt.get("broll_sources") or []
    if receipt.get("source_tier") == "screen_studio_master":
        return "screen_studio"
    if receipt.get("alignment_engine") == "screen_studio":
        return "screen_studio"
    if "Screen Studio" in law or "screen_studio" in law.lower():
        return "screen_studio"
    if recovered == "checkpoint" and not broll:
        return "unknown_finish"
    if any(".webm" in str(x) for x in broll) or receipt.get("linear_ui_capture"):
        return "playwright_automated"
    if receipt.get("human_smooth"):
        return "playwright_human_smooth"
    if probe.get("duration_s", 0) > 120 and probe.get("height", 0) >= 2000:
        return "playwright_extended"
    return "unknown"


def _grade_asset(
    *,
    label: str,
    path: Path,
    receipt: dict[str, Any] | None,
    config: dict[str, Any],
    quality_bar: dict[str, Any],
) -> dict[str, Any]:
    gate = config.get("ship_gate") or {}
    probe = _probe_video(path)
    rec = receipt or {}
    claimed = str(rec.get("grade") or "none")
    capture = _capture_method(rec, probe)
    failures: list[str] = []
    warnings: list[str] = []

    if not probe.get("exists"):
        failures.append("file missing")
    if probe.get("exists") and not probe.get("has_audio") and gate.get("require_audio"):
        failures.append("no audio track")
    if probe.get("width") and probe.get("height"):
        if probe["height"] < 1200 and probe["width"] >= 3000:
            failures.append(f"wrong aspect {probe['width']}x{probe['height']}")
    min_br = int(gate.get("min_bitrate_kbps_4k") or 3000)
    if probe.get("height", 0) >= 2000 and probe.get("bitrate_kbps", 0) < min_br:
        failures.append(f"weak bitrate {probe.get('bitrate_kbps')} < {min_br} kbps for 4K")

    tier = "F"
    law = str(rec.get("law") or "")
    if capture == "screen_studio":
        tier = "S"
    elif "ingest" in law.lower() or "Screen Studio" in law:
        tier = "A"
    elif capture in ("playwright_automated", "playwright_human_smooth", "playwright_extended"):
        tier = "C"
        failures.append("Playwright automated capture — not buyer-grade hero (research: C+ dev only)")
    if gate.get("block_playwright_hero") and capture.startswith("playwright"):
        failures.append("ship_gate blocks Playwright public hero")

    if claimed in ("A+", "A") and tier in ("C", "F"):
        failures.append(f"grade inflation — receipt claims {claimed} but capture tier {tier}")
        if gate.get("block_grade_inflation"):
            warnings.append("receipt grade is marketing, not market truth")

    if rec.get("cinematic_finish") and capture.startswith("playwright"):
        warnings.append("cinematic_finish/vignette on automated capture — obscures UI per quality bar")

    min_public = str((config.get("ship_gate") or {}).get("min_tier_public") or "A")
    tier_order = {"F": 0, "C": 1, "B": 2, "A": 3, "S": 4}
    acceptable_public = tier_order.get(tier, 0) >= tier_order.get(min_public, 3) and not failures

    return {
        "label": label,
        "path": str(path),
        "probe": probe,
        "receipt_grade_claimed": claimed,
        "capture_method": capture,
        "tier": tier,
        "acceptable_public": acceptable_public,
        "failures": failures,
        "warnings": warnings,
        "verdict": "PASS" if acceptable_public else "BLOCK",
    }


def _witnessbc_receipt_path() -> Path:
    v5 = SINA / "enforcement/witnessbc-commercial-film-receipt-v5.json"
    if v5.is_file():
        rec = _read_json(v5)
        if rec.get("source_tier") == "screen_studio_master" or "Screen Studio" in str(rec.get("law") or ""):
            return v5
    return SINA / "enforcement/witnessbc-commercial-film-receipt-v1.json"


def _asset_catalog() -> list[tuple[str, Path, Path | None, str]]:
    wb_receipt = _witnessbc_receipt_path()
    return [
        (
            "sourcea_site_hero",
            ROOT / "SourceA-landing/green-unified/assets/commercial-short-demo.mp4",
            SINA / "enforcement/commercial-short-film-receipt-v1.json",
            "sourcea",
        ),
        (
            "sourcea_desktop",
            Path.home() / "Desktop/SourceA-Commercial-Short.mp4",
            SINA / "enforcement/commercial-short-film-receipt-v1.json",
            "sourcea",
        ),
        (
            "witnessbc_desktop",
            Path.home() / "Desktop/WitnessBC-Commercial.mp4",
            wb_receipt,
            "witnessbc",
        ),
        (
            "witnessbc_v5_desktop",
            Path.home() / "Desktop/WitnessBC-Commercial-v5.mp4",
            SINA / "enforcement/witnessbc-commercial-film-receipt-v5.json",
            "witnessbc",
        ),
        (
            "witnessbc_site",
            ROOT / "witnessbc-site/assets/witnessbc-commercial.mp4",
            wb_receipt,
            "witnessbc",
        ),
    ]


def _set_freeze(*, reason: str, until: str, next_action: str) -> None:
    config = _read_json(CONFIG)
    FREEZE_FLAG.write_text(
        json.dumps(
            {
                "frozen_at": _now(),
                "reason": reason,
                "until": until or config.get("frozen_until"),
                "next_action": next_action,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _clear_freeze() -> bool:
    if FREEZE_FLAG.is_file():
        try:
            FREEZE_FLAG.unlink()
            return True
        except OSError:
            return False
    return False


def run(
    *,
    write_freeze: bool = True,
    lane: str = "all",
) -> dict[str, Any]:
    config = _read_json(CONFIG)
    quality_bar = _read_json(QUALITY_BAR)
    lane = (lane or "all").strip().lower()
    assets = _asset_catalog()
    if lane in ("sourcea", "witnessbc"):
        assets = [a for a in assets if a[3] == lane]

    judgments: list[dict[str, Any]] = []
    for label, path, receipt_path, _lane in assets:
        receipt = _read_json(receipt_path) if receipt_path and receipt_path.is_file() else {}
        judgments.append(
            _grade_asset(
                label=label,
                path=path,
                receipt=receipt,
                config=config,
                quality_bar=quality_bar,
            )
        )

    public_labels = [j for j in judgments if "site" in j["label"] or "desktop" in j["label"]]
    all_public_block = any(j["verdict"] == "BLOCK" for j in public_labels) if public_labels else True
    ok = not all_public_block

    learnings = [
        "Founder rejection is correct — Playwright factory output is C tier, not Linear/S tier.",
        "Receipt A+ grades were pipeline self-grade, not buyer-grade — grade inflation incident.",
        "Only path to acceptable public hero: Screen Studio 4K master → Descript → ingest.",
        "Do not rerun commercial_short_film_v1.py for hero until critic circle PASS on ingest.",
    ]

    next_action = str(config.get("next_action_only") or "Screen Studio master + ingest only")
    verdict = "BLOCK" if all_public_block else "PASS"

    receipt_out = {
        "schema": "commercial-film-critic-circle-receipt-v1",
        "at": _now(),
        "ok": ok,
        "verdict": verdict,
        "loop": config.get("loop"),
        "quality_bar": str(QUALITY_BAR),
        "judgments": judgments,
        "learnings": learnings,
        "next_action_only": next_action,
        "render_frozen": verdict == "BLOCK",
        "frozen_reason": str(config.get("frozen_until") or "critic BLOCK on public assets"),
        "lane": lane,
    }

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt_out, indent=2) + "\n", encoding="utf-8")

    INCIDENTS.parent.mkdir(parents=True, exist_ok=True)
    with INCIDENTS.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "at": _now(),
                    "verdict": receipt_out["verdict"],
                    "lane": lane,
                    "blocked": [j["label"] for j in judgments if j["verdict"] == "BLOCK"],
                    "learning": learnings[0],
                }
            )
            + "\n"
        )

    if write_freeze:
        if receipt_out["verdict"] == "PASS":
            cleared = _clear_freeze()
            receipt_out["freeze_cleared"] = cleared
            receipt_out["render_frozen"] = False
            RECEIPT.write_text(json.dumps(receipt_out, indent=2) + "\n", encoding="utf-8")
        else:
            _set_freeze(
                reason="critic_circle BLOCK — no Playwright hero rerenders",
                until=str(config.get("frozen_until") or ""),
                next_action=next_action,
            )

    return receipt_out


def main() -> int:
    ap = argparse.ArgumentParser(description="Commercial film critic circle — judge before ship")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-freeze", action="store_true", help="Judge only; do not write freeze flag")
    ap.add_argument("--lane", choices=("all", "sourcea", "witnessbc"), default="all")
    args = ap.parse_args()
    out = run(write_freeze=not args.no_freeze, lane=args.lane)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"CRITIC_CIRCLE {out['verdict']} ok={out['ok']}")
        for j in out["judgments"]:
            print(f"  {j['label']}: {j['verdict']} tier={j['tier']} capture={j['capture_method']}")
            for f in j["failures"]:
                print(f"    FAIL: {f}")
        print(f"NEXT: {out['next_action_only']}")
        print(f"RECEIPT={RECEIPT}")
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
