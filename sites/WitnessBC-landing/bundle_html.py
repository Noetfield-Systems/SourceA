#!/usr/bin/env python3
"""Bundle Witness BC landings — standalone brand, no SourceA mixing."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WBC_DIR = ROOT / "WitnessBC-landing"
C12 = ROOT / "C12"
SINA = Path.home() / ".sina"
ARCHIVE = ROOT / "archive" / "attachments" / "commercial"

OUT_ZENITY = SINA / "witnessbc-sourcea-layout-light-platform-v1.html"
OUT_NOMOTIC = SINA / "witnessbc-sourcea-layout-dark-platform-v1.html"
ARCH_ZENITY = ARCHIVE / "witnessbc-sourcea-layout-light-platform-v1.html"
ARCH_NOMOTIC = ARCHIVE / "witnessbc-sourcea-layout-dark-platform-v1.html"


def bundle_sourcea-layout-light() -> str:
    html = (WBC_DIR / "witnessbc-sourcea-layout-light.html").read_text(encoding="utf-8")
    base = (C12 / "styles.css").read_text(encoding="utf-8")
    theme = (WBC_DIR / "witnessbc-theme.css").read_text(encoding="utf-8")
    html = re.sub(r'\s*<link rel="stylesheet" href="\.\./C12/styles\.css" />\s*', "", html)
    html = re.sub(r'\s*<link rel="stylesheet" href="witnessbc-theme\.css" />\s*', "", html)
    return html.replace("</head>", f"<style>{base}\n{theme}</style>\n</head>", 1)


def bundle_sourcea-layout-dark() -> str:
    return (WBC_DIR / "witnessbc-sourcea-layout-dark.html").read_text(encoding="utf-8")


def write_all() -> dict[str, str]:
    SINA.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    z = bundle_sourcea-layout-light()
    n = bundle_sourcea-layout-dark()
    OUT_ZENITY.write_text(z, encoding="utf-8")
    OUT_NOMOTIC.write_text(n, encoding="utf-8")
    ARCH_ZENITY.write_text(z, encoding="utf-8")
    ARCH_NOMOTIC.write_text(n, encoding="utf-8")
    return {
        "witnessbc_sourcea-layout-light": str(OUT_ZENITY),
        "witnessbc_sourcea-layout-dark": str(OUT_NOMOTIC),
        "witnessbc_sourcea-layout-light_archive": str(ARCH_ZENITY),
        "witnessbc_sourcea-layout-dark_archive": str(ARCH_NOMOTIC),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("target", nargs="?", choices=["all", "sourcea-layout-light", "sourcea-layout-dark"], default="all")
    p.add_argument("--open", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    paths = write_all()
    if args.target == "sourcea-layout-light":
        sel = {k: paths[k] for k in ("witnessbc_sourcea-layout-light", "witnessbc_sourcea-layout-light_archive")}
    elif args.target == "sourcea-layout-dark":
        sel = {k: paths[k] for k in ("witnessbc_sourcea-layout-dark", "witnessbc_sourcea-layout-dark_archive")}
    else:
        sel = paths
    if args.json:
        import json
        print(json.dumps({"ok": True, "paths": sel}, indent=2))
    else:
        for v in sel.values():
            print(v)
    if args.open:
        open_file = str(WBC_DIR / f"witnessbc-{args.target}.html") if args.target != "all" else str(WBC_DIR / "witnessbc-sourcea-layout-light.html")
        subprocess.run(["open", open_file], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
