#!/usr/bin/env bash
# INCIDENT-038 v1.1 — Mac control vs cloud factory vocabulary logged
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VOCAB="$ROOT/data/mac-worker-vs-factory-vocabulary-v1.json"
LOCK="$ROOT/data/mac-law-agent-execution-plane-lock-v1.json"
GLOSS="$ROOT/data/founder-reply-glossary-v1.json"
INCIDENT="$ROOT/brain-os/incidents/SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md"

fail=0
check_file() { [[ -f "$1" ]] || { echo "FAIL missing $1"; fail=1; }; }

check_file "$VOCAB"
check_file "$LOCK"
check_file "$GLOSS"
check_file "$INCIDENT"

python3 - <<'PY' || fail=1
import json, sys
from pathlib import Path
root = Path(".")
v = json.loads((root / "data/mac-worker-vs-factory-vocabulary-v1.json").read_text())
lock = json.loads((root / "data/mac-law-agent-execution-plane-lock-v1.json").read_text())
gloss = json.loads((root / "data/founder-reply-glossary-v1.json").read_text())
incident = (root / "brain-os/incidents/SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md").read_text()

if lock.get("worker_on_mac_required"):
    print("FAIL mac-law lock must NOT have worker_on_mac_required (removed v1.1)")
    sys.exit(1)
if "Worker on Mac runs every plan" not in v.get("forbidden_phrases", [{}])[0].get("phrase", "") and not any(
    x.get("phrase") == "Worker on Mac runs every plan" for x in v.get("forbidden_phrases", [])
):
    print("FAIL vocab missing forbidden phrase Worker on Mac runs every plan")
    sys.exit(1)
sec = v.get("secondary_cloud_only") or {}
if sec.get("mac_executes") is not False:
    print("FAIL secondary_cloud_only.mac_executes must be false")
    sys.exit(1)
must = " ".join(lock.get("agents_must", []))
if "secondary -1000 as cloud-only" not in must:
    print("FAIL agents_must missing secondary cloud-only line")
    sys.exit(1)
if "Worker on Mac runs every plan" in incident:
    if "FORBIDDEN" not in incident:
        print("FAIL incident must mark phrase as FORBIDDEN")
        sys.exit(1)
if gloss.get("translations", {}).get("Worker on Mac runs every plan") != "FORBIDDEN PHRASE — instant fail INCIDENT-038":
    print("FAIL glossary missing forbidden phrase entry")
    sys.exit(1)
if v.get("schema") != "mac-worker-vs-factory-vocabulary-v1":
    print("FAIL vocab schema")
    sys.exit(1)
print("PASS mac-worker-vs-factory vocabulary wired v1.1")
PY

bash "$ROOT/scripts/validate-doc-datetime-header-v1.sh" "$INCIDENT" >/dev/null || fail=1

if [[ "$fail" -eq 0 ]]; then
  echo "PASS validate-mac-worker-vs-factory-vocabulary-v1.sh"
else
  echo "FAIL validate-mac-worker-vs-factory-vocabulary-v1.sh"
  exit 1
fi
