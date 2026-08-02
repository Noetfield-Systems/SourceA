#!/usr/bin/env bash
# sourcea_founder_gates_e2e_v1.sh — light cloud E2E for Founder Gates (≤90s)
# Law: Mac founder session — one light check; body runs on Cloudflare.
set -euo pipefail
BASE="${SOURCEA_GATES_URL:-https://sourcea-founder-gates-v1.sina-kazemnezhad-ca.workers.dev}"
BASE="${BASE%/}"
UA="SourceA-FounderGates-E2E/1.0"
SECRET="${GATES_SIGNING_SECRET:-}"
if [[ -z "$SECRET" && -f "$HOME/.sina/secrets.env" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$HOME/.sina/secrets.env"; set +a
  SECRET="${GATES_SIGNING_SECRET:-}"
fi
if [[ -z "$SECRET" ]]; then
  echo "FAIL missing GATES_SIGNING_SECRET" >&2
  exit 2
fi

echo "health…"
curl -sS -A "$UA" --max-time 15 "$BASE/health" | tee /tmp/gates_health.json
echo
python3 - <<'PY'
import json
h=json.load(open("/tmp/gates_health.json"))
assert h.get("ok") and h.get("ui")=="v3" and h.get("governor_wired"), h
print("health PASS")
PY

echo "e2e/run…"
curl -sS -A "$UA" --max-time 60 -X POST "$BASE/v1/e2e/run" \
  -H "authorization: Bearer ${SECRET}" \
  -H "content-type: application/json" \
  | tee /tmp/gates_e2e.json
echo
python3 - <<'PY'
import json,sys
r=json.load(open("/tmp/gates_e2e.json"))
print("ok=", r.get("ok"), "receipt=", r.get("receipt_id"), "ms=", r.get("ms"))
for s in r.get("steps") or []:
    print(("PASS" if s.get("ok") else "FAIL"), s.get("step"), s.get("detail") or s.get("error") or "")
sys.exit(0 if r.get("ok") else 1)
PY

echo "PASS founder-gates e2e"
