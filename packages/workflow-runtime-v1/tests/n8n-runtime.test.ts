import assert from "node:assert/strict";
import { test } from "node:test";
import { N8nWorkflowRuntime } from "../src/index.ts";

test("N8nWorkflowRuntime startRun falls back to QUEUED on 404", async () => {
  const fetchImpl: typeof fetch = async () => new Response("nope", { status: 404 });
  const rt = new N8nWorkflowRuntime({
    baseUrl: "https://n8n.example",
    apiKey: "k" + "x".repeat(32),
    fetchImpl,
  });
  const handle = await rt.startRun({
    workflow_id: "wf_1",
    correlation_id: "c1",
    idempotency_key: "idem_1",
    payload: { event_type: "webpage.repair.requested" },
  });
  assert.equal(handle.status, "QUEUED");
  assert.equal(handle.run_id, "n8n_run_idem_1");
});

test("getRun maps finished success", async () => {
  const fetchImpl: typeof fetch = async () =>
    new Response(
      JSON.stringify({
        id: "ex1",
        finished: true,
        status: "success",
        workflowId: "wf_1",
        startedAt: "2026-07-24T00:00:00.000Z",
        stoppedAt: "2026-07-24T00:00:01.000Z",
      }),
      { status: 200 },
    );
  const rt = new N8nWorkflowRuntime({
    baseUrl: "https://n8n.example",
    apiKey: "k" + "x".repeat(32),
    fetchImpl,
  });
  const run = await rt.getRun("ex1");
  assert.equal(run.status, "SUCCEEDED");
  assert.equal(run.terminal, "ACCEPTED");
});
