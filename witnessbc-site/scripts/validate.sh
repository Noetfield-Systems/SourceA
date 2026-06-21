#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/scripts/build.py" --json >/dev/null

FORBIDDEN='sourcea|[external-design-benchmark]|[external-design-benchmark]|notenic|witness bc'
BRAND_ALLOW='witnessbc\.com|brand-disambiguation|operations@noetfield\.com|class="brand-other"|lane-router|noetfield\.com/copilot'
for f in "$ROOT/index.html" "$ROOT/platform.html" "$ROOT/lifecycle.html" "$ROOT/proof.html" "$ROOT/compare.html" "$ROOT/policy.html" "$ROOT/pricing.html" "$ROOT/faq.html" "$ROOT/sources.html" "$ROOT/assets/styles.css" "$ROOT/assets/motion.css" "$ROOT/assets/tokens.css" "$ROOT/assets/site.js" "$ROOT/assets/proof-demo.js" "$ROOT/assets/control-plane.js" "$ROOT/data/references.json"; do
  if [[ -f "$f" ]] && grep -iE "$FORBIDDEN" "$f" 2>/dev/null | grep -viE "$BRAND_ALLOW"; then
    echo "FAIL: forbidden brand reference in $f"
    exit 1
  fi
done

if grep -iE 'witnessai|witness\.ai' "$ROOT/index.html" | grep -viE 'brand-disambiguation|brand-other|not WitnessAI'; then
  echo "FAIL: competitor brand reference outside disambiguation on index.html"
  exit 1
fi

if [[ ! -f "$ROOT/data/references.json" ]]; then
  echo "FAIL: missing data/references.json"
  exit 1
fi

PAGE_FILES=(index.html platform.html lifecycle.html proof.html compare.html policy.html pricing.html faq.html sources.html learn.html toolkits.html)
for pf in "${PAGE_FILES[@]}"; do
  if [[ ! -f "$ROOT/$pf" ]]; then
    echo "FAIL: missing assembled page $pf"
    exit 1
  fi
  if grep -q '{{' "$ROOT/$pf"; then
    echo "FAIL: unreplaced template placeholder in $pf"
    exit 1
  fi
done

if ! grep -q 'class="trust-pills"' "$ROOT/index.html"; then
  echo "FAIL: missing trust-pills on index.html"
  exit 1
fi

if ! grep -q 'class="hero-institutional"' "$ROOT/index.html"; then
  echo "FAIL: missing hero-institutional on index.html"
  exit 1
fi

if grep -q 'class="hero-category"' "$ROOT/index.html"; then
  echo "FAIL: hero-category duplicate should be removed from index.html"
  exit 1
fi

if ! grep -q 'class="deposit-note"' "$ROOT/pricing.html"; then
  echo "FAIL: missing deposit-note on pricing.html"
  exit 1
fi

if ! grep -q 'id="proofFilmToggle"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof film strip on proof.html"
  exit 1
fi

if [[ ! -f "$ROOT/data/cta.json" ]]; then
  echo "FAIL: missing data/cta.json"
  exit 1
fi

PROOF_MAILTO=$(python3 -c "import json; print(json.load(open('$ROOT/data/cta.json'))['proof_mailto'])")
LIVE_DEMO=$(python3 -c "import json; print(json.load(open('$ROOT/data/cta.json'))['live_demo_url'])")

if ! grep -qF "$PROOF_MAILTO" "$ROOT/index.html"; then
  echo "FAIL: proof mailto not found on index.html"
  exit 1
fi

if ! grep -q 'class="brand-disambiguation"' "$ROOT/index.html"; then
  echo "FAIL: missing brand-disambiguation on index.html"
  exit 1
fi

if ! grep -qF "$LIVE_DEMO" "$ROOT/proof.html"; then
  echo "FAIL: live demo URL not found on proof.html"
  exit 1
fi

if ! grep -qF "$PROOF_MAILTO" "$ROOT/faq.html"; then
  echo "FAIL: proof mailto not found on faq.html"
  exit 1
fi

if ! grep -q 'data-proof-mailto=' "$ROOT/index.html"; then
  echo "FAIL: missing data-proof-mailto on body"
  exit 1
fi

REF_COUNT=$(python3 -c "import json; print(len(json.load(open('$ROOT/data/references.json'))['refs']))")
if [[ "$REF_COUNT" -lt 8 ]]; then
  echo "FAIL: references.json has $REF_COUNT refs (min 8)"
  exit 1
fi

GARTNER_URL=$(python3 -c "import json; print(json.load(open('$ROOT/data/references.json'))['gartner_primary_url'])")
if ! grep -qF "$GARTNER_URL" "$ROOT/index.html"; then
  echo "FAIL: Gartner primary URL from JSON not found in index.html"
  exit 1
fi

SECTION_COUNT=$(grep -c '<section ' "$ROOT/index.html" || true)
if [[ "$SECTION_COUNT" -gt 10 ]]; then
  echo "FAIL: index.html has $SECTION_COUNT sections (max 10)"
  exit 1
fi

for n in $(python3 -c "import json; print(' '.join(str(r['id']) for r in json.load(open('$ROOT/data/references.json'))['refs']))"); do
  if ! grep -q "id=\"ref-$n\"" "$ROOT/sources.html"; then
    echo "FAIL: missing reference ref-$n in sources.html"
    exit 1
  fi
done

CITED=$(grep -ohE 'href="[^"]*#ref-[0-9]+"' "$ROOT"/*.html | grep -oE '[0-9]+' | sort -u)
for c in $CITED; do
  if ! grep -q "id=\"ref-$c\"" "$ROOT/sources.html"; then
    echo "FAIL: orphan citation #ref-$c"
    exit 1
  fi
done

if ! grep -q 'class="crosswalk-table"' "$ROOT/sources.html"; then
  echo "FAIL: missing framework crosswalk table on sources.html"
  exit 1
fi

if ! grep -q 'class="arch-diagram"' "$ROOT/platform.html"; then
  echo "FAIL: missing architecture diagram on platform.html"
  exit 1
fi

if [[ ! -f "$ROOT/assets/proof-demo.js" ]]; then
  echo "FAIL: missing assets/proof-demo.js"
  exit 1
fi

if [[ ! -f "$ROOT/assets/motion.css" ]]; then
  echo "FAIL: missing assets/motion.css"
  exit 1
fi

if ! grep -q 'assets/motion.css' "$ROOT/index.html"; then
  echo "FAIL: index.html does not reference motion.css"
  exit 1
fi

if [[ ! -f "$ROOT/assets/control-plane.js" ]]; then
  echo "FAIL: missing assets/control-plane.js"
  exit 1
fi

if ! grep -q 'control-plane.js' "$ROOT/index.html"; then
  echo "FAIL: index.html does not reference control-plane.js"
  exit 1
fi

if grep -q 'proof-demo.js' "$ROOT/index.html"; then
  echo "FAIL: index.html should not reference proof-demo.js"
  exit 1
fi

if ! grep -q 'proof-demo.js' "$ROOT/proof.html"; then
  echo "FAIL: proof.html does not reference proof-demo.js"
  exit 1
fi

if ! grep -q 'id="themeToggle"' "$ROOT/index.html"; then
  echo "FAIL: missing theme toggle button"
  exit 1
fi

if ! grep -q 'data-theme=' "$ROOT/index.html"; then
  echo "FAIL: missing data-theme attribute on html element"
  exit 1
fi

if ! grep -q 'witness-ai-theme' "$ROOT/index.html" "$ROOT/assets/site.js"; then
  echo "FAIL: missing witness-ai-theme localStorage key"
  exit 1
fi

if ! grep -q 'rel="icon"' "$ROOT/index.html"; then
  echo "FAIL: missing favicon link"
  exit 1
fi

if ! grep -q 'id="proofScenarioPills"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof scenario pills on proof.html"
  exit 1
fi

if ! grep -q 'id="proofScenarioCards"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof scenario cards grid on proof.html"
  exit 1
fi

if ! grep -q 'id="proofEvidencePanel"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof evidence panel on proof.html"
  exit 1
fi

if ! grep -q 'id="proofProgressTracker"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof progress tracker on proof.html"
  exit 1
fi

if ! grep -q 'id="proofScrubber"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof replay scrubber on proof.html"
  exit 1
fi

if ! grep -q 'proof-scenarios-v1.json' "$ROOT/assets/proof-demo.js"; then
  echo "FAIL: proof-demo.js must load proof-scenarios-v1.json SSOT"
  exit 1
fi

if [[ ! -f "$ROOT/data/proof-scenarios-v1.json" ]]; then
  echo "FAIL: missing data/proof-scenarios-v1.json"
  exit 1
fi

SCENARIO_COUNT=$(python3 -c "import json; print(len(json.load(open('$ROOT/data/proof-scenarios-v1.json'))['scenarios']))")
if [[ "$SCENARIO_COUNT" -lt 5 ]]; then
  echo "FAIL: proof-scenarios-v1.json has $SCENARIO_COUNT scenarios (min 5)"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/data/proof-scenarios-v1.json" ]]; then
  echo "FAIL: missing dist/deploy/data/proof-scenarios-v1.json"
  exit 1
fi

if ! grep -q 'stats-scenario-chips' "$ROOT/index.html"; then
  echo "FAIL: missing stats scenario chips on index.html"
  exit 1
fi

if ! grep -q 'data-scenario=' "$ROOT/assets/control-plane.js"; then
  echo "FAIL: control-plane.js must deep-link agent rows to proof scenarios"
  exit 1
fi

if grep -q 'id="proofScenarioPills"' "$ROOT/index.html"; then
  echo "FAIL: proof scenario pills should not be on index.html"
  exit 1
fi

if ! grep -q 'class="explore-hub"' "$ROOT/index.html"; then
  echo "FAIL: missing explore hub section on index.html"
  exit 1
fi

if ! grep -q 'class="page-hero"' "$ROOT/platform.html"; then
  echo "FAIL: missing page-hero on platform.html"
  exit 1
fi

if [[ ! -f "$ROOT/dist/witnessbc-site-v1.html" ]]; then
  echo "FAIL: missing dist/witnessbc-site-v1.html bundle"
  exit 1
fi

if ! grep -q '@media print' "$ROOT/assets/styles.css"; then
  echo "FAIL: missing print CSS in styles.css"
  exit 1
fi

if [[ ! -f "$ROOT/data/cohort.json" ]]; then
  echo "FAIL: missing data/cohort.json"
  exit 1
fi

if ! grep -q 'founding-cohort' "$ROOT/index.html"; then
  echo "FAIL: missing founding-cohort on index.html"
  exit 1
fi

if ! grep -q 'founding-cohort' "$ROOT/pricing.html"; then
  echo "FAIL: missing founding-cohort on pricing.html"
  exit 1
fi

if ! grep -qF "$PROOF_MAILTO" "$ROOT/pricing.html"; then
  echo "FAIL: proof mailto not found on pricing.html Flow tier"
  exit 1
fi

if ! grep -q 'lane-router' "$ROOT/pricing.html"; then
  echo "FAIL: missing lane-router on pricing.html"
  exit 1
fi

if ! grep -q 'lane-router' "$ROOT/faq.html"; then
  echo "FAIL: missing lane-router on faq.html"
  exit 1
fi

if ! grep -q 'id="diligence"' "$ROOT/policy.html"; then
  echo "FAIL: missing diligence section on policy.html"
  exit 1
fi

if ! grep -q 'id="integrations"' "$ROOT/platform.html"; then
  echo "FAIL: missing integrations section on platform.html"
  exit 1
fi

if ! grep -q 'id="w1-demo-film"' "$ROOT/proof.html"; then
  echo "FAIL: missing w1-demo-film on proof.html"
  exit 1
fi

PROOF_TITLE=$(python3 -c "import json; print(json.load(open('$ROOT/data/pages.json'))['pages'][3]['title'])")
PRICING_TITLE=$(python3 -c "import json; print(json.load(open('$ROOT/data/pages.json'))['pages'][6]['title'])")
if ! grep -qF "$PROOF_TITLE" "$ROOT/proof.html"; then
  echo "FAIL: proof.html title mismatch with pages.json"
  exit 1
fi
if ! grep -qF "$PRICING_TITLE" "$ROOT/pricing.html"; then
  echo "FAIL: pricing.html title mismatch with pages.json"
  exit 1
fi
if grep -qF "$PROOF_TITLE" "$ROOT/pricing.html"; then
  echo "FAIL: proof and pricing share same title tag"
  exit 1
fi

if ! grep -q 'id="controlPlaneDensity"' "$ROOT/index.html"; then
  echo "FAIL: missing control plane density toggle on index.html"
  exit 1
fi

if ! grep -q 'data-wbc-trust-bar' "$ROOT/index.html"; then
  echo "FAIL: missing live trust bar on index.html"
  exit 1
fi

if [[ ! -f "$ROOT/data/trust-signals.json" ]]; then
  echo "FAIL: missing data/trust-signals.json"
  exit 1
fi

if [[ ! -f "$ROOT/assets/trust-signals.js" ]]; then
  echo "FAIL: missing assets/trust-signals.js"
  exit 1
fi

if ! grep -q 'trust-signals.js' "$ROOT/index.html"; then
  echo "FAIL: index.html does not reference trust-signals.js"
  exit 1
fi

if ! grep -q 'class="page-breadcrumb"' "$ROOT/platform.html"; then
  echo "FAIL: missing breadcrumb on platform.html"
  exit 1
fi

if ! grep -q 'w1-demo-embed' "$ROOT/proof.html"; then
  echo "FAIL: missing commercial short embed on proof.html"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/_redirects" ]] || [[ ! -f "$ROOT/dist/deploy/data/proof-scenarios-v1.json" ]]; then
  bash "$ROOT/scripts/deploy_witnessbc_v1.sh" --skip-recipe >/dev/null
fi

if [[ ! -f "$ROOT/dist/deploy/_redirects" ]]; then
  echo "FAIL: missing dist/deploy/_redirects"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/_routes.json" ]]; then
  echo "FAIL: missing dist/deploy/_routes.json coexistence routes"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/data/trust-signals.json" ]]; then
  echo "FAIL: missing dist/deploy/data/trust-signals.json"
  exit 1
fi

if [[ ! -f "$ROOT/data/proof-scenarios-v1.json" ]]; then
  echo "FAIL: missing data/proof-scenarios-v1.json"
  exit 1
fi

if ! python3 -c "import json; d=json.load(open('$ROOT/data/proof-scenarios-v1.json')); assert len(d.get('scenarios',[]))>=5" 2>/dev/null; then
  echo "FAIL: proof-scenarios-v1.json needs 5+ scenarios"
  exit 1
fi

if ! grep -q 'id="wbcProofScenarios"' "$ROOT/proof.html"; then
  echo "FAIL: proof.html missing embedded scenarios JSON"
  exit 1
fi

if ! grep -q 'id="proofEvidencePanel"' "$ROOT/proof.html"; then
  echo "FAIL: missing proof evidence panel on proof.html"
  exit 1
fi

if ! grep -q 'id="proofTamperBtn"' "$ROOT/proof.html"; then
  echo "FAIL: missing tamper demo button on proof.html"
  exit 1
fi

if ! grep -q 'id="proofReplayPrev"' "$ROOT/proof.html"; then
  echo "FAIL: missing replay controls on proof.html"
  exit 1
fi

if ! grep -q 'id="heroProofTicker"' "$ROOT/index.html"; then
  echo "FAIL: missing hero proof ticker on index.html"
  exit 1
fi

if ! grep -q 'proof-scenarios-v1.json' "$ROOT/assets/proof-demo.js"; then
  echo "FAIL: proof-demo.js must reference proof-scenarios-v1.json"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/data/proof-scenarios-v1.json" ]]; then
  echo "FAIL: missing dist/deploy/data/proof-scenarios-v1.json"
  exit 1
fi

if ! grep -q 'id="learnHub"' "$ROOT/learn.html"; then
  echo "FAIL: missing learn hub on learn.html"
  exit 1
fi

if ! grep -q 'id="wbcLearnChapters"' "$ROOT/learn.html"; then
  echo "FAIL: learn.html missing embedded chapters JSON"
  exit 1
fi

if [[ ! -f "$ROOT/assets/learn-hub.js" ]]; then
  echo "FAIL: missing assets/learn-hub.js"
  exit 1
fi

if ! grep -q 'learn-hub.js' "$ROOT/learn.html"; then
  echo "FAIL: learn.html does not reference learn-hub.js"
  exit 1
fi

if [[ ! -f "$ROOT/data/learn-chapters-v1.json" ]]; then
  echo "FAIL: missing data/learn-chapters-v1.json"
  exit 1
fi

CHAPTER_COUNT=$(python3 -c "import json; print(len(json.load(open('$ROOT/data/learn-chapters-v1.json'))['chapters']))")
if [[ "$CHAPTER_COUNT" -lt 6 ]]; then
  echo "FAIL: learn-chapters-v1.json has $CHAPTER_COUNT chapters (min 6)"
  exit 1
fi

if ! grep -q 'explore-card-featured' "$ROOT/index.html"; then
  echo "FAIL: missing featured Learn card on index.html"
  exit 1
fi

if ! grep -q 'href="learn.html"' "$ROOT/index.html"; then
  echo "FAIL: index.html missing learn.html link"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/learn.html" ]]; then
  bash "$ROOT/scripts/deploy_witnessbc_v1.sh" --skip-recipe >/dev/null
fi

if [[ ! -f "$ROOT/dist/deploy/data/learn-chapters-v1.json" ]]; then
  echo "FAIL: missing dist/deploy/data/learn-chapters-v1.json"
  exit 1
fi

for slug in proof pricing faq; do
  if [[ ! -f "$ROOT/dist/witnessbc-site-${slug}-v1.html" ]]; then
    echo "FAIL: missing dist/witnessbc-site-${slug}-v1.html send bundle"
    exit 1
  fi
done

if ! grep -q 'observe/index.html' "$ROOT/index.html"; then
  echo "FAIL: missing Observe link on index.html"
  exit 1
fi

if [[ ! -f "$ROOT/observe/index.html" ]]; then
  echo "FAIL: missing observe/index.html"
  exit 1
fi

if ! grep -q 'We observe and narrate' "$ROOT/observe/index.html"; then
  echo "FAIL: Observe hub missing witness tagline"
  exit 1
fi

if ! grep -q 'id="observeFeedGrid"' "$ROOT/observe/index.html"; then
  echo "FAIL: Observe feed grid missing"
  exit 1
fi

if [[ ! -f "$ROOT/dist/deploy/observe/index.html" ]]; then
  bash "$ROOT/scripts/deploy_witnessbc_v1.sh" --skip-recipe >/dev/null
fi

if [[ ! -f "$ROOT/dist/deploy/observe/index.html" ]]; then
  echo "FAIL: missing dist/deploy/observe/index.html"
  exit 1
fi

echo "PASS: witnessbc-site v10 Observe lane — ${#PAGE_FILES[@]} pages + observe, index ${SECTION_COUNT} sections, $REF_COUNT refs, ${SCENARIO_COUNT:-6} scenarios, deploy routes"
