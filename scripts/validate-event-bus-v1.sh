#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import urllib.request

from runtime.event_bus.bus_v1 import event_bus_payload, publish, tail

pub = publish(topic="validate.event_bus", payload={"probe": True}, source="validator")
assert pub.get("ok"), pub
recent = tail(topic="validate.event_bus", n=3)
assert recent, "no events after publish"

payload = event_bus_payload()
assert payload.get("schema") == "event-bus-v1", payload
assert payload.get("ok"), payload

with urllib.request.urlopen("http://127.0.0.1:13020/api/event-bus-v1", timeout=60) as resp:
    api = json.loads(resp.read().decode())
assert api.get("ok"), api
print("OK: validate-event-bus-v1")
PY
