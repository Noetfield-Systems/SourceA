#!/usr/bin/env python3
"""Cinematic factory — captions from beats.json (no ASR)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _fmt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def _segments_from_beats(beats: dict[str, float], lines: list[str]) -> list[tuple[float, float]]:
    attempt = beats.get("attempt", beats.get("action_execute", beats.get("intent_start", 0)))
    block = beats.get("block", beats.get("block_state", attempt + 4))
    receipt = beats.get("receipt", beats.get("proof_generation", block + 4))
    end = beats.get("end", beats.get("audit_commit", receipt + 3))

    if len(lines) == 7:
        return [
            (0, attempt),
            (attempt, block),
            (block, block + 3),
            (block, receipt),
            (receipt, end),
            (receipt, end),
            (end, end + 2),
        ]
    # Generic: spread evenly across timeline
    span = max(end + 2, 1.0)
    step = span / max(len(lines), 1)
    return [(i * step, (i + 1) * step) for i in range(len(lines))]


def build_srt(beats: dict[str, float], script_lines: list[str]) -> str:
    segments = _segments_from_beats(beats, script_lines)
    out: list[str] = []
    for i, ((start, end), txt) in enumerate(zip(segments, script_lines), 1):
        if end <= start:
            end = start + 1.5
        out.extend([str(i), f"{_fmt(start)} --> {_fmt(end)}", txt.strip(), ""])
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build SRT from beats + script SSOT")
    ap.add_argument("--work-dir", type=Path, required=True)
    ap.add_argument("--script", type=Path, required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    beats_path = args.work_dir / "beats.json"
    beats: dict[str, Any] = json.loads(beats_path.read_text(encoding="utf-8"))
    lines = [ln.strip() for ln in args.script.read_text(encoding="utf-8").splitlines() if ln.strip()]

    srt = build_srt(beats, lines)
    out_path = args.work_dir / "assets" / "captions.srt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(srt + "\n", encoding="utf-8")

    payload = {"ok": True, "captions": str(out_path), "segments": len(lines)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"OK captions → {out_path}")


if __name__ == "__main__":
    main()
