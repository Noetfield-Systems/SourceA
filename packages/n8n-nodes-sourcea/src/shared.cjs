"use strict";

const { createHash, randomUUID } = require("crypto");

function governorBase(env = process.env) {
  return String(
    env.SOURCEA_GOVERNOR_URL ||
      "https://sourcea-executive-governor-v1.sina-kazemnezhad-ca.workers.dev",
  ).replace(/\/$/, "");
}

function sha256Hex(text) {
  return createHash("sha256").update(text).digest("hex");
}

async function buildContextEnvelope(input) {
  const correlationId = String(input.correlation_id || input.event_id || randomUUID());
  const targetUrl = String(
    input.target_url || (input.payload && input.payload.target_url) || "",
  );
  const eventType = String(input.event_type || "webpage.repair.requested");
  const pack = {
    schema: "sourcea.context_pack.v1",
    correlation_id: correlationId,
    event_type: eventType,
    target_url: targetUrl,
    policy_ref: "WEBPAGE_REPAIR@1",
  };
  const hash = sha256Hex(JSON.stringify(pack));
  return {
    schema: "sourcea.node_result.v1",
    node: "SourceA.Context",
    envelope_ref: `ctx://${correlationId}`,
    content_hash: hash,
    usage: { bytes: JSON.stringify(pack).length, model_tokens: 0 },
    summary: { event_type: eventType, target_url: targetUrl },
  };
}

async function buildRoleEnvelope(input) {
  const roleId = String(input.role_id || "sg_planner");
  const correlationId = String(input.correlation_id || randomUUID());
  const row = {
    schema: "sourcea.role_assignment.v1",
    role_id: roleId,
    correlation_id: correlationId,
    control_mode: String(input.control_mode || "SINGLE"),
  };
  const hash = sha256Hex(JSON.stringify(row));
  return {
    schema: "sourcea.node_result.v1",
    node: "SourceA.Role",
    envelope_ref: `role://${roleId}/${correlationId}`,
    content_hash: hash,
    usage: { bytes: JSON.stringify(row).length, model_tokens: 0 },
    summary: { role_id: roleId },
  };
}

async function callGovernor(input, fetchImpl = fetch, env = process.env) {
  const base = governorBase(env);
  const correlationId = String(input.correlation_id || input.event_id || randomUUID());
  const idempotencyKey = String(input.idempotency_key || `n8n_${correlationId}`);
  const targetUrl = String(
    input.target_url || (input.payload && input.payload.target_url) || "https://example.com",
  );
  const body = {
    event_id: correlationId,
    event_type: String(input.event_type || "webpage.repair.requested"),
    idempotency_key: idempotencyKey,
    payload: {
      task_type: "webpage_repair",
      target_url: targetUrl,
      ...(input.payload && typeof input.payload === "object" ? input.payload : {}),
    },
  };
  const res = await fetchImpl(`${base}/v1/executive/runs`, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let json = {};
  try {
    json = JSON.parse(text);
  } catch {
    json = { raw: text.slice(0, 200) };
  }
  const hash = sha256Hex(text);
  return {
    schema: "sourcea.node_result.v1",
    node: "SourceA.Governor",
    envelope_ref: `gov://${json.run_id || correlationId}`,
    content_hash: hash,
    usage: { bytes: text.length, model_tokens: 0 },
    http_status: res.status,
    summary: {
      run_id: json.run_id || null,
      terminal: json.terminal || json.status || null,
      ok: res.ok,
    },
  };
}

module.exports = {
  governorBase,
  sha256Hex,
  buildContextEnvelope,
  buildRoleEnvelope,
  callGovernor,
};
