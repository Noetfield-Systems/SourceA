#!/usr/bin/env python3
"""ElevenLabs alignment → word-aligned ASS captions (SSOT from synthesis, not ASR).

Convert /with-timestamps character alignment into burned-in .ass subtitles.
Jargon like tamper-FAIL and receipt hashes stay exact — no Whisper guessing.

Accepted input JSON shapes:
  1. Bare alignment: {characters, character_start_times_seconds, character_end_times_seconds}
  2. Full TTS response with "alignment" key
  3. film-narration-words-v1: {"schema": "...", "words": [{"word", "start", "end"}, ...]}
  4. List of any above; optional {"alignment": {...}, "offset": <seconds>} per segment

Usage:
  python3 scripts/elevenlabs_alignment_to_ass_v1.py in.json out.ass
  python3 scripts/elevenlabs_alignment_to_ass_v1.py in.json out.ass --font "Inter" --max-chars 34 --max-dur 3.5
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Word:
    text: str
    start: float
    end: float


def _extract_alignment(obj: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(obj.get("alignment"), dict):
        return obj["alignment"]
    if "characters" in obj:
        return obj
    return None


def chars_to_words(alignment: dict[str, Any], offset: float = 0.0) -> list[Word]:
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    words: list[Word] = []
    buf, w_start, w_end = "", None, None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if buf:
                words.append(Word(buf, w_start + offset, w_end + offset))
                buf, w_start, w_end = "", None, None
            continue
        if w_start is None:
            w_start = float(s)
        w_end = float(e)
        buf += c
    if buf:
        words.append(Word(buf, w_start + offset, w_end + offset))
    return words


def words_dicts_to_words(rows: list[dict[str, Any]], offset: float = 0.0) -> list[Word]:
    out: list[Word] = []
    for row in rows:
        token = str(row.get("word") or "").strip()
        if not token:
            continue
        out.append(
            Word(
                token,
                float(row.get("start", 0)) + offset,
                float(row.get("end", 0)) + offset,
            )
        )
    return out


def load_words(path: Path) -> list[Word]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict) and data.get("schema") == "film-narration-words-v1":
        return words_dicts_to_words(data.get("words") or [])

    segments = data if isinstance(data, list) else [data]
    words: list[Word] = []
    cursor = 0.0
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        if "words" in seg and isinstance(seg["words"], list):
            explicit = seg.get("offset")
            base = cursor if explicit is None else float(explicit)
            seg_words = words_dicts_to_words(seg["words"], base)
            words.extend(seg_words)
            if seg_words:
                cursor = seg_words[-1].end
            continue
        align = _extract_alignment(seg)
        if not align:
            continue
        explicit = seg.get("offset")
        base = cursor if explicit is None else float(explicit)
        seg_words = chars_to_words(align, base)
        words.extend(seg_words)
        if seg_words:
            cursor = seg_words[-1].end
    return words


def group_phrases(
    words: list[Word],
    *,
    max_chars: int = 34,
    max_dur: float = 3.5,
) -> list[tuple[float, float, str]]:
    """Pack words into short phrases — not karaoke single words."""
    phrases: list[tuple[float, float, str]] = []
    cur: list[Word] = []

    def flush() -> None:
        if cur:
            text = " ".join(w.text for w in cur)
            phrases.append((cur[0].start, cur[-1].end, text))
            cur.clear()

    for w in words:
        tentative = " ".join(x.text for x in (cur + [w]))
        dur = (w.end - cur[0].start) if cur else 0.0
        if cur and (len(tentative) > max_chars or dur > max_dur):
            flush()
        cur.append(w)
        if w.text and w.text[-1] in ".!?":
            flush()
    flush()
    return phrases


def group_phrases_from_dicts(
    words: list[dict[str, Any]],
    *,
    max_chars: int = 34,
    max_dur: float = 3.5,
    max_words: int = 7,
) -> list[tuple[float, float, str]]:
    """Pipeline adapter — dict words from film_elevenlabs_wire_v1."""
    typed = words_dicts_to_words(words)
    if not typed:
        return []
    phrases = group_phrases(typed, max_chars=max_chars, max_dur=max_dur)
    if phrases:
        return phrases
    # Fallback for very short clips
    chunk: list[Word] = []

    def flush() -> None:
        if chunk:
            phrases.append((chunk[0].start, chunk[-1].end, " ".join(w.text for w in chunk)))
            chunk.clear()

    for w in typed:
        prospective = " ".join(x.text for x in (chunk + [w]))
        if chunk and (len(chunk) >= max_words or len(prospective) > max_chars):
            flush()
        chunk.append(w)
    flush()
    return phrases


def ass_time(t: float) -> str:
    t = max(0.0, t)
    cs_total = int(round(t * 100))
    h, rem = divmod(cs_total, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


ASS_HEADER = """[Script Info]
Title: WitnessBC Commercial Captions
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,2,2,160,160,96,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_ass(
    phrases: list[tuple[float, float, str]],
    *,
    font: str = "Arial",
    size: int = 54,
    play_res: tuple[int, int] = (1920, 1080),
) -> str:
    w, h = play_res
    out = [ASS_HEADER.format(font=font, size=size, width=w, height=h)]
    for start, end, text in phrases:
        if end <= start:
            end = start + 0.05
        safe = text.strip().replace("\n", " ")
        out.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{safe}")
    return "\n".join(out) + "\n"


def write_ass_file(
    phrases: list[tuple[float, float, str]],
    path: Path,
    *,
    font: str = "Arial",
    size: int = 54,
    play_res: tuple[int, int] = (1920, 1080),
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_ass(phrases, font=font, size=size, play_res=play_res), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="ElevenLabs alignment JSON or film-narration-words-v1")
    ap.add_argument("output", type=Path, help="output .ass path")
    ap.add_argument("--font", default="Arial", help="brand sans font name")
    ap.add_argument("--size", type=int, default=54)
    ap.add_argument("--max-chars", type=int, default=34)
    ap.add_argument("--max-dur", type=float, default=3.5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    words = load_words(args.input)
    if not words:
        print("No words parsed — check alignment JSON shape.", file=sys.stderr)
        return 1
    phrases = group_phrases(words, max_chars=args.max_chars, max_dur=args.max_dur)
    write_ass_file(phrases, args.output, font=args.font, size=args.size)
    row = {
        "ok": True,
        "words": len(words),
        "phrases": len(phrases),
        "output": str(args.output),
    }
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"{len(words)} words -> {len(phrases)} caption phrases -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
