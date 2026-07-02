#!/usr/bin/env bash
# Minimal L4 buyer-surface verify — curl public URLs, forbidden-marker scan, receipt JSON.
# No psql · no Supabase migration · no determinism gate (see determinism-gate.yml).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACK="${ROOT}/data/client-proof-founder-review-pack-v1.json"
OUT="${EXTERNAL_VERIFY_L4_RECEIPT:-/tmp/external-verify-l4-receipt.json}"
RUN_ID="${GITHUB_RUN_ID:-local}"
RUN_URL="${GITHUB_RUN_URL:-}"
SHA="${GITHUB_SHA:-$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)}"
PY="${PYTHON:-/usr/bin/python3}"

exec "$PY" - "$PACK" "$OUT" "$RUN_ID" "$SHA" "$RUN_URL" <<'PY'
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

pack_path, out_path, run_id, sha, run_url = sys.argv[1:6]
forbidden_re = r"kazemnezhadsina144-dot|/Users/|sinakazemnezhad|Desktop/SourceA"
pack = json.load(open(pack_path, encoding="utf-8"))
rows = []
passed = failed = 0
for rec in pack.get("rows", []):
    rid = rec.get("recipe_id", "")
    url = rec.get("live_url", "")
    row = {"recipe_id": rid, "url": url, "verdict": "PASS", "http_code": "", "defect": ""}
    if not str(url).startswith("https://"):
        row.update({"verdict": "SKIP", "defect": "not_public_https"})
        passed += 1
        rows.append(row)
        continue
    body_file = tempfile.NamedTemporaryFile(delete=False)
    body_file.close()
    try:
        proc = subprocess.run(
            ["curl", "-sS", "-o", body_file.name, "-w", "%{http_code}",
             "--max-time", "45", "-A", "sourcea-external-verify-l4/1.0", url],
            capture_output=True, text=True, timeout=50,
        )
        code = (proc.stdout or "000").strip() or "000"
        row["http_code"] = code
        body = open(body_file.name, encoding="utf-8", errors="replace").read()
        if code != "200":
            row.update({"verdict": "FAIL", "defect": f"http_code:{code}"})
            failed += 1
        elif re.search(forbidden_re, body):
            row.update({"verdict": "FAIL", "defect": "forbidden_marker"})
            failed += 1
        else:
            passed += 1
    except Exception as exc:
        row.update({"verdict": "FAIL", "defect": str(exc)[:120]})
        failed += 1
    finally:
        try:
            os.unlink(body_file.name)
        except OSError:
            pass
    rows.append(row)

total = len(rows)
ok = failed == 0
at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
doc = {
    "schema": "external-verify-l4-minimal-v1",
    "version": "1.0.0",
    "at": at,
    "law": "L4 buyer surfaces — curl + forbidden scan only",
    "github_run_id": run_id,
    "github_sha": sha,
    "run_url": run_url,
    "ok": ok,
    "total": total,
    "passed": passed,
    "failed": failed,
    "rows": rows,
    "report_line": f"external-verify-l4 {'PASS' if ok else 'FAIL'} · {passed}/{total} · run={run_id}",
}
open(out_path, "w", encoding="utf-8").write(json.dumps(doc, indent=2) + "\n")
print(doc["report_line"])
sys.exit(0 if ok else 1)
PY
