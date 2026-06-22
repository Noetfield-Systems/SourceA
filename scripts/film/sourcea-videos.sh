#!/usr/bin/env bash
# SourceA video stack ONLY — commercial + W1 ingest + landing deploy
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
SINA="${HOME}/.sina"

echo "=== SOURCEA videos $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Lane: SourceA only — NOT WitnessBC"

cd "$ROOT"

# 1 — W1 hero ingest (Screen Studio master on Desktop)
if [[ -f "$HOME/Desktop/SourceA-W1-Master.mp4" || -f "$HOME/Desktop/SourceA-W1-Master.mov" ]]; then
  echo ""
  echo "Step 1 — W1 hero ingest..."
  python3 "$ROOT/scripts/w1_film_ingest_master_v1.py" --no-deploy
else
  echo ""
  echo "Step 1 — SKIP W1 (no ~/Desktop/SourceA-W1-Master.{mp4,mov})"
fi

# 2 — Commercial short
if [[ "${1:-}" != "--w1-only" ]]; then
  echo ""
  if [[ -f "$HOME/Desktop/SourceA-Commercial-Master.mp4" || -f "$HOME/Desktop/SourceA-Commercial-Master.mov" ]]; then
    echo "Step 2 — Commercial Screen Studio ingest..."
    python3 "$ROOT/scripts/sourcea_commercial_film_ingest_master_v1.py" --no-deploy
  elif [[ "${1:-}" == "--commercial-only" || "${1:-}" == "--force" ]]; then
    echo "Step 2 — Commercial film (Linear-quality Playwright capture)..."
    bash "$ROOT/sourcea-commercial-film.sh"
  elif [[ "${1:-}" == "--skip-commercial" ]]; then
    echo "SKIP commercial (--skip-commercial)"
  else
    RECEIPT="$SINA/enforcement/commercial-short-film-receipt-v1.json"
    if [[ -f "$RECEIPT" ]]; then
      PRODUCT=$(python3 -c "import json; print(json.load(open('$RECEIPT')).get('product',''))" 2>/dev/null || echo "")
      if [[ "$PRODUCT" == "sourcea" ]]; then
        echo "OK: commercial receipt exists (product=sourcea) — use --force to rebuild"
      else
        bash "$ROOT/sourcea-commercial-film.sh"
      fi
    else
      bash "$ROOT/sourcea-commercial-film.sh"
    fi
  fi
fi

# 3 — Deploy landing (embeds commercial + W1 on site)
echo ""
echo "Step 3 — Deploy SourceA landing..."
bash "$ROOT/SourceA-landing/green-unified/scripts/run-recipe.sh" 2>&1 | tail -8

echo ""
echo "=== SOURCEA videos done ==="
echo "Desktop:  ~/Desktop/SourceA-Commercial-Short.mp4"
echo "Desktop:  ~/Desktop/SourceA-W1-Master.mp4"
echo "Site:     http://127.0.0.1:5180/sourcea/"
echo "Proof:    http://127.0.0.1:5180/sourcea/proof.html#sourcea-commercial-film"
echo "Receipts: $SINA/enforcement/commercial-short-film-receipt-v1.json"
echo "          $SINA/enforcement/w1-film-receipt-v1.json"
echo "Quality bar: $ROOT/data/video-quality-bar-v1.json"
echo "Screen Studio: save as ~/Desktop/SourceA-Commercial-Master.mov for Linear-grade ingest"
