#!/usr/bin/env python3
"""Build .icns icons for Sina Command + mini-apps from master artwork."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install Pillow: pip3 install Pillow", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "brand" / "icons" / "source"
OUT = ROOT / "brand" / "icons" / "icns"
ICONSET = ROOT / "brand" / "icons" / "iconset"

# id, source file (or command base), accent hex, badge letter (optional)
ICON_SPECS = [
    ("sina-command", "sina-command.png", None, None),
    ("sina-promptos", "sina-promptos.png", None, None),
    ("sina-dispatch", "sina-command.png", "#5b9cf5", "D"),
    ("sina-execute", "sina-command.png", "#d4a853", "E"),
    ("sina-decide", "sina-command.png", "#a78bfa", "?"),
    ("sina-run", "sina-command.png", "#34d399", "▶"),
    ("sina-status", "sina-command.png", "#38bdf8", "S"),
    ("sina-apple-health", "sina-command.png", "#ff6b8a", "♥"),
    ("sina-mac-health", "sina-command.png", "#34d399", "🛡"),
    ("sina-chat-unify", "sina-command.png", "#a78bfa", "⇄"),
    ("sina-n8n-integration", "sina-command.png", "#ff6d3f", "⎇"),
    ("sina-portfolio-mail", "sina-command.png", "#6366f1", "✉"),
    ("sina-worker-hub", "sina-command.png", "#4f6ef7", "⚡"),
    ("sina-cloud-workers", "sina-command.png", "#38bdf8", "☁"),
]


def load_rgba(path: Path, size: int = 1024) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


def badge_variant(base: Image.Image, accent: str, letter: str) -> Image.Image:
    img = base.copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size
    r = int(w * 0.19)
    cx, cy = int(w * 0.78), int(h * 0.78)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=accent, outline="#0f1419", width=max(4, w // 128))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNSRounded.ttf", int(r * 1.05))
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2 - 2), letter, fill="#0f1419", font=font)
    return img


def write_iconset(png: Path, icon_id: str) -> Path:
    iconset = ICONSET / f"{icon_id}.iconset"
    iconset.mkdir(parents=True, exist_ok=True)
    img = Image.open(png).convert("RGBA")
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        if size <= 32:
            for name, dim in ((f"icon_{size}x{size}.png", size), (f"icon_{size}x{size}@2x.png", size * 2)):
                if dim > 1024:
                    continue
                resized2 = img.resize((dim, dim), Image.Resampling.LANCZOS)
                resized2.save(iconset / name)
        else:
            resized.save(iconset / f"icon_{size}x{size}.png")
            if size < 1024:
                resized2 = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
                resized2.save(iconset / f"icon_{size}x{size}@2x.png")
    # Ensure required mac iconset names
    mapping = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }
    for fname, dim in mapping.items():
        img.resize((dim, dim), Image.Resampling.LANCZOS).save(iconset / fname)
    return iconset


def png_to_icns(icon_id: str, png_path: Path) -> Path:
    iconset = write_iconset(png_path, icon_id)
    OUT.mkdir(parents=True, exist_ok=True)
    icns_path = OUT / f"{icon_id}.icns"
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)], check=True)
    return icns_path


def main() -> None:
    built = []
    for icon_id, src_name, accent, letter in ICON_SPECS:
        src = SRC / src_name
        if not src.is_file():
            print(f"skip {icon_id}: missing {src}")
            continue
        img = load_rgba(src)
        if accent and letter:
            img = badge_variant(img, accent, letter)
        png_out = OUT / f"{icon_id}.png"
        OUT.mkdir(parents=True, exist_ok=True)
        img.save(png_out)
        icns = png_to_icns(icon_id, png_out)
        built.append({"id": icon_id, "png": str(png_out), "icns": str(icns)})
    (OUT / "manifest.json").write_text(json.dumps(built, indent=2), encoding="utf-8")
    print(f"Built {len(built)} icons → {OUT}")


if __name__ == "__main__":
    main()
