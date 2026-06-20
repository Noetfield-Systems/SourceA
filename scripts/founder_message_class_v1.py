#!/usr/bin/env python3
"""Founder message class — re-exports factory_control_v1."""
from factory_control_v1 import classify_founder_message as classify

if __name__ == "__main__":
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser()
    p.add_argument("text", nargs="?", default="")
    p.add_argument("--stdin", action="store_true")
    a = p.parse_args()
    text = sys.stdin.read() if a.stdin else a.text
    print(json.dumps({"class": classify(text)}))
    raise SystemExit(0)
