import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildWebpageRepairEvent,
  createRunwayGoalKernelRouter,
  ExecutiveMeshPipeline,
  MemoryCanonicalStore,
  RUN_TERMINALS,
} from "../src/index.ts";

test("simulated webpage repair stays pending until an accepted artifact is verified", async () => {
  const store = new MemoryCanonicalStore();
  const pipeline = new ExecutiveMeshPipeline({
    store,
    runwayRouter: createRunwayGoalKernelRouter({ simulate: true }),
  });

  const evt = buildWebpageRepairEvent({
    event_id: "evt_repair_page_x",
    target_url: "https://sourcea.app/operating-brain-install",
    canonical_state_version: 1,
  });

  const run = await pipeline.ingest(evt);
  assert.equal(run.terminal, null);
  assert.equal(run.status, "AWAITING_EXECUTION");
  assert.equal(run.commitment_status, "OPEN");
  assert.equal(run.digest!.terminal, null);
  assert.ok(!RUN_TERMINALS.includes(run.status as never));
  assert.notEqual(run.status, "ACTIVE_FOREVER");

  // ContextPack versioned
  assert.ok(run.context_pack);
  assert.equal(run.context_pack!.snapshot_version, 1);
  assert.ok(run.context_pack!.context_hash.length > 10);

  // Planner + Critic packets
  const roles = run.role_packets.map((p) => p.role);
  assert.deepEqual(roles, ["SG", "MEMORY_STEWARD", "STRATEGIC_PLANNER", "CRITIC"]);
  assert.equal(run.role_packets.find((p) => p.role === "CRITIC")!.conclusion, "PASS");
  assert.equal(run.plan!.critic_status, "PASSED");

  // One Governor decision
  assert.ok(run.decision_id);
  assert.ok(run.decision_hash);

  // One WorkPacket, Runway route, no illegal fanout
  assert.ok(run.work_packet);
  assert.equal(run.work_packet!.executor_class, "RUNWAY_GOAL_KERNEL");
  assert.equal(run.work_packet!.budget.max_fanout, 0);

  // Verify + commitment close
  assert.equal(run.evidence.length, 1);
  assert.equal(run.evidence[0]!.valid, true);
  assert.equal(run.commitment_status, "CLOSED");

  // Digest present
  assert.ok(run.digest);
  assert.equal(run.digest!.terminal, "ACCEPTED");
  assert.ok(run.digest!.committed_version);

  // Idempotent ingest / replay no duplicate
  const again = await pipeline.ingest(evt);
  assert.equal(again.run_id, run.run_id);
  assert.equal(store.listRuns().filter((r) => r.idempotency_key === evt.idempotency_key).length, 1);
});

test("live Goal admission starts Runway and only terminal receipt verification closes the commitment", async () => {
  let goalStatus = "RUNNING";
  let startCalled = false;
  const requiredIds = [
    "prompt_fidelity",
    "artifact_available",
    "required_sections",
    "links_valid",
    "receipt_verified",
    "staging_deployed",
  ];
  const goalSnapshot = () => ({
    goal_id: "goal_live_123",
    status: goalStatus,
    work_packet_terminal: goalStatus === "PASSED" ? "ACCEPTED_ARTIFACT" : null,
    receipt_id: goalStatus === "PASSED" ? "receipt_live_123" : null,
    receipt_hash: goalStatus === "PASSED" ? "b".repeat(64) : null,
    acceptance_criteria: requiredIds.map((id) => ({ id, required: true })),
    acceptance_results: requiredIds.map((id) => ({
      id,
      status: goalStatus === "PASSED" ? "PASS" : "WAITING",
    })),
  });
  const fetchImpl: typeof fetch = async (input, init) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    if (url.endsWith("/v1/goals") && method === "POST") {
      return new Response(JSON.stringify({ goal_id: "goal_live_123" }), { status: 201 });
    }
    if (url.endsWith("/v1/goals/goal_live_123/start") && method === "POST") {
      startCalled = true;
      return new Response(JSON.stringify({ status: "RUNNING", workflow_instance_id: "wf_live_123" }), { status: 202 });
    }
    if (url.endsWith("/v1/goals/goal_live_123/verify") && method === "POST") {
      return new Response(JSON.stringify({ passed: true, receipt_id: "receipt_live_123" }), { status: 200 });
    }
    if (url.endsWith("/v1/goals/goal_live_123") && method === "GET") {
      return new Response(JSON.stringify(goalSnapshot()), { status: 200 });
    }
    return new Response(JSON.stringify({ error: "unexpected_request", url, method }), { status: 404 });
  };

  const store = new MemoryCanonicalStore();
  const router = createRunwayGoalKernelRouter({
    baseUrl: "https://runway.example.test",
    simulate: false,
    fetchImpl,
  });
  const pipeline = new ExecutiveMeshPipeline({
    store,
    runwayRouter: router,
    runwayBaseUrl: "https://runway.example.test",
    runwayFetch: fetchImpl,
  });

  const run = await pipeline.ingest(buildWebpageRepairEvent({
    event_id: "evt_followup_live",
    target_url: "https://sourcea.app/example",
    idempotency_key: "followup-live-1",
    canonical_state_version: 1,
  }));
  assert.equal(startCalled, true);
  assert.equal(run.status, "AWAITING_EXECUTION");
  assert.equal(run.terminal, null);
  assert.equal(run.commitment_status, "OPEN");
  assert.equal(run.digest!.goal_status, "RUNNING");

  goalStatus = "PASSED";
  const reconciled = await pipeline.reconcile(run.run_id);
  assert.equal(reconciled.status, "ACCEPTED");
  assert.equal(reconciled.terminal, "ACCEPTED");
  assert.equal(reconciled.commitment_status, "CLOSED");
  assert.ok(reconciled.digest!.receipt_id === "receipt_live_123");
  assert.equal(reconciled.evidence.at(-1)!.valid, true);
});

test("stale packet / stale event rejected", async () => {
  const store = new MemoryCanonicalStore();
  const pipeline = new ExecutiveMeshPipeline({ store });

  // Advance canonical version once
  await pipeline.ingest(
    buildWebpageRepairEvent({
      event_id: "evt_advance",
      target_url: "https://example.com/a",
      idempotency_key: "adv1",
      canonical_state_version: 1,
    }),
  );
  assert.equal(store.getVersion(), 2);

  const stale = await pipeline.ingest(
    buildWebpageRepairEvent({
      event_id: "evt_stale",
      target_url: "https://example.com/b",
      idempotency_key: "stale1",
      canonical_state_version: 1,
    }),
  );
  assert.equal(stale.stale_rejected, true);
  assert.equal(stale.terminal, "BOUNDED_FAILURE");

  const rejected = pipeline.rejectStalePacket(1, "CRITIC");
  assert.equal(rejected.stale_rejected, true);
  assert.equal(rejected.terminal, "BOUNDED_FAILURE");
});

test("executor reject → INCIDENT not ACTIVE_FOREVER", async () => {
  const store = new MemoryCanonicalStore();
  const pipeline = new ExecutiveMeshPipeline({
    store,
    runwayRouter: async () => ({
      admitted: false,
      goal_ref: "x",
      status: "REJECTED",
      detail: "forced_reject",
    }),
  });
  const run = await pipeline.ingest(
    buildWebpageRepairEvent({
      event_id: "evt_incident",
      target_url: "https://example.com/fail",
      idempotency_key: "inc1",
      canonical_state_version: 1,
    }),
  );
  assert.equal(run.terminal, "INCIDENT");
  assert.notEqual(String(run.status), "ACTIVE_FOREVER");
});

test("document stub for non-RUNWAY executor classes", async () => {
  const router = createRunwayGoalKernelRouter({ simulate: true });
  const stub = await router({
    action_id: "a",
    goal_id: "g",
    decision_id: "d",
    commitment_id: "c",
    why_now: "x",
    executor_class: "FBE_RAILWAY",
    inputs: {},
    allowed_capabilities: [],
    forbidden_capabilities: [],
    acceptance_predicates: [],
    evidence_required: [],
    budget: { max_attempts: 1, max_minutes: 1, max_cost_usd: 1, max_fanout: 0 },
    rollback_policy: "none",
    failure_policy: "INCIDENT",
    execution_idempotency_key: "k",
  });
  assert.equal(stub.status, "DOCUMENT_STUB");
});
