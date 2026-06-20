#!/usr/bin/env python3
"""ElevenLabs VO + forced alignment — one shared API key, separate build outputs.

Shared key (SourceA + WitnessBC film builds):
  ~/.sina/elevenlabs-v1.env → ELEVENLABS_API_KEY · VOICE_ID · MODEL_ID

vo_lane (sourcea | witnessbc) only namespaces voice **cache** — different scripts, same key.
Each agent builds its film locally and publishes to its own repo/assets.

Flow:
  1. POST /v1/text-to-speech/{voice_id}/with-timestamps → mp3 + char alignment
  2. Fallback: plain TTS + POST /v1/forced-alignment
  3. Words JSON + phrase-level SRT/ASS for burn-in
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Literal

VoLane = Literal["sourcea", "witnessbc"]

SINA = Path.home() / ".sina"
SHARED_SECRETS = SINA / "elevenlabs-v1.env"
VO_LANES: tuple[VoLane, ...] = ("sourcea", "witnessbc")
DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"
DEFAULT_MODEL = "eleven_multilingual_v2"

SHARED_KEYS = {
    "api_key": "ELEVENLABS_API_KEY",
    "voice_id": "ELEVENLABS_VOICE_ID",
    "model_id": "ELEVENLABS_MODEL_ID",
}

# Lane = cache partition only (same API key)
LANE_CACHE: dict[VoLane, Path] = {
    "sourcea": SINA / "film-voice-cache-sourcea-v1",
    "witnessbc": SINA / "film-voice-cache-witnessbc-v1",
}

_LEGACY_KEY_ALIASES = (
    ("SOURCEA_ELEVENLABS_API_KEY", SINA / "sourcea-elevenlabs-v1.env"),
    ("WITNESSBC_ELEVENLABS_API_KEY", SINA / "witnessbc-elevenlabs-v1.env"),
    ("ELEVENLABS_API_KEY", SINA / "secrets.env"),
)

_ACTIVE_LANE: VoLane = "sourcea"
_REFRESH_VOICE = False


def _resolve_lane(lane: VoLane | str | None = None) -> VoLane:
    raw = lane or _ACTIVE_LANE
    if raw not in VO_LANES:
        raise ValueError(f"invalid vo_lane {raw!r} — must be one of {VO_LANES}")
    return raw  # type: ignore[return-value]


def set_vo_lane(lane: VoLane | str) -> None:
    global _ACTIVE_LANE
    _ACTIVE_LANE = _resolve_lane(lane)


def set_refresh_voice(refresh: bool) -> None:
    global _REFRESH_VOICE
    _REFRESH_VOICE = refresh


def lane_secrets_path(lane: VoLane | str | None = None) -> Path:
    """Shared ElevenLabs vault — same key for all film builds."""
    return SHARED_SECRETS


def _read_from_env_file(path: Path, key: str) -> str:
    if not path.is_file():
        return ""
    bare_eleven: str | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#") or not s:
            continue
        if "=" not in s:
            if (
                key.endswith("API_KEY")
                and s.startswith("sk_")
                and not s.startswith(("sk-or-", "sk_live_", "sk_test_"))
                and len(s) >= 40
            ):
                bare_eleven = s
            continue
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return bare_eleven or ""


def _read_shared_secret(key: str) -> str:
    val = _read_from_env_file(SHARED_SECRETS, key)
    if val:
        return val
    for legacy_key, legacy_path in _LEGACY_KEY_ALIASES:
        if key == SHARED_KEYS["api_key"]:
            val = _read_from_env_file(legacy_path, legacy_key)
            if val:
                return val
    if key == SHARED_KEYS["voice_id"]:
        for legacy_key, legacy_path in _LEGACY_KEY_ALIASES:
            vid = legacy_key.replace("API_KEY", "VOICE_ID")
            val = _read_from_env_file(legacy_path, vid)
            if val:
                return val
    if key == SHARED_KEYS["model_id"]:
        for legacy_key, legacy_path in _LEGACY_KEY_ALIASES:
            mid = legacy_key.replace("API_KEY", "MODEL_ID")
            val = _read_from_env_file(legacy_path, mid)
            if val:
                return val
    return os.environ.get(key, "").strip()


def has_elevenlabs(lane: VoLane | str | None = None) -> bool:
    return bool(_read_shared_secret(SHARED_KEYS["api_key"]))


def elevenlabs_config(lane: VoLane | str | None = None) -> dict[str, str]:
    lane = _resolve_lane(lane)
    return {
        "lane": lane,
        "secrets_path": str(SHARED_SECRETS),
        "api_key": _read_shared_secret(SHARED_KEYS["api_key"]),
        "voice_id": _read_shared_secret(SHARED_KEYS["voice_id"]) or DEFAULT_VOICE,
        "model_id": _read_shared_secret(SHARED_KEYS["model_id"]) or DEFAULT_MODEL,
    }


def upsert_elevenlabs_secret(key: str, value: str) -> Path:
    """Write into shared ~/.sina/elevenlabs-v1.env."""
    lines: list[str] = []
    if SHARED_SECRETS.is_file():
        lines = SHARED_SECRETS.read_text(encoding="utf-8", errors="replace").splitlines()
    prefix = f"{key}="
    out: list[str] = []
    found = False
    for line in lines:
        if line.startswith(prefix):
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(line)
    if not found:
        if not out:
            out.extend(["# Shared ElevenLabs — SourceA + WitnessBC film VO", ""])
        elif out[-1].strip():
            out.append("")
        out.append(f"{key}={value}")
    SHARED_SECRETS.parent.mkdir(parents=True, exist_ok=True)
    SHARED_SECRETS.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    try:
        SHARED_SECRETS.chmod(0o600)
    except OSError:
        pass
    return SHARED_SECRETS


def upsert_lane_secret(key: str, value: str, *, lane: VoLane | str) -> Path:
    """Alias — writes shared key (lane ignored)."""
    return upsert_elevenlabs_secret(key, value)


def _post_json(url: str, payload: dict[str, Any], *, api_key: str, timeout: int = 120) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _alignment_to_words(alignment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not alignment:
        return []
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    if not chars or len(chars) != len(starts) or len(chars) != len(ends):
        return []

    words: list[dict[str, Any]] = []
    buf = ""
    w_start: float | None = None
    w_end = 0.0

    def flush() -> None:
        nonlocal buf, w_start, w_end
        token = buf.strip()
        if token and w_start is not None:
            words.append({"word": token, "start": w_start, "end": w_end})
        buf = ""
        w_start = None
        w_end = 0.0

    for ch, st, en in zip(chars, starts, ends):
        if ch in (" ", "\n", "\t"):
            flush()
            continue
        if w_start is None:
            w_start = float(st)
        buf += ch
        w_end = float(en)
    flush()
    return words


def _tts_with_timestamps(text: str, out_mp3: Path, cfg: dict[str, str]) -> list[dict[str, Any]] | None:
    voice_id = cfg["voice_id"]
    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
        "?output_format=mp3_44100_192"
    )
    payload = {
        "text": text,
        "model_id": cfg["model_id"],
        "voice_settings": {"stability": 0.42, "similarity_boost": 0.82, "style": 0.28, "speed": 1.0},
    }
    try:
        data = _post_json(url, payload, api_key=cfg["api_key"])
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError):
        return None
    b64 = data.get("audio_base64")
    if not b64:
        return None
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    out_mp3.write_bytes(base64.b64decode(b64))
    if out_mp3.stat().st_size < 500:
        return None
    alignment = data.get("alignment") or data.get("normalized_alignment")
    words = _alignment_to_words(alignment)
    return words if words else None


def _tts_plain(text: str, out_mp3: Path, cfg: dict[str, str]) -> bool:
    voice_id = cfg["voice_id"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": text,
        "model_id": cfg["model_id"],
        "voice_settings": {"stability": 0.42, "similarity_boost": 0.82, "style": 0.28},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"xi-api-key": cfg["api_key"], "Content-Type": "application/json", "Accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            out_mp3.write_bytes(resp.read())
        return out_mp3.stat().st_size > 500
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _forced_align(audio: Path, text: str, cfg: dict[str, str]) -> list[dict[str, Any]] | None:
    boundary = "----SourceAFilmBoundary7MA4YWxkTrZu0gW"
    body_parts: list[bytes] = []
    for name, val, filename in (
        ("text", text, None),
        ("file", None, audio.name),
    ):
        body_parts.append(f"--{boundary}\r\n".encode())
        if filename:
            body_parts.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode())
            body_parts.append(b"Content-Type: audio/mpeg\r\n\r\n")
            body_parts.append(audio.read_bytes())
        else:
            body_parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            body_parts.append(val.encode("utf-8"))
        body_parts.append(b"\r\n")
    body_parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(body_parts)
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/forced-alignment",
        data=body,
        headers={"xi-api-key": cfg["api_key"], "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None
    words_raw = data.get("words") or []
    if words_raw and isinstance(words_raw[0], dict) and "word" in words_raw[0]:
        return [
            {"word": str(w.get("word") or ""), "start": float(w.get("start", 0)), "end": float(w.get("end", 0))}
            for w in words_raw
            if str(w.get("word") or "").strip()
        ]
    return _alignment_to_words(data.get("alignment"))


def _cache_dir(text: str, cfg: dict[str, str], lane: VoLane | str) -> Path:
    blob = f"{lane}|{cfg['voice_id']}|{cfg['model_id']}|{text}".encode("utf-8")
    key = hashlib.sha256(blob).hexdigest()[:16]
    return LANE_CACHE[_resolve_lane(lane)] / key


def _load_voice_cache(
    text: str, cfg: dict[str, str], out_mp3: Path, *, lane: VoLane | str
) -> tuple[bool, str, list[dict[str, Any]]] | None:
    if _REFRESH_VOICE or os.environ.get("ELEVENLABS_REFRESH") == "1":
        return None
    cdir = _cache_dir(text, cfg, lane)
    cached_mp3 = cdir / "audio.mp3"
    cached_words = cdir / "words.json"
    if not cached_mp3.is_file() or cached_mp3.stat().st_size < 500:
        return None
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cached_mp3, out_mp3)
    words: list[dict[str, Any]] = []
    eng = "elevenlabs_timestamps"
    if cached_words.is_file():
        try:
            words = json.loads(cached_words.read_text(encoding="utf-8")).get("words") or []
        except json.JSONDecodeError:
            words = []
    if not words:
        eng = "elevenlabs"
    return True, eng, words


def _save_voice_cache(
    text: str, cfg: dict[str, str], mp3: Path, words: list[dict[str, Any]], eng: str, *, lane: VoLane | str
) -> None:
    cdir = _cache_dir(text, cfg, lane)
    cdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp3, cdir / "audio.mp3")
    meta = {
        "schema": "film-voice-cache-v1",
        "lane": _resolve_lane(lane),
        "text": text,
        "alignment_engine": eng,
        "voice_id": cfg["voice_id"],
    }
    (cdir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if words:
        write_words_json(words, cdir / "words.json")


def synthesize_narration(
    text: str, out_mp3: Path, *, lane: VoLane | str | None = None
) -> tuple[bool, str, list[dict[str, Any]]]:
    """Returns (ok, alignment_engine, words). Shared API key; lane namespaces cache only."""
    text = (text or "").strip()
    if not text:
        return False, "none", []
    lane = _resolve_lane(lane)
    cfg = elevenlabs_config(lane)
    if not cfg["api_key"]:
        return False, "none", []

    cached = _load_voice_cache(text, cfg, out_mp3, lane=lane)
    if cached:
        return cached

    words = _tts_with_timestamps(text, out_mp3, cfg)
    if words:
        _save_voice_cache(text, cfg, out_mp3, words, "elevenlabs_timestamps", lane=lane)
        return True, "elevenlabs_timestamps", words

    if _tts_plain(text, out_mp3, cfg):
        words = _forced_align(out_mp3, text, cfg) or []
        eng = "elevenlabs_forced_alignment" if words else "elevenlabs"
        _save_voice_cache(text, cfg, out_mp3, words, eng, lane=lane)
        if words:
            return True, "elevenlabs_forced_alignment", words
        return True, "elevenlabs", []

    return False, "none", []


def offset_words(words: list[dict[str, Any]], offset_sec: float) -> list[dict[str, Any]]:
    return [
        {"word": w["word"], "start": float(w["start"]) + offset_sec, "end": float(w["end"]) + offset_sec}
        for w in words
    ]


def words_to_phrase_srt_entries(
    words: list[dict[str, Any]], *, max_words: int = 7, max_chars: int = 34, max_dur: float = 3.5
) -> list[tuple[float, float, str]]:
    from elevenlabs_alignment_to_ass_v1 import group_phrases_from_dicts  # noqa: WPS433

    return group_phrases_from_dicts(words, max_chars=max_chars, max_dur=max_dur, max_words=max_words)


def write_words_json(words: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema": "film-narration-words-v1", "words": words}, indent=2) + "\n",
        encoding="utf-8",
    )


def write_srt(entries: list[tuple[float, float, str]], path: Path) -> None:
    lines: list[str] = []

    def _ts(sec: float) -> str:
        sec = max(0.0, sec)
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int(round((sec - int(sec)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    for i, (start, end, text) in enumerate(entries, 1):
        if end <= start:
            end = start + 0.05
        lines.extend([str(i), f"{_ts(start)} --> {_ts(end)}", text.strip(), ""])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ass(
    entries: list[tuple[float, float, str]],
    path: Path,
    *,
    play_res: tuple[int, int] = (1920, 1080),
    size: int = 54,
    font: str = "Arial",
) -> None:
    from elevenlabs_alignment_to_ass_v1 import write_ass_file  # noqa: WPS433

    write_ass_file(entries, path, font=font, size=size, play_res=play_res)


def main() -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description="ElevenLabs film VO — shared key, lane cache")
    ap.add_argument("--lane", choices=VO_LANES, default="sourcea", help="cache namespace only")
    ap.add_argument("--check", action="store_true", help="Print config status (no API call)")
    ap.add_argument("--test", metavar="TEXT", help="Synthesize sample phrase to work dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    lane = _resolve_lane(args.lane)
    cfg = elevenlabs_config(lane)
    if args.check:
        ok = bool(cfg["api_key"])
        verify = {"ok": False, "error": "missing_key"}
        if ok:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from sourcea_elevenlabs_vo_setup_v1 import _verify_key  # noqa: WPS433

            verify = _verify_key(cfg["api_key"], voice_id=cfg["voice_id"], model_id=cfg["model_id"])
            ok = verify.get("ok", False)
        row = {
            "ok": ok,
            "lane": lane,
            "elevenlabs_configured": bool(cfg["api_key"]),
            "key_valid": verify.get("ok", False),
            "voice_id": cfg["voice_id"],
            "model_id": cfg["model_id"],
            "secrets_path": cfg["secrets_path"],
            "verify": verify,
            "hint": f"ElevenLabs VO live for {lane} — re-run film with --refresh-voice"
            if ok
            else "Add ELEVENLABS_API_KEY via scripts/sourcea_elevenlabs_vo_setup_v1.py",
        }
        print(json.dumps(row, indent=2) if args.json else ("PASS: ElevenLabs configured" if row["ok"] else f"FAIL: {lane} key missing"))
        return 0 if row["ok"] else 1
    if args.test:
        out = SINA / f"film-elevenlabs-wire-test-{lane}-v1" / "sample.mp3"
        ok, eng, words = synthesize_narration(args.test, out, lane=lane)
        row = {"ok": ok, "lane": lane, "alignment_engine": eng, "words": len(words), "output": str(out)}
        if words:
            write_words_json(words, out.with_suffix(".words.json"))
        print(json.dumps(row, indent=2) if args.json else str(row))
        return 0 if ok else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
