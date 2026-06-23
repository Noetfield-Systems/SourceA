#!/usr/bin/env python3
"""Video ad factory orchestration — brief → script → AUDIO_READY → render bridge.

Maps Gemini orchestration to SourceA disk:
  - Zod-equivalent validation via inline schema
  - ElevenLabs via scripts/film_elevenlabs_wire_v1.py (live wire)
  - After AUDIO_READY invokes scripts/video_ad_rendering_bridge_v1.py (no approval gate)
  - Supabase optional — local JSON campaign file for P1 stdio

Law: data/multi-factory-enterprise-tree-advisory-v1.json · shared/types/campaign-v1.ts
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
CAMPAIGNS_DIR = DATA / "video-ad-campaigns-v1"
RECEIPT_PATH = SINA / "video-ad-orchestration-receipt-v1.json"
ELEVENLABS_WIRE = ROOT / "scripts" / "film_elevenlabs_wire_v1.py"
FACTORY_ID = "video-ad-factory-v1"

VALID_STEPS = frozenset(
    {
        "BRIEF_ANALYSIS",
        "AUDIO_READY",
        "VIDEO_RENDERING",
        "HUMAN_APPROVAL_REQUIRED",
        "DISPATCHED",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_scenario(raw: dict) -> dict:
    script = str(raw.get("refined_script") or "").strip()
    if len(script) < 10:
        raise ValueError("refined_script too short (min 10 chars)")
    prompts = raw.get("visual_prompts") or []
    if not isinstance(prompts, list) or len(prompts) < 1:
        raise ValueError("visual_prompts must be non-empty array")
    vs = raw.get("voice_settings") or {}
    for key in ("stability", "similarity_boost"):
        v = vs.get(key)
        if v is None or not (0 <= float(v) <= 1):
            raise ValueError(f"voice_settings.{key} must be 0..1")
    return {
        "refined_script": script,
        "visual_prompts": [str(p) for p in prompts],
        "voice_settings": {
            "stability": float(vs["stability"]),
            "similarity_boost": float(vs["similarity_boost"]),
        },
    }


def _load_campaign(campaign_id: str) -> dict:
    path = CAMPAIGNS_DIR / f"{campaign_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"campaign not found: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _save_campaign(campaign: dict) -> None:
    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    cid = campaign["id"]
    path = CAMPAIGNS_DIR / f"{cid}.json"
    campaign["updated_at"] = _now()
    path.write_text(json.dumps(campaign, indent=2) + "\n", encoding="utf-8")


def generate_scenario_from_brief(raw_brief: str, *, mock: bool = True) -> dict:
    """LLM hook placeholder — OEGCC/controller integration in WORK order."""
    if mock:
        return {
            "refined_script": (
                "The future of technology is in your hands. "
                "Automate your business with our new stack."
            )[: max(10, min(500, len(raw_brief) + 20))],
            "visual_prompts": [
                "Futuristic cybernetic factory ultra realistic 4k cinematic lighting neon accents"
            ],
            "voice_settings": {"stability": 0.75, "similarity_boost": 0.85},
        }
    raise NotImplementedError("LLM orchestration — wire OEGCC OpenRouter in WORK order")


def synthesize_audio_via_wire(script: str, *, vo_lane: str = "sourcea") -> dict:
    """Invoke live ElevenLabs wire if key present; else MOCK_ONLY receipt."""
    if not ELEVENLABS_WIRE.is_file():
        return {"ok": False, "verdict": "MOCK_ONLY", "reason": "elevenlabs wire missing"}
    env_file = SINA / "elevenlabs-v1.env"
    if not env_file.is_file():
        return {
            "ok": True,
            "verdict": "MOCK_ONLY",
            "reason": "no ~/.sina/elevenlabs-v1.env — audio skipped",
            "script_chars": len(script),
        }
    proc = subprocess.run(
        [sys.executable, str(ELEVENLABS_WIRE), "--lane", vo_lane, "--test", script[:500]],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "verdict": "FAIL",
            "stderr": (proc.stderr or "")[-400:],
        }
    return {"ok": True, "verdict": "PASS", "wire_stdout": (proc.stdout or "")[-200:]}


def preview_orchestration(raw_brief: str, *, cfg: dict[str, Any]) -> dict[str, Any]:
    """Dry-run orchestration for golden eval — no campaign disk write."""
    if not str(raw_brief or "").strip():
        return {"ok": False, "verdict": "BLOCKED", "error": "empty_brief"}
    try:
        generated = generate_scenario_from_brief(raw_brief, mock=bool(cfg.get("mock_llm", True)))
        validated = _validate_scenario(generated)
    except ValueError as exc:
        return {"ok": False, "verdict": "BLOCKED", "error": str(exc)}
    script = validated["refined_script"]
    if len(script) > int(cfg.get("max_script_chars") or 500):
        return {"ok": False, "verdict": "BLOCKED", "error": "script_too_long"}
    step = "VIDEO_RENDERING"
    return {
        "ok": True,
        "verdict": "ALLOW",
        "current_step": step,
        "config_version": cfg.get("config_version"),
        "variation_key": cfg.get("variation_key"),
        "mock_llm": bool(cfg.get("mock_llm", True)),
    }


def orchestrate_campaign(
    campaign_id: str,
    *,
    require_approval: bool = False,
    mock_llm: bool = True,
    vo_lane: str = "sourcea",
    variation_key: str | None = None,
    write_receipt: bool = True,
) -> dict:
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from agent_runtime_config_v1 import load_factory_runtime_config  # noqa: WPS433

    cfg = load_factory_runtime_config(FACTORY_ID, variation_key=variation_key)
    mock_llm = bool(cfg.get("mock_llm", mock_llm))
    vo_lane = str(cfg.get("vo_lane") or vo_lane)

    campaign = _load_campaign(campaign_id)
    raw_brief = str(campaign.get("raw_brief") or "").strip()
    if not raw_brief:
        raise ValueError("raw_brief empty")

    generated = generate_scenario_from_brief(raw_brief, mock=mock_llm)
    validated = _validate_scenario(generated)

    campaign["refined_script"] = validated["refined_script"]
    campaign["video_prompt_loop"] = {
        "positive_prompt": validated["visual_prompts"][0],
        "aspect_ratio": "9:16",
        "variants": [{"label": "primary", "prompt": validated["visual_prompts"][0]}],
    }
    campaign["current_step"] = "AUDIO_READY"

    audio = synthesize_audio_via_wire(validated["refined_script"], vo_lane=vo_lane)
    campaign["current_step"] = "VIDEO_RENDERING"
    _save_campaign(campaign)

    from video_ad_rendering_bridge_v1 import run_bridge  # noqa: WPS433

    render_receipt = run_bridge(
        campaign_id,
        mock_only=not bool(cfg.get("allow_fal_render", False)),
    )

    receipt = {
        "schema": "video-ad-orchestration-receipt-v1",
        "ok": True,
        "at": _now(),
        "campaign_id": campaign_id,
        "factory_id": FACTORY_ID,
        "config_version": cfg.get("config_version"),
        "variation_key": cfg.get("variation_key"),
        "current_step": render_receipt.get("current_step"),
        "audio": audio,
        "render": render_receipt.get("render"),
        "honest_label": render_receipt.get("render", {}).get("verdict") or audio.get("verdict", "MOCK_ONLY"),
        "next": "scripts/video_ad_rendering_bridge_v1.py",
    }
    if write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def seed_demo_campaign() -> dict:
    CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    demo = {
        "schema": "campaign-automation-v1",
        "id": "demo-campaign-v1",
        "creator_id": "00000000-0000-0000-0000-000000000001",
        "raw_brief": "15s ad for SourceA Forge — proof layer for AI agents.",
        "current_step": "BRIEF_ANALYSIS",
        "created_at": _now(),
        "updated_at": _now(),
    }
    _save_campaign(demo)
    return demo


def main() -> int:
    ap = argparse.ArgumentParser(description="Video ad factory orchestration v1")
    ap.add_argument("--campaign-id", default="demo-campaign-v1")
    ap.add_argument("--seed-demo", action="store_true")
    ap.add_argument("--no-approval-gate", action="store_true")
    ap.add_argument("--variation-key", default="")
    ap.add_argument("--no-write", action="store_true", help="Skip ~/.sina receipt (validators/mac-light)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.seed_demo:
        seed_demo_campaign()

    try:
        row = orchestrate_campaign(
            args.campaign_id,
            variation_key=args.variation_key or None,
            write_receipt=not args.no_write,
        )
    except Exception as exc:
        row = {"ok": False, "error": str(exc), "at": _now()}
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(f"FAIL: {exc}")
        return 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: {args.campaign_id} → {row.get('current_step')} · {row.get('honest_label')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
