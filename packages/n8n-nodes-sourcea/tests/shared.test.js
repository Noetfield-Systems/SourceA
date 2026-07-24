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

test("Governor calls Mesh and returns refs", async () => {
  const fetchImpl = async () =>
    new Response(
      JSON.stringify({
        run_id: "run_test",
        terminal: "ACCEPTED",
        status: "ACCEPTED",
      }),
      { status: 200 },
    );
  const env = await callGovernor(
    {
      target_url: "https://example.com",
      correlation_id: "c3",
      idempotency_key: "idem_test",
    },
    fetchImpl,
  );
  assert.equal(env.summary.terminal, "ACCEPTED");
  assert.equal(env.summary.run_id, "run_test");
  assert.match(env.envelope_ref, /^gov:\/\//);
});
