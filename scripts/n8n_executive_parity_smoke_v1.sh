#!/usr/bin/env bash
# Prove Executive Workflow path parity with Mesh webpage-repair (ACCEPTED).
# Uses SourceA Governor node helper (same code the n8n node calls).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RECEIPT_DIR="$ROOT/receipts/n8n"
mkdir -p "$RECEIPT_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
CID="parity_${TS}_$$"
URL="${TARGET_URL:-https://sourcea.app/}"

node <<NODE
const { callGovernor, buildContextEnvelope, buildRoleEnvelope } = require("$ROOT/packages/n8n-nodes-sourcea/src/shared.cjs");
const fs = require("fs");
const path = require("path");

(async () => {
  const role = await buildRoleEnvelope({ role_id: "sg_planner", correlation_id: "$CID" });
  const ctx = await buildContextEnvelope({
    target_url: "$URL",
    correlation_id: "$CID",
    event_type: "webpage.repair.requested",
  });
  const gov = await callGovernor({
    target_url: "$URL",
    correlation_id: "$CID",
    idempotency_key: "n8n_parity_$CID",
  });
  const terminal = gov.summary && gov.summary.terminal;
  const accepted = terminal === "ACCEPTED";
  const out = {
    schema: "sourcea_n8n_executive_parity_v1",
    decision_id: "NF-SOURCEA-N8N-ORCHESTRATOR-V1",
    at: new Date().toISOString(),
    workflow: "n8n/workflows/executive_webpage_repair_v1.json",
    correlation_id: "$CID",
    role_ref: role.envelope_ref,
    context_ref: ctx.envelope_ref,
    governor: gov.summary,
    terminal,
    ok: accepted,
    note: accepted
      ? "Governor ACCEPTED — Executive Workflow path parity with Mesh webpage-repair"
      : "Governor did not return ACCEPTED; inspect mesh/runway config",
  };
  const dest = path.join("$RECEIPT_DIR", "EXECUTIVE_WEBPAGE_REPAIR_PARITY_${TS}.json");
  fs.writeFileSync(dest, JSON.stringify(out, null, 2) + "\\n");
  console.log(JSON.stringify(out, null, 2));
  process.exit(accepted ? 0 : 2);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
NODE
