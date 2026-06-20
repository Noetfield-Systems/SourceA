#!/usr/bin/env python3
"""Wire shared ElevenLabs API key — SourceA + WitnessBC film builds use the same key.

Usage:
  python3 scripts/sourcea_elevenlabs_vo_setup_v1.py --check --json
  python3 scripts/sourcea_elevenlabs_vo_setup_v1.py --api-key 'sk_...' --json

Writes ~/.sina/elevenlabs-v1.env (shared):
  ELEVENLABS_API_KEY
  ELEVENLABS_VOICE_ID   (optional · default Rachel)
  ELEVENLABS_MODEL_ID   (optional · eleven_multilingual_v2)

Separation is at **build + publish** — each agent renders its film and uploads to its repo.
WitnessBC film script reads the same key automatically.

Receipt: ~/.sina/enforcement/elevenlabs-vo-setup-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "enforcement" / "elevenlabs-vo-setup-receipt-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from film_elevenlabs_wire_v1 import (  # noqa: E402
    SHARED_KEYS,
    SHARED_SECRETS,
    elevenlabs_config,
    set_vo_lane,
    synthesize_narration,
    upsert_elevenlabs_secret,
)

DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"
DEFAULT_MODEL = "eleven_multilingual_v2"
DASHBOARD = "https://elevenlabs.io/app/developers/api-keys"
_BARE_ELEVEN = re.compile(r"^sk_[a-f0-9]{32,}$")
_KEY_EXTRACT = re.compile(r"(sk_[a-f0-9]{32,})")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_api_key(raw: str) -> tuple[str, str | None]:
    raw = (raw or "").strip()
    if not raw:
        return "", "empty"
    if "\n" in raw or len(raw) > 80:
        found = _KEY_EXTRACT.findall(raw)
        if len(found) == 1:
            return found[0], None
        if len(found) > 1:
            return "", "multiple_keys_in_paste"
        return "", "clipboard_not_key"
    if not raw.startswith("sk_"):
        return "", "clipboard_not_key"
    if not _BARE_ELEVEN.match(raw):
        return "", "bad_key_shape"
    return raw, None


def organize_secrets() -> dict:
    """Promote bare sk_* from elevenlabs-v1.env or legacy files → named keys."""
    for path in (SHARED_SECRETS, SINA / "sourcea-elevenlabs-v1.env", SINA / "secrets.env"):
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if any(ln.startswith(f"{SHARED_KEYS['api_key']}=") for ln in lines):
            return {"ok": True, "action": "already_named", "path": str(SHARED_SECRETS)}
        bare = next((ln.strip() for ln in lines if _BARE_ELEVEN.match(ln.strip())), None)
        if bare:
            upsert_elevenlabs_secret(SHARED_KEYS["api_key"], bare)
            upsert_elevenlabs_secret(SHARED_KEYS["voice_id"], DEFAULT_VOICE)
            upsert_elevenlabs_secret(SHARED_KEYS["model_id"], DEFAULT_MODEL)
            return {"ok": True, "action": "organized", "key_mask": _mask_key(bare), "path": str(SHARED_SECRETS)}
    return {"ok": False, "error": "no_bare_elevenlabs_key", "path": str(SHARED_SECRETS)}


def _verify_key(api_key: str, *, voice_id: str = DEFAULT_VOICE, model_id: str = DEFAULT_MODEL) -> dict:
    api_key = (api_key or "").strip()
    if not api_key:
        return {"ok": False, "error": "missing_key"}
    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
        "?output_format=mp3_44100_192"
    )
    payload = json.dumps({"text": "Verify.", "model_id": model_id}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        if data.get("audio_base64"):
            return {"ok": True, "method": "tts_with_timestamps", "restricted_key": True}
        return {"ok": False, "error": "no_audio", "method": "tts_with_timestamps"}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        detail = {}
        try:
            detail = json.loads(body).get("detail") or {}
        except json.JSONDecodeError:
            pass
        status = detail.get("status") if isinstance(detail, dict) else None
        message = detail.get("message") if isinstance(detail, dict) else body[:200]
        if exc.code == 401 and status == "missing_permissions":
            return {
                "ok": False,
                "error": "missing_tts_permission",
                "detail": message,
                "founder_hint": "Create key with Text to Speech → Access (not No Access)",
            }
        if exc.code == 401 and status == "invalid_api_key":
            return {"ok": False, "error": "invalid_api_key", "detail": message}
        return {"ok": False, "error": f"http_{exc.code}", "detail": message or str(exc.reason)}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": "network", "detail": str(exc)}


def _mask_key(key: str) -> str:
    key = (key or "").strip()
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}…{key[-4:]}"


def check_status() -> dict:
    cfg = elevenlabs_config()
    verify = (
        _verify_key(cfg["api_key"], voice_id=cfg["voice_id"], model_id=cfg["model_id"])
        if cfg["api_key"]
        else {"ok": False, "error": "missing_key"}
    )
    return {
        "ok": bool(cfg["api_key"]) and verify.get("ok"),
        "schema": "elevenlabs-vo-setup-v1",
        "at": _now(),
        "elevenlabs_configured": bool(cfg["api_key"]),
        "key_valid": verify.get("ok", False),
        "key_mask": _mask_key(cfg["api_key"]) if cfg["api_key"] else None,
        "voice_id": cfg["voice_id"],
        "model_id": cfg["model_id"],
        "secrets_path": str(SHARED_SECRETS),
        "shared_by": ["sourcea", "witnessbc"],
        "separation": "build + publish per repo — same API key",
        "dashboard": DASHBOARD,
        "verify": verify,
        "film_scripts": [
            "scripts/run_commercial_short_film_v1.sh",
            "scripts/w1_film_generate_v1.py",
            "scripts/witnessbc-commercial-film.sh",
        ],
        "founder_line": (
            "ElevenLabs live — SourceA + WitnessBC film scripts share this key"
            if verify.get("ok")
            else "Paste sk_ key once — wires both SourceA and WitnessBC film VO"
        ),
    }


def save_key(*, api_key: str, voice_id: str, model_id: str) -> dict:
    api_key, norm_err = _normalize_api_key(api_key)
    if norm_err:
        hints = {
            "empty": "No key provided",
            "clipboard_not_key": "Copy ONLY the sk_ key from ElevenLabs",
            "multiple_keys_in_paste": "Paste contains multiple sk_ tokens",
            "bad_key_shape": "Key must look like sk_ plus hex characters",
        }
        return {"ok": False, "error": norm_err, "dashboard": DASHBOARD, "founder_line": hints.get(norm_err, "Invalid key")}
    verify = _verify_key(api_key, voice_id=voice_id, model_id=model_id)
    if not verify.get("ok"):
        hint = verify.get("founder_hint") or f"Key verify failed: {verify.get('error')}"
        return {"ok": False, "error": verify.get("error", "invalid_key"), "verify": verify, "founder_line": hint}

    upsert_elevenlabs_secret(SHARED_KEYS["api_key"], api_key)
    upsert_elevenlabs_secret(SHARED_KEYS["voice_id"], voice_id)
    upsert_elevenlabs_secret(SHARED_KEYS["model_id"], model_id)

    set_vo_lane("sourcea")
    test_mp3 = SINA / "film-elevenlabs-wire-test-v1" / "setup-phrase.mp3"
    tts_ok, align_eng, words = synthesize_narration(
        "SourceA runs controlled agentic automation — policy at dispatch, verification built in.",
        test_mp3,
        lane="sourcea",
    )

    row = {
        "ok": True,
        "schema": "elevenlabs-vo-setup-v1",
        "at": _now(),
        "key_mask": _mask_key(api_key),
        "voice_id": voice_id,
        "model_id": model_id,
        "verify": verify,
        "tts_test": {"ok": tts_ok, "alignment_engine": align_eng, "words": len(words), "mp3": str(test_mp3)},
        "secrets_path": str(SHARED_SECRETS),
        "shared_by": ["sourcea", "witnessbc"],
        "founder_line": "ElevenLabs wired — re-run SourceA or WitnessBC film scripts",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Wire shared ElevenLabs VO (SourceA + WitnessBC films)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--organize", action="store_true", help="Name bare sk_* in elevenlabs-v1.env")
    ap.add_argument("--api-key")
    ap.add_argument("--voice-id", default=DEFAULT_VOICE)
    ap.add_argument("--model-id", default=DEFAULT_MODEL)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.check:
        row = check_status()
        print(json.dumps(row, indent=2) if args.json else row["founder_line"])
        return 0 if row.get("ok") else 1

    if args.organize:
        row = organize_secrets()
        if row.get("ok") and row.get("action") == "organized":
            row = {**row, **check_status()}
        print(json.dumps(row, indent=2) if args.json else row.get("founder_line") or row.get("error"))
        return 0 if row.get("ok") and row.get("key_valid", True) else 1

    key = (args.api_key or "").strip() or sys.stdin.read().strip()
    key, norm_err = _normalize_api_key(key)
    if norm_err:
        row = {"ok": False, "error": norm_err, "founder_line": "Invalid key paste"}
        print(json.dumps(row, indent=2) if args.json else row["founder_line"])
        return 1

    row = save_key(api_key=key, voice_id=args.voice_id, model_id=args.model_id)
    print(json.dumps(row, indent=2) if args.json else row.get("founder_line", "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
