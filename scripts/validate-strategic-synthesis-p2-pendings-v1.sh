#!/usr/bin/env bash
# sa-0030 / sa-0055 / sa-0080 — P2 L0-full pendings status partial not open
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from strategic_synthesis_hub import pendings, strategic_synthesis_payload

pend = pendings()
p2 = next((x for x in pend if x.get("id") == "P2"), {})
assert p2, "missing P2 in pendings()"
assert p2.get("status") == "partial", p2
assert p2.get("status") != "open", p2
title = (p2.get("title") or "").lower()
assert "l0" in title, f"P2 title missing L0: {p2.get('title')!r}"

payload = strategic_synthesis_payload()
pp2 = next((x for x in (payload.get("pendings") or []) if x.get("id") == "P2"), {})
assert pp2.get("status") == "partial", pp2
assert pp2 == p2, "payload pendings P2 drift"
print(f"OK: validate-strategic-synthesis-p2-pendings-v1 · P2 partial · {p2.get('title')!r}")
PY
