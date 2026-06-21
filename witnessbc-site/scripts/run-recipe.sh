#!/usr/bin/env bash
# Witness AI site — canonical run recipe (assemble · inject · build · validate · sync · receipt)
# Pattern: validate-sourcea-e2e-standard-v1.sh · validate-e2e-recipe-p1-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"
RECEIPT="${SINA}/witnessbc-site-run-receipt-v1.json"
OPEN=0
SERVE=0
JSON=0
PORT="${PORT:-8090}"

usage() {
  echo "Usage: bash witnessbc-site/scripts/run-recipe.sh [--open] [--serve] [--json]"
  echo "  (no flags)  assemble · inject refs · validate · build · sync · write receipt"
  echo "  --open      open index.html in browser after PASS"
  echo "  --serve     start http.server on PORT=${PORT} after PASS"
  echo "  --json      print receipt JSON to stdout"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --open) OPEN=1; shift ;;
    --serve) SERVE=1; shift ;;
    --json) JSON=1; shift ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      exit 1
      ;;
  esac
done

t0=$SECONDS
started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== WITNESSBC-SITE-RUN-RECIPE start ${started_at} ==="
echo ""

echo "=== step 1: preflight ==="
for f in \
  "$ROOT/data/pages.json" \
  "$ROOT/data/references.json" \
  "$ROOT/data/cta.json" \
  "$ROOT/data/cohort.json" \
  "$ROOT/data/proof-scenarios-v1.json" \
  "$ROOT/data/learn-chapters-v1.json" \
  "$ROOT/data/toolkits-v1.json" \
  "$ROOT/partials/head.html" \
  "$ROOT/partials/header.html" \
  "$ROOT/partials/breadcrumb.html" \
  "$ROOT/partials/footer.html" \
  "$ROOT/partials/refs-list.html" \
  "$ROOT/content/index.html" \
  "$ROOT/scripts/assemble_pages.py" \
  "$ROOT/scripts/build.py" \
  "$ROOT/scripts/inject_refs.py" \
  "$ROOT/scripts/inject_trust_signals_v1.py" \
  "$ROOT/scripts/render_toolkits_v1.py" \
  "$ROOT/scripts/render_observe_v1.py" \
  "$ROOT/data/observe-feed-v1.json" \
  "$ROOT/scripts/validate.sh"; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; exit 1; }
done
content_count="$(find "$ROOT/content" -name '*.html' | wc -l | tr -d ' ')"
if [[ "$content_count" -lt 11 ]]; then
  echo "FAIL: content/ has $content_count files (expected 11)"
  exit 1
fi
echo "OK: preflight · ${content_count} content files · references SSOT logged"
echo ""

echo "=== step 2: inject trust signals ==="
python3 "$ROOT/scripts/inject_trust_signals_v1.py"
echo ""

echo "=== step 2b: inject stripe links ==="
python3 "$ROOT/scripts/inject_stripe_links_v1.py"
echo ""

echo "=== step 3: assemble + inject + build ==="
python3 "$ROOT/scripts/build.py" --json >/dev/null
echo ""

echo "=== step 4: validate ==="
bash "$ROOT/scripts/validate.sh"
section_count="$(grep -c '<section ' "$ROOT/index.html" || true)"
echo ""

echo "=== step 4: stage deploy artifact ==="
bash "$ROOT/scripts/deploy_witnessbc_v1.sh" --skip-recipe
echo ""

echo "=== step 5: receipt ==="
build_json_file="$(mktemp)"
python3 "$ROOT/scripts/build.py" --json >"$build_json_file"
elapsed=$((SECONDS - t0))
mkdir -p "$SINA"
BUILD_JSON_FILE="$build_json_file" \
ROOT="$ROOT" \
RECEIPT="$RECEIPT" \
STARTED_AT="$started_at" \
ELAPSED="$elapsed" \
SECTION_COUNT="$section_count" \
JSON_OUT="$JSON" \
python3 - <<'PY'
import json
import os
from pathlib import Path

build_path = Path(os.environ["BUILD_JSON_FILE"])
build = json.loads(build_path.read_text(encoding="utf-8"))
root = Path(os.environ["ROOT"])
ref_count = len(json.loads((root / "data/references.json").read_text(encoding="utf-8"))["refs"])
page_count = len(json.loads((root / "data/pages.json").read_text(encoding="utf-8"))["pages"])
receipt = {
    "schema": "witnessbc-site-run-recipe-v1",
    "ok": True,
    "at": os.environ["STARTED_AT"],
    "elapsed_sec": int(os.environ["ELAPSED"]),
    "recipe": [
        "preflight",
        "inject_trust_signals_v1",
        "assemble_pages",
        "inject_refs",
        "validate.sh (build + brand gate)",
        "deploy_witnessbc_v1.sh --skip-recipe",
        "receipt",
    ],
    "verify": "bash witnessbc-site/scripts/run-recipe.sh",
    "page_count": page_count,
    "section_count": int(os.environ["SECTION_COUNT"]),
    "ref_count": ref_count,
    "paths": build.get("paths", {}),
    "bundle": str(root / "dist/witnessbc-site-v1.html"),
}
Path(os.environ["RECEIPT"]).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
if os.environ.get("JSON_OUT") == "1":
    print(json.dumps(receipt, indent=2))
PY
rm -f "$build_json_file"

echo "OK: receipt → ${RECEIPT}"
echo ""
echo "PASS: witnessbc-site run recipe (${elapsed}s)"
echo "  pages    10 assembled HTML files"
echo "  source   ${ROOT}/index.html"
echo "  bundle   ${ROOT}/dist/witnessbc-site-v1.html"
echo "  deploy   ${ROOT}/dist/deploy/"
echo "  e2e      bash ${ROOT}/scripts/wbc-e2e.sh"
echo "  e2e      cd ${ROOT}/dist/deploy && bash e2e.sh"
echo "  send     ${SINA}/witnessbc-site-v1.html"
echo ""

if [[ "$OPEN" -eq 1 ]]; then
  open "$ROOT/index.html"
fi

if [[ "$SERVE" -eq 1 ]]; then
  echo "Serving http://127.0.0.1:${PORT}/ (Ctrl+C to stop)"
  python3 -m http.server "$PORT"
fi
