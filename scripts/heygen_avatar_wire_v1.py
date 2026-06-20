#!/usr/bin/env python3
"""HeyGen Photo Avatar API — upload assets, talking photo, poll, download.

Secrets: ~/.sina/heygen-v1.env → HEYGEN_API_KEY

Flow (high quality):
  1. POST /v3/assets — master image + ElevenLabs mp3
  2. POST /v3/avatars — reusable photo avatar (cached by image hash)
  3. POST /v3/videos — type avatar · audio_asset_id · 1080p · motion
  4. GET /v3/videos/{id} — poll until completed
  5. Download video_url → local mp4
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
HEYGEN_SECRETS = SINA / "heygen-v1.env"
HEYGEN_EXAMPLE = SINA / "heygen-v1.env.example"
API_BASE = "https://api.heygen.com"
DEFAULT_QUALITY: dict[str, Any] = {
    "resolution": "1080p",
    "aspect_ratio": "auto",
    "expressiveness": "high",
    "motion_prompt": "natural subtle head movement, professional presenter, confident eye contact",
    "engine": {"type": "avatar_v"},
    "poll_interval_sec": 10,
    "poll_timeout_sec": 900,
}


def _read_env_file(path: Path, key: str) -> str:
    if not path.is_file():
        return os.environ.get(key, "").strip()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return os.environ.get(key, "").strip()


def has_heygen() -> bool:
    return bool(_read_env_file(HEYGEN_SECRETS, "HEYGEN_API_KEY"))


def heygen_config() -> dict[str, str]:
    return {
        "secrets_path": str(HEYGEN_SECRETS),
        "api_key": _read_env_file(HEYGEN_SECRETS, "HEYGEN_API_KEY"),
    }


def upsert_heygen_secret(key: str, value: str) -> Path:
    lines: list[str] = []
    if HEYGEN_SECRETS.is_file():
        lines = HEYGEN_SECRETS.read_text(encoding="utf-8", errors="replace").splitlines()
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
            out.extend(["# HeyGen API — avatar pipeline (LinkedIn / tier C social)", ""])
        elif out[-1].strip():
            out.append("")
        out.append(f"{key}={value}")
    HEYGEN_SECRETS.parent.mkdir(parents=True, exist_ok=True)
    HEYGEN_SECRETS.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    try:
        HEYGEN_SECRETS.chmod(0o600)
    except OSError:
        pass
    return HEYGEN_SECRETS


def write_env_example() -> Path:
    text = "\n".join(
        [
            "# HeyGen API key — avatar pipeline (LinkedIn / tier C social only)",
            "# Get key: https://app.heygen.com/settings?nav=API",
            "#",
            "HEYGEN_API_KEY=your_heygen_api_key_here",
            "",
        ]
    )
    HEYGEN_EXAMPLE.parent.mkdir(parents=True, exist_ok=True)
    HEYGEN_EXAMPLE.write_text(text, encoding="utf-8")
    return HEYGEN_EXAMPLE


def _mask_key(key: str) -> str:
    key = (key or "").strip()
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}…{key[-4:]}"


def _api_json(
    method: str,
    path: str,
    *,
    api_key: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    data = None
    headers = {"X-Api-Key": api_key, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _upload_asset(file_path: Path, *, api_key: str) -> str:
    mime, _ = mimetypes.guess_type(str(file_path))
    if not mime:
        ext = file_path.suffix.lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".mp3": "audio/mpeg"}.get(
            ext, "application/octet-stream"
        )
    content = file_path.read_bytes()
    boundary = "----SourceAHeyGenBoundary7MA4YWxkTrZu0gW"
    body_parts: list[bytes] = [
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode(),
        f"Content-Type: {mime}\r\n\r\n".encode(),
        content,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    body = b"".join(body_parts)
    req = urllib.request.Request(
        f"{API_BASE}/v3/assets",
        data=body,
        headers={"X-Api-Key": api_key, "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    asset_id = ((data.get("data") or {}).get("asset_id") or "").strip()
    if not asset_id:
        raise RuntimeError(f"asset upload missing asset_id: {data}")
    return asset_id


def _download_url(url: str, dest: Path, *, timeout: int = 300) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "SourceA-AvatarPipeline/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.read())


def _avatar_cache_path(cache_dir: Path) -> Path:
    return cache_dir / "heygen-photo-avatar-cache-v1.json"


def _load_avatar_cache(cache_dir: Path) -> dict[str, Any]:
    path = _avatar_cache_path(cache_dir)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_avatar_cache(cache_dir: Path, row: dict[str, Any]) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    _avatar_cache_path(cache_dir).write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _image_fingerprint(image_path: Path) -> str:
    h = hashlib.sha256()
    h.update(image_path.read_bytes())
    return h.hexdigest()


def _get_or_create_photo_avatar(
    *,
    api_key: str,
    image_path: Path,
    cache_dir: Path,
    avatar_name: str = "SourceA Founder Photo Avatar",
) -> tuple[str, str]:
    fingerprint = _image_fingerprint(image_path)
    cached = _load_avatar_cache(cache_dir)
    if cached.get("image_sha256") == fingerprint and cached.get("avatar_id"):
        return str(cached["avatar_id"]), str(cached.get("image_asset_id") or "")

    image_asset_id = _upload_asset(image_path, api_key=api_key)
    resp = _api_json(
        "POST",
        "/v3/avatars",
        api_key=api_key,
        payload={
            "type": "photo",
            "name": avatar_name,
            "file": {"type": "asset_id", "asset_id": image_asset_id},
        },
    )
    avatar_item = (resp.get("data") or {}).get("avatar_item") or {}
    avatar_id = str(avatar_item.get("id") or "").strip()
    if not avatar_id:
        raise RuntimeError(f"photo avatar create failed: {resp}")
    _save_avatar_cache(
        cache_dir,
        {
            "schema": "heygen-photo-avatar-cache-v1",
            "image_sha256": fingerprint,
            "image_asset_id": image_asset_id,
            "avatar_id": avatar_id,
            "avatar_name": avatar_name,
        },
    )
    return avatar_id, image_asset_id


def _poll_video(
    *,
    api_key: str,
    video_id: str,
    poll_interval_sec: float,
    poll_timeout_sec: float,
) -> tuple[bool, str, str | None]:
    deadline = time.time() + poll_timeout_sec
    last_status = "unknown"
    while time.time() < deadline:
        resp = _api_json("GET", f"/v3/videos/{video_id}", api_key=api_key, timeout=60)
        data = resp.get("data") or resp
        last_status = str(data.get("status") or "unknown")
        if last_status == "completed":
            url = str(data.get("video_url") or "").strip()
            return True, last_status, url or None
        if last_status == "failed":
            msg = str(data.get("failure_message") or data.get("error") or "generation failed")
            return False, msg, None
        time.sleep(poll_interval_sec)
    return False, f"timeout after {int(poll_timeout_sec)}s (last={last_status})", None


def verify_key(api_key: str) -> dict[str, Any]:
    api_key = (api_key or "").strip()
    if not api_key:
        return {"ok": False, "error": "missing_key"}
    try:
        resp = _api_json("GET", "/v3/voices?limit=1", api_key=api_key, timeout=60)
        voices = (resp.get("data") or {}).get("voices")
        if voices is None and resp.get("error"):
            err = resp.get("error") or {}
            return {"ok": False, "error": err.get("code") or "api_error", "detail": err.get("message")}
        return {"ok": True, "method": "list_voices", "voice_count_hint": len(voices or [])}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        detail = {}
        try:
            parsed = json.loads(body)
            detail = parsed.get("error") or parsed
        except json.JSONDecodeError:
            detail = {"message": body[:200]}
        if exc.code == 401:
            return {"ok": False, "error": "invalid_api_key", "detail": detail}
        return {"ok": False, "error": f"http_{exc.code}", "detail": detail}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": "network", "detail": str(exc)}


def generate_talking_photo(
    *,
    api_key: str,
    image_path: Path,
    audio_path: Path,
    out_mp4: Path,
    cache_dir: Path,
    quality: dict[str, Any] | None = None,
    title: str = "SourceA Avatar Pipeline",
    _allow_engine_fallback: bool = True,
) -> tuple[bool, str]:
    """Upload ElevenLabs audio + photo avatar → 1080p talking head mp4."""
    q = {**DEFAULT_QUALITY, **(quality or {})}
    if not api_key:
        return False, "missing HEYGEN_API_KEY"
    if not image_path.is_file():
        return False, f"master image missing: {image_path}"
    if not audio_path.is_file() or audio_path.stat().st_size < 500:
        return False, f"voice audio missing: {audio_path}"

    try:
        avatar_id, _ = _get_or_create_photo_avatar(api_key=api_key, image_path=image_path, cache_dir=cache_dir)
        audio_asset_id = _upload_asset(audio_path, api_key=api_key)

        payload: dict[str, Any] = {
            "type": "avatar",
            "avatar_id": avatar_id,
            "audio_asset_id": audio_asset_id,
            "title": title,
            "resolution": q.get("resolution") or "1080p",
            "aspect_ratio": q.get("aspect_ratio") or "auto",
        }
        motion = q.get("motion_prompt")
        if motion:
            payload["motion_prompt"] = str(motion)
        engine = q.get("engine")
        if engine:
            payload["engine"] = engine
            # expressiveness rejected on avatar_v — only set for avatar_iv/default
            if isinstance(engine, dict) and engine.get("type") == "avatar_v":
                pass
            elif q.get("expressiveness"):
                payload["expressiveness"] = q["expressiveness"]
        elif q.get("expressiveness"):
            payload["expressiveness"] = q["expressiveness"]

        create = _api_json("POST", "/v3/videos", api_key=api_key, payload=payload)
        video_id = str((create.get("data") or {}).get("video_id") or "").strip()
        if not video_id:
            return False, f"create video failed: {create}"

        ok, note, video_url = _poll_video(
            api_key=api_key,
            video_id=video_id,
            poll_interval_sec=float(q.get("poll_interval_sec") or 10),
            poll_timeout_sec=float(q.get("poll_timeout_sec") or 900),
        )
        if not ok or not video_url:
            # Retry once with Avatar IV + expressiveness if avatar_v poll/generation failed
            if _allow_engine_fallback and isinstance(engine, dict) and engine.get("type") == "avatar_v":
                fallback_q = dict(q)
                fallback_q.pop("engine", None)
                fallback_q["expressiveness"] = q.get("expressiveness") or "high"
                return generate_talking_photo(
                    api_key=api_key,
                    image_path=image_path,
                    audio_path=audio_path,
                    out_mp4=out_mp4,
                    cache_dir=cache_dir,
                    quality=fallback_q,
                    title=title + " (avatar_iv fallback)",
                    _allow_engine_fallback=False,
                )
            return False, note or "poll failed"

        _download_url(video_url, out_mp4)
        if not out_mp4.is_file() or out_mp4.stat().st_size < 5000:
            return False, "downloaded mp4 too small"
        return True, f"heygen_v3 photo avatar · video_id={video_id} · {note}"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        try:
            err = json.loads(body).get("error") or {}
            msg = err.get("message") or body[:240]
        except json.JSONDecodeError:
            msg = body[:240] or str(exc.reason)
        return False, f"http_{exc.code}: {msg}"
    except (urllib.error.URLError, TimeoutError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        return False, str(exc)
