"use strict";

const { test } = require("node:test");
const assert = require("node:assert/strict");
const {
  buildContextEnvelope,
  buildRoleEnvelope,
  callGovernor,
} = require("../src/shared.cjs");

test("Context returns envelope ref + hash only", async () => {
  const env = await buildContextEnvelope({
    target_url: "https://example.com/x",
    correlation_id: "c1",
  });
  assert.equal(env.node, "SourceA.Context");
  assert.match(env.envelope_ref, /^ctx:\/\//);
  assert.equal(env.content_hash.length, 64);
  assert.ok(!("raw_html" in env));
});

test("Role returns role envelope", async () => {
  const env = await buildRoleEnvelope({ role_id: "sg_critic", correlation_id: "c2" });
  assert.equal(env.summary.role_id, "sg_critic");
});

test("Governor authenticates and returns an open follow-up reference", async () => {
  let captured;
  const fetchImpl = async (_url, options) => {
    captured = options;
    return new Response(
      JSON.stringify({
        run_id: "run_test",
        terminal: null,
        status: "AWAITING_EXECUTION",
        commitment_status: "OPEN",
      }),
      { status: 202 },
    );
  };
  const env = await callGovernor(
    {
      target_url: "https://example.com",
      correlation_id: "c3",
      idempotency_key: "idem_test",
    },
    fetchImpl,
    {
      SOURCEA_GOVERNOR_URL: "https://governor.example.test",
      SOURCEA_GOVERNOR_TOKEN: "test-ingress-token",
    },
  );
  assert.equal(env.http_status, 202);
  assert.equal(env.summary.terminal, "AWAITING_EXECUTION");
  assert.equal(env.summary.run_id, "run_test");
  assert.match(env.envelope_ref, /^gov:\/\//);
  assert.equal(captured.headers.authorization, "Bearer test-ingress-token");
});

test("Governor refuses to call without an ingress token", async () => {
  await assert.rejects(
    () => callGovernor(
      { target_url: "https://example.com", correlation_id: "c4" },
      async () => { throw new Error("fetch_must_not_be_called"); },
      { SOURCEA_GOVERNOR_URL: "https://governor.example.test" },
    ),
    /SOURCEA_GOVERNOR_TOKEN_MISSING/,
  );
});
