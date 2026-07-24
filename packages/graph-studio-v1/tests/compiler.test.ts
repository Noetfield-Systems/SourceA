import assert from "node:assert/strict";
import { test } from "node:test";
import {
  compileBlueprint,
  executePinnedPlan,
  MemoryPlanStore,
  WEBPAGE_REPAIR_L0_BLUEPRINT,
  assertPlanHash,
  projectRunGraph,
  stripLayout,
} from "../src/index.ts";
import type { BlueprintGraph } from "../src/types.ts";

test("golden blueprint compiles to stable plan_hash", () => {
  const a = compileBlueprint(WEBPAGE_REPAIR_L0_BLUEPRINT);
  const b = compileBlueprint(WEBPAGE_REPAIR_L0_BLUEPRINT);
  assert.equal(a.ok, true);
  assert.equal(b.ok, true);
  if (!a.ok || !b.ok) return;
  assert.equal(a.plan.plan_hash, b.plan.plan_hash);
  assert.ok(a.plan.plan_hash.length === 64);
  assert.equal(assertPlanHash(a.plan), true);
  assert.equal(a.plan.topology, "webpage_repair_l0_v1");
  assert.deepEqual(a.plan.executor_ids, ["n_exec"]);
  assert.deepEqual(a.plan.verifier_ids, ["n_verify"]);
});

test("layout-only mutation does not change plan_hash when stripped", () => {
  const dirty = {
    ...WEBPAGE_REPAIR_L0_BLUEPRINT,
    nodes: WEBPAGE_REPAIR_L0_BLUEPRINT.nodes.map((n, i) => ({
      ...n,
      // layout must not live on blueprint; stripLayout removes if we accidentally nest
    })),
  };
  // Separate layout document — compile only semantic graph
  const layout = {
    blueprint_id: dirty.blueprint_id,
    version: dirty.version,
    positions: Object.fromEntries(dirty.nodes.map((n, i) => [n.id, { x: i * 10, y: 20, color: "red" }])),
  };
  void layout;
  const clean = stripLayout(dirty);
  const r1 = compileBlueprint(WEBPAGE_REPAIR_L0_BLUEPRINT);
  const r2 = compileBlueprint(clean);
  assert.equal(r1.ok && r2.ok, true);
  if (!r1.ok || !r2.ok) return;
  assert.equal(r1.plan.plan_hash, r2.plan.plan_hash);
});

test("layout pollution in blueprint fails compile", () => {
  const polluted = JSON.parse(JSON.stringify(WEBPAGE_REPAIR_L0_BLUEPRINT)) as BlueprintGraph & {
    nodes: Array<Record<string, unknown>>;
  };
  polluted.nodes[0] = { ...polluted.nodes[0], x: 100, y: 200 };
  const r = compileBlueprint(polluted as BlueprintGraph);
  assert.equal(r.ok, false);
  if (r.ok) return;
  assert.ok(r.errors.some((e) => e.code === "LAYOUT_POLLUTION"));
});

test("omitting IndependentVerifier fails compile", () => {
  const g: BlueprintGraph = {
    ...WEBPAGE_REPAIR_L0_BLUEPRINT,
    nodes: WEBPAGE_REPAIR_L0_BLUEPRINT.nodes.filter((n) => n.node_kind !== "IndependentVerifier"),
    edges: WEBPAGE_REPAIR_L0_BLUEPRINT.edges.filter(
      (e) => e.to_node !== "n_verify" && e.from_node !== "n_verify",
    ),
  };
  // reconnect exec → commit (illegal)
  g.edges = [
    ...g.edges.filter((e) => e.id !== "e10" && e.id !== "e11"),
    { id: "e_bad", from_node: "n_exec", from_port: "execution", to_node: "n_commit", to_port: "evidence" },
  ];
  const r = compileBlueprint(g);
  assert.equal(r.ok, false);
  if (r.ok) return;
  assert.ok(
    r.errors.some((e) => e.code === "VERIFIER_COVERAGE" || e.code === "TOPOLOGY_MISMATCH" || e.code === "PORT_TYPE_MISMATCH"),
  );
});

test("unknown node_kind fails compile", () => {
  const g = {
    ...WEBPAGE_REPAIR_L0_BLUEPRINT,
    nodes: [
      ...WEBPAGE_REPAIR_L0_BLUEPRINT.nodes,
      { id: "n_bogus", node_kind: "BogusNode" as never, manifest_version: "1.0.0" },
    ],
  };
  const r = compileBlueprint(g as BlueprintGraph);
  assert.equal(r.ok, false);
  if (r.ok) return;
  assert.ok(r.errors.some((e) => e.code === "UNKNOWN_NODE_KIND"));
});

test("executePinnedPlan invokes mesh after hash assert", async () => {
  const compiled = compileBlueprint(WEBPAGE_REPAIR_L0_BLUEPRINT);
  assert.equal(compiled.ok, true);
  if (!compiled.ok) return;
  const store = new MemoryPlanStore();
  store.put(compiled.plan);

  const mesh = {
    async ingest() {
      return {
        run_id: "run_mesh_1",
        status: "ACCEPTED",
        terminal: "ACCEPTED" as const,
        audit: [
          { at: "t0", kind: "SNAPSHOT_LOCKED", detail: {} },
          { at: "t1", kind: "CONTEXT_PACK", detail: {} },
          { at: "t2", kind: "GOVERNOR", detail: {} },
          { at: "t3", kind: "VERIFY", detail: {} },
        ],
        digest: { terminal: "ACCEPTED" },
      };
    },
  };

  const out = await executePinnedPlan(
    compiled.plan.plan_hash,
    {
      event_id: "evt_1",
      event_type: "webpage_repair_request",
      schema_version: "1",
      organization_id: "sourcea",
      correlation_id: "c1",
      causation_id: null,
      idempotency_key: "k1",
      producer: "test",
      produced_at: new Date().toISOString(),
      payload: { target_url: "https://example.com" },
    },
    { store, mesh },
  );
  assert.equal(out.ok, true);
  assert.equal(out.mesh_run_id, "run_mesh_1");

  const rg = projectRunGraph(
    compiled.plan,
    {
      run_id: "run_mesh_1",
      status: "ACCEPTED",
      terminal: "ACCEPTED",
      audit: out.audit!,
    },
    "grun_1",
  );
  assert.equal(rg.plan_hash, compiled.plan.plan_hash);
  assert.ok(rg.nodes.every((n) => n.status === "PASSED"));
});

test("missing plan_hash rejects execute", async () => {
  const store = new MemoryPlanStore();
  const out = await executePinnedPlan(
    "deadbeef",
    {
      event_id: "e",
      event_type: "webpage_repair_request",
      schema_version: "1",
      organization_id: "sourcea",
      correlation_id: "c",
      causation_id: null,
      idempotency_key: "k",
      producer: "t",
      produced_at: new Date().toISOString(),
      payload: {},
    },
    {
      store,
      mesh: {
        async ingest() {
          throw new Error("should not run");
        },
      },
    },
  );
  assert.equal(out.ok, false);
  assert.equal(out.detail, "PLAN_NOT_FOUND");
});
