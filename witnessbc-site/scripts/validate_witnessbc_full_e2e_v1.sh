#!/usr/bin/env bash
# Full WitnessBC commercial site E2E — pages · toolkits subpages · assets · internal links
set -euo pipefail
BASE="${1:-https://witnessbc-commercial.pages.dev}"
TMP="/tmp/wbc-full-e2e-$$.html"
fail=0
checked=0
passed=0

COMMERCIAL_PAGES=(
  "/index.html"
  "/platform.html"
  "/lifecycle.html"
  "/proof.html"
  "/compare.html"
  "/policy.html"
  "/pricing.html"
  "/contact.html"
  "/faq.html"
  "/sources.html"
  "/learn.html"
  "/toolkits.html"
)

TOOLKIT_PAGES=(
  "/toolkits/free/sourcing/"
  "/toolkits/free/corrections/"
  "/toolkits/free/privacy/"
  "/toolkits/free/public-record/"
  "/toolkits/free/story-template/"
  "/toolkits/free/action-map/"
  "/toolkits/training/"
  "/toolkits/training/evidence-literacy-101/"
  "/toolkits/training/privacy-first-publishing/"
)

ASSETS=(
  "/assets/styles.css"
  "/assets/tokens-v12.css"
  "/assets/layout-ultra-v12.css"
  "/assets/surface-v12.css"
  "/assets/toolkits.css"
  "/assets/site.js"
  "/assets/toolkits.js"
  "/assets/proof-demo.js"
  "/assets/learn-hub.js"
  "/assets/favicon.svg"
  "/data/stripe-links-v1.json"
  "/data/proof-scenarios-v1.json"
  "/data/learn-chapters-v1.json"
  "/data/toolkits-v1.json"
)

check_page() {
  local path="$1"
  local label="${2:-$path}"
  local url="${BASE%/}${path}"
  checked=$((checked + 1))
  local code
  code="$(curl -sS -o "$TMP" -w '%{http_code}' -L "$url" 2>/dev/null || echo "000")"
  if [[ "$code" != "200" ]]; then
    echo "FAIL [$label] HTTP $code — $url"
    fail=1
    return
  fi
  if ! grep -q 'layout-ultra-v12' "$TMP"; then
    echo "FAIL [$label] missing layout-ultra-v12 — $url"
    fail=1
    return
  fi
  if ! grep -q 'assets/styles.css' "$TMP"; then
    echo "FAIL [$label] missing styles.css — $url"
    fail=1
    return
  fi
  if ! grep -q 'brand-disambiguation' "$TMP"; then
    echo "FAIL [$label] missing brand-disambiguation — $url"
    fail=1
    return
  fi
  if grep -qi 'noetfield' "$TMP" && ! grep -q 'brand-other' "$TMP"; then
    echo "FAIL [$label] noetfield leak — $url"
    fail=1
    return
  fi
  passed=$((passed + 1))
  echo "OK  [$label]"
}

check_asset() {
  local path="$1"
  local url="${BASE%/}${path}"
  checked=$((checked + 1))
  local code
  code="$(curl -sS -o /dev/null -w '%{http_code}' -L "$url" 2>/dev/null || echo "000")"
  if [[ "$code" != "200" ]]; then
    echo "FAIL [asset] HTTP $code — $path"
    fail=1
    return
  fi
  passed=$((passed + 1))
  echo "OK  [asset] $path"
}

echo "=== WITNESSBC FULL E2E — $BASE ==="
echo ""

echo "--- commercial pages (12) ---"
for p in "${COMMERCIAL_PAGES[@]}"; do
  check_page "$p"
done
echo ""

echo "--- toolkit subpages (9) ---"
for p in "${TOOLKIT_PAGES[@]}"; do
  check_page "$p" "toolkit$p"
done
echo ""

echo "--- key assets + data (14) ---"
for a in "${ASSETS[@]}"; do
  check_asset "$a"
done
echo ""

echo "--- content markers ---"
checked=$((checked + 1))
curl -sS -L "${BASE%/}/index.html" -o "$TMP"
if grep -q 'proof@witnessbc.com' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] proof@witnessbc.com on home"
else
  echo "FAIL [marker] proof@witnessbc.com missing on home"
  fail=1
fi

checked=$((checked + 1))
curl -sS -L "${BASE%/}/proof.html" -o "$TMP"
if grep -q 'Proof Lab' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] Proof Lab on proof.html"
else
  echo "FAIL [marker] Proof Lab missing on proof.html"
  fail=1
fi

checked=$((checked + 1))
curl -sS -L "${BASE%/}/toolkits.html" -o "$TMP"
if grep -q 'data-freemium-active="true"' "$TMP" && grep -q '/toolkits/sandbox/' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] freemium quickstart + sandbox links on toolkits hub"
else
  echo "FAIL [marker] toolkits hub missing freemium/sandbox activation"
  fail=1
fi

checked=$((checked + 1))
curl -sS -L "${BASE%/}/toolkits.html" -o "$TMP"
if grep -q 'data-buy="pro"' "$TMP" && grep -q 'Education only' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] freemium + Stripe on toolkits hub"
else
  echo "FAIL [marker] toolkits hub missing freemium/Stripe markers"
  fail=1
fi

checked=$((checked + 1))
curl -sS -L "${BASE%/}/contact.html" -o "$TMP"
if grep -q 'contact@witnessbc.com' "$TMP" && grep -q 'Book 15-min proof' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] contact route has intake + proof CTA"
else
  echo "FAIL [marker] contact route missing intake/proof CTA"
  fail=1
fi

checked=$((checked + 1))
curl -sS -L "${BASE%/}/toolkits/free/sourcing/" -o "$TMP"
if grep -q 'toolkit-textarea' "$TMP" && grep -q 'href="/assets/styles.css"' "$TMP"; then
  passed=$((passed + 1))
  echo "OK  [marker] free template + root CSS on sourcing"
else
  echo "FAIL [marker] sourcing subpage broken layout/CSS"
  fail=1
fi
echo ""

echo "--- internal links from toolkits hub ---"
curl -sS -L "${BASE%/}/toolkits.html" -o "$TMP"
link_fail=0
while IFS= read -r href; do
  [[ -z "$href" ]] && continue
  [[ "$href" == http* ]] && continue
  [[ "$href" == mailto:* ]] && continue
  [[ "$href" == \#* ]] && continue
  local_path="$href"
  [[ "$local_path" != /* ]] && local_path="/${local_path}"
  link_url="${BASE%/}${local_path}"
  link_code="$(curl -sS -o /dev/null -w '%{http_code}' -L "$link_url" 2>/dev/null || echo "000")"
  checked=$((checked + 1))
  if [[ "$link_code" == "200" ]]; then
    passed=$((passed + 1))
    echo "OK  [link] $href"
  else
    echo "FAIL [link] HTTP $link_code — $href"
    link_fail=1
    fail=1
  fi
done < <(grep -oE 'href="(/toolkits/[^"#]+|toolkits/[^"#]+)"' "$TMP" | sed 's/href="//;s/"$//' | sort -u)

if [[ "$link_fail" -eq 0 ]]; then
  echo "OK  [link] all toolkits hub internal links"
fi
echo ""

rm -f "$TMP"

if [[ "$fail" -ne 0 ]]; then
  echo "FAIL: full E2E — $passed/$checked passed"
  exit 1
fi

echo "PASS: full E2E — $passed/$checked checks on $BASE"
echo "  12 commercial · 9 toolkit subpages · 14 assets · 6 markers · hub links"
