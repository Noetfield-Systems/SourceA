#!/usr/bin/env bash
# validate-icp-one-product-line-gate-v1.sh — U029 one product paragraph max
set -euo pipefail
cd "$(dirname "$0")/.."

python3 - <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts")))
from icp_one_product_line_gate_v1 import check_one_product_line

for name in ("fundmore-approved-v1.txt", "ocree-approved-v1.txt", "sourcea-factory-approved-v1.txt"):
    body = (Path("data/icp-compile") / name).read_text(encoding="utf-8")
    row = check_one_product_line(body)
    if not row.get("ok"):
        raise SystemExit(f"FAIL {name}: {row.get('issues')}")
    print(f"OK: {name} · product_paragraphs={row.get('product_paragraph_count')}")

print("PASS: validate-icp-one-product-line-gate-v1")
PY
