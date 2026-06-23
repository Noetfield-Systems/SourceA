#!/usr/bin/env python3
"""Rendering bridge — Fal.ai vendor-swappable interface (thin P1 stub).

Law: docs/SCALE_EVOLUTION_LOCKED_v1.md — swap provider without touching orchestration.
Only runs after HUMAN_APPROVAL_REQUIRED cleared or current_step=VIDEO_RENDERING.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
CAMPAIGNS_DIR = DATA / "video-ad-campaigns-v1"
RECEIPT_PATH = SINA / "video-ad-rendering-bridge-receipt-v1.json"

FAL_DEFAULT_ENDPOINT = "https://fal.run/fal-ai/flux/dev"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_campaign(campaign_id: str) -> dict:
    path = CAMPAIGNS_DIR / f"{campaign_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"campaign not found: {campaign_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def render_video_stub(
    *,
    campaign_id: str,
    prompt: str,
    aspect_ratio: str = "9:16",
    mock_only: bool = True,
) -> dict:
    """Fal.ai call or MOCK_ONLY when FAL_KEY absent."""
    fal_key = os.environ.get("FAL_KEY", "").strip()
    if mock_only or not fal_key:
        return {
            "ok": True,
            "verdict": "MOCK_ONLY",
            "provider": "FAL_AI",
            "campaign_id": campaign_id,
            "prompt_preview": prompt[:120],
            "aspect_ratio": aspect_ratio,
            "output_url": None,
            "honest_label": "FAL_KEY not set — no cloud render spend",
        }

    body = json.dumps({"prompt": prompt, "image_size": "portrait_16_9"}).encode()
    req = urllib.request.Request(
        FAL_DEFAULT_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Key {fal_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
        return {
            "ok": True,
            "verdict": "PASS",
            "provider": "FAL_AI",
            "campaign_id": campaign_id,
            "output_url": payload.get("images", [{}])[0].get("url") if isinstance(payload.get("images"), list) else None,
            "raw_keys": list(payload.keys()),
        }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "verdict": "FAIL",
            "provider": "FAL_AI",
            "status": exc.code,
            "body": exc.read().decode()[:300],
        }


def run_bridge(campaign_id: str, *, mock_only: bool = False) -> dict:
    campaign = _load_campaign(campaign_id)
    step = campaign.get("current_step")
    allowed = frozenset({"VIDEO_RENDERING", "HUMAN_APPROVAL_REQUIRED", "DISPATCHED"})
    if step not in allowed:
        raise ValueError(f"current_step={step!r} — orchestration must reach VIDEO_RENDERING first")

    loop = campaign.get("video_prompt_loop") or {}
    prompt = str(loop.get("positive_prompt") or campaign.get("refined_script") or "")
    if len(prompt) < 5:
        raise ValueError("no render prompt on campaign")

    result = render_video_stub(
        campaign_id=campaign_id,
        prompt=prompt,
        aspect_ratio=str(loop.get("aspect_ratio") or "9:16"),
        mock_only=mock_only,
    )

    if result.get("verdict") == "PASS":
        campaign["current_step"] = "DISPATCHED"
        campaign["render_output_url"] = result.get("output_url")
    elif result.get("verdict") == "MOCK_ONLY":
        campaign["current_step"] = "HUMAN_APPROVAL_REQUIRED"

    campaign["updated_at"] = _now()
    (CAMPAIGNS_DIR / f"{campaign_id}.json").write_text(
        json.dumps(campaign, indent=2) + "\n", encoding="utf-8"
    )

    receipt = {
        "schema": "video-ad-rendering-bridge-receipt-v1",
        "ok": result.get("ok", False),
        "at": _now(),
        "campaign_id": campaign_id,
        "current_step": campaign["current_step"],
        "render": result,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Video ad rendering bridge v1")
    ap.add_argument("--campaign-id", default="demo-campaign-v1")
    ap.add_argument("--live", action="store_true", help="Call Fal when FAL_KEY set")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        row = run_bridge(args.campaign_id, mock_only=not args.live)
    except Exception as exc:
        row = {"ok": False, "error": str(exc), "at": _now()}
        if args.json:
            print(json.dumps(row, indent=2))
        return 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: render {row.get('render', {}).get('verdict')} · step={row.get('current_step')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
